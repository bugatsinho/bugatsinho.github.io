# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib, re, os
from urlparse import urljoin
from resources.modules import cache, cleantitle, client, control


class subzxyz:
    def __init__(self):
        self.list = []

    def get(self, query):
        try:
            match = re.findall('(.+?) \((\d{4})\)/imdb=$', query)

            if len(match) > 0:

                title, year = match[0][0], match[0][1]

                query = ' '.join(urllib.unquote_plus(re.sub('%\w\w', ' ', urllib.quote_plus(title))).split())

                url = 'https://subz.xyz/search?q=%s' % urllib.quote_plus(query)

                result = client.request(url)
                result = re.sub(r'[^\x00-\x7F]+', ' ', result)

                url = client.parseDOM(result, 'section', attrs={'class': 'movies'})[0]
                url = re.findall('(/movies/\d+)', url)
                url = [x for y, x in enumerate(url) if x not in url[:y]]
                url = [urljoin('https://subz.xyz', i) for i in url]
                url = url[:3]

                for i in url:
                    c = cache.get(self.cache, 2200, i)

                    if c is not None:
                        if cleantitle.get(c[0]) == cleantitle.get(title) and c[1] == year:
                            try:
                                item = self.r
                            except BaseException:
                                item = client.request(i)
                            break


            else:

                title, season, episode = re.findall('(.+?) S(\d+)E(\d+)/imdb=$', query)[0]

                season, episode = '%01d' % int(season), '%01d' % int(episode)

                query = ' '.join(urllib.unquote_plus(re.sub('%\w\w', ' ', urllib.quote_plus(title))).split())

                url = 'https://subz.xyz/search?q=%s' % urllib.quote_plus(query)

                result = client.request(url)
                result = re.sub(r'[^\x00-\x7F]+', ' ', result)

                url = client.parseDOM(result, 'section', attrs={'class': 'tvshows'})[0]
                url = re.findall('(/series/\d+)', url)
                url = [x for y, x in enumerate(url) if x not in url[:y]]
                url = [urljoin('https://subz.xyz', i) for i in url]
                url = url[:3]

                for i in url:
                    c = cache.get(self.cache, 2200, i)

                    if c is not None:
                        if cleantitle.get(c[0]) == cleantitle.get(title):
                            item = i
                            break

                item = '%s/seasons/%s/episodes/%s' % (item, season, episode)
                item = client.request(item)

            item = re.sub(r'[^\x00-\x7F]+', ' ', item)
            items = client.parseDOM(item, 'tr', attrs={'data-id': '.+?'})
        except BaseException:
            return

        for item in items:
            try:

                r = client.parseDOM(item, 'td', attrs={'class': '.+?'})[-1]

                url = client.parseDOM(r, 'a', ret='href')[0]
                url = client.replaceHTMLCodes(url)
                url = url.replace("'","").encode('utf-8')
                
                name = url.split('/')[-1].strip()
                name = re.sub('\s\s+', ' ', name)
                name = name.replace('_','').replace('%20','.')
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'source': 'subzxyz', 'rating': 5})
            except BaseException:
                pass

        return self.list

    def cache(self, i):

        try:
            self.r = client.request(i)
            self.r = re.sub(r'[^\x00-\x7F]+', ' ', self.r)
            t = re.findall('(?:\"|\')original_title(?:\"|\')\s*:\s*(?:\"|\')(.+?)(?:\"|\')', self.r)[0]
            y = re.findall('(?:\"|\')year(?:\"|\')\s*:\s*(?:\"|\'|)(\d{4})', self.r)[0]
            return (t, y)
        except BaseException:
            pass

    def download(self, path, url):

        try:

            result = client.request(url)

            # f = os.path.splitext(urlparse.urlparse(url).path)[1][1:]
            f = os.path.join(path, url.rpartition('/')[2])

            with open(f, 'wb') as subFile:
                subFile.write(result)

            dirs, files = control.listDir(path)

            if len(files) == 0:
                return

            if not f.lower().endswith('.rar'):
                control.execute('Extract("%s","%s")' % (f, path))

            if control.infoLabel('System.Platform.Windows'):
                conversion = urllib.quote
            else:
                conversion = urllib.quote_plus

            if f.lower().endswith('.rar'):

                uri = "rar://{0}/".format(conversion(f))
                dirs, files = control.listDir(uri)

            else:

                for i in range(0, 10):

                    try:
                        dirs, files = control.listDir(path)
                        if len(files) > 1:
                            break
                        if control.aborted is True:
                            break
                        control.wait(1)
                    except BaseException:
                        pass

            filename = [i for i in files if any(i.endswith(x) for x in ['.srt', '.sub'])][0].decode('utf-8')
            subtitle = os.path.join(path, filename)

            if f.lower().endswith('.rar'):

                content = control.openFile(uri + filename).read()

                with open(subtitle, 'wb') as subFile:
                    subFile.write(content)

                control.deleteFile(f)

                return subtitle

            else:

                control.deleteFile(f)

                return subtitle

        except BaseException:

            pass
