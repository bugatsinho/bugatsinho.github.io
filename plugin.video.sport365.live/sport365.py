# -*- coding: utf-8 -*-
'''
Credits to original dev GalAnonim!
╭━━╮╱╱╱╱╱╱╱╱╱╱╭╮╱╱╱╱╱╱╱╭╮
┃╭╮┃╱╱╱╱╱╱╱╱╱╭╯╰╮╱╱╱╱╱╱┃┃
┃╰╯╰┳╮╭┳━━┳━━╋╮╭╋━━┳┳━╮┃╰━┳━━╮
┃╭━╮┃┃┃┃╭╮┃╭╮┃┃┃┃━━╋┫╭╮┫╭╮┃╭╮┃
┃╰━╯┃╰╯┃╰╯┃╭╮┃┃╰╋━━┃┃┃┃┃┃┃┃╰╯┃
╰━━━┻━━┻━╮┣╯╰╯╰━┻━━┻┻╯╰┻╯╰┻━━╯
╱╱╱╱╱╱╱╭━╯┃
╱╱╱╱╱╱╱╰━━╯
'''


import urllib2
import urllib
import re
import time
import json
import base64
import cookielib
import requests
import xbmc
from resources.lib import client, jscrypto, pyaes_new as pyAES

UA = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0"
# UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
# UA = 'Mozilla/5.0 (Linux; Android 8.0; Nexus 6P Build/OPP3.170518.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.121 Mobile Safari/537.36'
# UA = 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'


def getUrl(url, data=None, header={}, usecookies=True):
    if usecookies:
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    if not header:
        header = {'User-Agent': UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    return link


def getUrlc(url, data=None, header={}, usecookies=True):
    cj = cookielib.LWPCookieJar()
    if usecookies:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    if not header:
        header = {'User-Agent': UA}
    req = urllib2.Request(url, data, headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    c = ''.join(['%s=%s' % (c.name, c.value) for c in cj]) if cj else ''
    return link, c


def getChannels(addheader=False, BASEURL='http://www.sport365.live/en'):

    from datetime import datetime
    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) -
                  datetime.utcfromtimestamp(ts)).total_seconds()

    minutes = int(utc_offset) / 60
    url = BASEURL + '/events/-/1/-/-/' + str(minutes)

    content = getUrl(url)
    content = re.sub(r"\n|\r|\t|\s{2}", "", content)
    # regex = '''<tr\s+style=["']background:\s+#EEEBDA;["']\s+title=["']Live['"]\s+onClick=.*?&quot;(http:\/\/dpaste.com\/.*?.txt).*?img\s+alt="([^"]+).*?>(\d+:\d+)<'''
    # regex = 'onclick=.*?"event_\w+"\,\s*"(.+?)"\,.*?<td rowspan="2".*?src="([^"]+)".*?<td rowspan="2".*?>(\d+:\d+)<.*?<td.*?>([^<]+)<.*?<td.*?>(.*?)/td>.*?<tr.*?<td colspan="2".*?>([^<]+)</td><[^>]+>([^<]*)'
    regex = 'onClick=.*?"event_(\w+)".*?<td rowspan=2.*?src="([^"]+)".*?<td rowspan=2.*?>(\d+:\d+)<.*?<td.*?>([^<]+)<.*?<td.*?>(.*?)/td>.*?<tr.*?<td colspan=2.*?>([^<]+)</td><[^>]+>([^<]*)<'
    streams = re.findall(regex, content, re.DOTALL)
    out = []
    for event, color, hora, title, quality, league, lang in streams:
        online = '[COLOR lightgreen]•[/COLOR]' if '-green-' in color else '[COLOR red]*[/COLOR]'
        url = BASEURL + '/links/{}/1'.format(event)
        quality = re.sub('<.+?>', '', quality).split('&')[0] if 'nbsp' in quality else 'SD'
        qualang = '[COLOR gold]%s-%s[/COLOR]' % (lang, quality)
        title = '%s%s: [COLOR blue]%s[/COLOR] %s, %s' % (online, hora, title, qualang, league)
        code = quality + lang
        out.append({"title": title, "url": url, "code": code})
    # xbmc.log('HTMLCODE-OUT: %s' % str(out), level=xbmc.LOGNOTICE)
    return out


