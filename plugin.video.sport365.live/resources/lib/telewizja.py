# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode
import urlparse
import threading

BASEURL='http://tele-wizja.com/'
UA = 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0'
fix={'animalplanet': 'Animal Planet',
 'boomerang': 'Boomerang',
 'canal': 'Canal+',
 'canaldiscovery': 'Canal+ Discovery HD',
 'canalfamily': 'Canal+ Film',
 'canalsport': 'Canal+ Sport',
 'canalsport2': 'Canal+ Sport 2',
 'cartoon': 'Cartoon Network',
 'cfilm': 'Canal+ Film',
 'cinemax': 'Cinemax',
 'comedycenter': 'Comedy Central',
 'discovery': 'Discovery Channel',
 'discoverys': 'Discovery Science',
 'disney-channel': 'Disney Channel',
 'eleven': 'Eleven',
 'elevensport': 'Eleven Sports',
 'eurosport': 'Eurosport',
 'eurosport2': 'Eurosport 2',
 'fox': 'Fox',
 'h2 ': 'History 2 ',
 'hbo': 'HBO',
 'hbo2': 'HBO2',
 'hbo3': 'HBO3',
 'id': 'ID',
 'kinopolska': 'Kino Polska',
 'kuchene': 'Kuchnia+',
 'minimini': 'Minimini+',
 'natgeo': 'National Geographic Channel',
 'natgeowild': 'Nat Geo Wild',
 'nsport': 'nSport',
 'stopklatka': 'Stopklatka TV',
 'tlc': 'TLC',
 'tvn': 'TVN',
 'tvn24': 'TVN 24',
 'tvn24bis': 'TVN 24 BIS',
 'tvn7': 'TVN 7',
 'tvnstyle': 'TVN Style',
 'tvnturbo': 'TVN Turbo',
 'tvp1': 'TVP 1',
 'tvp2': 'TVP 2',
 'tvphd': 'TVP HD',
 'tvpinfo1': 'TVP Info',
 'tvpseriale': 'TVP Seriale',
 'tvpsport': 'TVP Sport',
 'tvpuls': 'TV Puls',
 'tvrepublika': 'TV Republika',
 'xtra': 'Discovery Turbo Xtra',
 'ps':'Polsat Sport',
 'psn':'Polsat Sport News',
 'pse':'Polsat Sport Extra',
 'superstacja':'Superstacja',
 'pols':'Polsat',
 'tvv4':'TV 4'
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
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def ThreadFunction(url, threadData, index):
    out = getOne(url)
    threadData[index]=out

def getChannels(addheader=False):
    out=[]
    threadList = list()
    urls=['http://tele-wizja.com/ogolne.html','http://tele-wizja.com/info.html',
            'http://tele-wizja.com/filmowe.html','http://tele-wizja.com/naukowe.html',
            'http://tele-wizja.com/sportowe.html','http://tele-wizja.com/bajkowe.html']
    threadData = [[] for x in urls]
    for i,url in enumerate(urls):
        thread = threading.Thread(name='Thread%d'%i, target = ThreadFunction, args=[url,threadData,i])
        threadList.append(thread)
        thread.start()

    while any([i.isAlive() for i in threadList]): time.sleep(0.1) 
    del threadList[:]
    
    for one in threadData:
        out.extend(one)
        
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (tele-wizja)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
       
    return out
    
def getOne(url='http://tele-wizja.com/ogolne.html'):
    out=[]
    content = getUrl(url)
    code=url[:-5].split('/')[-1]
    items = re.compile('<a href="(.*?)" class="link"><img src="(.*?)"').findall(content)
    #href,icon=items[0]
    for href,icon in items:
        #print h,t,i
        c = code
        #c = href.split('/')[0]
        t = icon.split('.')[0].split('/')[-1]
        i = urlparse.urljoin(BASEURL,icon)
        h = urlparse.urljoin(BASEURL,href)
        # if t in orange:
        #     print t
        #     c = '[COLOR orange]'+c+'[/COLOR]'
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':'','code':c}))
    return out

def getChannelVideo(url='http://tele-wizja.com/tvn.html'):
    video=[]
    
    content = getUrl(url)
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    for iframe in iframes:
        pageUrl = re.compile('src="(.*?)"').findall(iframe)
        if pageUrl:
            data = getUrl(pageUrl[0])
            vido_url = mydecode.decode(url,data)
            print '$$$$$$$$$$$$$$$$$$$$$$$',vido_url
            if vido_url:
                video.append({'url':vido_url,'titile':'Live','resolved':1})
    return video 
    
def test():
    out = getChannels(False)
    outg=[]
    one =out[0]
    for one in out:
        print '\n',one.get('title')
        video=getChannelVideo(one.get('url'))
        if not video:
            outg.append(one.get('title'))
        print video
   
