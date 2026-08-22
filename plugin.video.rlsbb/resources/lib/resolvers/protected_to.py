# -*- coding: utf-8 -*-
"""Resolver for protected.to link gates (ASP.NET "Ncrypt" app). Every gated download
link on rlsbb.to posts points here first.

Verified live protocol (2026), 3 steps:
  1. GET the gate URL -- returns a form with an antiforgery token, a "Slug", a
     "CaptchaDeText" hidden field tied to the captcha image, and the captcha image itself.
  2. POST the solved captcha back to the same URL -- on success, the response is a NEW
     page (not a redirect). Two shapes seen for this page:
       a) the host picker -- one `<a class="UploadHost" data-slug="...">` per available
          host, the host identified by its icon filename (e.g. "rapidgator.net.png").
       b) a single-host "folder" listing (single-host backups, e.g. "Single File RAR:
          RAPiDGATOR Backup") -- `<div class="links">` with either ONE `<a href="...">`
          pointing at ANOTHER protected.to gate for the actual file (needs its own
          captcha solve, repeat shape a) or b)) or -- on the final round -- straight at
          the resolved hoster URL with no GetInFo step at all (this chain is why these
          can take 2-3 pin entries instead of 1); or MULTIPLE `<a href="...">`, one
          already-resolved hoster link per episode -- a season pack.
  3. POST {token, folder: Slug, link: <chosen data-slug>} to
     protected.to/admin/Main/GetInFo -- plain-text response, either
     "redirect: <final hoster url>" or "stop: <error message>".
"""
import hashlib
import re
from urllib.parse import urljoin, urlparse

import requests
import xbmc
import xbmcgui
import xbmcvfs

from resources.lib.modules import client, control


def _log(msg):
    xbmc.log('plugin.video.rlsbb protected_to :: {0}'.format(msg), xbmc.LOGINFO)

