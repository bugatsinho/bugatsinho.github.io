# -*- coding: utf-8 -*-
import json
import requests
import os
import re
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import six
import xbmcvfs
import time

from six.moves.urllib_parse import urlparse, urlencode, urljoin, unquote, unquote_plus, quote, quote_plus, parse_qsl

try:
    from sqlite3 import dbapi2 as database
except BaseException:
    from pysqlite2 import dbapi2 as database

from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import control
from resources.lib.modules import init
from resources.lib.modules import views
from resources.lib.modules import domparser as dom
from resources.lib.modules.control import addDir


ADDON = xbmcaddon.Addon()
ADDON_DATA = ADDON.getAddonInfo('profile')
ADDON_PATH = ADDON.getAddonInfo('path')
DESCRIPTION = ADDON.getAddonInfo('description')
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
ID = ADDON.getAddonInfo('id')
NAME = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
Lang = control.lang#ADDON.getLocalizedString
Dialog = xbmcgui.Dialog()
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"
gmtfile = ADDON_DATA + 'gamato_url.txt'


def get_gamdomain():
    try:
        adpath = control.transPath(ADDON_DATA)
        if not xbmcvfs.exists(adpath):
            xbmcvfs.mkdir(adpath)
        if xbmcvfs.exists(gmtfile):
            creation_time = xbmcvfs.Stat(gmtfile).st_mtime()
            if (creation_time + 18000) >= time.time():
                file = xbmcvfs.File(gmtfile)
                domains = json.loads(file.read())
                domain = domains['gamato']['main']
                control.setSetting('gamato.domain', domain)
                file.close()
                return domain

        mainurl = 'https://pastebin.com/raw/AdKpPAHC'
        response = requests.get(mainurl)
        resp = response.json()
        domain = resp['gamato']['main']

        file = xbmcvfs.File(gmtfile, 'w')
        data = json.dumps(resp)
        if isinstance(data, six.string_types):
            file.write(data)
        else:
            file.write(six.ensure_text(data, 'utf-8', 'replace'))
        file.close()
        return domain

    except BaseException:
        domain = 'https://gamatotv.info/m/'
        return domain


BASEURL = 'https://tenies-online1.gr/genre/kids/'  # 'https://paidikestainies.online/'
GAMATO = get_gamdomain()  #control.setting('gamato.domain') #or 'https://gmtv.co/'  # 'https://gamatokid.com/'
Teniesonline = control.setting('tenies.domain') or 'https://tenies-online1.gr/'


