from ffprobe import FFProbe
import os

def get_eng_sub_net_data(media_file):
  metadata = FFProbe(media_file)
  streams = metadata.streams
  subtitle_streams = [stream for stream in streams if stream.is_subtitle()]
  eng_subtitle_streams = [stream.__dict__ for stream in subtitle_streams if stream.language() == 'eng']
  eng_subtitle_streams_net_data = {
      int(stream['index']):stream.get('TAG:title', "") for stream in eng_subtitle_streams
  }
  return eng_subtitle_streams_net_data

def try_to_get_best_sub_from_net_data(net_data):
  keywords = ['full', 'sdh', 'english']
  selected = None
  for stream_no, stream_val in net_data.items():
    last = stream_no
    for k in keywords:
      if k in stream_val.lower():selected = stream_no
  if selected == None:selected = last
  return selected

def rip_sub(media_file, stream_no):
  sream_no_as_str = str(stream_no)
  file_root = os.path.dirname(media_file)
  sub_root = os.path.join(file_root, 'Subs')
  if not os.path.exists(sub_root):os.system(f'mkdir "{sub_root}"')
  media_file_name = os.path.basename(media_file)
  subtitle_file_name = os.path.splitext(media_file_name)[0] + '.srt'
  subtitle_file_path = os.path.join(sub_root, subtitle_file_name)
  command=f'ffmpeg -hide_banner -loglevel error -i "{media_file}" -map 0:{sream_no_as_str} -c:s copy "{subtitle_file_path}"'
  return_code = os.system(command)
  return return_code, subtitle_file_path


def get_upl_file_path(video_file_path):
  video_root = os.path.dirname(video_file_path)
  video_file_name = os.path.basename(video_file_path)
  upl_file_name = os.path.splitext(video_file_name)[0] + '.upl'
  upl_root = os.path.join(video_root, 'upl')
  upl_file_path = os.path.join(upl_root, upl_file_name)
  return upl_file_path

def mark_uploaded_video(video_file_path):
  upl_file_path = get_upl_file_path(video_file_path)
  upl_root = os.path.dirname(upl_file_path)
  if not os.path.exists(upl_root): os.system(f'mkdir "{upl_root}"')
  os.system(f'touch "{upl_file_path}"')

def check_if_video_is_uploaded(video_file_path):
  upl_file_path = get_upl_file_path(video_file_path)
  if os.path.exists(upl_file_path):
    return True
  else:
    return False

def upload_with_metadata(service, title, description, media_file):
  catagoryId = '1'
  videoId = youtubepd_.video_upload(service,body={
          'snippet': {
              'title': title,
              'description': description,
              'categoryId': catagoryId
          },
          'status': {
              'privacyStatus': 'private'
          }
      },
      media_body=MediaFileUpload(media_file, chunksize=4 * 1024 * 1024, resumable=True))

def create_srt_from_video(video_file_path):
  net_data = get_eng_sub_net_data(video_file_path)
  if net_data != {}:
    selected_stream_no = try_to_get_best_sub_from_net_data(net_data)
    code, sub_name = rip_sub(video_file_path, selected_stream_no)
    if code == 0:
      return sub_name
    else:
      print(f'Error while riping stream {selected_stream_no} from {video_file_path}')
      for error in code:
        print(f'\t{error}')
      return None
  else:
    return None
  