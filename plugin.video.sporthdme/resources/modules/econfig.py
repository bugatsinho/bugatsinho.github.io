# -*- coding: utf-8 -*-

"""
Decoder for the ``window._econfig`` blob used by the streaming player pages
(``fisherman.click``, ``wilderness.click`` and friends) that the ``glisco.link``
and ``sansat.link`` channel pages redirect to.

The encoding is layered:

    1. The page emits ``window._econfig = '<outer base64>';``
    2. Decoding the outer base64 yields a string of length L which is then
       split into 4 equal chunks of size floor(L/4) (any leftover bytes are
       discarded -- this matches the JS implementation).
    3. Each chunk has the character at index 3 removed (i.e. the 4th char),
       then the result is base64-decoded.
    4. The four decoded chunks are reordered using the index map [2, 0, 3, 1]:
       ``out[2] = chunk0, out[0] = chunk1, out[3] = chunk2, out[1] = chunk3``.
    5. The four pieces are concatenated and base64-decoded again, producing
       a JSON document with ``stream_url`` / ``stream_url_nop2p`` and friends.

This is a faithful Python re-implementation of the JS function ``_0x89331a``
seen in ``/assets/stream.js`` (offset ~78050), with the obfuscation removed
for clarity.

The module is stdlib-only on purpose so it works in every Kodi 18 / 19 / 20 /
21 environment without extra ``<requires>`` entries in addon.xml.
"""

from __future__ import absolute_import, print_function

import base64
import json
import re

try:
    string_types = (str, unicode)  # noqa: F821 (Python 2)
except NameError:
    string_types = (str,)


_ECONFIG_RE = re.compile(
    r"window\._econfig\s*=\s*['\"]([A-Za-z0-9+/=]+)['\"]"
)
_REORDER = (2, 0, 3, 1)
_CHUNKS = 4


def _b64decode_lossy(s):
    """
    base64-decode ``s``, padding as required, returning a latin-1 ``str`` so
    that further string slicing (which is byte-oriented in this protocol)
    keeps working without UnicodeDecodeError on intermediate layers.
    """
    if isinstance(s, bytes):
        s = s.decode("ascii", "ignore")
    s = s + "=" * (-len(s) % 4)
    return base64.b64decode(s).decode("latin-1")


def find_econfig(html):
    """Return the raw ``_econfig`` base64 string from page HTML, or ``None``."""
    if not isinstance(html, string_types):
        try:
            html = html.decode("utf-8", "replace")
        except AttributeError:
            return None
    match = _ECONFIG_RE.search(html)
    return match.group(1) if match else None


def decode(econfig):
    """
    Decode an ``_econfig`` blob into a Python ``dict``.

    Raises ``ValueError`` if the blob does not produce valid JSON. Returns a
    dict that typically contains keys like ``swarm_id``, ``stream_url``,
    ``stream_url_nop2p``, ``p2p``, ``p2p_tracker``, ``alt_domain``, ``hframes``.
    """
    if not econfig:
        raise ValueError("empty _econfig blob")

    layer1 = _b64decode_lossy(econfig)
    chunk_size = len(layer1) // _CHUNKS
    if chunk_size <= 0:
        raise ValueError("_econfig too short to split into 4 chunks")

    pieces = [None] * _CHUNKS
    for i in range(_CHUNKS):
        chunk = layer1[i * chunk_size:(i + 1) * chunk_size]
        # JS: chunk.substring(0, 3) + chunk.substring(4) -- drop index 3.
        pieces[_REORDER[i]] = _b64decode_lossy(chunk[:3] + chunk[4:])

    final = _b64decode_lossy("".join(pieces))
    try:
        return json.loads(final)
    except ValueError as exc:
        raise ValueError("decoded _econfig is not valid JSON: %s" % exc)


def extract_stream_from_html(html):
    """
    Convenience wrapper: locate the ``_econfig`` blob in ``html`` and return
    a tuple ``(stream_url, full_config_dict)`` or ``(None, None)`` if no
    blob can be decoded.

    Prefers ``stream_url_nop2p`` (Kodi cannot do the WebRTC P2P swarm anyway)
    and falls back to ``stream_url``.
    """
    raw = find_econfig(html)
    if not raw:
        return None, None
    try:
        cfg = decode(raw)
    except ValueError:
        return None, None
    url = cfg.get("stream_url_nop2p") or cfg.get("stream_url")
    return url, cfg
