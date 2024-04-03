# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import base64
import re
import sys
import six
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip
from datetime import datetime, timedelta
import json
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.modules import control, client
import time
from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal
from dateutil import parser, tz


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

BASEURL = 'https://sporthd.me/'#'https://sportl.ivesoccer.sx/'
Live_url = 'https://sporthd.me/' #'https://sportl.ivesoccer.sx/'
Alt_url = 'https://liveon.sx/program'#'https://1.livesoccer.sx/program'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}


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


def time_convert(timestamp):
    timestamp = int(str(timestamp)[:10])
    dt_object = datetime.fromtimestamp(timestamp)
    time_ = dt_object.strftime("%d-%b, %H:%M")
    return time_


def adjust_date_and_convert_to_timestamp_ms(matchDate, livetvtimestr):
    date_obj = parser.parse(matchDate[2:])

    hours, minutes = map(int, livetvtimestr.split(":"))
    date_obj = date_obj.replace(hour=hours, minute=minutes)

    date_obj += timedelta(days=1)

    user_timezone = tz.gettz(xbmc.getRegion('time'))
    date_obj = date_obj.astimezone(user_timezone)

    timestamp_ms = int(date_obj.timestamp() * 1000)

    return timestamp_ms




# def matchdate_to_timestamp_ms(matchdate, livetvtime):
#     matchdate = matchdate[2:-5]
#     time_h, time_m = livetvtime.split(":")
#     matchdate_format = "%Y-%m-%dT%H:%M:%S"
#
#     try:
#         date_event = datetime.strptime(matchdate, matchdate_format)
#     except TypeError:
#         date_event = datetime(*(time.strptime(matchdate, matchdate_format)[0:6]))
#     except ValueError:
#         return None
#     date_event = date_event + timedelta(hours=int(time_h)+6, minutes=int(time_m))
#     return int(date_event.timestamp() * 1000)

##########################################################################################
##########################################################################################

