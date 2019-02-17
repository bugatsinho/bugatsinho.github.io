# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import mydecode

BASEURL='http://polon-tv.blogspot.com/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def getUrl(url,data=None,header={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
def getChannels(addheader=False):
    content = getUrl(BASEURL)
    out=[]
    chs = re.compile('<li><a href=["\'](.*?)["\']>(.*?)</a></li>').findall(content)
    for href,title in chs:
        out.append({'title':title.strip(),'tvid':title.strip(),'img':'','url':href,'group':'','urlepg':''})
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (psa-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})        
    return out
     
def getChannelVideo(url='http://polon-tv.blogspot.com/p/tvn.html'):
    #rtmp://50.7.115.2/stream/<playpath>2111L <swfUrl>http://p.jwpcdn.com/6/12/jwplayer.flash.swf <pageUrl>http://filterup.blogspot.com/p/tp2.html
    video=[]
    if 'blogspot' in url:
        content = getUrl(url)
        s_hex = re.compile('document.write\(unescape\(\'(.*?)\'\)').findall(content)
        s_hex = urllib.unquote(s_hex[0]) if s_hex else ''
        src = re.compile('src="(.*?)"',re.IGNORECASE).findall(s_hex)
        if src:
            data = getUrl(src[0])
            rtmp = re.compile('{"file":"(.*?)"').findall(data)
            swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            pageUrl = re.compile('<meta content=["\'](.*?)["\'] property=["\']og:url["\']/>').findall(data)
            if rtmp and pageUrl:
                href = rtmp[0]+ ' swfUrl=%s pageUrl=%s live=1 timeout=10'%(swfUrl,pageUrl[0])
                video=[{'url':href}]
            else:
                iframe = re.compile('<iframe(.*?)</iframe>',re.DOTALL|re.IGNORECASE).findall(data)
                if iframe:
                    connection = re.compile('netConnection=(rtmp.*?)"').findall(iframe[0])
                    if connection:
                        source = re.compile('source=([^&]+)').findall(connection[0])
                        if source:
                            href = source[0] + ' swfUrl=%s pageUrl=%s live=1 timeout=10'%(swfUrl,pageUrl[0])
                            video=[{'url':href}]
                    else:
                        href = mydecode.decode(pageUrl[0],iframe[0])
                        if href : video=[{'url':href}]
    return video
    
      