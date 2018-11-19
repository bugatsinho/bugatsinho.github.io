# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import urllib
import urlparse
import re
import sys
import os
import resolveurl
import random
import json
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import dom_parser as dom
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net


try:
    from sqlite3 import dbapi2 as sqlite
    print "Loading sqlite3 as DB engine"
except BaseException:
    from pysqlite2 import dbapi2 as sqlite
    print "Loading pysqlite2 as DB engine"

addon_id = 'plugin.video.releaseBB'
plugin = xbmcaddon.Addon(id=addon_id)
DB = os.path.join(xbmc.translatePath("special://database"), 'cache.db')
BASE_URL = 'http://rlsbb.to'
net = Net()
addon = Addon('plugin.video.releaseBB', sys.argv)


##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', None)
title = addon.queries.get('title', None)
img = addon.queries.get('img', None)
text = addon.queries.get('text', None)
plot = addon.queries.get('plot', None)
##### paths ##########
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/icons/"


def MainMenu():    #homescreen
    addon.add_directory({'mode': 'Categories', 'section': 'movies'},
                        {'title':  '[COLOR orange][B]Release BB [COLOR blue]Movies [/COLOR][/B]'},
                        img=IconPath + 'movie.png', fanart=FANART)
    addon.add_directory({'mode': 'Categories', 'section': 'tv-shows'},
                        {'title':  '[COLOR orange][B]Release BB [COLOR blue]Tv Shows [/COLOR][/B]'},
                        img=IconPath + 'tv.png', fanart=FANART)
    addon.add_directory({'mode': 'GetSearchQuery9'},  {'title':  '[COLOR orange][B]ReleaseBB [COLOR yellow]Search[/COLOR][/B]'},
                        img=IconPath + 'search.png', fanart=FANART)
    addon.add_directory({'mode': 'RealDebrid'},  {'title':  '[COLOR gold][B]Real Debrid Auth[/B][/COLOR]'},
                        img=IconPath + 'rd.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR cyan][B]Resolver Settings[/B][/COLOR]'}, 
                        img=IconPath + 'resolver.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'ClearCache'}, {'title': '[COLOR red][B]Clear Cache[/B][/COLOR]'},
                        img=ICON, fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'help'}, {'title':  '[COLOR gold][B][I]https://bugatsinho.github.io[/B][/I][/COLOR]'},
                        img='https://bugatsinho.github.io/images/bug.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'forceupdate'}, {'title': '[COLOR gold][B]Version:' + ' [COLOR lime]%s[/COLOR][/B]' % version},
                        img=ICON, fanart=FANART, is_folder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def Categories(section):  # categories
    sec = '/category/%s' % section
    html = cache.get(client.request, 96, BASE_URL)
    match = client.parseDOM(html, 'li', attrs={'id': 'categories-2'})[0]
    items = zip(client.parseDOM(match, 'a'),
                client.parseDOM(match, 'a', ret='href'))
    items = [(i[0], i[1]) for i in items if sec in i[1]]
    for title, link in items:
        title = title.encode('utf-8')
        link = client.replaceHTMLCodes(link)
        addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': link,
                             'startPage': '1', 'numOfPages': '2'}, {'title': title},
                            img='https://pbs.twimg.com/profile_images/834058861669654528/p7gDr9C6_400x400.jpg',
                            fanart=FANART)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def GetTitles(section, url, startPage= '1', numOfPages= '1'): # Get Movie Titles
    try:
        if int(startPage) > 1:
            pageUrl = urlparse.urljoin(url, 'page/%d' % int(startPage))
        else:
            pageUrl = url

        html = cache.get(client.request, 3, pageUrl)
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range(start, end):
            if page != start:
                pageUrl = urlparse.urljoin(url, 'page/%s' % page)
                html = cache.get(client.request, 3, pageUrl)
            match = client.parseDOM(html, 'div', attrs={'class': 'post'})
            match = [(client.parseDOM(i, 'a', ret='href')[0],
                      client.parseDOM(i, 'a')[0],
                      client.parseDOM(i, 'img', ret='src')[1],
                      client.parseDOM(i, 'div', attrs={'class': 'postContent'})[0]) for i in match if i]
            #match = re.compile('postHeader.+?href="(.+?)".+?>(.+?)<.+?src=.+? src="(.+?).+?(Plot:.+?)</p>"', re.DOTALL).findall(html)
            for movieUrl, name, img, desc in match:
                img = img.replace('rlsbb.ru/', 'rlsbb.to/')
                desc = Sinopsis(desc)

                addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl, 'img': img, 'plot': desc},
                                    {'title':  name, 'plot': desc}, img=img, fanart=FANART)
            if 'Older Entries' not in html:
                    break
        # keep iterating until the laast page is reached
        if 'Older Entries' in html:
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages},
                                    {'title': '[COLOR orange][B][I]Older Entries...[/B][/I][/COLOR]'},
                                    img=IconPath + 'nextpage.png', fanart=FANART)
    except BaseException:
        control.infoDialog('[COLOR red][B]Ooops![/B][/COLOR],[COLOR lime][B]Something wrong!![/B][/COLOR]', 7000, '')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


