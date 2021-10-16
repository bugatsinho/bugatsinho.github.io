# -*- coding: utf-8 -*-
import six

import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import xbmcplugin
import re
import sys
import os
import threading
from sys import argv
from six.moves.urllib.parse import urljoin, parse_qsl, urlparse, unquote_plus, quote_plus, quote, unquote
from six.moves import zip, urllib
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import tools
from resources.lib.modules import view
from resources.lib.modules import dom_parser as dom
from resources.lib.modules.addon import Addon

addon_id = 'plugin.video.rlshub'
plugin = xbmcaddon.Addon(id=addon_id)
DB = os.path.join(control.translatePath("special://database"), 'cache.db')
addon = Addon(addon_id, sys.argv)

##### Queries ##########
queries = dict(parse_qsl(argv[2][1:]))
mode = queries.get('mode', None)
url = queries.get('url', None)
content = queries.get('content', None)
query = queries.get('query', None)
startPage = queries.get('startPage', None)
numOfPages = queries.get('numOfPages', None)
listitem = queries.get('listitem', None)
urlList = queries.get('urlList', None)
section = queries.get('section', None)
title = queries.get('title', None)
img = queries.get('img', None)
text = queries.get('text', None)
plot = queries.get('plot', None)

##### paths ##########
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')

NAME = ADDON.getAddonInfo('name')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/resources/icons/"
BANNER = IconPath + "banner.png"
base = control.setting('domain')
BASE_URL = 'http://%s' % base.lower()

tested_links = []
allfun = [
    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)
]


