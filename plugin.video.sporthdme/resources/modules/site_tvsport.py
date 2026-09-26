# -*- coding: utf-8 -*-
"""
TVSport Guide (tvsport.guide) source for plugin.video.sporthdme.

Same NAME/KEY/DESC/list_events()/resolve() contract as the other extra sites.

  /schedule.txt                          -> plain-text agenda (see parse_schedule)
  https://watchfa.st/embed.php?code=<h>  -> player page (embed host of the
                                            nexa/vertex "PP" player family)
  <embed url>&ppcfg=1&_=<ms>             -> JSON {"src": <hls.hockey.do m3u8>, ...}

The embed host answers "Domain not allowed" (403) to a foreign Referer such as
tvsport.guide, so the embed page is fetched with no Referer. The signed m3u8
needs Referer/Origin = https://watchfa.st (site_play derives that from the
embed URL this module returns alongside the m3u8).
"""

import re
import json
import time
from datetime import datetime

from dateutil.parser import parse as _dtparse
from dateutil.tz import gettz, tzutc

NAME = 'TVSport Guide'
KEY = 'tvsport'
DESC = ('[B]TVSport Guide[/B]\n\n'
        'Live sports agenda (tvsport.guide), sorted by time, with several '
        'channels per event. Finished events are hidden. Times shown in your '
        'local timezone.')
TAG_LAST = True  # menu label: "time title [league]" instead of "[league] time title"
BASE = 'https://tvsport.guide'
SCHEDULE = BASE + '/schedule.txt'
# schedule.txt carries bare HH:MM with no zone; the site is Romanian and its
# kick-off times match Europe/Bucharest (e.g. UEFA 21:45 = 20:45 CEST).
TZ = 'Europe/Bucharest'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

_EPOCH = datetime(1970, 1, 1, tzinfo=tzutc())


# ---- pure parsers (testable without network) -----------------------------

def _to_ms(dt):
    return int((dt - _EPOCH).total_seconds() * 1000)


def _status(start_ms, now_ms, duration_min=150):
    if now_ms < start_ms:
        return 'soon'
    if now_ms <= start_ms + duration_min * 60 * 1000:
        return 'live'
    return 'done'


def _day_date(label, today):
    """'Friday 25 September' -> a date; the year is not in the file."""
    try:
        d = _dtparse(label + ' %d' % today.year, dayfirst=True).date()
    except Exception:
        return None
    # agenda only spans a few days: around New Year pick the nearer year
    if (today - d).days > 180:
        d = d.replace(year=d.year + 1)
    elif (d - today).days > 180:
        d = d.replace(year=d.year - 1)
    return d


def parse_schedule(text, now=None):
    """Parse schedule.txt into normalized event dicts (finished dropped).

    File layout:  '-Friday 25 September-' day header, then per channel:
        https://watchfa.st/embed.php?code=<hex> [<id>]
        20:00 [League] Sport: Home vs Away [Channel Name]
    The same match repeats once per channel -> merged into one event with
    several servers.
    """
    tz = gettz(TZ) or tzutc()
    now = now or datetime.now(tz)
    now_ms = _to_ms(now)
    today = now.astimezone(tz).date()
    day = None
    url = None
    events = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or re.match(r'^[-=]{10,}$', line):
            continue
        if re.match(r'^-[^-].*-$', line):
            day = _day_date(line.strip('-').strip(), today)
            continue
        m = re.match(r'^(https?://\S+?)(?:\s+\[[^\]]*\])?$', line)
        if m:
            url = m.group(1)
            continue
        m = re.match(r'^(\d{1,2}):(\d{2})\s+(.+)$', line)
        if not (m and url and day):
            continue
        rest = m.group(3)
        chan = re.search(r'\s*\[([^\]]+)\]\s*$', rest)
        channel = chan.group(1) if chan else 'Stream'
        rest = rest[:chan.start()] if chan else rest
        lg = re.match(r'^\[([^\]]+)\]\s*(.*)$', rest)
        league, title = (lg.group(1), lg.group(2)) if lg else ('', rest)
        dt = datetime(day.year, day.month, day.day, int(m.group(1)), int(m.group(2)),
                      tzinfo=tz)
        start_ms = _to_ms(dt)
        status = _status(start_ms, now_ms)
        if status == 'done' or not title:
            continue
        ev = events.setdefault((start_ms, title), {
            'title': title, 'code': '', 'league': league, 'start_ms': start_ms,
            'poster': '', 'status': status, 'servers': []})
        ev['servers'].append([channel, url])
    return sorted(events.values(), key=lambda e: e['start_ms'])


def extract_src(payload):
    """m3u8 from the ?ppcfg=1 JSON, or from window.PP_CLAPPR_CONFIG in the
    plain embed page (same object)."""
    try:
        cfg = json.loads(payload)
    except Exception:
        m = re.search(r'PP_CLAPPR_CONFIG\s*=\s*(\{.*?\});?\s*</script>', payload, re.S)
        try:
            cfg = json.loads(m.group(1)) if m else {}
        except Exception:
            cfg = {}
    return cfg.get('src') or cfg.get('srcBase') or None


# ---- network -------------------------------------------------------------

def _get(url, referer=None):
    import requests
    headers = {'User-Agent': UA}
    if referer:
        headers['Referer'] = referer
    return requests.get(url, headers=headers, timeout=15).text


def list_events():
    return parse_schedule(_get(SCHEDULE, referer=BASE + '/'))


def resolve(server_url):
    """server_url is the watchfa.st embed URL; return (m3u8, embed_url) so
    site_play uses the embed host as Referer/Origin. None if the channel is
    not live yet (embed host answers 404 until the event starts)."""
    cfg_url = '{0}{1}ppcfg=1&_={2}'.format(
        server_url, '&' if '?' in server_url else '?', int(time.time() * 1000))
    src = extract_src(_get(cfg_url))
    if not src:
        src = extract_src(_get(server_url))
    return (src, server_url) if src else None


if __name__ == '__main__':
    _sample = ('-Friday 25 September-\n' + '-' * 40 + '\n'
               'https://watchfa.st/embed.php?code=aaaa [1]\n\n'
               '20:00 [ULEB Euroleague] Basketball: Besiktas vs Valencia [Magenta Sport DE]\n'
               + '-' * 40 + '\n'
               'https://watchfa.st/embed.php?code=bbbb [2]\n\n'
               '20:00 [ULEB Euroleague] Basketball: Besiktas vs Valencia [M+ Baloncesto ES]\n'
               + '-' * 40 + '\n'
               'https://watchfa.st/embed.php?code=cccc [3]\n\n'
               '08:00 [Formula 1] Motorsport: Practice [Sky]\n')
    _now = datetime(2026, 9, 25, 12, 0, tzinfo=gettz(TZ))
    _ev = parse_schedule(_sample, _now)
    assert len(_ev) == 1, _ev          # 08:00 finished, dropped
    assert [s[0] for s in _ev[0]['servers']] == ['Magenta Sport DE', 'M+ Baloncesto ES']
    assert _ev[0]['title'] == 'Basketball: Besiktas vs Valencia'
    assert _ev[0]['league'] == 'ULEB Euroleague'
    assert extract_src('{"src":"https://x/a.m3u8","srcBase":"b"}') == 'https://x/a.m3u8'
    assert extract_src('<script>window.PP_CLAPPR_CONFIG={"srcBase":"https://x/b.m3u8"};</script>') \
        == 'https://x/b.m3u8'
    print('ok')