def Main_addDir():
    addDir('[B][COLOR yellow]Gamato ' + Lang(32000) + '[/COLOR][/B]', '', 20, ART + 'dub.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32005) + '[/COLOR][/B]', BASEURL, 8, ART + 'random.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32008) + '[/COLOR][/B]', BASEURL, 5, ART + 'latest.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32004) + '[/COLOR][/B]', BASEURL + 'quality/metaglotismeno/',
    #        5, ART + 'dub.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32003) + '[/COLOR][/B]', BASEURL+'quality/ellinikoi-ypotitloi/',
    #        5, ART + 'sub.jpg', FANART, '')

    # addDir('[B][COLOR yellow]Tenies-Online[/COLOR][/B]', '', 30, ART + 'dub.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32000) + '[/COLOR][/B]', '', 13, ART + 'movies.jpg', FANART, '')
    # addDir('[B][COLOR yellow]' + Lang(32001) + '[/COLOR][/B]', '', 14, ART + 'tvshows.jpg', FANART, '')
    downloads = True if control.setting('downloads') == 'true' and (
            len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or
            len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
    if downloads:
        addDir('[B][COLOR yellow]Downloads[/COLOR][/B]', '', 40, ICON, FANART, '')

    addDir('[B][COLOR gold]' + Lang(32002) + '[/COLOR][/B]', '', 6, ICON, FANART, '')
    addDir('[B][COLOR gold]' + Lang(32020) + '[/COLOR][/B]', '', 17, ART + 'set.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32021) + '[/COLOR][/B]', '', 9, ART + 'set.jpg', FANART, '')
    addDir('[B][COLOR gold]' + Lang(32019) + ': [COLOR lime]%s[/COLOR][/B]' % vers, '', 'bug',
           ART + 'ver.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def gamatokids():
    if xbmcvfs.exists(gmtfile):
        file = xbmcvfs.File(gmtfile)
        text = json.loads(file.read())
        file.close()
        meta = text['gamato']['meta']
        control.setSetting('gamato.metag', meta)
        anim = text['gamato']['animation']
        control.setSetting('gamato.anim', anim)
        fam = text['gamato']['family']
        control.setSetting('gamato.fam', fam)
        chris = text['gamato']['christmas']
        control.setSetting('gamato.chris', chris)
        addDir('[B][COLOR yellow]' + Lang(32004) + '[/COLOR][/B]', meta, 4, ART + 'dub.jpg', FANART, '')
        addDir('[B][COLOR yellow]' + Lang(32010) + '[/COLOR][/B]', anim, 4, ART + 'genre.jpg', FANART, '')
        addDir('[B][COLOR yellow]Family[/COLOR][/B]', fam, 4, ART + 'genre.png', FANART, '')
        addDir('[B][COLOR yellow]' + Lang(32044) + '[/COLOR][/B]', chris, 4, ART + 'mas.jpg', FANART, '')
        addDir('[B][COLOR gold]' + Lang(32002) + '[/COLOR][/B]', GAMATO, 18, ICON, FANART, '')

    else:
        get_gamdomain()
        gamatokids()

    views.selectView('menu', 'menu-view')


def Peliculas():
    addDir('[B][COLOR orangered]' + Lang(32008) + '[/COLOR][/B]',
           BASEURL, 5, ART + 'movies.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32006) + '[/COLOR][/B]',
           BASEURL, 3, ART + 'genre.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32007) + '[/COLOR][/B]',
           BASEURL, 15, ART + 'etos.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def Series():
    addDir('[B][COLOR orangered]' + Lang(32006) + '[/COLOR][/B]',
           BASEURL, 7, ART + 'genre.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32007) + '[/COLOR][/B]',
           BASEURL, 16, ART + 'etos.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32010) + '[/COLOR][/B]',
           BASEURL + 'tvshows-genre/κινούμενα-σχέδια/', 5, ART + 'tvshows.jpg', FANART, '')
    addDir('[B][COLOR orangered]' + Lang(32009) + '[/COLOR][/B]',
           BASEURL + 'tvshows/', 5, ART + 'tvshows.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def year(url):
    r = cache.get(client.request, 120, url)
    r = client.parseDOM(r, 'div', attrs={'id': 'moviehome'})[0]
    r = client.parseDOM(r, 'div', attrs={'class': 'filtro_y'})[0]
    r = client.parseDOM(r, 'li')
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            year = client.parseDOM(post, 'a')[0].encode('utf-8')
        except IndexError:
            year = '[N/A]'

        addDir('[B][COLOR white]%s[/COLOR][/B]' % year, url, 5, ART + 'movies.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def Get_TV_Genres(url):  # 7
    r = cache.get(client.request, 120, url)
    r = client.parseDOM(r, 'div', attrs={'id': 'serieshome'})[0]
    r = client.parseDOM(r, 'div', attrs={'class': 'categorias'})[0]
    r = client.parseDOM(r, 'li', attrs={'class': 'cat-item.+?'})
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            name = client.parseDOM(post, 'a')[0]
            name = re.sub(r'\d{4}', '', name)
            items = client.parseDOM(post, 'span')[0].encode('utf-8')
        except BaseException:
            pass
        name = clear_Title(name) + ' ([COLORlime]' + items + '[/COLOR])'
        addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 5, ART + 'tvshows.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def year_TV(url):
    r = cache.get(client.request, 120, url)
    r = client.parseDOM(r, 'div', attrs={'id': 'serieshome'})[0]
    r = client.parseDOM(r, 'div', attrs={'class': 'filtro_y'})[0]
    r = client.parseDOM(r, 'li')
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            year = client.parseDOM(post, 'a')[0].encode('utf-8')
        except BaseException:
            pass
        addDir('[B][COLOR white]%s[/COLOR][/B]' % year, url, 5, ART + 'tvshows.jpg', FANART, '')
    views.selectView('menu', 'menu-view')


def Get_random(url):  # 8
    r = client.request(url)
    r = client.parseDOM(r, 'div', attrs={'id': 'slider1'})[0]
    r = client.parseDOM(r, 'div', attrs={'class': 'item'})
    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            icon = client.parseDOM(post, 'img', ret='src')[0]
            name = client.parseDOM(post, 'span', attrs={'class': 'ttps'})[0].encode('utf-8')
            name = re.sub('\d{4}', '', name)
        except BaseException:
            pass
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'ytps'})[0].encode('utf-8')
        except BaseException:
            year = 'N/A'

        name = clear_Title(name)
        if '/ ' in name:
            name = name.split('/ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        elif '\ ' in name:
            name = name.split('\ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        else:
            name = name + ' ([COLORlime]' + year + '[/COLOR])'
        if 'tvshows' in url or 'syllogh' in url:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 11, icon, FANART, '')
        else:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 10, icon, FANART, '')
    views.selectView('movies', 'movie-view')


def Get_epoxiakes(url):  # 19
    try:
        r = client.request(url)
        r = client.parseDOM(r, 'div', attrs={'id': 'slider2'})[0]
        if r is None:
            control.infoDialog('Δεν υπάρχουν διαθέσιμοι τίτλοι αυτήν την περίοδο', NAME, ICON, 7000)
        else:
            r = client.parseDOM(r, 'div', attrs={'class': 'item'})
    except BaseException:
        r = []

    for post in r:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            icon = client.parseDOM(post, 'img', ret='src')[0]
            name = client.parseDOM(post, 'span', attrs={'class': 'ttps'})[0].encode('utf-8')
            name = re.sub(r'\d{4}', '', name)
        except BaseException:
            pass
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'ytps'})[0].encode('utf-8')
        except BaseException:
            year = 'N/A'

        name = clear_Title(name)
        if '/ ' in name:
            name = name.split('/ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        elif '\ ' in name:
            name = name.split('\ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        else:
            name = name + ' ([COLORlime]' + year + '[/COLOR])'
        if 'tvshows' in url or 'syllogh' in url:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 11, icon, FANART, '')
        else:
            addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 10, icon, FANART, '')
    views.selectView('movies', 'movie-view')


def Get_content(url):  # 5
    r = cache.get(client.request, 4, url)
    data = client.parseDOM(r, 'div', attrs={'id': 'mt-\d+'})
    for post in data:
        try:
            url = client.parseDOM(post, 'a', ret='href')[0]
            icon = client.parseDOM(post, 'img', ret='src')[0]
            if icon.startswith('data:'):
                icon = client.parseDOM(post, 'img', ret='data-lazy-src')[0]
            name = client.parseDOM(post, 'span', attrs={'class': 'tt'})[0]
            name = re.sub(r'\d{4}', '', name)
            desc = client.parseDOM(post, 'span', attrs={'class': 'ttx'})[0]
        except BaseException:
            pass
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'year'})[0].encode('utf-8')
        except BaseException:
            year = 'N/A'
        try:
            calidad = client.parseDOM(post, 'span', attrs={'class': 'calidad2'})[0].encode('utf-8')
            calidad = calidad.replace('Μεταγλωτισμένο', 'Μετ').replace('Ελληνικοί Υπότιτλοι', 'Υποτ')
            if '/' in calidad:
                calidad = Lang(32014)
            elif 'Προσ' in calidad:
                calidad = Lang(32017)
            elif calidad == 'Μετ':
                calidad = Lang(32015)
            else:
                calidad = Lang(32016)
        except BaseException:
            calidad = 'N/A'

        desc = clear_Title(desc)
        name = clear_Title(name)
        if '/ ' in name:
            name = name.split('/ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        elif '\ ' in name:
            name = name.split('\ ')
            name = name[1] + ' ([COLORlime]' + year + '[/COLOR])'
        else:
            name = name + ' ([COLORlime]' + year + '[/COLOR])'
        if 'tvshows' in url or 'syllogh' in url:
            addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(name, calidad), url, 11, icon, FANART, desc)
        else:
            addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(name, calidad), url, 10, icon, FANART, desc)
    try:
        np = re.compile('class="pag_b"><a href="(.+?)"', re.DOTALL).findall(r)
        for url in np:
            page = re.compile('page/(\d+)/', re.DOTALL).findall(url)[0]
            page = '[B][COLORlime]' + page + '[B][COLORwhite])[/B][/COLOR]'
            addDir('[B][COLORgold]>>>' + Lang(32011) + '[/COLOR] [COLORwhite](%s' % page, url, 5,
                   ART + 'next.jpg', FANART, '')
    except BaseException:
        pass
    views.selectView('movies', 'movie-view')


