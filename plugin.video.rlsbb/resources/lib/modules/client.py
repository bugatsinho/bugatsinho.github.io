# -*- coding: utf-8 -*-
import socket
from urllib.parse import urlparse

import requests

from resources.lib.modules import cache, control
from resources.lib.modules import dom_parser

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

_session = requests.Session()
_session.headers.update({'User-Agent': USER_AGENT})

# many countries block rlsbb's domains at the DNS level (the ISP's resolver lies
# about the IP -- the site itself is reachable) -- resolving via DNS-over-HTTPS
# instead sidesteps that specific block. Doesn't help an IP-level or SNI-level
# block, only the (most common) DNS one.
_DOH_RESOLVERS = ['https://cloudflare-dns.com/dns-query', 'https://dns.google/resolve']
_orig_getaddrinfo = socket.getaddrinfo
_doh_ip_cache = {}
_doh_patched = False


def _doh_lookup(hostname):
    for resolver in _DOH_RESOLVERS:
        try:
            r = requests.get(resolver, params={'name': hostname, 'type': 'A'},
                              headers={'Accept': 'application/dns-json'}, timeout=5)
            r.raise_for_status()
            for answer in (r.json().get('Answer') or []):
                if answer.get('type') == 1:  # A record
                    return answer['data']
        except Exception:
            continue
    return None


def _patched_getaddrinfo(host, *args, **kwargs):
    ip = _doh_ip_cache.get(host)
    return _orig_getaddrinfo(ip, *args, **kwargs) if ip else _orig_getaddrinfo(host, *args, **kwargs)


def enable_doh(hostname):
    """Resolve `hostname` via DoH and pin the socket layer to that IP for the rest
    of this plugin invocation -- monkeypatching socket.getaddrinfo only changes
    which IP the TCP connection lands on, urllib3 still uses the real hostname
    string for the TLS handshake (SNI) and cert verification, so nothing about
    HTTPS security changes. Cached 6h so this only round-trips to Cloudflare/Google
    once per domain for a while, not on every single request. Silently does
    nothing if both resolvers fail (or return no answer) -- normal DNS still runs,
    same as before this existed."""
    global _doh_patched
    if hostname in _doh_ip_cache:
        return
    ip = cache.get(_doh_lookup, 6, hostname)
    if not ip:
        return
    _doh_ip_cache[hostname] = ip
    if not _doh_patched:
        socket.getaddrinfo = _patched_getaddrinfo
        _doh_patched = True


def request(url, params=None, data=None, headers=None, timeout=20):
    hostname = urlparse(url).hostname
    if hostname:
        enable_doh(hostname)
    method = _session.post if data is not None else _session.get
    r = method(url, params=params, data=data, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


def request_with_fallback(path):
    """GET `path` (starting with '/') against the configured main domain, falling back
    to the mirror domain on any request failure. Returns (html, domain_used)."""
    domains = [control.setting('domain.main') or 'rlsbb.to',
               control.setting('domain.mirror') or 'rlsbb.in']
    last_err = None
    for domain in domains:
        try:
            html = request('https://{0}{1}'.format(domain, path))
            return html, domain
        except Exception as e:
            last_err = e
            continue
    raise last_err


def parseDOM(html, name, attrs=None, ret=False):
    results = dom_parser.parse_dom(html, name, attrs=attrs)
    if ret:
        return [r.attrs.get(ret) for r in results if ret in r.attrs]
    return [r.content for r in results]
