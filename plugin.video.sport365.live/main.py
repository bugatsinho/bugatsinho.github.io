# -*- coding: utf-8 -*-
'''

Credits to original dev GalAnonim!
╭━━╮╱╱╱╱╱╱╱╱╱╱╭╮╱╱╱╱╱╱╱╭╮
┃╭╮┃╱╱╱╱╱╱╱╱╱╭╯╰╮╱╱╱╱╱╱┃┃
┃╰╯╰┳╮╭┳━━┳━━╋╮╭╋━━┳┳━╮┃╰━┳━━╮
┃╭━╮┃┃┃┃╭╮┃╭╮┃┃┃┃━━╋┫╭╮┫╭╮┃╭╮┃
┃╰━╯┃╰╯┃╰╯┃╭╮┃┃╰╋━━┃┃┃┃┃┃┃┃╰╯┃
╰━━━┻━━┻━╮┣╯╰╯╰━┻━━┻┻╯╰┻╯╰┻━━╯
╱╱╱╱╱╱╱╭━╯┃
╱╱╱╱╱╱╱╰━━╯
'''
import sys
import re
import os
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import threading

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')
my_addon_id     = my_addon.getAddonInfo('id')
PATH            = my_addon.getAddonInfo('path')
DATAPATH        = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES       = PATH+'/resources/'

sys.path.append(os.path.join(RESOURCES, "lib"))

FANART = my_addon.getAddonInfo('fanart')
ICON = my_addon.getAddonInfo('icon')


## COMMON Functions

def addLinkItem(name, url, mode, params=1, iconimage='DefaultFolder.png', infoLabels=False, IsPlayable=True,fanart=FANART,itemcount=1,contextmenu=None):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link' : url, 'params':params})
    
    liz = xbmcgui.ListItem(name)
    
    art_keys=['thumb','poster','banner','fanart','clearart','clearlogo','landscape','icon']
    art = dict(zip(art_keys,[iconimage for x in art_keys]))
    art['landscape'] = fanart if fanart else art['landscape'] 
    art['fanart'] = fanart if fanart else art['landscape'] 
    liz.setArt(art)
    
    if not infoLabels:
        infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')

    if contextmenu:
        contextMenuItems=contextmenu
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)

    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz,isFolder=False,totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok

def addDir(name, ex_link=None, params=1, mode='folder', iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART, contextmenu=None):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link': ex_link, 'params': params})

    li = xbmcgui.ListItem(name)
    if infoLabels:
        li.setInfo(type="video", infoLabels=infoLabels)
    li.setProperty('fanart_image', fanart)
    art_keys=['thumb', 'poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'icon']
    art = dict(zip(art_keys,[iconImage for x in art_keys]))
    art['landscape'] = fanart if fanart else art['landscape'] 
    art['fanart'] = fanart if fanart else art['landscape'] 
    li.setArt(art)


    if contextmenu:
        contextMenuItems=contextmenu
        li.addContextMenuItems(contextMenuItems, replaceItems=True) 

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
    
def build_url(query):
    return base_url + '?' + urllib.urlencode(encoded_dict(query))


def sport356Thread(url):
    import sport365 as s
    from time import gmtime, strftime
    href, headers= url.split('|')
    header={}
    header['Referer']= urllib.unquote(re.compile('Referer=(.*?)&').findall(headers)[0])
    header['User-Agent']= urllib.unquote(re.compile('User-Agent=(.*?)&').findall(headers)[0])
    header['Origin']= 'http://h5.adshell.net'
    header['If-Modified-Since']= strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
    header['Connection']= 'keep-alive'
    header['etag']= '"5820cda8-2b9"'
    print '#'*25
    print '#'*25
    xbmc.sleep(2000)    # speep
    player = xbmc.Player()
    player.pause()
    print 'sport356Thread: passed url: [%s] '%href
    #print header
    h=header
    while player.isPlaying():
        print 'sport356Thread: KODI IS PLAYING, sleeping 1s'
        a,hret=s.getUrlrh(href,header=header)
        header['etag'] = hret.get('etag','')
        header['date'] = hret.get('date','')
       
        #h.update(header)
        print a,hret
        xbmc.sleep(1000)
    print 'sport356Thread: KODI STOPPED, OUTSIDE WHILE LOOP ... EXITING'


def sport356Thread2(url, header):
    import sport365 as s
    import re

    player = xbmc.Player()
    xbmc.sleep(2000)
    print 'sport356Thread: passed url: [%s] ' % url
    player.pause()

    while player.isPlaying():
        print 'sport356Thread: KODI IS PLAYING, sleeping 4s'
        a, c = s.getUrlc(url, header=header, usecookies=True)
        banner = re.compile('url:["\'](.*?)[\'"]').findall(a)[0]
        xbmc.log(banner)
        xbmc.sleep(2000)
        s.getUrlc(banner)
        xbmc.sleep(2000)
    print 'sport356Thread: KODI STOPED, OUTSIDE WHILE LOOP ... EXITING'

## ######################
## MAIN
## ######################

# Get passed arguments


mode = args.get('mode', None)
fname = args.get('foldername', [''])[0]
ex_link = args.get('ex_link', [''])[0]
params = args.get('params', [{}])[0]


def play_stream(params):
    params = eval(params)
    service = params.get('_service')
    act = params.get('_act')
    mod = __import__(service)
    if act == 'ListChannels':
        params.update({'_act': 'get_streams_play'})
        items = mod.getChannels(ex_link)
        img_service = '%s.png' % (RESOURCES + service)
        print img_service
        for one in items:
            addLinkItem(one.get('title', ''), one['url'], params=params, mode='site2', IsPlayable=True,
                        infoLabels=one, iconimage=one.get('img', img_service))

    if act == 'get_streams_play':
        frames = mod.getStreams(ex_link)
        if frames:
            t = [frame['title'] for frame in frames]
            s = xbmcgui.Dialog().select("Select Stream", t)
            if s == -1:
                return
            elif s > -1:
                stream_url, url, header = mod.getChannelVideo(frames[s])
            else:
                return
            if stream_url:
                # thread = threading.Thread(name='sport356Thread', target=sport356Thread2, args=[url,header])
                # thread.start()
                xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else:
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcgui.Dialog().ok("Sorry for that", 'plz contact Dev')


if mode is None:
    addDir('Sport365 LIVE', ex_link='', params={'_service':'sport365','_act':'ListChannels'}, mode='site2', iconImage=ICON, fanart=FANART)
    #li = xbmcgui.ListItem(label = '[COLOR blue]aktywuj PVR Live TV[/COLOR]', iconImage=RESOURCES+'PVR.png')
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'mode': 'Opcje'}) ,listitem=li)


elif mode[0] == 'site2':
    play_stream(params)

elif mode[0] == 'folder':
    pass

else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)

