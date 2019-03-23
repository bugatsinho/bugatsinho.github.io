# -*- coding: utf-8 -*-
#Bugatsinho fixes 28/08/2018

import urllib, urllib2, re
import xbmcplugin, xbmcgui, os, xbmc, sys
import settings, time
import requests
from t0mm0.common.net import Net
from threading import Thread
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


cookie_jar = settings.cookie_jar()
net = Net()
ADDON = settings.addon()
GOTHAM_FIX = False
GOLDEN_PATH = False
KEEP_DOWNLOADS = settings.keep_downloads()
ARTIST_ART = settings.artist_icons()
FAV_ARTIST = settings.favourites_file_artist()
FAV_ALBUM = settings.favourites_file_album()
FAV_SONG = settings.favourites_file_songs()
PLAYLIST_FILE = settings.playlist_file()
MUSIC_DIR = settings.music_dir()
HIDE_FANART = settings.hide_fanart()
QUEUE_SONGS = settings.default_queue()
QUEUE_ALBUMS = settings.default_queue_album()
DOWNLOAD_LIST = settings.download_list()
FOLDERSTRUCTURE = settings.folder_structure()
fanart = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams', 'fanart.jpg'))
art = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams', 'art')) + '/'
artgenre = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams/art', 'genre')) + '/'
artbillboard = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams/art', 'billboard')) + '/'
urllist = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams', 'lists', 'mp3url.list'))
audio_fanart = ""
iconart = xbmc.translatePath(os.path.join('special://home/addons/plugin.audio.mp3streams', 'icon.png'))
download_lock = os.path.join(MUSIC_DIR, 'downloading.txt')
xbmc_version=xbmc.getInfoLabel("System.BuildVersion")[:4]
ua = 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'


GOTHAM_FIX_2 = ADDON.getSetting('gotham_fix_2') == 'true'
if GOTHAM_FIX_2:
    GOTHAM_FIX = False

def newPlay(pl, clear):
    if clear or (not xbmc.Player().isPlayingAudio()):
        xbmc.Player().play(pl)

def open_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', ua)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def GET_url(url):
    header_dict = {}
    if 'musicmp3' in url:
        header_dict['Accept'] = 'audio/webm,audio/ogg,udio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5'
        header_dict['User-Agent'] = 'AppleWebKit/<WebKit Rev>'
        header_dict['Host'] = 'musicmp3.ru'
        header_dict['Referer'] = 'http://musicmp3.ru/'
        header_dict['Connection'] = 'keep-alive'
    if 'goldenmp3' in url:
        header_dict['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        header_dict['User-Agent'] = ua
        header_dict['Host'] = 'www.goldenmp3.ru'
        header_dict['Referer'] = 'http://www.goldenmp3.ru/compilations/events/albums'
        header_dict['Connection'] = 'keep-alive'
    net.set_cookies(cookie_jar)
    link = net.http_GET(url, headers=header_dict).content.encode("utf-8").rstrip()
    net.save_cookies(cookie_jar)
    return link

def get_cookie():
    header_dict = {}
    header_dict['User-Agent'] = ua
    header_dict['Connection'] = 'keep-alive'
    net.set_cookies(cookie_jar)
    link = net.http_GET('http://musicmp3.ru/', headers=header_dict).content.encode("utf-8").rstrip()
    net.save_cookies(cookie_jar)

def CATEGORIES():
    addDir('Artists','http://musicmp3.ru/artists.html',21,art + 'artists.jpg','')
    addDir('Top Albums','http://musicmp3.ru/genres.html',12,art + 'topalbums.jpg','')
    addDir('New Albums','http://musicmp3.ru/new_albums.html',12,art + 'newalbums.jpg','')
    addDir('Compilations','url',400,art + 'compilations.jpg','')
    addDir('Billboard Charts','url',101,art + 'billboardcharts.jpg','')
    addDir('Search Artists','url',24,art + 'searchartists.jpg','')
    addDir('Search Albums','url',24,art + 'searchalbums.jpg','')
    addDir('Search Songs','url',24,art + 'searchsongs.jpg','')
    addDir('Favourite Artists','url',63,art + 'favouriteartists.jpg','')
    addDir('Favourite Albums','url',66,art + 'favouritealbums.jpg','')
    addDir('Favourite Songs','url',69,art + 'favouritesongs.jpg','')
    addDirAudio('Instant Mix Favourite Songs (Shuffle and Play)','url',99,art + 'mixfavouritesongs.jpg','','','','','')
    addDirAudio('Instant Mix Favourite Albums (Shuffle and Play)','url',89,art + 'mixfavouritealbums.jpg','','','','','')
    addDirAudio('Clear Playlist','url',100,art + 'clearplaylist.jpg','','','','','')
    addDirAudio('Add ID3 Tags','url',300,art + 'addid3tags.jpg','','','','','')
    addDir('Browse Alternate Source','url',700,artgenre + 'alternate.jpg','')

def charts():
    addDir('BillBoard Hot 20 Singles','http://www.officialcharts.com/charts/billboard-hot-100-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('BillBoard 20 Albums','http://www.officialcharts.com/charts/billboard-200/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 Streaming Singles','http://www.officialcharts.com/charts/audio-streaming-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 UK Singles','http://www.officialcharts.com/charts/singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 UK Albums','http://www.officialcharts.com/charts/albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 End of Year Singles','http://www.officialcharts.com/charts/end-of-year-singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 End of Year Albums','http://www.officialcharts.com/charts/end-of-year-artist-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 100 Compilation Albums','http://www.officialcharts.com/charts/official-compilations-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 50 Soundtracks','http://www.officialcharts.com/charts/soundtrack-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 Dance Singles','http://www.officialcharts.com/charts/dance-singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 Dance Albums','http://www.officialcharts.com/charts/dance-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 R&B Singles','http://www.officialcharts.com/charts/r-and-b-singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 R&B Albums','http://www.officialcharts.com/charts/r-and-b-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 Rock/Metal Singles','http://www.officialcharts.com/charts/rock-and-metal-singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 40 Rock/Metal Albums','http://www.officialcharts.com/charts/rock-and-metal-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 50 Independent Singles','http://www.officialcharts.com/charts/independent-singles-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 50 Independent Albums','http://www.officialcharts.com/charts/independent-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 20 Country Albums','http://www.officialcharts.com/charts/country-artists-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 20 Country Compilation Albums','http://www.officialcharts.com/charts/country-compilations-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 50 Classical Compilation Albums','http://www.officialcharts.com/charts/classical-compilation-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 30 Jazz & Blues Albums','http://www.officialcharts.com/charts/jazz-and-blues-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    addDir('Top 20 Christian & Gospel Albums','http://www.officialcharts.com/charts/christian-and-gospel-albums-chart/',102,artbillboard +'billboardcharts.jpg','')
    #addDir('UK Single Chart - Top 100','https://www.billboard.com/charts/official-uk-songs',102,artbillboard +'uksinglecharttop100.jpg','')
    #addDir('BillBoard 200','https://www.billboard.com/charts/billboard-200',102,artbillboard +'billboard200.jpg','')
    #addDir('Hot 100 Singles','https://www.billboard.com/charts/hot-100',102,artbillboard +'hot100singles.jpg','')
    #addDir('Country Albums','http://www.billboard.com/charts/country-albums',102,artbillboard +'countryalbums.jpg','')
    #addDir('HeatSeeker Albums','http://www.billboard.com/charts/heatseekers-albums',102,artbillboard +'heatseekeralbums.jpg','')
    #addDir('Independent Albums','http://www.billboard.com/charts/independent-albums',102,artbillboard +'independentalbums.jpg','')
    #addDir('Catalogue Albums','http://www.billboard.com/charts/catalog-albums',102,artbillboard +'cataloguealbums.jpg','')
    #addDir('Folk Albums','http://www.billboard.com/charts/folk-albums',102,artbillboard +'folkalbums.jpg','')
    #addDir('Blues Albums','http://www.billboard.com/charts/blues-albums',102,artbillboard +'bluesalbums.jpg','')
    #addDir('Tastemaker Albums','http://www.billboard.com/charts/tastemaker-albums',102,artbillboard +'tastemakeralbums.jpg','')
    #addDir('Rock Albums','http://www.billboard.com/charts/rock-albums',102,artbillboard +'rockalbums.jpg','')
    #addDir('Alternative Albums','http://www.billboard.com/charts/alternative-albums',102,artbillboard +'alternativealbums.jpg','')
    #addDir('Hard Rock Albums','http://www.billboard.com/charts/hard-rock-albums',102,artbillboard +'hardrockalbums.jpg','')
    #addDir('Digital Albums','http://www.billboard.com/charts/digital-albums',102,artbillboard +'digitalalbums.jpg','')
    #addDir('R&B Albums','http://www.billboard.com/charts/r-b-hip-hop-albums',102,artbillboard +'randbalbums.jpg','')
    #addDir('Top R&B/Hip-Hop Albums','http://www.billboard.com/charts/r-and-b-albums',102,artbillboard +'toprandbandhiphop.jpg','')
    #addDir('Dance Electronic Albums','http://www.billboard.com/charts/dance-electronic-albums',102,artbillboard +'danceandelectronic.jpg','')

def chart_lists(name, url): #102
    req = urllib2.Request(url)
    req.add_header('User-Agent', ua)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    if "officialcharts.com" in url:
        all_list = regex_get_all(link, '<div class="track">', '<div class="label')
        for list in all_list:
            iconimage = regex_from_to(list, '<img src="', '"')
            titles=regex_get_all(list,'<a href=','/a>')
            type = regex_from_to(titles[0], 'search/', '/').replace('&#039;',"'").replace('&#39;',"'")
            artist = regex_from_to(titles[1], '">', '<').replace('&#039;',"'").replace('&#39;',"'")
            title = regex_from_to(titles[0], '">', '<').replace('&#039;',"'").replace('&#39;',"'")
            if 'singles' in type:
                if '&' in artist or 'FT' in artist or 'FEATURING' in artist or '&amp;' in artist or '/' in artist:
                    addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),title.replace('&amp;', '&'),28,iconimage,'')
                else:
                    addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),artist.replace('&amp;', '&') + ' ' + title.replace('&amp;', '&'),28,iconimage,'')
            elif 'albums' in type:
                addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),'url',25,iconimage,'')
    elif "billboard.com" in url:
        link = link.replace('\n', '').replace('\t', '')
        match = re.compile('<span class="this-week">(.+?)</span> <span class="last-week">(.+?)</span></div><div class="row-image"(.+?)<div class="row-title"><h2>(.+?)</h2><h3><a href="(.+?)" data-tracklabel="Artist Name">(.+?)</a>').findall(link)
        for pos, lw, iconimage, title, artisturl, artist in match:
            text = "%s %s" % (artist, title)
            try:
                iconimage='http' + regex_from_to(iconimage,'http','"').replace(')','')
            except:
                iconimage='http://www.billboard.com/sites/all/themes/bb/images/default/no-album.png'
            if not 'Single' in name and not 'Best Songs of 2014' in text:
                addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),'url',25,iconimage,'')
            elif not 'Best Songs of 2014' in text:
                addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),'url',26,iconimage,'')
    else:
        all_list=regex_get_all(link,'<span class="chart_position','</header>')
        for a in all_list:
            title=regex_from_to(a,'<h1>','</h1>').rstrip()
            try:
                artist=regex_from_to(a,' title="','">').strip()
            except:
                artist=regex_from_to(a,'<p class="chart_info">','</p>').strip()
            try:
                iconimage=regex_from_to(a,'Image" src="','"')
            except:
                iconimage='http://www.billboard.com/sites/all/themes/bb/images/default/no-album.png'
            text = "%s %s" % (artist, title)
            if not 'Single' in name and not 'Best Songs of 2014' in text:
                addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),'url',25,iconimage,'')
            elif not 'Best Songs of 2014' in text:
                addDir(artist.replace('&amp;', '&') + ' - ' + title.replace('&amp;', '&'),'url',26,iconimage,'')