_TOKEN_RE = re.compile(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"')
_SLUG_RE = re.compile(r'id="Slug"[^>]*value="([^"]+)"')
_CAPTCHA_TEXT_RE = re.compile(r'name="CaptchaDeText"[^>]*value="([^"]+)"')
_CAPTCHA_IMG_RE = re.compile(r'id="CaptchaImage"[^>]*src="([^"]+)"')
_JS_TOKEN_RE = re.compile(r'var token\s*=\s*"([^"]+)"')
_JS_SLUG_RE = re.compile(r'var Slug\s*=\s*"([^"]+)"')
_HOST_RE = re.compile(r'data-slug="([^"]+)"[^>]*class="UploadHost"><img[^>]*src="([^"]+)"')
# single-host "backup" gates skip the host picker and instead show a file listing
# here -- either another protected.to gate to chain through, or (on the final round)
# the resolved hoster link(s) themselves -- season packs list one link per episode
_LINKS_DIV_RE = re.compile(r'<div class="links"[^>]*>(.*?)</div>', re.S)
_HREF_RE = re.compile(r'''href=['"]([^'"]+)['"]''')
_CAPTCHA_DIR = 'special://temp/'
_GETINFO_URL = 'http://protected.to/admin/Main/GetInFo'

_session = requests.Session()


def _get(url, **kwargs):
    # protected.to keeps its own requests.Session() (cookies need to persist across
    # a multi-round captcha chain) instead of going through client.py's -- routing
    # through client.request() would lose that, so DoH has to be applied here too
    # (client.enable_doh() is safe to call repeatedly, cached) or a gated link never
    # benefits from it even though the rest of the addon does.
    client.enable_doh(urlparse(url).hostname)
    return _session.get(url, **kwargs)


def _post(url, **kwargs):
    client.enable_doh(urlparse(url).hostname)
    return _session.post(url, **kwargs)


class _CaptchaImageWindow(xbmcgui.WindowDialog):
    """Just the captcha image, nothing else -- shown non-modally (.show(), not
    .doModal()) so it stays on screen while Kodi's own native input dialog collects
    the code. A hand-rolled OK/Cancel control layout needs its own remote-navigation
    wiring to work at all and is one more thing that can silently fail; the native
    input dialog is a proven, fully self-contained Kodi widget."""

    def __init__(self, image_path):
        super().__init__()
        self.addControl(xbmcgui.ControlImage(60, 40, 300, 150, image_path))


def _fetch_form(gate_url):
    html = _get(gate_url, timeout=20).text
    token = _TOKEN_RE.search(html)
    slug = _SLUG_RE.search(html)
    captcha_text = _CAPTCHA_TEXT_RE.search(html)
    captcha_img = _CAPTCHA_IMG_RE.search(html)
    if not (token and slug and captcha_text and captcha_img):
        return None
    return {
        '__RequestVerificationToken': token.group(1),
        'Slug': slug.group(1),
        'CaptchaDeText': captcha_text.group(1),
        'img_url': urljoin(gate_url, captcha_img.group(1)),
    }


def _prompt_captcha(img_url):
    data = _get(img_url, timeout=20).content
    # a fixed filename would let Kodi's image cache keep showing a stale texture for
    # a new round's captcha (same path in, cached bitmap out) -- hash the image URL
    # (unique per round) into the filename so every round is a genuinely new path
    digest = hashlib.md5(img_url.encode('utf-8')).hexdigest()
    image_path = xbmcvfs.translatePath('{0}releaseBB_captcha_{1}.jpg'.format(_CAPTCHA_DIR, digest))
    with xbmcvfs.File(image_path, 'wb') as f:
        f.write(bytearray(data))

    image_window = _CaptchaImageWindow(image_path)
    image_window.show()
    try:
        # captchas here are digits-only -- the numeric PIN pad is smaller and simpler
        # than the full alphanumeric keyboard
        code = xbmcgui.Dialog().numeric(0, 'Enter the code shown above')
    finally:
        image_window.close()
        del image_window
    return code or None


def _pick_host_slug(html, host_hint):
    """host_hint is a hostname substring like 'rapidgator.net' -- matched against the
    icon filename of each offered host. Falls back to the first host if no hint matches."""
    hosts = _HOST_RE.findall(html)  # [(link_slug, icon_src), ...]
    if not hosts:
        return None
    if host_hint:
        for link_slug, icon_src in hosts:
            if host_hint in icon_src:
                return link_slug
    return hosts[0][0]


_MAX_CAPTCHA_ROUNDS = 5


def resolve(gate_url, host_hint=None):
    _log('resolve() start gate_url={0} host_hint={1}'.format(gate_url, host_hint))
    reason = 'unknown'
    for attempt in range(_MAX_CAPTCHA_ROUNDS):
        _log('--- round {0}/{1} ---'.format(attempt + 1, _MAX_CAPTCHA_ROUNDS))
        if attempt > 0:
            control.infoDialog('Another code needed ({0}/{1})'.format(
                attempt + 1, _MAX_CAPTCHA_ROUNDS), time=2000)

        form = _fetch_form(gate_url)
        if not form:
            reason = 'gate page format not recognized'
            _log('_fetch_form failed -- form fields not found in gate page')
            continue
        _log('form fetched: Slug={0} CaptchaDeText={1} img_url={2}'.format(
            form['Slug'], form['CaptchaDeText'], form['img_url']))

        code = _prompt_captcha(form['img_url'])
        if not code:
            _log('user cancelled captcha entry')
            return None  # user cancelled -- no point retrying
        _log('code entered: {0}'.format(code))

        solve_response = _post(gate_url, data={
            '__RequestVerificationToken': form['__RequestVerificationToken'],
            'Slug': form['Slug'],
            'CaptchaDeText': form['CaptchaDeText'],
            'CaptchaInputText': code,
        }, timeout=20)
        _log('solve POST status={0} response[:300]={1}'.format(
            solve_response.status_code, solve_response.text[:300].replace('\n', ' ').replace('\r', '')))

        js_token = _JS_TOKEN_RE.search(solve_response.text)
        js_slug = _JS_SLUG_RE.search(solve_response.text)
        if not (js_token and js_slug):
            reason = 'code not accepted'
            _log('js token/slug NOT found in solve response -- code rejected or page changed shape')
            continue  # wrong captcha -- retry with a fresh one
        _log('code accepted: js_token={0} js_slug={1}'.format(js_token.group(1), js_slug.group(1)))

        link_slug = _pick_host_slug(solve_response.text, host_hint)
        if not link_slug:
            # single-host "backup" gates don't show the host picker straight away --
            # solving the captcha instead reveals a one-item file listing that's
            # either ANOTHER protected.to gate to chain through (needs its own solve),
            # or, on the final round, the already-resolved hoster link itself
            links_match = _LINKS_DIV_RE.search(solve_response.text)
            targets = _HREF_RE.findall(links_match.group(1)) if links_match else []
            if len(targets) == 1:
                target = targets[0]
                if (urlparse(target).hostname or '') == 'protected.to':
                    gate_url = target
                    reason = 'chained to nested gate'
                    _log('no host picker yet -- following nested gate {0}'.format(gate_url))
                    continue
                _log('resolved directly via single-host backup listing: {0}'.format(target))
                return target
            if len(targets) > 1 and not any(
                    (urlparse(t).hostname or '') == 'protected.to' for t in targets):
                # a season pack -- one already-resolved hoster link per episode, no
                # further gate/captcha needed for any of them
                _log('resolved to a {0}-link season pack'.format(len(targets)))
                return targets
            debug_path = xbmcvfs.translatePath('{0}releaseBB_debug_nohost.html'.format(_CAPTCHA_DIR))
            with xbmcvfs.File(debug_path, 'w') as f:
                f.write(solve_response.text)
            _log('no UploadHost data-slug and no links listing found -- full response dumped to {0}'.format(
                debug_path))
            control.infoDialog('No hoster link found behind this gate')
            return None
        _log('picked link_slug={0}'.format(link_slug))

        info_response = _post(_GETINFO_URL, data={
            'token': js_token.group(1),
            'folder': js_slug.group(1),
            'link': link_slug,
        }, timeout=20)
        text = info_response.text.strip()
        _log('GetInFo status={0} response={1}'.format(info_response.status_code, text[:300]))
        if text.startswith('redirect:'):
            final_url = text.split(':', 1)[1].strip()
            _log('SUCCESS final_url={0}'.format(final_url))
            return final_url
        if text.startswith('stop:'):
            _log('GetInFo returned stop -- gate refused this link_slug/token pair')
            control.infoDialog(text.split(':', 1)[1].strip())
            return None
        reason = 'unexpected response: {0}'.format(text[:60])
        _log('unexpected GetInFo response shape')

    _log('gave up after {0} rounds, reason={1}'.format(_MAX_CAPTCHA_ROUNDS, reason))
    control.okDialog('ReleaseBB', 'Could not solve the link gate: {0}'.format(reason))
    return None
