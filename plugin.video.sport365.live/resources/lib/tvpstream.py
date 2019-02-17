# -*- coding: utf-8 -*-

import re
import urllib2,urllib

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
BASEURL = 'http://tvpstream.tvp.pl/'
BRAMKA='http://www.bramka.proxy.net.pl/index.php?q='

def fixForEPG(one):
    return one

def getUrl(url,data=None,header={},cookies={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link = ''
    return link


def getChannels(url='http://tvpstream.tvp.pl/'):
    data=getUrl(url)
    livesrc="/sess/tvplayer.php?object_id=%s"
    
    id_title=re.compile('data-video_id="(.*?)" title="(.*?)">').findall(data)
    img_alt = re.compile('<span class="img"><img src="(.*?)" alt="(.*?)" />').findall(data)
    len(id_title)
    len(img_alt)
    out=[]
    for i in range(len(id_title)):
        video_id = id_title[i][0]
        title = img_alt[i][1].decode('utf-8') + ' : ' + id_title[i][1].decode('utf-8')
        img = img_alt[i][0]
        out.append({'title':title,'img':img,
                    'url':url+livesrc % video_id})
    return out   


def getChannelVideo(ex_link='http://tvpstream.tvp.pl/sess/tvplayer.php?object_id=15438607'):
    data=getUrl(ex_link)
    video=[]
    live_src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(data)
    if live_src:
        if 'material_niedostepny' in live_src[0]:
            data = getUrl(BRAMKA+urllib.quote_plus(ex_link)+'&hl=2a5')
            live_src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(data)
        video.append({'url':live_src[0],'titile':'Live','resolved':1})
    return video

def _getUrl(url='http://www.tvp.pl/tvplayer?channel_id=1634191&autoplay=true'):
    video=[{}]
    if 'http://www.tvp.pl/tvplayer' in url:
        data=getUrl(url)
        src=re.compile('src="(.*?)"').findall(data)
        if src and src[0].startswith('/sess/tvplayer.php'):
            video = getChannelVideo('http://tvpstream.tvp.pl'+src[0])
    elif '/sess/tvplayer.php' in url:
        video = getChannelVideo(url)
    return video
        