def Main_menu():

    # addDir('[B][COLOR gold]Channels 24/7[/COLOR][/B]', 'https://1.livesoccer.sx/program.php', 14, ICON, FANART, '')
    addDir('[B][COLOR white]LIVE EVENTS[/COLOR][/B]', Live_url, 5, ICON, FANART, '')
    # addDir('[B][COLOR gold]Alternative VIEW [/COLOR][/B]', '', '', ICON, FANART, '')
    addDir('[B][COLOR gold]Alternative LIVE EVENTS[/COLOR][/B]', Alt_url, 15, ICON, FANART, '')
    addDir('[B][COLOR white]SPORTS[/COLOR][/B]', '', 3, ICON, FANART, '')
    addDir('[B][COLOR white]BEST LEAGUES[/COLOR][/B]', '', 2, ICON, FANART, '')
    addDir('[B][COLOR gold]Settings[/COLOR][/B]', '', 10, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]{}[/COLOR][/B]'.format(vers), '', 'BUG', ICON, FANART, '')
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
    addDir('[B][COLOR white]Football[/COLOR][/B]', BASEURL + 'sport/football', 5,
           BASEURL + 'images/football.png', FANART, 'Football')
    addDir('[B][COLOR white]Basketball[/COLOR][/B]', BASEURL + 'sport/basketball', 5,
           BASEURL + 'images/basketball.png', FANART, 'Basketball')
    addDir('[B][COLOR white]MotorSport[/COLOR][/B]', BASEURL + 'sport/motorsport', 5,
           BASEURL + 'images/motorsport.png', FANART, 'MotorSport')
    addDir('[B][COLOR white]Rugby[/COLOR][/B]', BASEURL + 'sport/rugby', 5,
           BASEURL + 'images/rugby.png', FANART, 'Rugby')
    addDir('[B][COLOR white]NFL[/COLOR][/B]', BASEURL + 'sport/american-football', 5,
           BASEURL + 'images/nfl.png', FANART, 'NFL')
    addDir('[B][COLOR white]UFC[/COLOR][/B]', BASEURL + 'sport/ufc', 5,
           BASEURL + 'images/ufc.png', FANART, 'UFC')
    addDir('[B][COLOR white]Hockey[/COLOR][/B]', BASEURL + 'sport/hockey', 5,
           'https://s2watch.ru/images/hockey-puck-solid.svg', FANART, 'Hokey')
    addDir('[B][COLOR white]Volleyball[/COLOR][/B]', BASEURL + 'sport/volleyball', 5,
           BASEURL + 'images/volleyball.png', FANART, 'Volleyball')
    # addDir('[B][COLOR white]Wrestling[/COLOR][/B]', BASEURL + '?type=wresling', 5,
    #        BASEURL + 'images/wresling.png', FANART, 'Wresling')
    # addDir('[B][COLOR white]Handball[/COLOR][/B]', BASEURL + '?type=handball', 5,
    #        BASEURL + 'images/handball.png', FANART, 'Handball')
    # addDir('[B][COLOR white]Darts[/COLOR][/B]', BASEURL + '?type=darts', 5,
    #        BASEURL + 'images/darts.png', FANART, 'Darts')
    # addDir('[B][COLOR white]Tennis[/COLOR][/B]', BASEURL + '?type=tennis', 5,
    #        BASEURL + 'images/tennis.png', FANART, 'Tennis')
    # addDir('[B][COLOR white]Boxing[/COLOR][/B]', BASEURL + '?type=boxing', 5,
    #        BASEURL + 'images/boxing.png', FANART, 'Boxing')
    # addDir('[B][COLOR white]Cricket[/COLOR][/B]', BASEURL + '?type=cricket', 5,
    #        BASEURL + 'images/cricket.png', FANART, 'Cricket')
    # addDir('[B][COLOR white]Baseball[/COLOR][/B]', BASEURL + '?type=baseball', 5,
    #        BASEURL + 'images/baseball.png', FANART, 'Baseball')
    # addDir('[B][COLOR white]Snooker[/COLOR][/B]', BASEURL + '?type=snooker', 5,
    #        BASEURL + 'images/snooker.png', FANART, 'Snooker')
    # addDir('[B][COLOR white]Chess[/COLOR][/B]', BASEURL + '?type=chess', 5,
    #        BASEURL + 'images/chess.png', FANART, 'Chess')



################################################################################
#########################CHANNELS HELPERS#######################################
################################################################################

JSON_FILE_PATH = control.translatePath(ADDON_DATA + 'channels.json')
LAST_UPDATE_FILE = control.translatePath(ADDON_DATA + 'last_update.txt')

if six.PY2:
    os.makedirs(os.path.dirname(JSON_FILE_PATH))
    os.makedirs(os.path.dirname(LAST_UPDATE_FILE))
elif six.PY3:
    os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LAST_UPDATE_FILE), exist_ok=True)
else:
    os.makedirs(os.path.dirname(JSON_FILE_PATH))
    os.makedirs(os.path.dirname(LAST_UPDATE_FILE))


def is_time_to_update(hours=6):
    try:
        with open(LAST_UPDATE_FILE, 'r') as f:
            last_update_timestamp = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return True

    hours_in_seconds = hours * 60 * 60
    current_time = time.time()

    return (current_time - last_update_timestamp) >= hours_in_seconds

def update_last_update_time():
    with open(LAST_UPDATE_FILE, 'w') as f:
        f.write(str(time.time()))