def get_tenies_online_links(url):
    urls = []

    headers = {'User-Agent': client.randomagent(),
               'Referer': url}
    #r = client.request(url)
    r = requests.get(url).text
    try:
        frames = client.parseDOM(r, 'div', {'id': 'playeroptions'})[0]
        frames = dom.parse_dom(frames, 'li', attrs={'class': 'dooplay_player_option'},
                               req=['data-post', 'data-nume', 'data-type'])
        for frame in frames:
            post = 'action=doo_player_ajax&post=%s&nume=%s&type=%s' % \
                   (frame.attrs['data-post'], frame.attrs['data-nume'], frame.attrs['data-type'])
            if '=trailer' in post: continue
            p_link = 'https://tenies-online1.gr/wp-admin/admin-ajax.php'

            #flink = client.request(p_link, post=post, headers=headers)
            flink = requests.post(p_link, data=post, headers=headers).text
            flink = client.parseDOM(flink, 'iframe', ret='src')[0]

            host = __top_domain(flink)
            urls.append((flink, host))
        # xbmc.log('FRAMES-LINKs: %s' % urls)
    except BaseException:
        pass

    try:
        extra = client.parseDOM(r, 'div', attrs={'class': 'links_table'})[0]
        extra = dom.parse_dom(extra, 'td')
        extra = [dom.parse_dom(i.content, 'img', req='src') for i in extra if i]
        extra = [(i[0].attrs['src'], dom.parse_dom(i[0].content, 'a', req='href')) for i in extra if i]
        extra = [(re.findall('domain=(.+?)$', i[0])[0], i[1][0].attrs['href']) for i in extra if i]
        for item in extra:
            url = item[1]
            if 'paidikestainies' in url:
                continue
            if 'tenies-online' in url:
                url = client.request(url, output='geturl', redirect=True)
            else:
                url = url

            host = item[0]

            urls.append((url, host))
        # xbmc.log('EXTRA-LINKs: %s' % urls)
    except BaseException:
        pass

    return urls


def __top_domain(url):
    elements = urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res: domain = res.group(1)
    domain = domain.lower()
    return domain


def search_menu():  # 6
    addDir(Lang(32024), 'new', 26, ICON, FANART, '')

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
        search = six.ensure_str(search, errors='replace')
        if 'gamato' in url:
            _url = GAMATO + "?s={}".format(quote_plus(search))
            domain = 'GAMATOKIDS'
        else:
            _url = Teniesonline + "?s={}".format(quote_plus(search))
            domain = 'TENIES-ONLINE'
        title = '[B]%s[/B] - [COLORgold][B]%s[/COLOR][/B]' % (search, domain)
        delete_option = True
        addDir(title, _url, 26, ICON, FANART, '')
        lst += [(search)]
    dbcur.close()

    if delete_option:
        addDir(Lang(32039), '', 29, ICON, FANART, '')
    views.selectView('movies', 'movie-view')


