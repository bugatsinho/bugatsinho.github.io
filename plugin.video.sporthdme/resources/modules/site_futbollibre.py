# -*- coding: utf-8 -*-
"""
Fútbol Libre (futbollibretv.space) source for plugin.video.sporthdme.

Same NAME/KEY/DESC/list_events()/resolve() contract as the other extra sites.
Structure (Astro-based):

  /api/agenda            -> {events:[{id,title,time,sport,embeds:[{name,iframe}]}]}
  embed iframe           -> base64 or direct URL to player page
  player page            -> Clappr with playbackURL = "...m3u8?token="
"""

import re
import json
import base64
from datetime import datetime

from dateutil.parser import parse as _dtparse
from dateutil.tz import gettz

NAME = 'Futbol Libre'
KEY = 'fllibre'
DESC = ('[B]Futbol Libre[/B]\n\n'
        'Agenda de futbol en directo (futbollibretv.space), ordenada por hora, con '
        'varios canales por evento. Los eventos finalizados se ocultan.\n\n'
        '[I]Live football agenda, sorted by time, several channels per event. '
        'Finished events are hidden. Commentary in Latin American Spanish.[/I]')
BASE = 'https://futbollibretv.space'
AGENDA = BASE + '/api/agenda'
TZ = 'America/Lima'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')


# ---- pure parsers (testable without network) -----------------------------

def _decode_embed(embed_iframe):
    """embed_iframe is /embed/eventos.html?r=<base64> -> the real player URL."""
    m = re.search(r'[?&]r=([A-Za-z0-9+/=_-]+)', embed_iframe or '')
    if not m:
        return None
    b = m.group(1).replace('-', '+').replace('_', '/')
    try:
        url = base64.b64decode(b + '=' * (-len(b) % 4)).decode('utf-8', 'replace')
        return url if url.startswith('http') else None
    except Exception:
        return None


def _start_ms(date_diary, diary_hour):
    try:
        dt = _dtparse('%s %s' % (date_diary, diary_hour)).replace(tzinfo=gettz(TZ) or gettz())
        return int(dt.timestamp() * 1000)
    except Exception:
        return 0


def _start_ms_from_time(time_str):
    """Parse 'HH:MM' into today's start_ms in Lima timezone."""
    if not time_str:
        return 0
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        dt = _dtparse('%s %s' % (today, time_str)).replace(tzinfo=gettz(TZ) or gettz())
        return int(dt.timestamp() * 1000)
    except Exception:
        return 0


def _status(start_ms, duration_min=120):
    if not start_ms:
        return 'soon'
    now_ms = datetime.now().timestamp() * 1000
    if now_ms < start_ms:
        return 'soon'
    if now_ms <= start_ms + duration_min * 60 * 1000:
        return 'live'
    return 'done'


def parse_events(payload):
    """Parse /api/agenda into normalized event dicts (finished dropped)."""
    out = []
    for item in payload.get('events', []):
        title = (item.get('title') or '').strip()
        servers = []
        for emb in (item.get('embeds') or []):
            url = _decode_embed(emb.get('iframe', '')) or emb.get('iframe', '')
            if url and url.startswith('http'):
                servers.append([emb.get('name') or 'Canal', url])
        if not (title and servers):
            continue
        # Parse time "HH:MM" into start_ms
        time_str = item.get('time', '')
        start_ms = _start_ms_from_time(time_str)
        status = _status(start_ms)
        if status == 'done':
            continue
        out.append({
            'title': title,
            'code': item.get('sport', ''),
            'league': '',
            'start_ms': start_ms,
            'poster': item.get('flag', ''),
            'status': status,
            'servers': servers,
        })
    out.sort(key=lambda e: e['start_ms'])
    return out


def extract_m3u8(html):
    """Extract m3u8 URL from Clappr player page."""
    # Clappr may use playbackURL or other patterns
    patterns = [
        r'playbackURL\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        r'["\']?source["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
    ]
    for pattern in patterns:
        m = re.search(pattern, html)
        if m:
            return m.group(1)
    return None


# ---- network -------------------------------------------------------------

def _get(url, referer=None):
    import requests
    return requests.get(url, headers={'User-Agent': UA,
                                      'Referer': referer or BASE + '/'}, timeout=15).text


def list_events():
    return parse_events(json.loads(_get(AGENDA, referer=BASE + '/agenda')))


def resolve(server_url):
    """server_url is iframe URL (base64 or plaintext); return the m3u8."""
    # Decode if base64
    url = _decode_embed(server_url) or server_url
    if not url.startswith('http'):
        return None
    return extract_m3u8(_get(url, referer=BASE + '/'))


# ---- self-check ----------------------------------------------------------

if __name__ == '__main__':
    d = _decode_embed('/embed/eventos.html?r=' + base64.b64encode(
        b'https://futbollibre.ch/canales.php?stream=sportv').decode())
    assert d == 'https://futbollibre.ch/canales.php?stream=sportv', d

    evs = parse_events(json.load(open('/tmp/fl_data.json')))
    assert evs and all(e['servers'] and e['title'] for e in evs), 'bad events'
    assert all(e['start_ms'] > 1600000000000 for e in evs), 'bad start_ms'
    assert evs == sorted(evs, key=lambda e: e['start_ms']), 'not chronological'
    print('events:', len(evs), '| sample:', evs[0]['title'], '|', evs[0]['code'],
          '|', evs[0]['status'], '|', len(evs[0]['servers']), 'servers')

    m3u8 = extract_m3u8(open('/tmp/canales.html', encoding='utf-8', errors='replace').read())
    assert m3u8 and m3u8.startswith('http') and 'm3u8' in m3u8, m3u8
    print('playback:', m3u8[:70], '...')
    print('OK')
