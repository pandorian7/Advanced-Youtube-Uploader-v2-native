from __future__ import print_function

import os.path
import sys
from tqdm import tqdm

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# from IPython.display import clear_output
# from googleapiclient.http import MediaFileUpload



def video_upload(service, body, media_body):
  request = service.videos().insert(part='snippet,status', body=body, media_body=media_body)
  response = None
  position = -1
  with tqdm(total=100, bar_format='Uploading : {desc:<5.5}{percentage:3.0f}%|{bar:100}|') as pbar:
    while response is None:
      while True:
          status, response = request.next_chunk()
          try:
            new_position = int(status.progress() * 100)
          except:
            new_position = 100
          if position != new_position:
              position = new_position
              status, response = request.next_chunk()
              break
      pbar.update(position - pbar.n)

  videoid = response.get('id')
  return videoid

def add_video_to_playlist(service, video_id, playlist_id):
  playlistItem = service.playlistItems().insert(part='snippet', body={'snippet':{
      'playlistId': playlist_id,
      'resourceId': {"kind": "youtube#video",
                "videoId": video_id}
  }}).execute()

def add_thumbnail(service, video_id, image_resource):
  service.thumbnails().set(videoId=video_id, media_body=image_resource).execute()

def get_playlist_id(service, playlist_name, playlist_description=None):
  playlists = get_playlists(service)
  if playlist_name in playlists: 
    id = playlists[playlist_name]
  else:
    id = create_playlist(service, playlist_name, playlist_description)
  return id

def get_playlists(service):
  playlists = []
  first_dose = service.playlists().list(mine=True, part='snippet', maxResults=50).execute()
  playlists += first_dose['items']
  next_page_token = first_dose.get('nextPageToken', None)
  while next_page_token != None:
    later_dose = service.playlists().list(mine=True, part='snippet', maxResults=50, pageToken=next_page_token).execute()
    playlists += later_dose['items']
    next_page_token = later_dose.get('nextPageToken', None)
  brefied_playlists = {playlist['snippet']['title']: playlist['id'] for playlist in playlists}
  return brefied_playlists

def create_playlist(service, title, description=None):
  req_body = {
      'snippet': {
          'title': title
      },
      'status': {
          "privacyStatus": "public"
      }
  }
  if description != None: req_body['snippet']['description'] = description
  playlist = service.playlists().insert(part="snippet,status", body=req_body).execute()
  return playlist.get('id')

class YouTubeService:
  def __init__(self, rootDir="creds"):
      self.rootDir = rootDir
      self.SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
  def getService(self,cred_int):
      creds = None
      cwd = self.rootDir
      scopes = self.SCOPES
      cred_folder = os.path.join(cwd, str(cred_int))
      secret = os.path.join(cred_folder, 'credentials.json')
      token = os.path.join(cred_folder, 'token.json')
      if os.path.exists(token):
          creds = Credentials.from_authorized_user_file(token, scopes)

      if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
              creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file(
                  secret, scopes)
              creds = flow.run_console()
          with open(token, 'w') as token:
              token.write(creds.to_json())
      
      service = build('youtube', 'v3', credentials=creds)

      return service