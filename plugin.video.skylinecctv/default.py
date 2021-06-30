# -*- coding: utf-8 -*-
import re
import sys
import six
from kodi_six import xbmcaddon, xbmcgui, xbmcplugin, xbmc
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip
from resources.modules import control, client, dom_parser as dom

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
new_url = 'https://www.skylinewebcams.com/{0}/new-livecams.html'

headers = {'User-Agent': 'iPad',
           'Referer': BASEURL}


# reload(sys)
# sys.setdefaultencoding("utf-8")

def get_lang():
    lang = ADDON.getSetting('lang').encode('utf-8') if six.PY2 else ADDON.getSetting('lang')
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
    addDir('[B][COLOR white]New Live Cams[/COLOR][/B]', new_url.format(web_lang), 5, ICON, FANART, '')
    addDir('[B][COLOR white]Live Cams by Country[/COLOR][/B]', BASEURL.format(web_lang), 4, ICON, FANART, '')
    addDir('[B][COLOR white]Live Cams by Category[/COLOR][/B]', BASEURL.format(web_lang), 9, ICON, FANART, '')
    addDir('[B][COLOR white]Random Live Cam[/COLOR][/B]', base_url, 3, ICON, FANART, '')
    addDir('[B][COLOR white]Greek Live Cams[/COLOR][/B]', BASEURL.format(web_lang), 8, ICON, FANART, '')
    addDir('[B][COLOR cyan]Settings[/COLOR][/B]', '', 7, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_cat_cams():
    try:
        html = six.ensure_str(client.request(base_url, referer=BASEURL))
        data = client.parseDOM(html, 'li', attrs={'class': 'dropdown mega-dropdown'})[0]
        cats = client.parseDOM(data, 'div', attrs={'class': 'container-fluid'})[0]
        cats = dom.parse_dom(cats, 'a', req='href')
        for cat in cats:
            name = client.parseDOM(cat.content, 'p', attrs={'class': 'tcam'})[0]
            if six.PY2:
                name = name.encode('utf-8')
            name = '[B][COLOR white]{}[/COLOR][/B]'.format(name)
            icon = client.parseDOM(cat.content, 'img', ret='data-src')[0]
            icon = 'https:{}'.format(icon) if icon.startswith('//') else icon
            icon = icon + '|Referer={}'.format(base_url)
            url = cat.attrs['href'][3:]
            url = '{2}/{0}/{1}'.format(web_lang, url, base_url)
            addDir(name, url, 5, icon, FANART, '')
    except BaseException:
        pass
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    # addDir('[B][COLOR white]Beaches[/COLOR][/B]',
    #        'https://www.skylinewebcams.com/{0}/live-cams-category/beach-cams.html'.format(web_lang), 5, ICON, FANART, '')
    # addDir('[B][COLOR white]CITY Views[/COLOR][/B]',
    #        'https://www.skylinewebcams.com/{0}/live-cams-category/city-cams.html'.format(web_lang), 5, ICON, FANART, '')
    # addDir('[B][COLOR white]Landscapes[/COLOR][/B]',
    #        'https://www.skylinewebcams.com/{0}/live-cams-category/nature-mountain-cams.html'.format(web_lang), 5, ICON,
    #        FANART, '')
    # addDir('[B][COLOR white]Landscapes[/COLOR][/B]',
    #        'https://www.skylinewebcams.com/{0}/live-cams-category/nature-mountain-cams.html'.format(web_lang), 5, ICON, FANART, '')


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
        name = re.sub(r'".+?false', '', name)
        name = client.replaceHTMLCodes(name).encode('utf-8')
        stream = 'http:' + stream if stream.startswith('//') else stream
        stream += '|Referer={}'.format(link)
        poster = link + poster if poster.startswith('/') else poster
        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, stream, 100, poster, '', 'name')


