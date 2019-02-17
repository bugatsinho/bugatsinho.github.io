# -*- coding: utf-8 -*-

import urllib2,urllib
import re,time
import cookielib

BASEURL='http://www.amigostv.eu/'
TIMEOUT=10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

fix={
'axn':'AXN',
'bbchd':'BBC',
'cnhd':'Cartoon Network',
'elevenhd':'Eleven',
'filmbox':'Filmbox',
'hbohd':'HBO',
'tv4':'TV 4',
'tvpuls':'TV Puls',
'tvnstyle':'TVN Style',
'tvp1hd':'TVP 1',
'tvp2hd':'TVP 2',
'tvpinfo':'TVP Info',
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
    if setCookies:
        cj = cookielib.LWPCookieJar()
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

    except urllib2.HTTPError as e:
        link = ''
    return link,cookie

def getChannels(addheader=False):
    content,cookie = getUrl(BASEURL)
    out=[]
    chs = re.compile('<div class="col-sm-6 col-md-3">(.*?)</a>\s*</div>',re.DOTALL).findall(content)
    for ch in chs:
        #ch=chs[0]
        href = re.search('href="(.*?)"',ch)
        img = re.search('data-original="(.*?)"',ch)
        if href:
            href = href.group(1)
            title = href.split('/')[-1]
            img = BASEURL+img.group(1) if img else ''
            out.append(fixForEPG({'title':title.strip(),'tvid':title.strip(),'img':img,'url':BASEURL+href+'|%s'%cookie,'group':'','urlepg':''}))
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (amigostv.eu)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})        
    return out

# out=getChannels(addheader=False)
# url=out[0]['url']
# url='http://www.amigostv.eu/kanal/tvpinfo|__cfduid=d51d6885c2933d9cd1caa9514eca3aeb71478294444;'
def getChannelVideo(url):
    video=[]
    if 'amigostv' in url:
        myurl,cookie=url.split('|')
        header = {'User-Agent':UA,'Cookie':cookie,'Referer':'http://www.amigostv.eu/','X-Requested-With':'XMLHttpRequest'}
        content,c = getUrl(myurl,header=header,setCookies=False)
        src = re.compile('<source src="(.*?)" type="application/x-mpegURL">').findall(content)
        if src:
            video=[{'url':src[0]}]
        else:
            video=[{'msg':'Nie znalazłem linku'}]
    return video

def test():
    for o in out:
        print o['title']