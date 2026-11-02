# -*- coding: utf-8 -*-
"""EZTV TV-show source for plugin.video.rlsbb.

Optional menu (gated by the 'eztv_menu' setting). Uses EZTV's official JSON API
(/api/get-torrents) instead of scraping the HTML, which is now behind Cloudflare.
The active mirror comes from the 'eztv.domain' setting, refreshed from
eztvstatus.org by refresh_domains(). Magnets play through resolveurl (debrid).
"""

import json

import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

from six.moves.urllib.parse import urlencode, quote

from resources.lib.modules import client, control, view, tmdb, trakt_bridge
from resources.lib.modules import init
from resources.lib.modules.resolveurl_bridge import evaluate as resolveurl_evaluate

_NOW_PLAYING = 'plugin.video.rlsbb.now_playing'

_ICON = control.join(control.addonPath, 'resources', 'icons', 'eztv.png')
if not xbmcvfs.exists(_ICON):
    _ICON = control.join(control.addonPath, 'resources', 'icons', 'tvshows.png')
FANART = control.addonInfo('fanart')

DEFAULT_DOMAINS = ['EZTVX.TO', 'EZTV1.XYZ', 'EZTV.WF', 'EZTV.TF', 'EZTV.YT']
STATUS_URL = 'https://eztvstatus.org'
_PER_PAGE = 100


def _base():
    d = (control.setting('eztv.domain') or 'EZTVX.TO').strip()
    return 'https://%s' % d.lower()


def _api(**params):
    url = '{0}/api/get-torrents?{1}'.format(_base(), urlencode(params))
    try:
        return json.loads(client.request(url))
    except Exception:
        return {}


def _poster(t):
    img = t.get('large_screenshot') or t.get('small_screenshot') or ''
    if img.startswith('//'):
        img = 'https:' + img
    return img or _ICON


def _add_item(t):
    magnet = t.get('magnet_url')
    if not magnet:
        return
    imdb = (t.get('imdb_id') or '').strip()
    if imdb and not imdb.startswith('tt'):
        imdb = 'tt' + imdb
    payload = json.dumps({'m': magnet, 'imdb': imdb,
                          's': t.get('season'), 'e': t.get('episode'),
                          't': t.get('title', '')})
    label = '{0}  [COLOR gray][S:{1}][/COLOR]'.format(t.get('title', 'N/A'), t.get('seeds', 0))
    control.addDir(label, payload, 'eztv_play', iconimage=_poster(t), fanart=FANART,
                   is_folder=False, is_playable=True)


# ---- menus ---------------------------------------------------------------

def menu():
    control.addDir('Latest Releases', '1', 'eztv_latest', iconimage=_ICON, fanart=FANART)
    control.addDir('Search (by show title)', '', 'eztv_search', iconimage=_ICON, fanart=FANART)
    _end('addons')


def latest(page='1'):
    try:
        page = int(page or 1)
    except ValueError:
        page = 1
    data = _api(limit=_PER_PAGE, page=page)
    torrents = data.get('torrents', [])
    for t in torrents:
        _add_item(t)
    if torrents:
        control.addDir('[COLOR gold]Next Page >>[/COLOR]', str(page + 1), 'eztv_latest',
                       iconimage=_ICON, fanart=FANART)
    elif page == 1:
        control.infoDialog('EZTV returned no releases')
    _end('videos')


def _title_to_imdb(query):
    """Resolve a show title to an IMDB id. EZTV's API filters by imdb_id only, so
    search needs this. Uses IMDb's keyless suggestion endpoint first (works for
    everyone), falling back to TMDB if an API key is configured."""
    query = query.strip()
    try:
        first = query.lower()[0]
        url = 'https://v2.sg.media-imdb.com/suggestion/{0}/{1}.json'.format(
            first, quote(query.lower()))
        data = json.loads(client.request(url))
        cand = [x for x in data.get('d', []) if str(x.get('id', '')).startswith('tt')]
        series = [x for x in cand if 'series' in str(x.get('q', '')).lower()]
        pick = series or cand
        if pick:
            return pick[0]['id']
    except Exception:
        pass
    try:
        show = tmdb.lookup_show(query)
        if show and show.get('imdb'):
            return show['imdb']
    except Exception:
        pass
    return None


