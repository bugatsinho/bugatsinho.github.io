# -*- coding: utf-8 -*-
from __future__ import print_function
import xbmcvfs
import base64
import re
import sys
import six
from six.moves.urllib.parse import unquote_plus, quote_plus, quote, unquote, parse_qsl, urlencode
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
from dateutil import parser, tz

_url = sys.argv[0]
_handle = int(sys.argv[1])

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

BASEURL = 'https://my.ivesoccer.sx/'  # 'https://sporthd.live/'  #'https://sportl.ivesoccer.sx/'
Live_url = 'https://sporthd.live/'  # 'https://sportl.ivesoccer.sx/'
Alt_url = 'https://liveon.sx/program'  # 'https://1.livesoccer.sx/program'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}


def Main_menu():
    # addDir('[B][COLOR gold]Channels 24/7[/COLOR][/B]', 'https://1.livesoccer.sx/program.php', 14, ICON, FANART, '')
    addDir('[B][COLOR white]LIVE EVENTS[/COLOR][/B]', Live_url, 'events', ICON, FANART, True)
    # addDir('[B][COLOR gold]Alternative VIEW [/COLOR][/B]', '', '', ICON, FANART, '')
    # addDir('[B][COLOR gold]Alternative LIVE EVENTS[/COLOR][/B]', Alt_url, 15, ICON, FANART, '')
    # addDir('[B][COLOR white]SPORTS[/COLOR][/B]', '', 3, ICON, FANART, '')
    # addDir('[B][COLOR white]BEST LEAGUES[/COLOR][/B]', '', 2, ICON, FANART, '')
    addDir('[B][COLOR gold]Settings[/COLOR][/B]', 'set', 'settings', ICON, FANART, False)
    addDir('[B][COLOR gold]Clear Addon Data[/COLOR][/B]', 'clear', 'clear', ICON, FANART, False)
    addDir('[B][COLOR gold]Version: [COLOR lime]{}[/COLOR][/B]'.format(vers), '', 'version', ICON, FANART, False)
    xbmcplugin.setContent(_handle, 'movies')
    xbmcplugin.endOfDirectory(_handle)


def get_events(url):  # 5
    # data = client.request(url)
    import requests
    data = requests.get(url)
    data = data.text
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data).replace('&nbsp', '')

    events = client.parseDOM(data, 'script')
    try:
        events = [i for i in events if '''matchDate''' in i][0]
    except:
        control.infoDialog("[COLOR red]No Match Scheduled.[/COLOR]", NAME, ICON, 5000)
        return
    events = events[:-1].replace('self.__next_f.push(', '').replace('\\', '')

    # matches = re.findall('''null\,(\{"(?:matches|customNotFoundMessage).+?)\]\}\]n''', events, re.DOTALL)[0]
    # pattern = r'("matches"\s*\:\s*\[.+?])}]}]n"'
    pattern = r'"matches"\s*\:\s*(\[.+?])}]]}]n'
    matches = re.findall(pattern, events, re.DOTALL)[0]
    # xbmc.log('EVENTSSS: {}'.format(matches))
    matches = json.loads(matches)

    event_list = []

    if six.PY2:
        now = datetime.now()
        now_time_in_ms = (time.mktime(now.timetuple()) + now.microsecond / 1e6) * 1000
    else:
        now_time_in_ms = datetime.now().timestamp() * 1000
    for match in matches:
        channels = match.get("channels", [])
        # links = match['additionalLinks']
        # links.extend(match['channels'])
        icon = match.get('team1Img', ICON)
        sport = match.get('sport', '')
        lname = match.get('league', None)
        lname = six.ensure_text(lname, encoding='utf-8', errors='replace') if lname else sport
        team1 = match.get('team1', None)
        team1 = six.ensure_text(team1, encoding='utf-8', errors='replace') if team1 else None
        team2 = match.get('team2', None)
        team2 = six.ensure_text(team2, encoding='utf-8', errors='replace') if team2 else None
        event = u"{} vs {}".format(team1, team2) if team1 and team2 else team1

        try:
            compare = match['startTimestamp']
            ftime = time_convert(compare)
        except:
            try:
                matchdt = match['matchDate']
                tvtime = match['livetvtimestr']
                compare = adjust_date_and_convert_to_timestamp_ms(matchdt, tvtime)
                ftime = time_convert(compare)
                # xbmc.log('SHOW FTIME: {}'.format(ftime))
            except:
                compare = int('999999999999')
                ftime = '-'

        duration_in_ms = match['duration'] * 60 * 1000

        is_live = False
        if compare <= now_time_in_ms <= compare + duration_in_ms:
            is_live = True

        m_color = "lime" if is_live else "gold"
        ftime = '[COLOR cyan]{}[/COLOR]'.format(ftime)
        name = u'{0} [COLOR {1}]{2}[/COLOR] - [I]{3}[/I]'.format(ftime, m_color, event, lname)
        event_list.append([name, compare, channels, icon])

        # streams = str(quote(base64.b64encode(six.ensure_binary(str(streams)))))
    events = sorted(event_list, key=lambda x: x[1])
    for event in events:
        streams = str(quote(base64.b64encode(six.ensure_binary(str(event[2])))))
        name = event[0]
        icon = event[3]
        addDir(name, streams, 'get_streams', icon, FANART, isFolder=True)

    xbmcplugin.setContent(_handle, 'videos')
    xbmcplugin.endOfDirectory(_handle)


