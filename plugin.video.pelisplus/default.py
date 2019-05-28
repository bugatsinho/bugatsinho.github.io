# -*- coding: utf-8 -*-

import urllib, xbmcgui, xbmcaddon, xbmcplugin, xbmc, re, sys, os
import shutil, urlparse
import resolveurl
import requests

from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import control

reload(sys)
sys.setdefaultencoding('utf8')

BASEURL = 'https://www.pelisplus.to/'

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

def Main_addDir():
    addDir('[B][COLOR yellow]' + Lang(32000).encode('utf-8') + '[/COLOR][/B]', '', 13, ART + 'movies.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32001).encode('utf-8') + '[/COLOR][/B]', '', 14, ART + 'shows.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32002).encode('utf-8') + '[/COLOR][/B]', BASEURL+'documentales/', 5, ART + 'docu.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32003).encode('utf-8') + '[/COLOR][/B]', BASEURL+'kids/', 5, ART + 'kids.jpg', FANART, '')
    addDir('[B][COLOR yellow]' + Lang(32004).encode('utf-8') + '[/COLOR][/B]', '', 15, ART + 'anicon.jpg', ART + 'fanimet.jpg', '')
    addDir('[B][COLOR gold]' + Lang(32020).encode('utf-8') + '[/COLOR][/B]', '', 17, ICON, FANART, '')
    addDir('[B][COLOR gold]' + Lang(32021).encode('utf-8') + '[/COLOR][/B]', '', 9, ICON, FANART, '')
    addDir('[B][COLOR gold]' + Lang(32019).encode('utf-8') + ': [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    setView('movies', 'menu-view')

def Peliculas():#13
    addDir('[B][COLOR orangered]' + Lang(32008).encode('utf-8') + '[/COLOR][/B]', BASEURL + 'peliculas/estrenos', 5, ART + 'ultimas.jpg', FANART,'')
    addDir('[B][COLOR orangered]' + Lang(32010).encode('utf-8') + '[/COLOR][/B]',BASEURL + 'peliculas/populares', 5, ART + 'popular.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32009).encode('utf-8') + '[/COLOR][/B]', BASEURL + 'peliculas/', 5, ART + 'movies.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32006).encode('utf-8') + '[/COLOR][/B]', 'peliculas', 3, ART + 'genre.jpg',FANART,'')
    addDir('[B][COLOR gold]' + Lang(32005).encode('utf-8') + '[/COLOR][/B]', '', 6, ICON, FANART, '')
    setView('movies', 'menu-view')

def Series():#14
    addDir('[B][COLOR orangered]' + Lang(32008).encode('utf-8') + '[/COLOR][/B]',BASEURL + 'series/estrenos/', 5,ART + 'ultimas.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32010).encode('utf-8') + '[/COLOR][/B]',BASEURL + 'series/populares/', 5,ART + 'popular.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(33009).encode('utf-8') + '[/COLOR][/B]', BASEURL + 'series', 5, ART + 'shows.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32006).encode('utf-8') + '[/COLOR][/B]', 'series', 3, ART + 'genre.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32005).encode('utf-8') + '[/COLOR][/B]', '', 6, ICON, FANART, '')
    setView('movies', 'menu-view')

def Get_Genres(url): #3
    r = client.request(BASEURL)
    r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))

    if 'peliculas' in url:
        data = [(i[0], i[1]) for i in r if '/peliculas/generos/' in i[0]]
    else:
        data = [(i[0], i[1]) for i in r if '/series/generos/' in i[0]]

    for post in data:
        try:
            link = urlparse.urljoin(BASEURL, post[0])
            link = client.replaceHTMLCodes(link)
            link = link.encode('utf-8')

            name = post[1]
            name = client.replaceHTMLCodes(name)
            name = clear_Title(name)
            name = name.encode('utf-8')
        except:
            name = ''

        addDir('[B][COLOR yellow]%s[/COLOR][/B]' % name, link, 5, ART + 'genre.jpg', FANART, '')
    setView('movies', 'menu-view')


