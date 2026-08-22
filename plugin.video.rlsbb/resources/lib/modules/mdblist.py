# -*- coding: utf-8 -*-
"""MDBList integration -- OAuth device-code auth + watchlist reading.

MDBList can sync a user's Trakt watchlist/history on their own account (set up
once on mdblist.com's own "Trakt Sync" feature), sidestepping Trakt's own
VIP-gated API app registration entirely. Verified live (2026):
  1. POST /oauth/device-authorization/ {client_id, scope} -> device_code,
     user_code, verification_uri, interval, expires_in.
  2. Show user_code + verification_uri, poll POST /oauth/token/ with
     grant_type=urn:ietf:params:oauth:grant-type:device_code until an
     access_token/refresh_token pair comes back (access tokens last 30 days).
  3. GET /watchlist/items/ with Authorization: Bearer <access_token>.
"""
import base64
import json
import sqlite3
import struct
import time
import zlib

import requests
import xbmc
import xbmcgui
import xbmcvfs

from resources.lib.modules import cache, control

_BASE = 'https://api.mdblist.com'
_DEVICE_AUTH_URL = _BASE + '/oauth/device-authorization/'
_TOKEN_URL = _BASE + '/oauth/token/'
_WATCHLIST_URL = _BASE + '/watchlist/items/'
_TOKEN_FILE = 'mdblist_token.json'
_QR_FILE = 'special://temp/mdblist_qr.png'

# the app's own OAuth client id (public identifier, not a secret -- device-code
# apps have no client_secret at all), base64'd just so it doesn't sit as a plain
# grep-able string; every install of this addon shares it, each user still
# authenticates their own separate account via authenticate() below
_CLIENT_ID = base64.b64decode('dFpsWWd2QVJjYUhNOFgzY2VEQkdnZGZXY1gwU0VXUHM5WjhaMHBRdw==').decode()


def _token_path():
    control.makeFile(control.dataPath)
    return control.join(control.dataPath, _TOKEN_FILE)


def _load_token():
    path = _token_path()
    if not control.exists(path):
        return None
    try:
        f = control.openFile(path, 'r')
        data = json.loads(f.read())
        f.close()
        return data
    except Exception:
        return None


def _save_token(data):
    f = control.openFile(_token_path(), 'w')
    f.write(json.dumps(data))
    f.close()


def is_authenticated():
    return _load_token() is not None


def sign_out():
    path = _token_path()
    if control.exists(path):
        control.deleteFile(path)


def get_username():
    """The connected account's username, or None if not authenticated / the
    request failed -- shown in the MDBList menu so the user can confirm which
    account they're actually looking at."""
    r = _authed_request('GET', '/user')
    if r is None:
        return None
    try:
        return r.json().get('username')
    except Exception:
        return None


def _ensure_white_texture():
    """A 1x1 opaque white PNG, built once from stdlib (no bundled asset needed) --
    every rect in the popup below is this same texture tinted via colorDiffuse."""
    path = xbmcvfs.translatePath('special://temp/rlsbb_solid_white.png')
    if not xbmcvfs.exists(path):
        def chunk(tag, data):
            return (struct.pack('!I', len(data)) + tag + data +
                    struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff))
        png = (b'\x89PNG\r\n\x1a\n' +
               chunk(b'IHDR', struct.pack('!IIBBBBB', 1, 1, 8, 6, 0, 0, 0)) +
               chunk(b'IDAT', zlib.compress(bytes([0, 255, 255, 255, 255]))) +
               chunk(b'IEND', b''))
        with xbmcvfs.File(path, 'wb') as f:
            f.write(bytearray(png))
    return path


