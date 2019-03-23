
#
#       Copyright (C) 2014-2015
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

#http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcvfs.html

import xbmcaddon
def GetXBMCVersion():
    version = xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')
    version = version.split('.')
    return int(version[0]), int(version[1]) #major, minor eg, 13.9.902


MAJOR, MINOR = GetXBMCVersion()
FRODO        = (MAJOR == 12) and (MINOR < 9)


ADDONID = 'plugin.audio.mp3streams'
ADDON   = xbmcaddon.Addon(ADDONID)
TITLE   = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')



DEBUG = False #set to True to enable output to kodi.log
def log(text):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except:
        pass


PROPERTY  = 'MP3_DOWNLOADER_STATE_%d'
RESOLVING = 'MP3_RESOLVING'

############################### SERVICE LOGIC ###############################


import xbmc
import xbmcgui

global COUNT
global STARTED

RETRIES = 25
COUNT   = 0
STARTED = False


def stopDownloaders():
    import playerMP3
    playerMP3.stopDownloaders()


def resetCache():
    import playerMP3
    playerMP3.resetCache()


def clear():
    log('Clearing MP3 Streams Service')
    global COUNT
    global STARTED

    if xbmcgui.Window(10000).getProperty(RESOLVING) != RESOLVING:
        stopDownloaders()
        resetCache()
    else:
        log('Clearing cancelled due to RESOLVING property')

    COUNT   = 0
    STARTED = False


def check():
    global COUNT
    if xbmc.Player().isPlaying():
        COUNT = 0
    else:
        COUNT += 1

        log('MP3 Service Checking Kodi is still trying to play %d' % COUNT)

        if COUNT > RETRIES:
            clear()


if __name__ == '__main__':
    log('********** XBMC STARTED **********')
    clear()
    while (not xbmc.abortRequested):  
        if not STARTED:
            STARTED = xbmc.Player().isPlaying()
        else:
            check()    
        xbmc.sleep(1000)

    log('********** XBMC ABORTED **********')
    clear()


############################### END OF SERVICE ###############################


import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import urllib

import os
import requests
import shutil


try:    
    from hashlib import md5
    MD5 = md5
except: 
    import md5
    MD5 = md5.new



ADDONID    = 'plugin.audio.mp3streams'
ADDON      =  xbmcaddon.Addon(ADDONID)
HOME       =  xbmc.translatePath(ADDON.getAddonInfo('path'))
PROFILE    =  xbmc.translatePath(ADDON.getAddonInfo('profile'))
PROFILE    =  ADDON.getAddonInfo('profile')
ICON       =  os.path.join(HOME, 'icon.png')
TEMP       =  xbmc.translatePath(os.path.join(PROFILE, 'temp_dl'))

MAX_DOWNLOADERS = 3


#---------------------------- Global Methods ----------------------------


def deleteFile(filename):
    log('Deleting %s' % filename)

    if len(filename) < 1:
        log('Empty filename')
        return

    try:    current = xbmc.Player().getPlayingFile() if xbmc.Player().isPlaying() else ''
    except: current = ''

    while current == filename:
        try:    current = xbmc.Player().getPlayingFile() if xbmc.Player().isPlaying() else ''
        except: current = ''
        xbmc.sleep(1000)

    tries = 15
    while xbmcvfs.exists(filename) and tries > 0:
        tries -= 1 
        try: 
            xbmcvfs.delete(filename)
        except Exception, e: 
            log('ERROR %s in deleteFile %s' % (str(e), filename))
            log('ERROR tries=%d' % tries)
            xbmc.sleep(500)

    if xbmcvfs.exists(filename):
        log('FAILED to delete %s' % filename)
    else:
        log('Deleted %s' % filename)


