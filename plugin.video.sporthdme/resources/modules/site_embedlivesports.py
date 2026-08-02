# -*- coding: utf-8 -*-
"""
Embed Live Sports (streamx-hd.com) source for plugin.video.sporthdme.

Kodi-agnostic on purpose: the parse/decode functions take raw text so they run
(and self-test) outside Kodi. Only the fetch helpers touch the network.

Flow:
  streamveri.xyz         -> active official domain (rotates)
  {domain}/eventos.json  -> full agenda (sports -> leagues -> events -> servers)
  {domain}/live1.php?... -> Clappr page with an IP-locked m3u8 obfuscated in a
                            char-array; Kodi must fetch it so the token binds to
                            the user's IP.
"""

import re
import json
import base64
from datetime import datetime, timedelta

from dateutil.parser import parse as _dtparse
from dateutil.tz import gettz

NAME = 'Eventos En Vivo'
KEY = 'emls'
DESC = ('[B]Eventos En Vivo[/B]\n\n'
        'Agenda de deportes en directo: fútbol y más, ordenados por hora, '
        'con varios servidores por partido (Manual y Automática). '
        'Los eventos finalizados se ocultan automáticamente. '
        'La narración de los partidos está en español latinoamericano.\n\n'
        '[I]Live sports agenda: football and more, sorted by time, with '
        'several servers per match (Manual and Auto). Finished events are '
        'hidden automatically. Match commentary is in Latin American '
        'Spanish.[/I]')
VERI_URL = 'https://streamveri.xyz/'
FALLBACK_DOMAIN = 'https://streamx-hd.com'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')


# ---- pure parsers (testable without network) -----------------------------

def parse_active_domain(veri_html):
    """Pick the online 'main' domain from streamveri's embedded DOMAINS array."""
    block = re.search(r'const\s+DOMAINS\s*=\s*(\[.*?\]);', veri_html, re.DOTALL)
    if block:
        # entries look like { type:"main", domain:"x", url:"https://x", status:"online" }
        for entry in re.findall(r'\{[^{}]*\}', block.group(1)):
            typ = re.search(r'type:\s*"([^"]*)"', entry)
            url = re.search(r'url:\s*"([^"]*)"', entry)
            status = re.search(r'status:\s*"([^"]*)"', entry)
            if (url and typ and typ.group(1) == 'main'
                    and (not status or status.group(1) == 'online')):
                return url.group(1).rstrip('/')
    return FALLBACK_DOMAIN


def _start_ms(time_str, timezone):
    """The event's start as a UTC epoch in ms (0 if unparseable).

    eventos.json gives a wall-clock time in an IANA zone; convert to an absolute
    instant so default.py can format it with the addon's shared time_convert()
    (same path the built-in LIVE EVENTS page uses)."""
    try:
        tz = gettz(timezone) or gettz()
        dt = _dtparse(time_str).replace(tzinfo=tz)
        return int(dt.timestamp() * 1000)
    except Exception:
        return 0


def _status(start_ms, duration_min):
    """'live' | 'soon' | 'done' from the absolute start instant + duration."""
    if not start_ms:
        return 'soon'
    now_ms = datetime.now().timestamp() * 1000
    if now_ms < start_ms:
        return 'soon'
    if now_ms <= start_ms + (duration_min or 120) * 60 * 1000:
        return 'live'
    return 'done'


def parse_events(eventos):
    """Flatten eventos.json into a list of normalized event dicts."""
    out = []
    for sport in eventos.get('sports', []):
        sport_name = sport.get('name', '')
        for league in sport.get('leagues', []):
            for ev in league.get('events', []):
                # keep only servers this module can resolve (streamx-hd live1.php);
                # foreign embed hosts would just be dead entries. For each we also
                # offer the site's "Automática" twin (live2.php, same stream id) as
                # a fallback path to the same feed -- it is not listed in the JSON.
                servers = []
                for s in ev.get('servers', []):
                    u = s.get('url') or ''
                    if 'live1.php' not in u:
                        continue
                    nm = s.get('name') or 'Server'
                    servers.append([nm, u])
                    servers.append([nm + ' · Auto', u.replace('live1.php', 'live2.php')])
                if not servers:
                    continue
                start_ms = _start_ms(ev.get('time', ''), ev.get('timezone', 'UTC'))
                status = _status(start_ms, ev.get('duration'))
                if status == 'done':      # hide finished / yesterday's events
                    continue
                out.append({
                    'title': ev.get('title') or '%s vs %s' % (
                        ev.get('homeTeam', ''), ev.get('awayTeam', '')),
                    'code': ev.get('code', ''),
                    'start_ms': start_ms,
                    'sport': sport_name,
                    'league': ev.get('league') or league.get('name', ''),
                    'poster': ev.get('image') or ev.get('homeLogo') or ev.get('awayLogo') or '',
                    'status': status,
                    'servers': servers,
                })
    out.sort(key=lambda e: e['start_ms'])   # chronological, like the LIVE EVENTS page
    return out


