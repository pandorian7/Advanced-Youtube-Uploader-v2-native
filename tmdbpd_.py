from tmdbv3api import TMDb, Movie, TV, Episode 
from tmdbv3api.exceptions import TMDbException
from tmdbv3api.as_obj import AsObj

from env import TMDB_API_KEY
import datetime

tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
mv, tv, ep = Movie(), TV(), Episode()


def get_handler_by_type(kind:str):
    if kind == 'Movie': handler = mv
    if kind == 'TV': handler = tv
    return handler



def search_bar(query:str, kind:str):
    searchHandler = get_handler_by_type(kind)
    try:
        res = searchHandler.search(query)
        return list(res)
    except UnboundLocalError:
        raise TMDbException(f'$kind must be an element of ["Movie", "TV"]. "{kind}" is not valid.')

def details(tmdb_id:int, kind:str):  # to be deleated
    searchHandler = get_handler_by_type(kind)
    res = searchHandler.details(tmdb_id)
    res.kind = kind
    return res
    
def get_native_dic(obj:AsObj):  # to be deleated
    genetal_keys = ['backdrop_path', 'id', 'overview', 'poster_path', 'kind']
    if obj.kind == "TV":
        specified_keys = ['name', 'seasons']
    if obj.kind == "Movie":
        specified_keys = ['title']
    keys = genetal_keys + specified_keys
    return_dic = {}
    for i in keys:
        return_dic[i] = obj.get(i)
    return return_dic

def get_detils_from_tv(tmdb_id:int):
    obj =  tv.details(tmdb_id)
    return obj

def get_details_from_movie(tmdb_id:int):
    obj = mv.details(tmdb_id)
    obj.display_year = str(datetime.date.fromisoformat(obj.release_date).year)
    return obj

def get_details_from_episode(tmdb_id, season_no, episode_no):
    return ep.details(tmdb_id, season_no, episode_no)
    