def GetLinks(section, url, img, plot): # Get Links
    try:
        html = cache.get(client.request, 3, url)
        listitem = GetMediaInfo(html)
        name = '%s (%s)' % (listitem[0], listitem[1])
        main = client.parseDOM(html, 'div', {'class': 'postContent'})
        main = [i for i in main if i]
        comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
        main += [i.content for i in comments if i]
        for item in main:
            frames = client.parseDOM(item, 'a', ret='href')
            for url in frames:
                host = GetDomain(url)
                if 'Unknown' in host:
                    continue

                # ignore .rar files
                if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.'])\
                        or any(url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']):
                    continue
                if any(x in url.lower() for x in ['sample', 'zippyshare']):
                    continue

                print '*****************************' + host + ' : ' + url
                if resolveurl.HostedMediaFile(url=url):
                    print 'in GetLinks if loop'
                    title = url.rpartition('/')
                    title = title[2].replace('.html', '')
                    title = title.replace('.htm', '')
                    title = title.replace('.rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('www.', '')
                    title = title.replace ('-', ' ')
                    title = title.replace('_', ' ')
                    title = title.replace('.', ' ')
                    title = title.replace('480p', '[COLOR coral][B][I]480p[/B][/I][/COLOR]')
                    title = title.replace('720p', '[COLOR gold][B][I]720p[/B][/I][/COLOR]')
                    title = title.replace('1080p', '[COLOR orange][B][I]1080p[/B][/I][/COLOR]')
                    title = title.replace('1080i', '[COLOR orange][B][I]1080i[/B][/I][/COLOR]')
                    title = title.replace('mkv', '[COLOR gold][B][I]MKV[/B][/I][/COLOR] ')
                    title = title.replace('avi', '[COLOR pink][B][I]AVI[/B][/I][/COLOR] ')
                    title = title.replace('mp4', '[COLOR purple][B][I]MP4[/B][/I][/COLOR] ')
                    host = host.replace('youtube.com', '[COLOR red][B][I]Movie Trailer[/B][/I][/COLOR]')
                    addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem, 'img': img, 'title': name, 'plot': plot},
                                        {'title':  host + ' : ' + title, 'plot': plot}, img=img, fanart=FANART, is_folder=False)


    except BaseException:
        control.infoDialog("[COLOR red][B]Sorry there was a problem ![/B][/COLOR],[COLOR lime][B]Please try again !![/B][/COLOR]", 7000, "")
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


def PlayVideo(url, title, img, plot):
    try:
        stream_url = resolveurl.resolve(url)
        liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=img)
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": plot})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except BaseException:
        control.infoDialog('[COLOR red][B]Sorry Link may have been removed ![/B][/COLOR],[COLOR lime][B]Please try a different link/host !![/B][/COLOR]', 7000, '')


def GetDomain(url):
    elements = urlparse.urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res:
        domain = res.group(1)
    domain = domain.lower()
    return domain



def GetMediaInfo(html):
    try:
        #<h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.findall('(.+?)\s+(\d{4}|S\d+E\d+)', match)[0]
        return match
    except BaseException:
        return []


def Sinopsis(txt):
    OPEN = txt.encode('utf8') #re.findall('''((Plot:.+?)</p>|</p>\n<p>(.+?)</p><p>)''', desc, re.DOTALL | re.I)[0]
    try:
        Sinopsis = re.findall('(Plot:.+?)</p>', OPEN, flags=re.DOTALL)[0]
        if not Sinopsis:
            Sinopsis = re.findall('</p>\n<p>(.+?)</p><p>', OPEN, flags=re.DOTALL)[0]
        part = re.sub('<.*?>', '', Sinopsis)
        part = re.sub('\.\s+', '.', part)
        desc = clear_Title(part)
        desc = desc.decode('ascii', errors='ignore')
        return desc
    except BaseException:
        pass


def GetSearchQuery9():                 #search a
    last_search = addon.load_data('search')
    if not last_search:
        last_search = ''
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('[COLOR green]Search[/COLOR]')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        _query = keyboard.getText()
        addon.save_data('search', _query)
        Search9(_query.encode('utf-8'))
    else:
        return


def Search9(query):
    try:
        from resources.lib.modules import cfscrape
        scraper = cfscrape.create_scraper()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                   'Referer': 'http://rlsbb.ru'}
        query = urllib.quote_plus(query).replace('+', '%2B')
        url = 'http://search.rlsbb.ru/lib/search6515260491260.php?phrase=%s&pindex=1&&radit=0.%s' % (query, random.randint(00000000000000001, 99999999999999999))
        html = scraper.get(url, headers=headers).content
        posts = json.loads(html)['results']
        posts = [(i['post_name'], i['post_title']) for i in posts if i]
        for movieUrl, title in posts:
            movieUrl = urlparse.urljoin('http://rlsbb.to/', movieUrl)
            title = title.encode('utf-8')
            addon.add_directory({'mode': 'GetLinks', 'url': movieUrl}, {'title':  title}, img=IconPath + 'search.png', fanart=FANART)
    except BaseException:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':').replace('\n', ' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&amp;#038;', '&').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('&#8216;', '"').replace('\t', ' ')
    return txt


if mode == 'main': 
    MainMenu()
elif mode == 'Categories':
    Categories(section)
elif mode == 'GetTitles': 
    GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetLinks':
    GetLinks(section, url, img, plot)
elif mode == 'GetSearchQuery9':
    GetSearchQuery9()
elif mode == 'Search9':
    Search9(query)
elif mode == 'PlayVideo':
    PlayVideo(url, title, img, plot)
elif mode == 'ResolverSettings':
    resolveurl.display_settings()
elif mode == 'RealDebrid':
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)')
elif mode == 'ClearCache':
    cache.delete(control.cacheFile, False)
elif mode == 'forceupdate':
    control.infoDialog('Triggered a request for addon updates')
    control.execute('UpdateAddonRepos')

xbmcplugin.endOfDirectory(int(sys.argv[1]))
