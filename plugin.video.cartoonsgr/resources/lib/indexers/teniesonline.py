# -*- coding: utf-8 -*-

import xbmcgui
import xbmcaddon
import xbmc
import re
import requests
import six
from six.moves.urllib_parse import quote_plus
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import views
from resources.lib.modules import dom_parser as dom
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
Lang        = control.lang
Dialog      = xbmcgui.Dialog()
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

Baseurl = control.setting('tenies.domain') or 'https://tenies-online1.gr/'

def menu():
    addDir('[B][COLOR yellow]' + Lang(32004) + '[/COLOR][/B]', Baseurl + 'genre/kids/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32010) + '[/COLOR][/B]', Baseurl + 'genre/κινούμενα-σχέδια/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR yellow]Family[/COLOR][/B]', Baseurl + 'genre/ikogeniaki/',
           34, ART + 'dub.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32022) + '[/COLOR][/B]', Baseurl + 'genre/christmas/',
           34, ART + 'mas.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32002) + '[/COLOR][/B]', Baseurl, 35, ICON, FANART, '')
    views.selectView('menu', 'menu-view')


def metaglotismeno(url): #34
    #data = client.request(url)
    data = requests.get(url, timeout=10)
    if not data.ok:
        return control.infoDialog('Μη διαθέσιμο αυτή τη στιγμή', NAME, ICON)
    data.encoding = 'utf-8'
    posts = client.parseDOM(data.text, 'div', attrs={'class': 'items normal'})[0]
    posts = client.parseDOM(posts, 'article', attrs={'id': r'post-\d+'})
    for post in posts:
        post = six.ensure_str(post, errors='ignore')
        try:
            plot = client.parseDOM(post, 'div', attrs={'class': 'texto'})[0]
        except IndexError:
            plot = 'N/A'
        desc = client.replaceHTMLCodes(plot)
        #desc = six.ensure_str(desc, errors='ignore')
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
        link = client.replaceHTMLCodes(link)
        poster = client.parseDOM(post, 'img', ret='src')[0]
        poster = client.replaceHTMLCodes(poster)

        addDir(title, link, 33, poster, FANART, desc)
    try:
        np = client.parseDOM(data.text, 'div', attrs={'class': 'resppages'})[0]
        np = dom.parse_dom(np, 'a', req='href')
        np = [i.attrs['href'] for i in np if 'chevron-right' in i.content][0]
        page = re.findall(r'page/(\d+)/', np)[0]
        title = '[B][COLORgold]>>>' + Lang(32011) +\
                ' [COLORwhite]([COLORlime]{}[/COLOR])[/COLOR][/B]'.format(page)
        addDir(title, np, 34, ART + 'next.jpg', FANART, '')
    except BaseException:
        pass
    views.selectView('movies', 'movie-view')


def get_links(name, url, iconimage, description):
    #data = client.request(url)
    data = requests.get(url, timeout=10)
    if not data.ok:
        return control.infoDialog('Μη διαθέσιμο αυτή τη στιγμή', NAME, ICON)
    data = six.ensure_str(data.text, errors='ignore')
    try:
        if 'Τρέιλερ' in data:
            flink = client.parseDOM(data, 'iframe', ret='src', attrs={'class': 'rptss'})[0]
            if 'youtu' in flink:
                addDir('[B][COLOR lime]Trailer[/COLOR][/B]', flink, 100, iconimage, FANART, '')
        else:
            addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')
    except BaseException:
        pass
    try:
        if 'tvshows' not in url:
            frames = client.parseDOM(data, 'tr', {'id': r'link-\d+'})
            frames = [(client.parseDOM(i, 'a', ret='href', attrs={'target': '_blank'})[0],
                       client.parseDOM(i, 'img', ret='src')[0],
                       client.parseDOM(i, 'strong', {'class': 'quality'})[0],
                       client.parseDOM(i, 'td')[-3]) for i in frames if frames]
            for frame, domain, quality, info in frames:
                info = six.ensure_str(info, errors='ignore')
                #xbmc.log('INFO: {}'.format(info))
                host = domain.split('=')[-1]
                if 'tenies' in host:
                    continue
                if 'Μεταγλωτισμένο' in info:
                    info = '[Μετ]'
                elif 'Ελληνικοί' in info:
                    info = '[Υπο]'
                elif 'Χωρίς' in info:
                    info = '[Χωρίς Υπ]'
                else:
                    info = '[N/A]'

                title = '{0} | [COLOR lime]{1}[/COLOR] | [B]{2}[/B] | ({3})'.format(
                    name.split('(')[0].split('/')[0], six.ensure_str(info, errors='ignore'), host.capitalize(), six.ensure_str(quality, errors='ignore')
                )
                addDir(title, frame, 100, iconimage, FANART, str(description))
        else:
            data = client.parseDOM(data, 'table', attrs={'class': 'easySpoilerTable'})
            seasons = [dom.parse_dom(i, 'a', {'target': '_blank'}, req='href') for i in data[:-1] if i]
            episodes = []
            for season in seasons:
                for epi in season:
                    title = clear_Title(epi.content.replace('&#215;', 'x'))
                    frame = epi.attrs['href']
                    episodes.append((title, frame))

            for title, frame in episodes:
                addDir(title, frame, 100, iconimage, FANART, str(description))

    except Exception as e:
        xbmc.log('tenies-online exc: ' + repr(e))
        title = '[B][COLOR white]NO LINKS[/COLOR][/B]'
        addDir(title, '', 'bug', iconimage, FANART, str(description))
    views.selectView('movies', 'movie-view')


def search(url): #35
    control.busy()
    #data = client.request(url)
    data = requests.get(url, timeout=10)
    if not data.ok:
        return control.infoDialog('Μη διαθέσιμο αυτή τη στιγμή', NAME, ICON)
    data.encoding = 'utf-8'
    posts = client.parseDOM(data.text, 'div', attrs={'class': 'result-item'})
    for post in posts:
        link = client.parseDOM(post, 'a', ret='href')[0]
        poster = client.parseDOM(post, 'img', ret='src')[0]
        title = client.parseDOM(post, 'img', ret='alt')[0]
        title = clear_Title(title)
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'year'})[0]
            desc = client.parseDOM(post, 'div', attrs={'class': 'contenido'})[0]
            desc = re.sub('<.+?>', '', desc)
            desc = six.ensure_str(desc, errors='ignore')
        except BaseException:
            year = 'N/A'
            desc = 'N/A'

        addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(title, year), link, 33, poster, FANART, str(desc))

    try:
        np = client.parseDOM(data.text, 'a', ret='href', attrs={'class': 'arrow_pag'})[-1]
        page = np.split('/')[-1]
        title = '[B][COLORgold]>>>' + Lang(32011) + ' [COLORwhite]([COLORlime]%s[/COLOR])[/COLOR][/B]' % page
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
    txt = six.ensure_str(txt, errors='ignore')
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace('Δες το ', '').replace(' online', '')
    txt = txt.replace("&quot;", "\"").replace('()','').replace("&#038;", "&").replace('&#8211;',':').replace('\n',' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;',"'").replace('&#039;',':').replace('&#;','\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;','"').replace('&#8216;','"').replace('&#160;','')
    txt = txt.replace("&nbsp;", "").replace('&#8220;','"').replace('&#8216;','"').replace('\t',' ')
    return txt