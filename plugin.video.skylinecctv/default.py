# -*- coding: utf-8 -*-
import re
import sys
import urllib
from kodi_six import xbmcaddon, xbmcgui, xbmcplugin, xbmc
from resources.modules import control, client


ADDON = xbmcaddon.Addon()
ADDON_DATA = ADDON.getAddonInfo('profile')
ADDON_PATH = ADDON.getAddonInfo('path')
DESCRIPTION = ADDON.getAddonInfo('description')
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
ID = ADDON.getAddonInfo('id')
NAME = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
Lang = ADDON.getLocalizedString
Dialog = xbmcgui.Dialog()
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://www.skylinewebcams.com/{0}/webcam.html'
base_url = 'https://www.skylinewebcams.com'
new_url = 'https://www.skylinewebcams.com/skyline/morewebcams.php?w=new&l={0}&b=5'

headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

reload(sys)
sys.setdefaultencoding("utf-8")

def get_lang():
    lang = ADDON.getSetting('lang').encode('utf-8')
    lang_dict = {'English': 'en',
                 'Greek': 'el',
                 'Español': 'es',
                 'Français': 'fr',
                 'Deutsch': 'de',
                 'Italiano': 'it',
                 'Polish': 'pl',
                 'Hrvatski': 'hr',
                 'Slovenski': 'sl'}

    return lang_dict[lang]


web_lang = get_lang()


def Main_menu():
    addDir('[B][COLOR white]Top Live Cams[/COLOR][/B]',
           'https://www.skylinewebcams.com/{0}/top-live-cams.html'.format(web_lang), 5, ICON, FANART, '')
    addDir('[B][COLOR white]New Live Cams[/COLOR][/B]', new_url.format(web_lang), 6, ICON, FANART, '')
    addDir('[B][COLOR white]Live Cams by Country[/COLOR][/B]', BASEURL.format(web_lang), 4, ICON, FANART, '')
    addDir('[B][COLOR white]Random Live Cam[/COLOR][/B]', BASEURL.format(web_lang), 3, ICON, FANART, '')
    addDir('[B][COLOR white]Greek Live Cams[/COLOR][/B]', BASEURL.format(web_lang), 8, ICON, FANART, '')
    addDir('[B][COLOR cyan]Settings[/COLOR][/B]', '', 7, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')



def get_greek_cams():
    link = 'http://www.livecameras.gr/'
    headers = {"User-Agent": client.agent()}
    r = client.request(link, headers=headers)
    r = r.encode('utf-8')
    cams = client.parseDOM(r, 'div', attrs={'class': 'fp-playlist'})[0]
    cams = zip(client.parseDOM(cams, 'a', ret='href'),
               client.parseDOM(cams, 'a', ret='data-title'),
               client.parseDOM(cams, 'img', ret='src'))
    for stream, name, poster in cams:
        name = re.sub('".+?false', '', name)
        name = client.replaceHTMLCodes(name).encode('utf-8')
        stream = 'http:' + stream if stream.startswith('//') else stream
        stream += '|Referer={}'.format(link)
        poster = link + poster if poster.startswith('/') else poster
        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, stream, 100, poster, '', 'name')


def get_the_random(url): #3
    r = client.request(url, headers=headers)
    frames = zip(client.parseDOM(r, 'a', ret='href'),
                 client.parseDOM(r, 'a'))
    frame = [i[0] for i in frames if 'random cam' in i[1].lower()][0]
    frame = base_url + frame if frame.startswith('/') else frame
    # xbmc.log('FRAME:%s' % frame)
    info = client.request(frame, headers=headers)
    head = client.parseDOM(info, 'title')[0].encode('utf-8')
    # title = client.parseDOM(info, 'meta', ret='content', attrs={'name': 'description'})[0].encode('utf-8')
    # name = '{0} - {1}'.format(head, title)
    # xbmc.log('NAME:%s' % head)
    poster = client.parseDOM(info, 'meta', ret='content', attrs={'property': 'og:image'})[0]
    # xbmc.log('INFO:%s' % info)
    link = re.findall(r'''\,url:['"](.+?)['"]\}''', info, re.DOTALL)[0]
    addDir('[B][COLOR white]%s[/COLOR][/B]' % head, link, 100, poster, '', 'Random Live Cam')