def search():
    kb = xbmc.Keyboard('', 'Search EZTV (show title)')
    kb.doModal()
    if not kb.isConfirmed() or not kb.getText().strip():
        return
    imdb = _title_to_imdb(kb.getText())
    if not imdb:
        control.infoDialog('Show not found')
        return
    data = _api(imdb_id=imdb.replace('tt', ''), limit=_PER_PAGE)
    torrents = data.get('torrents', [])
    for t in torrents:
        _add_item(t)
    if not torrents:
        control.infoDialog('No EZTV torrents for that show')
    _end('videos')


def play(payload):
    try:
        p = json.loads(payload)
    except ValueError:
        p = {'m': payload}          # backwards-compat: a bare magnet
    magnet = p.get('m')
    stream_url = resolveurl_evaluate(magnet) if magnet else None
    if not stream_url:
        control.infoDialog('Use a debrid service to play torrents')
        xbmcplugin.setResolvedUrl(init.syshandle, False, xbmcgui.ListItem())
        return

    # Let script.trakt + the MDBList playback monitor (service.py) scrobble this,
    # same as rlsbb.play() does for its own links.
    imdb = p.get('imdb')
    if imdb:
        trakt_bridge.set_ids(imdb=imdb)
        info = {'type': 'episode', 'imdb': imdb, 'season': p.get('s'), 'episode': p.get('e')}
        xbmcgui.Window(10000).setProperty(_NOW_PLAYING, json.dumps(info))

    liz = xbmcgui.ListItem(p.get('t', ''), path=stream_url)
    liz.setProperty('IsPlayable', 'true')
    info_tag = liz.getVideoInfoTag()
    info_tag.setMediaType('episode')
    if imdb:
        info_tag.setUniqueIDs({'imdb': imdb}, 'imdb')
        info_tag.setIMDBNumber(imdb)
    try:
        if p.get('s') is not None:
            info_tag.setSeason(int(p['s']))
        if p.get('e') is not None:
            info_tag.setEpisode(int(p['e']))
    except (TypeError, ValueError):
        pass
    xbmcplugin.setResolvedUrl(init.syshandle, True, liz)


def _end(content='videos'):
    xbmcplugin.setContent(init.syshandle, content)
    xbmcplugin.endOfDirectory(init.syshandle)
    try:
        view.apply_view(content)
    except Exception:
        pass


# ---- domain refresh (saves the mirror list into settings) ----------------

def refresh_domains(silent=False):
    """Read the current mirrors from eztvstatus.org and rewrite the eztv.domain
    option list in settings.xml, so Settings > EZTV always shows live domains."""
    import re
    domains = []
    try:
        html = client.request(STATUS_URL)
        mirrors = client.parseDOM(html, 'a', ret='href', attrs={'class': 'domainLink'})
        domains = [m.split('//')[-1].strip('/').upper() for m in mirrors if '//' in m]
        domains = ['EZTVX.TO'] + [d for d in domains if d != 'EZTVX.TO']
    except Exception:
        domains = []
    if not domains:
        domains = list(DEFAULT_DOMAINS)

    path = control.join(control.addonPath, 'resources', 'settings.xml')
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = fh.read()
        new = re.sub(r'(<setting id="eztv\.domain"[^>]*values=")[^"]*(")',
                     r'\g<1>' + '|'.join(domains) + r'\g<2>', data)
        if new != data:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new)
    except Exception as e:
        if not silent:
            control.infoDialog('EZTV domains refresh failed: {0}'.format(e))
        return domains
    if not silent:
        control.infoDialog('EZTV domains updated: {0}'.format(', '.join(domains)))
        control.refresh()
    return domains
