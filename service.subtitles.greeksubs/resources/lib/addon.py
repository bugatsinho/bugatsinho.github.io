# -*- coding: utf-8 -*-

'''
    Greek Subs
    Author Bugatsinho
        Credits to Lambda and Twilight0 for the original code.

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


import urllib, re, os, xbmc
from xbmc import getCleanMovieTitle
import s4f
import subztv
import yifi
import sys, urlparse
from resources.modules import control, workers

syshandle = int(sys.argv[1])
sysaddon = sys.argv[0]
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')
source = params.get('source')
url = params.get('url')
query = params.get('searchstring')
langs = params.get('languages')


class Search:

    def __init__(self):

        self.list = []

    def run(self, query=None):

        if not 'Greek' in str(langs).split(','):
            control.directory(syshandle)
            control.infoDialog(control.lang(32002).encode('utf-8'))
            return

        if query is None:
            if control.condVisibility('Player.HasVideo'):
                title = control.infoLabel('VideoPlayer.Title')

                if re.search(r'[^\x00-\x7F]+', title) is not None:
                    title = control.infoLabel('VideoPlayer.OriginalTitle')
                year = control.infoLabel('VideoPlayer.Year')

                tvshowtitle = control.infoLabel('VideoPlayer.TVshowtitle')

                season = control.infoLabel('VideoPlayer.Season')

                episode = control.infoLabel('VideoPlayer.Episode')
                try:
                    imdb = control.infoLabel('VideoPlayer.IMDBNumber')
                    if not imdb:
                        imdb = '0'
                except BaseException:
                    imdb = '0'
            else:
                title = xbmc.getInfoLabel("ListItem.OriginalTitle")
                year = xbmc.getInfoLabel("ListItem.Year")
                tvshowtitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
                season = xbmc.getInfoLabel("ListItem.Season")
                episode = xbmc.getInfoLabel("ListItem.Episode")
                #labelType = xbmc.getInfoLabel("ListItem.DBTYPE")
                try:
                    imdb = control.infoLabel('ListItem.IMDBNumber')
                    # xbmc.log('$#$QUERY-NONE-IMDB: %s' % imdb, xbmc.LOGNOTICE)
                    if not imdb:
                        imdb = '0'
                except BaseException:
                    imdb = '0'

            if 's' in episode.lower():
                season, episode = '0', episode[-1:]

            if not tvshowtitle == '':  # episode
                query = '%s S%02dE%02d/imdb=%s' % (tvshowtitle, int(season), int(episode), str(imdb))

            elif not year == '':  # movie
                query = '%s (%s)/imdb=%s' % (title, year, str(imdb))

            elif '(S' in title:
                query = '%s/imdb=%s' % (title, str(imdb))

            else:  # file
                query, year = getCleanMovieTitle(title)
                if not year == '':
                    query = '%s (%s)/imdb=%s' % (query, year, str(imdb))
            # xbmc.log('$#$QUERY-NONE-FINAL: %s' % query, xbmc.LOGNOTICE)

        else:
            query = '%s/imdb=0' % re.sub('[\(|\)]', '', query)
            # xbmc.log('$#$QUERY: %s' % query, xbmc.LOGNOTICE)

        self.query = query
        # xbmc.log('$#$QUERY: %s' % query, xbmc.LOGNOTICE)

        threads = []

        threads.append(workers.Thread(self.subztv))
        threads.append(workers.Thread(self.s4f))
        threads.append(workers.Thread(self.yifi))

        [i.start() for i in threads]
        [i.join() for i in threads]

        # for i in range(0, 10 * 2):
        #     try:
        #         is_alive = [x.is_alive() for x in threads]
        #         if all(x is False for x in is_alive):
        #             break
        #         if control.aborted is True:
        #             break
        #         control.sleep(500)
        #     except BaseException:
        #         pass

        if len(self.list) == 0:
            control.directory(syshandle)
            return

        f = []

        f += [i for i in self.list if i['source'] == 'subztv']
        f += [i for i in self.list if i['source'] == 's4f']
        f += [i for i in self.list if i['source'] == 'yifi']

        self.list = sorted(f, key=lambda k: k['rating'], reverse=True)

        for i in self.list:

            try:

                if i['source'] == 'subztv':
                    i['name'] = '[subztv] %s' % i['name']

                elif i['source'] == 's4f':
                    i['name'] = '[S4F] %s' % i['name']

                elif i['source'] == 'yifi':
                    i['name'] = '[yifi] %s' % i['name']
            except BaseException:
                pass

        for i in self.list:

            try:
                name, url, source, rating = i['name'], i['url'], i['source'], i['rating']

                u = {'action': 'download', 'url': url, 'source': source}
                u = '%s?%s' % (sysaddon, urllib.urlencode(u))

                item = control.item(label='Greek', label2=name, iconImage=str(rating), thumbnailImage='el')
                item.setProperty('sync', 'false')
                item.setProperty('hearing_imp', 'false')

                control.addItem(handle=syshandle, url=u, listitem=item, isFolder=False)
            except BaseException:
                pass

        control.directory(syshandle)

    def s4f(self):
        self.list.extend(s4f.s4f().get(self.query))

    def subztv(self):
        self.list.extend(subztv.subztv().get(self.query))

    def yifi(self):
        self.list.extend(yifi.yifi().get(self.query))


class Download:

    def __init__(self):

        pass

    def run(self, url, source):

        path = os.path.join(control.dataPath, 'temp')
        try:
            path = path.decode('utf-8')
        except Exception:

            pass

        control.deleteDir(control.join(path, ''), force=True)

        control.makeFile(control.dataPath)

        control.makeFile(path)

        if source == 's4f':

            subtitle = s4f.s4f().download(path, url)

        elif source == 'subztv':

            subtitle = subztv.subztv().download(path, url)

        elif source == 'yifi':

            subtitle = yifi.yifi().download(path, url)

        else:

            subtitle = None

        if subtitle is not None:
            item = control.item(label=subtitle)
            control.addItem(handle=syshandle, url=subtitle, listitem=item, isFolder=False)

        control.directory(syshandle)