def Search(url):  # 26
    if url == 'new':
        keyb = xbmc.Keyboard('', Lang(32002))
        keyb.doModal()
        if keyb.isConfirmed():
            search = quote_plus(keyb.getText())
            if six.PY2:
                term = unquote_plus(search).decode('utf-8')
            else:
                term = unquote_plus(search)

            dbcon = database.connect(control.searchFile)
            dbcur = dbcon.cursor()

            dp = xbmcgui.Dialog()
            select = dp.select('Select Website', ['[COLORgold][B]Tenies-Online[/COLOR][/B]', '[COLORgold][B]Gamato-Kids[/COLOR][/B]'])

            if select == 0:
                from resources.lib.indexers import teniesonline
                url = Teniesonline + "?s={}".format(search)
                dbcur.execute("DELETE FROM Search WHERE url = ?", (url,))
                dbcur.execute("INSERT INTO Search VALUES (?,?)", (url, term))
                dbcon.commit()
                dbcur.close()
                teniesonline.search(url)

            elif select == 1:
                url = GAMATO + "?s={}".format(search)
                dbcur.execute("DELETE FROM Search WHERE url = ?", (url,))
                dbcur.execute("INSERT INTO Search VALUES (?,?)", (url, term))
                dbcon.commit()
                dbcur.close()
                gamato_kids(url)
            else:
                return
        else:
            return


    else:
        if 'gamato' in url:
            gamato_kids(url)
        else:
            from resources.lib.indexers import teniesonline
            teniesonline.search(url)
    views.selectView('movies', 'movie-view')


def Del_search(url):
    control.busy()
    search = url.split('s=')[1].decode('utf-8')

    dbcon = database.connect(control.searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("DELETE FROM Search WHERE search = ?", (search,))
    dbcon.commit()
    dbcur.close()
    xbmc.executebuiltin('Container.Refresh')
    control.idle()


def download(name, iconimage, url):
    control.busy()
    if url is None:
        control.idle()
        return

    try:
        url = resolve(name, url, iconimage, '', return_url=True)
        url = url.split('|')[0]
    except Exception:
        control.idle()
        xbmcgui.Dialog().ok(NAME, 'Download failed' + '[CR]' + 'Your service can\'t resolve this hoster' + '[CR]' + 'or Link is down')
        return

    try:
        headers = dict(parse_qsl(url.rsplit('|', 1)[1]))
    except BaseException:
        headers = dict('')
    control.idle()
    name = name.split('|')[0].strip()
    title = re.sub('\[.+?\]', '', name)
    content = re.compile('(.+?)\s+[\.|\(|\[]S(\d+)E\d+[\.|\)|\]]', re.I).findall(title)
    try: transname = title.translate(None, '\/:*?"<>|').strip('.')
    except: transname = title.translate(str.maketrans('', '', '\/:*?"<>|')).strip('.')
    transname = re.sub('\[.+?\]', '', transname)
    levels = ['../../../..', '../../..', '../..', '..']
    if len(content) == 0:
        dest = control.setting('movie.download.path')
        dest = control.transPath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        dest = os.path.join(dest, transname)
        control.makeFile(dest)
    else:
        dest = control.setting('tv.download.path')
        dest = control.transPath(dest)
        for level in levels:
            try:
                control.makeFile(os.path.abspath(os.path.join(dest, level)))
            except:
                pass
        control.makeFile(dest)
        tvtitle = re.sub('\[.+?\]', '', content[0])
        try: transtvshowtitle = tvtitle.translate(None, '\/:*?"<>|').strip('.')
        except: transtvshowtitle = tvtitle.translate(str.maketrans('', '', '\/:*?"<>|')).strip('.')
        dest = os.path.join(dest, transtvshowtitle)
        control.makeFile(dest)
        dest = os.path.join(dest, 'Season %01d' % int(content[0][1]))
        control.makeFile(dest)
    control.idle()
    # ext = os.path.splitext(urlparse(url).path)[1]

    ext = os.path.splitext(urlparse(url).path)[1][1:]
    # xbmc.log('URL-EXT: %s' % ext)
    if not ext in ['mp4', 'mkv', 'flv', 'avi', 'mpg']: ext = 'mp4'
    dest = os.path.join(dest, transname + '.' + ext)
    headers = quote_plus(json.dumps(headers))
    # xbmc.log('URL-HEADERS: %s' % headers)

    from resources.lib.modules import downloader
    control.idle()
    downloader.doDownload(url, dest, name, iconimage, headers)


def downloads_root():
    movie_downloads = control.setting('movie.download.path')
    tv_downloads = control.setting('tv.download.path')
    cm = [(control.lang(32007),
           'RunPlugin(plugin://plugin.video.cartoonsgr/?mode=17)'),
          (control.lang(32008), 'RunPlugin(plugin://plugin.video.cartoonsgr/?mode=9)')]
    if len(control.listDir(movie_downloads)[0]) > 0:
        item = control.item(label='Movies')
        item.addContextMenuItems(cm)
        item.setArt({'icon': ART + 'movies.jpg', 'fanart': FANART})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), movie_downloads, item, True)

    if len(control.listDir(tv_downloads)[0]) > 0:
        item = control.item(label='Tv Shows')
        item.addContextMenuItems(cm)
        item.setArt({'icon': ART + 'tvshows.jpg', 'fanart': FANART})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), tv_downloads, item, True)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    views.selectView('movies', 'movie-view')


######################
####  GAMATOKIDS  ####
######################

def get_gam_genres(url):  # 3
    try:

        r = requests.get(url).text
        r = client.parseDOM(r, 'li', attrs={'id': r'menu-item-\d+'})[1:]
        # xbmc.log('POSTs: {}'.format(r))
        # r = client.parseDOM(r, 'div', attrs={'class': 'categorias'})[0]
        # r = client.parseDOM(r, 'li', attrs={'class': 'cat-item.+?'})
        for post in r:
            try:
                # xbmc.log('POST: {}'.format(post))
                url = client.parseDOM(post, 'a', ret='href')[0]
                name = client.parseDOM(post, 'a')[0]
                name = clear_Title(name)
                if 'facebook' in url or 'imdb' in url:
                    continue
                # xbmc.log('NAME: {} | URL: {}'.format(name, url))
                addDir('[B][COLOR white]%s[/COLOR][/B]' % name, url, 4, ART + 'movies.jpg', FANART, '')
            except BaseException:
                pass

    except BaseException:
        pass
    views.selectView('menu', 'menu-view')