def Get_Seasons(url, name):#4
    r = client.request(url).decode('latin-1').encode('utf-8')
    episodes = client.parseDOM(r, 'div', attrs={'class': 'tab-content'})[0]
    data = client.parseDOM(r, 'div', attrs={'class': 'VideoPlayer'})[0]
    poster = client.parseDOM(r, 'img', ret='src')[0]
    ss = zip(client.parseDOM(data, 'a', ret='href'),
             client.parseDOM(data, 'a'))
    xbmc.log('@#@SEASONS:%s' % ss, xbmc.LOGNOTICE)
    desc = client.parseDOM(r, 'p', attrs={'class': 'text-dark font-size-13'})[0].encode('latin-1')
    desc = clear_Title(desc)
    for i in ss:
        xbmc.log('@#@FOR-i:%s' % i[1], xbmc.LOGNOTICE)
        season = re.sub('[\n|\t|\r|\s]', '', i[1])
        surl = url + '|' + episodes.encode('utf-8') + '|' + i[0][1:].encode('utf-8') + '|' + str(poster)
        title = '[B][COLOR white]%s [B]| [COLOR lime]%s[/COLOR][/B]' % (name, season)
        addDir(title, surl, 7, poster, FANART, desc)
    setView('movies', 'menu-view')

def Get_epis(url):#7
    base, links, season, poster = url.split('|')
    episodes = client.parseDOM(links, 'div', attrs={'id': season})
    episodes = zip(client.parseDOM(episodes, 'a', ret='href'), client.parseDOM(episodes, 'a'))
    #  #title #url_image #tvSeasonEpisodeNumber
    for i in episodes:
        link = i[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')

        title = i[1]
        title = client.replaceHTMLCodes(title)
        title = title.encode('latin-1')
        title = '[B][COLOR white]%s[/COLOR][/B]' % title

        addDir(title, link, 10, poster, FANART, '')
    setView('movies', 'menu-view')


def Get_random(url):#8
    r = client.request(url)
    r = client.parseDOM(r, 'div', attrs={'id': 'slider1'})[0]
    r = client.parseDOM(r, 'div', attrs={'class': 'item'})
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            icon = client.parseDOM(post, 'img', ret='src')[0]
            name = client.parseDOM(post, 'span', attrs={'class': 'ttps'})[0].encode('utf-8')
            name = re.sub('\d{4}', '', name)
        except:
            name = ''
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'ytps'})[0].encode('utf-8')
        except:
            year = 'N/A'

        name = clear_Title(name)
        if '/ ' in name:
            name = name.split('/ ')
            name = name[1] + ' ([COLORlime]'+year+'[/COLOR])'
        elif '\ ' in name:
            name = name.split('\ ')
            name = name[1] + ' ([COLORlime]'+year+'[/COLOR])'
        else:
            name = name + ' ([COLORlime]' + year + '[/COLOR])'
        if 'tvshows' in url or 'syllogh' in url:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name,url,11,icon,FANART,'')
        else:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name,url,10,icon,FANART,'')
    setView('movies', 'movie-view')

def Get_content(url): #5
    r = client.request(url)
    try:
        data = client.parseDOM(r, 'div', attrs={'class': 'Posters'})[0]
        data = zip(client.parseDOM(data, 'a', ret='href'),
                   client.parseDOM(data, 'img', ret='src'),
                   client.parseDOM(data, 'p'))

        for post in data:
            url, icon, name = post[0], post[1], post[2]

            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            name = clear_Title(name).encode('utf-8')

            if 'kid' in url or 'serie' in url:
                addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 4, icon, FANART,'')
            else:
                addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 10, icon, FANART,'')
    except IndexError:
        addDir('[B][COLOR white]No Hay[/COLOR][/B]', url, 'BUG', ICON, FANART, '')

    try:
        np = client.parseDOM(r, 'a', ret='href', attrs={'rel': 'next'})[0]
        page = np.split('/')[-1]
        page = '[B][COLORlime]' + str(page) + '[B][COLORwhite])[/B][/COLOR]'
        url = client.replaceHTMLCodes(np)
        addDir('[B][COLORgold]>>>' +Lang(32011).encode('utf-8')+ '[/COLOR] [COLORwhite](%s' % page, url, 5, ART + 'next.jpg', FANART, '')
    except: pass
    setView('movies', 'movie-view')