def artists(url):
    link = GET_url(url)
    addDir('All Artists','http://musicmp3.ru/main_artists.html?type=artist&page=1',31,art + 'allartists.jpg','')
    sub_dir = re.compile('<li class="menu_sub__item"><a class="menu_sub__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url1, title in sub_dir:
        iconimage = 'http://musicmp3.ru/i' + url1.replace('.html', '.jpg').replace('artists', 'genres').replace('tracks', 'track')
        if title != 'Other':
            addDir(title.replace('&amp;', '&'),'https://musicmp3.ru' + url1,41,artgenre + title.replace(' ','').replace('&amp;','_').lower() + '.jpg','')

def all_artists(name, url):
    link = GET_url(url)
    all_artists = re.compile('<li class="small_list__item"><a class="small_list__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url1, title in all_artists:
        icon_path = os.path.join(ARTIST_ART, title + '.jpg')
        if os.path.exists(icon_path):
            iconimage = icon_path
        else:
            iconimage = iconart
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,22,iconimage,'artists')
    pgnumf = url.find('page=') + 5
    pgnum = int(url[pgnumf:]) + 1
    nxtpgurl = url[:pgnumf]
    nxtpgurl = "%s%s" % (nxtpgurl, pgnum)
    addDir('>> Next page', nxtpgurl, 31, art + 'nextpage.jpg', str(pgnumf))
    setView('movies', 'default')

def sub_dir(name, url, icon):
    link = GET_url(url)
    addDir('Top ' + name + ' Artists',url + '?page=1',31,artgenre + name.replace(' ','').replace('&amp;','_').lower() +'/' + 'top' + name.replace(' ','').replace('&amp;','_').lower() + '.jpg','')
    sub_dir = re.compile('<li class="menu_sub__item"><a class="menu_sub__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url, title in sub_dir:
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url + '?page=1',31,artgenre + name.replace(' ','').replace('&amp;','_').lower() +'/' + title.replace(' ','').replace('&amp;','_').lower() + '.jpg','')

def genres(name, url):
    link = GET_url(url)
    if name == 'Top Albums':
        addDir('Top Albums','http://musicmp3.ru/main_albums.html?gnr_id=&sort=top&type=album&page=1',15,art +'alltopalbums.jpg','')
    else:
        addDir('New Albums',url + '?page=1',15,art + 'allnewalbums.jpg','')
    sub_dir = re.compile('<li class="menu_sub__item"><a class="menu_sub__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url1, title in sub_dir:
        iconimage = 'http://musicmp3.ru/i' + url1.replace('.html', '.jpg').replace('tracks', 'track')
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,14,artgenre + title.replace(' ','').replace('&amp;','_').lower() + '.jpg','')

def all_genres(name, url):
    nxtpgnum = int(url.replace('http://musicmp3.ru/main_albums.html?gnr_id=2&sort=top&type=album&page=', '')) + 1
    nxtpgurl = "%s%s" % ('http://musicmp3.ru/main_albums.html?gnr_id=2&sort=top&type=album&page=', str(nxtpgnum))
    link = GET_url(url)
    all_genres = re.compile('<li class="small_list__item"><a class="small_list__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url1, title in all_genres:
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,22,'http://www.pearljamlive.com/images/pic_home.jpg','')
    addDir('>> Next page', nxtpgurl, 13, art + 'nextpage.jpg', next)

def genre_sub_dir(name, url, icon):
    link = GET_url(url)
    addDir('Top ' + name + ' Albums',url + '?page=1',15,artgenre + name.replace('and','&').replace(' ','').replace('&amp;','_').lower() +'/' + 'top' + name.replace('and','_').replace(' ','').replace('&amp;','_').lower() + '.jpg','')
    sub_dir = re.compile('<li class="menu_sub__item"><a class="menu_sub__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url, title in sub_dir:
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url + '?page=1',15,artgenre + name.replace('and','&').replace(' ','').replace('&amp;','_').lower() +'/' + title.replace(' ','').replace('&amp;','_').lower() + '.jpg','')

def genre_sub_dir2(name, url, icon):
    link = GET_url(url)
    addDir('Top ' + name + ' Albums',url,15,os.path.join(artgenre, 'alltopalbums.jpg'),'')
    sub_dir = re.compile('<li class="menu_sub__item"><a class="menu_sub__link" href="(.+?)">(.+?)</a></li>').findall(link)
    for url, title in sub_dir:
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url + '?page=1',15,icon,'')

