import datetime, os, json
import PTN


def getHTML_table(res):
    html = """
    <style>
      td, th, table {
        border: 1px solid white;
        border-collapse: collapse;
      }
    </style>
    <table>
  """
    for i in range(len(res)):
        item = res[i]
        id = item['id']
        poster = item["poster_path"]
        if not poster == None:
            poster_s = "https://image.tmdb.org/t/p/w92" + poster
            poster_l = "https://image.tmdb.org/t/p/original" + poster
            snap = f'<a href="{poster_l}" target="_blank"><img src="{poster_s}" /></a>'
        else:
            snap = "N/A"
        cover = snap
        try:
            name = item['name']
        except AttributeError:
            name = item['original_title']
        try:
            year = datetime.date.fromisoformat(item.first_air_date).year
        except:
            try:
                year = datetime.date.fromisoformat(item.release_date).year
            except:
                year = "N/A"
        row = f"""
      <tr> 
        <td>{id}<td>
        <td>{snap}<td>
        <td>{name}<td>
        <td>{year}<td>
      </tr>
    """
        html += row
    html += "</table>"
    return html


class PTNparseObj:
    def __init__(self, torrent_path):
        self.name = os.path.basename(torrent_path)

    def __repr__(self):
        return f"<metadata * '{self.name}'>"


def parse(torrent_path):
    torrent_name = os.path.basename(torrent_path)
    data = PTN.parse(torrent_name)
    obj = PTNparseObj(torrent_name)
    obj.title = data['title']
    obj.season = data.get('season', None)
    obj.episode = data.get('episode', None)
    if (obj.season != None) and (obj.episode != None):
        obj.kind = 'TV'
    else:
        obj.kind = 'Movie'
    return obj

def compare_titles(title1:str, title2:str):
    if not (title1.lower() == title2.lower()):
        print(f'title1: "{title1}" and title2: "{title2}" are different.')
        choice = input(f'Do you still wanna continue? (Y/N) | ').lower()
        if choice == 'n':
            print('exiting ..')
            exit()

def get_thumbnail_from_backdrop(backdrop):
  pre = 'https://image.tmdb.org/t/p/original'
  image_url = pre + backdrop
  image_name = backdrop[1:]
  os.system(f'wget -q {image_url}')
  return image_name

def get_sym_path(media_file_path):
    sym_name = 'sym.json'
    sym_file_path = os.path.join(
        os.path.dirname(media_file_path),
        sym_name
    )
    return sym_file_path

def add_sym(title1, title2, media_file_path):
    sym_file_path = get_sym_path(media_file_path)
    if not os.path.exists(sym_file_path):
        with open(sym_file_path, 'w') as file:
            file.write(json.dumps({"syms":{}}, indent=4))
    with open(sym_file_path, 'r') as sym_file:
        sym_data = json.loads(sym_file.read())
    
    if not title1 in sym_data['syms']:
        sym_data['syms'][title1] = []
    sym_data['syms'][title1].append(title2)
    
    with open(sym_file_path, 'w') as file:
        file.write(json.dumps(sym_data, indent=4))

def check_sym(title1, title2, media_file_path):
    sym_file_path = get_sym_path(media_file_path)

    if os.path.exists(sym_file_path):
        with open(sym_file_path, 'r') as sym_file:
            sym_data = json.loads(sym_file.read())
        if title2 in sym_data['syms'][title1]:
            return True
        else:
            return False
    else:
        return False

def compare_titles_v2(title1, title2, media_file_path):
    if not (title1.lower() == title2.lower()):
        if not check_sym(title1, title2, media_file_path):
            print('')
            print(f'title1: "{title1}" and title2: "{title2}" are different.\n')
            choice = input(f'Do you still wanna continue? (Y/N) | ').lower()
            if choice == 'y':
                add_sym(title1, title2, media_file_path)

            if choice == 'n':
                print('exiting ..')
                exit()