class _DeviceAuthWindow(xbmcgui.WindowDialog):
    ACTION_CANCEL = (10, 92)  # ACTION_PREVIOUS_MENU, ACTION_NAV_BACK

    def __init__(self, user_code, verify_url, qr_path):
        super().__init__()
        self.cancelled = False
        w, h = self.getWidth(), self.getHeight()
        white = _ensure_white_texture()

        # dim the rest of the screen so this reads as a modal popup, not stray text
        self.addControl(xbmcgui.ControlImage(0, 0, w, h, white, colorDiffuse='0x99000000'))

        panel_w, panel_h = 760, 320
        px, py = (w - panel_w) // 2, (h - panel_h) // 2
        self.addControl(xbmcgui.ControlImage(px, py, panel_w, panel_h, white, colorDiffuse='0xF0161a1f'))
        self.addControl(xbmcgui.ControlImage(px, py, panel_w, 6, white, colorDiffuse='0xFFFFA500'))

        pad = 40
        self.addControl(xbmcgui.ControlLabel(px + pad, py + 24, panel_w - 2 * pad, 40,
                                              'Connect MDBList', textColor='0xFFFFA500'))

        qr_size = 220
        if qr_path:
            qr_x, qr_y = px + pad, py + (panel_h - qr_size) // 2
            self.addControl(xbmcgui.ControlImage(qr_x, qr_y, qr_size, qr_size, qr_path))
            text_x = qr_x + qr_size + pad
        else:
            text_x = px + pad
        text_w = px + panel_w - pad - text_x
        text_y = py + (panel_h // 2) - 50

        self.addControl(xbmcgui.ControlLabel(text_x, text_y, text_w, 30,
                                              'Go to: {0}'.format(verify_url), textColor='0xFFFFFFFF'))
        self.addControl(xbmcgui.ControlLabel(text_x, text_y + 40, text_w, 30,
                                              'Enter code: {0}'.format(user_code), textColor='0xFFFFFFFF'))
        if qr_path:
            self.addControl(xbmcgui.ControlLabel(text_x, text_y + 80, text_w, 30,
                                                  'Or scan the QR code with your phone',
                                                  textColor='0xFFAAAAAA'))

        self.addControl(xbmcgui.ControlLabel(px, py + panel_h - 40, panel_w, 30, 'Press Back to cancel',
                                              textColor='0xFF888888', alignment=2))  # XBFONT_CENTER_X

    def onAction(self, action):
        if action.getId() in self.ACTION_CANCEL:
            self.cancelled = True
            self.close()


def _make_qr(text):
    try:
        import pyqrcode
        path = xbmcvfs.translatePath(_QR_FILE)
        pyqrcode.create(text).png(path, scale=6)
        return path
    except Exception:
        return None  # script.module.pyqrcode not installed -- fall back to text-only


def authenticate():
    try:
        r = requests.post(_DEVICE_AUTH_URL, data={'client_id': _CLIENT_ID, 'scope': 'read'}, timeout=15)
        r.raise_for_status()
        auth = r.json()
    except Exception:
        control.infoDialog('Could not start MDBList authentication')
        return

    device_code = auth['device_code']
    user_code = auth['user_code']
    verify_url = auth.get('verification_uri', 'mdblist.com/activate')
    interval = auth.get('interval', 5)
    expires_in = auth.get('expires_in', 600)

    # verification_uri_complete (if the server sends it) already embeds the code,
    # so scanning the QR code alone finishes the flow with nothing to type
    qr_target = auth.get('verification_uri_complete') or verify_url
    qr_path = _make_qr(qr_target)

    window = _DeviceAuthWindow(user_code, verify_url, qr_path)
    window.show()

    deadline = time.time() + expires_in
    token = None
    while time.time() < deadline:
        if window.cancelled:
            break
        xbmc.sleep(int(interval) * 1000)
        try:
            resp = requests.post(_TOKEN_URL, data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'device_code': device_code,
                'client_id': _CLIENT_ID,
            }, timeout=15)
            data = resp.json()
        except Exception:
            continue
        if resp.status_code == 200 and data.get('access_token'):
            token = data
            break
        # any pending/slow_down style response just means keep polling

    window.close()
    del window

    if token:
        _save_token(token)
        control.infoDialog('MDBList authenticated')
    else:
        control.infoDialog('MDBList authentication timed out or was cancelled')


def _refresh(token):
    try:
        r = requests.post(_TOKEN_URL, data={
            'grant_type': 'refresh_token',
            'refresh_token': token['refresh_token'],
            'client_id': _CLIENT_ID,
        }, timeout=15)
        r.raise_for_status()
        new_token = r.json()
        _save_token(new_token)
        return new_token
    except Exception:
        return None


def _authed_request(method, path, **kwargs):
    """GET/POST/PUT/DELETE against api.mdblist.com with the stored bearer token,
    refreshing once on a 401. Returns the Response, or None if not authenticated
    or the request failed outright."""
    token = _load_token()
    if not token:
        return None

    def _do(access_token):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = 'Bearer {0}'.format(access_token)
        return requests.request(method, _BASE + path, headers=headers, timeout=15, **kwargs)

    try:
        r = _do(token['access_token'])
        if r.status_code == 401 and token.get('refresh_token'):
            token = _refresh(token)
            if not token:
                return None
            r = _do(token['access_token'])
        r.raise_for_status()
        return r
    except Exception:
        return None


