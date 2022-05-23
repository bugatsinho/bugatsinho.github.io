# -*- coding: utf-8 -*-
import xbmcgui
import xbmcaddon
import six
import re
import sys
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import user_agents
from resources.lib.modules import tools
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
Lang        = control.lang
Dialog      = xbmcgui.Dialog()
addon = Addon(ID, sys.argv)
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

Baseurl = 'https://www.scnsrc.me/'
ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.329'
headers = {'User-Agent': ua, 'Referer': Baseurl}

allfun = [
    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)
]

def menu():
    addon.add_directory({'mode': 'scn_items', 'url': Baseurl + 'category/films/'},
                        {'title': '[B][COLOR yellow]Latest Movies[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'scn_items', 'url': Baseurl + 'category/tv/'},
                        {'title': '[B][COLOR yellow]Latest TV Shows[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'scn_movies'},
                        {'title': '[B][COLOR gold]Movies[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'scn_series'},
                        {'title': '[B][COLOR gold]TV Shows[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})

def movies_menu():
    addon.add_directory({'mode': 'scn_genre', 'url': Baseurl, 'section': 'movies'},
                        {'title': '[B][COLOR gold]' + control.get_lang(32035) + '[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'scn_items', 'url': Baseurl + 'category/films/'},
                        {'title': control.get_lang(32000)},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def series_menu():
    addon.add_directory({'mode': 'scn_genre', 'url': Baseurl, 'section': 'tvshows'},
                        {'title': '[B][COLOR gold]' + control.get_lang(32035) + '[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'scn_items', 'url': Baseurl + 'category/tv/'},
                        {'title': control.get_lang(32001)},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def genre(section):
    sec = 'category/films' if 'mov' in section else 'category/tv'
    html = six.ensure_text(client.request(Baseurl, headers=headers))
    items = client.parseDOM(html, 'ul', attrs={'class': 'categories'})[0]
    # xbmc.log('SCNSRC-GENRE2: {}'.format(str(items)))
    pattern = r'''<a href=(.+?)>(.+?)</a> <a.+?</.+?\((.+?)\)'''
    items = re.findall(pattern, items, re.DOTALL)
    # xbmc.log('SCNSRC-GENRE2: {}'.format(str(items)))
    items = [(i[0], i[1], i[2]) for i in items if sec in i[0]]
    for i in items:
        if 'tv-pack' in i[0]:
            continue
        title = i[1]
        title = tools.clear_Title(title)
        title = six.ensure_text(title, errors='ignore')
        title = '{} ([COLORyellow]{}[/COLOR])'.format(title, str(i[2]))
        url = i[0].split(' ')[0]
        addon.add_directory({'mode': 'scn_items', 'url': url},
                            {'title': title, 'plot': title}, allfun, img=ICON, fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def to_items(url): #34
    data = six.ensure_text(client.request(url, headers=headers))
    posts = client.parseDOM(data, 'div', attrs={'id': r'post-\d+'})
    # xbmc.log('SCNSRC-ITEMS: {}'.format(str(posts)))
    for post in posts:
        try:
            plot = client.parseDOM(post, 'div', attrs={'class': 'storycontent'})[0]
            plot = client.parseDOM(plot, 'p')
            plot = [i for i in plot if 'Synopsis' in i][0]
        except IndexError:
            plot = 'N/A'

        desc = client.replaceHTMLCodes(plot)
        desc = tools.clear_Title(desc)
        desc = six.ensure_text(desc, errors='ignore')
        # xbmc.log('SCNSRC-PLOT: {}'.format(str(desc)))
        try:
            name = client.parseDOM(post, 'h2')
            title = client.parseDOM(name, 'a')[0]
        except IndexError:
            title = client.parseDOM(post, 'img', ret='alt')[0]

        # try:
        #     year = client.parseDOM(data, 'div', {'class': 'metadata'})[0]
        #     year = client.parseDOM(year, 'span')[0]
        #     year = '[COLOR lime]({0})[/COLOR]'.format(year)
        # except IndexError:
        #     year = '(N/A)'
        title = tools.clear_Title(title)
        title = '[B][COLOR white]{}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
        link = client.parseDOM(post, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = six.ensure_text(link, errors='ignore')
        poster = client.parseDOM(post, 'img', ret='src')[0]
        poster = six.ensure_text(poster, errors='ignore')
        poster = client.replaceHTMLCodes(poster)
        # if '/tvshows/' in link:
        #     addon.add_directory({'mode': 'to_seasons', 'url': link}, {'title': title, 'plot': str(desc)},
        #                         allfun, img=poster, fanart=FANART)
        # else:
        addon.add_directory({'mode': 'scn_links', 'url': link, 'title': title, 'plot': str(desc), 'img': poster},
                            {'title': title, 'plot': str(desc)}, allfun, img=poster, fanart=FANART)
    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'rel': 'next'})[0]
        # np = dom_parser.parse_dom(np, 'a', req='href')
        # np = [i.attrs['href'] for i in np if 'icon-chevron-right' in i.content][0]
        page = re.findall(r'page/(\d+)/', np)[0]
        title = control.lang(32010).encode('utf-8') + \
                ' [COLORwhite]([COLORlime]{}[/COLOR])[/COLOR]'.format(page)
        addon.add_directory({'mode': 'scn_items', 'url': np},
                            {'title': title},
                            img=ART + 'next_page.png', fanart=FANART)
    except BaseException:
        pass
    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


def to_links(url, img, plot):  # Get Links
    try:
        html = six.ensure_text(client.request(url, headers=headers))
        try:
            # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
            match = client.parseDOM(html, 'h2')[0]
            match = re.findall(r'(.+?)\s+(\d{4}|S\d+E\d+|S\d+)', match, re.I)[0]
            listitem = match
        except IndexError:
            match = client.parseDOM(html, 'h2')[0]
            match = re.sub('<.+?>', '', match)
            listitem = match
        name = '%s (%s)' % (listitem[0].replace('.', ' '), listitem[1])
        # xbmc.log('SCNSRC-NAME: {}'.format(str(name)))
        main = client.parseDOM(html, 'div', {'id': 'comment_list'})[0]
        main = client.parseDOM(main, 'p')
        # main = [i for i in main if i]
        # xbmc.log('SCNSRC-MAIN: {}'.format(str(main)))
        try:
            comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
            main += [i.content for i in comments if i]
        except IndexError:
            pass
        links = []
        import resolveurl
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
                title = '{} - {}'.format(host, title)
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