def get_stream(name, url):  # 4
    data = six.ensure_text(base64.b64decode(unquote(url))).strip('\n')

    import ast
    sstreams = []
    for event in ast.literal_eval(data):
        if not isinstance(event, dict):  # TNT Sports 1
            datos = get_links_for_channel(event)
            # xbmc.log('SHOW DATOS: {}'.format(datos))
            for chan, link, lang in datos:
                chan = '[COLOR gold]{}[/COLOR] - {}'.format(chan, lang)
                sstreams.append((link, chan))

        else:
            link = event.get('links', [])
            lang = event.get('language', '')
            chan = six.ensure_text(event.get('name', ''), encoding='utf-8', errors='replace')
            chan = '[COLOR gold]{}[/COLOR] - {}'.format(chan, lang)
            for url_ in link:
                sstreams.append((url_, chan))

    if len(sstreams) < 1:
        control.infoDialog("[COLOR gold]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                           ICON, 5000)
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
                resolve(name, host)
            else:
                return False
        else:
            link = streams[0][0]
            resolve(name, link)


def resolve(name, url):
    stream_url = ''
    ragnaru = ['liveon.sx/embed', '//em.bedsport', 'cdnz.one/ch', 'cdn1.link/ch', 'cdn2.link/ch', 'onlive.sx',
               'reditsport', 's2watch']
    xbmc.log('RESOLVE-URL: {}'.format(url))
    ua_win = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
    # dialog.notification(AddonTitle, '[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]', icon, 5000)
    if 'webplay' in url or 'livestreames' in url:
        html = six.ensure_text(client.request(url, referer=BASEURL))
        # xbmc.log('HTMLLLLL: {}'.format(html))
        url = client.parseDOM(html, 'div', attrs={'class': 'container'})[0]
        stream_url = client.parseDOM(url, 'iframe', ret='src')[0]
    elif 'acestream' in url:
        url1 = "plugin://program.plexus/?url=" + url + "&mode=1&name=acestream+"
        liz = xbmcgui.ListItem(name)
        liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
        liz.setPath(url)
        xbmc.Player().play(url1, liz, False)
        quit()

    elif '/live.cdnz' in url:
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

            flink += '|Referer={}'.format(quote(stream))  # if not 'azcdn' in flink else ''
        stream_url = flink

    elif '1l1l.to/' in url or 'l1l1.to/' in url:  # https://l1l1.to/ch18
        # '//cdn122.com/embed/2k2kr220ol6yr6i&scrolling=no&frameborder=0&allowfullscreen=true'
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
                # hls:  "https://ad2017.vhls.ru.com/lb/nuevo40/index.m3u8",
                link = re.findall(r'''hls:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
                # ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
                stream_url = link + '|Referer=https://video.netwrk.ru.com/&User-Agent=iPad'.format(referer, ua)
            elif 'class="player"' in r:
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                rr = six.ensure_str(client.request(frame, referer=referer))
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
                    flink += '|Referer={}'.format(quote(frame))
                    stream_url = flink
            elif 'stream2watch' in r:
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                data = six.ensure_str(client.request(frame, referer=referer))
                hlsurl, pk, ea = \
                    re.findall('.*hlsUrl\s*=\s*"(.*?&\w+=)".*?var\s+\w+\s*=\s*"([^"]+).*?>\s*ea\s*=\s*"([^"]+)', data,
                               re.DOTALL)[0]
                link = hlsurl.replace('" + ea + "', ea) + pk
                data_link = six.ensure_str(client.request(link, referer='https://stream2watch.freeucp.com'))
                link2 = re.findall('.*(http.+?$)', data_link)[0]
                stream_url = link2 + '|Referer=https://stream2watch.freeucp.com/&Origin=https://stream2watch.freeucp.com/&User-Agent=iPad'

            else:
                if 'fid=' in r:
                    regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
                    vid, getembed = re.findall(regex, r, re.DOTALL)[0]
                    # vid = re.findall(r'''fid=['"](.+?)['"]''', r, re.DOTALL)[0]
                    getembed = 'https:' + getembed if getembed.startswith('//') else getembed
                    embed = six.ensure_str(client.request(getembed))
                    embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
                    host = '{}=desktop&live={}'.format(embed, str(vid))
                    data = six.ensure_str(client.request(host, referer=referer))
                    try:
                        link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
                    except IndexError:
                        link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]

                    stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/',
                                                                                                                  '/')
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
            flink += '|User-Agent={}&Referer={}&Origin={}'.format(quote(ua), quote('https://ftmstreams.click/'),
                                                                  quote('https://ftmstreams.click'))
        stream_url = flink

    elif 'smycdn' in url:
        html = six.ensure_text(client.request(url))
        # xbmc.log('HTMLSTART: {}'.format(html))
        # https://godzcast.com/embed2.php?player='+ embedded +'&live='+ fid +'" '
        if 'fid=' in html:
            regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
            vid, getembed = re.findall(regex, html, re.DOTALL)[0]
            getembed = 'https:' + getembed if getembed.startswith('//') else getembed
            embed = six.ensure_str(client.request(getembed))
            # xbmc.log('EMBED: {}'.format(embed))
            embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
            host = '{}&live={}'.format(embed, str(vid))
            data = six.ensure_str(client.request(host, referer='https://smycdn.ru/'))
            # xbmc.log('HTMLSTART: {}'.format(data))
            try:
                link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
            except IndexError:
                link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
            stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
            stream_url += '|Referer={}&User-Agent=iPad'.format(host.split('embed')[0])
        else:
            stream = client.parseDOM(html, 'iframe', ret='src')[0]
            html = six.ensure_text(client.request(stream))  # https://candlenorth.net/embed/xdpq3ptcuts1qpp
            xbmc.log('HTML: {}'.format(html))
            tok, srv = re.findall(r'''"player","(.+?)",\{"(.+?)"''', html, re.DOTALL)[0]
            flink = 'https://' + srv + '/hls/' + tok + '/live.m3u8'
            flink += '|Referer={}&User-Agent=iPad'.format(quote('https://candlenorth.net/'))
            stream_url = flink

    elif any(i in url for i in ragnaru):
        hdrs = {'User-Agent': 'iPad'}
        referer = 'https://liveon.sx/' if 'liveon' in url else url
        if 'link/player.' in url:
            url = re.sub('player.php\?id=ch', 'flash', url)
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
                    if 'jwplayer.key' in rr:
                        flink = re.findall(r'''file":\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                    else:
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

    elif '//coolrea' in url:
        '''https://f6hmx3jswd83sq.librarywhispering.com/hls/039beb93983959e1-0e2a3bb76283a966aa758ab00478ae20c590853264d6b277a7808d282b7c0109/live.m3u8'''
        # 039beb93983959e1-0e2a3bb76283a966aa758ab00478ae20c590853264d6b277a7808d282b7c0109
        r = six.ensure_str(client.request(url))
        frame = client.parseDOM(r, 'iframe', ret='src')[0]
        data = six.ensure_str(client.request(frame, referer=url))
        # xbmc.log('DATAAAAA: {}'.format(data))
        player = re.findall(r'''new\s*Player.+?player['"]\,['"](.+?)['"].+?['"](.+?)['"]''', data, re.DOTALL)[0]
        stream_url = 'https://' + player[1] + '/hls/' + player[0] + '/live.m3u8'
        stream_url += '|Referer={0}&Origin={0}&User-Agent={1}'.format(quote('https://librarywhispering.com/'), quote(
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'))

    elif '//istorm' in url or '//zvision':
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
            stream_url += '|Referer={}&User-Agent={}'.format(host.split('embed')[0], quote(ua))
        else:
            # r = six.ensure_str(client.request(url))
            frame = client.parseDOM(r, 'iframe', ret='src')[-1]
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

    # xbmc.log('STREAM: {}'.format(stream_url))
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': ICON, 'thumb': ICON, 'poster': ICON, 'fanart': FANART})
    liz.setProperty("IsPlayable", "true")
    liz.setPath(stream_url)
    # liz.setMimeType('application/vnd.apple.mpegurl')
    # liz.setContentLookup(False)
    # if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) < 19:
    #     liz.setInfo(type="Video", infoLabels={"Title": name})
    #     # liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
    # if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 19 < 21:
    #     liz.setInfo(type="Video", infoLabels={"Title": name})
    #     liz.setProperty('inputstream', 'inputstream.adaptive')
    #     liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
    #     stream_url, headers = stream_url.split('|')
    #     liz.setProperty('inputstream.adaptive.stream_headers', headers)
    # if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 20:
    #     # liz.InfoTagVideo(False)
    #     liz.setProperty('inputstream', 'inputstream.adaptive')
    #     # liz.setProperty('inputstream.adaptive.max_bandwidth', '100000000000')
    #     liz.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
    #     stream_url, headers = stream_url.split('|')
    #     liz.setProperty('inputstream.adaptive.stream_headers', headers)
    # else:
    #     liz.setProperty('inputstreamaddon', None)
    # xbmcplugin.setResolvedUrl(_handle, True, listitem=liz)
    xbmc.Player().play(stream_url, liz, False)


################################################################################
#########################CHANNELS HELPERS#######################################
################################################################################

xbmcvfs.mkdir(control.translatePath(ADDON_DATA))
JSON_FILE_PATH = control.translatePath(ADDON_DATA + 'channels.json')
LAST_UPDATE_FILE = control.translatePath(ADDON_DATA + 'last_update.txt')


def is_time_to_update(hours=6):
    if not xbmcvfs.exists(LAST_UPDATE_FILE):
        f = control.openFile(LAST_UPDATE_FILE, 'w')
        f.write(str(time.time()))
        f.close()
    f = control.openFile(LAST_UPDATE_FILE, 'r')
    content = f.read()
    last_update_timestamp = float(content.strip())
    f.close()

    hours_in_seconds = hours * 60 * 60
    current_time = time.time()

    return (current_time - last_update_timestamp) >= hours_in_seconds


def fetch_and_store_channel_data():
    hdrs = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'}
    try:
        url = BASEURL + '''api/trpc/mutual.getTopTeams,saves.getAllUserSaves,mutual.getFooterData,mutual.getAllChannels,mutual.getWebsiteConfig?batch=1&input={"0":{"json":null,"meta":{"values":["undefined"]}},"1":{"json":null,"meta":{"values":["undefined"]}},"2":{"json":null,"meta":{"values":["undefined"]}},"3":{"json":null,"meta":{"values":["undefined"]}},"4":{"json":null,"meta":{"values":["undefined"]}}}'''
        response = six.ensure_text(client.request(url, headers=hdrs), encoding='utf-8', errors='ignore')
        new_data = json.loads(response)

        new_channels_data = None
        for result in new_data:
            if ("result" in result and "data" in result["result"] and
                    "json" in result["result"]["data"] and "allChannels" in result["result"]["data"]["json"]):
                new_channels_data = result["result"]["data"]["json"]["allChannels"]
                break

        if not new_channels_data:
            return

        if not xbmcvfs.exists(JSON_FILE_PATH):
            existing_data = []
        else:
            file = xbmcvfs.File(JSON_FILE_PATH)
            existing_data = json.load(file)
            file.close()

        existing_data_map = {channel['_id']: channel for channel in existing_data}
        changes_made = False

        for new_channel in new_channels_data:
            channel_id = new_channel['_id']
            if channel_id not in existing_data_map or new_channel['links'] != existing_data_map[channel_id]['links']:
                existing_data_map[channel_id] = new_channel
                changes_made = True

        if changes_made:
            file = xbmcvfs.File(JSON_FILE_PATH, 'w')
            file.write(json.dumps(list(existing_data_map.values())))
            file.close()
            print("Channel links updated")

    except Exception as e:
        print("Error fetching or updating channel data: {}".format(e))


def load_data_from_json():
    f = control.openFile(JSON_FILE_PATH, 'r')
    contents = f.read()
    f.close()
    return json.loads(contents)


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
        else:
            if channel['channelName'].replace(' ', '') == channel_name.replace(' ', ''):
                for link in channel['links']:
                    chan = channel['channelName']
                    lang = channel['language']
                    datos.append((chan, link, lang))
                return datos
    return None


###################################################
###################################################
###################################################
########### Time and Date Helpers #################
###################################################
def fetch_user_timezone():
    try:
        locale_timezone = json.loads(xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}'))

        if locale_timezone['result']['value']:
            local_tzinfo = gettz(locale_timezone['result']['value'])
            if local_tzinfo:
                xbmc.log('SHOW FINAL ΤΙΜΕΖΟΝΕ: {}'.format(local_tzinfo))
                return local_tzinfo
            else:
                xbmc.log("Failed to get tzinfo for timezone: {}".format(locale_timezone['result']['value']))
        else:
            xbmc.log("No timezone value found in Kodi settings")
    except Exception as e:
        xbmc.log("Error fetching timezone from Kodi settings: {}".format(e))

    return gettz()


def convDateUtil(timestring, newfrmt='default', in_zone='UTC'):
    if newfrmt == 'default':
        newfrmt = xbmc.getRegion('time').replace(':%S', '')
    try:
        local_tzinfo = fetch_user_timezone()
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


def time_to_update(hours=6):
    try:
        f = control.openFile(LAST_UPDATE_FILE, 'r')
        content = f.read()
        last_update_timestamp = float(content.strip())
        f.close()
    except:
        return True

    hours_in_seconds = int(hours) * 60 * 60
    current_time = time.time()

    return (current_time - last_update_timestamp) >= hours_in_seconds


def update_last_update_time():
    try:
        f = control.openFile(LAST_UPDATE_FILE, 'w')
        f.write(str(time.time()))
        f.close()
    except:
        print("Error updating last update time")


def adjust_date_and_convert_to_timestamp_ms(matchDate, livetvtimestr):
    date_obj = parser.parse(matchDate[2:])
    hours, minutes = map(int, livetvtimestr.split(":"))
    date_obj = date_obj.replace(hour=hours, minute=minutes)

    date_obj += timedelta(days=1)
    user_timezone = fetch_user_timezone()
    date_obj = date_obj.astimezone(user_timezone)

    if six.PY2:
        timestamp_ms = int((time.mktime(date_obj.timetuple()) + date_obj.microsecond / 1e6) * 1000)
    else:
        timestamp_ms = int(date_obj.timestamp() * 1000)
    return timestamp_ms


##########################################################################################
##########################################################################################


def Open_settings():
    control.openSettings()


def addDir(name, url, mode, iconimage, description, isFolder=True, infoLabels=None):
    url_encoded = quote_plus(url.encode('utf-8'))
    name_encoded = quote_plus(name.encode('utf-8'))
    iconimage_encoded = quote_plus(iconimage.encode('utf-8'))
    description_encoded = quote_plus(description.encode('utf-8'))
    u = sys.argv[0] + "?url=" + url_encoded + "&mode=" + str(
        mode) + "&name=" + name_encoded + "&iconimage=" + iconimage_encoded + "&description=" + description_encoded

    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': FANART})
    if infoLabels:
        liz.setInfo(type="Video", infoLabels=infoLabels)
    if not isFolder:
        if mode == 'settings' or mode == 'version' or mode == 'clear':
            isFolder = False
        else:
            liz.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(_handle, url=u, listitem=liz, isFolder=isFolder)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['mode'] == 'events':
            if time_to_update():
                fetch_and_store_channel_data()
                update_last_update_time()
            else:
                print("Not yet time to check for updates.")
            get_events(params['url'])
        elif params['mode'] == 'get_streams':
            get_stream(params['name'], params['url'])
        elif params['mode'] == 'settings':
            Open_settings()
        elif params['mode'] == 'clear':
            control.deleteFile(LAST_UPDATE_FILE)
            control.infoDialog("[COLOR gold]Files cleared[/COLOR]", NAME,
                               ICON, 5000)
        elif params['mode'] == 'version':
            xbmc.executebuiltin('UpdateAddonRepos')
    else:
        Main_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:])