def _fetch_details_batch(provider_type, ids):
    """The actual network call, factored out so cache.get() can memoize it by
    (provider_type, ids) -- ids must be a hashable (tuple), not a list."""
    try:
        r = _authed_request('POST', '/tmdb/{0}/'.format(provider_type), json={'ids': list(ids)})
        return r.json() if r is not None else []
    except Exception:
        return []


def _enrich_with_details(items):
    """Batch-fetch poster/description/genres for a list of items (mutates and
    returns them) using their tmdb ids -- one API call per media_type present in
    the list, not one per item, and cached for 12h (posters/plots/genres barely
    change) so repeat menu opens don't re-hit the API at all. Verified live:
    POST /tmdb/{movie|show}/ {ids: [tmdb_id, ...]} returns [{ids: {tmdb, ...},
    poster, description, genres: [{id, title}, ...], ...}, ...]. None of
    watchlist/upnext/watched/list items carry poster or plot text themselves --
    this is the only way to get them."""
    by_type = {}
    for item in items:
        if item.get('tmdb'):
            by_type.setdefault(item.get('type', 'movie'), []).append(item)

    for media_type, group in by_type.items():
        provider_type = 'movie' if media_type == 'movie' else 'show'
        ids = tuple(sorted(set(it['tmdb'] for it in group)))
        details = cache.get(_fetch_details_batch, 12, provider_type, ids)
        by_tmdb = {}
        for d in (details or []):
            if isinstance(d, dict):
                by_tmdb[(d.get('ids') or {}).get('tmdb')] = d
        for it in group:
            d = by_tmdb.get(it['tmdb'])
            if not d:
                continue
            it['poster'] = d.get('poster') or ''
            it['plot'] = d.get('description') or ''
            genres = d.get('genres') or []
            it['genre'] = ' / '.join(g.get('title') for g in genres if g.get('title'))
    return items


def _media_ref(item):
    """Best-effort title/year/ids extraction -- exact field names per endpoint
    aren't all verified against live data yet, see the mdblist-api skill."""
    ids = item.get('ids') or {}
    return {
        'title': item.get('title') or item.get('name'),
        'year': item.get('release_year') or item.get('year'),
        'imdb': item.get('imdb') or ids.get('imdb'),
        'tmdb': item.get('tmdb') or ids.get('tmdb'),
    }


def get_watchlist():
    """Returns [{'title', 'year', 'type': 'movie'|'show', 'imdb', 'tmdb'}, ...]
    or None if not authenticated / the request failed."""
    r = _authed_request('GET', '/watchlist/items/')
    if r is None:
        return None
    data = r.json()
    items = []
    for m in (data.get('movies') or []):
        items.append(dict(_media_ref(m), type='movie'))
    for s in (data.get('shows') or []):
        items.append(dict(_media_ref(s), type='show'))
    return _enrich_with_details(items)


_OVERRIDE_TABLE = 'upnext_override'


def _override_table(dbcur):
    dbcur.execute('CREATE TABLE IF NOT EXISTS {0} (show_tmdb TEXT PRIMARY KEY, '
                  'season INTEGER, episode INTEGER)'.format(_OVERRIDE_TABLE))


def set_upnext_override(show_tmdb, season, episode):
    """Remember locally that `show_tmdb`'s next episode should be (season, episode) --
    called right after a successful episode mark_watched, so Up Next can advance
    immediately instead of waiting out MDBList's own 15-min server cache on /upnext
    (verified live, not fixable from the request side -- see get_upnext())."""
    if not show_tmdb:
        return
    try:
        dbcon = sqlite3.connect(control.upnextOverrideFile)
        dbcur = dbcon.cursor()
        _override_table(dbcur)
        dbcur.execute('INSERT OR REPLACE INTO {0} VALUES (?, ?, ?)'.format(_OVERRIDE_TABLE),
                       (str(show_tmdb), season, episode))
        dbcon.commit()
    except Exception:
        pass


def _get_upnext_override(show_tmdb):
    try:
        dbcon = sqlite3.connect(control.upnextOverrideFile)
        dbcur = dbcon.cursor()
        _override_table(dbcur)
        dbcur.execute('SELECT season, episode FROM {0} WHERE show_tmdb = ?'.format(_OVERRIDE_TABLE),
                       (str(show_tmdb),))
        return dbcur.fetchone()
    except Exception:
        return None