def get_the_random(url):  # 3
    r = six.ensure_str(client.request(url, headers=headers))
    frame = client.parseDOM(r, 'div', attrs={'class': 'row home'})[0]
    head = client.parseDOM(frame, 'h1')[0]
    head = clear_Title(head)
    frame = client.parseDOM(frame, 'a', ret='href')[0]
    frame = base_url + frame if frame.startswith('/') else frame
    # xbmc.log('FRAME:%s' % frame)
    if six.PY2:
        head = head.encode('utf-8')
    addDir('[B][COLOR white]%s[/COLOR][/B]' % head, frame, 100, ICON, '', 'Random Live Cam')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_country(url):  # 4
    r = six.ensure_str(client.request(url, headers=headers))
    r = client.parseDOM(r, 'div', attrs={'class': 'dropdown mega-dropdown live'})[0]
    r = zip(client.parseDOM(r, 'a'),
            client.parseDOM(r, 'a', ret='href'))
    for name, link in r:
        name = re.sub('<.+?>', '', name).replace('&nbsp;', ' ')
        name = client.replaceHTMLCodes(name)
        name = '[B][COLOR white]{}[/COLOR][/B]'.format(name)
        link = client.replaceHTMLCodes(link)
        if six.PY2:
            name = name.encode('utf-8')
            link = link.encode('utf-8')
        link = base_url + link if link.startswith('/') else link
        addDir(name, link, 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_new(url):
    r = client.request(url, headers=headers)
    r = client.parseDOM(r, 'div', attrs={'class': 'row'})[0]
    r = zip(client.parseDOM(r, 'a', ret='href'),
            client.parseDOM(r, 'img', ret='src'),
            client.parseDOM(r, 'img', ret='alt'))
    for link, poster, name in r:
        name = client.replaceHTMLCodes(name)

        link = client.replaceHTMLCodes(link)
        link = 'https:' + link if link.startswith('//') else link

        poster = client.replaceHTMLCodes(poster)
        poster = 'https:' + poster if poster.startswith('//') else poster
        if six.PY2:
            poster = poster.encode('utf-8')
            name = name.encode('utf-8')
            link = link.encode('utf-8')

        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 100, poster, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_content(url):  # 5 <div id="content"><div class="container">
    r = six.ensure_str(client.request(url, headers=headers))
    data = client.parseDOM(r, 'div', attrs={'class': 'container'})[0]
    data = dom.parse_dom(data, 'a', req='href')
    data = [i for i in data if 'subt' in i.content]
    # xbmc.log('DATA22: {}'.format(str(data)))
    for item in data:
        link = item.attrs['href']
        if link == '#':
            continue
        link = client.replaceHTMLCodes(link)

        name = client.parseDOM(item.content, 'img', ret='alt')[0]
        name = client.replaceHTMLCodes(name)

        desc = client.parseDOM(item.content, 'p', attrs={'class': 'subt'})[0]
        desc = clear_Title(desc)

        try:
            poster = client.parseDOM(item.content, 'img', ret='data-src')[0]
        except IndexError:
            poster = client.parseDOM(item.content, 'img', ret='src')[0]
        poster = client.replaceHTMLCodes(poster)
        poster = 'https:' + poster if poster.startswith('//') else poster

        if six.PY2:
            link = link.encode('utf-8')
            name = name.encode('utf-8')
            desc = desc.decode('ascii', errors='ignore')
            poster = poster.encode('utf-8')
        link = '{}/{}'.format(base_url, link)
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
    # xbmc.log('URLLLL: {}'.format(url))
    if 'm3u8' in url:
        link = url
        link += '|User-Agent={}&Referer={}'.format('iPad', quote_plus(headers['Referer']))
        liz = xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
    else:
        import requests
        url = base_url + url if url.startswith('/') else url
        # xbmc.log('URLLLL2: {}'.format(url))
        # cj = client.request(base_url, headers=headers, output='cookie')
        # xbmc.log('COOKIES: {}'.format(str(cj)))
        # headers['Cookie'] = cj
        info = requests.get(url, headers=headers).text
        info = six.ensure_str(info, encoding='utf-8')
        # xbmc.log('INFOOOO: {}'.format(info))
        head = client.parseDOM(info, 'title')[0]
        # title = client.parseDOM(info, 'meta', ret='content', attrs={'name': 'description'})[0].encode('utf-8')
        # name = '{0} - {1}'.format(head, title)
        poster = client.parseDOM(info, 'meta', ret='content', attrs={'property': 'og:image'})[0]
        link = re.findall(r'''source:['"](.+?)['"]\,''', info, re.DOTALL)[0]
        link = "https://hd-auth.skylinewebcams.com/" + link.replace('livee', 'live') if link.startswith('live') else link
        # xbmc.log('LINK: {}'.format(link))
        link += '|User-Agent=iPad&Referer={}'.format(BASEURL)
        if six.PY2:
            head = head.encode('utf-8')
            link = str(link)
        liz = xbmcgui.ListItem(head)
        liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': poster, 'fanart': fanart})

    try:
        liz.setInfo(type="Video", infoLabels={"Title": description})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(link)
        # control.player.play(link, liz)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except:
        control.infoDialog("[COLOR red]Dead Link[/COLOR]!\n[COLOR white]Please Try Another[/COLOR]", NAME, '')


def addDir(name, url, mode, iconimage, fanart, description):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(
        name) + "&iconimage=" + quote_plus(iconimage) + "&description=" + quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setProperty('fanart_image', fanart)
    if mode == 100 or mode == 'BUG' or mode == 7:
        liz.setProperty("IsPlayable", "true")
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    elif mode == 7:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    else:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'): params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2: param[splitparams[0]] = splitparams[1]
    return param


params = get_params()
url = BASEURL
name = NAME
iconimage = ICON
mode = None
fanart = FANART
description = DESCRIPTION
query = None

try:
    url = unquote_plus(params["url"])
except:
    pass
try:
    name = unquote_plus(params["name"])
except:
    pass
try:
    iconimage = unquote_plus(params["iconimage"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    fanart = unquote_plus(params["fanart"])
except:
    pass
try:
    description = unquote_plus(params["description"])
except:
    pass
try:
    query = unquote_plus(params["query"])
except:
    pass

print(str(NAME) + ': ' + str(VERSION))
print("Mode: " + str(mode))
print("URL: " + str(url))
print("Name: " + str(name))
print("IconImage: " + str(iconimage))
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
elif mode == 9:
    get_cat_cams()
elif mode == 100:
    resolve(name, url, iconimage, description)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