def fetch_and_store_channel_data():
    import requests
    try:
        response = requests.get('''https://sporthd.me/api/trpc/mutual.getTopTeams,saves.getAllUserSaves,mutual.getFooterData,mutual.getAllChannels,mutual.getWebsiteConfig?batch=1&input={"0":{"json":null,"meta":{"values":["undefined"]}},"1":{"json":null,"meta":{"values":["undefined"]}},"2":{"json":null,"meta":{"values":["undefined"]}},"3":{"json":null,"meta":{"values":["undefined"]}},"4":{"json":null,"meta":{"values":["undefined"]}}}''')
        response.raise_for_status()
        new_data = response.json()
        for result in new_data:
            if "result" in result and "data" in result["result"] and "json" in result["result"][
                "data"] and "allChannels" in result["result"]["data"]["json"]:
                new_channels_data = result["result"]["data"]["json"]["allChannels"]
                break
        else:
            print("Channels not found")
            return

        try:
            with open(JSON_FILE_PATH, 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        changes_made = False

        existing_data_map = {channel['_id']: channel for channel in existing_data}

        for new_channel in new_channels_data:
            channel_id = new_channel['_id']
            if channel_id in existing_data_map:
                if new_channel['links'] != existing_data_map[channel_id]['links']:
                    existing_data_map[channel_id]['links'] = new_channel['links']
                    changes_made = True
            else:
                existing_data_map[channel_id] = new_channel
                changes_made = True

        if changes_made:
            with open(JSON_FILE_PATH, 'w') as file:
                updated_data = list(existing_data_map.values())
                json.dump(updated_data, file)
            print("Channel links updated")
        else:
            print("No updates")

    except requests.RequestException as e:
        print("Error fetching data from API: {}".format(e))

def load_data_from_json():
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def get_links_for_channel(channel_name):
    channels_data = load_data_from_json()
    for channel in channels_data:
        datos = []
        if channel['channelName'] == channel_name:
            for link in channel['links']:
                chan = channel['channelName']
                lang = channel['language']
                datos.append((chan, link, lang))
            return datos
    return None
##################################################################################
##################################################################################


def get_events(url):  # 5
    data = client.request(url)
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data).replace('&nbsp', '')

    events = client.parseDOM(data, 'script')
    try:
        events = [i for i in events if '''matchDate''' in i][0]
    except:
        control.infoDialog("[COLOR red]No Match Scheduled.[/COLOR]", NAME,
                           iconimage, 5000)
        return
    events = events[:-1].replace('self.__next_f.push(', '').replace('\\', '')
    matches = re.findall('''null\,(\{"(?:matches|customNotFoundMessage).+?)\]\}\]n''', events, re.DOTALL)[0]
    matches = json.loads(matches)

    event_list = []
    now_time_in_ms = datetime.now().timestamp()*1000
    for match in matches['matches']:
        links = match['additionalLinks']
        links.extend(match['channels'])
        icon = match['team1Img']
        lname = six.ensure_text(match['league'], encoding='utf-8', errors='ignore')
        country = six.ensure_text(match['country'], encoding='utf-8', errors='ignore')
        event = six.ensure_text(match['fullName'], encoding='utf-8', errors='ignore')

        try:
            compare = match['timestampInMs']
            ftime = time_convert(compare)
        except:
            try:
                matchdt = match['matchDate']
                tvtime = match['livetvtimestr']
                compare = adjust_date_and_convert_to_timestamp_ms(matchdt, tvtime)
                ftime = time_convert(compare)
            except:
                compare = int('999999999999')
                ftime = '-'


        duration_in_ms = match['duration']*60*1000

        is_live = False
        if compare <= now_time_in_ms <= compare+duration_in_ms:
            is_live = True

        m_color = "lime" if is_live else "gold"
        ftime = '[COLOR cyan]{}[/COLOR]'.format(ftime)
        name = '{0} [COLOR {1}]{2}[/COLOR] - [I]{3}-{4}[/I]'.format( ftime, m_color, event, lname, country)
        event_list.append((name, compare, links, icon))

        # streams = str(quote(base64.b64encode(six.ensure_binary(str(streams)))))
    events = sorted(event_list, key=lambda x:x[1])
    for event in events:
        streams = str(quote(base64.b64encode(six.ensure_binary(str(event[2])))))
        name = event[0]
        icon = event[3]
        addDir(name, streams, 4, icon, FANART, name)

xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_livetv(url):
    data = client.request(url)
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = client.parseDOM(data, 'table', attrs={'class': 'styled-table'})[0]
    chans = list(zip(client.parseDOM(data, 'button', attrs={'class': 'tvch'}),
                    client.parseDOM(data, 'a', ret='href')))
    for chan, stream in chans:
        # stream = str(quote(base64.b64encode(six.ensure_binary(stream))))
        chan = chan.encode('utf-8') if six.PY2 else chan
        chan = '[COLOR gold][B]{}[/COLOR][/B]'.format(chan)

        addDir(chan, stream, 100, ICON, FANART, name)


xbmcplugin.setContent(int(sys.argv[1]), 'videos')


def get_new_events(url):# 15
    #import requests
    data = six.ensure_text(client.request(url, headers=headers))
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data)
    days = list(zip(client.parseDOM(data, 'button', attrs={'class': 'accordion'}),
                    client.parseDOM(data, 'div', attrs={'class': "panel"})))
    # data = client.parseDOM(str(data), 'div', attrs={'class': "panel"})
    # xbmc.log('@#@DAYSSS: {}'.format(str(days)))
    for day, events in days[1:]:
        dia = client.parseDOM(day, 'span')[-1]
        dia = '[COLOR lime][B]{}[/B][/COLOR]'.format(dia)
        events = six.ensure_text(events, encoding='utf-8', errors='ignore')
        events = list(zip(client.parseDOM(events, 'div', attrs={'class': "left.*?"}),
                          client.parseDOM(events, 'div', attrs={'class': r"d\d+"})))
        #xbmc.log('@#@EVENTS: {}'.format(str(events)))
    # addDir('[COLORcyan]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
        addDir(dia, '', 'BUG', ICON, FANART, name)
        tevents = []
        for event, streams in events:
            if '\n' in event:
                ev = event.split('\n')
                for i in ev:
                    try:
                        time = re.findall(r'(\d{2}:\d{2})', i, re.DOTALL)[0]
                    except IndexError:
                        time = 'N/A'
                    tevents.append((i, streams, time))
            else:
                try:
                    time = re.findall(r'(\d{2}:\d{2})', event, re.DOTALL)[0]
                except IndexError:
                    time = 'N/A'
                tevents.append((event, streams, time))
        #xbmc.log('EVENTSSS: {}'.format(tevents))
        for event, streams, time in sorted(tevents, key=lambda x: x[2]):
            # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
            streams = str(quote(base64.b64encode(six.ensure_binary(streams))))
            cov_time = convDateUtil(time, 'default', 'GMT{}'.format(str(control.setting('timezone'))))
            ftime = '[COLOR cyan]{}[/COLOR]'.format(cov_time)

            event = event.encode('utf-8') if six.PY2 else event
            event = client.replaceHTMLCodes(event)
            event = re.sub('<.+?>', '', event)
            event = re.sub(r'(\d{2}:\d{2})', '', event)
            event = ftime + ' [COLOR gold][B]{}[/COLOR][/B]'.format(event.replace('\t', ''))

            addDir(event, streams, 4, ICON, FANART, name)


xbmcplugin.setContent(int(sys.argv[1]), 'videos')