def _clear_upnext_override(show_tmdb):
    try:
        dbcon = sqlite3.connect(control.upnextOverrideFile)
        dbcur = dbcon.cursor()
        _override_table(dbcur)
        dbcur.execute('DELETE FROM {0} WHERE show_tmdb = ?'.format(_OVERRIDE_TABLE), (str(show_tmdb),))
        dbcon.commit()
    except Exception:
        pass


def get_upnext():
    """In-progress shows with their next unwatched episode. Verified live shape:
    {items: [{show: {title, year, ids}, next_episode: {season, episode, title,
    ...}, progress, last_watched_at}, ...]} -- show/episode are nested, not flat."""
    # The API caches this endpoint's response for up to 15 min server-side
    # (Cache-Control: max-age=900/s-maxage=900, verified live) and does not honor a
    # client Cache-Control: no-cache request (tried, confirmed no effect) -- a
    # just-marked-watched episode can take up to that long to advance here. Nothing
    # fixable client-side; this is upstream API behavior, not an addon bug.
    r = _authed_request('GET', '/upnext', params={'limit': 100})
    if r is None:
        return None
    data = r.json()
    items = []
    for it in (data.get('items') or []):
        show = it.get('show') or {}
        ep = it.get('next_episode') or {}
        ids = show.get('ids') or {}
        show_tmdb = ids.get('tmdb')
        season, episode = ep.get('season'), ep.get('episode')
        # ponytail: locally guess past the API's own stale answer when we know
        # better. set_upnext_override() records (season, episode) right after a
        # successful mark_watched -- if the API hasn't caught up yet (still <= what
        # we just marked), use our guess instead; once the API's own next_episode
        # passes it, the override is stale and gets dropped. Doesn't know a show's
        # season length, so a season-finale watch briefly guesses a nonexistent next
        # episode in the same season until the API confirms the real S+1E1 -- self
        # heals within that same 15-min window, upgrade path is fetching season
        # episode counts if that edge case ever actually bothers someone.
        override = _get_upnext_override(show_tmdb) if show_tmdb else None
        if override:
            ov_season, ov_episode = override
            if (season or 0, episode or 0) < (ov_season, ov_episode):
                season, episode = ov_season, ov_episode
            else:
                _clear_upnext_override(show_tmdb)
        title = show.get('title') or 'Untitled'
        if season and episode:
            title = '{0} S{1:02d}E{2:02d}'.format(title, season, episode)
        items.append({'title': title, 'year': show.get('year'), 'imdb': ids.get('imdb'),
                       'tmdb': show_tmdb, 'season': season, 'episode': episode,
                       'type': 'episode' if (season and episode) else 'show'})
    return _enrich_with_details(items)


def get_watched():
    """Watch history ('Recently Watched'). Verified live shape: movies are
    {last_watched_at, movie: {title, year, ids}}; per-episode watches are under
    "episodes": {last_watched_at, episode: {season, number, name, show: {title,
    year, ids}}} -- both nested one level deeper than watchlist items."""
    r = _authed_request('GET', '/sync/watched', params={'limit': 100})
    if r is None:
        return None
    data = r.json()
    items = []
    for m in (data.get('movies') or []):
        movie = m.get('movie') or {}
        ids = movie.get('ids') or {}
        items.append({'title': movie.get('title'), 'year': movie.get('year'),
                       'imdb': ids.get('imdb'), 'tmdb': ids.get('tmdb'), 'type': 'movie'})
    for e in (data.get('episodes') or []):
        ep = e.get('episode') or {}
        show = ep.get('show') or {}
        ids = show.get('ids') or {}
        season, episode = ep.get('season'), ep.get('number')
        title = show.get('title') or 'Untitled'
        if season and episode:
            title = '{0} S{1:02d}E{2:02d}'.format(title, season, episode)
        items.append({'title': title, 'year': show.get('year'), 'imdb': ids.get('imdb'),
                       'tmdb': ids.get('tmdb'), 'season': season, 'episode': episode,
                       'type': 'episode' if (season and episode) else 'show'})
    return _enrich_with_details(items)


