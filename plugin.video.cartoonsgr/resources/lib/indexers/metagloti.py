# -*- coding: utf-8 -*-

import urllib, xbmcgui, xbmcaddon, xbmcplugin, xbmc, re, sys, os
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import control
from resources.lib.modules import init
from resources.lib.modules import views
from resources.lib.modules import domparser as dom
from resources.lib.modules.control import addDir
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
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

METAGLOTISMENO = 'https://metaglotismeno.online/'

def menu():
    addDir('[B][COLOR yellow]' + Lang(32004).encode('utf-8') + '[/COLOR][/B]', METAGLOTISMENO + 'paidikes-tainies/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32007).encode('utf-8') + '[/COLOR][/B]', '', 32, ART + 'top.png', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32002).encode('utf-8') + '[/COLOR][/B]', METAGLOTISMENO, 35, ICON, FANART, '')
    views.selectView('menu', 'menu-view')


def metaglotismeno(url): #34
    data = client.request(url)
    posts = client.parseDOM(data, 'article', attrs={'class': 'item movies'})
    for post in posts:
        try:
            plot = re.findall('''texto["']>(.+?)</div> <div''', post, re.DOTALL)[0]
        except IndexError:
            plot = 'N/A'
        desc = client.replaceHTMLCodes(plot)
        desc = desc.encode('utf-8')
        try:
            title = client.parseDOM(post, 'h4')[0]
        except BaseException:
            title = client.parseDOM(post, 'img', ret='alt')[0]
        try:
            year = client.parseDOM(data, 'div', {'class': 'metadata'})[0]
            year = client.parseDOM(year, 'span')[0]
            year = '[COLOR lime]({0})[/COLOR]'.format(year)
        except IndexError:
            year = '(N/A)'
        title = clear_Title(title).encode('utf-8', 'ignore')
        title = '[B][COLOR white]%s[/COLOR][/B] %s ' % (title, year)
        link = client.parseDOM(post, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link).encode('utf-8', 'ignore')
        poster = client.parseDOM(post, 'img', ret='src')[0]
        poster = client.replaceHTMLCodes(poster).encode('utf-8', 'ignore')

        addDir(title, link, 33, poster, FANART, desc)
    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'class': 'arrow_pag'})[-1]
        page = np[-2] if np.endswith('/') else re.findall('page/(\d+)/', np)[0]
        title = '[B][COLORgold]>>>' + Lang(32011).encode('utf-8') + ' [COLORwhite]([COLORlime]%s[/COLOR])[/COLOR][/B]' % page
        addDir(title, np.encode('utf-8'), 34, ART + 'next.jpg', FANART, '')
    except BaseException:
        pass
    views.selectView('movies', 'movie-view')

def years():
    r = cache.get(client.request, 120, METAGLOTISMENO)
    r = client.parseDOM(r, 'nav', attrs={'class': 'releases'})[0]
    r = client.parseDOM(r, 'li')
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            year = client.parseDOM(post, 'a')[0].encode('utf-8')
        except BaseException:
            pass

        addDir('[B][COLOR white]%s[/COLOR][/B]' % year, url, 34, ART + 'movies.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def get_links(name, url, iconimage, description):
    # try:
        headers = {'Referer': url}
        data = client.request(url)
        try:
            back = client.parseDOM(data, 'div', {'id': 'dt_galery'})[0]#dt_galery
            back = client.parseDOM(back, 'a', ret='href')[0]
        except IndexError:
            back = FANART
        try:
            frames = client.parseDOM(data, 'div', {'id': 'playeroptions'})[0]
            frames = dom.parse_dom(frames, 'li', attrs={'class': 'dooplay_player_option'},
                               req=['data-post', 'data-nume', 'data-type'])
            for frame in frames:
                post = 'action=doo_player_ajax&post=%s&nume=%s&type=%s' % \
                       (frame.attrs['data-post'], frame.attrs['data-nume'], frame.attrs['data-type'])
                p_link = 'https://metaglotismeno.online/wp-admin/admin-ajax.php'

                flink = client.request(p_link, post=post, headers=headers)
                flink = client.parseDOM(flink, 'iframe', ret='src')[0]

                if '=trailer' in post and 'youtu' in flink:
                    addDir('[B][COLOR white]%s | [B][COLOR lime]Trailer[/COLOR][/B]' % name, flink, 100, iconimage,
                           FANART, '')

                else:
                    host = __top_domain(flink)
                    title = '{0} [B][COLOR white]| {1}[/COLOR][/B]'.format(name, host.capitalize())
                    addDir(title, flink, 100, iconimage, back, str(description))
        except BaseException:
            title = '[B][COLOR white]NO LINKS[/COLOR][/B]'
            addDir(title, '', 'bug', iconimage, back, str(description))
    # except BaseException:
    #     pass
        views.selectView('movies', 'movie-view')


def search(url): #35
    control.busy()
    data = client.request(url)
    posts = client.parseDOM(data, 'div', attrs={'class': 'result-item'})
    for post in posts:
        link = client.parseDOM(post, 'a', ret='href')[0]
        poster = client.parseDOM(post, 'img', ret='src')[0]
        title = client.parseDOM(post, 'img', ret='alt')[0]
        title = clear_Title(title).encode('utf-8')
        try:
            year = client.parseDOM(data, 'span', attrs={'class': 'year'})[0]
            desc = client.parseDOM(data, 'div', attrs={'class': 'contenido'})[0]
            desc = re.sub('<.+?>', '', desc)
            desc = desc.encode('utf-8', 'ignore')
        except BaseException:
            year = 'N/A'
            desc = 'N/A'

        addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(title, year), link, 33, poster, FANART, str(desc))

    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'class': 'arrow_pag'})[-1]
        page = np.split('/')[-1]
        title = '[B][COLORgold]>>>' + Lang(32011).encode('utf-8') + ' [COLORwhite]([COLORlime]%s[/COLOR])[/COLOR][/B]' % page
        addDir(title, np, 34, ART + 'next.jpg', FANART, '')
    except BaseException:
        pass
    control.idle()
    views.selectView('movies', 'movie-view')


def __top_domain(url):
    import urlparse
    elements = urlparse.urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res: domain = res.group(1)
    domain = domain.lower()
    return domain


def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()','').replace("&#038;", "&").replace('&#8211;',':').replace('\n',' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;',"'").replace('&#039;',':').replace('&#;','\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;','"').replace('&#8216;','"').replace('&#160;','')
    txt = txt.replace("&nbsp;", "").replace('&#8220;','"').replace('&#8216;','"').replace('\t',' ')
    return txt