def Search_gamato(url):  # 18
    control.busy()
    data = r = requests.get(url).text
    posts = client.parseDOM(data, 'div', attrs={'class': 'result-item'})
    for post in posts:
        link = client.parseDOM(post, 'a', ret='href')[0]
        poster = client.parseDOM(post, 'img', ret='src')[0].encode('utf-8', 'ignore')
        title = client.parseDOM(post, 'img', ret='alt')[0]
        title = clear_Title(title)
        try:
            year = client.parseDOM(post, 'span', attrs={'class': 'year'})[0]
            desc = client.parseDOM(post, 'div', attrs={'class': 'contenido'})[0]
            desc = re.sub('<.+?>', '', desc)
            desc = clear_Title(desc)
        except IndexError:
            year = 'N/A'
            desc = 'N/A'

        addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(title, year), link, 12, poster, FANART, str(desc))

    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'class': 'arrow_pag'})[-1]
        page = np.split('/')[-1]
        title = '[B][COLORgold]>>>' + Lang(32011) + ' [COLORwhite]([COLORlime]%s[/COLOR])[/COLOR][/B]' % page
        addDir(title, np, 4, ART + 'next.jpg', FANART, '')
    except IndexError:
        pass
    control.idle()
    views.selectView('movies', 'movie-view')


def gamato_kids(url):  # 4
    data = six.ensure_text(requests.get(url).text)
    posts = client.parseDOM(data, 'div', attrs={'id': 'post-\d+'})
    for post in posts:
        try:
            plot = re.findall('''texto["']>(.+?)</div> <div''', post, re.DOTALL)[0]
        except IndexError:
            plot = client.parseDOM(post, 'div', attrs={'class': 'entry-summary'})[0]
        if len(plot) < 1:
            plot = 'N/A'
        desc = client.replaceHTMLCodes(plot)
        desc = six.ensure_str(desc, encoding='utf-8')
        try:
            title = client.parseDOM(post, 'a', ret='title')[0]
            year = re.findall(r'(\d{4})', title, re.DOTALL)[0]
            title = re.sub(r'\d{4}', '', title)
            if not (len(year) == 4 and year.isdigit()):
                year = 'N/A'
        except IndexError:
            title = client.parseDOM(post, 'img', ret='alt')[0]
            year = 'N/A'
        year = '[COLORlime]{}[/COLOR]'.format(year)
        title = clear_Title(title)
        link = client.parseDOM(post, 'a', ret='href')[0]
        link = clear_Title(link)
        poster = client.parseDOM(post, 'img', ret='src')[0]
        if poster.startswith('data:'):
            poster = client.parseDOM(post, 'img', ret='data-lazy-src')[0]
        poster = clear_Title(poster)

        addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(title, year), link, 12, poster, FANART, desc)
    try:
        np = client.parseDOM(data, 'a', ret='href', attrs={'class': 'next page-numbers'})[-1]
        np = clear_Title(np)
        page = np[-2] if np.endswith('/') else re.findall(r'page/(\d+)/', np)[0]
        title = '[B][COLORgold]>>>' + Lang(32011) + ' [COLORwhite]([COLORlime]%s[/COLOR])[/COLOR][/B]' % page
        addDir(title, np, 4, ART + 'next.jpg', FANART, '')
    except IndexError:
        pass
    views.selectView('movies', 'movie-view')


def gamatokids_top(url):  # 21
    data = requests.get(url).text
    posts = client.parseDOM(data, 'article', attrs={'class': 'w_item_a'})
    for post in posts:
        try:
            title = client.parseDOM(post, 'h3')[0]
            title = clear_Title(title)
            link = client.parseDOM(post, 'a', ret='href')[0]
            poster = client.parseDOM(post, 'img', ret='src')[0]
            year = client.parseDOM(post, 'span', attrs={'class': 'wdate'})[0]

            addDir('[B][COLOR white]{0} [{1}][/COLOR][/B]'.format(title, year), link, 12, poster, FANART,
                   'Προτεινόμενα')
        except IndexError:
            pass
    views.selectView('movies', 'movie-view')


def gamato_links(url, name, poster, description):  # 12
    # try:
        url = quote(url, ':/.')
        data = six.ensure_text(requests.get(url).text, encoding='utf-8', errors='replace')
        html = client.parseDOM(data, 'div', attrs={'id': 'content'})[0]
        # xbmc.log('DATA: {}'.format(html))
        try:
            desc = re.findall(r'<p>(.+?)<a', html, re.DOTALL)[0]
            desc = clear_Title(desc)
        except IndexError:
            desc = description

        try:
            fanart = client.parseDOM(data, 'div', attrs={'class': 'g-item'})[0]
            fanart = client.parseDOM(fanart, 'a', ret='href')[0]
        except IndexError:
            fanart = FANART

        dlink = client.parseDOM(html, 'div', attrs={'class': 'entry-content'})[0]
        main_links = []
        trailer_links = []
        try:
            iframes = client.parseDOM(dlink, 'iframe', ret='src')
            xbmc.log('LINKSS222: {}'.format(str(iframes)))
        except:
            iframes = []
        try:
            hrefs = client.parseDOM(dlink, 'a', ret='href')
            xbmc.log('LINKSS111: {}'.format(str(hrefs)))
        except:
            hrefs = []

        for href in hrefs:
            if "youtube" in href or "trailer" in href.lower():
                trailer_links.append(href)
            else:
                main_links.append(href)
        for src in iframes:
            if "youtube" in src:
                trailer_links.append(src)
            else:
                main_links.append(src)
        if len(trailer_links) < 1:
            addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')
        else:
            addDir('[B][COLOR lime]Trailer[/COLOR][/B]', trailer_links[0], 100, iconimage, fanart, str(desc))
        for link in main_links:
            link = unquote_plus(link)
            addDir(name, link, 100, poster, fanart, str(desc))

    # except BaseException:
    #     return
        views.selectView('movies', 'movie-view')