def verifyFileSize(filename):
    if not filename:
        return True

    ADDONID = 'plugin.audio.mp3streams'
    ADDON   =  xbmcaddon.Addon(ADDONID)
    precache = int(ADDON.getSetting('pre-cache').replace('K', ''))

    filename = xbmc.translatePath(filename)

    log('VERIFYING %s' % filename)
    count = 100
    while count > 0:
        if xbmcgui.Window(10000).getProperty(filename) == 'EXCEPTION':
            xbmcgui.Window(10000).clearProperty(filename)
            log('Exception downloading %s' % filename)
            return False

        log('verifyFileSize %d' % count)
        if xbmcvfs.exists(filename):
            size = xbmcvfs.File(filename).size()
            log('CURRENT SIZE = %d' % size)
            if size == 212 and unavailable(filename):
                return False
            if size > precache * 1024:
                log(size)
                log('FILE SIZE VERIFIED!!')
                return True

        count -= 1
        xbmc.sleep(500)

    return False


def unavailable(filename):
    f    = xbmcvfs.File(filename, 'r')
    text = f.read().lower()
    if 'unavailable' in text:
        log('unavailable message received from website')
        return True
    return False


def stopDownloaders():
    log('in STOPDOWNLOADERS')

    #signal all downloaders to stop
    for i in range(MAX_DOWNLOADERS):
        state = xbmcgui.Window(10000).getProperty(PROPERTY % i)
        if state:
            xbmcgui.Window(10000).setProperty(PROPERTY % i, 'Signal')

    #now wait for them to all stop
    i = 0
    while i < MAX_DOWNLOADERS:
        state = xbmcgui.Window(10000).getProperty(PROPERTY % i)
        if state:
            xbmc.sleep(100)
            i = 0
        else:
            i += 1


def getFreeSlot():
    for i in range(MAX_DOWNLOADERS):
        state = xbmcgui.Window(10000).getProperty(PROPERTY % i)
        if state:
            log('State %d Found' % i)
        else:
            return i

    return -1


def getNmrDownloaders():
    count = 0
    for i in range(MAX_DOWNLOADERS):
        state = xbmcgui.Window(10000).getProperty(PROPERTY % i)
        if state:
            count += 1        

    return count


def startFile(title, artist, album, track, url, filename):
    log('Creating downloader')

    retries = 2
    while retries > 0:
        retries -= 1
        downloader = Downloader(title, artist, album, track, url, filename)
        downloader.start()
    
        if verifyFileSize(filename):
            return

        stopDownloaders()
        deleteFile(filename)


def resetCache_original():
    log('in RESETCACHE')
    if os.path.exists(TEMP):
        try:    shutil.rmtree(TEMP)
        except: pass

    xbmc.sleep(1000)

    try:    os.makedirs(TEMP)
    except: pass


def resetCache():
    log('in RESETCACHE')
    if not xbmcvfs.exists(TEMP):
        try:    xbmcvfs.mkdirs(TEMP)
        except: pass
        return

    dirs, files = xbmcvfs.listdir(TEMP)
    for file in files:
        filename = os.path.join(TEMP, file)
        deleteFile(filename)


def createMD5(url):
    return MD5(url).hexdigest()


def clean(text):
    text = text.replace('/',  '')
    text = text.replace("\\", '')
    text = text.replace(':',  '')
    text = text.replace('*',  '')
    text = text.replace('?',  '')
    text = text.replace('"',  '')
    text = text.replace('<',  '')
    text = text.replace('>',  '')
    text = text.replace('|',  '')

    return text.strip()


def createFilename(title, artist, album, url):
    if ADDON.getSetting('keep_downloads')=='false':
        return os.path.join(TEMP, createMD5(url))

    title  = clean(title)
    artist = clean(artist)
    album  = clean(album)

    customdir = ADDON.getSetting('custom_directory')
    folder = ADDON.getSetting('music_dir')

    if customdir=='false':
        folder = TEMP

    if ADDON.getSetting('folder_structure')=="0":
        filename = os.path.join(folder, artist, album)
    else:
        filename = os.path.join(folder, artist + ' - ' + album)
 
    try:
        xbmcvfs.mkdirs(filename)
    except Exception, e:
        log('Error creating folder %s - %s' % (filename, str(e)))

    filename = os.path.join(filename, title + '.mp3')

    return filename


