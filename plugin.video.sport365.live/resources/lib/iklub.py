# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import threading
import mydecode

def fixForEPG(one):
    return one
    
def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
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
    urls=['http://iklub.net/info/','http://iklub.net/rozrywka/',
            'http://iklub.net/film/','http://iklub.net/muza/',
            'http://iklub.net/sports/']
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
        t='[COLOR yellow]Updated: %s (iklub)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://iklub.net','group':'','urlepg':''})        
    return out
    
def getOne(url='http://iklub.net/info/'):
    out=[]
    content = getUrl(url)
    code=url[:-1].split('/')[-1]
    idx1=content.find('class="entry-content"')
    idx2=content[idx1:].find('.entry-content')
    content = content[idx1:idx1+idx2]    
    
    href=re.compile('<a href="(http://iklub.net/.*?)"').findall(content)
    title = re.compile('alt="(.*?)"').findall(content)
    img = re.compile('src="(.*?)"').findall(content)
    #one=match[0]
    for h,t,i in zip(href,title,img):
        #print h,t,i
        t = t.replace('Telewizja online - ','').replace('_',' ').strip()
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':'','code':code}))
    return out


# url='http://iklub.net/filmboxfamily'
# url='http://iklub.net/eurosport/'
# url='http://iklub.net/fightbox-2/'
# url='http://iklub.net/mini-2/'
# url='http://iklub.net/1tvn/'
# url='http://iklub.net/polsat1-2/'
# url='http://iklub.net/polsat/'
# url='http://iklub.net/tv24/'
# url='http://iklub.net/tvpregionalna/'

#http://iklub.net/polszati.html
def getChannelVideo(url='http://iklub.net/tv24/'):
    video=[]
    if 'iklub.net' in url:
        urlpl = getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>').findall(urlpl)
        zapas = re.compile('<a href="(.*?)"><img src=".*?" alt="Zapasowy Player"').findall(urlpl)
        if zapas:
            urlpl2 = getUrl(zapas[0])
            iframe2 = re.compile('<iframe(.*?)</iframe>').findall(urlpl2)
            if iframe2: 
                iframes.extend(iframe2)
        #iframe= iframes[0]
        threadList = []
        threadData = [[] for x in iframes]
        for i,iframe in enumerate(iframes):
            thread = threading.Thread(name='Thread%d'%i, target = ThreadFunction2, args=[iframe,threadData,i])
            threadList.append(thread)
            thread.start()
        while any([i.isAlive() for i in threadList]): time.sleep(0.1) 
        del threadList[:]
    
        for i,one in enumerate(threadData):
            if one:
                video.append({'url':one,'title':'Link %d'%(i+1),'resolved':1})
    return video


def ThreadFunction2(iframe, threadData, index):
    out = decode_iframe(iframe)
    threadData[index]=out

def decode_iframe(iframe):
    video_url=''
    pageUrl = re.compile('src="(.*?)"').findall(iframe)
    if pageUrl:
        video_url = _getUrl(pageUrl[0])
    return video_url

def _getUrl(url):
    video_url=''
    content=getUrl(url)
    fun_hex = re.compile('eval\(unescape\(\'(.*?)\'\)\);\n').findall(content)
    code = re.search('\+ \'(.*?)\' \+',content)
    code = urllib.unquote(code.group(1)) if code else ''
    decoded = ''
    if fun_hex and code:
        fun = urllib.unquote(fun_hex[0])
        _split = re.compile('s\.split\(["\'](.*?)["\']').findall(fun)[0]
        _add1 = re.compile('unescape\(tmp\[1\] \+ ["\'](.*?)["\']\)').findall(fun)[0]
        _add2 = re.compile('charCodeAt\(i\)\)\+(.*?)\)\;').findall(fun)[0]

        tmp = code.split(str(_split))
        tk = tmp[1] + str(_add1)
        table=[]
        for i in range(0, len(code)):
            a = ord(code[i])
            b = int(tk[i % len(tk)])
            table.append((b ^ a) + int(_add2))
            decoded = ''.join(map(chr, table))

    src = re.search('src="(.*?)"',decoded)
    if src:
        src=src.group(1)
        if src.startswith('//'): 
            src='http:'+src
    else:
        src=''
    
    if decoded.find('var a =')>0:
        a=int(re.search('a = ([0-9]+)',decoded).group(1))
        b=int(re.search('b = ([0-9]+)',decoded).group(1))
        c=int(re.search('c = ([0-9]+)',decoded).group(1))
        d=int(re.search('d = ([0-9]+)',decoded).group(1))
        f=int(re.search('f = ([0-9]+)',decoded).group(1))
        v_part = re.search('v_part = \'(.*?)\';',decoded).group(1)
        link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]
        swfUrl=re.compile('src="(.*?)"').findall(decoded)[-1]
        swfUrl=swfUrl.replace('.js','.flash.swf').replace('_remote','')
        video_url = link + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+url

        #rtmp://31.220.0.201/privatestream/<playpath>tvvvppspportch <swfUrl>http://privatestream.tv/js/jwplayer.flash.swf <pageUrl>http://iklub.net/tvpsportl.html
    elif 'static.u-pro.fr' in src:
        source = re.compile('source=(rtmp.*?[^&]*)').findall(src)
        if source:
            video_url=source[0]
    else:
        data = getUrl(src)
        vido_url = mydecode.decode(src,decoded.replace('\\',''))
        if vido_url:
            video_url=vido_url
        elif data:
            idx = data.find('Initialize player')
            if idx<0:
                src = re.search('src="(.*?)"',data)
                if src:
                    src=src.group(1)
                    if src.startswith('//'): 
                        src='http:'+src
                    data = getUrl(src)
                    idx = data.find('Initialize player')
            data = data[idx:]
            swfUrl = re.search('"flashplayer": "(.*?)"',data)
            if swfUrl:
                swfUrl=swfUrl.group(1)
                if swfUrl.startswith('//'): 
                    swfUrl='http:'+swfUrl
            file = re.search('"file": "(.*?)",[\n\t ]+"type"',data)
            if file:
                file=file.group(1)
                if file.endswith('m3u8'):
                    video_url = file
                else:
                    video_url = file + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+url
    return video_url

def decode_all_urls(out,):
    out_hrefs=[]    
    for one in out:
        print one.get('title'),': ',one.get('url','')
        vido_url = decode_url(one.get('url',''))
        if vido_url:
            print'\t',vido_url
            one['url']=vido_url
            out_hrefs.append(one) 
    return out_hrefs

def build_m3u(out,fname='iklub.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    #OUTxmu=OUTxmu+'\n#EXTINF:-1, [COLOR yellow]Update: %s [/COLOR]\nhttp://www.youtube.com/\n\n' %(time.strftime("%d/%m/%Y: %H:%M:%S"))
    for one in out:
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()

##

# out=get_root()
# for one in out:
#     print one.get('title'),one.get('url'),one.get('img')
# 
# vido_url = decode_url(url='http://iklub.net/tvp1/')
# 
# out2=decode_all_urls(out)
# build_m3u(out2)
# len(out2)