def compilations_menu():
    addDir('Best Compilations','http://www.goldenmp3.ru/albums_showcase.html?section=compilations&type=albums&page=',401,art + 'topalbums.jpg','1')
    addDir('New Compilations','http://www.goldenmp3.ru/albums_showcase.html?section=compilations&sort=new&type=albums&page=',401,art + 'newalbums.jpg','1')
    addDir('Major Hits','http://www.goldenmp3.ru/albums_showcase.html?gnr_id=806&section=compilations&type=albums&page=',401,art + 'newalbums.jpg','1')
    addDir('Nightclub Hits','http://www.goldenmp3.ru/albums_showcase.html?gnr_id=822&section=compilations&type=albums&page=',401,art + 'newalbums.jpg','1')
    addDir('Chillout Hits','http://www.goldenmp3.ru/albums_showcase.html?gnr_id=848&section=compilations&type=albums&page=',401,art + 'newalbums.jpg','1')
    addDir('Tributes and Covers','http://www.goldenmp3.ru/albums_showcase.html?gnr_id=872&section=compilations&type=albums&page=',401,art + 'newalbums.jpg','1')
    addDir('Events','http://www.goldenmp3.ru/compilations/events/albums',401,art + 'newalbums.jpg','n')

def compilations_list(name, url, iconimage, page):
    link = open_url(url)
    match=re.compile('<a href="(.+?)"><img alt="(.+?)" src="(.+?)"/></a><a class="(.+?)" href="(.+?)">(.+?)</a><span class="(.+?)">(.+?)</span><span class="f_year">(.+?)</span><span class="ga_price">(.+?)</span>').findall(link)
    #match=re.compile('<a href="(.+?)"><img alt="(.+?)" src="(.+?)" /></a><a class="(.+?)" href="(.+?)">(.+?)</a><span class="(.+?)">(.+?)</span><span class="f_year">(.+?)</span><span class="ga_price">(.+?)</span></div>').findall(link)
    for link, d1, iconimage, cl, url2, title, cl, artist, year, prc in match:
        link ='http://www.goldenmp3.ru' + link
        addDir(title.replace('&amp;', 'and'), link, 5, iconimage, 'albums')
    if page != 'n':
        nextpage = int(page) + 1
        nxtpgurl = "%s%s" % (url, nextpage)
        url = "%s%s" % (url, page)
        addDir('>> Next page', nxtpgurl, 401, art + 'nextpage.jpg', str(nextpage))
    setView('movies', 'album')

def search(name, url):
    keyboard = xbmc.Keyboard('', name, False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if len(query) > 0:
            if name == 'Search Artists':
                search_artists(query)
            elif name == 'Search Albums':
                search_albums(query)
            elif name == 'Search Songs':
                search_songs(query)

def search_artists(query):
    url = 'https://musicmp3.ru/search.html?text=%s&all=artists' % urllib.quote_plus(query)
    link = GET_url(url)
    all_artists = re.compile('<a class="artist_preview__title" href="(.+?)">(.+?)</a>').findall(link)
    for url1, title in all_artists:
        icon_path = os.path.join(ARTIST_ART, title + '.jpg')
        if os.path.exists(icon_path):
            iconimage = icon_path
        else:
            iconimage = iconart
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,22,iconimage,'artists')

def search_albums(query):
    url = 'https://musicmp3.ru/search.html?text=%s&all=albums' % urllib.quote_plus(query.replace(' - ', ' ').replace('-', ' '))
    link = GET_url(url)
    link = link.replace('<span class="album_report__artist">Various Artists</span>', '<a class="album_report__artist" href="/artist_various-artist.html">Various Artist</a>')
    all_albums = re.compile('<a class="album_report__link" href="(.+?)"><img class="album_report__image" src="(.+?)"/><span class="album_report__name">(.+?)</span></a>(.+?)album_report__artist" href="(.+?)">(.+?)</a>, <span class="album_report__date">(.+?)</span>').findall(link)
    #all_albums = re.compile('<a class="album_report__link" href="(.+?)"><img class="album_report__image" src="(.+?)" /><span class="album_report__name">(.+?)</span></a>(.+?)album_report__artist" href="(.+?)">(.+?)</a>, <span class="album_report__date">(.+?)</span>').findall(link)
    for url1,thumb,album,plot,artisturl,artist,year in all_albums:
        title = "%s - %s (%s)" % (artist, album, year)
        thumb = thumb.replace('al', 'alm').replace('covers', 'mcovers')
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,5,thumb,'albums')
    setView('movies', 'album')

def search_songs(query):
    playlist = []
    url = 'https://musicmp3.ru/search.html?text=%s&all=songs' % urllib.quote_plus(query.replace(' - ', ' ').replace('-', ' ').replace(' FT ', ' ').replace(' FEATURING ', ' ').replace(' ', '+'))
    link = GET_url(url)
    link = link.replace('<td class="song__artist song__artist--search">Various Artist</td>', '<td class="song__artist song__artist--search"><a class="song__link" href="/artist_various-artist.html">Various Artist</a></td>')
    match = re.compile('<tr class="song"><td class="song__play_button"><a class="player__play_btn js_play_btn" href="#" rel="(.+?)" title="Play track"/></td><td class="song__name song__name--search"><a class="song__link" href="(.+?)">(.+?)</a></td><td class="song__artist song__artist--search"><a class="song__link" href="(.+?)">(.+?)</a></td><td class="song__album song__album--search"><a class="song__link" href="(.+?)">(.+?)</a>').findall(link)
    for id,songurl,song,artisturl,artist,albumurl,album in match:
        iconimage = ""
        url = 'https://listen.musicmp3.ru/' + id # 'http://files.musicmp3.ru/lofi/' + id
        #url = 'http://listen.musicmp3.ru/2f99f4bf4ce7b171/' + id
        title = "%s - %s - %s" % (artist.replace('&amp;','and'), song.replace('&amp;','&'), album.replace('&amp;','&'))
        addDirAudio(title,url,10,iconimage,song,artist,album,'','')
        liz=xbmcgui.ListItem(song, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo('music', {'Title':song, 'Artist':artist, 'Album':album})
        liz.setProperty('mimetype', 'audio/mpeg')
        liz.setThumbnailImage(iconimage)
        liz.setProperty('fanart_image', audio_fanart)
        playlist.append((url, liz))
    setView('music', 'song')

def album_list(name, url):
    link = GET_url(url)
    try:
        artist_url = regex_from_to(link, 'class="art_wrap__img" src="', '"')
        get_artist_icon(name, artist_url)
        xbmc.log("348 name = {0}\nartist_url = {1}".format(name, artist_url), xbmc.LOGNOTICE)
    except:
        pass
    all_albums = re.compile('<a class="album_report__link" href="(.+?)"><img alt="(.+?)" class="album_report__image" src="(.+?)"/><span class="album_report__name">(.+?)</span>(.+?)"album_report__artist" href="(.+?)">(.+?)</a>, <span class="album_report__date">(.+?)</span>').findall(link)
    #all_albums = re.compile('<a class="album_report__link" href="(.+?)"><img alt="(.+?)" class="album_report__image" src="(.+?)" /><span class="album_report__name">(.+?)</span>(.+?)"album_report__artist" href="(.+?)">(.+?)</a>, <span class="album_report__date">(.+?)</span>').findall(link)
    for url1,d1,thumb,album,plot,artisturl,artist,year in all_albums:
        title = "%s - %s - %s" % (artist, album, year)
        thumb = thumb.replace('al', 'alm').replace('covers', 'mcovers')
        addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,5,thumb,'albums')
    pgnumf = url.find('page=') + 5
    pgnum = int(url[pgnumf:]) + 1
    nxtpgurl = url[:pgnumf]
    nxtpgurl = "%s%s" % (nxtpgurl, pgnum)
    addDir('>> Next page', nxtpgurl, 15, art + 'nextpage.jpg', str(pgnumf))
    setView('movies', 'album')

