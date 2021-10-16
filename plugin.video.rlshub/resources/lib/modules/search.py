# -*- coding: utf-8 -*-

'''
    Based on Covenant's search
    Author Bugatsinho

        License summary below, for more details please read license.txt file

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 2 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import xbmc
import json
import random
import sys
import re
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import client
from resources.lib.modules import view
from resources.lib.modules.addon import Addon
import six
# from six.moves import urllib
from six.moves.urllib_parse import urlparse, urljoin, quote_plus, unquote, unquote_plus

addon = Addon('plugin.video.rlshub', sys.argv)
Lang = control.lang
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
NAME = ADDON.getAddonInfo('name')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/resources/icons/"
base = control.setting('domain')
BASE_URL = 'http://%s' % base.lower()
OLD_URL = 'http://old3.proxybb.com/'

try:
    from sqlite3 import dbapi2 as database
except ImportError:
    from pysqlite2 import dbapi2 as database


def Search_bb(url):
    if 'new' == url:
        keyboard = xbmc.Keyboard()
        keyboard.setHeading(control.lang(32002).encode('utf-8'))
        keyboard.doModal()
        if keyboard.isConfirmed():
            _query = keyboard.getText()
            query = _query.encode('utf-8')
            try:
                query = quote_plus(query)
                referer_link = 'http://search.proxybb.com?s={0}'.format(query)

                url = 'http://search.proxybb.com/Home/GetPost?phrase={0}&pindex=1&content=true&type=Simple&rad=0.{1}'
                url = url.format(query, random.randint(33333333333333333, 99999999999999999))
                #########save in Database#########
                if six.PY2:
                    term = unquote_plus(query).decode('utf-8')
                else:
                    term = unquote_plus(query)

                dbcon = database.connect(control.searchFile)
                dbcur = dbcon.cursor()
                dbcur.execute("DELETE FROM Search WHERE search = ?", (term,))
                dbcur.execute("INSERT INTO Search VALUES (?,?)", (url, term))
                dbcon.commit()
                dbcur.close()

                #########search in website#########
                headers = {'Referer': referer_link,
                           'X-Requested-With': 'XMLHttpRequest'}
                first = client.request(referer_link, headers=headers)
                xbmc.sleep(10)
                html = client.request(url, headers=headers)
                posts = json.loads(html)['results']
                posts = [(i['post_name'], i['post_title'], i['post_content'], i['domain']) for i in posts if i]
                for movieUrl, title, infos, domain in posts:
                    if not 'imdb.com/title' in infos:
                        continue
                    base = BASE_URL if 'old' not in domain else OLD_URL
                    movieUrl = urljoin(base, movieUrl) if not movieUrl.startswith('http') else movieUrl
                    title = title.encode('utf-8')
                    infos = infos.replace('\\', '')
                    try:
                        img = client.parseDOM(infos, 'img', ret='src')[0]
                        img = img.replace('.ru', '.to')
                    except:
                        img = ICON

                    try:
                        fan = client.parseDOM(infos, 'img', ret='src')[1]
                    except:
                        fan = FANART

                    try:
                        # desc = client.parseDOM(infos, 'div', attrs={'class': 'entry-summary'})[0]
                        desc = re.findall(r'>(Plot:.+?)</p>', infos, re.DOTALL)[0]
                    except:
                        desc = 'N/A'

                    desc = Sinopsis(desc)
                    # title = six.python_2_unicode_compatible(six.ensure_str(title))
                    title = six.ensure_str(title, 'utf-8')
                    name = '[B][COLORgold]{0}[/COLOR][/B]'.format(title)

                    mode = 'GetPack' if re.search(r'\s+S\d+\s+', name) else 'GetLinks'
                    addon.add_directory(
                        {'mode': mode, 'url': movieUrl, 'img': img, 'plot': desc},
                        {'title': name, 'plot': desc},
                        [(control.lang(32007).encode('utf-8'),
                          'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                         (control.lang(32008).encode('utf-8'),
                          'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                         (control.lang(32009).encode('utf-8'),
                          'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                        img=img, fanart=fan)

                # if 'olderEntries' in ref_html:
                pindex = int(re.search('pindex=(\d+)&', url).group(1)) + 1
                np_url = re.sub(r'&pindex=\d+&', '&pindex={0}&'.format(pindex), url)
                rand = random.randint(33333333333333333, 99999999999999999)
                np_url = re.sub(r'&rand=0\.\d+$', '&rand={}'.format(rand), np_url)
                addon.add_directory(
                    {'mode': 'search_bb', 'url': np_url + '|Referer={0}|nextpage'.format(referer_link)},
                    {'title': control.lang(32010).encode('utf-8')},
                    img=IconPath + 'next_page.png', fanart=FANART)

            except BaseException:
                control.infoDialog(control.lang(32022).encode('utf-8'), NAME, ICON, 5000)

    elif '|nextpage' in url:
        url, referer_link, np = url.split('|')
        referer_link = referer_link.split('=', 1)[1]
        headers = {'Referer': referer_link,
                   'X-Requested-With': 'XMLHttpRequest'}
        first = client.request(referer_link, headers=headers)
        xbmc.sleep(10)
        html = client.request(url, headers=headers)
        # xbmc.log('NEXT HTMLLLLL: {}'.format(html))
        posts = json.loads(html)['results']
        posts = [(i['post_name'], i['post_title'], i['post_content'], i['domain']) for i in posts if i]
        for movieUrl, title, infos, domain in posts:
            base = BASE_URL if 'old' not in domain else OLD_URL
            movieUrl = urljoin(base, movieUrl) if not movieUrl.startswith('http') else movieUrl
            title = six.ensure_str(title, 'utf-8')
            infos = infos.replace('\\', '')
            try:
                img = client.parseDOM(infos, 'img', ret='src')[0]
                img = img.replace('.ru', '.to')
            except:
                img = ICON

            try:
                fan = client.parseDOM(infos, 'img', ret='src')[1]
            except:
                fan = FANART

            try:
                desc = re.search(r'>(Plot:.+?)</p>', infos, re.DOTALL).group(0)
            except:
                desc = 'N/A'

            desc = Sinopsis(desc)
            name = '[B][COLORgold]{0}[/COLOR][/B]'.format(title)
            mode = 'GetPack' if re.search(r'\s+S\d+\s+', name) else 'GetLinks'
            addon.add_directory(
                {'mode': mode, 'url': movieUrl, 'img': img, 'plot': desc},
                {'title': name, 'plot': desc},
                [(control.lang(32007).encode('utf-8'),
                  'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                 (control.lang(32008).encode('utf-8'),
                  'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                 (control.lang(32009).encode('utf-8'),
                  'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                img=img, fanart=fan)

        # if 'olderEntries' in ref_html:
        pindex = int(re.search('pindex=(\d+)&', url).groups()[0]) + 1
        np_url = re.sub('&pindex=\d+&', '&pindex={0}&'.format(pindex), url)
        rand = random.randint(33333333333333333, 99999999999999999)
        np_url = re.sub(r'&rand=0\.\d+$', '&rand={}'.format(rand), np_url)
        addon.add_directory(
            {'mode': 'search_bb', 'url': np_url + '|Referer={0}|nextpage'.format(referer_link)},
            {'title': control.lang(32010).encode('utf-8')},
            img=IconPath + 'next_page.png', fanart=FANART)

    else:
        try:
            url = quote_plus(url)
            referer_link = 'http://search.proxybb.com?s={0}'.format(url)
            headers = {'Referer': referer_link,
                       'X-Requested-With': 'XMLHttpRequest'}
            # first = scraper.get('http://rlsbb.ru', headers=headers).text
            xbmc.sleep(10)
            s_url = 'http://search.proxybb.com/Home/GetPost?phrase={0}&pindex=1&content=true&type=Simple&rad=0.{1}'
            s_url = s_url.format(url, random.randint(33333333333333333, 99999999999999999))
            html = client.request(s_url, headers=headers)
            posts = json.loads(html)['results']
            posts = [(i['post_name'], i['post_title'], i['post_content'], i['domain']) for i in posts if i]
            for movieUrl, title, infos, domain in posts:
                base = BASE_URL if 'old' not in domain else OLD_URL
                movieUrl = urljoin(base, movieUrl) if not movieUrl.startswith('http') else movieUrl
                title = six.ensure_str(title, 'utf-8')
                infos = infos.replace('\\', '')
                try:
                    img = client.parseDOM(infos, 'img', ret='src')[0]
                    img = img.replace('.ru', '.to')
                except:
                    img = ICON

                try:
                    fan = client.parseDOM(infos, 'img', ret='src')[1]
                except:
                    fan = FANART

                try:
                    desc = re.search(r'>(Plot:.+?)</p>', infos, re.DOTALL).group(0)
                except:
                    desc = 'N/A'

                desc = Sinopsis(desc)
                name = '[B][COLORgold]{0}[/COLOR][/B]'.format(title)

                mode = 'GetPack' if re.search(r'\s+S\d+\s+', name) else 'GetLinks'
                addon.add_directory(
                    {'mode': mode, 'url': movieUrl, 'img': img, 'plot': desc},
                    {'title': name, 'plot': desc},
                    [(control.lang(32007).encode('utf-8'),
                      'RunPlugin(plugin://plugin.video.rlshub/?mode=settings)',),
                     (control.lang(32008).encode('utf-8'),
                      'RunPlugin(plugin://plugin.video.rlshub/?mode=ClearCache)',),
                     (control.lang(32009).encode('utf-8'),
                      'RunPlugin(plugin://plugin.video.rlshub/?mode=setviews)',)],
                    img=img, fanart=fan)

            pindex = int(re.search('pindex=(\d+)&', s_url).groups()[0]) + 1
            np_url = re.sub('&pindex=\d+&', '&pindex={0}&'.format(pindex), s_url)
            rand = random.randint(33333333333333333, 99999999999999999)
            np_url = re.sub(r'&rand=0\.\d+$', '&rand={}'.format(rand), np_url)
            addon.add_directory(
                {'mode': 'search_bb', 'url': np_url + '|Referer={0}|nextpage'.format(referer_link)},
                {'title': control.lang(32010).encode('utf-8')},
                img=IconPath + 'next_page.png', fanart=FANART)

        except BaseException:
            control.infoDialog(control.lang(32022).encode('utf-8'), NAME, ICON, 5000)

    control.content(int(sys.argv[1]), 'videos')
    control.directory(int(sys.argv[1]))
    view.setView('videos', {'skin.estuary': 55, 'skin.confluence': 500})


def del_search(query):
    control.busy()
    # xbmc.log('$#$DEL-search:%s' % query, xbmc.LOGNOTICE)
    search = quote_plus(query)

    dbcon = database.connect(control.searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("DELETE FROM Search WHERE search = ?", (search,))
    dbcon.commit()
    dbcur.close()
    control.refresh()
    control.idle()


def search_clear():
    cache.delete(control.searchFile, withyes=False)
    control.refresh()
    control.idle()


def Sinopsis(txt):
    OPEN = six.ensure_str(txt, 'utf-8')
    try:
        # try:
        #     if 'Plot:' in OPEN:
        #         Sinopsis = re.findall('(Plot:.+?)</p>', OPEN, re.DOTALL)[0]
        #     else:
        #         Sinopsis = re.findall('</p>\n<p>(.+?)</p><p>', OPEN, re.DOTALL)[0]
        #
        # except:
        #     Sinopsis = re.findall('</p>\n<p>(.+?)</p>\n<p style', OPEN, re.DOTALL)[0]
        part = re.sub('<.*?>', '', OPEN)
        part = re.sub(r'\.\s+', '.', part)
        desc = clear_Title(part)
        if six.PY2:
            desc = desc.decode('ascii', errors='ignore')
        else:
            desc = six.python_2_unicode_compatible(six.ensure_str(desc))
        return desc
    except BaseException:
        return 'N/A'


def clear_Title(txt):
    txt = re.sub('<.+?>', '', txt)
    txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':')
    txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
    txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
    txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('\t', ' ').replace('\n', ' ')
    return txt