def Get_links(name, url):#10
    r = client.request(url).decode('latin-1').encode('utf-8')
    poster = client.parseDOM(r, 'div', attrs={'class': 'col-sm-3'})[0]
    poster = client.parseDOM(poster, 'img', ret='src')[0]
    links = []
    try:
        frames = zip(client.parseDOM(r, 'a', attrs={'href': '#option\d+'}),
                     re.findall('''video\[\d+\]\s*=\s*['"](.+?)['"]''', r, re.DOTALL))
        links = sorted(frames, key=lambda x: x[0])
    except:
        if len(links) == 0: addDir('[B][COLOR white]No Hay Enlace[/COLOR][/B]', url, 'BUG', poster, FANART, '')

    try:
        desc = client.parseDOM(r, 'div', attrs={'class': 'text-large'})[0].encode('utf-8')
        desc = clear_Title(desc).encode('latin-1')
    except:
        desc = 'N/A'

    try:
        trailer = Trailer(r)
        if trailer:
            addDir('[B][COLORlime]Trailer[/B][/COLOR]', trailer, 100, poster, fanart, str(desc))
    except:
        pass

    for host, link in links:
        link = client.replaceHTMLCodes(link).encode('utf-8')
        link = link.replace(' ', '%20')

        host = clear_Title(host)
        host = host.encode('utf-8')

        title = '[B][COLOR white]%s [B]| [B][COLOR lime]%s[/COLOR][/B]' % (name, host)
        addDir(title, link, 100, poster, fanart, str(desc))
    setView('movies', 'menu-view')



def Trailer(html):
    trailer = client.parseDOM(html, 'iframe', ret='src')
    trailer = [i for i in trailer if 'youtu' in i][0]
    #xbmc.log('@#@tr-links:%s' % trailer, xbmc.LOGNOTICE)
    #.replace('ú', u'\xbf')
    #trailer = urllib.quote(trailer.encode('latin-1'), ':/')
    #xbmc.log('@#@TRAILER:%s' % trailer, xbmc.LOGNOTICE)
    return trailer


def Search_Pelis():#6
    keyb = xbmc.Keyboard('', 'Search')
    keyb.doModal()
    if keyb.isConfirmed():
            search = urllib.quote_plus(keyb.getText())
            url = BASEURL + "search/?s=" + search
            Get_content(url)
    else:
        return

######################
######################
###  ANIMEHD MENU  ###
######################
######################
ANIME = 'https://www.animeshd.tv/'
p_link = 'https://www.animeshd.tv/rest/ajax/animes'