def get_liked_lists():
    """Lists the user has liked (their own or others')."""
    r = _authed_request('GET', '/lists/liked', params={'limit': 100})
    if r is None:
        return None
    data = r.json()
    lists = data.get('lists') if isinstance(data, dict) else data
    return [{'id': lst.get('id'), 'name': lst.get('name') or lst.get('title')}
            for lst in (lists or [])]


def get_user_lists():
    """The authenticated user's own custom static lists."""
    r = _authed_request('GET', '/lists/user')
    if r is None:
        return None
    data = r.json()
    lists = data.get('lists') if isinstance(data, dict) else data
    return [{'id': lst.get('id'), 'name': lst.get('name') or lst.get('title')}
            for lst in (lists or [])]


def get_list_items(list_id):
    r = _authed_request('GET', '/lists/{0}/items'.format(list_id))
    if r is None:
        return None
    data = r.json()
    items = []
    for m in (data.get('movies') or []):
        items.append(dict(_media_ref(m), type='movie'))
    for s in (data.get('shows') or []):
        items.append(dict(_media_ref(s), type='show'))
    return _enrich_with_details(items)


def _sync_key(media_type):
    return 'movies' if media_type == 'movie' else 'shows'


def _ids_payload(media_type, imdb, tmdb, nested):
    entry = {}
    if imdb:
        entry['imdb'] = imdb
    if tmdb:
        entry['tmdb'] = tmdb
    if nested:
        entry = {'ids': entry}
    return {_sync_key(media_type): [entry]}


def remove_from_watchlist(media_type, imdb=None, tmdb=None):
    body = _ids_payload(media_type, imdb, tmdb, nested=True)  # watchlist wants {"ids": {...}}
    r = _authed_request('POST', '/watchlist/items/remove', json=body)
    return r is not None


def remove_from_list(list_id, media_type, imdb=None, tmdb=None):
    body = _ids_payload(media_type, imdb, tmdb, nested=False)  # list items want flat ids
    r = _authed_request('POST', '/lists/{0}/items/remove'.format(list_id), json=body)
    return r is not None


def unlike_list(list_id):
    r = _authed_request('DELETE', '/lists/{0}/like'.format(list_id))
    return r is not None


def _now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _episode_ids(imdb, tmdb):
    ids = {}
    if imdb:
        ids['imdb'] = imdb
    if tmdb:
        ids['tmdb'] = tmdb
    return ids


def mark_watched(media_type, imdb=None, tmdb=None, season=None, episode_number=None):
    if media_type == 'episode':
        # episodes identify by the SHOW's own ids + season/episode number nested
        # underneath -- not a separate per-episode id. This works identically
        # whether the episode came straight from a fresh /upnext response or from a
        # locally guessed override (set_upnext_override) that /upnext hasn't caught
        # up to yet, since we always know season+episode number either way.
        entry = {'ids': _episode_ids(imdb, tmdb), 'seasons': [{'number': int(season), 'episodes': [
            {'number': int(episode_number), 'watched_at': _now_iso()}]}]}
        r = _authed_request('POST', '/sync/watched', json={'shows': [entry]})
        return r is not None
    entry = {'ids': _episode_ids(imdb, tmdb), 'watched_at': _now_iso()}
    r = _authed_request('POST', '/sync/watched', json={_sync_key(media_type): [entry]})
    return r is not None


def remove_watched(media_type, imdb=None, tmdb=None, season=None, episode_number=None):
    if media_type == 'episode':
        entry = {'ids': _episode_ids(imdb, tmdb), 'seasons': [{'number': int(season), 'episodes': [
            {'number': int(episode_number)}]}]}
        r = _authed_request('POST', '/sync/watched/remove', json={'shows': [entry]})
        return r is not None
    body = _ids_payload(media_type, imdb, tmdb, nested=True)
    r = _authed_request('POST', '/sync/watched/remove', json=body)
    return r is not None


def rate(media_type, rating, imdb=None, tmdb=None, season=None, episode_number=None):
    """rating: 1-10."""
    if media_type == 'episode':
        entry = {'ids': _episode_ids(imdb, tmdb), 'seasons': [{'number': int(season), 'episodes': [
            {'number': int(episode_number), 'rating': int(rating)}]}]}
        r = _authed_request('POST', '/sync/ratings', json={'shows': [entry]})
        return r is not None
    entry = {'ids': _episode_ids(imdb, tmdb), 'rating': int(rating), 'rated_at': _now_iso()}
    r = _authed_request('POST', '/sync/ratings', json={_sync_key(media_type): [entry]})
    return r is not None
