# -*- coding: utf-8 -*-
import base64
import re
import sys
import six
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip
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

BASEURL = 'http://www.sporthd.live/'
Live_url = 'http://www.sporthd.live/index.php?'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal

# reload(sys)
# sys.setdefaultencoding("utf-8")

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
           BASEURL + 'index.php?champ=uefa-champions-league', 5,
           BASEURL + 'flags/uefa-champions-league.png', FANART, 'Uefa Champions League')
    addDir('[B][COLOR white]Uefa Europa League[/COLOR][/B]', BASEURL + 'index.php?champ=uefa-europa-league',
           5, BASEURL + 'flags/uefa-europa-league.png', FANART, 'Uefa Europa League')
    addDir('[B][COLOR white]Premier League[/COLOR][/B]', BASEURL + 'index.php?champ=premier-league', 5,
           BASEURL + 'flags/premier-league.png', FANART, 'Premier League')
    addDir('[B][COLOR white]Bundesliga[/COLOR][/B]', BASEURL + 'index.php?champ=bundesliga', 5,
           BASEURL + 'flags/bundesliga.png', FANART, 'Bundesliga')
    addDir('[B][COLOR white]Laliga[/COLOR][/B]', BASEURL + 'index.php?champ=laliga', 5,
           BASEURL + 'flags/spanish-primera-division.png', FANART, 'Laliga')
    addDir('[B][COLOR white]Serie A[/COLOR][/B]', BASEURL + 'index.php?champ=serie-a', 5,
           BASEURL + 'flags/serie-a.png', FANART, 'Serie a')
    addDir('[B][COLOR white]France Ligue 1[/COLOR][/B]', BASEURL + 'index.php?champ=france-ligue-1', 5,
           BASEURL + 'flags/france-ligue-1.png', FANART, 'France ligue 1')
    addDir('[B][COLOR white]Eredivisie[/COLOR][/B]', BASEURL + 'index.php?champ=eredivisie', 5,
           BASEURL + 'flags/eredivisie.png', FANART, 'Eredivisie')
    addDir('[B][COLOR white]Australian A League[/COLOR][/B]',
           BASEURL + 'index.php?champ=australian-a-league', 5,
           BASEURL + 'flags/australian-a-league.png', FANART, 'Australian a league')
    addDir('[B][COLOR white]MLS[/COLOR][/B]', BASEURL + 'index.php?champ=mls', 5,
           BASEURL + 'flags/mls.png', FANART, 'Mls')
    addDir('[B][COLOR white]Rugby Top 14[/COLOR][/B]', BASEURL + 'index.php?champ=rugby-top-14', 5,
           BASEURL + 'flags/rugby-top-14.png', FANART, 'Rugby top 14')
    addDir('[B][COLOR white]Greece Super League[/COLOR][/B]',
           BASEURL + 'index.php?champ=greece-super-league', 5,
           BASEURL + 'flags/greece-super-league.png', FANART, 'Greece super league')
    addDir('[B][COLOR white]Argentina Superliga[/COLOR][/B]',
           BASEURL + 'index.php?champ=argentina-superliga', 5,
           BASEURL + 'flags/argentina-superliga.png', FANART, 'Argentina superliga')
    addDir('[B][COLOR white]Portuguese Primeira Liga[/COLOR][/B]',
           BASEURL + 'index.php?champ=portuguese-primeira-liga', 5,
           BASEURL + 'flags/portuguese-primeira-liga.png', FANART, 'Portuguese primeira liga')
    addDir('[B][COLOR white]Primera Division Apertura[/COLOR][/B]',
           BASEURL + 'index.php?champ=primera-division-apertura', 5,
           BASEURL + 'flags/primera-division-apertura.png', FANART, 'Primera division apertura')
    addDir('[B][COLOR white]Bundesliga 2[/COLOR][/B]', BASEURL + 'index.php?champ=bundesliga-2', 5,
           BASEURL + 'flags/bundesliga-2.png', FANART, 'Bundesliga 2')
    addDir('[B][COLOR white]Greece Super League 2[/COLOR][/B]',
           BASEURL + 'index.php?champ=greece-super-league-2', 5,
           BASEURL + 'flags/greece-super-league-2.png', FANART, 'Greece super league 2')
    addDir('[B][COLOR white]Belarus Vysheyshaya Liga[/COLOR][/B]',
           BASEURL + 'index.php?champ=belarus-vysheyshaya-liga', 5,
           BASEURL + 'flags/belarus-vysheyshaya-liga.png', FANART, 'Belarus vysheyshaya liga')