#called from default.py
def getListItem(title, artist, album, track, image, duration, url, fanart, isPlayable, useDownload):

    liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

    liz.setInfo('music', {'Title':title, 'Artist':artist, 'Album':album, 'Duration':duration})

    liz.setProperty('mimetype',    'audio/mpeg')
    liz.setProperty('fanart_image', fanart)
    liz.setProperty('IsPlayable',   isPlayable)

    if FRODO or ('.mp3' in url) or (not useDownload):
        return url, liz
    title = "%s. %s" % (track,title)
    filename = createFilename(title, artist, album, url)
                
    plugin = 'plugin://%s/'  % ADDONID
    plugin += '?mode=%d'     % 999
    plugin += '&title=%s'    % urllib.quote_plus(title)
    plugin += '&artist=%s'   % urllib.quote_plus(artist)
    plugin += '&album=%s'    % urllib.quote_plus(album)
    plugin += '&track=%s'    % urllib.quote_plus(str(track))
    plugin += '&image=%s'    % urllib.quote_plus(image)
    plugin += '&duration=%s' % urllib.quote_plus(duration)
    plugin += '&filename=%s' % urllib.quote_plus(filename)
    plugin += '&url=%s'      % urllib.quote_plus(url)

    return plugin, liz

#----------------------------- The Play Methods ----------------------------

def getParams(url):
    if len(url) < 2:
        return []

    cleaned = url.split('?', 1)[-1]
    pairs   = cleaned.split('&')

    param = {}

    for i in range(len(pairs)):
        split = pairs[i].split('=')
        if len(split) == 2:
            param[split[0]] = split[1]
                                
    return param


def fetchNext(posn):
    log('IN fetchNext')

    if getNmrDownloaders() == MAX_DOWNLOADERS:
        return

    if posn == 0:
        return

    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

    len = playlist.size()

    if posn >= len:
        log('Reached end of playlist')
        return

    item = playlist[posn]
    url  = item.getfilename()

    log('URL = %s' % url)

    if not url.startswith('plugin://plugin.audio.mp3streams'):
        return

    log('Next Position    = %d' % posn)
    log('Next URL         = %s' % url)

    params = getParams(url)

    try:    mode = int(urllib.unquote_plus(params['mode']))
    except: return

    if mode != 999:
        return fetchNext(posn+1)

    try:    title = urllib.unquote_plus(params['title'])
    except: return

    try:    artist = urllib.unquote_plus(params['artist'])
    except: return

    try:    album = urllib.unquote_plus(params['album'])
    except: return

    try:    track = urllib.unquote_plus(params['track'])
    except: return

    try:    url = urllib.unquote_plus(params['url'])
    except: return

    try:    filename = urllib.unquote_plus(params['filename'])
    except: return

    log('Title    %s' % title)
    log('URL      %s' % url)
    log('Filename %s' % filename)

    if xbmcvfs.exists(xbmc.translatePath(filename)):
        return

    downloader = Downloader(title, artist, album, track, url, filename)
    downloader.start()


def fetchFile(title, artist, album, track, url, filename):
    log('IN fetchFile')

    nDownloaders = getNmrDownloaders()
    log('Number of downloaders= %d' % nDownloaders)
    if nDownloaders >= MAX_DOWNLOADERS: #-1 to allow for fetchNext
        stopDownloaders()

    if xbmcvfs.exists(xbmc.translatePath(filename)) and xbmcvfs.File(filename).size() > 250 * 1024:
        log('%s already exists' % filename)
        return

    log('**** FILE %s DOES NOT EXISTS - START DOWNLOADING****' % filename)
    startFile(title, artist, album, track, url, filename)


def play(sys, params):
    log('Setting resolving property')
    xbmcgui.Window(10000).setProperty(RESOLVING, RESOLVING)

    title    = urllib.unquote_plus(params['title'])
    artist   = urllib.unquote_plus(params['artist'])
    album    = urllib.unquote_plus(params['album'])
    track    = urllib.unquote_plus(params['track'])
    image    = urllib.unquote_plus(params['image'])
    duration = urllib.unquote_plus(params['duration'])
    filename = urllib.unquote_plus(params['filename'])
    url      = urllib.unquote_plus(params['url'])

    log('**** In playFile ****')
    log(title)
    log(url)
    log(filename)

    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    posn     = playlist.getposition()
    next     = posn+1

    fetchFile(title, artist, album, track, url, filename)
    fetchNext(next)

    log('**** FILE %s NOW AVAILABLE ****' % filename)
    liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image, path=filename)

    liz.setInfo('music', {'Title':title, 'Artist':artist, 'Album':album, 'Duration':duration})
    liz.setProperty('mimetype', 'audio/mpeg')
    liz.setProperty('IsPlayable','true')

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

    log('Clearing resolving property')
    xbmcgui.Window(10000).clearProperty(RESOLVING)


