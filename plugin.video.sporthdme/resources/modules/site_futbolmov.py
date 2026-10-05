# -*- coding: utf-8 -*-
"""
Futbol Libre MOV (futbol-libre.mov) source for plugin.video.sporthdme.

The site shows three lists, exposed here as three sub-sites (SUBSITES), each
with the usual NAME/KEY/UA/list_events()/resolve() contract:

  latin   cdn.strm-api.org/api/v1/latin/matches   Latin American channels
  us      cdn.strm-api.org/api/v1/gsc/matches     US sports
  soccer  cdn.strm-api.org/api/v1/matches         football (kora edges),
          + /api/v1/matche/<id>/en per match for its channels

API bodies are "k1" + reversed, alphabet-substituted base64url of
IV(12) || AES-256-GCM ciphertext || tag(16), static key (see _decode).
Plain JSON is passed through, in case they drop the encryption.

Players:
  https://<edge>.kora-plus.li/frame.php|framelatin.php|framegs.php?ch=...
      -> CONFIG.token = base64url(m3u8). Needs iframe Sec-Fetch headers,
         otherwise it redirects to google.com.
  sportiskes.space/streamlat.html|streamgs.html?key=<mid>-<n>
      -> wrapper that builds the kora framelatin/framegs URL above.
  streame.center/embed/chN.php -> iframe hls.php -> m3u8 in page.
  anything else (tarjetarojita...) -> site_futbollibre's generic resolver.
"""

import re
import json
import time
import uuid
import base64
import random
import struct
from datetime import datetime

import six

from resources.modules import site_futbollibre as _fl

API = 'https://cdn.strm-api.org/api/v1/'
HOME = 'https://futbol-libre.mov/'
# the site's own player pages live here; kora edges check this Referer
PLAYER_REF = 'https://01futbol-libre-mov.sportiskes.space/'
EDGES = ['a11', 'a12', 'a13', 'a14', 'a15', 'a16']
EDGE_DOMAIN = 'kora-plus.li'
# hosts that never play from Europe (fubo18 CDN -> 403) or need JS we don't run
SKIP_HOSTS = ('la18hd.su', 'gsports.lat')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')
IFRAME_HEADERS = {'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate',
                  'Sec-Fetch-Site': 'cross-site'}

_KEY = base64.b64decode('vqW3n/yB1R+GwSPc4kJs2dCkV7kRmXaNy3lQ/3XkHJI=')
_ALPHA = dict(zip('MiljRIn9PX1o63wGBYTtFsKmEkSur-pC_U02cvzAdy5e8ZqLDgJ4OhVN7QbHxfWa',
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))


# ---- AES-256-GCM decrypt (stdlib only) -----------------------------------

def _build_tables():
    sbox = [0] * 256
    p = q = 1
    while True:
        p = (p ^ (p << 1) ^ (0x1b if p & 0x80 else 0)) & 0xff
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xff
        if q & 0x80:
            q ^= 0x09
        x = q
        for s in (1, 2, 3, 4):
            x ^= ((q << s) | (q >> (8 - s))) & 0xff
        sbox[p] = x ^ 0x63
        if p == 1:
            break
    sbox[0] = 0x63
    te = ([], [], [], [])
    for s in sbox:
        s2 = ((s << 1) ^ (0x1b if s & 0x80 else 0)) & 0xff
        s3 = s2 ^ s
        w = (s2 << 24) | (s << 16) | (s << 8) | s3
        for i in range(4):
            te[i].append(((w >> (8 * i)) | (w << (32 - 8 * i))) & 0xffffffff)
    return sbox, te


_SBOX, _TE = _build_tables()


