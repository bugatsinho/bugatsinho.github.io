# -*- coding: utf-8 -*-
import xbmcgui
import xbmcaddon
import xbmc
import re
import sys
import six
from resources.lib.modules import client, user_agents
from resources.lib.modules import control, tools
from resources.lib.modules import view
from resources.lib.modules import dom_parser as dom
from resources.lib.modules.addon import Addon

ADDON       = xbmcaddon.Addon()
ADDON_DATA  = ADDON.getAddonInfo('profile')
ADDON_PATH  = ADDON.getAddonInfo('path')
DESCRIPTION = ADDON.getAddonInfo('description')
FANART      = ADDON.getAddonInfo('fanart')
ICON        = ADDON.getAddonInfo('icon')
ID          = ADDON.getAddonInfo('id')
NAME        = ADDON.getAddonInfo('name')
VERSION     = ADDON.getAddonInfo('version')
Lang        = ADDON.getLocalizedString
Dialog      = xbmcgui.Dialog()
addon = Addon(ID, sys.argv)
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

Baseurl = 'https://www.ddlvalley.me' #control.
headers = {'User-Agent': user_agents.agent(), 'Referer': Baseurl}
allfun = [
    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)
]


def menu():
    addon.add_directory({'mode': 'to_items', 'url': Baseurl + '/category/movies/'},
                        {'title': '[B][COLOR yellow]Latest Movies[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'to_items', 'url': Baseurl + '/category/tv-shows/'},
                        {'title': '[B][COLOR yellow]Latest TV Shows[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'movies'},
                        {'title': '[B][COLOR gold]Movies[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'series'},
                        {'title': '[B][COLOR gold]TV Shows[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def movies_menu():
    # addon.add_directory({'mode': 'to_etos'},
    #                     {'title': '[B][COLOR gold]' + Lang(32034).encode('utf-8') + '[/COLOR][/B]'},
    #                     allfun, img=ICON, fanart=FANART)
    addon.add_directory({'mode': 'to_genre', 'url': Baseurl, 'section': 'movies'},
                        {'title': '[B][COLOR gold]' + control.get_lang(32035) + '[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'to_items', 'url': Baseurl + '/category/movies/'},
                        {'title': control.get_lang(32000)},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def series_menu():
    addon.add_directory({'mode': 'to_genre', 'url': Baseurl, 'section': 'tvshows'},
                        {'title': '[B][COLOR gold]' + control.get_lang(32035) + '[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'to_items', 'url': Baseurl + '/category/tv-shows/'},
                        {'title': control.get_lang(32001)},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def etos():
    from datetime import datetime
    dt = datetime.today()
    year = dt.year
    for etos in range(int(year) - 0, 1980, -1):
        titlos = str(etos)
        link = ''.join([Baseurl, '/tag/{}'.format(str(etos))])
        addon.add_directory({'mode': 'to_items', 'url': link},
                            {'title': titlos, 'plot': titlos}, allfun, img=ICON, fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def genre(section):
    sec = 'category/movies' if 'mov' in section else 'category/tv-shows'
    html = six.ensure_text(client.request(Baseurl, headers=headers))
    items = client.parseDOM(html, 'ul', attrs={'class': 'cat'})[0]
    # xbmc.log('DDLVALLEY-GENRE: {}'.format(str(items)))
    pattern = r'''<a href=(.+?)\s*data-wpel-link=internal>(.+?)</a> <a.+?</.+?\((.+?)\)'''
    items = re.findall(pattern, items, re.DOTALL)
    # xbmc.log('DDLVALLEY-GENRE2: {}'.format(str(items)))
    items = [(i[0], i[1], i[2]) for i in items if sec in i[0]]
    for i in items:
        if 'tv-pack' in i[0]:
            continue
        title = i[1]
        title = tools.clear_Title(title)
        title = '{} ([COLORyellow]{}[/COLOR])'.format(six.ensure_text(title, errors='ignore'), six.ensure_text(i[2], errors='ignore'))
        url = i[0]
        addon.add_directory({'mode': 'to_items', 'url': url},
                            {'title': title, 'plot': title}, allfun, img=ICON, fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def to_items(url): #34
    data = six.ensure_text(client.request(url, headers=headers))
    posts = zip(client.parseDOM(data, 'div', attrs={'id': r'post-\d+'}),
                client.parseDOM(data, 'h2'))
    for post, name in posts:
        try:
            plot = client.parseDOM(post, 'div', attrs={'class': 'plot'})[0]
        except IndexError:
            plot = 'N/A'
        desc = client.replaceHTMLCodes(plot)
        desc = tools.clear_Title(desc)
        desc = six.ensure_text(desc, errors='ignore')
        try:
            title = client.parseDOM(name, 'a')[0]
        except BaseException:
            title = client.parseDOM(name, 'img', ret='alt')[0]
        # try:
        #     year = client.parseDOM(data, 'div', {'class': 'metadata'})[0]
        #     year = client.parseDOM(year, 'span')[0]
        #     year = '[COLOR lime]({0})[/COLOR]'.format(year)
        # except IndexError:
        #     year = '(N/A)'
        title = tools.clear_Title(title)
        title = '[B][COLOR white]{}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
        link = client.parseDOM(name, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(six.ensure_text(link, errors='ignore'))
        poster = client.parseDOM(post, 'img', ret='src')[0]
        poster = client.replaceHTMLCodes(six.ensure_text(poster, errors='ignore'))
        # if '/tvshows/' in link:
        #     addon.add_directory({'mode': 'to_seasons', 'url': link}, {'title': title, 'plot': str(desc)},
        #                         allfun, img=poster, fanart=FANART)
        # else:
        addon.add_directory({'mode': 'to_links', 'url': link}, {'title': title, 'plot': str(desc)},
                            allfun, img=poster, fanart=FANART)
    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'rel': 'next'})[0]
        # np = dom_parser.parse_dom(np, 'a', req='href')
        # np = [i.attrs['href'] for i in np if 'icon-chevron-right' in i.content][0]
        page = re.findall(r'page/(\d+)/', np)[0]
        title = control.get_lang(32010) + ' [COLORwhite]([COLORlime]{}[/COLOR])[/COLOR]'.format(page)
        addon.add_directory({'mode': 'to_items', 'url': np},
                            {'title': title},
                            img=ART + 'next_page.png', fanart=FANART)
    except BaseException:
        pass
    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


def to_links(url, img, plot):  # Get Links
    try:
        import resolveurl
        from resources.lib.modules import init
        # html = response_html(url, '3')
        html = six.ensure_text(client.request(url, headers=headers))
        try:
            # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
            match = client.parseDOM(html, 'h1')[0]
            match = re.findall(r'(.+?)\.(\d{4}|S\d+E\d+)\.', match)[0]
            listitem = match
        except IndexError:
            match = client.parseDOM(html, 'h1')[0]
            match = re.sub('<.+?>', '', match)
            listitem = match
        name = '%s (%s)' % (listitem[0].replace('.', ' '), listitem[1])

        main = client.parseDOM(html, 'div', {'id': r'post-\d+'})
        # main = [i for i in main if i]

        try:
            comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
            main += [i.content for i in comments if i]
        except IndexError:
            pass
        links = []
        for item in main:
            frames = client.parseDOM(item, 'a', ret='href')
            for url in frames:
                host = tools.GetDomain(url)
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
                    title = title.replace('DDLValley.me_', ' ')
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
                            {'mode': 'PlayVideo', 'url': url, 'img': img, 'title': name,
                             'plot': plot},
                            {'title': title, 'plot': plot},
                            [(control.lang(32007).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                             (control.lang(32008).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                             (control.lang(32009).encode('utf-8'),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                            img=img, fanart=FANART, is_folder=False)
                    else:
                        links.append((host, title, url, name))

        if control.setting('test.links') == 'true':
            threads = []
            for i in links:
                threads.append(tools.Thread(tools.link_tester, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            for item in tools.tested_links:
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
            control.lang(32012).encode('utf-8'),
            NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})