def getStreams(url):
    try:
        from resources.lib import cache

        past = 'U2FsdGVkX19q9T+lFjzxG4a0je4b6tI1Uc3HUVnoWBiD/Vw59IpxZ+cJuwDsjszZPsVkradgfXb0sxZVxY2J1h96IuNIpyAHyNS1vUKYpcU='
        # xbmc.log('PAST IS: %s' % past, level=xbmc.LOGNOTICE)
        pastes = cache.get(getUrl, 3, jscrypto.decode(past, base64.b64decode('SXMgT25seSBPbmUgQnVnYXRzaW5obw==')))
        # xbmc.log('PASTES IS: %s' % pastes, level=xbmc.LOGNOTICE)
        ret = xor2(base64.b64decode(pastes), 'sly6B89wqxt2N')
        ret = json.loads(ret)
        info, key = ret['i7'], ret['k7']
    except BaseException:
        raise Exception()
    xbmc.log('RET IS: %s' % str(ret), level=xbmc.LOGNOTICE)

    myurl = url
    content = getUrl(myurl)
    sources = re.findall(r'''onClick=['"]\w+\(\'(\w+)\'''', content, re.DOTALL)
    out = []

    for i, s in enumerate(set(sources)):
        decrypter = pyAES.Decrypter(pyAES.AESModeOfOperationECB(key))
        data = decrypter.feed(s.strip().decode('hex'))
        data += decrypter.feed()
        s = data.decode('hex')
        title = 'Link {}'.format(i + 1)
        out.append({"title": title, "tvid": title, "url": '{}@{}@{}'.format(s, info, key), "refurl": url})
    # xbmc.log('HTMLSTREAMS-OUT: %s' % str(out), level=xbmc.LOGNOTICE)
    return out


