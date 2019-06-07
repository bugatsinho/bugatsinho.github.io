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

import sys
import traceback
import urllib2
import urllib
import re
import time
import json
import base64
import cookielib
import requests
import magic_aes
import xbmc


UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'


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


def getChannels(addheader=False, BASEURL='http://www.sport365.sx/en'):
    ret = ''
    content = getUrl(BASEURL + '/main')
    wrapper = re.compile('(http[^"]+/advertisement.js\?\d+)').findall(content)
    wrappers = re.compile('<script type="text/javascript" src="(http://s1.medianetworkinternational.com/js/\w+.js)"').findall(content)
    for wrapper in wrappers:
        wc = getUrl(wrapper)
        content=JsUnwiser().unwiseAll(wc)
        ret = content
        ret = re.compile('return "(.*?)"').findall(content)
        if ret:
            ret = ret[0]
            print 'key %s'%ret
            break

    from datetime import datetime
    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) -
                  datetime.utcfromtimestamp(ts)).total_seconds()

    minutes = int(utc_offset) / 60
    url = BASEURL + '/events/-/1/-/-/' + str(minutes)

    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('onClick=', content)]
    ids.append( (-1,-1) )
    out=[]
   
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        links=re.compile('\("([^"]+)", "([^"]+)", "[^"]+", 1\)').findall(subset)
        title2=re.compile('<img alt="(.*?)"').findall(subset)
        t=re.compile('>([^<]+)<').findall(subset)
        online = '[COLOR lightgreen]•[/COLOR]' if subset.find('/images/types/dot-green-big.png')>0 else '[COLOR red]*[/COLOR]'
        if links and title2:
            event,urlenc=links[0]
            url = BASEURL + '/links/%s/1@%s'%(event.split('_')[-1],ret)
            etime,title1= t[:2]
            lang = t[-1]
            quality = t[-2].replace('&nbsp;', '') if 'nbsp' in t[-2] else 'SD'
            qualang = '[COLOR gold]%s-%s[/COLOR]' % (lang, quality)
            title = '%s%s: [COLOR blue]%s[/COLOR] %s, %s' % (online, etime, title1, qualang, title2[0])
            code = quality + lang
            out.append({"title": title, "url": url, "code": code})
    return out


def getStreams(url):
    myurl, ret = url.split('@')
    content = getUrl(myurl)
    sources=re.compile('<span id=["\']span_link_links[\'"] onClick="\w+\(\'(.*?)\'').findall(content)
    out = []
    for i, s in enumerate(set(sources)):
        enc_data=json.loads(base64.b64decode(s))
        ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
        src= magic_aes.decrypt(ret, base64.b64encode(ciphertext))
        src=src.strip('"').replace('\\','')
        title = 'Link %d' % (i+1)
        out.append({"title": title, "tvid": title, "key": ret, "url": src, "refurl": myurl})
    return out


