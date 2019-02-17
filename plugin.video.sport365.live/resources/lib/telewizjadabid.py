# -*- coding: utf-8 -*-

import urllib2,urllib
import re,os,time
import cookielib

BASEURL='http://telewizjada.bid'
COOKIEFILE=''
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
TIMEOUT = 10

fix={
'TVP1':'TVP 1',
'TVP2':'TVP 2',
'TVP HD':'TVP HD',
'Polsat':'Polsat',
'Polsat 2':'Polsat 2',
'Polsat Sport':'Polsat Sport',
'TVN':'TVN',
'TVN 24':'TVN 24',
'CANAL SPORT HD':'Canal+ Sport',
'Discovery Channel PL':'Discovery Channel',
'CANALFILMD':'Canal+ Film',
'HBO HD':'HBO',
'COMEDY CENTRAL':'Comedy Central',
'CANA&#x141;&#x2B;':'Canal+',
'NATGEOCHANELL HD':'National Geographic Channel',
'FILMBOX HD':'Filmbox',
'Discovery Science':'Discovery Science',
'Eurosport 1HD':'Eurosport',
'HBO 2':'HBO2',
'Investigation Discovery':'Investigation Discovery',
'Kinopolska':'Kino Polska',
'TV plus':'TV Puls',
'TLC':'TLC',
'TVN 7':'TVN 7',
    }

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one



def getUrl(url,data=None,header={},setCookies=True):
    cookie=''
    cj=[]
    #if COOKIEFILE and setCookies:
    if setCookies:
        cj = cookielib.LWPCookieJar()
        #cj.load(COOKIEFILE)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
        cookie = ''.join(['%s=%s;'%(c.name, c.value) for c in cj])
        # if COOKIEFILE and setCookies:
        #     dataPath=os.path.dirname(COOKIEFILE)
        #     if not os.path.exists(dataPath): os.makedirs(dataPath)
        #     if cj: cj.save(COOKIEFILE, ignore_discard = True) 
            
    except urllib2.HTTPError as e:
        link = ''
    return link,cookie



def getChannels(addheader=False):     
    content,cookie=getUrl(BASEURL+'/live')
    out=[]
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="channels" ', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)"',re.DOTALL).findall(subset)
        img = re.compile('<img src="(.*?)"',re.DOTALL).findall(subset)  
        title = re.compile('alt="(.*?)"',re.DOTALL).findall(subset)  
        if href and title and img:
            t= title[0].replace('Watch ','').strip()
            one = { 'id': '', 
                'title': t,
                'tvid': t,
                'img': BASEURL + img[0],
                'group': '',
                'url': href[0]+'?%s'%cookie,
                'urlepg' :'',
                'epgname':'',
                'cookie': cookie}
        one_fix = fixForEPG(one)
        print one_fix.get('title')
        out.append(one_fix)

    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (tele-wizja)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})        
    return out


def cookieString(COOKIEFILE):
    sc=''
    if os.path.isfile(COOKIEFILE):
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        sc+=''.join(['%s=%s;'%(c.name, c.value) for c in cj])
    return sc

def getChannelVideo(url='/live/tvn7?__cfduid=db727ed1b540ce099a9f931f972546bbb1477336595;'):
    video=[]
    url,cookie=url.split('?') if '?'in url else (url,'')
    header ={'User-Agent':UA,
             'X-Requested-With':'XMLHttpRequest',
             'Referer':BASEURL+url,
             'Cookie':cookie,
             }
    dataurl=BASEURL+'/data/%s'%url.split('/')[-1]
    content,c = getUrl(dataurl,header=header)
    vido_url = re.compile('"url":"(.*?)"').findall(content)
    if vido_url:
        vido_url = vido_url[0]+'|Referer=%s&User-Agent=%s|Cookie=%s'%(BASEURL+url,UA,urllib.quote_plus(cookie))
        video.append({'url':vido_url,'titile':'Live','resolved':1})
    return video