def get_links(name, url, iconimage, description):
    hdrs = {'Referer': GAMATO,
            'User-Agent': client.agent()}
    data = six.ensure_str(requests.get(url).content)
    if '''data-nume='trailer'>''' in data:
        try:
            flink = client.parseDOM(data, 'iframe', ret='src', attrs={'class': 'rptss'})[0]
            if 'youtu' in flink:
                addDir('[B][COLOR lime]Trailer[/COLOR][/B]', flink, 100, iconimage, FANART, '')
            else:
                addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')
        except IndexError:
            yid = client.parseDOM(data, 'li', ret='data-post', attrs={'id': 'player-option-trailer'})[0]
            post_data = {'action': 'doo_player_ajax',
                         'post': yid,
                         'nume': 'trailer',
                         'type': 'movie'}
            post_data = urlencode(post_data).encode('utf-8')
            post_link = GAMATO + 'wp-admin/admin-ajax.php'
            ylink = client.request(post_link, post=post_data, headers=hdrs)
            if ylink:
                flink = json.loads(ylink)['embed_url']
                addDir('[B][COLOR lime]Trailer[/COLOR][/B]', flink, 100, iconimage, FANART, '')
            else:
                addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')
            # except:
            #     # http://gamatotv.info/wp-json/dooplayer/v1/post/45755?type=movie&source=trailer
            #     # action=doo_player_ajax&post=69063&nume=trailer&type=movie
            #     ylink = ' http://gamatotv.info/wp-json/dooplayer/v1/post/{}?type=movie&source=trailer'
            #     # li id='player-option-trailer'
            #     yid = client.parseDOM(data, 'li', ret='data-post', attrs={'id': 'player-option-trailer'})[0]
            #     flink = ylink.format(yid)
            #     flink = client.request(flink)
            #     flink = json.loads(flink)['embed_url']

    else:
        addDir('[B][COLOR lime]No Trailer[/COLOR][/B]', '', 100, iconimage, FANART, '')

    try:
        if 'tvshows' not in url:

            # try:
            #     frame = client.parseDOM(data, 'iframe', ret='src', attrs={'class': 'metaframe rptss'})[0]
            # except IndexError:
            #     get_vid = 'http://gamatotv.info/wp-json/dooplayer/v1/post/{}?type=movie&source=1'
            #     id = client.parseDOM(data, 'li', ret='data-post', attrs={'id': 'player-option-1'})[0]
            #     frame = client.request(get_vid.format(id))
            #     frame = json.loads(frame)['embed_url']
            #     if 'coverapi' in frame:
            #         html = requests.get(frame).text
            #         post_url = 'https://coverapi.store/engine/ajax/controller.php'
            #         postdata = re.findall(r'''data: \{mod: 'players', news_id: '(\d+)'\},''', html, re.DOTALL)[0]
            #         # xbmc.log('POSR-DATA: {}'.format(str(postdata)))
            #         postdata = {'mod': 'players',
            #                     'news_id': postdata}
            #         hdrs = {'Origin': 'https://coverapi.store',
            #                 'Referer': frame,
            #                 'User-Agent': client.agent()}
            #         post_html = requests.post(post_url, data=postdata, headers=hdrs).text.replace('\\', '')
            #         # xbmc.log('POSR-HTML: {}'.format(str(post_html)))
            #         frame = re.findall(r'''file:\s*['"](http.+?)['"]''', post_html, re.DOTALL)[0]
            #         title = '{} | [B]{}[/B]'.format(name, 'Gamato')
            #         addDir(title, frame, 100, iconimage, FANART, str(description))
            #     elif '/jwplayer/?source' in frame:
            #         frame = re.findall(r'''/jwplayer/\?source=(.+?)&id=''', frame, re.DOTALL)[0]
            #         # xbmc.log('FRAME-JWPLAYER: {}'.format(str(frame)))
            #         # frame = unquote_plus(frame)
            #         title = '{} | [B]{}[/B]'.format(name, 'Gamato')
            #         addDir(title, frame, 100, iconimage, FANART, str(description))
            #     else:
            #         host = GetDomain(frame)
            #         title = '{} | [B]{}[/B]'.format(name, host.capitalize())
            #         addDir(title, frame, 100, iconimage, FANART, str(description))

                    # try:
            frames = client.parseDOM(data, 'tr', {'id': r'link-\d+'})
            frames = [(client.parseDOM(i, 'a', ret='href', attrs={'target': '_blank'})[0],
                       re.findall(r'''favicons\?domain=(.+?)['"]>''', i, re.DOTALL)[0]) for i in frames if frames]
            for frame, domain in frames:
                # host = domain.split('=')[-1]
                host = six.ensure_str(domain, 'utf-8')
                # if 'Μεταγλωτισμένο' in info.encode('utf-8', 'ignore'):
                #     info = '[Μετ]'
                # elif 'Ελληνικοί' in info.encode('utf-8', 'ignore'):
                #     info = '[Υπο]'
                # elif 'Χωρίς' in info.encode('utf-8', 'ignore'):
                #     info = '[Χωρίς Υπ]'
                # else:
                #     info = '[N/A]'
                quality = 'SD'
                title = '{} | [B]{}[/B] | ({})'.format(name, host.capitalize(), quality)
                addDir(title, frame, 100, iconimage, FANART, str(description))
                    # except BaseException:
                    #     pass


        else:
            data = client.parseDOM(data, 'table', attrs={'class': 'easySpoilerTable'})
            seasons = [dom.parse_dom(i, 'a', {'target': '_blank'}, req='href') for i in str(data)[:-1] if i]
            episodes = []
            for season in seasons:
                for epi in season:
                    title = clear_Title(epi.content.replace('&#215;', 'x'))
                    frame = epi.attrs['href']
                    episodes.append((title, frame))

            for title, frame in episodes:
                addDir(title, frame, 100, iconimage, FANART, str(description))

    except BaseException:
        title = '[B][COLOR white]NO LINKS[/COLOR][/B]'
        addDir(title, '', 'bug', iconimage, FANART, str(description))
    views.selectView('movies', 'movie-view')


