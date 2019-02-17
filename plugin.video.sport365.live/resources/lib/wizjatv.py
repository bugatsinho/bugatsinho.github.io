# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time,json

BASEURL='http://wizja.tv/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

fix={
'Alekino':'ale kino+',
'Animal':'Animal Planet',
'Canal':'Canal+',
'Canaldiscovery':'Canal+ Discovery HD',
'Canalfamily':'Canal+ Family',
'Canalfilm':'Canal+ Film',
'Canalsport':'Canal+ Sport',
'Canalsport2':'Canal+ Sport 2',
'Cartoon':'Cartoon Network',
'Cinemax':'Cinemax',
'Comedy':'Comedy Central',
'Discovery':'Discovery Channel',
'Discoveryhistoria':'Discovery Historia',
'Discoveryscience':'Discovery Science',
'Disneyjunior':'Disney Junior',
'Eleven':'Eleven',
'Elevenextra':'Eleven Extra',
'Elevensports':'Eleven Sports',
'Eska':'Eska TV',
'Eurosport1':'Eurosport',
'Eurosport2':'Eurosport 2',
'Filmbox':'Filmbox',
'Hbo':'HBO',
'Hbo2':'HBO2',
'Hbo3':'HBO3',
'History':'History',
'Kinopolska':'Kino Polska',
'Mtv':'MTV Polska',
'Natgeo':'National Geographic Channel',
'Natgeowild':'Nat Geo Wild',
'Nsport':'nSport',
'Polsat':'Polsat',
'Polsatnews':'Polsat News',
'Polsatplay':'Polsat Play',
'Polsatsport':'Polsat Sport',
'Polsatsportextra':'Polsat Sport Extra',
'Polsatsportnews':'Polsat Sport News',
'Tlc':'TLC',
'Travel':'Travel Channel',
'Tv4':'TV 4',
'Tvn':'TVN',
'Tvn24':'TVN 24',
'Tvn7':'TVN 7',
'Tvnstyle':'TVN Style',
'Tvnturbo':'TVN Turbo',
'Tvp1':'TVP 1',
'Tvp2':'TVP 2',
'Tvpseriale':'TVP Seriale',
'Tvpsport':'TVP Sport',
'Tvpuls':'TV Puls',
'Viva':'VIVA Polska',
}


def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one
    
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
    url='http://wizja.tv/'
    content = getUrl(url)
    channels=re.compile('<a href="(watch.*?)"><img src="(.*?)"></a>').findall(content)
    out=[]
    #one=match[0]
    for ch in channels:
        t = ch[1].split('/')[-1].split('.')[0].title()
        i = BASEURL + ch[1]
        h = BASEURL + ch[0]
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    out = sorted(out, key=lambda k: k['title'],reverse=False)    
    if out and addheader:
        t='[COLOR yellow]Updated: %s (wizja.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://wizja.tv/','group':'','urlepg':''})
    return out
    
#rtmp://185.66.141.231:1875/haYequChasp4T3eT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6<playpath>pHe7repheT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6 <swfUrl>http://wizja.tv/player/StrobeMediaPlayback_v2.swf <pageUrl>http://wizja.tv/player.php?target=ams_nl1&ch=37
def get_Cookies(url,params=None,header={}):
    req = urllib2.Request(url,params,headers=header)
    sock=urllib2.urlopen(req)
    cookies=sock.info()['Set-Cookie']
    sock.close()
    return cookies

def get_cookie_value(cookies='',value='sesssid'):
    idx1=cookies.find(value+'=')
    if idx1==-1:
        return''
    else:
        idx2=cookies.find(';',idx1+1)
    return cookies[idx1:idx2]    

def getChannelVideo(url='http://wizja.tv/watch.php?id=47'):
    video=[]
    if 'wizja.tv' in url:
        
        id = re.search('id=(.*?)$',url).group(1)
        
        posterurl='http://wizja.tv/porter.php?ch=%s'%id
        playerulr='http://wizja.tv/player.php?target=ams_nl2&ch=%s'%id
        
        header={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                'Host':'wizja.tv',
                'Referer':url,
                'Cache-Control':'max-age=0',
                "Connection":"keep-alive",
                'Upgrade-Insecure-Requests':'1',
                }

        c=get_Cookies(url,header=header)
        
        cookie=' '.join(['%s;'%get_cookie_value(c,s) for s in ['__cfduid','PHPSESSID']])
        header['Cookie']=cookie
        data = getUrl(posterurl,header=header)

        mylink = re.compile('src: "(.*?)"').findall(data)
        if len(mylink)>0:
            rtmp2 = urllib.unquote(mylink[0]).decode('utf8')
            rtmp1 = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(rtmp2)
            vido_url = 'rtmp://' + rtmp1[0][0] + '/' + rtmp1[0][1] +'/' +rtmp1[0][2]+ '?'+ rtmp1[0][3]+ ' app=' + rtmp1[0][1] + '?' +rtmp1[0][3]+' swfVfy=1 flashver=WIN\\2020,0,0,306 timeout=10 swfUrl=http://wizja.tv/player/StrobeMediaPlayback.swf live=true pageUrl='+url
            video=[{'url':vido_url}]
        else:
            video=[{'msg':'UWAGA! Brak Premium! limit oglądania: max. 3 godziny - dostęp tylko do serwerów standard'}]
    return video


def test():
    out = getChannels()
    for o in out:
        print o.get('title')