def albums(name, url):
    duplicate = []
    link = GET_url(url)
    try:
        artist_url = regex_from_to(link, 'class="album_report__image"\s*src="', '"')
        get_artist_icon(name, artist_url)
        xbmc.log("370 name = {0}\nartist_url = {1}".format(name, artist_url), xbmc.LOGNOTICE)
    except:
        pass
    all_albums = re.compile('<div class="album_report"><h5 class="album_report__heading"><a class="album_report__link" href="(.+?)"><img alt="(.+?)" class="album_report__image" src="(.+?)"/><span class="album_report__name">(.+?)</span></a></h5><div cla(.+?)lbum_report__second_line"><span class="album_report__date">(.+?)</span>').findall(link)
    #all_albums = re.compile('<div class="album_report"><h5 class="album_report__heading"><a class="album_report__link" href="(.+?)"><img alt="(.+?)" class="album_report__image" src="(.+?)"/><span class="album_report__name">(.+?)</span></a></h5><div class="album_report__second_line"><span class="album_report__date">(.+?)</span>').findall(link)
    for url1,d1,thumb,album,d2,year in all_albums:
        title = "%s - %s - %s" % (name, album, year)
        if title not in duplicate:
            duplicate.append(title)
            thumb = thumb.replace('al', 'alm').replace('covers', 'mcovers')
            addDir(title.replace('&amp;', 'and'),'http://musicmp3.ru' + url1,5,thumb,'albums')
    setView('movies', 'album')

def find_url(id):
    s = read_from_file(urllist)
    if id + '-' in s:
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                urlstart = list.split('-')
                urlid = urlstart[0]
                url = urlstart[1]
                if urlid == id:
                    return url
    else:
        return 'https://listen.musicmp3.ru/1d6c13041066bed9/'

def play_album(name, url, iconimage, mix, clear):
    if ' - ' in name:
        nartist=name.split(' - ')[0]
        nalbum=name.split(' - ')[1]
    else:
        nartist='Various'
        nalbum=name
    if GOLDEN_PATH:
        url=url.replace('http://','https://').replace('musicmp3','www.goldenmp3').replace('artist_','/').replace('__album_','/').replace('.html','')
    origurl=url
    if 'musicmp3' in origurl:
        std = 'id="(.+?)" itemprop="tracks" itemscope="itemscope" itemtype="http://schema.org/MusicRecording"><td class="song__play_button"><a class="player__play_btn js_play_btn" href="#" rel="(.+?)" title="Play track"/></td><td class="song__name"><div class="title_td_wrap"><meta content="(.+?)" itemprop="url"/><meta content="(.+?)" itemprop="duration"(.+?)<meta content="(.+?)" itemprop="inAlbum"/><meta content="(.+?)" itemprop="byArtist"/><span itemprop="name">(.+?)</span><div class="jp-seek-bar" data-time="(.+?)"><div class="jp-play-bar">'
        #std = 'id="(.+?)" itemprop="tracks" itemscope="itemscope" itemtype="http://schema.org/MusicRecording"><td class="song__play_button"><a class="player__play_btn js_play_btn" href="#" rel="(.+?)" title="Play track" /></td><td class="song__name"><div class="title_td_wrap"><meta content="(.+?)" itemprop="url" /><meta content="(.+?)" itemprop="duration"(.+?)<meta content="(.+?)" itemprop="inAlbum" /><meta content="(.+?)" itemprop="byArtist" /><span itemprop="name">(.+?)</span><div class="jp-seek-bar" data-time="(.+?)"><div class="jp-play-bar"></div></div></div></td><td class="(.+?)__service song__service--ringtone'
    elif 'goldenmp3' in origurl:#track,id,songurl,meta, d1,album,artist,songname,dur,artist1
        std = 'itemscope="(.+?)" itemtype="http://schema.org/MusicRecording"><td><a class="play" href="#" rel="(.+?)" title="Listen the song in low quality">(.+?)</a>(.+?)<td><div class="title_td_wrap">(.+?)<span itemprop="name">(.+?)</span>(.+?)<span class="artist">&ndash;&ensp;by (.+?)</span><div class="jp-seek-bar"><div class="jp-play-bar"></div></div></div></td><td>(.+?)</p></td><td><a class="price" href="/pricing.html"> </a></td></tr>'
        #std = 'itemscope="(.+?)" itemtype="http://schema.org/MusicRecording"><td><a class="play" href="#" rel="(.+?)" title="Listen the song in low quality">(.+?)</a>(.+?)<td><div class="title_td_wrap">(.+?)<span itemprop="(.+?)am(.+?)">(.+?)</span>&ensp;(.+?)<div class="jp-seek-bar"><div class="jp-play-bar"></div></div></div></td><td>(.+?)</p></td><td><a class="price" href="/pricing.html"> </a></td></tr>'
    else:
        std = 'prop="tracks" itemscope="(.+?)" itemtype="http://schema.org/MusicRecording"><td><a class="play" href="#" rel="(.+?)" title="Listen the song in low quality">(.+?)</td>(.+?)<div (.+?)="title_td_wrap">(.+?).<span (.+?)="name">(.+?)</span>&ensp;[(](.+?)[)]&ensp;<span class="artist">&ndash;&ensp;by (.+?)</span><div class="jp-seek-bar"><div class="jp-play-bar"></div>'
    alt = std.replace('rel="(.+?)', '')
    browse=False
    playlist=[]
    dialog = xbmcgui.Dialog()
    if mode != 6 and mix != 'mix' and mix != 'queue':
        if dialog.yesno("MP3 Streams", 'Browse songs or play full album?', '', '', 'Play Now','Browse'):
            browse=True
    match = []
    link  = GET_url(url)
    if 'musicmp3' in origurl:
        link = link.split('<tr class="song" ')
    elif 'goldenmp3' in origurl:
        link=regex_from_to(link,'<table class="title_list">','<div>Total')
        link = link.split('itemprop="tracks"')
    else:
        link = link.split('<tr item')
    for song in link:
        if 'rel=' in song:
            items = re.compile(std).findall(song)
            for item in items:
                match.append(item)
        else:
            items = re.compile(alt).findall(song)
            for item in items:
                item = (item[0], '', item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8])
                match.append(item)
    nItem = len(match)
    count=0
    if browse == True:
        for track,id,songurl,meta, d1,album,artist,songname,dur in match:
            count+=1
            if 'musicmp3' in origurl:
                trn = track.replace('track','')
            else:
                trn = album.replace('.&ensp','')
            if GOTHAM_FIX:
                url = find_url(trn).strip() + id
            else:
                url = 'https://listen.musicmp3.ru/' + id #'http://files.musicmp3.ru/lofi/' + id #find_url(trn).strip() + id
            songname = songname.replace('&amp;', 'and')
            if 'musicmp3' in origurl:
                artist = artist.replace('&amp;', 'and')
                album = album.replace('&amp;', 'and')
                title = "%s. %s" % (track.replace('track',''), songname)
            elif 'goldenmp3' in origurl:
                dur = artist.replace('(','').replace(')','')
                artist = nartist.replace('&amp;', 'and')
                ntrack = album.replace('&amp;', 'and')
                album = nalbum.replace('&amp;', 'and')
                title = "%s. %s - %s" % (count, ntrack, songname)
            else:
                artist = artist.replace('&amp;', 'and')
                album = name.replace('&amp;', 'and')
                title = "%s. %s" % (trn, songname)
                dur=dur.replace('(','').replace(')','')
                dur=str((int(dur.split(':')[0])*60) + int(dur.split(':')[1]))
            addDirAudio(title,url,10,iconimage,songname,artist,album,dur,'')
        return
    import playerMP3
    if mix != 'mix':
        dp = xbmcgui.DialogProgress()
        dp.create("MP3 Streams",'Creating Your Playlist')
        dp.update(0)
    for track,id,songurl,meta, d1,album,artist,songname,dur in match:
        count+=1
        if 'musicmp3' in origurl:
            trn = track.replace('track','')
        elif 'goldenmp3' in origurl:
            trn = str(count)
        else:
            trn = album.replace('.&ensp','')
        if GOTHAM_FIX:
            try:
                alturl = 'http://www.myfreemp3.eu/music/%s+%s' % (artist.replace('&amp; ', '').replace('& ', '').replace(' and ', ' '), songname.replace('&amp; ', '').replace('& ', '').replace(' and ', ' '))
                alturl = alturl.replace(' ', '+').lower()
                link = open_url(alturl)
                data = regex_from_to(link, 'data-aid=', '"').replace('"','').replace('\\','')
                url = 'http://myfreemp3.eu/play/%s_24662006e9/' % data
                response = requests.get(url,allow_redirects=False)
                url = response.headers['location']
            except:
                url = find_url(trn).strip() + id
        else:
            url = 'https://listen.musicmp3.ru/' + id  #'http://files.musicmp3.ru/lofi/' + id #find_url(trn).strip() + id
        songname = songname.replace('&amp;', 'and')
        if 'musicmp3' in origurl:
            artist = artist.replace('&amp;', 'and')
            album = album.replace('&amp;', 'and')
            title = "%s. %s" % (track.replace('track',''), songname)
        elif 'goldenmp3' in origurl:
            artist = nartist.replace('&amp;', 'and')
            ntrack = album.replace('&amp;', 'and')
            album = nalbum.replace('&amp;', 'and')
            title = "%s. %s - %s" % (count, ntrack, songname)
        else:
            artist = artist.replace('&amp;', 'and')
            album = name.replace('&amp;', 'and')
            title = "%s. %s" % (trn, songname)
            dur=str((int(dur.split(':')[0])*60) + int(dur.split(':')[1]))
        addDirAudio(title, url, 10, iconimage, songname, artist, album, dur, '')
        if 'musicmp3' in origurl:
            url, liz = playerMP3.getListItem(songname, artist, album, trn, iconimage, dur, url, fanart, 'true', GOTHAM_FIX_2)
        elif 'goldenmp3' in origurl:
            url, liz = playerMP3.getListItem(ntrack, songname, album, trn, iconimage, dur, url, fanart, 'true', GOTHAM_FIX_2)
        else:
            url, liz = playerMP3.getListItem(songname, artist, album, trn, iconimage, dur, url, fanart, 'true', GOTHAM_FIX_2)
        if FOLDERSTRUCTURE=="0":
            stored_path = os.path.join(MUSIC_DIR, artist, album, songname + '.mp3')
        else:
            stored_path = os.path.join(MUSIC_DIR, artist + ' - ' + album, songname + '.mp3')
        if os.path.exists(stored_path):
            url = stored_path
        playlist.append((url, liz))
        if mix != 'mix':
            progress = len(playlist) / float(nItem) * 100
            dp.update(int(progress), 'Adding to Your Playlist',title)
            if dp.iscanceled():
                return
    pl = get_XBMCPlaylist(clear)
    for url ,liz in playlist:
        pl.add(url,liz)
        #if pl.size() > 3:
        #    break
    dp.close()
    if float(xbmc_version) < 17:
        newPlay(pl, clear)
    else:
        if clear or (not xbmc.Player().isPlayingAudio()):
            xbmc.Player().play(pl)