def sports_menu():
    addDir('[B][COLOR white]Football[/COLOR][/B]', BASEURL + '?type=football', 5,
           BASEURL + 'images/football.png', FANART, 'Football')
    addDir('[B][COLOR white]Basketball[/COLOR][/B]', BASEURL + '?type=basketball', 5,
           BASEURL + 'images/basketball.png', FANART, 'Basketball')
    addDir('[B][COLOR white]MotorSport[/COLOR][/B]', BASEURL + '?type=motorsport', 5,
           BASEURL + 'images/motorsport.png', FANART, 'MotorSport')
    addDir('[B][COLOR white]Handball[/COLOR][/B]', BASEURL + '?type=handball', 5,
           BASEURL + 'images/handball.png', FANART, 'Handball')
    addDir('[B][COLOR white]Rugby[/COLOR][/B]', BASEURL + '?type=rugby', 5,
           BASEURL + 'images/rugby.png', FANART, 'Rugby')
    addDir('[B][COLOR white]NFL[/COLOR][/B]', BASEURL + '?type=nfl', 5,
           BASEURL + 'images/nfl.png', FANART, 'NFL')
    addDir('[B][COLOR white]UFC[/COLOR][/B]', BASEURL + '?type=ufc', 5,
           BASEURL + 'images/ufc.png', FANART, 'UFC')
    addDir('[B][COLOR white]Wrestling[/COLOR][/B]', BASEURL + '?type=wresling', 5,
           BASEURL + 'images/wresling.png', FANART, 'Wresling')
    addDir('[B][COLOR white]Hockey[/COLOR][/B]', BASEURL + '?type=hokey', 5,
           BASEURL + 'images/hockey.png', FANART, 'Hokey')
    addDir('[B][COLOR white]Volleyball[/COLOR][/B]', BASEURL + '?type=volleyball', 5,
           BASEURL + 'images/volleyball.png', FANART, 'Volleyball')
    addDir('[B][COLOR white]Darts[/COLOR][/B]', BASEURL + '?type=darts', 5,
           BASEURL + 'images/darts.png', FANART, 'Darts')
    addDir('[B][COLOR white]Tennis[/COLOR][/B]', BASEURL + '?type=tennis', 5,
           BASEURL + 'images/tennis.png', FANART, 'Tennis')
    addDir('[B][COLOR white]Boxing[/COLOR][/B]', BASEURL + '?type=boxing', 5,
           BASEURL + 'images/boxing.png', FANART, 'Boxing')
    addDir('[B][COLOR white]Cricket[/COLOR][/B]', BASEURL + '?type=cricket', 5,
           BASEURL + 'images/cricket.png', FANART, 'Cricket')
    addDir('[B][COLOR white]Baseball[/COLOR][/B]', BASEURL + '?type=baseball', 5,
           BASEURL + 'images/baseball.png', FANART, 'Baseball')
    addDir('[B][COLOR white]Snooker[/COLOR][/B]', BASEURL + '?type=snooker', 5,
           BASEURL + 'images/snooker.png', FANART, 'Snooker')
    addDir('[B][COLOR white]Chess[/COLOR][/B]', BASEURL + '?type=chess', 5,
           BASEURL + 'images/chess.png', FANART, 'Chess')


