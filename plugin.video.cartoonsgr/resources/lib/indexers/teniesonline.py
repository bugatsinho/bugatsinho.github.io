# -*- coding: utf-8 -*-

import xbmcgui
import xbmcaddon
import re
from resources.lib.modules import client
from resources.lib.modules import control
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

Baseurl = 'https://tenies-online.gr/'

def menu():
    addDir('[B][COLOR yellow]' + Lang(32004).encode('utf-8') + '[/COLOR][/B]', Baseurl + 'genre/kids/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32010).encode('utf-8') + '[/COLOR][/B]', Baseurl + 'genre/κινούμενα-σχέδια/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32022).encode('utf-8') + '[/COLOR][/B]', Baseurl + 'genre/christmas/',
           34, ART + 'mas.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32002).encode('utf-8') + '[/COLOR][/B]', Baseurl, 35, ICON, FANART, '')
    views.selectView('menu', 'menu-view')


def metaglotismeno(url): #34
    data = client.request(url)
    posts = client.parseDOM(data, 'article', attrs={'class': 'item movies'})
    for post in posts:
        try:
            plot = client.parseDOM(post, 'div', attrs={'class': 'texto'})[0]
        except IndexError:
            plot = 'N/A'
        desc = client.replaceHTMLCodes(plot)
        desc = desc.encode('utf-8')
        try:
            title = client.parseDOM(post, 'h3')[0]
        except BaseException:
            title = client.parseDOM(post, 'img', ret='alt')[0]
        # try:
        #     year = client.parseDOM(data, 'div', {'class': 'metadata'})[0]
        #     year = client.parseDOM(year, 'span')[0]
        #     year = '[COLOR lime]({0})[/COLOR]'.format(year)
        # except IndexError:
        #     year = '(N/A)'
        title = clear_Title(title)
        title = '[B][COLOR white]{}[/COLOR][/B]'.format(title)
        link = client.parseDOM(post, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link).encode('utf-8', 'ignore')
        poster = client.parseDOM(post, 'img', ret='src')[0]
        poster = client.replaceHTMLCodes(poster).encode('utf-8', 'ignore')

        addDir(title, link, 33, poster, FANART, desc)
    try:
        np = client.parseDOM(data, 'div', attrs={'class': 'resppages'})[0]
        np = dom.parse_dom(np, 'a', req='href')
        np = [i.attrs['href'] for i in np if 'icon-chevron-right' in i.content][0]
        page = re.findall(r'page/(\d+)/', np)[0]
        title = '[B][COLORgold]>>>' + Lang(32011).encode('utf-8') +\
                ' [COLORwhite]([COLORlime]{}[/COLOR])[/COLOR][/B]'.format(page)
        addDir(title, np.encode('utf-8'), 34, ART + 'next.jpg', FANART, '')
    except BaseException:
        pass
    views.selectView('movies', 'movie-view')


def get_links(name, url, iconimage, description):
    data = client.request(url)
    if 'Τρέιλερ' in data:
        flink = client.parseDOM(data, 'iframe', ret='src', attrs={'class': 'rptss'})[0]
        if 'youtu' in flink:
            addDir('[B][COLOR lime]Trailer[/COLOR][/B]', flink, 100, iconimage, FANART, '')
    else:
        addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')
    try:
        frames = client.parseDOM(data, 'tr', {'id': r'link-\d+'})
        frames = [(client.parseDOM(i, 'a', ret='href')[0],
                   client.parseDOM(i, 'img', ret='src')[0],
                   client.parseDOM(i, 'strong', {'class': 'quality'})[0],
                   client.parseDOM(i, 'td')[-3]) for i in frames if frames]
        for frame, domain, quality, info in frames:
            host = domain.split('=')[-1].encode('utf-8')
            if 'Μεταγλωτισμένο' in info.encode('utf-8', 'ignore'):
                info = '[Μετ]'
            elif 'Ελληνικοί' in info.encode('utf-8', 'ignore'):
                info = '[Υπο]'
            elif 'Χωρίς' in info.encode('utf-8', 'ignore'):
                info = '[Χωρίς Υπ]'
            else:
                info = '[N/A]'
            title = '[COLOR lime]{}[B][COLOR white]{}-({})[/B][/COLOR]'.format(info, host.capitalize(), quality.encode('utf-8'))
            addDir(title, frame, 100, iconimage, FANART, str(description))
    except BaseException:
        title = '[B][COLOR white]NO LINKS[/COLOR][/B]'
        addDir(title, '', 'bug', iconimage, FANART, str(description))
    views.selectView('movies', 'movie-view')


def search(url): #35
    control.busy()
    data = client.request(url)
    posts = client.parseDOM(data, 'div', attrs={'class': 'result-item'})
    for post in posts:
        link = client.parseDOM(post, 'a', ret='href')[0]
        poster = client.parseDOM(post, 'img', ret='src')[0]
        title = client.parseDOM(post, 'img', ret='alt')[0]
        title = clear_Title(title)
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
    regex = r"(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res: domain = res.group(1)
    domain = domain.lower()
    return domain


def clear_Title(txt):
    txt = txt.encode('utf-8', 'ignore')
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace(' online ελληνικοί υπότιτλοι', '')
    txt = txt.replace("&quot;", "\"").replace('()','').replace("&#038;", "&").replace('&#8211;',':').replace('\n',' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;',"'").replace('&#039;',':').replace('&#;','\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;','"').replace('&#8216;','"').replace('&#160;','')
    txt = txt.replace("&nbsp;", "").replace('&#8220;','"').replace('&#8216;','"').replace('\t',' ')
    return txt