def _expand_key(key):
    rk = list(struct.unpack('>8I', key))
    rcon = 1
    for i in range(8, 60):
        t = rk[i - 1]
        if i % 8 == 0:
            t = ((t << 8) | (t >> 24)) & 0xffffffff
            t = ((_SBOX[t >> 24] << 24) | (_SBOX[(t >> 16) & 255] << 16) |
                 (_SBOX[(t >> 8) & 255] << 8) | _SBOX[t & 255]) ^ (rcon << 24)
            rcon = ((rcon << 1) ^ (0x1b if rcon & 0x80 else 0)) & 0xff
        elif i % 8 == 4:
            t = ((_SBOX[t >> 24] << 24) | (_SBOX[(t >> 16) & 255] << 16) |
                 (_SBOX[(t >> 8) & 255] << 8) | _SBOX[t & 255])
        rk.append(rk[i - 8] ^ t)
    return rk


def _encrypt_block(rk, s0, s1, s2, s3):
    t0, t1, t2, t3 = _TE
    s0 ^= rk[0]
    s1 ^= rk[1]
    s2 ^= rk[2]
    s3 ^= rk[3]
    for r in range(1, 14):
        k = 4 * r
        s0, s1, s2, s3 = (
            t0[s0 >> 24] ^ t1[(s1 >> 16) & 255] ^ t2[(s2 >> 8) & 255] ^ t3[s3 & 255] ^ rk[k],
            t0[s1 >> 24] ^ t1[(s2 >> 16) & 255] ^ t2[(s3 >> 8) & 255] ^ t3[s0 & 255] ^ rk[k + 1],
            t0[s2 >> 24] ^ t1[(s3 >> 16) & 255] ^ t2[(s0 >> 8) & 255] ^ t3[s1 & 255] ^ rk[k + 2],
            t0[s3 >> 24] ^ t1[(s0 >> 16) & 255] ^ t2[(s1 >> 8) & 255] ^ t3[s2 & 255] ^ rk[k + 3])
    S = _SBOX
    return struct.pack('>4I', *[
        ((S[a >> 24] << 24) | (S[(b >> 16) & 255] << 16) |
         (S[(c >> 8) & 255] << 8) | S[d & 255]) ^ rk[56 + i]
        for i, (a, b, c, d) in enumerate(((s0, s1, s2, s3), (s1, s2, s3, s0),
                                           (s2, s3, s0, s1), (s3, s0, s1, s2)))])


def _gcm_decrypt(key, iv, data):
    # ponytail: GCM tag is not verified (CTR part only); a corrupted body
    # just fails json.loads afterwards.
    rk = _expand_key(key)
    i0, i1, i2 = struct.unpack('>3I', iv)
    ct = bytearray(data[:-16])
    out = bytearray(len(ct))
    ctr = 2  # GCM: counter 1 is the tag mask, data starts at 2
    for off in range(0, len(ct), 16):
        ks = bytearray(_encrypt_block(rk, i0, i1, i2, ctr))
        ctr = (ctr + 1) & 0xffffffff
        chunk = ct[off:off + 16]
        for j in range(len(chunk)):
            out[off + j] = chunk[j] ^ ks[j]
    return six.binary_type(out)


def _decode(text):
    text = text.strip()
    if not text.startswith('k1'):
        return json.loads(text)
    s = ''.join(_ALPHA.get(c, c) for c in reversed(text[2:]))
    raw = base64.urlsafe_b64decode(six.ensure_binary(s + '=' * (-len(s) % 4)))
    return json.loads(six.ensure_text(_gcm_decrypt(_KEY, raw[:12], raw[12:])))


# ---- pure parsers --------------------------------------------------------

def _status(start_ms, live, now_ms, duration_min=180):
    if live:
        return 'live'
    if not start_ms or now_ms < start_ms:
        return 'soon'
    return 'done' if now_ms > start_ms + duration_min * 60 * 1000 else 'soon'


def _usable(url):
    return url.startswith('http') and not any(h in url for h in SKIP_HOSTS)


