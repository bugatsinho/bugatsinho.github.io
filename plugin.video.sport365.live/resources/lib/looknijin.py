# -*- coding: utf-8 -*-
import urllib2,urllib
import re
import time
import sys,os
import json
import cookielib
import threading
     

BASEURL='https://looknij.in'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='
TIMEOUT = '10'

fix={
'CANAŁ+':'Canal+',
'Canal Sport HD':'Canal+ Sport',
'HBOHD':'HBO',
'Minimini HD':'Minimini+',
'Polsat2HD':'Polsat 2',
'NsportHD':"nSport",
'TLC Polska HD':"TLC",
'Discovery Channel Historia':"Discovery Historia",
'TVPHD':'TVP HD',
'NATGEOCHANELL HD':"National Geographic Channel",
'TVP2 HD':'TVP 2',
'TVP1HD':'TVP 1',
'TVP HD':'TVP HD',
'POLSAT HD':'Polsat',
'POLSAT2HD':'Polsat 2',
'TVN PL':'TVN',
'COMEDY CENTRAL':'Comedy Central',
'Discovery Channel PL':'Discovery Channel',
'FILMBOX HD':'Filmbox',
'EUROSPORTHD':'Eurosport'
}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one



def getUrl(url,data=None,header={},cookies=None):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    if cookies:
        req.add_header("cookie", cookies)
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link=''
    return link    


def ThreadFunction(page, threadData, index):
    out = get_page(page=page)
    threadData[index]=out

def getChannels(addheader=False):
    out=[]
    pages = range(2)
    threadList = []
    threadData = [[] for x in pages]
    for i,page in enumerate(pages):
        thread = threading.Thread(name='Thread%d'%i, target = ThreadFunction, args=[page+1,threadData,i])
        threadList.append(thread)
        thread.start()

    while any([i.isAlive() for i in threadList]): time.sleep(0.1) 
    del threadList[:]
    
    for one in threadData:
        out.extend(one)
    

    if len(out)>0 and addheader:
        t='[COLOR yellow]Updated: %s (looknij.in)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://yoy.tv/','group':'','urlepg':''})
    return out
    

def get_page(page=2):
    url = 'https://looknij.in/telewizja-online/strona[%d]+'%(page)
    content = getUrl(BRAMKA+url)
    out=[]
    hrefs = re.compile('<h3 class.*?<a href="(.*?)">(.*?)</a>').findall(content)
    imgs = re.compile('<a href="(.*?)"><img src="(.*?)"').findall(content)

    for im,href in zip(imgs,hrefs):
        group=''
        t=href[-1].split('[')[0].strip()
        i=urllib.unquote(im[-1].replace(BRAMKA,''))
        h=urllib.unquote(im[0].replace(BRAMKA,''))
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))

    return out


def getChannelVideo(url='/telewizja-filmbox-hd-lektor-62'):
    video=[]
    if 'looknij.in' in url:
        id = url.split('-')[-1]
        urldata='https://looknij.in/tv/data/%s'%id
        data = getUrl(BRAMKA+urldata)
        if data:
            src = re.compile('"[U|u]rl":"(http.*?)"').findall(data)
            if src:
                vido_url = src[0].replace('\\','')+"|referer=%s"%(url)
                video=[{'url':vido_url}]
        else:
            video=[{'msg':'We are having a problem with Looknij.in'}]
    return video    

##    
def test():
    out=getChannels(addheader=False)
    o = out[0]
    for o in out:
        url= o.get('url')
        title= o.get('title')
        print title
        o['url']=decode_url(o.get('url'))
        print o['url']
    with open('looknij.json', 'w') as outfile:
        json.dump(out, outfile, indent=2, sort_keys=True)