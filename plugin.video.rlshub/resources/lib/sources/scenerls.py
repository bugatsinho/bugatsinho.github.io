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

Baseurl = 'https://scene-rls.net/'
headers = {'User-Agent': user_agents.agent(), 'Referer': Baseurl}
allfun = [
    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)
]


def menu():
    addon.add_directory({'mode': 'scene_items', 'url': Baseurl + 'category/movies/'},
                        {'title': '[B][COLOR yellow]Latest Movies[/COLOR][/B]'},
                        allfun, img=ART + 'movies.png', fanart=FANART)
    addon.add_directory({'mode': 'scene_items', 'url': Baseurl + 'category/tv-shows/'},
                        {'title': '[B][COLOR yellow]Latest TV Shows[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'scene_tvpacks', 'url': Baseurl + 'category/tv-packs/'},
                        {'title': '[B][COLOR gold]TV PACKS[/COLOR][/B]'},
                        allfun, img=ART + 'tv_shows.png', fanart=FANART)
    addon.add_directory({'mode': 'search_menu_scene'}, {'title': control.get_lang(32002)},
                        allfun, img=ART + 'search.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def to_items(url): #34
    data = client.request(url, headers=headers)
    # xbmc.log('SCENE-data: {}'.format(str(data)))
    match = client.parseDOM(data, 'div', attrs={'class': 'post'})
    # xbmc.log('SCENE-ITEMS: {}'.format(str(match)))
    for item in match:
        # xbmc.log('SCENE-ITEM: {}'.format(str(item)))
        movieUrl = client.parseDOM(item, 'a', ret='href')[0]
        name = client.parseDOM(item, 'a')[0]
        try:
            img = client.parseDOM(item, 'img', ret='src')[0]
            # img = img.replace('.ru', '.to')
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
        desc = tools.Sinopsis(desc)
        name = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(name, errors='ignore'))
        mode = 'scene_tvpacks_items' if 'tv-packs' in url else 'scene_links'
        addon.add_directory({'mode': mode, 'url': movieUrl, 'img': img, 'plot': desc},
                            {'title': name, 'plot': desc}, allfun, img=img, fanart=FANART)
    # if 'Older Entries' not in data:
    #     break
    # # keep iterating until the last page is reached

    if 'Older Entries' in data:

        url = client.parseDOM(data, 'span', attrs={'id': 'olderEntries'})[0]
        url = client.parseDOM(url, 'a', ret='href')[0]
        addon.add_directory({'mode': 'scene_items', 'url': url},
                            {'title': control.get_lang(32010)},
                            img=ART + 'next_page.png', fanart=FANART)

    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


def to_links(url, img, plot):  # Get Links
    try:
        html = client.request(url, headers=headers)
        try:
            # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
            match = client.parseDOM(html, 'h2')[0]
            match = re.findall(r'(.+?)\.(\d{4}|S\d+E\d+)\.', match)[0]
            listitem = match
        except IndexError:
            match = client.parseDOM(html, 'h2')[0]
            match = re.sub('<.+?>', '', match)
            listitem = match
        name = '{} ({})'.format(six.ensure_text(listitem[0], errors='ignore').replace('.', ' '), six.ensure_text(listitem[1], errors='ignore'))
        main = list()
        try:
            main = client.parseDOM(html, 'div', {'class': 'postContent'})
        except IndexError:
            pass
        main = [i for i in main if i]
        comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
        main += [i.content for i in comments if i]
        links = []
        import resolveurl
        frames = client.parseDOM(main, 'a', ret='href')
        for url in frames:
            host = tools.GetDomain(url)
            if 'Unknown' in host:
                continue
            # ignore .rar files
            if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.', '.part']) \
                    or any(url.lower().endswith(x) for x in ['.rar', '.zip', '.iso', '.part']):
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
                    (control.get_lang(32008),
                     'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
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


def to_get_pack(url, img, plot):  # TV packs links
    try:
        # html = response_html(url, '3')
        html = client.request(url, headers=headers)
        main = client.parseDOM(html, 'div', {'class': 'postContent'})[0]
        data = re.findall(r'''<p style.+?>(.+?)<.+?<h2.+?>(.+?)</h2''', main, re.DOTALL)
        data = [(i[0], i[1]) for i in data if '/nfo.' in i[1]]
        # xbmc.log('SCENE-data: {}'.format(str(data)))
        for i in data:
            title = i[0]
            title = tools.clear_Title(title)
            title = '[B][COLORgold]{0}[/COLOR][/B]'.format(six.ensure_text(title, errors='ignore'))
            frames = dom.parse_dom(i[1], 'a', req='href')
            frames = [i.attrs['href'] for i in frames if not 'uploadgig' in i.content.lower()]
            frames = [i for i in frames if 'nfo.' in i]
            addon.add_directory({'mode': 'scene_tvpacks_links', 'url': frames, 'img': img, 'plot': plot},
                                {'title': title, 'plot': plot},
                                [(control.get_lang(32007),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                                 (control.get_lang(32008),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                                 (control.get_lang(32009),
                                  'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                                img=img, fanart=FANART)

    except BaseException:
        control.infoDialog(
            control.lang(32012).encode('utf-8'),
            NAME, ICON, 5000)
    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def to_get_links_pack(url, img, plot, listitem):
    try:
        check = False
        urls = eval(url)
        frames = []
        for u in urls:
            # html = response_html(u, '72')
            html = client.request(u, headers=headers)
            data = client.parseDOM(html, 'ol')[0]
            frames += client.parseDOM(data, 'a', ret='href')
            try:
                check = re.findall(r'\.(S\d+E\d+)\.', data, re.I)[0]
                if check:
                    check = True
                    hdlr = re.compile(r'\.(S\d+E\d+)\.', re.I)
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
            host = tools.GetDomain(frame)
            host = '[B][COLORcyan]{0}[/COLOR][/B]'.format(six.ensure_text(host, errors='ignore'))
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

def scene_search():
    url = 'http://scene-rls.net/'
    search_url = 'http://scene-rls.net/?s={}&submit=Find'
    from resources.lib.modules import user_agents
    from resources.lib.modules.compat import quote_plus
    headers = {'User-Agent': user_agents.randomagent(),
               'Referer': url}
    keyboard = xbmc.Keyboard()
    keyboard.setHeading(control.get_lang(32002))
    keyboard.doModal()
    if keyboard.isConfirmed():
        _query = keyboard.getText()
        query = six.ensure_text(_query, encoding='utf-8')
        query = quote_plus(query)
        # get_link = client.request(url.format(query), output='location')
        search_url = search_url.format(query)
        # xbmc.log('SEARCH-URL: {}'.format(search_url))
        # data = client.request(query)
        try:
            to_items(search_url)
        except IndexError:
            pass
    else:
        return
    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})