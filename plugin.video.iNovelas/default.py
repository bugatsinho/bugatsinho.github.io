# -*- coding: utf-8 -*-
import re, sys, urllib, urlparse
import xbmcaddon, xbmcgui, xbmcplugin, xbmc
from resources.modules import control, client
import resolveurl


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

BASEURL = 'http://mastelenovelashd.com/'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

def Main_menu():
    addDir('[B][COLOR white]Últimos capítulos agregados[/COLOR][/B]', BASEURL, 5, ICON, FANART, '')
    addDir('[B][COLOR white]Telenovelas en Emisión[/COLOR][/B]', BASEURL+'page/telenovelas-en-emision/', 5, ICON, FANART, '')
    addDir('[B][COLOR white]Lista de Telenovelas[/COLOR][/B]', BASEURL, 3, ICON, FANART, '')
    addDir('[B][COLOR white]Navegar por letras[/COLOR][/B]', BASEURL, 9, ICON, FANART, '')
    addDir('[B][COLOR gold]Versión: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def Get_lista(url): #3
    r = client.request(url, headers=headers)
    r = client.parseDOM(r, 'ul', attrs={'id': 'telenovelas'})[0]
    r = client.parseDOM(r, 'li')
    for item in r:
        name = client.parseDOM(item, 'a')[0]
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        url = client.parseDOM(item, 'a', ret='href')[0]
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 8, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def Get_letras(url): #9
    r = client.request(url, headers=headers)
    r = client.parseDOM(r, 'ul', attrs={'id': 'letras'})[0]
    r = client.parseDOM(r, 'li')
    for item in r:
        name = client.parseDOM(item, 'a')[0]
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        url = client.parseDOM(item, 'a', ret='href')[0]
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        addDir('[B][COLOR white]Telenovelas de %s[/COLOR][/B]' % name, url, 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def Get_content(url): #5
    r = client.request(url, headers=headers)
    data = client.parseDOM(r, 'div', attrs={'class': 'imagen'})
    data = zip(client.parseDOM(data, 'a', ret='href'),
               client.parseDOM(data, 'a', ret='title'),
               client.parseDOM(data, 'img', ret='src'))
    for item in data:
        link, name, icon = item[0], item[1], item[2]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')

        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')
        if 'capitulo' in link:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 10, icon, FANART, '')
        else:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 8, icon, FANART, '')
    try:
        np = client.parseDOM(r, 'li')
        np = [i for i in np if 'iguiente' in i][0]
        np = client.parseDOM(np, 'a', ret='href')[0]

        page = re.search('(\d+)', np, re.DOTALL)
        page = '[COLORlime]%s[/COLOR]' % page.groups()[0]

        url = urlparse.urljoin(url, np)
        url = client.replaceHTMLCodes(url)

        addDir('[B][COLORgold]Siguiente(%s)>>>[/COLOR][/B]' % page, url, 5, ICON, FANART, '')
    except: pass
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def Episodes(url): #8
    r = client.request(url, headers=headers)
    data = client.parseDOM(r, 'ul', attrs={'id': 'listado'})[0]
    data = client.parseDOM(data, 'li')
    data = zip(client.parseDOM(data, 'a', ret='href'),
               client.parseDOM(data, 'a'))
    get_icon = client.parseDOM(r, 'img', ret='src', attrs={'class': 'transparent'})[0]

    for item in data[::-1]:
        url, title = client.replaceHTMLCodes(item[0]), client.replaceHTMLCodes(item[1])
        url = url.encode('utf-8')
        title = title.encode('utf-8')

        addDir(title, url, 10, get_icon, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def Get_links(name,url): #10
    OPEN = client.request(url, headers=headers)
    Regex = client.parseDOM(OPEN, 'iframe', ret='src')
    for link in Regex[::-1]:
        if 'verestrenos' in link:
            idp = link.split('mula=')[1]
            post = 'mole=%s' % idp
            link = client.request('http://www.verestrenos.net/rm/ajax.php', post=post)

        vid_id = re.compile('http[s]?://(.+?)\.', re.DOTALL).findall(link)[0]
        if 'sebuscar' in vid_id:
            continue
        vid_id = vid_id.replace('hqq', 'netu.tv')

        addDir('[B][COLOR white]{0} [B]| [COLOR lime]{1}[/COLOR][/B]'.format(name, vid_id), '%s|%s' % (link, url), 100, iconimage, FANART, name)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def resolve(name, url, iconimage, description):
    host = url
    xbmc.log('@#@#HOST:%s' % host, xbmc.LOGNOTICE)
    stream_url = evaluate(host)
    xbmc.log('@#@#STREAM:%s' % stream_url, xbmc.LOGNOTICE)
    name = name.split(' [B]|')[0]
    try:
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={"Title": description})
        liz.setProperty("IsPlayable","true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except:
        control.infoDialog("[COLOR red]Dead Link[/COLOR]!\n[COLOR white]Please Try Another[/COLOR]", NAME, '')


def evaluate(host):
    try:

        if 'openload' in host:
            host, referer = host.split('|')
            from resources.resolvers import openload
            oplink = openload.get_video_openload(host)
            if oplink == '':
                host = resolveurl.resolve(host)
            else:
                host = oplink
            return host

        elif 'gamovideo' in host:
            host, referer = host.split('|')
            r = client.request(host, referer=referer)
            #xbmc.log('@#@GAMO-DATA:%s' % r, xbmc.LOGNOTICE)
            from resources.modules import jsunpack
            source = re.findall('''(eval\(function\(p,a,c,k,e,(?:r|d).+?.split\('\|'\)\)\))''', r, re.DOTALL)[0]
            data = jsunpack.unpack(source)
            #xbmc.log('@#@GAMO-UNPACK:%s' % data, xbmc.LOGNOTICE)
            link = re.findall('''file:['"](http.+?v.mp4)['"]''', data, re.DOTALL)[0]
            #xbmc.log('@#@GAMO-link:%s' % link, xbmc.LOGNOTICE)
            return link.replace('https:', 'http:')

        elif 'hqq' in host or 'waaw' in host:
            #xbmc.log('@#@#-HQQ', xbmc.LOGNOTICE)
            host, referer = host.split('|')
            from resources.resolvers import netutv
            media = netutv.get_video_url(host, referer)
            #xbmc.log('@#@#MEDIA-HQQ:%s' % media, xbmc.LOGNOTICE)
            return media

        elif resolveurl.HostedMediaFile(host):
            host = resolveurl.resolve(host)
            return host

        else:
            return host
    except:
        return host


def addDir(name, url, mode, iconimage, fanart, description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
    liz.setProperty('fanart_image', fanart)
    if mode==100 or mode == 'BUG':
        liz.setProperty("IsPlayable","true")
        liz.addContextMenuItems([('GRecoTM Pair Tool', 'RunAddon(script.grecotm.pair)',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok



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


try   : url=urllib.unquote_plus(params["url"])
except: pass
try   : name=urllib.unquote_plus(params["name"])
except: pass
try   : iconimage=urllib.unquote_plus(params["iconimage"])
except:pass
try   : mode=int(params["mode"])
except: pass
try   : fanart=urllib.unquote_plus(params["fanart"])
except: pass
try   : description=urllib.unquote_plus(params["description"])
except: pass
try   : query=urllib.unquote_plus(params["query"])
except: pass


print str(ADDON_PATH)+': '+str(VERSION)
print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "IconImage: " + str(iconimage)
#########################################################

if   mode == None : Main_menu()
elif mode == 3    : Get_lista(url)
elif mode == 5    : Get_content(url)
elif mode == 8    : Episodes(url)
elif mode == 9    : Get_letras(url)
elif mode == 10   : Get_links(name,url)
elif mode == 100  : resolve(name,url,iconimage,description)
xbmcplugin.endOfDirectory(int(sys.argv[1]))