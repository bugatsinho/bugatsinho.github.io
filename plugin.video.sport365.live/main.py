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
import json
import sys
import re
import os
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

dialog = xbmcgui.Dialog()

base_url        = sys.argv[0]
addon_handle    = int(sys.argv[1])
args            = urlparse.parse_qs(sys.argv[2][1:])
my_addon        = xbmcaddon.Addon()
addonName       = my_addon.getAddonInfo('name')
my_addon_id     = my_addon.getAddonInfo('id')
PATH            = my_addon.getAddonInfo('path')
VERSION         = my_addon.getAddonInfo('version')
DATAPATH        = xbmc.translatePath(my_addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES       = PATH+'/resources/'

sys.path.append(os.path.join(RESOURCES, "lib"))

FANART = my_addon.getAddonInfo('fanart')
ICON = my_addon.getAddonInfo('icon')

mode = args.get('mode', None)
fname = args.get('foldername', [''])[0]
ex_link = args.get('ex_link', [''])[0]
params = args.get('params', [{}])[0]

reload(sys)
sys.setdefaultencoding("utf-8")

def play_stream(params):
    params = eval(params)
    service = params.get('_service')
    act = params.get('_act')
    url = params.get('_url') + str(my_addon.getSetting('language'))
    mod = __import__(service)
    if act == 'ListChannels':
        items = mod.getChannels(ex_link, url)
        img_service = '%s.png' % (RESOURCES + service)
        for one in items:
            params.update({'title': one.get('title', '')})
            addDir(one.get('title', ''), one['url'], params=params, mode='get_streams_play',
                        infoLabels=one, iconImage=one.get('img', img_service), fanart=FANART)


def get_streams_play(params):
    import sport365 as mod
    params = eval(params)
    orig_title = params.get('title')
    frames = mod.getStreams(ex_link)
    if frames:
        for frame in frames:
            params.update({"title": orig_title})
            addLinkItem(frame.get('title', ''), str(frame), mode='take_stream',
                        params=params, iconimage=ICON, fanart=FANART,  IsPlayable=True)
            # addDir(frame.get('title', ''), json.dumps(frame), params=params,
            #        mode='take_stream', iconImage=ICON, fanart=FANART)


def enable_silent_inputstream():
    try:
        isa_enable()
        rtmp_enable()
    except BaseException:
        return


def take_stream(params):
    import sport365 as mod
    params = eval(params)
    orig_title = params.get('title')
    # busy()
    xbmc.log(str(ex_link), level=xbmc.LOGNOTICE)
    stream_url, url, header, title, ref = mod.getChannelVideo(str(ex_link))
    # xbmc.log(stream_url, level=xbmc.LOGNOTICE)
    # xbmc.log(ref, level=xbmc.LOGNOTICE)
    # xbmc.log(title, level=xbmc.LOGNOTICE)

    if stream_url:
        UA = 'Mozilla/5.0 (Linux; Android 8.0; Nexus 6P Build/OPP3.170518.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.121 Mobile Safari/537.36'
        hdrs = 'User-Agent={}&Referer={}'.format(urllib.quote(UA), urllib.quote('http://h5.adshell.net/peer5'))
        liz = xbmcgui.ListItem(label=orig_title)
        liz.setArt({"fanart": FANART, "icon": ICON})
        liz.setInfo(type="Video", infoLabels={"title": orig_title,
                                              'mediatype': 'video'})
        liz.setProperty("IsPlayable", "true")
        idle()
        if my_addon.getSetting('play') == 'Inputstream':

            stream_url = stream_url.replace('/i', '/index.m3u8') if stream_url.endswith('/i') else stream_url
            stream_url += '|' + hdrs
            liz.setPath(stream_url)
            if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 17.5:
                liz.setMimeType('application/vnd.apple.mpegurl')
                liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
                liz.setProperty('inputstream.adaptive.stream_headers', str(hdrs))
            else:
                liz.setProperty('inputstreamaddon', None)
                liz.setContentLookup(True)


            try:
                # import threading
                # thread = threading.Thread(name='sport356Thread', target=sport356Thread2, args=[url, header])
                # thread.start()
                # xbmc.Player().play(stream_url, liz)
                xbmcplugin.setResolvedUrl(addon_handle, True, liz)
                #ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=stream_url, listitem=liz, isFolder=False)
            except BaseException:
                pass

        elif my_addon.getSetting('play') == 'Streamlink':
            import streamlink.session
            session = streamlink.session.Streamlink()

            stream_url = 'hls://' + stream_url.replace('/i', '/index.m3u8') if stream_url.endswith('/i') else\
                'hls://' + stream_url
            hdrs += '&Origin=http://h5.adshell.net'
            session.set_option("http-headers", hdrs)

            streams = session.streams(stream_url)
            stream_url = streams['best'].to_url() + '|' + hdrs

            liz.setPath(stream_url)
            idle()

            # import threading
            # thread = threading.Thread(name='sport356Thread', target=sport356Thread2, args=[url, header])
            # thread.start()
            xbmcplugin.setResolvedUrl(addon_handle, False, liz)

        else:
            try:
                stream_url = 'plugin://plugin.video.f4mTester/?streamtype=HLSRETRY&url={0}&name={1}'.format(
                    urllib.quote_plus(stream_url), urllib.quote_plus(orig_title))
                liz.setPath(stream_url)
                idle()
                xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
                xbmc.executebuiltin('RunPlugin(' + stream_url + ')')
                return
            except BaseException:
                pass

    else:
        xbmcgui.Dialog().ok("Sorry for that", 'plz contact Dev')


def resolve_stream(name, url, description):
    pass


## COMMON Functions

def addLinkItem(name, url, mode, params=1, iconimage='DefaultFolder.png', infoLabels=False, IsPlayable=True,
                fanart=FANART, itemcount=1, contextmenu=None):
    u = build_url({'mode': mode, 'foldername': name, 'ex_link': url, 'params': params})

    liz = xbmcgui.ListItem(name)

    art_keys = ['thumb', 'poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'icon']
    art = dict(zip(art_keys, [iconimage for x in art_keys]))
    art['landscape'] = fanart if fanart else art['landscape']
    art['fanart'] = fanart if fanart else art['landscape']
    liz.setArt(art)

    if not infoLabels:
        infoLabels = {"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    if IsPlayable:
        liz.setProperty('IsPlayable', 'true')

    if contextmenu:
        contextMenuItems = contextmenu
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)

    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=False, totalItems=itemcount)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask="%R, %Y, %P")
    return ok


