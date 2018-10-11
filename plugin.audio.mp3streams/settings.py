import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os

ADDON = xbmcaddon.Addon(id='plugin.audio.mp3streams')
DATA_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.audio.mp3streams'), '')

def cookie_jar():
    return create_file(DATA_PATH, "cookiejar.lwp")
	
def addon():
    return ADDON
		
def artist_icons():
    return create_directory(DATA_PATH, "artist_icons")
	
def folder_structure():
    return ADDON.getSetting('folder_structure')
	
def favourites_file_artist():
    return create_file(DATA_PATH, "favourites_artist.list")
	
def favourites_file_album():
    return create_file(DATA_PATH, "favourites_album.list")
	
def download_list():
    return create_file(DATA_PATH, "downloads.list")
	
def favourites_file_songs():
    return create_file(DATA_PATH, "favourites_songs.list")
	
def playlist_file():
    return create_file(DATA_PATH, "playlist_file.list")
	
def custom_directory():
    if ADDON.getSetting('custom_directory') == "true":
        return True
    else:
        return False
		
def keep_downloads():
    if ADDON.getSetting('keep_downloads') == "true":
        return True
    else:
        return False
		
def gotham_fix():
    if ADDON.getSetting('gotham_fix') == "true":
        return True
    else:
        return False
		
def golden_path():
    if ADDON.getSetting('golden_path') == "true":
        return True
    else:
        return False
		
def default_queue():
    if ADDON.getSetting('default_queue') == "true":
        return True
    else:
        return False
		
def hide_fanart():
    if ADDON.getSetting('hide_fanart') == "true":
        return True
    else:
        return False
		
def default_queue_album():
    if ADDON.getSetting('default_queue_album') == "true":
        return True
    else:
        return False
		
def music_dir():
    if ADDON.getSetting('music_dir')=="set":
        return create_directory(DATA_PATH, "music")
    else:
        return ADDON.getSetting('music_dir')
	
def create_directory(dir_path, dir_name=None):
    if dir_name:
        dir_path = os.path.join(dir_path, dir_name)
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def create_file(dir_path, file_name=None):
    if file_name:
        file_path = os.path.join(dir_path, file_name)
    file_path = file_path.strip()
    if not os.path.exists(file_path):
        f = open(file_path, 'w')
        f.write('')
        f.close()
    return file_path
	
create_directory(DATA_PATH, "")
   