def get_country(url): #4
    r = client.request(url, headers=headers)
    r = client.parseDOM(r, 'li', attrs={'class': 'dropdown'})[0]
    r = zip(client.parseDOM(r, 'a', attrs={'class': 'menu-item'}),
            client.parseDOM(r, 'a', attrs={'class': 'menu-item'}, ret='href'))
    for name, link in r:
        name = re.sub('<.+?>', '', name).replace('&nbsp;', ' ')
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')
        link = base_url + link if link.startswith('/') else link
        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_new(url):
    r = client.request(url, headers=headers)
    r = client.parseDOM(r, 'div', attrs={'class': 'row'})[0]
    r = zip(client.parseDOM(r, 'a', ret='href'),
            client.parseDOM(r, 'img', ret='src'),
            client.parseDOM(r, 'img', ret='alt'))
    for link, poster, name in r:
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')
        link = 'https:' + link if link.startswith('//') else link

        poster = client.replaceHTMLCodes(poster)
        poster = 'https:' + poster if poster.startswith('//') else poster
        poster = poster.encode('utf-8')

        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 100, poster, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_content(url): #5 <div id="content"><div class="container">
    r = client.request(url, headers=headers)
    # data = client.parseDOM(r, 'div', attrs={'class': 'container'})[0]
    # xbmc.log('DATAAAA: %s' % data)
    data = client.parseDOM(r, 'div', attrs={'class': 'col-sm-6 col-md-4 webcam'})
    data = [i for i in data if not 'adsbygoogle' in i]
    for item in data:
        link = client.parseDOM(item, 'a', ret='href')[0]
        if link == '#':
            continue
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')

        name = client.parseDOM(item, 'span', attrs={'class': 'title'})[0]
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        desc = client.parseDOM(item, 'span', attrs={'class': 'description'})[0]
        desc = clear_Title(desc)
        desc = desc.decode('ascii', errors='ignore')

        poster = client.parseDOM(item, 'img', ret='data-original')[0]
        poster = client.replaceHTMLCodes(poster)
        poster = 'https:' + poster if poster.startswith('//') else poster
        poster = poster.encode('utf-8')

        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 100, poster, '', desc)

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('\t', ' ').replace('\n', ' ')
    return txt


def Open_settings():
    control.openSettings()


def resolve(name, url, iconimage, description):
    xbmc.log('URLLLL: {}'.format(url))
    if 'm3u8' in url:
        link = url
        link += '|User-Agent={}&Referer={}'.format(urllib.quote_plus(client.agent()),
                                                   urllib.quote_plus(headers['Referer']))
        liz = xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
    else:
        import requests
        url = base_url + url if url.startswith('/') else url
        # xbmc.log('URLLLL2: {}'.format(url))
        cj = client.request(base_url, headers=headers, output='cookie')
        # xbmc.log('COOKIES: {}'.format(str(cj)))
        headers['Cookie'] = cj
        info = requests.get(url, headers=headers).text
        # xbmc.log('INFOOOO: {}'.format(info))
        head = client.parseDOM(info, 'title')[0].encode('utf-8')
        # title = client.parseDOM(info, 'meta', ret='content', attrs={'name': 'description'})[0].encode('utf-8')
        # name = '{0} - {1}'.format(head, title)
        poster = client.parseDOM(info, 'meta', ret='content', attrs={'property': 'og:image'})[0]
        link = re.findall(r'''\,url:['"](.+?)['"]\}''', info, re.DOTALL)[0]
        link += '|User-Agent={}&Referer={}'.format(urllib.quote_plus(client.agent()), urllib.quote_plus(url))
        liz = xbmcgui.ListItem(head, iconImage=ICON, thumbnailImage=poster)

    try:
        liz.setInfo(type="Video", infoLabels={"Title": description})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(link))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except:
        control.infoDialog("[COLOR red]Dead Link[/COLOR]!\n[COLOR white]Please Try Another[/COLOR]", NAME, '')


def addDir(name, url, mode, iconimage, fanart, description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setProperty('fanart_image', fanart)
    if mode == 100 or mode == 'BUG' or mode == 7:
        liz.setProperty("IsPlayable", "true")
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    elif mode == 7:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    else:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
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

if mode is None:
    Main_menu()
elif mode == 3:
    get_the_random(url)
elif mode == 4:
    get_country(url)
elif mode == 5:
    get_content(url)
elif mode == 6:
    get_new(url)
elif mode == 7:
    Open_settings()
elif mode == 8:
    get_greek_cams()
elif mode == 100:
    resolve(name, url, iconimage, description)
xbmcplugin.endOfDirectory(int(sys.argv[1]))