def Anime():#15
    addDir('[B][COLOR orangered]' + Lang(32041).encode('utf-8') + '[/COLOR][/B]', ANIME, 23, ART + 'ulepis.jpg', ART + 'fanimet.jpg','')
    addDir('[B][COLOR orangered]' + Lang(32042).encode('utf-8') + '[/COLOR][/B]', ANIME, 24, ART + 'ulagre.jpg', ART + 'fanimet.jpg', '')
    addDir('[B][COLOR orangered]' + Lang(32010).encode('utf-8') + '[/COLOR][/B]', ANIME, 25,ART + 'apopul.jpg', ART + 'fanimet.jpg', '')
    addDir('[B][COLOR orangered]' + Lang(32006).encode('utf-8') + '[/COLOR][/B]', ANIME, 21,ART + 'anigenre.jpg',ART + 'fanimet.jpg','')
    addDir('[B][COLOR orangered]' + Lang(32040).encode('utf-8') + '[/COLOR][/B]', ANIME, 22,ART + 'anicon.jpg',ART + 'fanimet.jpg','')
    addDir('[B][COLOR orangered]' + Lang(32043).encode('utf-8') + '[/COLOR][/B]', ANIME + 'buscar?t=todo&q=', 26, ART + 'anicon.jpg',ART + 'fanimet.jpg', '')
    addDir('[B][COLOR gold]' + Lang(32005).encode('utf-8') + '[/COLOR][/B]', '', 29, ART + 'anicon.jpg',ART + 'fanimet.jpg','')
    setView('movies', 'menu-view')

def An_Genre(url):#21
    r = client.request(url)
    r = client.parseDOM(r, 'li', attrs={'class': 'dropdown.*?'})[0]
    r = client.parseDOM(r, 'ul', attrs={'class': 'dropdown-menu'})[0]
    r = zip(client.parseDOM(r, 'a', ret='href'),
            client.parseDOM(r, 'a'))

    for item in r:
        url, name = item[0], item[1]
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')

        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')
        if not name: continue

        addDir('[B][COLOR lime]%s[/COLOR][/B]' % name, url, 26, ART + 'genre.jpg', ART + 'fanimet.jpg', '')
    setView('movies', 'menu-view')


def An_idioma(url):#22
    r = client.request(url)
    r = client.parseDOM(r, 'li', attrs={'class':'dropdown.*?'})[1]
    r = client.parseDOM(r, 'ul', attrs={'class': 'dropdown-menu'})[0]
    r = zip(client.parseDOM(r, 'a', ret='href'),
            client.parseDOM(r, 'a'))

    for item in r:
        url, name = item[0], item[1]
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')

        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        addDir('[B][COLOR lime]%s[/COLOR][/B]' % name, url, 26, ART + 'genre.jpg', ART + 'fanimet.jpg', '')
    setView('movies', 'menu-view')