def parse_list(payload, now_ms=None):
    """latin/matches and gsc/matches share one shape."""
    now_ms = now_ms or time.time() * 1000
    out = []
    for m in payload.get('matches', []):
        home = (m.get('home') or {}).get('name')
        away = (m.get('away') or {}).get('name')
        title = m.get('title') or ('%s vs %s' % (home, away) if home and away else '')
        servers = []
        for s in m.get('streams') or []:
            url = s.get('embed_url') or ''
            if _usable(url):
                host = re.sub(r'^www\.', '', url.split('/')[2]).split('.')[0]
                servers.append([u'%s (%s)' % (s.get('name') or s.get('language') or
                                              'Server %d' % (len(servers) + 1), host), url])
        start_ms = int(m.get('timestamp') or 0)
        status = _status(start_ms, m.get('live'), now_ms)
        if not (title and servers) or status == 'done':
            continue
        out.append({'title': title, 'code': '',
                    'league': m.get('league') or m.get('sport_name') or '',
                    'start_ms': start_ms, 'poster': m.get('poster') or '',
                    'status': status, 'servers': servers})
    out.sort(key=lambda e: (e['status'] != 'live', e['start_ms']))
    return out


def _utc_ms(date, hhmm):
    # kora feed times are UTC (Egypt-South Africa 18:00 = 21:00 Cairo)
    try:
        dt = datetime.strptime('%s %s' % (date, hhmm), '%Y-%m-%d %H:%M')
        return int((dt - datetime(1970, 1, 1)).total_seconds() * 1000)
    except Exception:
        return 0


def soccer_servers(match, kt=None):
    edges = match.get('edges') or EDGES
    dom = match.get('edge_domain') or EDGE_DOMAIN
    kt = kt or int(time.time())
    out = []
    for c in match.get('channels') or []:
        name = c.get('server_name') or 'Server %d' % (len(out) + 1)
        if c.get('type') == 'HLS' and c.get('link'):
            out.append([name, c['link']])
        elif c.get('ch') and str(c.get('edge')) != '0':
            out.append([name, 'https://%s.%s/frame.php?ch=%s&p=12&token=%s&kt=%d' % (
                random.choice(edges), dom, c['ch'], uuid.uuid4(), kt)])
    return out


# ---- resolvers -----------------------------------------------------------

def _get(url, referer=None, extra=None):
    import requests
    headers = {'User-Agent': UA}
    if referer:
        headers['Referer'] = referer
    headers.update(extra or {})
    return requests.get(url, headers=headers, timeout=15).text


def _kora_token(html):
    m = re.search(r'token\s*:\s*"([A-Za-z0-9_=-]{20,})"', html)
    if not m:
        return None
    t = m.group(1)
    url = six.ensure_text(base64.urlsafe_b64decode(six.ensure_binary(t + '=' * (-len(t) % 4))),
                          errors='replace')
    return url if url.startswith('http') else None


def _resolve_kora(url):
    """Try the given edge first, then the others on the same domain."""
    m = re.match(r'https://(a\d+)\.([^/]+)(/frame\w*\.php\?.*)$', url)
    edges = [m.group(1)] + [e for e in EDGES if e != m.group(1)] if m else [None]
    for edge in edges:
        u = 'https://%s.%s%s' % (edge, m.group(2), m.group(3)) if m else url
        try:
            m3u8 = _kora_token(_get(u, PLAYER_REF, IFRAME_HEADERS))
        except Exception:
            m3u8 = None
        if m3u8:
            return m3u8, u
    return None


def resolve(url):
    w = re.search(r'sportiskes\.[^/]+/stream\w*\.html\?.*?key=([\w-]+)', url)
    if w:  # wrapper page (streamlat/streamgs/streame...): it names its kora frame
        f = re.search(r'/(frame\w*)\.php', _get(url, PLAYER_REF))
        if not f:
            return None
        url = 'https://%s.%s/%s.php?ch=%s' % (random.choice(EDGES), EDGE_DOMAIN,
                                             f.group(1), w.group(1))
    if re.search(r'//a\d+\.[^/]+/frame\w*\.php', url):
        return _resolve_kora(url)
    if '.m3u8' in url:
        return url
    if 'streame.center' in url:
        html = _get(url, HOME)
        f = re.search(r'<iframe[^>]+src=["\']([^"\']*hls\.php[^"\']*)', html)
        if f:
            page = f.group(1)
            page = 'https:' + page if page.startswith('//') else page
            html = _get(page, url)
        m = re.search(r'(https?:[^"\'\s<>]+\.m3u8[^"\'\s<>]*)', html)
        if m:
            return m.group(1).replace('\\u0026', '&').replace('\\/', '/'), url
        return None
    return _fl.resolve(url)


