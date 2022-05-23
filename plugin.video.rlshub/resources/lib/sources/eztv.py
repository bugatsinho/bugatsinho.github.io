# -*- coding: utf-8 -*-
import six

import xbmcgui
import xbmcaddon
import xbmc
import re
import sys
from six.moves.urllib.parse import urljoin, parse_qsl, urlparse, unquote_plus, quote_plus, quote, unquote
from resources.lib.modules import client
from resources.lib.modules import control
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

##### Queries ##########
queries = dict(parse_qsl(sys.argv[2][1:]))
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

eztv_base = control.setting('eztv.domain')
eztv_base = 'https://%s' % eztv_base.lower()
headers = {'User-Agent': client.agent(), 'Referer': eztv_base}
allfun = [
    (control.get_lang(32007), 'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
    (control.get_lang(32008), 'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
    (control.get_lang(32009), 'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)
]


def eztv_menu():
    addon.add_directory({'mode': 'eztv_latest'}, {'title': 'Latest Releases'}, allfun,
                        img=ART + 'eztv.png', fanart=FANART)
    addon.add_directory({'mode': 'eztv_calendar', 'url': urljoin(eztv_base, '/calendar')},
                        {'title': 'Calendar'}, allfun, img=ART + 'eztv.png', fanart=FANART)
    addon.add_directory({'mode': 'eztv_search'}, {'title': 'Search'}, allfun,
                        img=ART + 'eztv.png', fanart=FANART)
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500})


def eztv_latest(url):
    html = six.ensure_text(client.request(eztv_base))
    posts = client.parseDOM(html, 'tr', attrs={'class': 'forum_header_border'})
    for post in posts:
        infos = dom.parse_dom(post, 'a')[1]
        title = infos.attrs['title']
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
                            img=ART + 'eztv.png', fanart=FANART)
    except BaseException:
        pass

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def eztv_calendar(url):
    html = six.ensure_text(client.request(url))
    tables = client.parseDOM(html, 'table', attrs={'class': 'forum_header_border'})[1:]
    for table in tables:
        day = client.parseDOM(table, 'td', attrs={'class': 'forum_thread_header'})[0]
        day = '[B][COLORgold]{}[/B][/COLOR]'.format(day.strip().upper())
        addon.add_item({}, {'title': day}, allfun, img=ART + 'eztv.png', fanart=FANART)

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
    html = six.ensure_text(client.request(url))
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
    html = six.ensure_text(client.request(url))
    try:
        poster = client.parseDOM(html, 'td', attrs={'align': 'center'})
        poster = [i for i in poster if 'img src=' in i][0]
        poster = client.parseDOM(poster, 'img', ret='src')[0]
        poster = urljoin(eztv_base, poster) if poster.startswith('/') else poster
    except IndexError:
        poster = ART + 'eztv.png'
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
    url = 'https://eztv.io/search/'
    search_url = 'https://eztv.re/search/{}'
    from resources.lib.modules import user_agents
    headers = {'User-Agent': user_agents.randomagent(),
               'Referer': url}
    keyboard = xbmc.Keyboard()
    keyboard.setHeading(control.get_lang(32002))
    keyboard.doModal()
    if keyboard.isConfirmed():
        _query = keyboard.getText()
        query = six.ensure_text(_query, encoding='utf-8')
        query = quote_plus(query).replace('+', '-')
        # get_link = client.request(url.format(query), output='location')
        search_url = search_url.format(query)
        data = six.ensure_text(client.request(search_url, headers=headers))
        try:
            alts = client.parseDOM(data, 'table', attrs={'class': 'forum_header_border'})[-1]
            alts = client.parseDOM(alts, 'tr', attrs={'name': 'hover'})
            # alts = client.parseDOM(alts, 'td', attrs={'class': 'forum_thread_post'})
            alts = [dom.parse_dom(str(i), 'a', req=['href', 'title'])[1] for i in alts if alts]
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