# -*- coding: utf-8 -*-
import re
from resources.modules import jsunpack, client


def resolver(host):
    referer = re.sub('embed-', 'player-', host)
    OPEN = client.request(referer, referer=referer)

    key = ''
    for list in find_multiple_matches(OPEN, '_[^=]+=(\[[^\]]+\]);'):
        if len(list) == 703 or len(list) == 711:
            key = "".join(eval(list)[7:9])
            break
    if key.startswith("embed"):
        key = key[6:] + key[:6]
    matches = find_single_match(OPEN, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    data = jsunpack.unpack(matches).replace("\\", "")

    data = find_single_match(data.replace('"', "'"), "sources\s*=[^\[]*\[([^\]]+)\]")
    print data
    matches = find_multiple_matches(data, "[src|file]:'([^']+)'")
    video_urls = []
    for video_url in matches:
        _hash = find_single_match(video_url, '[A-z0-9\_\-]{40,}')
        hash = decrypt(_hash, key)
        video_url = video_url.replace(_hash, hash)
        filename = get_filename_from_url(video_url)[-4:]
        if video_url.startswith("rtmp"):
            rtmp, playpath = video_url.split("vod/", 1)
            video_url = "%svod/ playpath=%s swfUrl=%splayer6/jwplayer.flash.swf pageUrl=%s" % \
                        (rtmp, playpath, 'http://streamplay.to/', host)
            filename = "RTMP"
        elif video_url.endswith("/v.mp4"):
            video_url_flv = re.sub(r'/v.mp4', '/v.flv', video_url)
            video_urls.append(["flv [streamplay]", video_url_flv])

        video_urls.append([filename + " [streamplay]", video_url])
        video_urls.sort(key=lambda x: x[0], reverse=True)
    return video_urls    




def decrypt(h, k):
    import base64

    if len(h) % 4:
        h += "=" * (4 - len(h) % 4)
    sig = []
    h = base64.b64decode(h.replace("-", "+").replace("_", "/"))
    for c in range(len(h)):
        sig += [ord(h[c])]

    sec = []
    for c in range(len(k)):
        sec += [ord(k[c])]

    dig = range(256)
    g = 0
    v = 128
    for b in range(len(sec)):
        a = (v + (sec[b] & 15)) % 256
        c = dig[(g)]
        dig[g] = dig[a]
        dig[a] = c
        g += 1

        a = (v + (sec[b] >> 4 & 15)) % 256
        c = dig[g]
        dig[g] = dig[a]
        dig[a] = c
        g += 1

    k = 0
    q = 1
    p = 0
    n = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 3
    for a in range(v):
        b = 255 - a
        if dig[a] > dig[b]:
            c = dig[a]
            dig[a] = dig[b]
            dig[b] = c

    k = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 5
    for a in range(v):
        b = 255 - a
        if dig[a] > dig[b]:
            c = dig[a]
            dig[a] = dig[b]
            dig[b] = c

    k = 0
    for b in range(512):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c

    q = 7
    k = 0
    u = 0
    d = []
    for b in range(len(dig)):
        k = (k + q) % 256
        n = (p + dig[(n + dig[k]) % 256]) % 256
        p = (k + p + dig[n]) % 256
        c = dig[k]
        dig[k] = dig[n]
        dig[n] = c
        u = dig[(n + dig[(k + dig[(u + p) % 256]) % 256]) % 256]
        d += [u]

    c = []
    for f in range(len(d)):
        try:
            c += [(256 + (sig[f] - d[f])) % 256]
        except:
            break

    h = ""
    for s in c:
        h += chr(s)

    return h




def find_single_match(data, patron, index=0):
    try:
        matches = re.findall(patron, data, flags=re.DOTALL)
        return matches[index]
    except:
        return ""


def find_multiple_matches(text, pattern):
    return re.findall(pattern, text, re.DOTALL)


def get_filename_from_url(url):
    import urlparse
    parsed_url = urlparse.urlparse(url)
    try:
        filename = parsed_url.path
    except:
        # Si falla es porque la implementación de parsed_url no reconoce los atributos como "path"
        if len(parsed_url) >= 4:
            filename = parsed_url[2]
        else:
            filename = ""

    if "/" in filename:
        filename = filename.split("/")[-1]

    return filename


