# -*- coding: utf-8 -*-
import urllib2,urllib
import cookielib
import re
import time

BASEURL='http://sport.tvp.pl'
proxy={}
TIMEOUT = 10
BRAMKA='http://www.bramka.proxy.net.pl/index.php?q='

def getUrl(url,proxy={},timeout=TIMEOUT):
    if proxy:
        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.ProxyHandler(proxy)
            )
        )
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36')

    try:
        response = urllib2.urlopen(req,timeout=timeout)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def getChannels(url='http://sport.tvp.pl/na-antenie'):
    out=[]
    content=getUrl(url)
    #idx=content.find('Transmisje sport.tvp.pl')
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="date">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])): 
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        dzis = re.compile('<span>(DZI.*)</span>').findall(subset)
        if dzis:
            when=''
        else:
            when=re.compile('<span>(.*?)</span>').findall(subset)
            when = when[0]+' ' if when else ''
        idi = [(a.start(), a.end()) for a in re.finditer('<div class="item-time live">', subset)]
        idi.append( (-1,-1) )
        for j in range(len(idi[:-1])):
            item = subset[ idi[j][1]:idi[j+1][0] ]
            #print item
            href=[]
            time = re.compile('<span class="time">(.*?)</span>').findall(item)
            title= re.compile('<div class="item-title">([^<]+)</div>',re.DOTALL).findall(item)
            if not title:
                title_href = re.compile('<div class="item-title">(.*?)</div>',re.DOTALL).findall(item)
                title_href = title_href[0] if title_href else ''
                href  = re.compile('<a href="(.*?)"').findall(title_href)
                title = re.compile('>(.*?)<').findall(title_href)
            if title and time:
                t = '%s%s: [COLOR blue]%s[/COLOR]'%(when,time[0],title[0].strip())
                code='[B][COLOR lightgreen]Live[/COLOR][/B]' if href else ''
                href = getTvpStrem(href[0]) if href else ''
                out.append({'title':t,'tvid':'','url':href,'group':'','urlepg':'','code':code})
    return out

def getProxies():
    content=getUrl('http://www.idcloak.com/proxylist/free-proxy-list-poland.html')
    speed = re.compile('<div style="width:\d+%" title="(\d+)%"></div>').findall(content)
    trs = re.compile('<td>(http[s]*)</td><td>(\d+)</td><td>(.*?)</td>',re.DOTALL).findall(content)
    # if len(speed) == len(trs):
    #    speed = [int(x) for x in speed] 
    #    trs = [x for (y,x) in sorted(zip(speed,trs),reverse=True)]
    proxies=[{x[0]: '%s:%s'%(x[2],x[1])} for x in trs]
    return proxies
 
def getTvpStrem(url):
    vido_link=''
    if url=='':
        return vido_link
    if url.startswith('http://sport.tvp.pl'):
        content = getUrl(url)
    else:
        content = getUrl(BASEURL+url)
    iframe = re.compile("<iframe(.*?)</iframe>", re.DOTALL).findall(content)
    for frame in iframe:
        src = re.compile('src="(.*?)"', re.DOTALL).findall(frame)
        if src:
            vido_link='http://tvpstream.tvp.pl'+src[0]
    return vido_link

ex_link='http://sport.tvp.pl/27532589/pilka-nozna-liga-europejska-anderlecht-bruksela-fsv-mainz'

def getChannelVideo(ex_link):
    stream_url = decode_url(ex_link)
    if 'material_niedostepny' in stream_url:
        stream_url = decode_url(ex_link,pgate=True)
    if 'manifest.m3u8' in stream_url:
        stream_url = m3u_quality(stream_url.strip())
    if not stream_url:
        stream_url=[{'msg':'Materiał jest niedostępny'}]
        
    return stream_url 

# out=get_root()


def decode_url(ex_link,proxy={},timeout=TIMEOUT,pgate=False):
    vido_link=''
    if ex_link=='':
        return vido_link
    if pgate:
        data = getUrl(BRAMKA+urllib.quote_plus(ex_link)+'&hl=2a5')
    else:
        data = getUrl(ex_link,proxy,timeout=timeout)
    vido_link = re.compile("1:{src:\'(.+?)\'", re.DOTALL).findall(data)
    if not vido_link:
        vido_link = re.compile("0:{src:\'(.+?)\'", re.DOTALL).findall(data)
    
    vido_link = vido_link[0] if vido_link else ''
    
    return vido_link  