def get_stream(url):  # 4
    data = six.ensure_text(base64.b64decode(unquote(url))).strip('\n')
    import ast
    sstreams = []
    for event in ast.literal_eval(data):
        if not 'http' in str(event):  #TNT Sports 1
            datos = get_links_for_channel(event)
            for chan, link, lang in datos:
                chan = '[COLOR gold]{}[/COLOR] - {}'.format(chan, lang)
                sstreams.append((link, chan))

        else:
            link = event['link']
            lang = event['lang']
            chan = six.ensure_text(event['name'], encoding='utf-8', errors='ignore')
            chan = '[COLOR gold]{}[/COLOR] - {}'.format(chan, lang)
            sstreams.append((link, chan))

    if len(sstreams) < 1:
        control.infoDialog("[COLOR gold]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                           iconimage, 5000)
        return
    else:
        titles = []
        streams = []

        for i in sstreams:
            title, link = i[1], i[0]
            # if not 'vecdn' in link:
            if not 'https://bedsport' in link and not 'vecdn' in link:
                if str(link) == str(title):
                    title = title
                else:
                    title += ' | {}'.format(link)
                streams.append(link.rstrip())
                titles.append(title)
        if len(streams) > 1:
            dialog = xbmcgui.Dialog()
            ret = dialog.select('[COLOR gold][B]Choose Stream[/B][/COLOR]', titles)
            if ret == -1:
                return
            elif ret > -1:
                host = streams[ret]
                return resolve(host, name)
            else:
                return False
        else:
            link = streams[0][0]
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
    ragnaru = ['liveon.sx/embed', '//em.bedsport', 'cdnz.one/ch', 'cdn1.link/ch', 'cdn2.link/ch', 'onlive.sx',
               'reditsport', 's2watch']
    xbmc.log('RESOLVE-URL: {}'.format(url))
    ua_win = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
    # dialog.notification(AddonTitle, '[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]', icon, 5000)
    if 'webplay' in url or 'livestreames' in url:
        html = six.ensure_text(client.request(url, referer=BASEURL))
        # xbmc.log('HTMLLLLL: {}'.format(html))
        url = client.parseDOM(html,'div', attrs={'class': 'container'})[0]
        url = client.parseDOM(url, 'iframe', ret='src')[0]
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
        else:
            r = r
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

            flink = 'plugin://plugin.video.youtube/play/?video_id={}'.format(str(fid))

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
        stream_url = flink

    elif '1l1l.to/' in url or 'l1l1.to/' in url:#https://l1l1.to/ch18
        #'//cdn122.com/embed/2k2kr220ol6yr6i&scrolling=no&frameborder=0&allowfullscreen=true'
        if 'l1l1.' in url:
            referer = 'https://l1l1.to/'
            r = six.ensure_str(client.request(url, referer=referer))
            stream = client.parseDOM(r, 'iframe', ret='src')[-1]
            stream = 'https:' + stream if stream.startswith('//') else stream
            rr = six.ensure_str(client.request(stream, referer=referer))
            if '<script>eval' in rr:
                rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
                from resources.modules import jsunpack
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("STREAM-UNPACK: {}".format(str(unpack)))
                if '<script>eval' in rr and not '.m3u8?':
                    unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                    rr = jsunpack.unpack(str(unpack) + ')')
                    # xbmc.log("STREAM-UNPACK22: {}".format(str(unpack)))
                else:
                    rr = rr
                if 'player.src({src:' in rr:
                    flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
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
                flink += '|Referer={}'.format(quote(stream))
                stream_url = flink
        else:
            referer = 'https://1l1l.to/'
            r = six.ensure_str(client.request(url))
            if 'video.netwrk.ru' in r:
                ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0'
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                data = six.ensure_str(client.request(frame, referer=referer))
                #hls:  "https://ad2017.vhls.ru.com/lb/nuevo40/index.m3u8",
                link = re.findall(r'''hls:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
                # ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
                stream_url = link + '|Referer=https://video.netwrk.ru.com/&User-Agent=iPad'.format(referer, ua)
            elif 'stream2watch' in r:
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                data = six.ensure_str(client.request(frame, referer=referer))
                hlsurl, pk, ea = re.findall('.*hlsUrl\s*=\s*"(.*?&\w+=)".*?var\s+\w+\s*=\s*"([^"]+).*?>\s*ea\s*=\s*"([^"]+)', data, re.DOTALL)[0]
                link = hlsurl.replace('" + ea + "', ea) + pk
                data_link = six.ensure_str(client.request(link, referer='https://stream2watch.freeucp.com'))
                link2 = re.findall('.*(http.+?$)', data_link)[0]
                stream_url = link2 + '|Referer=https://stream2watch.freeucp.com/&Origin=https://stream2watch.freeucp.com/&User-Agent=iPad'

            else:
                if 'fid=' in r:
                    regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
                    vid, getembed = re.findall(regex, r, re.DOTALL)[0]
                    #vid = re.findall(r'''fid=['"](.+?)['"]''', r, re.DOTALL)[0]
                    getembed = 'https:' + getembed if getembed.startswith('//') else getembed
                    embed = six.ensure_str(client.request(getembed))
                    embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
                    host = '{}=desktop&live={}'.format(embed, str(vid))
                    data = six.ensure_str(client.request(host, referer=referer))
                    try:
                        link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
                    except IndexError:
                        link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]

                    stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
                    stream_url += '|Referer={}/&User-Agent={}'.format(host.split('embed')[0], quote(ua))

    elif 'fastreams' in url:
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        hdr = {'User-Agent': ua}
        first = six.ensure_text(client.request(url, headers=hdr))
        link = client.parseDOM(first, 'iframe', ret='src')[0]
        xbmc.sleep(5)
        hdr.update({'Referer': link})
        html = six.ensure_text(client.request(link))
        frame = client.parseDOM(html, 'iframe', ret='src')[0]
        rr = six.ensure_text(client.request(frame, headers=hdr))
        if 'Clappr.Player' in rr:
            flink = six.ensure_text(re.findall(r'''source\s*:\s*window.atob\(["'](.+?)['"]\)''', str(rr), re.DOTALL)[0])
            # xbmc.log('FLINK: {}'.format(flink))
            if 'aHR' in flink:
                flink = six.ensure_text(base64.b64decode(flink))
                # xbmc.log('FLINK2: {}'.format(flink))
            else:
                flink = flink
            flink += '|User-Agent={}&Referer={}&Origin={}'.format(quote(ua), quote('https://ftmstreams.click/'), quote('https://ftmstreams.click'))
        stream_url = flink

    elif 'smycdn' in url:
        xbmc.log('URL: {}'.format(url))
        html = six.ensure_text(client.request(url))
        #https://godzcast.com/embed2.php?player='+ embedded +'&live='+ fid +'" '
        if 'fid=' in html:
            regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
            vid, getembed = re.findall(regex, html, re.DOTALL)[0]
            getembed = 'https:' + getembed if getembed.startswith('//') else getembed
            embed = six.ensure_str(client.request(getembed))
            embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
            host = '{}=desktop&live={}'.format(embed, str(vid))
            data = six.ensure_str(client.request(host, referer='https://smycdn.ru/'))
            try:
                link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
            except IndexError:
                link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
            stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
            stream_url += '|Referer={}/&User-Agent={}'.format(host.split('embed')[0], quote(ua))
        else:
            stream = client.parseDOM(html, 'iframe', ret='src')[0]
            html = six.ensure_text(client.request(stream))
            tok, srv = re.findall(r'''"player","(.+?)",\{"(.+?)"''', html, re.DOTALL)[0]
            flink = 'https://' + srv + '/hls/' + tok + '/live.m3u8'
            flink += '|Origin=https://nobodywalked.com&Referer=https://nobodywalked.com/'
            stream_url = flink

    elif any(i in url for i in ragnaru):
        hdrs = {'User-Agent': 'iPad'}
        referer = 'https://liveon.sx/' if 'liveon' in url else url
        r = six.ensure_text(client.request(url, headers=hdrs, referer=referer))
        stream = client.parseDOM(r, 'iframe', ret='src')[-1]
        stream = 'https:' + stream if stream.startswith('//') else stream
        rr = six.ensure_str(client.request(stream, headers=hdrs, referer=referer))
        from resources.modules import jsunpack
        if '<script>eval' in rr:
            rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
            # unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
            unpack = client.parseDOM(rr, 'script')
            unpack = [i for i in unpack if 'eval' in i][0]
            # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
            rr = jsunpack.unpack(str(unpack))
            # xbmc.log("STREAM-UNPACK: {}".format(str(rr)))
            if jsunpack.detect(rr) and not '.m3u8?':
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("STREAM-UNPACK22: {}".format(str(rr)))
            # elif 'eval(function' in rr:
            #     xbmc.log("MALAKASSSS")
            #     rr = jsunpack.unpack(str(rr))
            #     xbmc.log("STREAM-UNPACK222: {}".format(str(unpack)))
            else:
                rr = rr
            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]

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
            flink += '|Referer={}'.format(quote(stream))
            stream_url = flink
        else:

            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
            elif 'Clappr.Player' in rr:
                flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]

            elif 'hlsjsConfig' in rr:
                flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]

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
            flink += '|Referer={}'.format(
                quote(stream.split('mono.')[0])) if not 'reddit' in stream else '|Referer={}'.format(
                quote('https://redittsports.com/'))
            flink += '&User-Agent={}'.format(quote(ua))
            stream_url = flink

    elif '//bedsport' in url:
        r = six.ensure_str(client.request(url))
        frame = client.parseDOM(r, 'iframe', ret='src')[0]
        data = six.ensure_str(client.request(frame))
        unpack = re.findall(r'''script>(eval.+?\{\}\))\)''', data, re.DOTALL)[0]

        from resources.modules import jsunpack
        data = six.ensure_text(jsunpack.unpack(str(unpack) + ')'), encoding='utf-8')
    elif '//istorm' in url or '//coolrea' in url or '//zvision':
        referer = 'https://istorm.live/' if 'istorm' in url else 'https://coolrea.link/'
        r = six.ensure_str(client.request(url))
        if 'fid=' in r:
            regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
            vid, getembed = re.findall(regex, r, re.DOTALL)[0]
            getembed = 'https:' + getembed if getembed.startswith('//') else getembed
            embed = six.ensure_str(client.request(getembed))
            embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
            host = '{}=desktop&live={}'.format(embed, str(vid))
            data = six.ensure_str(client.request(host, referer=referer))
            try:
                link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
            except IndexError:
                link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]

            stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
            stream_url += '|Referer={}/&User-Agent={}'.format(host.split('embed')[0], quote(ua))
        else:
            # r = six.ensure_str(client.request(url))
            frame = client.parseDOM(r,'iframe', ret='src')[-1]
            # xbmc.log('FRAME: {}'.format(frame))
            data = six.ensure_str(client.request(frame, referer=url, output=url))
            unpack = re.findall(r'''script>(eval.+?\{\}\))\)''', data, re.DOTALL)[0]

            from resources.modules import jsunpack
            rr = six.ensure_text(jsunpack.unpack(str(unpack) + ')'), encoding='utf-8')
            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
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
            flink += '|Referer={}&User-Agent=iPad'.format(quote('https://candlenorth.net/'))
            stream_url = flink


    else:
        stream_url = url

    liz = xbmcgui.ListItem(name)
    liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty("IsPlayable", "true")
    liz.setPath(str(stream_url))
    if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 17.5:
        liz.setMimeType('application/vnd.apple.mpegurl')
        liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
        # liz.setProperty('inputstream.adaptive.stream_headers', str(headers))
    else:
        liz.setProperty('inputstreamaddon', None)
        liz.setContentLookup(True)
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
    elif mode == 10 or mode == 'BUG' or mode == 4:
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
    if is_time_to_update():
        fetch_and_store_channel_data()
        update_last_update_time()
    else:
        print("Not yet time to check for updates.")
    get_events(url)
elif mode == 4:
    get_stream(url)
elif mode == 10:
    Open_settings()
elif mode == 14:
    get_livetv(url)
elif mode == 15:
    get_new_events(url)

elif mode == 100:
    resolve(url, name)
xbmcplugin.endOfDirectory(int(sys.argv[1]))