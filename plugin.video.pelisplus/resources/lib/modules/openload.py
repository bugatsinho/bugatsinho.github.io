# -*- coding: utf-8 -*-
import cookielib, urllib2, re, urllib
from resources.lib.modules import client
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:61.0) Gecko/20100101 Firefox/61.0"


def test_video(url):
    data = client.request(url)
    if 'We’re Sorry!' in data:
        data = client.request(url.replace("/embed/", "/f/"))
        if 'We’re Sorry!' in data:
            return False, "[Openload] No file available"
    return True, ""


def get_video_openload(url):
    data = client.request(url, headers={'User-Agent': ua})
    try:
        try:
            code = re.findall('p id="[^"]+" style="">(.*?)<\/p', data, flags=re.DOTALL)[0]
        except IndexError:
            code = re.findall('<p style="" id="[^"]+">(.*?)</p>', data, flags=re.DOTALL)[0]
        _0x59ce16 = eval(re.findall('_0x59ce16=([^;]+)', data)[0].replace('parseInt', 'int'))
        _1x4bfb36 = eval(re.findall('_1x4bfb36=([^;]+)', data)[0].replace('parseInt', 'int'))
        parseInt = eval(re.findall('_0x30725e,(\(parseInt.*?)\),', data)[0].replace('parseInt', 'int'))
        link = decode(code, parseInt, _0x59ce16, _1x4bfb36)
        link = read_openload(link)
        return '%s|User-Agent=%s&Referer=%s' % (link, urllib.quote_plus(ua), urllib.quote_plus(url))
    except:
        return ''



def read_openload(url):
    default_headers = dict()
    default_headers[
        "User-Agent"] = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3163.100 Safari/537.36"
    default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
    default_headers["Accept-Charset"] = "UTF-8"
    default_headers["Accept-Encoding"] = "gzip"
    cj = cookielib.MozillaCookieJar()
    request_headers = default_headers.copy()
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    handlers = [urllib2.HTTPHandler(debuglevel=False)]
    handlers.append(NoRedirectHandler())
    handlers.append(urllib2.HTTPCookieProcessor(cj))
    opener = urllib2.build_opener(*handlers)
    req = urllib2.Request(url, None, request_headers)
    handle = opener.open(req, timeout=None)

    return handle.headers.dict.get('location')


def decode(code, parseInt, _0x59ce16, _1x4bfb36):
    import math

    _0x1bf6e5 = ''
    ke = []

    for i in range(0, len(code[0:9 * 8]), 8):
        ke.append(int(code[i:i + 8], 16))

    _0x439a49 = 0
    _0x145894 = 0

    while _0x439a49 < len(code[9 * 8:]):
        _0x5eb93a = 64
        _0x896767 = 0
        _0x1a873b = 0
        _0x3c9d8e = 0
        while True:
            if _0x439a49 + 1 >= len(code[9 * 8:]):
                _0x5eb93a = 143;

            _0x3c9d8e = int(code[9 * 8 + _0x439a49:9 * 8 + _0x439a49 + 2], 16)
            _0x439a49 += 2

            if _0x1a873b < 6 * 5:
                _0x332549 = _0x3c9d8e & 63
                _0x896767 += _0x332549 << _0x1a873b
            else:
                _0x332549 = _0x3c9d8e & 63
                _0x896767 += int(_0x332549 * math.pow(2, _0x1a873b))

            _0x1a873b += 6
            if not _0x3c9d8e >= _0x5eb93a: break

        # _0x30725e = _0x896767 ^ ke[_0x145894 % 9] ^ _0x59ce16 ^ parseInt ^ _1x4bfb36
        _0x30725e = _0x896767 ^ ke[_0x145894 % 9] ^ parseInt ^ _1x4bfb36
        _0x2de433 = _0x5eb93a * 2 + 127

        for i in range(4):
            _0x3fa834 = chr(((_0x30725e & _0x2de433) >> (9 * 8 / 9) * i) - 1)
            if _0x3fa834 != '$':
                _0x1bf6e5 += _0x3fa834
            _0x2de433 = (_0x2de433 << (9 * 8 / 9))

        _0x145894 += 1


    url = "https://openload.co/stream/%s?mime=true" % _0x1bf6e5
    return url


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