def get_events(url):  # 5
    data = client.request(url)
    # xbmc.log('@#@EDATAAA: {}'.format(data), xbmc.LOGNOTICE)
    events = list(zip(client.parseDOM(str(data), 'li', attrs={'class': "item itemhov"}),
                      re.findall(r'<i class="material-icons">(.+?)</a> </li>', str(data), re.DOTALL)))
    # addDir('[COLORcyan]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
    for event, streams in events:
        # xbmc.log('@#@EVENTTTTT:%s' % event, xbmc.LOGNOTICE)
        watch = '[COLORlime]*[/COLOR]' if '>Live<' in event else '[COLORred]*[/COLOR]'
        try:
            teams = client.parseDOM(event, 'td')
            # xbmc.log('@#@TEAMSSSS:%s' % str(teams), xbmc.LOGNOTICE)
            home, away = re.sub(r'\s*(<img.+?>)\s*', '', teams[0]), re.sub(r'\s*(<img.+?>)\s*', '', teams[2])
            if six.PY2:
                home = home.strip().encode('utf-8')
                away = away.strip().encode('utf-8')
            teams = '[B]{0} vs {1}[/B]'.format(home, away)
        except IndexError:
            teams = client.parseDOM(event, 'center')[0]
            teams = re.sub(r'<.+?>|\s{2}', '', teams)
            teams = teams.encode('utf-8') if six.PY2 else teams
            teams = '[B]{}[/B]'.format(teams)
        # xbmc.log('@#@TEAM-FINAL:%s' % str(teams), xbmc.LOGNOTICE)
        lname = client.parseDOM(event, 'a')[1]
        lname = re.sub(r'<.+?>', '', lname)
        time = client.parseDOM(event, 'span', attrs={'class': 'gmt_m_time'})[0]
        time = time.split('GMT')[0].strip()
        cov_time = convDateUtil(time, 'default', 'GMT{}'.format(str(control.setting('timezone'))))
        # xbmc.log('@#@COVTIMEEE:%s' % str(cov_time), xbmc.LOGNOTICE)
        ftime = '[COLORgold][I]{}[/COLOR][/I]'.format(cov_time)
        name = '{0}{1} {2} - [I]{3}[/I]'.format(watch, ftime, teams, lname)

        # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
        streams = str(quote(base64.b64encode(six.ensure_binary(streams))))

        icon = client.parseDOM(event, 'img', ret='src')[0]
        icon = urljoin(BASEURL, icon)

        addDir(name, streams, 4, icon, FANART, name)


xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_stream(url):  # 4
    data = base64.b64decode(unquote(url))
    # xbmc.log('@#@DATAAAA:%s' % data, xbmc.LOGINFO)
    if b'info_outline' in data:
        control.infoDialog("[COLOR gold]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                           iconimage, 5000)
        return
    else:
        links = list(zip(client.parseDOM(str(data), 'a', ret='href'), client.parseDOM(str(data), 'a')))
        # xbmc.log('@#@STREAMMMMMSSSSSS:%s' % links, xbmc.LOGINFO)
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
                return resolve(host, name)
            else:
                return
        else:
            link = links[0][0]
            return resolve(link, name)


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


def resolve(url, name):
    # xbmc.log('RESOLVE-URL: %s' % url, xbmc.LOGNOTICE)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    # dialog.notification(AddonTitle, '[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]', icon, 5000)
    if 'acestream' in url:
        url1 = "plugin://program.plexus/?url=" + url + "&mode=1&name=acestream+"
        liz = xbmcgui.ListItem(name)
        liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
        liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage,
                    'fanart': fanart})
        liz.setPath(url)
        xbmc.Player().play(url1, liz, False)
        quit()
    if '/live.cdnz' in url:
        r = six.ensure_str(client.request(url, referer=BASEURL)).replace('\t', '')
        # xbmc.log("[{}] - HTML: {}".format(ADDON.getAddonInfo('id'), str(r)))
        from resources.modules import jsunpack
        if 'script>eval' in r:
            unpack = re.findall(r'''<script>(eval.+?\{\}\)\))''', r, re.DOTALL)[0]
            r = jsunpack.unpack(unpack.strip())
            # xbmc.log('RESOLVE-UNPACK: %s' % str(r), xbmc.LOGNOTICE)
        else:
            r = r
        # xbmc.log("[{}] - HTML: {}".format(ADDON.getAddonInfo('id'), str(r)))
        if 'hfstream.js' in r:
            regex = '''<script type='text/javascript'> width=(.+?), height=(.+?), channel='(.+?)', g='(.+?)';</script>'''
            wid, heig, chan, ggg = re.findall(regex, r, re.DOTALL)[0]
            stream = 'https://www.playerfs.com/membedplayer/' + chan + '/' + ggg + '/' + wid + '/' + heig + ''
        else:
            if 'cbox.ws/box' in r:
                try:
                    stream = client.parseDOM(r, 'iframe', ret='src', attrs={'id': 'thatframe'})[0]
                except IndexError:
                    streams = client.parseDOM(r, 'iframe', ret='src')
                    stream = [i for i in streams if not 'adca.' in i][0]
                    # xbmc.log("[{}] - STREAM: {}".format(ADDON.getAddonInfo('id'), str(stream)))
            else:
                stream = client.parseDOM(r, 'iframe', ret='src')[-1]
                # xbmc.log("[{}] - STREAM-ELSE: {}".format(ADDON.getAddonInfo('id'), str(stream)))
        # xbmc.log("[{}] - STREAM: {}".format(ADDON.getAddonInfo('id'), str(stream)))
        rr = client.request(stream, referer=url)
        rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
        if 'eval' in rr:
            unpack = re.findall(r'''script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0]
            # unpack = client.parseDOM(rr, 'script')
            # xbmc.log('UNPACK: %s' % str(unpack))
            # unpack = [i.rstrip() for i in unpack if 'eval' in i][0]
            rr = six.ensure_text(jsunpack.unpack(str(unpack) + ')'), encoding='utf-8')
        else:
            r = rr
        if 'youtube' in rr:
            try:
                flink = client.parseDOM(r, 'iframe', ret='src')[0]
                fid = flink.split('/')[-1]
            except IndexError:
                fid = re.findall(r'''/watch\?v=(.+?)['"]''', r, re.DOTALL)[0]
            # xbmc.log('@#@STREAMMMMM111: %s' % fid, xbmc.LOGNOTICE)

            flink = 'plugin://plugin.video.youtube/play/?video_id={}'.format(str(fid))
            # xbmc.log('@#@STREAMMMMM111: %s' % flink, xbmc.LOGNOTICE)

        else:
            if '<script>eval' in rr and not '.m3u8?':
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(r)))
            # else:
            #     xbmc.log("[{}] - Error unpacking".format(ADDON.getAddonInfo('id')))
            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
                # xbmc.log('@#@STREAMMMMM: %s' % flink, xbmc.LOGNOTICE)
            elif 'hlsjsConfig' in rr:
                flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
            elif 'new Clappr' in rr:
                flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]
            elif 'player.setSrc' in rr:
                flink = re.findall(r'''player.setSrc\(["'](.+?)['"]\)''', rr, re.DOTALL)[0]

            else:
                try:
                    flink = re.findall(r'''source:\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                except IndexError:
                    ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', rr, re.DOTALL)[0]
                    ea = six.ensure_text(client.request(ea)).split('=')[1]
                    flink = re.findall('''videoplayer.src = "(.+?)";''', ea, re.DOTALL)[0]
                    flink = flink.replace('" + ea + "', ea)

            flink += '|Referer={}'.format(quote(stream)) #if not 'azcdn' in flink else ''
        # xbmc.log('@#@STREAMMMMM111: %s' % flink)
        stream_url = flink

    else:
        stream_url = url
    liz = xbmcgui.ListItem(name)
    liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty("IsPlayable", "true")
    liz.setPath(str(stream_url))
    # if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 17.5:
    #     liz.setMimeType('application/vnd.apple.mpegurl')
    #     liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
    #     liz.setProperty('inputstream.adaptive.stream_headers', str(headers))
    # else:
    #     liz.setProperty('inputstreamaddon', None)
    #     liz.setContentLookup(True)
    xbmc.Player().play(stream_url, liz, False)
    quit()
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)


def Open_settings():
    control.openSettings()


def addDir(name, url, mode, iconimage, fanart, description):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(
        name) + "&iconimage=" + quote_plus(iconimage) + "&description=" + quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
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

print(str(ADDON_PATH) + ': ' + str(VERSION))
print("Mode: " + str(mode))
print("URL: " + str(url))
print("Name: " + str(name))
print("IconImage: " + str(iconimage))
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
    resolve(url, name)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