#------------------------------------------------------------------------


import threading
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

#log(EasyID3.valid_keys.keys())

class Downloader(threading.Thread):
     def __init__(self, title, artist, album, track, url, filename):
         super(Downloader, self).__init__()
         self._signal  = False
         self.title    = title
         self.artist   = artist
         self.album    = album
         self.track    = int(track)
         self.url      = url
         self.filename = xbmc.translatePath(filename)
         self.complete = False


     def downloadFile(self):
         try:
             headers = {'Host':'listen.musicmp3.ru', 'Range':'bytes=0-', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0', 'Accept':'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5','Referer':'https://www.goldenmp3.ru'}

             xbmcgui.Window(10000).setProperty(PROPERTY % self.slot, 'Downloading')

             from contextlib import closing
             with closing(requests.get(self.url, headers=headers, stream=True)) as r:
                 f = xbmcvfs.File(self.filename, 'w')
                 for chunk in r.iter_content(chunk_size=1024):
                     if xbmcgui.Window(10000).getProperty(PROPERTY % self.slot) == 'Signal':
                         log('SIGNALLED VIA WINDOW PROPERTY')
                         self.signal()
                     if self._signal:
                         log('SIGNALLED')
                         f.close()                     
                         return
                     if chunk:
                         f.write(chunk)

                 f.close()
                 self.complete = True
         except Exception, e:
             xbmcgui.Window(10000).setProperty(self.filename, 'EXCEPTION')
             log('Error in downloadFile % s' % str(e))
             try:    f.close()
             except: pass


     def applyID3(self):
         if ADDON.getSetting('keep_downloads')=='false':
             return 
         if not xbmcvfs.exists(self.filename):
             return

         if self.track < 1:
             return

         log('Applying ID3 tags to %s' % self.title)

         temp = self.filename.rsplit(os.sep, 1)[-1]
         temp = os.path.join(TEMP, temp)

         doCopy = self.filename != temp

         if doCopy:
             xbmcvfs.copy(self.filename, temp)

         #Remove track number from title
         title=self.title
         try: title=title[title.find('. ')+2:]
         except: title=title
		 
         audio = MP3(temp, ID3=EasyID3)
         audio['title']       = title
         audio['artist']      = self.artist
         audio['album']       = self.album
         audio['tracknumber'] = str(self.track)
         audio['date']        = ''
         audio['genre']       = ''
         audio.save(v1=2)
         log(audio.pprint())

         if doCopy:
             del audio 
             deleteFile(self.filename)
             xbmcvfs.copy(temp, self.filename)
             deleteFile(temp)


     def run(self):
         if xbmcvfs.exists(self.filename):
             log('DOWNLOADER - %s %s already exists' % (self.title, self.filename))
             self.complete = True
             return

         self.slot = getFreeSlot()
             
         log('DOWNLOADER - TITLE            %s' % self.title)
         log('DOWNLOADER - SLOT             %d' % self.slot)
         log('DOWNLOADER - DOWNLOADING URL  %s' % self.url)
         log('DOWNLOADER - DOWNLOADING FILE %s' % self.filename)

         if self.slot < 0:
             log('CAN\'T FIND FREE SLOT - WILL NOT DOWNLOAD')
         else:
             self.downloadFile()

         xbmcgui.Window(10000).clearProperty(PROPERTY % self.slot)

         if self.complete:
             log('%s DOWNLOAD COMPLETED' % self.title)
             try:
                 self.applyID3()
             except Exception, e:
                 log('Error applying tags %s' % str(e))
         else:
             log('%s DOWNLOAD CANCELLED' % self.title)
             deleteFile(self.filename)

         exit()


     def signal(self):
         self._signal = True