def An_ul_epis(url):#23
    r = client.request(url)
    token = re.findall('''var\s+TOKEN\s*=\s*['"](.+?)['"]''', r, re.DOTALL|re.I)[0]
    post = 'tipo=episodios&_token=%s' % token
    r = client.request(p_link, post=post, referer=ANIME)
    r = client.parseDOM(r, 'div', attrs={'class': 'episodios'})

    for item in r:
        poster = re.findall('url\((.+?)\)', item, re.DOTALL)[0]
        poster = urlparse.urljoin(ANIME, poster)

        link = client.parseDOM(item, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')
        link = '%s|%s' % (link, poster)

        ep = client.parseDOM(item, 'span', attrs={'class': 'Capi'})[0]
        title = client.parseDOM(item, 'h2')[0]
        title = client.replaceHTMLCodes(title)
        title = title.encode('utf-8')
        title = '[B][COLOR white]%s-[COLOR lime]%s[/COLOR][/B]' % (title, str(ep))

        addDir(title, link, 27, poster, ART + 'fanimet.jpg', '')
    setView('movies', 'menu-view')


def An_ul_agre(url):#24
    r = client.request(url)
    token = re.findall('''var\s+TOKEN\s*=\s*['"](.+?)['"]''', r, re.DOTALL | re.I)[0]
    post = 'tipo=estrenos&_token=%s' % token
    r = client.request(p_link, post=post, referer=ANIME)
    r = client.parseDOM(r, 'div', attrs={'class': 'anime'})

    for item in r:
        poster = re.findall('url\((.+?)\)', item, re.DOTALL)[0]
        poster = urlparse.urljoin(ANIME, poster)

        link = client.parseDOM(item, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf=8')

        title = client.parseDOM(item, 'h2')[0]
        title = client.replaceHTMLCodes(title)
        title = title.encode('utf-8')
        title = '[B][COLOR white]%s[/COLOR][/B]' % title

        addDir(title, link, 20, poster, ART + 'fanimet.jpg', '')
    setView('movies', 'menu-view')


def An_popul(url):#25
    r = client.request(url)
    token = re.findall('''var\s+TOKEN\s*=\s*['"](.+?)['"]''', r, re.DOTALL | re.I)[0]
    post = 'tipo=populares&_token=%s' % token
    r = client.request(p_link, post=post, referer=ANIME)
    r = client.parseDOM(r, 'div', attrs={'class': 'anime'})

    for item in r:
        poster = re.findall('url\((.+?)\)', item, re.DOTALL)[0]
        poster = urlparse.urljoin(ANIME, poster)

        link = client.parseDOM(item, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf=8')

        title = client.parseDOM(item, 'h2')[0]
        title = client.replaceHTMLCodes(title)
        title = title.encode('utf-8')
        title = '[B][COLOR white]%s[/COLOR][/B]' % title
        addDir(title, link, 20, poster, ART + 'fanimet.jpg', '')
    setView('movies', 'movie-view')


def An_Todo(url):#26
    #xbmc.log('@#@URL:%s' % url, xbmc.LOGNOTICE)
    r = client.request(url)
    data = client.parseDOM(r, 'div', attrs={'class': 'anime'})

    for item in data:
        poster = re.findall('url\((.+?)\)', item, re.DOTALL)[0]
        poster = urlparse.urljoin(ANIME, poster)

        link = client.parseDOM(item, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf=8')

        title = client.parseDOM(item, 'h2')[0]
        title = client.replaceHTMLCodes(title)
        title = title.encode('utf-8')
        title = '[B][COLOR white]%s[/COLOR][/B]' % title

        addDir(title, link, 20, poster, ART + 'fanimet.jpg', '')
    try:
        np = client.parseDOM(r, 'a', ret='href', attrs={'rel': 'next'})[0]
        page = re.search('page=(\d+)', np, re.DOTALL)
        page = '[B][COLORlime]' + page.groups()[0] + '[B][COLORwhite])[/B][/COLOR]'
        page = '[B][COLORgold]%s>>> [/COLOR] [COLORwhite](%s' % (Lang(32011).encode('utf-8'), page)

        url = urlparse.urljoin(ANIME, np)
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')

        addDir(page, url, 26, ART + 'next.jpg', ART + 'fanimet.jpg', '')
    except:
        pass
    setView('movies', 'movie-view')


def An_Episodios(url):#20
    r = client.request(url)
    poster = client.parseDOM(r, 'div', attrs={'class': 'single'})[0]
    poster = re.findall('url\((.+?)\)', poster, re.DOTALL)[0]
    poster = urlparse.urljoin(ANIME, poster)

    desc = client.parseDOM(r, 'div', attrs={'role':'tabpanel'})[0]
    desc = client.parseDOM(desc, 'p')[0]
    desc = client.replaceHTMLCodes(desc).strip()
    desc = desc.encode('utf-8')

    data = client.parseDOM(r, 'li', attrs={'id':'epi-\d+'})
    data = [(client.parseDOM(i, 'a', ret='href')[0],
             client.parseDOM(i, 'img', ret='title')[0],
             re.findall('img.+?</span>\s*(\w+\s*\w+)', i, re.DOTALL)[0]) for i in data if i]

    for post in data:
        url, lang, name = post[0], post[1], post[2]

        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        url = '%s|%s' % (url, poster)

        name = clear_Title(name).encode('utf-8')
        name = '[B][COLOR white]%s | %s[/COLOR][/B]' % (name.strip(), lang.encode('utf-8'))

        addDir(name, url, 27, poster, ART + 'fanimet.jpg', str(desc))
    setView('movies', 'movie-view')


def An_Ep_links(url):#27
    url, poster = url.split('|')
    r = client.request(url)
    nsepi = client.parseDOM(r, 'div', attrs={'class': 'vistopor text-center'})[0]
    nsepi = zip(client.parseDOM(nsepi, 'a', ret='href'),
            client.parseDOM(nsepi, 'a'))
    try:
        nep = [i[0] for i in nsepi if 'nterior' in i[1]][0]
        nepid = re.findall('\/(\d+)$', nep)[0]
        nepid = '[B][COLORwhite]Capitulo [COLORyellow](%s)[/B][/COLOR]' % nepid
        nep = '%s|%s' % (nep, poster)
    except:
        nep = '0'
    try:
        sep = [i[0] for i in nsepi if 'iguiente' in i[1]][0]
        sepid = re.findall('\/(\d+)$', sep)[0]
        sepid = '[B][COLORwhite]Capitulo [COLORlime](%s)[/B][/COLOR]' % sepid
        sep = '%s|%s' % (sep, poster)
    except:
        sep = '0'

    links = client.parseDOM(r, 'select')[-1]
    links = zip(client.parseDOM(links, 'option', ret='value'),
                client.parseDOM(links, 'option'))

    for item in links:
        link, host = item[0], item[1]

        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')

        host = client.replaceHTMLCodes(host).split('>')[-1]
        host = host.encode('utf-8').replace("'", "")
        host = '[B][COLORlime]%s[/B][/COLOR]' % host

        addDir(host, link, 100, poster, ART + 'fanimet.jpg', '')

    if not sep == '0': addDir(sepid, sep, 27, poster, ART + 'fanimet.jpg', '')
    if not nep == '0': addDir(nepid, nep, 27, poster, ART + 'fanimet.jpg', '')
    setView('movies', 'menu-view')

def Search_Anime():  # 29
    keyb = xbmc.Keyboard('', 'Search')
    keyb.doModal()
    if (keyb.isConfirmed()):
        search = urllib.quote_plus(keyb.getText())

        url = ANIME + "buscar?t=todo&q=" + search
        An_Todo(url)
    else:
        return


######################
######################
###   TOOLS MENU   ###
######################
######################
def find_single_match(data,patron,index=0):
    try:
        matches = re.findall( patron , data , flags=re.DOTALL )
        return matches[index]
    except:
        return ""

def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()','').replace("&#038;", "&").replace('&#8211;',':').replace('\n',' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;',"'").replace('&#039;',':').replace('&#;','\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;','"').replace('&#8216;','"').replace('&amp;#038;','&').replace('&#160;','')
    txt = txt.replace("&nbsp;", "").replace('&#8220;','"').replace('&#8216;','"').replace('\t',' ')
    return txt


def addDir(name, url, mode, iconimage, fanart, description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode('utf-8'))+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description.encode('utf-8'))
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
    liz.setProperty('fanart_image', fanart)
    if mode==100:
        liz.setProperty("IsPlayable", "true")
        liz.addContextMenuItems([('GRecoTM Pair Tool', 'RunAddon(script.grecotm.pair)',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    elif mode == 9 or mode == 17 or mode == 'BUG':
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok


def resolve(name, url, iconimage, description):
    stream_url = evaluate(url)
    name = name.split(' [B]|')[0]
    if stream_url is None:
        control.infoDialog('Prueba otro enlace', NAME, ICON, 4000)
    elif '.mpd|' in stream_url:
        stream_url, headers = stream_url.split('|')
        listitem = xbmcgui.ListItem(path=stream_url)
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        listitem.setMimeType('application/dash+xml')
        listitem.setProperty('inputstream.adaptive.stream_headers', headers)
        listitem.setContentLookup(False)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
    else:
        try:
            liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
            liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description })
            liz.setProperty("IsPlayable", "true")
            liz.setPath(str(stream_url))
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
        except:
            control.infoDialog('Prueba otro enlace', NAME, ICON, 4000)


def evaluate(host):
    try:
        #xbmc.log('@#@HOST:%s' % host, xbmc.LOGNOTICE)
        if 'animeshd' in host:
            host = client.request(host, output='geturl')

        elif 'server.pelisplus' in host:
            host = client.request(host)
            host = client.parseDOM(host, 'iframe', ret='src')[0]

        else:
            host = host
        #xbmc.log('@#@HOST-FINAL:%s' % host, xbmc.LOGNOTICE)
        if 'openload' in host:
            try:
                from resources.lib.modules import openload
                oplink = openload.get_video_openload(host)
                host = resolveurl.resolve(oplink) if oplink == '' else oplink
            except BaseException:
                host = resolveurl.resolve(host)
            return host

        elif 'animehdpro' in host:
            data = client.request(host)
            host = re.compile('''file['"]:['"]([^'"]+)''', re.DOTALL).findall(data)[0]
            host = requests.get(host).headers['location']
            #xbmc.log('@#@ANIMEHDPRO:%s' % host, xbmc.LOGNOTICE)
            return host + '|User-Agent=%s' % urllib.quote(client.agent())

        elif 'tiwi' in host:
            from resources.lib.modules import jsunpack
            data = client.request(host)
            if jsunpack.detect(data):
                data = jsunpack.unpack(data)
                link = re.compile('''\{file:['"]([^'"]+)''', re.DOTALL).findall(data)[0]
                #xbmc.log('@#@HDPRO:%s' % link, xbmc.LOGNOTICE)
            else:
                #link = re.compile('''video\/mp4.+?src:['"](.+?)['"]''', re.DOTALL).findall(data)[0]
                link = re.compile('''dash\+xml.+?src:['"](.+?)['"]''', re.DOTALL).findall(data)[0]
                #xbmc.log('@#@HDPRO:%s' % link, xbmc.LOGNOTICE)
            return link + '|User-Agent=%s&Referer=%s' % (urllib.quote(client.agent()), host)

        elif 'pelishd.tv' in host:
            res_quality = []
            stream_url = []
            from resources.lib.modules import unjuice
            import json
            data = client.request(host)
            if unjuice.test(data):
                juice = unjuice.run(data)
                links = json.loads(re.findall('sources:(\[.+?\])', juice)[0])
                for stream in links:
                    url = stream['file']
                    qual = '[COLORlime][B]%s Calidad[/B][/COLOR]' % stream['label']
                    res_quality.append(qual)
                    stream_url.append(url)
                if len(res_quality) > 1:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select('[COLORgold][B]Ver en[/B][/COLOR]', res_quality)
                    if ret == -1:
                        return
                    elif ret > -1:
                        host = stream_url[ret]
                        #xbmc.log('@#@HDPRO:%s' % host, xbmc.LOGNOTICE)
                        return host + '|User-Agent=%s' % urllib.quote(client.agent())
                    else:
                        return
                else:
                    host = stream_url[0]
                    return host + '|User-Agent=%s' % urllib.quote(client.agent())

        elif 'www.pelisplus.net' in host:
            res_quality = []
            stream_url = []

            headers = {'User-Agent': client.agent(),
                       'Referer': host}
            cj = requests.get(host, headers=headers).cookies
            cj = '__cfduid=%s' % str(cj['__cfduid'])
            vid_id = host.split('/')[-1]
            headers['Cookie'] = cj
            data = requests.post('https://www.pelisplus.net/api/source/%s' % vid_id, headers=headers).json()
            streams = data['data']
            for stream in streams:
                url = stream['file']
                url = 'https://www.pelisplus.net' + url if url.startswith('/') else url
                qual = '[COLORlime][B]%s Calidad[/B][/COLOR]' % stream['label']
                res_quality.append(qual)
                stream_url.append(url)
            if len(res_quality) > 1:
                dialog = xbmcgui.Dialog()
                ret = dialog.select('[COLORgold][B]Ver en[/B][/COLOR]', res_quality)
                if ret == -1:
                    return
                elif ret > -1:
                    host = stream_url[ret]
                    #xbmc.log('@#@HDPRO:%s' % host, xbmc.LOGNOTICE)
                    return host + '|User-Agent=%s' % urllib.quote(client.agent())
                else:
                    return

            else:
                host = stream_url[0]
                return host + '|User-Agent=%s' % urllib.quote(client.agent())

        else:
            host = resolveurl.resolve(host)
            return host
    except:
        return host


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
    return param

params=get_params()
url=BASEURL
name=NAME
iconimage=ICON
mode=None
fanart=FANART
description=DESCRIPTION
query=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass

def setView(content, viewType):
    ''' Why recode whats allready written and works well,
    Thanks go to Eldrado for it '''
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if control.setting('auto-view') == 'true':

        print control.setting(viewType)
        if control.setting(viewType) == 'Info':
            VT = '504'
        elif control.setting(viewType) == 'Info2':
            VT = '503'
        elif control.setting(viewType) == 'Info3':
            VT = '515'
        elif control.setting(viewType) == 'Fanart':
            VT = '508'
        elif control.setting(viewType) == 'Poster Wrap':
            VT = '501'
        elif control.setting(viewType) == 'Big List':
            VT = '51'
        elif control.setting(viewType) == 'Low List':
            VT = '724'
        elif control.setting(viewType) == 'List':
            VT = '50'
        elif control.setting(viewType) == 'Default Menu View':
            VT = control.setting('default-view1')
        elif control.setting(viewType) == 'Default TV Shows View':
            VT = control.setting('default-view2')
        elif control.setting(viewType) == 'Default Episodes View':
            VT = control.setting('default-view3')
        elif control.setting(viewType) == 'Default Movies View':
            VT = control.setting('default-view4')
        elif control.setting(viewType) == 'Default Docs View':
            VT = control.setting('default-view5')
        elif control.setting(viewType) == 'Default Cartoons View':
            VT = control.setting('default-view6')
        elif control.setting(viewType) == 'Default Anime View':
            VT = control.setting('default-view7')

        print viewType
        print VT

        xbmc.executebuiltin("Container.SetViewMode(%s)" % (int(VT)))


def check_source():
    REPO_PATH = xbmc.translatePath('special://home/addons/repository.bugatsinho')
    if not os.path.exists(REPO_PATH):
        shutil.rmtree(ADDON_PATH, ignore_errors=True)
        Dialog.ok(ADDON_PATH, Lang(32013))

def Open_settings():
    control.openSettings(None, ID)

def cache_clear():
    cache.clear(withyes=False)


print str(ADDON_PATH)+': '+str(VERSION)
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "IconImage: "+str(iconimage)


#########################################################

if mode == None: Main_addDir()
elif mode == 3 : Get_Genres(url)
elif mode == 4 : Get_Seasons(url, name)
elif mode == 5 : Get_content(url)
elif mode == 6 : Search_Pelis()
elif mode == 7 : Get_epis(url)
elif mode == 8 : Get_random(url)
elif mode == 9 : cache_clear()
elif mode == 10 : Get_links(name, url)
#elif mode == 11 :
elif mode == 13 : Peliculas()
elif mode == 14 : Series()

########ANIMEHD MODE########
elif mode == 15 : Anime()
elif mode == 20 : An_Episodios(url)
elif mode == 21 : An_Genre(url)
elif mode == 22 : An_idioma(url)
elif mode == 23 : An_ul_epis(url)
elif mode == 24 : An_ul_agre(url)
elif mode == 25 : An_popul(url)
elif mode == 26 : An_Todo(url)
elif mode == 27 : An_Ep_links(url)
elif mode == 29 : Search_Anime()
############################
elif mode == 17 : Open_settings()
elif mode == 100 : resolve(name,url,iconimage,description)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
