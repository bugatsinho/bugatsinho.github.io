# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import urllib
import urlparse
import re
import sys
import os
import threading
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import search
from resources.lib.modules import view
from resources.lib.modules import dom_parser as dom
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net


addon_id = 'plugin.video.releaseBB'
plugin = xbmcaddon.Addon(id=addon_id)
DB = os.path.join(xbmc.translatePath("special://database"), 'cache.db')
net = Net()
addon = Addon('plugin.video.releaseBB', sys.argv)

reload(sys)
sys.setdefaultencoding("utf-8")

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', None)
title = addon.queries.get('title', None)
img = addon.queries.get('img', None)
text = addon.queries.get('text', None)
plot = addon.queries.get('plot', None)
##### paths ##########
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')

NAME = ADDON.getAddonInfo('name')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/resources/icons/"
BANNER = IconPath + "banner.png"
base = control.setting('domain')
BASE_URL = 'http://%s' % base.lower()


def MainMenu():  # homescreen
    addon.add_directory({'mode': 'Categories', 'section': 'movies'},
                        {'title': '[COLOR orange][B]Release BB [COLOR blue]Movies [/COLOR][/B]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=IconPath + 'movie.png', fanart=FANART)
    addon.add_directory({'mode': 'Categories', 'section': 'tv-shows'},
                        {'title': '[COLOR orange][B]Release BB [COLOR blue]Tv Shows [/COLOR][/B]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=IconPath + 'tv.png', fanart=FANART)
    addon.add_directory({'mode': 'search_menu'},
                        {'title': '[COLOR orange][B]Release BB [COLOR yellow]Search[/COLOR][/B]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=IconPath + 'search.png', fanart=FANART)
    addon.add_directory({'mode': 'settings'}, {'title': '[COLOR cyan][B]Settings-Tools[/B][/COLOR]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=ICON, fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'setviews'}, {'title': '[COLOR cyan][B]Set View-Types[/B][/COLOR]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=ICON, fanart=FANART)
    # addon.add_directory({'mode': 'RealDebrid'},  {'title':  '[COLOR gold][B]Real Debrid Auth[/B][/COLOR]'},
    #                    img=IconPath + 'rd.png', fanart=FANART, is_folder=False)
    # addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR cyan][B]Resolver Settings[/B][/COLOR]'},
    #                    img=IconPath + 'resolver.png', fanart=FANART, is_folder=False)
    # addon.add_directory({'mode': 'ClearCache'}, {'title': '[COLOR red][B]Clear Cache[/B][/COLOR]'},
    #                    img=ICON, fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'help'}, {'title': '[COLOR gold][B][I]Github-Help[/B][/I][/COLOR]'},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img='https://bugatsinho.github.io/images/bug.png', fanart=FANART, is_folder=False)
    addon.add_directory({'mode': 'forceupdate'},
                        {'title': '[COLOR gold][B]Version:' + ' [COLOR lime]%s[/COLOR][/B]' % version},
                        [('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)')],
                        img=ICON, fanart=FANART, is_folder=False)
    
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500, 'skin.xonfluence': 500})

def Categories(section):  # categories
    sec = '/category/%s' % section
    html = response_html(BASE_URL, '96')
    match = client.parseDOM(html, 'li', attrs={'id': 'categories-2'})[0]
    items = zip(client.parseDOM(match, 'a'),
                client.parseDOM(match, 'a', ret='href'))
    items = [(i[0], i[1]) for i in items if sec in i[1]]
    for title, link in items:
        title = '[B][COLORgold]{0}[/COLOR][/B]'.format(title.encode('utf-8'))
        link = client.replaceHTMLCodes(link)
        addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': link, 'startPage': '1', 'numOfPages': '2'},
                            {'title': title},
                            [('Release BB Settings', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                             ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                             ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                            img='https://pbs.twimg.com/profile_images/834058861669654528/p7gDr9C6_400x400.jpg',
                            fanart=FANART)
    
    control.content(int(sys.argv[1]), 'addons')
    control.directory(int(sys.argv[1]))
    view.setView('addons', {'skin.estuary': 55, 'skin.confluence': 500, 'skin.xonfluence': 500})


def GetTitles(section, url, startPage='1', numOfPages='1'):  # Get Movie Titles
    try:
        if int(startPage) > 1:
            pageUrl = urlparse.urljoin(url, 'page/%d' % int(startPage))
        else:
            pageUrl = url

        html = response_html(pageUrl, '3')
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range(start, end):
            if page != start:
                pageUrl = urlparse.urljoin(url, 'page/%s' % page)
                html = response_html(pageUrl, '3')
            match = client.parseDOM(html, 'div', attrs={'class': 'post'})
            for item in match:
                movieUrl = client.parseDOM(item, 'a', ret='href')[0]
                name = client.parseDOM(item, 'a')[0]
                try:
                    img = client.parseDOM(item, 'img', ret='src')[1]
                    img = img.replace('.ru', '.to')
                except:
                    img = ICON
                try:
                    desc = client.parseDOM(item, 'div', attrs={'class': 'postContent'})[0]
                except:
                    desc = 'N/A'
            # match = [(client.parseDOM(i, 'a', ret='href')[0],
            #           client.parseDOM(i, 'a')[0],
            #           client.parseDOM(i, 'img', ret='src')[1],
            #           client.parseDOM(i, 'div', attrs={'class': 'postContent'})[0]) for i in match if i]
            # match = re.compile('postHeader.+?href="(.+?)".+?>(.+?)<.+?src=.+? src="(.+?).+?(Plot:.+?)</p>"', re.DOTALL).findall(html)
            # for movieUrl, name, img, desc in match:
                desc = Sinopsis(desc)
                name = '[B][COLORgold]{0}[/COLOR][/B]'.format(name.encode('utf-8'))
                addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl, 'img': img, 'plot': desc},
                                    {'title': name, 'plot': desc},
                                    [('Release BB Settings',
                                      'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                                     ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                                     ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                                    img=img, fanart=FANART)
            if 'Older Entries' not in html:
                break
        # keep iterating until the last page is reached
        if 'Older Entries' in html:
            addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages},
                                {'title': '[COLOR orange][B][I]Older Entries...[/B][/I][/COLOR]'},
                                img=IconPath + 'nextpage.png', fanart=FANART)
    except BaseException:
        control.infoDialog(
            '[COLOR red][B]Ooops![/B][/COLOR]\n[COLOR lime][B]Something wrong!![/B][/COLOR]', NAME, ICON, 3000)
    
    control.content(int(sys.argv[1]), 'movies')
    control.directory(int(sys.argv[1]))
    view.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500, 'skin.xonfluence': 500})


def GetLinks(section, url, img, plot):  # Get Links
    try:
        import resolveurl
        html = response_html(url, '3')
        listitem = GetMediaInfo(html)
        name = '%s (%s)' % (listitem[0], listitem[1])
        main = client.parseDOM(html, 'div', {'class': 'postContent'})
        main = [i for i in main if i]
        comments = dom.parse_dom(html, 'div', {'class': re.compile('content')})
        main += [i.content for i in comments if i]
        links = []
        for item in main:
            frames = client.parseDOM(item, 'a', ret='href')
            for url in frames:
                host = GetDomain(url)
                if 'Unknown' in host:
                    continue
                # ignore .rar files
                if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) \
                        or any(url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']):
                    continue
                if any(x in url.lower() for x in ['sample', 'zippyshare']):
                    continue

                addon.log('******* %s : %s' % (host, url))
                if resolveurl.HostedMediaFile(url=url):
                    addon.log('in GetLinks if loop')
                    title = url.rpartition('/')
                    title = title[2].replace('.html', '')
                    title = title.replace('.htm', '')
                    title = title.replace('.rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('rar', '[COLOR red][B][I]RAR no streaming[/B][/I][/COLOR]')
                    title = title.replace('www.', '')
                    title = title.replace('-', ' ')
                    title = title.replace('_', ' ')
                    title = title.replace('.', ' ')
                    title = title.replace('480p', '[COLOR coral][B][I]480p[/B][/I][/COLOR]')
                    title = title.replace('540p', '[COLOR coral][B][I]540p[/B][/I][/COLOR]')
                    title = title.replace('720p', '[COLOR gold][B][I]720p[/B][/I][/COLOR]')
                    title = title.replace('1080p', '[COLOR orange][B][I]1080p[/B][/I][/COLOR]')
                    title = title.replace('1080i', '[COLOR orange][B][I]1080i[/B][/I][/COLOR]')
                    title = title.replace('2160p', '[COLOR cyan][B][I]4K[/B][/I][/COLOR]')
                    title = title.replace('.4K.', '[COLOR cyan][B][I]4K[/B][/I][/COLOR]')
                    title = title.replace('mkv', '[COLOR gold][B][I]MKV[/B][/I][/COLOR] ')
                    title = title.replace('avi', '[COLOR pink][B][I]AVI[/B][/I][/COLOR] ')
                    title = title.replace('mp4', '[COLOR purple][B][I]MP4[/B][/I][/COLOR] ')
                    host = host.replace('youtube.com', '[COLOR red][B][I]Movie Trailer[/B][/I][/COLOR]')
                    if 'railer' in host:
                        title = host + ' : ' + title
                        addon.add_directory(
                            {'mode': 'PlayVideo', 'url': url, 'listitem': listitem, 'img': img, 'title': name,
                             'plot': plot},
                            {'title': title, 'plot': plot},
                            [('Release BB Settings',
                              'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                             ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                             ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                            img=img, fanart=FANART, is_folder=False)
                    else:
                        links.append((host, title, url, name))

        if control.setting('test.links') == 'true':
            threads = []
            for i in links:
                threads.append(Thread(link_tester, i))
            [i.start() for i in threads]
            [i.join() for i in threads]
        else:
            for item in links:
                host, title, link, name = item[0], item[1], item[2], item[3]
                title = '%s - %s' % (host, title)
                addon.add_directory(
                    {'mode': 'PlayVideo', 'url': link, 'listitem': listitem, 'img': img, 'title': name,
                     'plot': plot},
                    {'title': title, 'plot': plot},
                    [('Release BB Settings',
                      'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                     ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                     ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                    img=img, fanart=FANART, is_folder=False)

    except BaseException:
        control.infoDialog(
            "[COLOR red][B]Sorry there was a problem![/B][/COLOR]\n[COLOR lime][B]Please try again!![/B][/COLOR]",
            NAME, ICON, 3000)
    
    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500, 'skin.xonfluence': 500})


def cloudflare_mode(url):
    from resources.lib.modules import cfscrape
    scraper = cfscrape.create_scraper()
    headers = {'User-Agent': client.agent(),
               'Referer': BASE_URL}
    result = scraper.get(url, headers=headers).content
    return result


def response_html(url, cachetime):
    try:
        resulto = client.request(url)
        if resulto is None:
            html = cache.get(cloudflare_mode, int(cachetime), url)
        else:
            html = cache.get(client.request, int(cachetime), url)
        return html
    except BaseException:
        control.infoDialog(
            "[COLOR red][B]Sorry there was a problem![/B][/COLOR]\n[COLOR lime][B]Please try again!![/B][/COLOR]",
            NAME, ICON, 3000)


def link_tester(item):
    try:
        host, title, link, name = item[0], item[1], item[2], item[3]
        #addon.log('URL Tested: [%s]: URL: %s ' % (host.upper(), link))
        na = ['has been deleted', 'file not found', 'file removed', 'sorry', 'step 1: select your plan']
        r = response_html(link, 1)
        if r is None:
            addon.log('NO result: [%s]: URL: %s ' % (host.upper(), link))
            return False, 'N/A'
        else:
            if any(i in r.lower() for i in na):
                addon.log('URL Removed: [%s]: URL: %s ' % (host.upper(), link))
                valid, size = False, 'N/A'
            else:
                if 'nitroflare' in host:
                    r = client.parseDOM(r, 'legend')[0]
                    # addon.log('@#@RESULT:%s' % r)
                elif 'rapidgator' in host:
                    r = re.findall('''(File size:.+?)MD5''', r, re.I | re.DOTALL)[0]
                    # addon.log('@#@RESULT:%s' % r)
                elif 'turbobit' in host:
                    r = client.parseDOM(r, 'title')[0]
                    r = r.replace('Мб', 'MB')
                    # addon.log('@#@RESULT:%s' % r)
                elif any(i in host.lower() for i in ['rockfile', 'clicknupload']):
                    r = 'N/A'
                elif 'openload' in host or 'oload' in host:
                    r = re.findall('''(File size:.+?)</div>''', r, re.I | re.DOTALL)[0]
                    # addon.log('@#@RESULT:%s' % r)
                else:
                    r = r
                try:
                    size = get_size(r)
                except:
                    size = 'N/A'
                valid, size = True, str(size)

            if valid:
                addon.log('URL PASSED: [%s]: URL: %s : SIZE: %s' % (host.upper(), link, size))
                title = '%s|[COLORlime][B]%s[/COLOR][/B]| - %s' % (host, size, title)
                addon.add_directory(
                    {'mode': 'PlayVideo', 'url': link, 'listitem': listitem, 'img': img, 'title': name,
                     'plot': plot},
                    {'title': title, 'plot': plot},
                    [('Release BB Settings',
                      'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                     ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                     ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                    img=img, fanart=FANART, is_folder=False)

    except BaseException:
        addon.log('URL ERROR: [%s]: URL: %s ' % (host.upper(), link))




def PlayVideo(url, title, img, plot):
    try:
        import resolveurl
        stream_url = resolveurl.resolve(url)
        liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=img)
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": plot})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except BaseException:
        control.infoDialog(
            '[COLOR red][B]Probably your service doesn\'t support this provider![/B][/COLOR]\n'
            '[COLOR lime][B]Please try a different link!![/B][/COLOR]', NAME, ICON, 3000)


def get_size(text):
    try:
        text = text.upper()
        size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|Gb|MB|MiB|Mb))', text)[-1]
        div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
        size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
        size = '%.2f GB' % size
        return size
    except BaseException:
        return 'N/A'


def GetDomain(url):
    elements = urlparse.urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res:
        domain = res.group(1)
    domain = domain.lower()
    return domain


def GetMediaInfo(html):
    try:
        # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.findall('(.+?)\s+(\d{4}|S\d+E\d+)', match)[0]
        return match
    except BaseException:
        return []


def Sinopsis(txt):
    OPEN = txt.encode('utf8')
    try:
        try:
            if 'Plot:' in OPEN:
                Sinopsis = re.findall('(Plot:.+?)</p>', OPEN, re.DOTALL)[0]
            else:
                Sinopsis = re.findall('</p>\n<p>(.+?)</p><p>', OPEN, re.DOTALL)[0]

        except:
            Sinopsis = re.findall('</p>\n<p>(.+?)</p>\n<p style', OPEN, re.DOTALL)[0]
        part = re.sub('<.*?>', '', Sinopsis)
        part = re.sub('\.\s+', '.', part)
        desc = clear_Title(part)
        desc = desc.decode('ascii', errors='ignore')
        return desc
    except BaseException:
        return 'N/A'


def search_menu():
    addon.add_directory({'mode': 'search_bb', 'url': 'new'},
                        {'title': '[B][COLOR orange]New Search[/COLOR][/B]'}, img=IconPath + 'search.png', fanart=FANART)
    try:
        from sqlite3 import dbapi2 as database
    except BaseException:
        from pysqlite2 import dbapi2 as database

    dbcon = database.connect(control.searchFile)
    dbcur = dbcon.cursor()

    try:
        dbcur.execute("""CREATE TABLE IF NOT EXISTS Search (url text, search text)""")
    except BaseException:
        pass

    dbcur.execute("SELECT * FROM Search ORDER BY search")

    lst = []

    delete_option = False
    for (url, search) in dbcur.fetchall():
        title = '[B]%s[/B]' % urllib.unquote_plus(search).encode('utf-8')
        delete_option = True
        addon.add_directory({'mode': 'search_bb', 'url': search},
                            {'title': title},
                            [('Release BB Settings', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=settings)',),
                             ('Delete Search Item',
                              'RunPlugin(plugin://plugin.video.releaseBB/?mode=del_search_item&query=%s)' % search,),
                             ('Clear Cache', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=ClearCache)',),
                             ('Set View-Type', 'RunPlugin(plugin://plugin.video.releaseBB/?mode=setviews)',)],
                            img=IconPath + 'search.png', fanart=FANART)
        lst += [(search)]
    dbcur.close()

    if delete_option:
        addon.add_directory({'mode': 'del_search_items'},
                            {'title': 'Delete All Queries'},
                            img=IconPath + 'search.png', fanart=FANART, is_folder=False)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500, 'skin.xonfluence': 500})


def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('\t', ' ').replace('\n', ' ')
    return txt


def setviews():

    try:
        control.idle()

        items = [
            ('Menus', 'addons'), ('Movies & Shows', 'movies'), ('Links', 'files')
        ]

        select = control.selectDialog([i[0] for i in items], 'SELECT')

        if select == -1:
            raise Exception()

        content = items[select][1]
        xbmc.log('$#$CONTENT: %s' % content, xbmc.LOGNOTICE)

        title = 'CLICK HERE TO SAVE VIEW'

        poster, banner, fanart = ICON, BANNER, FANART

        addon.add_directory({'mode': 'addView', 'content': content},
                            {'type': 'video', 'title': title, 'icon': poster, 'thumb': poster,
                             'poster': poster, 'banner': banner},
                            img=ICON, fanart=FANART)
        control.content(int(sys.argv[1]), content)
        control.directory(int(sys.argv[1]))
        view.setView(content, {})
    except:
        quit()


class Thread(threading.Thread):

    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


if mode == 'main':
    MainMenu()
elif mode == 'Categories':
    Categories(section)
elif mode == 'GetTitles':
    GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetLinks':
    GetLinks(section, url, img, plot)
elif mode == 'search_menu':
    search_menu()
elif mode == 'search_bb':
    search.Search_bb(url)
elif mode == 'del_search_items':
    from resources.lib.modules import search
    search.search_clear()
elif mode == 'del_search_item':
    from resources.lib.modules import search
    search.del_search(query)
elif mode == 'PlayVideo':
    PlayVideo(url, title, img, plot)
elif mode == 'settings':
    control.openSettings()
elif mode == 'ResolverSettings':
    import resolveurl
    resolveurl.display_settings()
# elif mode == 'RealDebrid':
#    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)')
elif mode == 'ClearCache':
    cache.delete(control.cacheFile, False)
elif mode == 'forceupdate':
    control.infoDialog('Triggered a request for addon updates')
    control.execute('UpdateAddonRepos')
elif mode == 'help':
    control.open_git()
elif mode == 'addView':
    view.addView(content)
elif mode == 'setviews':
    setviews()
elif mode == 'del_views':
    view.view_clear()