def play_song(url, name, songname, artist, album, iconimage, dur, clear):
    import playerMP3
    try:
        track = int(name[:name.find('.')])
    except:
        track = 0
    url, liz = playerMP3.getListItem(songname, artist, album, track, iconimage, dur, url, fanart, 'true', GOTHAM_FIX_2)
    title=name
    if FOLDERSTRUCTURE=="0":
        stored_path = os.path.join(MUSIC_DIR, artist, album, title + '.mp3')
    else:
        stored_path = os.path.join(MUSIC_DIR, artist + ' - ' + album, title + '.mp3')
    if os.path.exists(stored_path):
        url = stored_path
    pl = get_XBMCPlaylist(clear)
    pl.add(url, liz)
    if float(xbmc_version) < 17:
        newPlay(pl, clear)
    else:
        if clear or (not xbmc.Player().isPlayingAudio()):
            xbmc.Player().play(pl)
    #if clear or (not xbmc.Player().isPlayingAudio()):
        #xbmc.Player().play(pl)
    #playlist.append((newurl, liz))
    #for blob ,liz in playlist:
    #    try:
    #        if blob:
    #            pl.add(blob,liz)
    #    except:
    #        pass
    #newPlay(pl, clear)

def download_song(url, name, songname, artist, album, iconimage):
    track = songname[:songname.find('.')]
    artist_path = create_directory(MUSIC_DIR, artist)
    album_path = create_directory(artist_path, album)
    list_data = "%s<>%s<>%s<>%s<>%s%s" % (album_path,artist,album,track,songname,'.mp3')
    local_filename = album_path + '/' + songname + '.mp3'
    headers = {'Host': 'listen.musicmp3.ru','Range': 'bytes=0-','User-Agent': 'AppleWebKit/<WebKit Rev>', 'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5'}
    r = requests.get(url, headers=headers, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(): #chunk_size=1024
            if chunk:
                f.write(chunk)
                f.flush()
    #urllib.urlretrieve(url, local_filename)
    add_to_list(list_data, DOWNLOAD_LIST, False)
'''
class DownloadMusicThread(Thread):
    def __init__(self, name, url, data_path, album_path):
        self.data = url
        self.path = data_path
        self.extpath = album_path
        Thread.__init__(self)

    def run(self):
        path = str(self.path)
        data = self.data
        extract = str(self.extpath)
        urllib.urlretrieve(data, path)
        notify = "%s,%s,%s" % ('XBMC.Notification(Download finished',clean_file_name(name, use_blanks=False),'4000)')
        xbmc.executebuiltin(notify)
        if mode!="download song":
            notify = "%s,%s,%s" % ('XBMC.Notification(Extracting songs',clean_file_name(name, use_blanks=False),'4000)')
            xbmc.executebuiltin(notify)
            time.sleep(1)
            extractfiles(path,extract)
            os.remove(path)
            notify = "%s,%s,%s" % ('XBMC.Notification(Finished',clean_file_name(name, use_blanks=False),'4000)')
            xbmc.executebuiltin(notify)
'''
def download_album(url, name, iconimage):
    nartist = name.split(' - ')[0]
    xbmc.log("nartist = {0}".format(nartist), xbmc.LOGNOTICE)
    nalbum = name.split(' - ')[1]
    xbmc.log("nalbum = {0}".format(nalbum), xbmc.LOGNOTICE)
    if GOLDEN_PATH:
        url = url.replace('http','https').replace('musicmp3','www.goldenmp3').replace('artist_','/').replace('__album_','/').replace('.html','')
    origurl = url
    xbmc.log("origurl = {0}".format(origurl), xbmc.LOGNOTICE)
    dialog = xbmcgui.Dialog()
    check_downloads = os.path.join(MUSIC_DIR, 'downloading.txt')
    xbmc.log("check_downloads = {0}".format(check_downloads), xbmc.LOGNOTICE)
    if os.path.exists(check_downloads):
        dialog.ok("Album download in progress", 'Please wait for the current download to finish')
        return
    playlist = []
    link = GET_url(url)
    xbmc.log("link = {0}".format(link), xbmc.LOGNOTICE)
    notification(name, 'Download started', '3000', iconimage)
    if 'goldenmp3' in url:
        link = regex_from_to(link,'<table class="title_list">','<div>Total')
        match = re.compile('itemscope="(.+?)" itemtype="http://schema.org/MusicRecording"><td><a class="play" href="#" rel="(.+?)" title="Listen the song in low quality">(.+?)</a>(.+?)<td><div class="title_td_wrap">(.+?)<span itemprop="(.+?)am(.+?)">(.+?)</span>&ensp;(.+?)<div class="jp-seek-bar"><div class="jp-play-bar"></div></div></div></td><td>').findall(link)
    else:
        match = re.compile('<tr class="song" id="(.+?)" itemprop="tracks" itemscope="itemscope" itemtype="http://schema.org/MusicRecording"><td class="song__play_button"><a class="player__play_btn js_play_btn" href="#" rel="(.+?)" title="Play track"/></td><td class="song__name"><div class="title_td_wrap"><meta content="(.+?)" itemprop="url"/><meta content="(.+?)" itemprop="duration"/><meta content="(.+?)" itemprop="inAlbum"/><meta content="(.+?)" itemprop="byArtist"/><span itemprop="name">(.+?)</span><div class="jp-seek-bar" data-time="(.+?)">').findall(link)
    xbmc.log("match = {0}".format(match), xbmc.LOGNOTICE)
    nSong = len(match)
    count = 0
    for track, id, songurl, meta, album, artist, songname, dur in match:
        count += 1
        songname = songname.replace('&amp;', 'and')
        if 'goldenmp3' in origurl:
            artist = nartist.replace('&amp;', 'and')
            album = nalbum.replace('&amp;', 'and')
            track = str(count)
        artist = artist.replace('&amp;', 'and')
        album = album.replace('&amp;', 'and')
        trn = track.replace('track','')
        #url = find_url(trn).strip() + id
        url = 'https://listen.musicmp3.ru/' + id #'http://files.musicmp3.ru/lofi/' + id
        playlist.append(songname)
        title = "%s. %s" % (track.replace('track',''), songname)
        artist_path = create_directory(MUSIC_DIR, artist)
        album_path = create_directory(artist_path, album)
        list_data = "%s<>%s<>%s<>%s<>%s%s" % (album_path,artist,album,trn,title,'.mp3')
        download_lock_file = create_file(MUSIC_DIR, "downloading.txt")
        local_filename = album_path + '/' + title + '.mp3'
        headers = {'Host':'listen.musicmp3.ru', 'Range':'bytes=0-', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0', 'Accept':'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5','Referer':'https://www.goldenmp3.ru'}
        r = requests.get(url, headers=headers, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        #urllib.urlretrieve(url, local_filename)
        text = "%s of %s tracks downloaded" % (trn, nSong)
        notification(artist + ' ' + album, text, '3000', iconimage)
        add_to_list(list_data, DOWNLOAD_LIST, False)
    notification(name.split(' - ')[0] + ' ' + name.split(' - ')[1], 'Album download finished', '3000', iconimage)
    if os.path.exists(download_lock):
        os.remove(download_lock)

def clear_lock():
    if os.path.exists(download_lock):
        os.remove(download_lock)
        notification('Downloads', 'Unlocked', '3000', iconart)

def id3_tags():
    id3Thread = Getid3Thread()
    id3Thread.start()

class Getid3Thread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if os.path.isfile(DOWNLOAD_LIST):
            s = read_from_file(DOWNLOAD_LIST)
            search_list = s.split('\n')
            for list in search_list:
                if list != '':
                    splitlist = list.split('<>')
                    filename = os.path.join(splitlist[0], splitlist[4])
                    artist = splitlist[1]
                    album = splitlist[2]
                    track = splitlist[3]
                    trackname = splitlist[4]
                    tracktitle = trackname
                    if os.path.exists(filename):
                        audio = MP3(filename, ID3=EasyID3)
                        audio["title"] = tracktitle
                        audio["artist"] = artist
                        audio["album"] = album
                        audio["tracknumber"] = track
                        audio.save()
                        remove_from_list(list, DOWNLOAD_LIST)
        notification('Music Library', 'ID3 tags updated', '3000', iconart)
        xbmc.executebuiltin('UpdateLibrary(music)')

def get_artist_icon(name, url):
    xbmc.log("724 name = {0}\nurl = {1}".format(name, url), xbmc.LOGNOTICE)
    data_path = os.path.join(ARTIST_ART, name + '.jpg')
    xbmc.log("726 datapath = {0}".format(data_path), xbmc.LOGNOTICE)
    if not os.path.exists(data_path):
        dlThread = DownloadIconThread(name, url, data_path)
        dlThread.start()

def instant_mix():
    menu_texts = []
    menu_texts.append("All Songs")
    dialog = xbmcgui.Dialog()
    if os.path.isfile(FAV_SONG):
        s = read_from_file(FAV_SONG)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                try:
                    plname = list1[5]
                    if not plname in menu_texts:
                        menu_texts.append(plname)
                except:
                    if not "Ungrouped" in menu_texts:
                        menu_texts.append("Ungrouped")
    menu_id = dialog.select('Select Group', menu_texts)
    if(menu_id < 0):
        return (None, None)
        dialog.close()
    groupname = menu_texts[menu_id]
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()
    if os.path.isfile(FAV_SONG):
        s = read_from_file(FAV_SONG)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                splitdata = list.split('<>')
                artist = splitdata[0]
                album = splitdata[1]
                songname = splitdata[2]
                url1 = splitdata[3].replace('listen.musicmp3.ru', 'files.musicmp3.ru/lofi')
                iconimage = splitdata[4]
                try:
                    plname = splitdata[5]
                except:
                    plname = "Ungrouped"
                if (plname == groupname) or groupname == "All Songs":
                    play_song(url1,songname.upper(),songname.upper(),artist.upper(),album.upper(),iconimage, '',False)
    playlist.shuffle()

def instant_mix_album():
    menu_texts = []
    menu_texts.append("All Albums")
    dialog = xbmcgui.Dialog()
    if os.path.isfile(FAV_ALBUM):
        s = read_from_file(FAV_ALBUM)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                try:
                    plname = list1[3]
                    if not plname in menu_texts:
                        menu_texts.append(plname)
                except:
                    if not "Ungrouped" in menu_texts:
                        menu_texts.append("Ungrouped")
    menu_id = dialog.select('Select Group', menu_texts)
    if(menu_id < 0):
        return (None, None)
        dialog.close()
    groupname = menu_texts[menu_id]
    shuffleThread = ShuffleAlbumThread(groupname)
    shuffleThread.start()

class ShuffleAlbumThread(Thread):
    def __init__(self,groupname):
        self.groupname=groupname
        Thread.__init__(self)

    def run(self):
        groupname=self.groupname
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()
        if os.path.isfile(FAV_ALBUM):
            s = read_from_file(FAV_ALBUM)
            search_list = s.split('\n')
            for list in search_list:
                if list != '':
                    list1 = list.split('<>')
                    title = list1[0]
                    url = list1[1]
                    thumb = list1[2]
                    try:
                        plname = list1[3]
                    except:
                        plname = "Ungrouped"
                    if (plname == groupname) or groupname == "All Albums":
                        play_album(title, url, thumb,'mix',False)
                        playlist.shuffle()
                    time.sleep(15)

class DownloadIconThread(Thread):
    def __init__(self, name, url, data_path):
        self.data = url
        self.path = data_path
        Thread.__init__(self)

    def run(self):
        path = str(self.path)
        data = self.data
        urllib.urlretrieve(data, path)


def favourite_artists():
    if os.path.isfile(FAV_ARTIST):
        s = read_from_file(FAV_ARTIST)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                title = list1[0]
                url = list1[1]
                icon_path = os.path.join(ARTIST_ART, title + '.jpg')
                if os.path.exists(icon_path):
                    iconimage = icon_path
                else:
                    iconimage = iconart
                addDir(title.replace('&amp;', '&').upper(),url,22,iconimage,'artists')

def favourite_albums():
    menu_texts = []
    menu_texts.append("All Albums")
    dialog = xbmcgui.Dialog()
    if os.path.isfile(FAV_ALBUM):
        s = read_from_file(FAV_ALBUM)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                try:
                    plname = list1[3]
                    if not plname in menu_texts:
                        menu_texts.append(plname)
                except:
                    if not "Ungrouped" in menu_texts:
                        menu_texts.append("Ungrouped")
    menu_id = dialog.select('Select Group', menu_texts)
    if(menu_id < 0):
        return (None, None)
        dialog.close()
    groupname = menu_texts[menu_id]
    if os.path.isfile(FAV_ALBUM):
        s = read_from_file(FAV_ALBUM)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                title = list1[0]
                url = list1[1]
                thumb = list1[2]
                try:
                    plname = list1[3]
                except:
                    plname = "Ungrouped"
                if (plname == groupname) or groupname == "All Albums":
                    addDir(title.replace('&amp;', '&').upper(),url,5,thumb,plname + 'qqalbums')

def favourite_songs():
    menu_texts = []
    menu_texts.append("All Songs")
    dialog = xbmcgui.Dialog()
    if os.path.isfile(FAV_SONG):
        s = read_from_file(FAV_SONG)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                try:
                    plname = list1[5]
                    if not plname in menu_texts:
                        menu_texts.append(plname)
                except:
                    if not "Ungrouped" in menu_texts:
                        menu_texts.append("Ungrouped")
    menu_id = dialog.select('Select Group', menu_texts)
    if(menu_id < 0):
        return (None, None)
        dialog.close()
    groupname = menu_texts[menu_id]
    if os.path.isfile(FAV_SONG):
        s = read_from_file(FAV_SONG)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                artist = list1[0]
                album = list1[1]
                title = list1[2]
                url = list1[3].replace('listen.musicmp3.ru', 'files.musicmp3.ru/lofi')
                iconimage = list1[4]
                try:
                    plname = list1[5]
                except:
                    plname = "Ungrouped"
                text = "%s - %s - %s" % (title, artist, album)
                if (plname == groupname) or groupname == "All Songs":
                    addDirAudio(text.upper(),url,10,iconimage,title,artist,album,'qq' + plname,'favsong')

def add_favourite(name, url, dir, text):
    splitdata = url.split('<>')
    if 'artist' in dir:
        artist = splitdata[0]
        url1 = splitdata[1]
        add_to_list(url, dir, True)
        notification(name.upper(), "[COLOR lime]" + text + "[/COLOR]", '5000','')
        link = GET_url(url1)
        try:
            artist_url = regex_from_to(link, 'class="art_wrap__img" src="', '"')
            get_artist_icon(artist, artist_url)
            xbmc.log("977 artist = {0}\nartist_url = {1}".format(artist, artist_url), xbmc.LOGNOTICE)
        except:
            pass
    else:
        menu_texts = []
        menu_texts.append("Add New Group")
        dialog = xbmcgui.Dialog()
        if os.path.isfile(dir):
            s = read_from_file(dir)
            search_list = s.split('\n')
            for list in search_list:
                if list != '':
                    list1 = list.split('<>')
                    try:
                        plname = list1[3]
                        if not plname in menu_texts:
                            menu_texts.append(plname)
                    except:
                        pass
        menu_id = dialog.select('Select Group', menu_texts)
        if(menu_id < 0):
            return (None, None)
            dialog.close()
        if (menu_id == 0):
            keyboard = xbmc.Keyboard('', 'Create New Group', False)
            keyboard.doModal()
            if keyboard.isConfirmed():
                query = keyboard.getText()
                if len(query) > 0:
                    plname = query
        else:
            plname = menu_texts[menu_id]
        artist = splitdata[0]
        url1 = splitdata[1]
        thumb = splitdata[2]
        url = "%s<>%s" % (url, plname)
        if 'artist' in dir:
            add_to_list(url, dir, True)
        else:
            add_to_list(url, dir, False)
        notification(name.upper(), "[COLOR lime]" + text + "[/COLOR]", '5000', thumb)

def add_favourite_song(name, url, dir, text):
    menu_texts = []
    menu_texts.append("Add New Group")
    dialog = xbmcgui.Dialog()
    if os.path.isfile(FAV_SONG):
        s = read_from_file(FAV_SONG)
        search_list = s.split('\n')
        for list in search_list:
            if list != '':
                list1 = list.split('<>')
                try:
                    plname = list1[5]
                    if not plname in menu_texts:
                        menu_texts.append(plname)
                except:
                    pass
    menu_id = dialog.select('Select Group', menu_texts)
    if(menu_id < 0):
        return (None, None)
        dialog.close()
    if (menu_id == 0):
        keyboard = xbmc.Keyboard('', 'Create New Group', False)
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            if len(query) > 0:
                plname = query
    else:
        plname = menu_texts[menu_id]
    splitdata = url.split('<>')
    artist = splitdata[0]
    album = splitdata[1]
    songname = splitdata[2]
    url1 = splitdata[3]
    iconimage = splitdata[4]
    url = "%s<>%s" % (url, plname)
    add_to_list(url, dir, False)
    notification(songname.upper(), "[COLOR lime]" + text + "[/COLOR]", '5000',iconimage)

def remove_from_favourites(name, url, dir, text):
    splitdata = url.split('<>')
    artist = splitdata[0]
    url1 = splitdata[1]
    thumb = splitdata[2]
    remove_from_list(url, dir)
    notification(name.upper(), "[COLOR orange]" + text + "[/COLOR]", '5000', thumb)

def find_list(query, search_file):
    try:
        content = read_from_file(search_file)
        lines = content.split('\n')
        index = lines.index(query)
        return index
    except:
        return -1

def add_to_list(list, file, refresh):
    if find_list(list, file) >= 0:
        return
    if os.path.isfile(file):
        content = read_from_file(file)
    else:
        content = ""
    lines = content.split('\n')
    s = '%s\n' % list
    for line in lines:
        if len(line) > 0:
            s = s + line + '\n'
    write_to_file(file, s)
    if refresh == True:
        xbmc.executebuiltin("Container.Refresh")

def remove_from_list(list, file):
    list = list.replace('<>Ungrouped', '').replace('All Songs', '')
    index = find_list(list, file)
    if index >= 0:
        content = read_from_file(file)
        lines = content.split('\n')
        lines.pop(index)
        s = ''
        for line in lines:
            if len(line) > 0:
                s = s + line + '\n'
        write_to_file(file, s)
        if not 'song' in file and not 'album' in file:
            xbmc.executebuiltin("Container.Refresh")

def write_to_file(path, content, append=False, silent=False):
    try:
        if append:
            f = open(path, 'a')
        else:
            f = open(path, 'w')
        f.write(content)
        f.close()
        return True
    except:
        if not silent:
            print("Could not write to " + path)
        return False

def read_from_file(path, silent=False):
    try:
        f = open(path, 'r')
        r = f.read()
        f.close()
        return str(r)
    except:
        if not silent:
            print("Could not read from " + path)
        return None

def notification(title, message, ms, nart):
    xbmc.executebuiltin("XBMC.notification(" + title + "," + message + "," + ms + "," + nart + ")")

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
            params = sys.argv[2]
            cleanedparams = params.replace('?','')
            if (params[len(params)-1] == '/'):
                    params = params[0:len(params)-2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                    splitparams = {}
                    splitparams = pairsofparams[i].split('=')
                    if (len(splitparams)) == 2:
                            param[splitparams[0]] = splitparams[1]
    return param

def get_XBMCPlaylist(clear):
    pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    if clear:
        pl.clear()
    return pl

def clear_playlist():
    pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    pl.clear()
    notification('Playlist', 'Cleared', '2000', iconart)

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

def regex_from_to(text, from_string, to_string, excluding=True):
    if excluding:
        r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
    else:
        r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
    return r

def regex_get_all(text, start_with, end_with):
    r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
    return r

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)

def addLink(name,url,iconimage):
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Audio", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', audio_fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
        return ok

def addDir(name, url, mode, iconimage, type):
        type1 = type
        type = type.replace('qq','')
        suffix = ""
        if type == "artists":
            list = "%s<>%s" % (str(name).lower(),url)
        else:
            if 'qq' in type1:
                spltype1 = type1.split('qq')
                list = "%s<>%s<>%s<>%s" % (str(name).lower(),url,str(iconimage),spltype1[0])
            else:
                list = "%s<>%s<>%s" % (str(name).lower(),url,str(iconimage))
        list = list.replace(',', '')
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&list="+str(list)+"&type="+str(type)
        ok = True
        contextMenuItems = []
        if type == "artists":
            if find_list(list, FAV_ARTIST) < 0:
                suffix = ""
                contextMenuItems.append(("[COLOR lime]Add to Favourite Artists[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=61)'%(sys.argv[0], name, str(list))))
            else:
                suffix = ' [COLOR lime]+[/COLOR]'
                contextMenuItems.append(("[COLOR orange]Remove from Favourite Artists[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=62)'%(sys.argv[0], name, str(list))))
        if 'album' in type:
            download_album = '%s?name=%s&url=%s&iconimage=%s&mode=202' % (sys.argv[0], urllib.quote(name), url, iconimage)
            xbmc.log("1230 sys.argv[0] = {0}\nurllib.quote(name) = {1}\nurl = {2}\niconimage = {3}".format(sys.argv[0], urllib.quote(name), url, iconimage), xbmc.LOGNOTICE)
            contextMenuItems.append(('[COLOR cyan]Download Album[/COLOR]', 'XBMC.RunPlugin(%s)' % download_album))
            if os.path.exists(download_lock):
                contextMenuItems.append(("Clear Download Lock",'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=333)'%(sys.argv[0], urllib.quote(name), url, iconimage)))
            if QUEUE_ALBUMS:
                play_music = '%s?name=%s&url=%s&iconimage=%s&mode=7' % (sys.argv[0], urllib.quote(name), url, iconimage)
                contextMenuItems.append(('[COLOR cyan]Play/Browse Album[/COLOR]', 'XBMC.RunPlugin(%s)' % play_music))
            else:
                queue_music = '%s?name=%s&url=%s&iconimage=%s&mode=6' % (sys.argv[0], urllib.quote(name), url, iconimage)
                contextMenuItems.append(('[COLOR cyan]Queue Album[/COLOR]', 'XBMC.RunPlugin(%s)' % queue_music))
            if not 'qq' in type1:
                suffix = ""
                contextMenuItems.append(("[COLOR lime]Add to Favourite Albums[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=64)'%(sys.argv[0], name.replace(',', ''), str(list))))
            else:
                suffix = ' [COLOR lime]+[/COLOR]'
                contextMenuItems.append(("[COLOR orange]Remove from Favourite Albums[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=65)'%(sys.argv[0], name.replace(',', ''), str(list))))
        liz = xbmcgui.ListItem(name + suffix, iconImage="DefaultAudio.png", thumbnailImage=iconimage)
        liz.addContextMenuItems(contextMenuItems, replaceItems=False)
        liz.setInfo( type="Audio", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addDirAudio(name, url, mode, iconimage, songname, artist, album, dur, type):
        suffix = ""
        if 'qq' in dur:
            list = "%s<>%s<>%s<>%s<>%s<>%s" % (str(artist),str(album),str(songname).lower(),url,str(iconimage),str(dur).replace('qq',''))
        else:
            list = "%s<>%s<>%s<>%s<>%s" % (str(artist),str(album),str(songname).lower(),url,str(iconimage))
        list = list.replace(',', '')
        contextMenuItems = []
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&songname="+urllib.quote_plus(songname)+"&artist="+urllib.quote_plus(artist)+"&album="+urllib.quote_plus(album)+"&dur="+str(dur)+"&type="+str(type)
        ok=True
        if os.path.exists(download_lock):
            contextMenuItems.append(("Clear Download Lock",'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&songname=%s&artist=%s&album=%s&mode=333)'%(sys.argv[0], songname, url, iconimage,name,artist,album)))
        download_song = '%s?name=%s&url=%s&iconimage=%s&songname=%s&artist=%s&album=%s&mode=201' % (sys.argv[0], songname, url, iconimage,name,artist,album)
        contextMenuItems.append(('[COLOR cyan]Download Song[/COLOR]', 'XBMC.RunPlugin(%s)' % download_song))
        if QUEUE_SONGS:
            play_song = '%s?name=%s&url=%s&iconimage=%s&songname=%s&artist=%s&album=%s&dur=%s&mode=18' % (sys.argv[0], urllib.quote(songname), url, iconimage,songname,artist,album,dur)
            contextMenuItems.append(('[COLOR cyan]Play Song[/COLOR]', 'XBMC.RunPlugin(%s)' % play_song))
        else:
            queue_song = '%s?name=%s&url=%s&iconimage=%s&songname=%s&artist=%s&album=%s&dur=%s&mode=11' % (sys.argv[0], urllib.quote(songname), url, iconimage,songname,artist,album,dur)
            contextMenuItems.append(('[COLOR cyan]Queue Song[/COLOR]', 'XBMC.RunPlugin(%s)' % queue_song))
        if type != 'favsong':
            suffix = ""
            contextMenuItems.append(("[COLOR lime]Add to Favourite Songs[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=67)'%(sys.argv[0], name.replace(',', ''), str(list))))
        else:
            suffix = ' [COLOR lime]+[/COLOR]'
            contextMenuItems.append(("[COLOR orange]Remove from Favourite Songs[/COLOR]",'XBMC.RunPlugin(%s?name=%s&url=%s&mode=68)'%(sys.argv[0], name.replace(',', ''), str(list))))
        liz = xbmcgui.ListItem(name + suffix, iconImage="DefaultAudio.png", thumbnailImage=iconimage)
        liz.addContextMenuItems(contextMenuItems, replaceItems=False)
        liz.setInfo( type="Audio", infoLabels={ "Title": name } )
        if HIDE_FANART == False:
            liz.setProperty('fanart_image', fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

params = get_params()
url = None
name = None
mode = None
songname = None
artist= None
album = None
iconimage = None 
dur = None
type = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        iconimage = urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        songname = urllib.unquote_plus(params["songname"])
except:
        pass
try:
        artist = urllib.unquote_plus(params["artist"])
except:
        pass
try:
        album = urllib.unquote_plus(params["album"])
except:
        pass
try:
        list = str(params["list"])
except:
        pass
try:
        dur = str(params["dur"])
except:
        pass
try:
        type = str(params["type"])
except:
        pass

if mode == None or url==None or len(url)<1:
    CATEGORIES()
    #get_cookie()

elif mode == 4:
     charts()

elif mode ==5:
    if QUEUE_ALBUMS:
        play_album(name, url, iconimage, 'queue', False)
    else:
        play_album(name, url, iconimage, '', True)

elif mode ==6:
    play_album(name, url, iconimage,'', False)

elif mode ==7:
    play_album(name, url, iconimage,'browse', False)

elif mode ==8:
    ADDON.openSettings()

elif mode == 10:
    if QUEUE_SONGS:
        play_song(url, name, songname, artist, album, iconimage, dur, False)
    else:
        play_song(url, name, songname, artist, album, iconimage, dur, True)

elif mode == 11:
    play_song(url, name, songname, artist, album, iconimage, dur, False)

elif mode == 18:
    play_song(url, name, songname, artist, album, iconimage, dur, True)

elif mode == 21:
    artists(url)

elif mode == 31:
    all_artists(name, url)

elif mode == 41:
    sub_dir(name, url, iconimage)

elif mode == 22:
    albums(name, url)

elif mode == 12:
    genres(name, url)

elif mode == 13:
    all_genres(name, url)

elif mode == 14:
    genre_sub_dir(name, url, iconimage)

elif mode == 16:
    genre_sub_dir2(name, url, iconimage)

elif mode == 15:
    album_list(name, url)

elif mode == 24:
    search(name, url)

elif mode == 25:
    search_albums(name)

elif mode == 26:
    search_songs(name)

elif mode == 27:
    search_artists(name)

elif mode == 28:
    search_songs(url)

elif mode == 61:
    add_favourite(name, url, FAV_ARTIST, "Added to Favourites")

elif mode == 62:
    remove_from_favourites(name, url, FAV_ARTIST, "Removed from Favourites")

elif mode == 63:
    favourite_artists()

elif mode == 64:
    add_favourite(name, url, FAV_ALBUM, "Added to Favourites")

elif mode == 65:
    remove_from_favourites(name, url, FAV_ALBUM, "Removed from Favourites")

elif mode == 67:
    add_favourite_song(name, url, FAV_SONG, 'Added to Favourites')

elif mode == 69:
    favourite_songs()

elif mode == 68:
    remove_from_favourites(name, url, FAV_SONG, "Removed from Favourites")

elif mode == 66:
    favourite_albums()

elif mode == 99:
    instant_mix()

elif mode == 89:
    instant_mix_album()

elif mode == 100:
    clear_playlist()

elif mode == 101:
    charts()

elif mode == 102:
    chart_lists(name, url)

elif mode == 201:
    download_song(url, name, songname, artist, album, iconimage)

elif mode == 202:
    download_album(url, name, iconimage)

elif mode == 300:
    id3_tags()

elif mode == 333:
    clear_lock()

elif mode == 400:
   compilations_menu()

elif mode == 401:
   compilations_list(name, url, iconimage, type)

elif mode == 500:
    ADDON.openSettings()


elif mode == 999:
    import playerMP3
    playerMP3.play(sys, params)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