def getChannelVideo(item):
    import xbmc
    #xbmc.log('@#@CHANNEL-VIDEO-ITEM: %s' % item, xbmc.LOGNOTICE)
    s = requests.Session()
    header = {'User-Agent': UA,
              'Referer': item.get('url')}
    content = s.get(item['url'], headers=header).content
    # import uuid
    # hash = uuid.uuid4().hex
    # url = re.findall(r'location.replace\(\'([^\']+)', content)[0]
    # uri = url + hash
    # content = s.get(uri, headers=header).content
    links = re.compile('(http://www.[^\.]+.pw/(?!&#)[^"]+)',
                       re.IGNORECASE + re.DOTALL + re.MULTILINE + re.UNICODE).findall(content)
    link = [x for x in links if '&#' in x]
    if link:
        link = re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), link[0])
        data = s.get(link, headers=header).content
        #xbmc.log('@#@CHANNEL-VIDEO-DATA: %s' % data, xbmc.LOGNOTICE)
        f = re.compile('.*?name="f"\s*value=["\']([^"\']+)["\']').findall(data)
        d = re.compile('.*?name="d"\s*value=["\']([^"\']+)["\']').findall(data)
        r = re.compile('.*?name="r"\s*value=["\']([^"\']+)["\']').findall(data)
        # b = re.compile('.*?name="b"\s*value=["\']([^"\']+)["\']').findall(data)
        action = re.compile('[\'"]action[\'"][,\s]*[\'"](http.*?)[\'"]').findall(data)
        srcs = re.compile('src=[\'"](.*?)[\'"]').findall(data)
        if f and r and d and action:
            # payload = urllib.urlencode({'b': b[0], 'd': d[0], 'f': f[0], 'r': r[0]})
            payload = urllib.urlencode({'f': f[0], 'd': d[0], 'r': r[0]})
            data2, c = getUrlc(action[0], payload, header=header, usecookies=True)
            try:
                #######ads banners#########
                bheaders = header
                bheaders['Referer'] = action[0]
                banner = re.findall(r'<script\s*src=[\'"](.+?)[\'"]', data2)[-1]
                #xbmc.log('@#@BANNER-LINK: %s' % banner, xbmc.LOGNOTICE)
                bsrc = s.get(banner, headers=bheaders).content
                #xbmc.log('@#@BANNER-DATA: %s' % bsrc, xbmc.LOGNOTICE)
                banner = re.findall(r"url:'([^']+)", bsrc)[0]
                #xbmc.log('@#@BANNER-LINK2: %s' % banner, xbmc.LOGNOTICE)
                bsrc = s.get(banner, headers=bheaders).content
                #xbmc.log('@#@BANNER-DATA2: %s' % bsrc, xbmc.LOGNOTICE)
                bheaders['Referer'] = banner
                banner = re.findall(r'window.location.replace\("([^"]+)"\);\s*}\)<\/script><div', bsrc)[0]
                banner = urllib.quote(banner, ':/()!@#$%^&;><?')
                #xbmc.log('@#@BANNER-LINK3: %s' % bsrc, xbmc.LOGNOTICE)
                bsrc = s.get(banner).status_code
                ###########################
            except BaseException:
                pass
            link = re.compile('\([\'"][^"\']+[\'"], [\'"][^"\']+[\'"], [\'"]([^"\']+)[\'"], 1\)').findall(data2)
            enc_data = json.loads(base64.b64decode(link[0]))
            ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
            src = magic_aes.decrypt(item['key'],base64.b64encode(ciphertext))
            src = src.replace('"','').replace('\\','').encode('utf-8')
            a, c = getUrlc(srcs[-1], header=header, usecookies=True) if srcs else '', ''
            a, c = getUrlc(src, header=header, usecookies=True)
            # print a
            url_head = '|User-Agent={0}&Referer={1}'.format(urllib.quote(UA), urllib.quote('http://h5.adshell.net/peer5'))

            if src.startswith('http'):
                href = src + url_head
                # print href
                return href, srcs[-1], header, item['title']
            else:
                href = magic_aes.decode_hls(src)
                if href:
                    href += url_head
                    return href, srcs[-1], header, item['title']
    return ''

# getUrlrh(src)

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



class JsUnwiser:
    def unwiseAll(self, data):
        try:
            in_data=data
            sPattern = 'eval\\(function\\(w,i,s,e\\).*?}\\((.*?)\\)'
            wise_data=re.compile(sPattern).findall(in_data)
            for wise_val in wise_data:
                unpack_val=self.unwise(wise_val)
                #print '\nunpack_val',unpack_val
                in_data=in_data.replace(wise_val,unpack_val)
            return re.sub(re.compile("eval\(function\(w,i,s,e\).*?join\(''\);}", re.DOTALL), "", in_data, count=1)
        except: 
            traceback.print_exc(file=sys.stdout)
            return data
        
    def containsWise(self, data):
        return 'w,i,s,e' in data
        
    def unwise(self, sJavascript):
        #print 'sJavascript',sJavascript
        page_value=""
        try:        
            ss = "w,i,s,e=("+sJavascript+')'
            exec (ss)
            page_value=self.__unpack(w,i,s,e)
        except: traceback.print_exc(file=sys.stdout)
        return page_value
        
    def __unpack( self, w, i, s, e):
        lIll = 0;
        ll1I = 0;
        Il1l = 0;
        ll1l = [];
        l1lI = [];
        while True:
            if (lIll < 5):
                l1lI.append(w[lIll])
            elif (lIll < len(w)):
                ll1l.append(w[lIll]);
            lIll+=1;
            if (ll1I < 5):
                l1lI.append(i[ll1I])
            elif (ll1I < len(i)):
                ll1l.append(i[ll1I])
            ll1I+=1;
            if (Il1l < 5):
                l1lI.append(s[Il1l])
            elif (Il1l < len(s)):
                ll1l.append(s[Il1l]);
            Il1l+=1;
            if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
                break;
            
        lI1l = ''.join(ll1l)#.join('');
        I1lI = ''.join(l1lI)#.join('');
        ll1I = 0;
        l1ll = [];
        for lIll in range(0,len(ll1l),2):
            #print 'array i',lIll,len(ll1l)
            ll11 = -1;
            if ( ord(I1lI[ll1I]) % 2):
                ll11 = 1;
            #print 'val is ', lI1l[lIll: lIll+2]
            l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11));
            ll1I+=1;
            if (ll1I >= len(l1lI)):
                ll1I = 0;
        ret=''.join(l1ll)
        if 'eval(function(w,i,s,e)' in ret:
            ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0] 
            return self.unwise(ret)
        else:
            return ret
