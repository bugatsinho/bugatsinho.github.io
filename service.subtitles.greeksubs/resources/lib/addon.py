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


import sys, re, os, xbmc, six
from xbmc import getCleanMovieTitle
from resources.lib import s4f, subztv, yifi
from six.moves.urllib_parse import urlencode
from resources.modules import control, workers
import concurrent.futures
try:
    from urlparse import parse_qsl
except ImportError:
    from urllib.parse import parse_qsl

syshandle = int(sys.argv[1])
sysaddon = sys.argv[0]
params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
source = params.get('source')
url = params.get('url')
query = params.get('searchstring')
langs = params.get('languages')


class Search:

    def __init__(self):

        self.list = list()

    def run(self, query=None):

        if not 'Greek' in str(langs).split(','):
            control.directory(syshandle)
            control.infoDialog(control.lang(32002).encode('utf-8'))
            return

        if control.kodi_version() >= 18.0 and not\
                control.conditional_visibility('System.HasAddon(vfs.libarchive)')\
                and not (control.condVisibility('System.Platform.Linux')):
            control.execute('InstallAddon(vfs.libarchive)')

        if not control.conditional_visibility('System.HasAddon(script.module.futures)') and six.PY2:
            if 17.0 <= control.kodi_version() <= 18.9:
                control.execute('InstallAddon(script.module.futures)')
                control.sleep(1500)


        if query:
            query = '{}/imdb=0'.format(re.sub(r'[\(|\)]', '', query))
            # xbmc.log('$#$QUERY-ELSE: %s' % query, xbmc.LOGINFO)
        else:
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
                    query = '{} ({})/imdb={}'.format(query, year, str(imdb))

        self.query = six.ensure_str(query, encoding='utf-8')

        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            query = self.query
            threads = [
                executor.submit(self.subztv, query),
                executor.submit(self.s4f, query),
                executor.submit(self.yifi, query)
            ]

            for future in concurrent.futures.as_completed(threads):

                item = future.result()

                if not item:
                    continue

                self.list.extend(item)
        # threads = []
        # if control.setting('provider.subztv.club'):
        #     threads.append(workers.Thread(self.subztv))
        # xbmc.log('$#$THREAD1: %s' % threads)
        # if control.setting('provider.s4f'):
        #     threads.append(workers.Thread(self.s4f))
        # xbmc.log('$#$THREAD2: %s' % threads)
        # if control.setting('provider.yifi'):
        #     threads.append(workers.Thread(self.yifi))
        # xbmc.log('$#$THREAD3: %s' % threads)
        #
        # [i.start() for i in threads]
        # [i.join() for i in threads]
        self.list = [i for i in self.list if i]

        f = []

        f += [i for i in self.list if i['source'] == 'subztv']

        f += [i for i in self.list if i['source'] == 's4f']

        f += [i for i in self.list if i['source'] == 'yifi']

        self.list = sorted(f, key=lambda k: k['rating'], reverse=True)
        for i in self.list:
            try:

                if i['source'] == 'subztv':
                    i['name'] = u'[SUBZ] {0}'.format(i['name'])

                elif i['source'] == 's4f':
                    i['name'] = u'[S4F] {0}'.format(i['name'])

                elif i['source'] == 'yifi':
                    i['name'] = u'[YIFI] {0}'.format(i['name'])
            except BaseException:
                pass

        for i in self.list:
            try:
                u = {'action': 'download', 'url': i['url'], 'source': i['source']}
                u = '{0}?{1}'.format(sysaddon, urlencode(u))
                item = control.item(label='Greek', label2=i['name'])
                item.setArt({'icon': str(i['rating'])[:1], 'thumb': 'el'})
                item.setProperty('hearing_imp', 'false')
                control.addItem(handle=syshandle, url=u, listitem=item, isFolder=False)
            except BaseException:
                pass

        control.directory(syshandle)

    def s4f(self, query=None):

        if not query:
            query = self.query

        try:

            if control.setting('provider.s4f') == 'false':
                raise TypeError

            result = s4f.s4f().get(query)

            return result

        except TypeError:

            pass
        # self.list.extend(s4f.s4f().get(self.query))

    def subztv(self, query=None):
        if not query:
            query = self.query

        try:

            if control.setting('provider.subztv') == 'false':
                raise TypeError

            result = subztv.subztv().get(query)

            return result

        except TypeError:
            pass
        # self.list.extend(subztv.subztv().get(self.query))

    def yifi(self, query=None):
        if not query:
            query = self.query

        try:

            if control.setting('provider.yifi') == 'false':
                raise TypeError

            result = yifi.yifi().get(query)

            return result

        except TypeError:

            pass
        # self.list.extend(yifi.yifi().get(self.query))


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
