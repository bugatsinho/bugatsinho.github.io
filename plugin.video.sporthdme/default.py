# -*- coding: utf-8 -*-
import base64
import re
import sys
import urllib
import urlparse
import json
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
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

BASEURL = 'http://www.sporthd.me/'
Live_url = 'http://www.sporthd.me/index.php?'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal
reload(sys)
sys.setdefaultencoding("utf-8")

#######################################
# Time and Date Helpers
#######################################
try:
    local_tzinfo = tzlocal()
    locale_timezone = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}'))
    if locale_timezone['result']['value']:
        local_tzinfo = gettz(locale_timezone['result']['value'])
except:
    pass


def convDateUtil(timestring, newfrmt='default', in_zone='UTC'):
    if newfrmt == 'default':
        newfrmt = xbmc.getRegion('time').replace(':%S', '')
    try:
        in_time = parse(timestring)
        in_time_with_timezone = in_time.replace(tzinfo=gettz(in_zone))
        local_time = in_time_with_timezone.astimezone(local_tzinfo)
        return local_time.strftime(newfrmt)
    except:
        return timestring


def Main_menu():
    addDir('[B][COLOR white]LIVE EVENTS[/COLOR][/B]', Live_url, 5, ICON, FANART, '')
    addDir('[B][COLOR white]SPORTS[/COLOR][/B]', '', 3, ICON, FANART, '')
    addDir('[B][COLOR white]BEST LEAGUES[/COLOR][/B]', '', 2, ICON, FANART, '')
    addDir('[B][COLOR gold]Settings[/COLOR][/B]', '', 10, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def leagues_menu():
    addDir('[B][COLOR white]Uefa Champions League[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=uefa-champions-league', 5,
           'http://www.sporthd.me/flags/uefa-champions-league.png', FANART, 'Uefa Champions League')
    addDir('[B][COLOR white]Uefa Europa League[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=uefa-europa-league',
           5, 'http://www.sporthd.me/flags/uefa-europa-league.png', FANART, 'Uefa Europa League')
    addDir('[B][COLOR white]Premier League[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=premier-league', 5,
           'http://www.sporthd.me/flags/premier-league.png', FANART, 'Premier League')
    addDir('[B][COLOR white]Bundesliga[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=bundesliga', 5,
           'http://www.sporthd.me/flags/bundesliga.png', FANART, 'Bundesliga')
    addDir('[B][COLOR white]Laliga[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=laliga', 5,
           'http://www.sporthd.me/flags/spanish-primera-division.png', FANART, 'Laliga')
    addDir('[B][COLOR white]Serie A[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=serie-a', 5,
           'http://www.sporthd.me/flags/serie-a.png', FANART, 'Serie a')
    addDir('[B][COLOR white]France Ligue 1[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=france-ligue-1', 5,
           'http://www.sporthd.me/flags/france-ligue-1.png', FANART, 'France ligue 1')
    addDir('[B][COLOR white]Eredivisie[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=eredivisie', 5,
           'http://www.sporthd.me/flags/eredivisie.png', FANART, 'Eredivisie')
    addDir('[B][COLOR white]Australian A League[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=australian-a-league', 5,
           'http://www.sporthd.me/flags/australian-a-league.png', FANART, 'Australian a league')
    addDir('[B][COLOR white]MLS[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=mls', 5,
           'http://www.sporthd.me/flags/mls.png', FANART, 'Mls')
    addDir('[B][COLOR white]Rugby Top 14[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=rugby-top-14', 5,
           'http://www.sporthd.me/flags/rugby-top-14.png', FANART, 'Rugby top 14')
    addDir('[B][COLOR white]Greece Super League[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=greece-super-league', 5,
           'http://www.sporthd.me/flags/greece-super-league.png', FANART, 'Greece super league')
    addDir('[B][COLOR white]Argentina Superliga[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=argentina-superliga', 5,
           'http://www.sporthd.me/flags/argentina-superliga.png', FANART, 'Argentina superliga')
    addDir('[B][COLOR white]Portuguese Primeira Liga[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=portuguese-primeira-liga', 5,
           'http://www.sporthd.me/flags/portuguese-primeira-liga.png', FANART, 'Portuguese primeira liga')
    addDir('[B][COLOR white]Primera Division Apertura[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=primera-division-apertura', 5,
           'http://www.sporthd.me/flags/primera-division-apertura.png', FANART, 'Primera division apertura')
    addDir('[B][COLOR white]Bundesliga 2[/COLOR][/B]', 'http://www.sporthd.me/index.php?champ=bundesliga-2', 5,
           'http://www.sporthd.me/flags/bundesliga-2.png', FANART, 'Bundesliga 2')
    addDir('[B][COLOR white]Greece Super League 2[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=greece-super-league-2', 5,
           'http://www.sporthd.me/flags/greece-super-league-2.png', FANART, 'Greece super league 2')
    addDir('[B][COLOR white]Belarus Vysheyshaya Liga[/COLOR][/B]',
           'http://www.sporthd.me/index.php?champ=belarus-vysheyshaya-liga', 5,
           'http://www.sporthd.me/flags/belarus-vysheyshaya-liga.png', FANART, 'Belarus vysheyshaya liga')


def sports_menu():
    addDir('[B][COLOR white]Football[/COLOR][/B]', 'http://www.sporthd.me/?type=football', 5,
           'http://www.sporthd.me/images/football.png', FANART, 'Football')
    addDir('[B][COLOR white]Basketball[/COLOR][/B]', 'http://www.sporthd.me/?type=basketball', 5,
           'http://www.sporthd.me/images/basketball.png', FANART, 'Basketball')
    addDir('[B][COLOR white]MotorSport[/COLOR][/B]', 'http://www.sporthd.me/?type=motorsport', 5,
           'http://www.sporthd.me/images/motorsport.png', FANART, 'MotorSport')
    addDir('[B][COLOR white]Handball[/COLOR][/B]', 'http://www.sporthd.me/?type=handball', 5,
           'http://www.sporthd.me/images/handball.png', FANART, 'Handball')
    addDir('[B][COLOR white]Rugby[/COLOR][/B]', 'http://www.sporthd.me/?type=rugby', 5,
           'http://www.sporthd.me/images/rugby.png', FANART, 'Rugby')
    addDir('[B][COLOR white]NFL[/COLOR][/B]', 'http://www.sporthd.me/?type=nfl', 5,
           'http://www.sporthd.me/images/nfl.png', FANART, 'NFL')
    addDir('[B][COLOR white]UFC[/COLOR][/B]', 'http://www.sporthd.me/?type=ufc', 5,
           'http://www.sporthd.me/images/ufc.png', FANART, 'UFC')
    addDir('[B][COLOR white]Wrestling[/COLOR][/B]', 'http://www.sporthd.me/?type=wresling', 5,
           'http://www.sporthd.me/images/wresling.png', FANART, 'Wresling')
    addDir('[B][COLOR white]Hockey[/COLOR][/B]', 'http://www.sporthd.me/?type=hokey', 5,
           'http://www.sporthd.me/images/hockey.png', FANART, 'Hokey')
    addDir('[B][COLOR white]Volleyball[/COLOR][/B]', 'http://www.sporthd.me/?type=volleyball', 5,
           'http://www.sporthd.me/images/volleyball.png', FANART, 'Volleyball')
    addDir('[B][COLOR white]Darts[/COLOR][/B]', 'http://www.sporthd.me/?type=darts', 5,
           'http://www.sporthd.me/images/darts.png', FANART, 'Darts')
    addDir('[B][COLOR white]Tennis[/COLOR][/B]', 'http://www.sporthd.me/?type=tennis', 5,
           'http://www.sporthd.me/images/tennis.png', FANART, 'Tennis')
    addDir('[B][COLOR white]Boxing[/COLOR][/B]', 'http://www.sporthd.me/?type=boxing', 5,
           'http://www.sporthd.me/images/boxing.png', FANART, 'Boxing')
    addDir('[B][COLOR white]Cricket[/COLOR][/B]', 'http://www.sporthd.me/?type=cricket', 5,
           'http://www.sporthd.me/images/cricket.png', FANART, 'Cricket')
    addDir('[B][COLOR white]Baseball[/COLOR][/B]', 'http://www.sporthd.me/?type=baseball', 5,
           'http://www.sporthd.me/images/baseball.png', FANART, 'Baseball')
    addDir('[B][COLOR white]Snooker[/COLOR][/B]', 'http://www.sporthd.me/?type=snooker', 5,
           'http://www.sporthd.me/images/snooker.png', FANART, 'Snooker')
    addDir('[B][COLOR white]Chess[/COLOR][/B]', 'http://www.sporthd.me/?type=chess', 5,
           'http://www.sporthd.me/images/chess.png', FANART, 'Chess')


def get_events(url):  # 5
    data = client.request(url)
    # xbmc.log('@#@EDATAAA: {}'.format(data), xbmc.LOGNOTICE)
    events = zip(client.parseDOM(data, 'li', attrs={'class': "item itemhov"}),
                 re.findall(r'<i class="material-icons">(.+?)</a> </li>', data, re.DOTALL))
    # addDir('[COLORcyan]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
    for event, streams in events:
        # xbmc.log('@#@EVENTTTTT:%s' % event, xbmc.LOGNOTICE)
        watch = '[COLORlime]*[/COLOR]' if '>Live<' in event else '[COLORred]*[/COLOR]'
        try:
            teams = client.parseDOM(event, 'td')
            home, away = re.sub(r'\s*(<img.+?>)\s*', '', teams[0]), re.sub(r'\s*(<img.+?>)\s*', '', teams[2])
            home = home.strip().encode('utf-8')
            away = away.strip().encode('utf-8')
            teams = '[B]{0} vs {1}[/B]'.format(home, away)
        except IndexError:
            teams = client.parseDOM(event, 'center')[0]
            teams = re.sub(r'<.+?>|\s{2}', '', teams).encode('utf-8')
        lname = client.parseDOM(event, 'a')[1]
        lname = re.sub(r'<.+?>', '', lname)
        time = client.parseDOM(event, 'span', attrs={'class': 'gmt_m_time'})[0]
        time = time.split('GMT')[0].strip()
        cov_time = convDateUtil(time, 'default', 'GMT{}'.format(str(control.setting('timezone'))))
        # xbmc.log('@#@COVTIMEEE:%s' % str(cov_time), xbmc.LOGNOTICE)
        ftime = '[COLORgold][I]{}[/COLOR][/I]'.format(cov_time)
        name = '{0}{1} {2} - [I]{3}[/I]'.format(watch, ftime, teams, lname)

        # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
        streams = base64.b64encode(streams)

        icon = client.parseDOM(event, 'img', ret='src')[0]
        icon = urlparse.urljoin(BASEURL, icon)

        addDir(name, str(streams), 4, icon, FANART, name)


xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_stream(url):  # 4
    data = base64.b64decode(url)
    if 'info_outline' in data:
        control.infoDialog("[COLOR gold]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                           iconimage, 5000)
        return
    else:
        links = zip(client.parseDOM(data, 'a', ret='href'), client.parseDOM(data, 'a'))
        # xbmc.log('@#@STREAMMMMMSSSSSS:%s' % links, xbmc.LOGNOTICE)
        titles = []
        streams = []
        for link, title in links:
            streams.append(link)
            titles.append(title)

        if len(streams) > 1:
            dialog = xbmcgui.Dialog()
            ret = dialog.select('[COLORgold][B]Choose Stream[/B][/COLOR]', titles)
            if ret == -1:
                return
            elif ret > -1:
                host = streams[ret]
                # xbmc.log('@#@STREAMMMMM:%s' % host, xbmc.LOGNOTICE)
                return resolve(host)
            else:
                return
        else:
            link = links[0][0]
            return resolve(link)


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


def resolve(url):
    try:
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        # dialog.notification(AddonTitle, '[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]', icon, 5000)
        if 'acestream' in url:
            url1 = "plugin://program.plexus/?url=" + url + "&mode=1&name=acestream+"
            liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
            liz.setPath(url)
            xbmc.Player().play(url1, liz, False)
            quit()
        if '/live.cdnz' in url:
            r = client.request(url, referer=BASEURL)

            if 'hfstream.js' in r:
                regex = '''<script type='text/javascript'> width=(.+?), height=(.+?), channel='(.+?)', g='(.+?)';</script>'''
                wid, heig, chan, ggg = re.findall(regex, r, re.DOTALL)[0]
                stream = 'https://www.playerfs.com/membedplayer/'+chan+'/'+ggg+'/'+wid+'/'+heig+''
            else:
                stream = client.parseDOM(r, 'iframe', ret='src')[-1]

            r = client.request(stream, referer=url)
            # xbmc.log('@#@DATAAAA: %s' % r, xbmc.LOGNOTICE)
            try:
                flink = re.findall(r'source:\s*"(.+?)",', r, re.DOTALL)[0]
            except IndexError:
                ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', r, re.DOTALL)[0]
                ea = client.request(ea).split('=')[1]
                flink = re.findall('''videoplayer.src = "(.+?)";''', r, re.DOTALL)[0]
                flink = flink.replace('" + ea + "', ea)
            # xbmc.log('@#@STREAMMMMM111: %s' % flink, xbmc.LOGNOTICE)
            flink += '|Referer={}'.format('https://limetvv.com/')
            stream_url = flink

        else:
            stream_url = url
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmc.Player().play(stream_url, liz, False)
        quit()
        # xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)
    except Exception as e:
        # try:
        #     liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        #     liz.setInfo(type="Video", infoLabels={"Title": 'Stream Link', 'mediatype': 'video'})
        #     liz.setProperty("IsPlayable", "true")
        #     liz.setPath(str(stream_url))
        #     xbmc.Player().play(stream_url, liz)
        #     # xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)
        # except:
        control.infoDialog("[COLOR red]Dead Link[/COLOR]!", NAME, iconimage)

def Open_settings():
    control.openSettings()


def addDir(name, url, mode, iconimage, fanart, description):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(
        name) + "&iconimage=" + urllib.quote_plus(iconimage) + "&description=" + urllib.quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setProperty('fanart_image', fanart)
    if mode == 100:
        liz.setProperty("IsPlayable", "true")
        liz.addContextMenuItems([('GRecoTM Pair Tool', 'RunAddon(script.grecotm.pair)',)])
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    elif mode == 10 or mode == 'BUG':
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
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    iconimage = urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    fanart = urllib.unquote_plus(params["fanart"])
except:
    pass
try:
    description = urllib.unquote_plus(params["description"])
except:
    pass
try:
    query = urllib.unquote_plus(params["query"])
except:
    pass

print str(ADDON_PATH) + ': ' + str(VERSION)
print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "IconImage: " + str(iconimage)
#########################################################

if mode == None:
    Main_menu()
elif mode == 3:
    sports_menu()
elif mode == 2:
    leagues_menu()
elif mode == 5:
    get_events(url)
elif mode == 4:
    get_stream(url)
elif mode == 10:
    Open_settings()

elif mode == 100:
    resolve(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
