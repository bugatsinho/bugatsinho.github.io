# -*- coding: utf-8 -*-
import xbmcvfs
import xbmcgui
import xbmcaddon
import xbmcplugin
import urllib
import re
import sys
import os
import threading
from sys import argv
from six.moves.urllib.parse import urljoin, parse_qsl, urlparse, unquote_plus, quote_plus, quote, unquote
from six.moves import zip
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import search
from resources.lib.modules import view
from resources.lib.modules import dom_parser as dom
from resources.lib.modules.addon import Addon

addon_id = 'plugin.video.rlshub'
plugin = xbmcaddon.Addon(id=addon_id)
DB = os.path.join(control.translatePath("special://database"), 'cache.db')
addon = Addon(addon_id, sys.argv)

##### Queries ##########
queries = dict(parse_qsl(argv[2][1:]))
mode = queries.get('mode', None)
url = queries.get('url', None)
content = queries.get('content', None)
query = queries.get('query', None)
startPage = queries.get('startPage', None)
numOfPages = queries.get('numOfPages', None)
listitem = queries.get('listitem', None)
urlList = queries.get('urlList', None)
section = queries.get('section', None)
title = queries.get('title', None)
img = queries.get('img', None)
text = queries.get('text', None)
plot = queries.get('plot', None)

tested_links = []

##### paths ##########
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')

NAME = ADDON.getAddonInfo('name')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/resources/icons/"
BANNER = IconPath + "banner.png"


def cloudflare_mode(url):
    from cloudscraper2 import CloudScraper
    import requests
    scraper = CloudScraper.create_scraper()
    ua = client.agent()
    scraper.headers.update({'User-Agent': ua})
    cookies = scraper.get(url).cookies.get_dict()
    headers = {'User-Agent': ua}
    req = requests.get(url, cookies=cookies, headers=headers)
    result = req.text
    # xbmc.log('RESULTTTTT: %s' % result)
    return result


def link_tester(item):
    try:
        host, title, link, name = item[0], item[1], item[2], item[3]
        # addon.log('URL Tested: [%s]: URL: %s ' % (host.upper(), link))
        na = ['has been deleted', 'file not found', 'file removed', 'sorry', 'step 1: select your plan']
        r = client.request(link)
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
                tested_links.append((link, title, name))

        # return tested_links
    except BaseException:
        addon.log('URL ERROR: [%s]: URL: %s ' % (host.upper(), link))


def PlayVideo(url, title, img, plot):
    try:
        import resolveurl
        stream_url = resolveurl.resolve(url)
        liz = xbmcgui.ListItem(title)
        liz.setArt({"icon": img, "thumbnail": FANART})
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": plot})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except BaseException:
        control.infoDialog(
            '[COLOR red][B]Probably your service doesn\'t support this provider![/B][/COLOR]\n'
            '[COLOR lime][B]Please try a different link!![/B][/COLOR]', NAME, ICON, 5000)


def get_size(text):
    try:
        text = text.upper()
        size = re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|Gb|MB|MiB|Mb))', text)[-1]
        div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
        size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
        size = '%.2f GB' % size
        return size
    except BaseException:
        return 'N/A'


def Sinopsis(txt):
    OPEN = txt.encode('utf8')
    try:
        try:
            if 'Plot:' in OPEN:
                try:
                    Sinopsis = re.findall(r'(Plot:.+?)</p>', OPEN, re.DOTALL)[0]
                except IndexError:
                    Sinopsis = re.findall(r'</p>\n<p>(.+?)</p><p>', OPEN, re.DOTALL)[0]
            elif 'imgaa.com' in OPEN:
                Sinopsis = re.findall(r'<br />\s*.+?<br />\s*(.+?)<br />', OPEN, re.DOTALL)[0]
        except:
            Sinopsis = re.findall('</p>\n<p>(.+?)</p>\n<p style', OPEN, re.DOTALL)[0]
        part = re.sub(r'<.*?>', '', Sinopsis)
        part = re.sub(r'\.\s+', '.', part)
        desc = clear_Title(part)
        desc = desc.decode('ascii', errors='ignore')
        return desc
    except BaseException:
        return 'N/A'


def clear_Title(txt):
    import re
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('\t', ' ').replace('\n', ' ')
    return txt


def GetDomain(url):
    elements = urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = r"(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res:
        domain = res.group(1)
    domain = domain.lower()
    return domain


def GetMediaInfo(html):
    try:
        # <h1 class="postTitle" rel="bookmark">American Dresser 2018 BRRip XviD AC3-RBG</h1>
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.findall(r'(.+?)\s+(\d{4}|S\d+E\d+)', match)[0]
        return match
    except IndexError:
        match = client.parseDOM(html, 'h1', attrs={'class': 'postTitle'})[0]
        match = re.sub('<.+?>', '', match)
        return match


def setviews():
    try:
        control.idle()

        items = [
            (control.lang(32017).encode('utf-8'), 'addons'),
            (control.lang(32018).encode('utf-8'), 'movies'),
            (control.lang(32019).encode('utf-8'), 'files')
        ]

        select = control.selectDialog([i[0] for i in items], 'SELECT')

        if select == -1:
            raise Exception()

        content = items[select][1]

        title = control.lang(32020).encode('utf-8')

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
