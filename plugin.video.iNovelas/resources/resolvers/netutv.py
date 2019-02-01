# -*- coding: utf-8 -*-

import re
import urllib
import xbmc
import random
from resources.modules import client, jsontools, jsUnwiser, jsunpack


def get_video_url(page_url, referer):
    headers = {'User-Agent': client.agent(),
               'Referer': referer}
    if "hash=" in page_url:
        data = urllib.unquote(client.request(page_url))
        id_video = find_single_match(data, "vid':'([^']+)'")
        page_url = "http://hqq.watch/player/embed_player.php?vid=%s" % id_video
    else:
        page_url = page_url.replace("/watch_video.php?v=", "/player/embed_player.php?vid=")
    page_url = page_url.replace('https://netu.tv/', 'http://hqq.watch/')
    page_url = page_url.replace('https://waaw.tv/', 'http://hqq.watch/')

    data = client.request(page_url, headers=headers)

    js_wise = find_single_match(data, "<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>")
    data = jswise(js_wise).replace("\\", "")
    # ~ logger.debug(data)

    alea = str(random.random())[2:]
    data_ip = client.request('http://hqq.watch/player/ip.php?type=json&rand=%s' % alea)
    # ~ logger.debug(data_ip)
    json_data_ip = jsontools.load(data_ip)

    url = find_single_match(data, 'self\.location\.replace\("([^)]+)\)')
    url = url.replace('"+rand+"', alea)
    url = url.replace('"+data.ip+"', json_data_ip['ip'])
    url = url.replace('"+need_captcha+"', '0')  # json_data_ip['need_captcha'])
    url = url.replace('"+token', '')
    # ~ logger.debug(url)

    headers = {
        "User-Agent": 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.127 Large Screen Safari/533.4 GoogleTV/162671'}
    data = client.request('http://hqq.watch' + url, headers=headers)
    # ~ logger.debug(data)

    codigo_js = find_multiple_matches(data, '<script>document.write\(unescape\("([^"]+)')
    # ~ logger.debug(codigo_js)

    js_aux = urllib.unquote(codigo_js[0])
    at = find_single_match(js_aux, 'var at = "([^"]+)')

    js_aux = urllib.unquote(codigo_js[1])
    var_link_1 = find_single_match(js_aux, '&link_1=\\"\+encodeURIComponent\(([^)]+)')
    var_server_2 = find_single_match(js_aux, '&server_2=\\"\+encodeURIComponent\(([^)]+)')
    vid = find_single_match(js_aux, '&vid=\\"\+encodeURIComponent\(\\"([^"]+)')
    ext = '.mp4.m3u8'
    # ~ logger.debug('%s %s %s %s' % (at, var_link_1, var_server_2, vid))

    js_wise = find_single_match(data, "<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>")
    data = jswise(js_wise).replace("\\", "")
    # ~ logger.debug(data)

    variables = find_multiple_matches(data, 'var ([a-zA-Z0-9]+) = "([^"]+)";')
    # ~ logger.debug(variables)

    for nombre, valor in variables:
        # ~ logger.debug('%s %s' % (nombre, valor))
        if nombre == var_link_1:
            link_1 = valor
        if nombre == var_server_2:
            server_2 = valor

    link_m3u8 = 'http://hqq.watch/player/get_md5.php?ver=2&at=%s&adb=0&b=1&link_1=%s&server_2=%s&vid=%s&ext=%s' % (
        at, link_1, server_2, vid, ext)
    # ~ logger.debug(link_m3u8)


    return link_m3u8


## Obtener la url del m3u8
def tb(b_m3u8_2):
    j = 0
    s2 = ""
    while j < len(b_m3u8_2):
        s2 += "\\u0" + b_m3u8_2[j:(j + 3)]
        j += 3

    return s2.decode('unicode-escape').encode('ASCII', 'ignore')


## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------

def jswise(wise):
    ## js2python
    def js_wise(wise):

        w, i, s, e = wise

        v0 = 0;
        v1 = 0;
        v2 = 0
        v3 = [];
        v4 = []

        while True:
            if v0 < 5:
                v4.append(w[v0])
            elif v0 < len(w):
                v3.append(w[v0])
            v0 += 1
            if v1 < 5:
                v4.append(i[v1])
            elif v1 < len(i):
                v3.append(i[v1])
            v1 += 1
            if v2 < 5:
                v4.append(s[v2])
            elif v2 < len(s):
                v3.append(s[v2])
            v2 += 1
            if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break

        v5 = "".join(v3);
        v6 = "".join(v4)
        v1 = 0
        v7 = []

        for v0 in range(0, len(v3), 2):
            v8 = -1
            if ord(v6[v1]) % 2: v8 = 1
            v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
            v1 += 1
            if v1 >= len(v4): v1 = 0
        return "".join(v7)

    ## loop2unobfuscated
    while True:
        wise = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", wise, re.DOTALL)
        if not wise: break
        ret = wise = js_wise(wise.groups())
    return ret


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