########################################

def find_single_match(data, patron, index=0):
    try:
        matches = re.findall(patron, data, flags=re.DOTALL)
        return matches[index]
    except IndexError:
        return ""


def clear_Title(txt):
    import six
    if six.PY2:
        txt = txt.encode('utf-8', 'ignore')
    else:
        txt = six.ensure_text(txt, encoding='utf-8', errors='ignore')
    txt = re.sub(r'<.+?>', '', txt)
    txt = re.sub(r'var\s+cp.+?document.write\(\'\'\);\s*', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':').replace('\n',
                                                                                                               ' ')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('&#8216;', '"').replace('\t', ' ')
    return txt


def Open_settings():
    control.openSettings()


def cache_clear():
    cache.clear(withyes=False)
    xbmcvfs.delete(gmtfile)


def search_clear():
    cache.delete(control.searchFile, withyes=False)
    control.refresh()
    control.idle()


def resolve(name, url, iconimage, description, return_url=False):
    liz = xbmcgui.ListItem(name)
    host = url
    if '/links/' in host:
        try:
            frame = client.request(host)
            host = client.parseDOM(frame, 'a', {'id': 'link'}, ret='href')[0]

        except BaseException:
            host = requests.get(host, allow_redirects=False).headers['Location']

    elif 'streamclood' in host:
        html = requests.get(host).text
        host = client.parseDOM(html, 'iframe', ret='src')[0]

    elif 'gmtv1' in host or 'gmtdb' in host or 'gmtbase' in host or 'gmtcloud' in host or 'gmtv' in host:
        html = requests.get(host).text
        try:
            host = client.parseDOM(html, 'source', ret='src', attrs={'type': 'video/mp4'})[0]
        # xbmc.log('HOSTTTT: {}'.format(host))
        except IndexError:
            host = client.parseDOM(html, 'iframe', ret='src')[0]


    else:
        host = host

    # try resolveurl first:  #https://gamatotv.site/embed/ooops/ http://gmtv1.com/embed/pinocchio2022/
    stream_url = evaluate(host)
    if not stream_url:
        if 'gamato' in host: #or 'gmtv1' in host
            html = requests.get(host).text
            host = client.parseDOM(html, 'source', ret='src')[0]
        else:
            pass
        if host.split('|')[0].endswith('.mp4?id=0') and 'clou' in host or 'gmtdb' in host or "gmtv1" in host:
            stream_url = host + '||User-Agent=iPad&Referer={}'.format(GAMATO)
            name = name
        elif host.endswith('.mp4') and 'vidce.net' in host:
            stream_url = host + '|User-Agent={}'.format(quote_plus(client.agent()))
        elif host.endswith('.mp4'):
            stream_url = host + '|User-Agent=%s&Referer=%s' % (quote_plus(client.agent(), ':/'), GAMATO)
        # stream_url = requests.get(host, headers=hdr).url
        elif '/aparat.' in host:
            try:
                from resources.lib.resolvers import aparat
                stream_url = aparat.get_video(host)
                stream_url, sub = stream_url.split('|')
                liz.setSubtitles([sub])
            except BaseException:
                stream_url = evaluate(host)
        # elif '/clipwatching.' in host:
        #     xbmc.log('HOST: {}'.format(host))
        #     # try:
        #     data = requests.get(host).text
        #     xbmc.log('DATA: {}'.format(data))
        #     try:
        #         sub = client.parseDOM(data, 'track', ret='src', attrs={'label': 'Greek'})[0]
        #         xbmc.log('SUBS: {}'.format(sub))
        #         liz.setSubtitles([sub])
        #     except IndexError:
        #         pass
        #
        #     stream_url = re.findall(r'''sources:\s*\[\{src:\s*['"](.+?)['"]\,''', data, re.DOTALL)[0]
        #     xbmc.log('HOST111: {}'.format(stream_url))
        #
        #
        #     # except BaseException:
        #     #     stream_url = evaluate(stream_url)
        elif 'coverapi' in host:
            html = requests.get(host).text
            # xbmc.log('ΠΟΣΤ_html: {}'.format(html))
            postdata = re.findall(r'''['"]players['"], news_id: ['"](\d+)['"]}''', html, re.DOTALL)[0]
            # xbmc.log('ΠΟΣΤ_html: {}'.format(postdata))
            postdata = {'mod': 'players',
                        'news_id': str(postdata)}
            post_url = 'https://coverapi.store/engine/ajax/controller.php'
            post_html = requests.post(post_url, data=postdata).text.replace('\\', '')
            # xbmc.log('ΠΟΣΤ_ΔΑΤΑ: {}'.format(post_html))
            stream_url = re.findall(r'''file\s*:\s*['"](.+?)['"]''', post_html, re.DOTALL)[0]
            # xbmc.log('ΠΟΣΤ_URL: {}'.format(stream_url))
            if 'http' in stream_url:
                stream_url = stream_url + '|User-Agent=iPad&Referer={}&verifypeer=false'.format('https://coverapi.store/')
            else:
                playlist_url = 'https://coverapi.store/' + stream_url
                data = requests.get(playlist_url).json()
                # xbmc.log('ΠΟΣΤ_ΔΑΤΑ: {}'.format(data))
                comments = []
                streams = []

                data = data['playlist']
                for dat in data:
                    url = dat['file']
                    com = dat['comment']
                    comments.append(com)
                    streams.append(url)

                if len(comments) > 1:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select('[COLORgold][B]ΔΙΑΛΕΞΕ ΠΗΓΗ[/B][/COLOR]', comments)
                    if ret == -1:
                        return
                    elif ret > -1:
                        host = streams[ret]
                        # xbmc.log('@#@HDPRO:{}'.format(host))User-Agent=iPad&verifypeer=false
                        stream_url = host + '|User-Agent=iPad&Referer={}&verifypeer=false'.format('https://coverapi.store/')
                    else:
                        return

                else:
                    host = streams[0]
                    stream_url = host + '|User-Agent=iPad&Referer={}&verifypeer=false'.format('https://coverapi.store/')

    else:
        name = name.split(' [B]|')[0]

    if return_url:
        return stream_url

    try:
        liz.setArt({'icon': iconimage, 'fanart': FANART})
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(str(stream_url))
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    except BaseException:
        control.infoDialog(Lang(32012), NAME)