def m3u_quality(url):
    out=url
    if url and url.endswith('.m3u8'):
        rptxt = re.search('/(\w+)\.m3u8',url)
        rptxt = rptxt.group(1) if rptxt else 'manifest'
        content = getUrl(url)
        #content = '#EXTM3U\r\n#EXT-X-VERSION:2\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=393072,RESOLUTION=512x288\r\nQualityLevels(376000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=730332,RESOLUTION=512x288\r\nQualityLevels(706000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1251552,RESOLUTION=512x288\r\nQualityLevels(1216000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1905632,RESOLUTION=720x404\r\nQualityLevels(1856000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2518832,RESOLUTION=1024x576\r\nQualityLevels(2456000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3847432,RESOLUTION=1280x720\r\nQualityLevels(3756000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=7935432,RESOLUTION=1920x1080\r\nQualityLevels(7756000)/manifest(format=m3u8-aapl)\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=266032\r\nQualityLevels(256000)/manifest(format=m3u8-aapl)\r\n'
        matches=re.compile('RESOLUTION=(.*?)\r\n(QualityLevels\(.*\)/manifest\(format=m3u8-aapl\))').findall(content)
        if matches:
            out=[{'title':'auto','url':url}]
            #title, part = matches[0]
            for title, part in matches:
                one={'title':title,'url':url.replace(rptxt,part)}
                out.append(one)
    return out

# def rio_program():
#     content = getUrl('http://sport.tvp.pl/rio/25851771/program')
#     itemdata = re.compile('<span class="epg-item(.*?)\n\t\t\t</span>',re.DOTALL).findall(content)
#     out=[]
#     for item in itemdata:
#         if item.find('video-icon'):
#             dataid=re.compile('data-id="(.*?)"').findall(item)
#             dataredir=re.compile('data-redir="(.*?)"').findall(item)
#             times=re.compile('"time">(.*?)<').findall(item)
#             title=re.compile('class="title">(.*?)<').findall(item)
#             category=re.compile('class="category">(.*?)<').findall(item)
#             if dataredir and times and title and category:
#                 print dataredir
#                 # break
#                 id = re.compile('/(\d+)/').findall(dataredir[0]) if dataredir else ''
#                 start=re.compile('data-broadcast-start="(.*?)"').findall(item)
#                 end=re.compile('data-broadcast-end="(.*?)"').findall(item)
#                 start = int(start[0]) if start else -1
#                 end = int(end[0]) if end else -1
#                 t = '%s: [COLOR blue]%s, %s[/COLOR]'%(times[0],title[0].strip(),category[0].strip())
#                 href = 'http://tvpstream.tvp.pl/sess/tvplayer.php?object_id='+id[0] if id else ''
#                 code='[B][COLOR green]video[/COLOR][/B]' if href else ''
#                 if start<= time.time() <=end:
#                     code='[B][COLOR lightgreen]Live[/COLOR][/B]'
#                     
#                 out.append({'title':t,'tvid':'','img':'','url':href,'group':'','urlepg':'','code':code})
#     return out

def rio_program():
    content = getUrl('http://sport.tvp.pl/rio/25851771/program')
    itemdata = re.compile('<span class="epg-item(.*?)\n\t\t\t</span>',re.DOTALL).findall(content)
    out=[]
    for item in itemdata:
        #if item.find('video-icon'):
        dataid=re.compile('data-id="(.*?)"').findall(item)
        dataredir=re.compile('data-redir="(.*?)"').findall(item)
        times=re.compile('"time">(.*?)<').findall(item)
        title=re.compile('class="title">(.*?)<').findall(item)
        category=re.compile('class="category">(.*?)<').findall(item)
        bstart=re.compile('data-broadcast-start="(.*?)"').findall(item)
        bstart = float(bstart[0])/1000 if bstart else 0
        bstop=re.compile('data-broadcast-end="(.*?)"').findall(item)
        bstop = float(bstop[0])/1000 if bstop else 0
        if item.find('video-icon') and dataredir and times and title and category:
            print time.localtime().tm_yday
            #time.strftime("%a %H:%M", time.localtime(bstart))
            #Time
            if time.localtime().tm_yday==time.localtime(bstart).tm_yday:
                print 'TODAY'
                times = [time.strftime("%a %H:%M", time.localtime(bstart))]
            else:
                times = [time.strftime("%a %H:%M", time.localtime(bstart))]
            
            id = re.compile('/(\d+)/').findall(dataredir[0]) if dataredir else ''
            href = 'http://tvpstream.tvp.pl/sess/tvplayer.php?object_id='+id[0] if id else ''
            code='[B][COLOR green]video[/COLOR][/B]' if href else ''
            #if bstart <= time.time() <= bstop:
            if time.time() <= bstop:
                bstart=bstart/10 # make live apear first
                code='[B][COLOR lightgreen]Live[/COLOR][/B]'
                times = [times[0].split(' ')[-1]]
            t = '%s: [COLOR blue]%s, %s[/COLOR]'%(times[0],title[0].strip(),category[0].strip())
            print times[0]
            out.append({'title':t,'tvid':'','img':'','url':href,'group':'','urlepg':'','code':code,'ttime':bstart})
    out = sorted(out, key=lambda x: x['ttime'])
    return out


def test():
    out=get_root()
    out=rio_program()