# ---- the three lists -------------------------------------------------------

class _Sub(object):
    UA = UA
    TAG_LAST = True

    def __init__(self, key, name, desc, lister):
        self.KEY, self.NAME, self.DESC = key, name, desc
        self.list_events = lister

    @staticmethod
    def resolve(url):
        return resolve(url)


def _list(path):
    return parse_list(_decode(_get(API + path, HOME)))


def _list_soccer():
    feed = _decode(_get(API + 'matches', HOME))
    now_ms = time.time() * 1000
    out = []
    # ponytail: one channels request per active match (sequential, ~7/day);
    # thread it if the agenda grows.
    for m in feed.get('matches', []):
        if str(m.get('active')) != '1' or str(m.get('has_channels')) != '1':
            continue
        start_ms = _utc_ms(m.get('date', ''), m.get('time', ''))
        status = _status(start_ms, m.get('status') in (1, 3), now_ms)
        if status == 'done' or m.get('status') == 2:
            continue
        try:
            det = _decode(_get(API + 'matche/%s/en' % m['id'], PLAYER_REF))
            servers = soccer_servers(det.get('match') or {})
        except Exception:
            servers = []
        if not servers:
            continue
        out.append({'title': '%s vs %s' % ((m.get('home') or {}).get('name', ''),
                                           (m.get('away') or {}).get('name', '')),
                    'code': '', 'league': (m.get('league') or {}).get('name', ''),
                    'start_ms': start_ms, 'poster': '', 'status': status,
                    'servers': servers})
    out.sort(key=lambda e: (e['status'] != 'live', e['start_ms']))
    return out


NAME = 'Futbol Libre MOV'
DESC = ('[B]Futbol Libre MOV[/B]\n\n'
        'Menú triple + búsqueda (futbol-libre.mov):\n'
        '- Latino: partidos con canales latinos (ESPN, Fox, TNT, Win...)\n'
        '- USA: deportes de EE. UU. (NFL, NBA, NHL, MLB, UFC...)\n'
        '- Football Live: fútbol en directo (comentario en árabe)\n'
        '- Search: busca por equipo o liga en los tres menús\n\n'
        '[I]Triple menu + search: Latino (Latin American channels), USA '
        '(US sports), Football Live (Arabic commentary) and a Search that '
        'looks up a team or league across all three lists.[/I]')
SUBSITES = [
    _Sub('fmov_latin', 'Latino', 'Partidos con canales latinos (ESPN, Fox, TUDN...).',
         lambda: _list('latin/matches')),
    _Sub('fmov_us', 'USA', 'US sports: NFL, NBA, NHL, MLB, UFC...',
         lambda: _list('gsc/matches')),
    _Sub('fmov_soccer', 'Football Live', 'Live football, Arabic commentary (kora).',
         _list_soccer),
]


# ---- self-check ----------------------------------------------------------

if __name__ == '__main__':
    # AES-256 FIPS-197 C.3 vector
    rk = _expand_key(six.binary_type(bytearray(range(32))))
    blk = _encrypt_block(rk, *struct.unpack('>4I', six.binary_type(bytearray.fromhex(
        '00112233445566778899aabbccddeeff'))))
    assert blk == six.binary_type(bytearray.fromhex('8ea2b7ca516745bfeafc49904b496089')), blk
    import sys
    for f in sys.argv[1:]:  # saved k1 bodies
        d = _decode(open(f).read())
        print(f, len(d.get('matches', [])), 'matches')
    print('OK')