def evaluate(host):
    import resolveurl
    try:
        url = None
        
        if resolveurl.HostedMediaFile(host):
            url = resolveurl.resolve(host)
    
        return url
    except BaseException:
        return


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


params = init.params
mode = params.get('mode')
name = params.get('name')
iconimage = params.get('iconimage')
fanart = params.get('fanart')
description = params.get('description')
url = params.get('url')

try:
    url = unquote_plus(params["url"])
except BaseException:
    pass
try:
    name = unquote_plus(params["name"])
except BaseException:
    pass
try:
    iconimage = unquote_plus(params["iconimage"])
except BaseException:
    pass
try:
    mode = int(params["mode"])
except BaseException:
    pass
try:
    fanart = unquote_plus(params["fanart"])
except BaseException:
    pass
try:
    description = unquote_plus(params["description"])
except BaseException:
    pass

xbmc.log('{}: {}'.format(str(ID), str(VERSION)))
xbmc.log('{}: {}'.format('Mode', str(mode)))
xbmc.log('{}: {}'.format('URL', str(url)))
xbmc.log('{}: {}'.format('Name', str(name)))
xbmc.log('{}: {}'.format('ICON', str(iconimage)))

#########################################################

if mode is None:
    Main_addDir()


###############GAMATOKIDS#################
elif mode == 3:
    get_gam_genres(url)
elif mode == 4:
    gamato_kids(url)
elif mode == 12:
    # get_links(name, url, iconimage, description)
    gamato_links(url, name, iconimage, description)
elif mode == 18:
    keyb = xbmc.Keyboard('', Lang(32002))
    keyb.doModal()
    if keyb.isConfirmed():
        search = quote_plus(keyb.getText())
        url = GAMATO + "?s={}".format(search)
        gamato_kids(url)
    else:
        pass
elif mode == 20:
    gamatokids()
elif mode == 21:
    gamatokids_top(url)


##########################################

###############METAGLOTISMENO#################
elif mode == 30:
    from resources.lib.indexers import teniesonline

    teniesonline.menu()
elif mode == 33:
    from resources.lib.indexers import teniesonline

    teniesonline.get_links(name, url, iconimage, description)
elif mode == 34:
    from resources.lib.indexers import teniesonline

    teniesonline.metaglotismeno(url)
elif mode == 35:
    from resources.lib.indexers import teniesonline

    keyb = xbmc.Keyboard('', Lang(32002))
    keyb.doModal()
    if keyb.isConfirmed():
        search = quote_plus(keyb.getText())
        url = Teniesonline + "?s={}".format(search)
        teniesonline.search(url)
    else:
        pass

##############################################

elif mode == 5:
    Get_content(url)
elif mode == 6:
    search_menu()
elif mode == 26:
    Search(url)
elif mode == 29:
    search_clear()
elif mode == 28:
    Del_search(url)
elif mode == 7:
    Get_TV_Genres(url)
elif mode == 8:
    Get_random(url)
elif mode == 9:
    cache_clear()
elif mode == 13:
    Peliculas()
elif mode == 14:
    Series()
elif mode == 15:
    year(url)
elif mode == 16:
    year_TV(url)
elif mode == 17:
    Open_settings()
elif mode == 19:
    Get_epoxiakes(url)

elif mode == 40:
    downloads_root()
elif mode == 41:
    download(name, iconimage, url)

elif mode == 100:
    resolve(name, url, iconimage, description)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