def addDir(name, ex_link=None, params=1, mode='folder', iconImage='DefaultFolder.png', infoLabels=None, fanart=FANART,
           contextmenu=None):
    url = build_url({'mode': mode, 'foldername': name, 'ex_link': ex_link, 'params': params})

    nofolders = ['take_stream', 'opensettings', 'enable_input', 'forceupdate', 'open_news', 'ccache', 'showalts']
    folder = False if mode in nofolders else True

    li = xbmcgui.ListItem(name)
    if infoLabels:
        li.setInfo(type="video", infoLabels=infoLabels)
    li.setProperty('fanart_image', fanart)
    art_keys = ['thumb', 'poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'icon']
    art = dict(zip(art_keys, [iconImage for x in art_keys]))
    art['landscape'] = fanart if fanart else art['landscape']
    art['fanart'] = fanart if fanart else art['landscape']
    li.setArt(art)

    if contextmenu:
        contextMenuItems = contextmenu
        li.addContextMenuItems(contextMenuItems, replaceItems=True)

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=folder)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask="%R, %Y, %P")


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


def idle():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    else:
        xbmc.executebuiltin('Dialog.Close(busydialog)')


def busy():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    else:
        xbmc.executebuiltin('ActivateWindow(busydialog)')


def Settings():

    try:
        idle()
        xbmcaddon.Addon(my_addon_id).openSettings()
    except:
        return


def json_rpc(command):
    # This function was taken from tknorris's kodi.py
    jsonrpc = xbmc.executeJSONRPC
    if not isinstance(command, basestring):
        command = json.dumps(command)
    response = jsonrpc(command)

    return json.loads(response)


def enable_addon(addon_id, enable=True):

    command = {
        "jsonrpc":"2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": addon_id, "enabled": enable}, "id": 1
    }

    json_rpc(command)


def addon_version(addon_id):

    version = int(xbmc.getInfoLabel('System.AddonVersion({0})'.format(addon_id)).replace('.', ''))

    return version


def addon_details(addon_id, fields=None):
    if fields is None:
        fields = ["enabled"]

    command = {
        "jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "id": 1, "params": {
            "addonid": addon_id, "properties": fields
        }
    }

    result = json_rpc(command)['result']['addon']

    return result


def isa_enable():
    if addon_version('xbmc.python') < 2250:
        dialog.ok(addonName, 'System is not compatible with inputstream type addons')
        return

    try:
        enabled = addon_details('inputstream.adaptive').get('enabled')
    except Exception:
        enabled = False

    try:
        if enabled:
            #dialog.notification(addonName, 'Inputstream adaptive addon is already enabled')
            return

        else:
            xbmc_path = os.path.join('special://xbmc', 'addons', 'inputstream.adaptive')
            home_path = os.path.join('special://home', 'addons', 'inputstream.adaptive')

            if os.path.exists(xbmc.translatePath(xbmc_path)) or os.path.exists(xbmc.translatePath(home_path)):
                yes = dialog.yesno(addonName, 'Inputstream adaptive (DASH) is not enabled. Do you to enabled it now?',
                                   yeslabel='YES', nolabel='NO')

                if yes:
                    enable_addon('inputstream.adaptive')
                    dialog.notification(addonName, 'Success')

            else:
                try:
                    xbmc.executebuiltin('InstallAddon(inputstream.adaptive)')

                except Exception:

                    dialog.ok(addonName, line1='Could not install requested addon,'
                                               'to install it you have to try another way,'
                                               ' such as your distribution\'s repositories.')
        return
    except Exception:
        dialog.notification(addonName, 'Inputstream adaptive addon could not be enabled')


