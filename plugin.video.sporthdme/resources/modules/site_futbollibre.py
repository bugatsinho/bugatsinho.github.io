# -*- coding: utf-8 -*-
"""
Fútbol Libre (futbollibretv.net.pe) source for plugin.video.sporthdme.

Same NAME/KEY/DESC/list_events()/resolve() contract as the other extra sites,
different structure:

  agenda-data.php        -> Strapi-style {data:[{attributes:{...}}]} agenda
  embed_iframe (?r=b64)  -> decodes to futbollibre.ch/canales.php?stream=X
  canales.php            -> Clappr page with a PLAIN playbackURL = "...m3u8?token="

Times (diary_hour) are America/Lima per the site.
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
        'Agenda de futbol en directo (futbollibretv), ordenada por hora, con '
        'varios canales por evento. Los eventos finalizados se ocultan.\n\n'
        '[I]Live football agenda, sorted by time, several channels per event. '
        'Finished events are hidden. Commentary in Latin American Spanish.[/I]')
BASE = 'https://futbollibretv.net.pe'
AGENDA = BASE + '/agenda-data.php'
IMG = 'https://img.futbollibrehd.com.pe'   # Strapi media host for /uploads/*
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
    """Flatten agenda-data.php into normalized event dicts (finished dropped)."""
    out = []
    for item in payload.get('data', []):
        a = item.get('attributes', {})
        title = ' '.join((a.get('diary_description') or '').split()).strip()
        servers = []
        for emb in ((a.get('embeds') or {}).get('data') or []):
            ea = emb.get('attributes', {})
            url = _decode_embed(ea.get('embed_iframe', ''))
            if url:
                servers.append([ea.get('embed_name') or 'Canal', url])
        if not (title and servers):
            continue
        start_ms = _start_ms(a.get('date_diary', ''), a.get('diary_hour', ''))
        status = _status(start_ms)
        if status == 'done':
            continue
        country_attr = (((a.get('country') or {}).get('data') or {})
                        .get('attributes') or {})
        img_url = ((((country_attr.get('image') or {}).get('data') or {})
                    .get('attributes') or {}).get('url', ''))
        poster = (IMG + img_url) if img_url.startswith('/') else img_url
        out.append({
            'title': title,
            'code': country_attr.get('name', ''),
            'league': '',
            'start_ms': start_ms,
            'poster': poster,        # country / sport icon from the Strapi media host
            'status': status,
            'servers': servers,
        })
    out.sort(key=lambda e: e['start_ms'])
    return out


def extract_m3u8(canales_html):
    """canales.php exposes a plain: var playbackURL = "https://....m3u8?token=..."."""
    m = re.search(r'playbackURL\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']', canales_html)
    return m.group(1) if m else None


# ---- network -------------------------------------------------------------

def _get(url, referer=None):
    import requests
    return requests.get(url, headers={'User-Agent': UA,
                                      'Referer': referer or BASE + '/'}, timeout=15).text


def list_events():
    return parse_events(json.loads(_get(AGENDA, referer=BASE + '/agenda')))


def resolve(server_url):
    """server_url is the decoded canales.php URL; return the m3u8."""
    return extract_m3u8(_get(server_url, referer=BASE + '/'))


# ---- self-check ----------------------------------------------------------

if __name__ == '__main__':
    d = _decode_embed('/embed/eventos.html?r=' + base64.b64encode(
        b'https://futbollibre.ch/canales.php?stream=sportv').decode())
    assert d == 'https://futbollibre.ch/canales.php?stream=sportv', d

    evs = parse_events(json.load(open('/tmp/fl_data.json')))
    assert evs and all(e['servers'] and e['title'] for e in evs), 'bad events'
    assert all(e['start_ms'] > 1_600_000_000_000 for e in evs), 'bad start_ms'
    assert evs == sorted(evs, key=lambda e: e['start_ms']), 'not chronological'
    print('events:', len(evs), '| sample:', evs[0]['title'], '|', evs[0]['code'],
          '|', evs[0]['status'], '|', len(evs[0]['servers']), 'servers')

    m3u8 = extract_m3u8(open('/tmp/canales.html', encoding='utf-8', errors='replace').read())
    assert m3u8 and m3u8.startswith('http') and 'm3u8' in m3u8, m3u8
    print('playback:', m3u8[:70], '...')
    print('OK')
