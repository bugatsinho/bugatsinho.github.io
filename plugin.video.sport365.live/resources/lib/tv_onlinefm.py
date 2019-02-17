# -*- coding: utf-8 -*-

import urllib2,urllib
import re
from urlparse import urlparse
import mydecode

BASEURL='http://tv-online.fm/'
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
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="item">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        title = re.compile('<b>(.*?)</b>').findall(subset)
        plot = re.compile('<div class ="progtvlista">(.*?)</div>',re.DOTALL).findall(subset)
        plot = re.sub(r'<.*?>','',plot[0]) if plot else ''
        href = re.compile('<a href="(.*?)">').findall(subset)
        linkN = re.compile('<b>\s*(\d+)\s*</b>').findall(subset)
        if href and title:
            group = href[0].split('?')[-1] if '?' in href[0] else ''
            linkN = linkN[0] if linkN else '?'
            t = title[0].strip()
            code = '[Linków:%s] %s'%(linkN,group)
            out.append({'title':t,'tvid':t,'img':'','url':href[0],'group':group,'urlepg':'','plot':plot,'code':code})
            
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (psa-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})        
    return out

SH=['static.u-pro.fr','iklub.net','looknij.in','wizja.tv','www.tvp.pl','tele-wizja.com']

def getStreams(url='http://tv-online.fm/telewizja.php?tv4?podstawowe'):
    out=[]
    content = getUrl(url)
    links =re.compile('<a class="listalinkalink" href="(.*?)"').findall(content)
    for link in links:
        title = urlparse(link).netloc
        if title in SH:
            title = '[COLOR green]%s[/COLOR]'%title
        else:
            title = '[COLOR red]%s[/COLOR]'%title
        out.append({'title':title,'tvid':title,'url':link})
    return out


    
def getChannelVideo(item):
    host = item.get('title')
    url = item.get('url')
    video=''
    if 'static.u-pro.fr' in host:
        data='src="%s"'%url
        video = mydecode.decode(url,data)
    elif 'iklub.net' in host:
        from iklub import _getUrl
        video = _getUrl(url)
    elif 'looknij.in' in host:
        from looknijin import getChannelVideo
        video = getChannelVideo(url)
        video = video[0].get('url','')
    elif 'wizja.tv' in host:
        from wizjatv import getChannelVideo
        video = getChannelVideo(url)
        video = video[0].get('url','')     
    elif 'tele-wizja' in host:
        data = getUrl(url)
        video = mydecode.decode(url,data)
    elif 'www.tvp.pl' in host:
        from tvpstream import _getUrl
        video = _getUrl(url)
        video = video[0].get('url','')     
    return video

    
      