def MainMenu():  # homescreen

    addon.add_directory({'mode': 'Categories', 'section': 'movies'},
                        {'title': control.get_lang(32000)},
                        allfun, img=IconPath + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'Categories', 'section': 'tv-shows'},
                        {'title': control.get_lang(32001)},
                        allfun, img=IconPath + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'search_menu'},
                        {'title': control.get_lang(32002)},
                        allfun, img=IconPath + 'search.png', fanart=FANART)

    downloads = True if control.setting('downloads') == 'true' and (
            len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or
            len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
    if downloads:
        addon.add_directory({'mode': 'downloadlist'}, {'title': control.get_lang(32003)},
                            allfun, img=IconPath + 'downloads.png', fanart=FANART)

    addon.add_directory({'mode': 'settings'}, {'title': control.get_lang(32004)},
                        allfun, img=IconPath + 'tools.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'setviews'}, {'title': control.get_lang(32005)},
                        allfun, img=IconPath + 'set_view.png', fanart=FANART)

    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def downloads_root():
    movie_downloads = control.setting('movie.download.path')
    tv_downloads = control.setting('tv.download.path')
    cm = [(control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)'),
          (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)')]
    if len(control.listDir(movie_downloads)[0]) > 0:
        item = control.item(label='Movies')
        item.addContextMenuItems(cm)
        item.setArt({'icon': IconPath + 'movies.png', 'fanart': FANART})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), movie_downloads, item, True)

    if len(control.listDir(tv_downloads)[0]) > 0:
        item = control.item(label='Tv Shows')
        item.addContextMenuItems(cm)
        item.setArt({'icon': IconPath + 'tv_shows.png', 'fanart': FANART})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), tv_downloads, item, True)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def Categories(section):  # categories
    sec = '/category/%s' % section
    # html = response_html(BASE_URL, '96')
    html = cloudflare_mode(BASE_URL)
    # xbmc.log('HTMLLLLL: %s' % html)
    match = client.parseDOM(html, 'aside', attrs={'id': 'categories-2'})[0]
    items = zip(client.parseDOM(match, 'a'),
                client.parseDOM(match, 'a', ret='href'))
    items = [(i[0], i[1]) for i in items if sec in i[1]]
    img = IconPath + 'movies.png' if 'movies' in section else IconPath + 'tv_shows.png'
    if 'movie' in section:
        addon.add_directory({'mode': 'recom', 'url': BASE_URL}, {'title': control.get_lang(32038)},
                            allfun, img=img, fanart=FANART)
        addon.add_directory({'mode': 'foreign', 'url': BASE_URL}, {'title': '[B][COLORgold]Foreign Movies[/COLOR][/B]'},
                            allfun, img=img, fanart=FANART)
    for title, link in items:
        title = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
        link = client.replaceHTMLCodes(link)
        addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': link, 'startPage': '1', 'numOfPages': '2'},
                            {'title': title}, allfun, img=img, fanart=FANART)

    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def foreign_movies(url):
    items = [('Bluray-1080p', '/category/foreign-movies/bluray-1080p-foreign-movies/'),
             ('Bluray-720p', '/category/foreign-movies/bluray-720p-foreign-movies/'),
             ('DVDRIP-BDRIP', '/category/foreign-movies/dvdrip-bdrip/'),
             ('WEBRIP-WEBDL', '/category/foreign-movies/webrip-web-dl/'),
             ('OLD', 'category/foreign-movies/old-foreign-movies/')]
    for title, link in items:
        title = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
        addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': BASE_URL + link,
                             'startPage': '1', 'numOfPages': '2'}, {'title': title}, allfun,
                            img=IconPath + 'movies.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def recommended_movies(url):
    try:
        # r = response_html(url, '8')
        r = cloudflare_mode(url)
        r = client.parseDOM(r, 'li', attrs={'id': r'text-\d+'})[-1]
        items = zip(client.parseDOM(r, 'a', ret='href'),
                    client.parseDOM(r, 'img', ret='src'))

        for item in items:
            movieUrl = urljoin(BASE_URL, item[0]) if not item[0].startswith('http') else item[0]
            name = movieUrl.split('/')[-1] if not movieUrl.endswith('/') else movieUrl[:-1].split('/')[-1]
            name = re.sub(r'-|\.', ' ', name)

            if 'search' in movieUrl:
                query = name.split('?s=')[1]
                query = query.replace('.', '+')
                action = {'mode': 'search_bb', 'url': query}
            else:
                action = {'mode': 'GetLinks', 'section': section, 'url': movieUrl, 'img': item[1], 'plot': 'N/A'}

            name = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(name, errors='ignore'))
            addon.add_directory(action, {'title': name, 'plot': 'N/A'}, allfun, img=item[1], fanart=FANART)

    except BaseException:
        control.infoDialog(
            control.lang(32011).encode('utf-8'), NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


def GetTitles(section, url, startPage='1', numOfPages='1'):  # Get Movie Titles
    try:
        if int(startPage) > 1:
            pageUrl = urljoin(url, 'page/%d' % int(startPage))
        else:
            pageUrl = url

        # html = response_html(pageUrl, '3')
        html = cloudflare_mode(pageUrl)
        # xbmc.log('RESULTOOOO: {}'.format(html))
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range(start, end):
            if page != start:
                pageUrl = urljoin(url, 'page/%s' % page)
                # html = response_html(pageUrl, '3')
                html = cloudflare_mode(pageUrl)
            match = client.parseDOM(html, 'div', attrs={'class': 'post'})
            for item in match:
                movieUrl = client.parseDOM(item, 'a', ret='href')[0]
                name = client.parseDOM(item, 'a')[0]
                try:
                    img = client.parseDOM(item, 'img', ret='src')[1]
                    img = img.replace('.ru', '.to')
                except:
                    img = ICON
                try:
                    desc = client.parseDOM(item, 'div', attrs={'class': 'postContent'})[0]
                except:
                    desc = 'N/A'

                # match = [(client.parseDOM(i, 'a', ret='href')[0],
                #           client.parseDOM(i, 'a')[0],
                #           client.parseDOM(i, 'img', ret='src')[1],
                #           client.parseDOM(i, 'div', attrs={'class': 'postContent'})[0]) for i in match if i]
                # match = re.compile('postHeader.+?href="(.+?)".+?>(.+?)<.+?src=.+? src="(.+?).+?(Plot:.+?)</p>"', re.DOTALL).findall(html)
                # for movieUrl, name, img, desc in match:
                desc = Sinopsis(desc)
                name = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(name, errors='ignore'))
                mode = 'GetPack' if 'tv-packs' in url else 'GetLinks'
                addon.add_directory({'mode': mode, 'section': section, 'url': movieUrl, 'img': img, 'plot': desc},
                                    {'title': name, 'plot': desc}, allfun, img=img, fanart=FANART)
            if 'Older Entries' not in html:
                break
        # keep iterating until the last page is reached
        if 'Older Entries' in html:
            addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages},
                                {'title': control.get_lang(32010)},
                                img=IconPath + 'next_page.png', fanart=FANART)
    except BaseException:
        control.infoDialog(control.get_lang(32011), NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


def GetPack(section, url, img, plot):  # TV packs links
    try:
        # html = response_html(url, '3')
        html = cloudflare_mode(url)
        main = client.parseDOM(html, 'div', {'class': 'postContent'})[0]
        data = client.parseDOM(main, 'p')
        data = [i for i in data if 'nfo1.' in i]
        for i in data:
            title = client.parseDOM(i, 'strong')[0]
            title = tools.clear_Title(title)
            title = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
            frames = dom.parse_dom(i, 'a', req='href')
            frames = [i.attrs['href'] for i in frames if not 'uploadgig' in i.content.lower()]
            frames = [i for i in frames if 'nfo1.' in i]
            addon.add_directory({'mode': 'GetLinksPack', 'section': section, 'url': frames, 'img': img, 'plot': plot},
                                {'title': title, 'plot': plot},
                                [(control.get_lang(32007),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                                 (control.get_lang(32008),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                                 (control.get_lang(32009),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                                img=img, fanart=FANART)

    except BaseException:
        control.infoDialog(control.get_lang(32012), NAME, ICON, 5000)
    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def GetLinksPack(section, url, img, plot):
    try:
        urls = eval(url)
        frames = []
        for u in urls:
            # html = response_html(u, '72')
            html = cloudflare_mode(u)
            data = client.parseDOM(html, 'ol')[0]
            frames += client.parseDOM(data, 'div')
            try:
                check = re.findall('.(S\d+E\d+).', data, re.I)[0]
                if check:
                    check = True
                    hdlr = re.compile(r'.(S\d+E\d+).', re.I)
                else:
                    check = re.findall(r'\.(\d+)\.', data, re.DOTALL)[0]
                    if check:
                        check = True
                        hdlr = re.compile(r'\.(\d+)\.')

            except IndexError:
                check = False

        if check:
            frames = sorted(frames, key=lambda x: hdlr.search(x).group(1))
        else:
            frames = frames

        for frame in frames:
            title = frame.split('/')[-1]
            host = GetDomain(frame)
            host = '[B][COLORcyan]{0}[/COLOR][/B]'.format(host.encode('utf-8'))
            title = '{0}-[B][COLORgold]{1}[/COLOR][/B]'.format(host, six.ensure_text(title, errors='ignore'))
            cm = [(control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                  (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                  (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)]
            downloads = True if control.setting('downloads') == 'true' and not (control.setting(
                'movie.download.path') == '' or control.setting('tv.download.path') == '') else False
            if downloads:
                cm.append((control.get_lang(32013),
                           'RunPlugin(plugin://plugin.video.rlshub/?mode=download&title=%s&img=%s&url=%s)' %
                           (title.split('-')[1], img, frame))
                          )
            addon.add_directory(
                {'mode': 'PlayVideo', 'url': frame, 'listitem': listitem, 'img': img, 'title': title, 'plot': plot},
                {'title': title, 'plot': plot}, cm, img=img, fanart=FANART, is_folder=False)

    except BaseException:
        control.infoDialog(
            control.get_lang(32012),
            NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def GetLinks(section, url, img, plot):  # Get Links
    try:
        import resolveurl
        from resources.lib.modules import init
        # html = response_html(url, '3')
        html = cloudflare_mode(url)
        listitem = GetMediaInfo(html)
        name = '%s (%s)' % (listitem[0], listitem[1])
        main = client.parseDOM(html, 'div', {'class': 'postContent'})
        main = [i for i in main if i]
        comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
        main += [i.content for i in comments if i]
        links = []
        for item in main:
            frames = client.parseDOM(item, 'a', ret='href')
            for url in frames:
                host = GetDomain(url)
                if 'Unknown' in host:
                    continue
                # ignore .rar files
                if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) \
                        or any(url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']):
                    continue
                if any(x in url.lower() for x in ['sample', 'zippyshare']):
                    continue

                addon.log('******* %s : %s' % (host, url))
                if resolveurl.HostedMediaFile(url=url):
                    addon.log('in GetLinks if loop')
                    title = url.rpartition('/')
                    title = title[2].replace('.html', '')
                    title = title.replace('.htm', '')
                    title = title.replace('.rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('www.', '')
                    title = title.replace('-', ' ')
                    title = title.replace('_', ' ')
                    title = title.replace('.', ' ')
                    title = title.replace('480p', '[COLOR coral][B][I]480p[/B][/I][/COLOR]')
                    title = title.replace('540p', '[COLOR coral][B][I]540p[/B][/I][/COLOR]')
                    title = title.replace('720p', '[COLOR gold][B][I]720p[/B][/I][/COLOR]')
                    title = title.replace('1080p', '[COLOR orange][B][I]1080p[/B][/I][/COLOR]')
                    title = title.replace('1080i', '[COLOR orange][B][I]1080i[/B][/I][/COLOR]')
                    title = title.replace('2160p', '[COLOR cyan][B][I]4K[/B][/I][/COLOR]')
                    title = title.replace('.4K.', '[COLOR cyan][B][I]4K[/B][/I][/COLOR]')
                    title = title.replace('mkv', '[COLOR gold][B][I]MKV[/B][/I][/COLOR] ')
                    title = title.replace('avi', '[COLOR pink][B][I]AVI[/B][/I][/COLOR] ')
                    title = title.replace('mp4', '[COLOR purple][B][I]MP4[/B][/I][/COLOR] ')
                    title = six.ensure_text(title, errors='ignore')
                    host = host.replace('youtube.com', '[COLOR red][B][I]Movie Trailer[/B][/I][/COLOR]')
                    if 'railer' in host:
                        title = six.ensure_text(host) + ' : ' + title
                        addon.add_directory(
                            {'mode': 'PlayVideo', 'url': url, 'listitem': listitem, 'img': img, 'title': name,
                             'plot': plot},
                            {'title': title, 'plot': plot},
                            [(control.get_lang(32007),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                             (control.get_lang(32008),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                             (control.get_lang(32009),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                            img=img, fanart=FANART, is_folder=False)
                    else:
                        links.append((host, title, url, name))

        if control.setting('test.links') == 'true':
            threads = []
            for i in links:
                threads.append(Thread(link_tester, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            for item in tested_links:
                link, title, name = item[0], item[1], item[2]
                title = six.ensure_text(title, errors='ignore')
                name = six.ensure_text(name, errors='ignore')
                cm = [
                    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)]
                downloads = True if control.setting('downloads') == 'true' and not (control.setting(
                    'movie.download.path') == '' or control.setting('tv.download.path') == '') else False
                if downloads:
                    # frame = resolveurl.resolve(link)
                    cm.append((control.get_lang(32013),
                               'RunPlugin(plugin://plugin.video.rlshub/?mode=download&title=%s&img=%s&url=%s)' %
                               (name, img, link))
                              )
                addon.add_directory(
                    {'mode': 'PlayVideo', 'url': link, 'listitem': listitem, 'img': img, 'title': name, 'plot': plot},
                    {'title': title, 'plot': plot}, cm, img=img, fanart=FANART, is_folder=False)

        else:
            for item in links:
                host, title, link, name = item[0], item[1], item[2], item[3]
                title = six.ensure_text(title, errors='ignore')
                name = six.ensure_text(name, errors='ignore')
                title = '%s - %s' % (host, title)
                cm = [
                    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)]
                downloads = True if control.setting('downloads') == 'true' and not (control.setting(
                    'movie.download.path') == '' or control.setting('tv.download.path') == '') else False
                if downloads:
                    cm.append((control.get_lang(32013),
                               'RunPlugin(plugin://plugin.video.rlshub/?mode=download&title=%s&img=%s&url=%s)' %
                               (name, img, link))
                              )
                addon.add_directory(
                    {'mode': 'PlayVideo', 'url': link, 'listitem': listitem, 'img': img, 'title': name, 'plot': plot},
                    {'title': title, 'plot': plot}, cm, img=img, fanart=FANART, is_folder=False)

    except BaseException:
        control.infoDialog(
            control.get_lang(32012),
            NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def cloudflare_mode(url):
    # from cloudscraper2 import CloudScraper
    # import requests
    # scraper = CloudScraper.create_scraper()
    # ua = client.agent()
    # scraper.headers.update({'User-Agent': ua})
    # cookies = scraper.get(url).cookies.get_dict()
    headers = {'User-Agent': client.agent(),
               'Referer': BASE_URL}
    import six
    result = six.ensure_str(client.request(url, headers=headers))
    # xbmc.log('RESULTTTTT: %s' % result)
    return result


##########################
###### EZTV TV ###########
##########################
eztv_base = control.setting('eztv.domain')
eztv_base = 'https://%s' % eztv_base.lower()


def eztv_menu():
    addon.add_directory({'mode': 'eztv_latest'}, {'title': 'Latest Releases'}, allfun,
                        img=IconPath + 'eztv.png', fanart=FANART)
    addon.add_directory({'mode': 'eztv_calendar', 'url': urljoin(eztv_base, '/calendar')},
                        {'title': 'Calendar'}, allfun, img=IconPath + 'eztv.png', fanart=FANART)
    addon.add_directory({'mode': 'eztv_search'}, {'title': 'Search'}, allfun,
                        img=IconPath + 'eztv.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def eztv_latest(url):
    html = client.request(eztv_base)
    posts = client.parseDOM(html, 'tr', attrs={'class': 'forum_header_border'})
    for post in posts:
        infos = dom.parse_dom(post, 'a')[1]
        title = infos.attrs['title'].encode('utf-8')
        page_link = infos.attrs['href']
        page_link = urljoin(eztv_base, page_link) if page_link.startswith('/') else page_link
        magnet = re.findall(r'href="(magnet:.+?)"', post, re.DOTALL)[0]
        addon.add_directory({'mode': 'open_page', 'url': page_link, 'img': img, 'plot': 'N/A'},
                            {'title': title}, allfun, img=img, fanart=FANART)

    try:
        np = dom.parse_dom(html, 'a', req='href')
        np = [i.attrs['href'] for i in np if 'next page' in i.content][0]
        np = urljoin(eztv_base, np)
        addon.add_directory({'mode': 'eztv_latest', 'url': np},
                            {'title': control.get_lang(32010)},
                            img=IconPath + 'eztv.png', fanart=FANART)
    except BaseException:
        pass

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def eztv_calendar(url):
    html = client.request(url)
    tables = client.parseDOM(html, 'table', attrs={'class': 'forum_header_border'})[1:]
    for table in tables:
        day = client.parseDOM(table, 'td', attrs={'class': 'forum_thread_header'})[0]
        day = '[B][COLORgold]{}[/B][/COLOR]'.format(day.strip().upper())
        addon.add_item({}, {'title': day}, allfun, img=IconPath + 'eztv.png', fanart=FANART)

        items = client.parseDOM(table, 'tr', attrs={'name': 'hover'})
        items = [i for i in items if 'alt="' in i]
        items = [(client.parseDOM(i, 'a', ret='href')[0],
                  client.parseDOM(i, 'img', ret='src')[0],
                  client.parseDOM(i, 'img', ret='alt')[0]) for i in items if i]
        for page_link, poster, name in items:
            poster = urljoin(eztv_base, poster) if poster.startswith('/') else poster
            page_link = urljoin(eztv_base, page_link) if page_link.startswith('/') else page_link
            addon.add_directory({'mode': 'open_show', 'url': page_link, 'img': poster, 'plot': 'N/A'},
                                {'title': name.encode('utf-8')}, allfun, img=poster, fanart=FANART)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def open_show(url):
    # xbmc.log('URLLLLL: {}'.format(url))
    html = client.request(url)
    try:
        alts = client.parseDOM(html, 'tr', attrs={'class': 'forum_header_border'})
        alts = [dom.parse_dom(str(i), 'a', req=['href', 'title'])[1] for i in alts if alts]

        for alt in alts:
            link, title = alt.attrs['href'], alt.attrs['title']
            link = urljoin(eztv_base, link) if link.startswith('/') else link
            addon.add_directory({'mode': 'open_page', 'url': link, 'img': img, 'plot': 'N/A'},
                                {'title': title}, allfun, img=img, fanart=FANART)
    except IndexError:
        pass

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def open_episode_page(url):
    html = client.request(url)
    try:
        poster = client.parseDOM(html, 'td', attrs={'align': 'center'})
        poster = [i for i in poster if 'img src=' in i][0]
        poster = client.parseDOM(poster, 'img', ret='src')[0]
        poster = urljoin(eztv_base, poster) if poster.startswith('/') else poster
    except IndexError:
        poster = IconPath + 'eztv.png'
    try:
        img = client.parseDOM(html, 'a', attrs={'class': 'pirobox'}, ret='href')[0]
        img = 'https:' + img if img.startswith('//') else img
        img = img.replace('large', 'small')
    except IndexError:
        img = FANART
    try:

        magnet = re.findall(r'href="(magnet:.+?)"', html, re.DOTALL)[0]
        title = client.parseDOM(html, 'title')[0].split(' EZTV')[0]
        addon.add_video_item({'mode': 'PlayVideo', 'url': magnet, 'img': img},
                             {'title': title}, allfun, img=poster, fanart=img)
    except IndexError:
        control.infoDialog(
            '[COLOR red][B]No Magnet Link available![/B][/COLOR]\n'
            '[COLOR lime][B]Please try other title!![/B][/COLOR]', NAME, ICON, 5000)
        return

    try:
        alts = client.parseDOM(html, 'tr', attrs={'class': 'forum_header_border'})
        alts = [dom.parse_dom(str(i), 'a', req=['href', 'title'])[0] for i in alts if alts]

        for alt in alts:
            link, title = alt.attrs['href'], alt.attrs['title']
            link = urljoin(eztv_base, link) if link.startswith('/') else link
            addon.add_directory({'mode': 'open_page', 'url': link, 'img': img, 'plot': 'N/A'},
                                {'title': title}, allfun, img=img, fanart=FANART)
    except IndexError:
        pass

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def eztv_search():
    url = 'https://eztv.io/search/?q1={}&q2=&search=Search'
    search_url = 'https://eztv.io/search/{}'
    keyboard = xbmc.Keyboard()
    keyboard.setHeading(control.lang(32002).encode('utf-8'))
    keyboard.doModal()
    if keyboard.isConfirmed():
        _query = keyboard.getText()
        query = _query.encode('utf-8')
        query = urllib.quote_plus(query).replace('+', '-')
        # get_link = client.request(url.format(query), output='location')
        search_url = search_url.format(query)
        # xbmc.log('SEARCH-URL: {}'.format(search_url))
        data = client.request(query)
        try:
            alts = client.parseDOM(data, 'tr', attrs={'class': 'forum_header_border'})
            alts = [dom.parse_dom(str(i), 'a', req=['href', 'title'])[0] for i in alts if alts]
            # xbmc.log('SEARCH-ALTSL: {}'.format(alts))
            for alt in alts:
                link, title = alt.attrs['href'], alt.attrs['title']
                link = urljoin(eztv_base, link) if link.startswith('/') else link
                addon.add_directory({'mode': 'open_page', 'url': link, 'img': img, 'plot': 'N/A'},
                                    {'title': title}, allfun, img=img, fanart=FANART)
        except IndexError:
            pass
    else:
        return
    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def download(title, img, url):
    control.busy()
    import json

    if url is None:
        return

    try:
        import resolveurl
        url = resolveurl.resolve(url)
    except Exception:
        control.idle()
        xbmcgui.Dialog().ok(NAME, 'Download failed', 'Your service can\'t resolve this hoster', 'or Link is down')
        return
    try:
        headers = dict(parse_qsl(url.rsplit('|', 1)[1]))
    except:
        headers = dict('')

    content = re.compile(r'(.+?)\s+[\.|\(|\[]S(\d+)E\d+[\.|\)|\]]', re.I).findall(title)
    transname = title.translate(None, r'\/:*?"<>|').strip('.')
    transname = re.sub(r'\[.+?\]', '', transname)
    levels = ['../../../..', '../../..', '../..', '..']

    if len(content) == 0:
        dest = control.setting('movie.download.path')
        dest = control.translatePath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        dest = os.path.join(dest, transname)
        control.makeFile(dest)
    else:
        dest = control.setting('tv.download.path')
        dest = control.translatePath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        tvtitle = re.sub(r'\[.+?\]', '', content[0])
        transtvshowtitle = tvtitle.translate(None, r'\/:*?"<>|').strip('.')
        dest = os.path.join(dest, transtvshowtitle)
        control.makeFile(dest)
        dest = os.path.join(dest, 'Season %01d' % int(content[0][1]))
        control.makeFile(dest)

    ext = os.path.splitext(urlparse(url).path)[1][1:]
    if ext not in ['mp4', 'mkv', 'flv', 'avi', 'mpg']: ext = 'mp4'
    dest = os.path.join(dest, transname + '.' + ext)
    headers = urllib.quote_plus(json.dumps(headers))

    from resources.lib.modules import downloader
    control.idle()
    downloader.doDownload(url, dest, title, img, headers)


def response_html(url, cachetime):
    try:
        resulto = client.request(url)
        if resulto is None:
            html = cache.get(cloudflare_mode, int(cachetime), url)
        else:
            html = cache.get(client.request, int(cachetime), url)

        if html is None:
            control.infoDialog(control.lang(32011).encode('utf-8'), NAME, ICON, 5000)

        else:
            return html
    except BaseException:
        control.infoDialog(control.lang(32011).encode('utf-8'), NAME, ICON, 5000)


def link_tester(item):
    try:
        host, title, link, name = item[0], item[1], item[2], item[3]
        # addon.log('URL Tested: [%s]: URL: %s ' % (host.upper(), link))
        na = ['has been deleted', 'file not found', 'file removed', 'sorry', 'step 1: select your plan']
        r = cloudflare_mode(link)
        if r is None:
            addon.log('NO result: [%s]: URL: %s ' % (host.upper(), link))
            return False, 'N/A'
        else:
            if any(i in r.lower() for i in na):
                addon.log('URL Removed: [%s]: URL: %s ' % (host.upper(), link))
                valid, size = False, 'N/A'
            else:
                if 'nitroflare' in host:
                    r = client.parseDOM(r, 'legend')[0]
                    # addon.log('@#@RESULT:%s' % r)
                elif 'rapidgator' in host:
                    r = re.findall('''(File size:.+?)MD5''', r, re.I | re.DOTALL)[0]
                    # addon.log('@#@RESULT:%s' % r)
                elif 'turbobit' in host:
                    r = client.parseDOM(r, 'title')[0]
                    r = r.replace('Мб', 'MB')
                    # addon.log('@#@RESULT:%s' % r)
                elif any(i in host.lower() for i in ['rockfile', 'clicknupload']):
                    r = 'N/A'
                elif 'openload' in host or 'oload' in host:
                    r = re.findall('''(File size:.+?)</div>''', r, re.I | re.DOTALL)[0]
                    # addon.log('@#@RESULT:%s' % r)
                else:
                    r = r
                try:
                    size = get_size(r)
                except:
                    size = 'N/A'
                valid, size = True, str(size)

            if valid:
                addon.log('URL PASSED: [%s]: URL: %s : SIZE: %s' % (host.upper(), link, size))
                title = '%s|[COLORlime][B]%s[/COLOR][/B]| - %s' % (host, size, title)
                tested_links.append((link, title, name))

    except BaseException:
        addon.log('URL ERROR: [%s]: URL: %s ' % (host.upper(), link))


def PlayVideo(url, title, img, plot):
    try:
        import resolveurl
        stream_url = resolveurl.resolve(url)
        liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=img)
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": plot})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except BaseException:
        control.infoDialog(
            '[COLOR red][B]Probably your service doesn\'t support this provider![/B][/COLOR]\n'
            '[COLOR lime][B]Please try a different link!![/B][/COLOR]', NAME, ICON, 5000)


def get_size(text):
    try:
        text = text.upper()
        size = re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|Gb|MB|MiB|Mb))', text)[-1]
        div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
        size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
        size = '%.2f GB' % size
        return size
    except BaseException:
        return 'N/A'


def GetDomain(url):
    elements = urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = r"(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res:
        domain = res.group(1)
    domain = domain.lower()
    return domain


def GetMediaInfo(html):
    try:
        # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.findall(r'(.+?)\s+(\d{4}|S\d+E\d+)', match)[0]
        return match
    except IndexError:
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.sub('<.+?>', '', match)
        return match


def Sinopsis(txt):
    OPEN = txt.encode('utf8')
    try:
        try:
            if 'Plot:' in OPEN:
                Sinopsis = re.findall('(Plot:.+?)</p>', OPEN, re.DOTALL)[0]
            else:
                Sinopsis = re.findall('</p>\n<p>(.+?)</p><p>', OPEN, re.DOTALL)[0]

        except:
            Sinopsis = re.findall('</p>\n<p>(.+?)</p>\n<p style', OPEN, re.DOTALL)[0]
        part = re.sub('<.*?>', '', Sinopsis)
        part = re.sub('\.\s+', '.', part)
        desc = tools.clear_Title(part)
        desc = desc.decode('ascii', errors='ignore')
        return desc
    except BaseException:
        return 'N/A'


def search_menu():
    addon.add_directory({'mode': 'search_bb', 'url': 'new'},
                        {'title': control.lang(32014).encode('utf-8')}, img=IconPath + 'search.png', fanart=FANART)
    try:
        from sqlite3 import dbapi2 as database
    except ImportError:
        from pysqlite2 import dbapi2 as database

    dbcon = database.connect(control.searchFile)
    dbcur = dbcon.cursor()

    try:
        dbcur.execute("""CREATE TABLE IF NOT EXISTS Search (url text, search text)""")
    except BaseException:
        pass

    dbcur.execute("SELECT * FROM Search ORDER BY search")

    lst = []

    delete_option = False
    for (url, search) in dbcur.fetchall():
        title = six.ensure_text(unquote_plus(search), 'utf-8')
        title = '[B]{}[/B]'.format(title)
        delete_option = True
        addon.add_directory({'mode': 'search_bb', 'url': search},
                            {'title': title},
                            [(control.lang(32007).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                             (control.lang(32015).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=del_search_item&query=%s)' % search,),
                             (control.lang(32008).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                             (control.lang(32009).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                            img=IconPath + 'search.png', fanart=FANART)
        lst += [(search)]
    dbcur.close()

    if delete_option:
        addon.add_directory({'mode': 'del_search_items'},
                            {'title': control.lang(32016).encode('utf-8')},
                            img=IconPath + 'search.png', fanart=FANART, is_folder=False)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def setviews():
    try:
        control.idle()

        items = [
            (control.lang(32017).encode('utf-8'), 'addons'),
            (control.lang(32018).encode('utf-8'), 'movies'),
            (control.lang(32019).encode('utf-8'), 'files')
        ]

        select = control.selectDialog([i[0] for i in items], 'SELECT')

        if select == -1:
            raise Exception()

        content = items[select][1]

        title = control.lang(32020).encode('utf-8')

        poster, banner, fanart = ICON, BANNER, FANART

        addon.add_directory({'mode': 'addView', 'content': content},
                            {'type': 'video', 'title': title, 'icon': poster, 'thumb': poster,
                             'poster': poster, 'banner': banner},
                            img=ICON, fanart=FANART)
        control.content(int(sys.argv[1]), content)
        control.directory(int(sys.argv[1]))
        view.setView(content, {})
    except:
        quit()


class Thread(threading.Thread):

    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