def decode_playback(live1_html):
    """Rebuild the IP-locked m3u8 from live1.php's char-array obfuscation.

    The page carries two char-arrays with per-request random var names -- one
    builds playbackURL (the stream), one builds adsPayload -- each with its own
    ``var k=A()+B();`` offset. Tie the array and k to the ``playbackURL`` loop."""
    # array var whose .forEach appends to playbackURL
    fe = re.search(r'(\w+)\.forEach\(\s*\(?\s*\w+\s*\)?\s*=>\s*\{'
                   r'[^{}]*?playbackURL\s*\+=', live1_html)
    if not fe:
        return None
    var = re.escape(fe.group(1))
    pairs_m = re.search(var + r'\s*=\s*(\[\[\d+.*?\]\])\s*;', live1_html, re.DOTALL)
    if not pairs_m:
        return None
    pairs = json.loads(pairs_m.group(1))
    # the ``var k=A()+B();`` immediately preceding this array's forEach
    k = 0
    kexpr = re.search(r'\bk\s*=\s*([^;]+);\s*' + var + r'\.forEach', live1_html)
    if kexpr:
        for fn in re.findall(r'(\w+)\s*\(\)', kexpr.group(1)):
            c = re.search(re.escape(fn) + r'\s*\(\)\s*\{\s*return\s+(\d+)', live1_html)
            if c:
                k += int(c.group(1))
    pairs.sort(key=lambda e: e[0])
    url = ''
    for _, b64 in pairs:
        dec = base64.b64decode(b64 + '=' * (-len(b64) % 4)).decode('utf-8', 'replace')
        url += chr(int(re.sub(r'\D', '', dec)) - k)
    return url or None


# ---- network (Kodi / real use) -------------------------------------------

def _get(url, referer=None):
    import requests
    return requests.get(url, headers={'User-Agent': UA,
                                      'Referer': referer or url}, timeout=15).text


def active_domain():
    try:
        return parse_active_domain(_get(VERI_URL))
    except Exception:
        return FALLBACK_DOMAIN


def list_events():
    domain = active_domain()
    data = json.loads(_get(domain + '/eventos.json', referer=domain + '/'))
    return parse_events(data)


def resolve(server_url):
    """server_url is a full .../live1.php?stream=X ; return the m3u8."""
    return decode_playback(_get(server_url))


# ---- self-check ----------------------------------------------------------

if __name__ == '__main__':
    veri = open('/tmp/veri.html', encoding='utf-8', errors='replace').read()
    dom = parse_active_domain(veri)
    assert dom.startswith('http') and 'streamx' in dom, dom
    print('domain:', dom)

    evs = parse_events(json.load(open('/tmp/eventos.json')))
    assert evs and all(e['servers'] and e['title'] for e in evs), 'bad events'
    assert all(e['start_ms'] > 1_600_000_000_000 for e in evs), 'bad start_ms'
    assert all(e['status'] != 'done' for e in evs), 'finished event leaked'
    assert evs == sorted(evs, key=lambda e: e['start_ms']), 'not chronological'
    print('events:', len(evs), '| first:', evs[0]['status'], evs[0]['start_ms'],
          '| last:', evs[-1]['status'], evs[-1]['start_ms'])

    import glob
    # cover both obfuscation shapes: old single-array (/tmp/live1.html) and the
    # newer two-array (playbackURL + adsPayload) live1 dumps (/tmp/l1_*.html).
    for f in ['/tmp/live1.html'] + glob.glob('/tmp/l1_*.html'):
        m3u8 = decode_playback(open(f, encoding='utf-8', errors='replace').read())
        assert m3u8 and m3u8.startswith('http') and 'm3u8' in m3u8, (f, m3u8)
        print('playback', f.split('/')[-1], '->', m3u8[:55], '...')
    print('OK')
