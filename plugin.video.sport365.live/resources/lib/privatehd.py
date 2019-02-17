# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import mydecode

BASEURL='http://privatehd.pw'
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

url='http://privatehd.pw/tv2/ace/pol/tvn24.php'     
def getChannelVideo(url='http://www.typertv.com.pl/tvn'):
    video=[]
    if 'typertv' in url:
        content = getUrl(url)
        iframe = re.compile('<iframe(.*?)</iframe>').findall(content)
        if iframe:
            src = re.compile('src="(.*?)"',re.IGNORECASE).findall(iframe[0])
            if src:
                data = getUrl(src[0])
                if file :
                    rtmp = file[0].split('&')[0]
                    href = rtmp + ' swfUrl=%s live=1 timeout=10 pageUrl=%s'%(src[0],url)
                    video=[{'url':href}]
                else:
                    vido_url = mydecode.decode(url,s_hex)
                    if vido_url: video=[{'url':vido_url}]
    return video

