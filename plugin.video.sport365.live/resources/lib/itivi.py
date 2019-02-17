# -*- coding: utf-8 -*-

import re
import urllib2,urllib
import base64
import time
import cookielib,os

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
BASEURL = 'http://itivi.pl/'

fix={
'TVP1 HD':'TVP 1',
'TVP2 HD':'TVP 2',
'POLSAT HD':'Polsat',
'TVN':'TVN',
'HBO HD':'HBO',
'CANAL SPORT': 'Canal+ Sport',
'FILMBOX PREMIUM':'Filmbox',
'Mini Mini':'Minimini+',
'ESKA TV':'Eska TV',
'Polo TV':'Polo TV',
'ESKA PARTY!':'Eska Part',
'CZWORKA POLSKIE RADIO LIVE':'Czwórka Polskie Radio',
'VOX':'VOX',
'Tlc HD':'TLC',
'canal film':'Canal+ Film',
'COMEDY CENTRAL':'Comedy Central',
'POLSAT 2HD':'Polsat 2',
'POLSAT SPORT HD':'Polsat Sport',
'TVP HD':'TVP HD',
'Discovery Channel':'Discovery Channel'
}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one


def getUrl(url,data=None,header={},cookies={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=10)
        header['Cookie']=response.info()['Set-Cookie']
        link = response.read()
        response.close()
    except:
        req = urllib2.Request(url,data,headers=header)
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    return link



def getChannels(addheader=False):
    content = getUrl(BASEURL)
    match=re.compile('<a href="(.*?)"><img alt="(.*?)" src="(.*?)" style').findall(content)
   
    out=[]
    #m=match[0]
    for m in match:
        h = m[0]
        t = m[1].replace('Telewizja online - ','').replace('_',' ').strip()
        i = m[2]
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    
    if addheader and out:
        t='[COLOR yellow]Updated: %s (itivi)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://itivi.pl/','group':'','urlepg':''})
    
    return out

def getChannelVideo(url='http://itivi.pl/program-telewizyjny/Discovery_Channel'):
    video=[]
    if 'itivi.pl' in url: 
        content = getUrl(url)
        link=re.compile('playM3U8byGrindPlayer\("(.*?)"\)').findall(content)
        if link:
            if link[0].startswith('http'):
                video.append({'url':link[0],'titile':'Live','resolved':1})
            else:
                swfUrl='http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf'
                vido_urls = link[0].replace('flv:','') + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=10 pageUrl='+url
                video.append({'url':vido_urls,'titile':'Live','resolved':1})
        else:
            video=[{'msg':'Zbyt wielu darmowych użytkowników korzysta z portalu!.'}]
    return video 
  

    
##
# out=getChannels()    
# 

# for h in out_hrefs:
#     l= h.get('url').split(' ')[0]
#     if 'itivi' in l:
#         print l
#         
#         
# for o in out:
#     print o.get('title')
#     if o.get('url').startswith('http'):
#         o['url']=o.get('url').split(' ')[0]
# import json
# 
# with open(r'D:\itivi.json', 'w') as outfile:
#     json.dump(out, outfile, indent=2, sort_keys=True)
