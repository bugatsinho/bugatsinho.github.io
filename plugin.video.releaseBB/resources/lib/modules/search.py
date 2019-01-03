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
import urllib
import json
import random
import urlparse
import sys
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import client
from t0mm0.common.addon import Addon

addon = Addon('plugin.video.releaseBB', sys.argv)
Lang = control.lang
ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
NAME = ADDON.getAddonInfo('name')
version = ADDON.getAddonInfo('version')
IconPath = control.addonPath + "/resources/icons/"
base = control.setting('domain')
BASE_URL = 'http://%s' % base.lower()

try:
    from sqlite3 import dbapi2 as database
except ImportError:
    from pysqlite2 import dbapi2 as database


def Search_bb(url):
    if 'new' in url:
        keyboard = xbmc.Keyboard()
        keyboard.setHeading('[COLOR green]Release BB Search[/COLOR]')
        keyboard.doModal()
        if keyboard.isConfirmed():
            _query = keyboard.getText()
            query = _query.encode('utf-8')
            try:
                from resources.lib.modules import cfscrape
                scraper = cfscrape.create_scraper()
                headers = {'User-Agent': client.randomagent(),
                           'Referer': 'http://rlsbb.ru'}
                query = urllib.quote_plus(query).replace('+', '%2B')
                url = 'http://search.rlsbb.ru/lib/search452341986049741.php?phrase=%s&pindex=1&radit=0.%s'
                url = url % (query, random.randint(00000000000000001, 99999999999999999))
                #########save in Database#########
                term = urllib.unquote_plus(query).decode('utf-8')
                dbcon = database.connect(control.searchFile)
                dbcur = dbcon.cursor()
                dbcur.execute("DELETE FROM Search WHERE search = ?", (term,))
                dbcur.execute("INSERT INTO Search VALUES (?,?)", (url, term))
                dbcon.commit()
                dbcur.close()

                #########search in website#########
                html = scraper.get(url, headers=headers).content
                posts = json.loads(html)['results']
                posts = [(i['post_name'], i['post_title']) for i in posts if i]
                for movieUrl, title in posts:
                    movieUrl = urlparse.urljoin(BASE_URL, movieUrl)
                    title = title.encode('utf-8')
                    addon.add_directory({'mode': 'GetLinks', 'url': movieUrl},
                                        {'title': title}, img=IconPath + 'search.png', fanart=FANART)

            except BaseException:
                control.infoDialog(
                    "[COLOR red][B]Sorry there was a problem![/B][/COLOR]\n"
                    "[COLOR lime][B]Please try again!![/B][/COLOR]",
                    NAME, ICON, 3000)
    else:
        try:
            from resources.lib.modules import cfscrape
            scraper = cfscrape.create_scraper()
            headers = {'User-Agent': client.randomagent(),
                       'Referer': 'http://rlsbb.ru'}
            html = scraper.get(url, headers=headers).content
            posts = json.loads(html)['results']
            posts = [(i['post_name'], i['post_title']) for i in posts if i]
            for movieUrl, title in posts:
                movieUrl = urlparse.urljoin(BASE_URL, movieUrl)
                title = title.encode('utf-8')
                addon.add_directory({'mode': 'GetLinks', 'url': movieUrl},
                                    {'title': title}, img=IconPath + 'search.png', fanart=FANART)
        except BaseException:
            control.infoDialog(
                "[COLOR red][B]Sorry there was a problem![/B][/COLOR]\n[COLOR lime][B]Please try again!![/B][/COLOR]",
                NAME, ICON, 3000)


def del_search(query):
    control.busy()
    #xbmc.log('$#$DEL-search:%s' % query, xbmc.LOGNOTICE)
    search = urllib.quote_plus(query)

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
