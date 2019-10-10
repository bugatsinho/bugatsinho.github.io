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
# ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://freevideolectures.com/'
yout_vid = 'plugin://plugin.video.youtube/play/?video_id={}'
yout_list = 'plugin://plugin.video.youtube/play/?playlist_id={}'

headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

reload(sys)
sys.setdefaultencoding("utf-8")


def Main_menu():
    addDir('[B]Most Popular Courses[/B]', BASEURL, 7, ICON, FANART, '')
    addDir('[B]Featured Online Courses[/B]', BASEURL, 6, ICON, FANART, '')
    addDir('[B]Artificial Intelligence[/B]', '', 11, ICON, FANART, '')
    addDir('[B]Computer Science[/B]', '', 12, ICON, FANART, '')
    addDir('[B]Engineering[/B]', '', 13, ICON, FANART, '')
    addDir('[B]Maths & Sciences[/B]', '', 14, ICON, FANART, '')
    addDir('[B]Medicine & Others[/B]', '', 15, ICON, FANART, '')
    addDir('[B]Categories[/B]', BASEURL, 4, ICON, FANART, '')
    addDir('[B]Search[/B]', '', 8, ICON, FANART, '')
    addDir('[B][COLOR cyan]Settings[/B][/COLOR]', '', 9, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]%s[/B][/COLOR]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def artifisial():
    addDir('[B]Machine learning[/B]', BASEURL + 'subject/machine-learning/', 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def cs():
    addDir('[B]Computer Science[/B]', BASEURL+ 'subject/computer-science/', 5, ICON, FANART, '')
    addDir('[B]Programming[/B]', BASEURL + 'subject/programming/', 5, ICON, FANART, '')
    addDir('[B]Database Design[/B]', BASEURL + 'subject/data-structures/', 5, ICON, FANART, '')
    addDir('[B]Web Design[/B]', BASEURL + 'subject/web-designing/', 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def engine():
    addDir('[B]Electronics Engineering[/B]', BASEURL + 'subject/electronics/', 5, ICON, FANART, '')
    addDir('[B]Electrical Engineering[/B]', BASEURL + 'subject/electrical-engineering/', 5, ICON, FANART, '')
    addDir('[B]Mechanical Engineering[/B]', BASEURL + 'subject/mechanical/', 5, ICON, FANART, '')
    addDir('[B]Civil Engineering[/B]', BASEURL + 'subject/civil-engineering/', 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def maths():
    addDir('[B]mathematics[/B]', BASEURL + 'subject/mathematics/', 5, ICON, FANART, '')
    addDir('[B]Physics[/B]', BASEURL + 'subject/physics/', 5, ICON, FANART, '')
    addDir('[B]Chemistry[/B]', BASEURL + 'subject/chemistry/', 5, ICON, FANART, '')
    addDir('[B]Biology[/B]', BASEURL + 'subject/biology/', 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def meds():
    addDir('[B]Medical Sciences[/B]', BASEURL + 'subject/medicine/', 5, ICON, FANART, '')
    addDir('[B]Anatomy & Physiology[/B]', BASEURL + 'subject/anatomy-physiology/', 5, ICON, FANART, '')
    addDir('[B]Economics[/B]', BASEURL + 'subject/economics/', 5, ICON, FANART, '')
    addDir('[B]Philosophy[/B]', BASEURL + 'subject/philosophy/', 5, ICON, FANART, '')
    addDir('[B]Psychology[/B]', BASEURL + 'subject/psychology/', 5, ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_categories(url):
    r = client._basic_request(url, headers=headers)
    r = client.parseDOM(r, 'div', attrs={'class': 'fullbody ptb-60'})[1]
    xbmc.log('CaTAEGORIES: %s' % str(r))
    cats = client.parseDOM(r, 'li')
    xbmc.log('CTAEGORIES: %s' % str(cats))
    for cat in cats:
        link = client.parseDOM(cat, 'a', ret='href')[0]
        title = client.parseDOM(cat, 'h5')[0]
        addDir('[B]%s[/B]' % str(title), link, 5, ICON, '', str(title))
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_popular(url):#7
    r = client._basic_request(url, headers=headers)
    r = client.parseDOM(r, 'div', attrs={'class': 'fullbody ptb-60'})[0]
    #class="fvl-productBox shadow-hover"
    posts = client.parseDOM(r, 'div', attrs={'class': 'fvl-productBox shadow-hover'})
    for post in posts:
        if 'FREE' in post:
            link = client.parseDOM(post, 'a', ret='href')[0]
            poster = client.parseDOM(post, 'img', ret='src')[0]
            desc = client.parseDOM(post, 'div', attrs={'class': 'fvl-productDescription'})[0]
            title = client.parseDOM(desc, 'h5')[0]
            plot = client.parseDOM(desc, 'span')[0]
            rate = client.parseDOM(post, 'div', attrs={'class': 'starrr'}, ret='data-rating')[0]
            desc = title + '\n' + str(plot)
            title += '[' + str(rate) + ']'
            addDir('[B]%s[/B]' % title, link, 5, poster, '', str(desc))
        else:
            pass

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

def get_feature(url): #6
    r = client._basic_request(url, headers=headers)
    r = client.parseDOM(r, 'div', attrs={'class': 'fullbody ptb-60 bg-dark'})[0]
    # class="fvl-productBox shadow-hover"
    posts = client.parseDOM(r, 'div', attrs={'class': 'fvl-productBox shadow-hover'})
    for post in posts:
        if 'FREE' in post:
            link = client.parseDOM(post, 'a', ret='href')[0]
            poster = client.parseDOM(post, 'img', ret='src')[0]
            desc = client.parseDOM(post, 'div', attrs={'class': 'fvl-productDescription'})[0]
            title = client.parseDOM(desc, 'h5')[0]
            plot = client.parseDOM(desc, 'span')[0]
            rate = client.parseDOM(post, 'div', attrs={'class': 'starrr'}, ret='data-rating')[0]
            desc = title + '\n' + str(plot)
            title += '[' + str(rate) + ']'
            addDir('[B]%s[/B]' % title, link, 5, poster, '', str(desc))
        else:
            pass

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_content(url): #5 <div class="products-list__item shadow-hover">
    r = client._basic_request(url, headers=headers)
    # data = client.parseDOM(r, 'div', attrs={'class': 'products-view'})[0]
    data = client.parseDOM(r, 'div', attrs={'class': 'products-view__list.+?'})
    xbmc.log('DATAAA: %s' % str(data))
    for item in data:
        if 'FREE' in item:
            link = client.parseDOM(item, 'a', ret='href')[0]
            link = client.replaceHTMLCodes(link)
            link = link.encode('utf-8')

            name = client.parseDOM(item, 'a')[1]
            name = client.replaceHTMLCodes(name)
            name = name.encode('utf-8')

            desc = client.parseDOM(item, 'div', attrs={'class': 'product-card__description'})[0]
            desc = clear_Title(desc)
            desc = desc.decode('ascii', errors='ignore')

            univ = client.parseDOM(item, 'div', attrs={'class': 'product-card__category'})[0]
            un_name, un_link = [client.parseDOM(univ, 'a')[0], client.parseDOM(univ, 'a', ret='href')[0]]
            un_name = re.sub('<.+?>', '', un_name)
            un_name = un_name.encode('utf-8')


            poster = client.parseDOM(item, 'img', ret='src')[0]
            poster = client.replaceHTMLCodes(poster)
            poster = 'https:' + poster if poster.startswith('//') else poster
            poster = poster.encode('utf-8')

            addDir('[B]%s[/B]' % name, link, 10, poster, '', desc)
            if not 'university' in url:
                addDir('[B]Find lectures from %s[/B]' % un_name, un_link, 5, poster, '', desc)
        else:
            pass

    try:
        np = re.findall('''<li><a href="(.+?)">Next''', r, re.DOTALL)[0]
        page = np.split('/')[:-1][-1]
        page = '[B][COLORlime]{}[B][COLORwhite])[/B][/COLOR]'.format(page)
        np = client.replaceHTMLCodes(np)
        addDir('[B][COLORgold]Next Page>>>[/COLOR] [COLORwhite]({}'.format(page), np, 5, ICON, '', 'Next Page')
    except:
        pass
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_lectures(name, url, poster, desc):
    r = client._basic_request(url, headers=headers)
    posts = client.parseDOM(r, 'li', attrs={'class': 'class-list__row'})
    for post in posts:
        link = client.parseDOM(post, 'a', ret='href')[0]
        link = client.replaceHTMLCodes(link)
        link = link.encode('utf-8')

        name = client.parseDOM(post, 'a')[0]
        name = client.replaceHTMLCodes(name)
        name = name.encode('utf-8')

        addDir('[B]%s[/B]' % name, link, 100, poster, '', desc)

    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

def search():#8
    keyb = xbmc.Keyboard('', 'Search')
    keyb.doModal()
    if keyb.isConfirmed():
        search = urllib.quote_plus(keyb.getText())
        url = BASEURL + "search/{}" + search
        get_content(url)
    else:
        return


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
    url = BASEURL + url if url.startswith('/') else url
    info = client._basic_request(url, headers=headers)
    # title = client.parseDOM(info, 'meta', ret='content', attrs={'name': 'description'})[0].encode('utf-8')
    # name = '{0} - {1}'.format(head, title)
    #<div class="youtube-player" data-id="0Eeuqh9QfNI"></div>
    link_id = client.parseDOM(info, 'div', ret='data-id', attrs={'class': 'youtube-player'})[0]
    link = yout_vid.format(link_id)
    liz = xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
    try:
        liz.setInfo(type="Video", infoLabels={"Title": description})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(link)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except:
        control.infoDialog("[COLOR red]Dead Link[/COLOR]!\n[COLOR white]Please Try Another[/COLOR]", NAME, '')


def addDir(name, url, mode, iconimage, fanart, description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setProperty('fanart_image', fanart)
    if mode == 100 or mode == 'BUG' or mode == 9:
        liz.setProperty("IsPlayable", "true")
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
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
elif mode == 11:
    artifisial()
elif mode == 12:
    cs()
elif mode == 13:
    engine()
elif mode == 14:
    maths()
elif mode == 15:
    meds()
elif mode == 4:
    get_categories(url)
elif mode == 5:
    get_content(url)
elif mode == 6:
    get_feature(url)
elif mode == 7:
    get_popular(url)
elif mode == 10:
    get_lectures(name, url, iconimage, description)
elif mode == 8:
    search()
elif mode == 9:
    Open_settings()
elif mode == 100:
    resolve(name, url, iconimage, description)
xbmcplugin.endOfDirectory(int(sys.argv[1]))

