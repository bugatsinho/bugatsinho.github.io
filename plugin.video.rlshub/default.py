# -*- coding: utf-8 -*-
import xbmcvfs
import xbmcgui
import xbmcaddon
import xbmcplugin
import urllib
import re
import sys
import os
from sys import argv
from six.moves.urllib.parse import parse_qsl, urlparse, unquote_plus, unquote, quote_plus
from resources.lib.modules import client
from resources.lib.modules import control, tools
from resources.lib.modules import cache
from resources.lib.modules import search
from resources.lib.modules import view
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
    addon.add_directory({'mode': 'open_news'}, {'title': '[COLOR lime][B]News - Updates[/COLOR][/B]'},
                        allfun, img=ICON, fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'scene'}, {'title': '[B][COLORwhite]SCENE RELEASE[/B][/COLOR]'},
                        allfun, img=IconPath + 'scenerls.png', fanart=FANART)
    addon.add_directory({'mode': 'twoddl'}, {'title': '[B][COLORwhite]TWODDL[/B][/COLOR]'},
                        allfun, img=IconPath + 'twoddl.png', fanart=FANART)
    addon.add_directory({'mode': 'ddlvalley',}, {'title': '[B][COLORwhite]DDLVALLEY[/B][/COLOR]'},
                        allfun, img=IconPath + 'ddlvalley.png', fanart=FANART)
    addon.add_directory({'mode': 'scnsrc'}, {'title': '[B][COLORwhite]SCENESOURCE[/B][/COLOR]'},
                        allfun, img=IconPath + 'scnsrc.png', fanart=FANART)
    addon.add_directory({'mode': 'rlsbb'}, {'title': '[B][COLORwhite]RELEASEBB[/B][/COLOR]'},
                        allfun, img=IconPath + 'rlsbb.png', fanart=FANART)
    addon.add_directory({'mode': 'eztv'}, {'title': '[B][COLORwhite]EZTV[/B][/COLOR]'},
                        allfun, img=IconPath + 'eztv.png', fanart=FANART)
    addon.add_directory({'mode': 'search_menu'}, {'title': control.get_lang(32002)},
                        allfun, img=IconPath + 'search.png', fanart=FANART)

    downloads = True if control.setting('downloads') == 'true' and (
            len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or
            len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
    if downloads:
        addon.add_directory({'mode': 'downloadlist'}, {'title': control.get_lang(32003)},
                            allfun, img=IconPath + 'downloads.png', fanart=FANART)

    # if control.setting('eztv_menu') == 'true':
    #     addon.add_directory({'mode': 'eztv'}, {'title': 'EZTV TV Shows'}, allfun,
    #                         img=IconPath + 'eztv.png', fanart=FANART)

    addon.add_directory({'mode': 'settings'}, {'title': control.get_lang(32004)},
                        allfun, img=IconPath + 'tools.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'setviews'}, {'title': control.get_lang(32005)},
                        allfun, img=IconPath + 'set_view.png', fanart=FANART)

    # addon.add_directory({'mode': 'help'}, {'title': control.get_lang(32006)},
    #                     [(control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)')],
    #                     img=IconPath + 'github.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'forceupdate'},
                        {'title': '[COLOR gold][B]Version: [COLOR lime]{}[/COLOR][/B]'.format(version)},
                        allfun, img=ICON, fanart=FANART, is_folder=False)

    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def downloads_root():
    movie_downloads = control.setting('movie.download.path')
    tv_downloads = control.setting('tv.download.path')
    cm = [(control.get_lang(32007),
           'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)'),
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


def download(title, img, url):
    from resources.lib.modules import control
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
    headers = quote_plus(json.dumps(headers))

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
            control.infoDialog(control.get_lang(32011), NAME, ICON, 5000)

        else:
            return html
    except BaseException:
        control.infoDialog(control.get_lang(32011), NAME, ICON, 5000)


def search_menu():
    addon.add_directory({'mode': 'search_bb', 'url': 'new'},
                        {'title': control.get_lang(32014)}, img=IconPath + 'search.png', fanart=FANART)
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
        title = '[B]{}[/B]'.format(unquote_plus(search))
        delete_option = True
        addon.add_directory({'mode': 'search_bb', 'url': search},
                            {'title': title},
                            [(control.get_lang(32007),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                             (control.get_lang(32015),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=del_search_item&query=%s)' % search,),
                             (control.get_lang(32008),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                             (control.get_lang(32009),
                              'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                            img=IconPath + 'search.png', fanart=FANART)
        lst += [(search)]
    dbcur.close()

    if delete_option:
        addon.add_directory({'mode': 'del_search_items'},
                            {'title': control.get_lang(32016)},
                            img=IconPath + 'search.png', fanart=FANART, is_folder=False)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


addon.log('Title: {}'.format(title))
addon.log('URL: {}'.format(url))

if mode == 'main' or mode == '' or mode is None:
    MainMenu()
###################DOMAINS########################
elif mode == 'rlsbb':
    from resources.lib.sources import rlsbb
    rlsbb.MainMenu()
elif mode == 'twoddl':
    from resources.lib.sources import twoddl
    twoddl.menu()
elif mode == 'scnsrc':
    from resources.lib.sources import scnsrc
    scnsrc.menu()
elif mode == 'scene':
    from resources.lib.sources import scenerls
    scenerls.menu()
elif mode == 'eztv':
    from resources.lib.sources import eztv
    eztv.eztv_menu()
elif mode == 'ddlvalley':
    from resources.lib.sources import ddlvalley
    ddlvalley.menu()
##################################################
elif mode == 'Categories':
    from resources.lib.sources import rlsbb
    rlsbb.Categories(section)
elif mode == 'GetTitles':
    from resources.lib.sources import rlsbb
    rlsbb.GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetPack':
    from resources.lib.sources import rlsbb
    rlsbb.GetPack(section, url, img, plot)
elif mode == 'GetLinksPack':
    from resources.lib.sources import rlsbb
    rlsbb.GetLinksPack(section, url, img, plot)
elif mode == 'GetLinks':
    from resources.lib.sources import rlsbb
    rlsbb.GetLinks(section, url, img, plot)
elif mode == 'recom':
    from resources.lib.sources import rlsbb
    rlsbb.recommended_movies(url)
elif mode == 'foreign':
    from resources.lib.sources import rlsbb
    rlsbb.foreign_movies(url)

elif mode == 'search_menu':
    search_menu()
elif mode == 'search_bb':
    search.Search_bb(url)
elif mode == 'del_search_items':
    from resources.lib.modules import search
    search.search_clear()
elif mode == 'del_search_item':
    from resources.lib.modules import search
    search.del_search(query)

elif mode == 'PlayVideo':
    tools.PlayVideo(url, title, img, plot)
elif mode == 'settings':
    control.Settings(ADDON.getAddonInfo('id'))
elif mode == 'ResolverSettings':
    import resolveurl
    resolveurl.display_settings()
# elif mode == 'RealDebrid':
#    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)')
elif mode == 'ClearCache':
    cache.delete(control.cacheFile, False)
elif mode == 'forceupdate':
    control.infoDialog(control.get_lang(32021))
    control.execute('UpdateAddonRepos')
elif mode == 'eztv':
    from resources.lib.sources import eztv
    eztv.eztv_menu()
elif mode == 'eztv_latest':
    from resources.lib.sources import eztv
    eztv.eztv_latest(url)
elif mode == 'eztv_calendar':
    from resources.lib.sources import eztv
    eztv_base = control.setting('eztv.domain')
    eztv_base = 'https://%s' % eztv_base.lower()
    url = '{0}/calendar/'.format(eztv_base)
    eztv.eztv_calendar(url)
elif mode == 'eztv_search':
    from resources.lib.sources import eztv
    eztv.eztv_search()
elif mode == 'open_page':
    from resources.lib.sources import eztv
    eztv.open_episode_page(url)
elif mode == 'open_show':
    from resources.lib.sources import eztv
    eztv.open_show(url)
elif mode == 'addView':
    view.addView(content)
elif mode == 'setviews':
    tools.setviews()
elif mode == 'del_views':
    view.view_clear()
elif mode == 'downloadlist':
    downloads_root()
elif mode == 'download':
    download(title, img, url)
elif mode == 'open_news':
    from resources.lib.modules import newsbox
    newsbox.welcome()

############# DDLVALLEY ##############
elif mode == 'movies':
    from resources.lib.sources import ddlvalley
    ddlvalley.movies_menu()
elif mode == 'series':
    from resources.lib.sources import ddlvalley
    ddlvalley.series_menu()
elif mode == 'to_items':
    from resources.lib.sources import ddlvalley
    ddlvalley.to_items(url)
elif mode == 'to_links':
    from resources.lib.sources import ddlvalley
    ddlvalley.to_links(url, img, plot)
elif mode == 'to_etos':
    from resources.lib.sources import ddlvalley
    ddlvalley.etos()
elif mode == 'to_genre':
    from resources.lib.sources import ddlvalley
    ddlvalley.genre(section)

############# SCNSRC ##############
elif mode == 'scn_movies':
    from resources.lib.sources import scnsrc
    scnsrc.movies_menu()
elif mode == 'scn_series':
    from resources.lib.sources import scnsrc
    scnsrc.series_menu()
elif mode == 'scn_items':
    from resources.lib.sources import scnsrc
    scnsrc.to_items(url)
elif mode == 'scn_links':
    from resources.lib.sources import scnsrc
    scnsrc.to_links(url, img, plot)
elif mode == 'scn_genre':
    from resources.lib.sources import scnsrc
    scnsrc.genre(section)

############# TWODDL ##############
elif mode == 'ddl_movies':
    from resources.lib.sources import twoddl
    twoddl.movies_menu()
elif mode == 'ddl_series':
    from resources.lib.sources import twoddl
    twoddl.series_menu()
elif mode == 'ddl_items':
    from resources.lib.sources import twoddl
    twoddl.to_items(url)
elif mode == 'ddl_links':
    from resources.lib.sources import twoddl
    twoddl.to_links(url, img, plot)
elif mode == 'ddl_genre':
    from resources.lib.sources import twoddl
    twoddl.genre(section)

############# SCENERLS ##############
elif mode == 'scene_tvpacks_links':
    from resources.lib.sources import scenerls
    scenerls.to_get_links_pack(url, img, plot, listitem)
elif mode == 'scene_tvpacks':
    from resources.lib.sources import scenerls
    scenerls.to_items(url)
elif mode == 'scene_tvpacks_items':
    from resources.lib.sources import scenerls
    scenerls.to_get_pack(url, img, plot)
elif mode == 'scene_items':
    from resources.lib.sources import scenerls
    scenerls.to_items(url)
elif mode == 'scene_links':
    from resources.lib.sources import scenerls
    scenerls.to_links(url, img, plot)
elif mode == 'search_menu_scene':
    from resources.lib.sources import scenerls
    scenerls.scene_search()