def getChannelVideo(item):
    item = eval(item)
    myurl, info, key = item['url'].split('@')
    s = requests.Session()
    header = {'User-Agent': UA,
              'Referer': myurl}
    content = s.get(myurl, headers=header)

    links = client.parseDOM(content.text, 'iframe', ret='src')
    link = [i for i in links if '.pw' in i][0]
    # xbmc.log('@#@DEROT-LINK: %s' % link, xbmc.LOGNOTICE)
    if link:
        header['Referer'] = item.get('url')
        # link = re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), link[0])
        data = requests.get(link).text
        f = re.compile(r'.*?name="f"\s*value=["\']([^"\']+)["\']').findall(data)
        d = re.compile(r'.*?name="d"\s*value=["\']([^"\']+)["\']').findall(data)
        r = re.compile(r'.*?name="r"\s*value=["\']([^"\']+)["\']').findall(data)
        # b = re.compile('.*?name="b"\s*value=["\']([^"\']+)["\']').findall(data)
        action = re.compile(r'[\'"]action[\'"][,\s]*[\'"](http.*?)[\'"]').findall(data)
        srcs = re.compile(r'src=[\'"](.*?)[\'"]').findall(data)
        if f and r and d and action:
            header['Referer'] = link
            # payload = urllib.urlencode({'b': b[0], 'd': d[0], 'f': f[0], 'r': r[0]})
            payload = urllib.urlencode({'f': f[0], 'd': d[0], 'r': r[0]})
            data2, c = getUrlc(action[0], payload, header=header, usecookies=True)
            # xbmc.log('@#@DEROT-DATA2: %s' % data2, xbmc.LOGNOTICE)
            script = re.findall(r'src="(http://s1.medianetworkinternational.com/js/\w+.js\?.+?)">', data2, re.DOTALL)[0]
            # xbmc.log('@#@DEROT-script: %s' % script, xbmc.LOGNOTICE)
            html = getUrl(script, header=header)
            xset = re.findall(r'var\s+xset=(\[[^\]]+\]);', html)[0]
            # xbmc.log('@#@DEROT-XSET: %s' % xset, xbmc.LOGNOTICE)
            hset = re.findall(r'var\s+hset=(\[[^\]]+\]);', html)[0]
            # xbmc.log('@#@DEROT-HSET: %s' % hset, xbmc.LOGNOTICE)
            try:
                #######ads banners#########
                bheaders = header
                bheaders['Referer'] = action[0]
                banner = re.findall(r'<script\s*src=[\'"](.+?)[\'"]', data2)[-1]
                # xbmc.log('@#@BANNER-LINK: %s' % banner, xbmc.LOGNOTICE)
                bsrc = s.get(banner, headers=bheaders).content
                # xbmc.log('@#@BANNER-DATA: %s' % bsrc, xbmc.LOGNOTICE)
                banner = re.findall(r"url:'([^']+)", bsrc)[0]
                # xbmc.log('@#@BANNER-LINK2: %s' % banner, xbmc.LOGNOTICE)
                bsrc = s.get(banner, headers=bheaders).content
                # xbmc.log('@#@BANNER-DATA2: %s' % bsrc, xbmc.LOGNOTICE)
                bheaders['Referer'] = banner
                banner = re.findall(r"img\s+src='([^']+)", bsrc)[0]
                banner = banner.replace('amp;', '')
                # xbmc.log('@#@BANNER-LINK3: %s' % banner, xbmc.LOGNOTICE)
                bsrc = s.get(banner).status_code
                #     ###########################
            except BaseException:
                pass
            src = re.findall(r"function\(\)\s*{\s*[a-z0-9]{43}\(.*?,.*?,\s*'([^']+)'", data2)[0]
            # xbmc.log('@#@FUNCTION: %s' % src, xbmc.LOGNOTICE)
            s = derot(xset, hset, src)
            key = key[:32]

            decrypter = pyAES.Decrypter(pyAES.AESModeOfOperationECB(key))
            data = decrypter.feed(s.decode('hex').strip())
            data += decrypter.feed()
            fstream = data.decode('hex')
            # fstream = aes.AESModeOfOperationCBC(key, info).decrypt(s.decode('hex'))
            # xbmc.log('getStreams-Final-data: %s' % fstream, level=xbmc.LOGNOTICE)
            # fstream = re.findall('([a-f0-9]+)', fstream)[0].decode('hex')
            # xbmc.log('@#@DAAAATAAA-2---LINK: %s' % fstream, xbmc.LOGNOTICE)
            # enc_data = json.loads(base64.b64decode(link[0]))
            # # ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
            # src = jscrypto.decode(enc_data["ct"], item['key'], enc_data["s"].decode("hex"))
            # src = src.replace('"','').replace('\\', '').encode('utf-8')

            if fstream.startswith('http'):
                href = fstream
                return href, srcs[-1], header, item['title'], myurl

    return ''


def derot(xset, hset, src):
    xset = eval(xset)
    hset = eval(hset)

    import string
    o = ''
    u = ''
    il = 0
    for first in hset:
        u += first
        o += xset[il]
        il += 1
    rot13 = string.maketrans(o, u)
    link = string.translate(src, rot13)
    xbmc.log('@#@DEROT-LINK: %s' % link, xbmc.LOGNOTICE)
    return link


def xor2(data, key):
    from itertools import izip, cycle
    xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(data, cycle(key)))
    return xored


def getUrlrh(url, data=None, header={}, usecookies=True):
    cj = cookielib.LWPCookieJar()
    if usecookies:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    if not header:
        header = {'User-Agent':UA}
    rh={}
    req = urllib2.Request(url, data, headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        for k in response.headers.keys(): rh[k]=response.headers[k]
        link = response.read()
        response.close()
    except:
        link=''
    c = ''.join(['%s=%s' % (c.name, c.value) for c in cj]) if cj else ''
    return link,rh