def rtmp_enable():

    if addon_version('xbmc.python') < 2250:
        dialog.ok(addonName, 'System is not compatible with inputstream type addons')
        return

    try:
        enabled = addon_details('inputstream.rtmp').get('enabled')
    except Exception:
        enabled = False

    try:
        if enabled:
            #dialog.notification(addonName, 'Inputstream RTMP addon is already enabled')
            return
        else:
            xbmc_path = os.path.join('special://xbmc', 'addons', 'inputstream.rtmp')
            home_path = os.path.join('special://home', 'addons', 'inputstream.rtmp')

            if os.path.exists(xbmc.translatePath(xbmc_path)) or os.path.exists(xbmc.translatePath(home_path)):

                yes = dialog.yesno(addonName, 'Inputstream RTMP is not enabled. Do you to enabled it now?',
                                   yeslabel='YES', nolabel='NO')

                if yes:
                    enable_addon('inputstream.rtmp')
                    dialog.notification(addonName, 'Success')

            else:
                try:
                    xbmc.executebuiltin('InstallAddon(inputstream.rtmp)')

                except Exception:
                    dialog.ok(addonName, line1='Could not install requested addon,'
                                               'to install it you have to try another way,'
                                               ' such as your distribution\'s repositories.')
        return
    except Exception:
        dialog.notification(addonName, 'Inputstream RTMP addon could not be enabled')

def show_alt():
    if my_addon.getSetting('domain') == 'false':
        my_addon.setSetting('domain', 'true')
    else:
        my_addon.setSetting('domain', 'false')
    xbmc.sleep(100)
    xbmc.executebuiltin('Container.Refresh')


if mode is None:
    if addon_version('xbmc.python') < 2250:
        my_addon.setSetting('play', 'F4M')
    else:
        enable_silent_inputstream()
    # domain = my_addon.getSetting('domain')
    # if 'livesport' in domain:
    #     url = 'http://www.livesportstreams.tv/'
    # else:
    #     url = 'http://www.{}.live/'.format(domain)

    addDir('News - Updates', ex_link='', mode='open_news', iconImage=ICON, fanart=FANART)
    addDir('Sport365 LIVE', ex_link='',
           params={'_service': 'sport365', '_act': 'ListChannels', '_url': 'http://www.sport365.live/'}, mode='site2',
           iconImage=ICON, fanart=FANART)

    addDir('[COLORcyan]Alternative Domains[/COLOR]', ex_link='', mode='showalts',
           iconImage=ICON, fanart=FANART)
    if my_addon.getSetting('domain') == 'true':
        addDir('Sport365 SX', ex_link='',
               params={'_service': 'sport365', '_act': 'ListChannels', '_url': 'http://www.sport365.sx/'}, mode='site2',
               iconImage=ICON, fanart=FANART)
        addDir('Sport247 LIVE', ex_link='',
               params={'_service': 'sport365', '_act': 'ListChannels', '_url': 'http://www.sport247.live/'}, mode='site2',
               iconImage=ICON, fanart=FANART)
        addDir('s365 LIVE(alt)', ex_link='',
               params={'_service': 'sport365', '_act': 'ListChannels', '_url': 'http://www.s365.live/'}, mode='site2',
               iconImage=ICON, fanart=FANART)
    # addDir('LiveSportStreams', ex_link='',
    #        params={'_service': 'sport365', '_act': 'ListChannels', '_url': 'http://www.livesportstreams.tv/'},
    #        mode='site2', iconImage=ICON, fanart=FANART)

    addDir('Settings', ex_link='', mode='opensettings', iconImage=ICON, fanart=FANART)
    addDir('Clear Cache', ex_link='', mode='ccache', iconImage=ICON, fanart=FANART)
    addDir('[COLOR gold][B]Version: [COLOR lime]%s[/COLOR][/B]' % VERSION, ex_link='', mode='forceupdate',
           iconImage=ICON, fanart=FANART)
    #li = xbmcgui.ListItem(label = '[COLOR blue]aktywuj PVR Live TV[/COLOR]', iconImage=RESOURCES+'PVR.png')
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'mode': 'Opcje'}) ,listitem=li)


elif mode[0] == 'site2':
    play_stream(params)

elif mode[0] == 'folder':
    pass

elif mode[0] == 'take_stream':
    take_stream(params)

elif mode[0] == 'get_streams_play':
    get_streams_play(params)

elif mode[0] == 'opensettings':
    Settings()
elif mode[0] == 'ccache':
    from resources.lib import cache
    cache.delete()
elif mode[0] == 'enable_adaptive':
   isa_enable()
   Settings()

elif mode[0] == 'enable_rtmp':
   rtmp_enable()
   Settings()

elif mode[0] == 'open_news':
    import newsbox
    newsbox.welcome()

elif mode[0] == 'showalts':
    show_alt()

elif mode[0] == 'forceupdate':
    dialog = xbmcgui.Dialog()
    dialog.notification(addonName, "Triggered a request for addon updates", ICON, 5000, sound=True)
    xbmc.executebuiltin('UpdateAddonRepos')

else:
    pass

xbmcplugin.endOfDirectory(addon_handle)

