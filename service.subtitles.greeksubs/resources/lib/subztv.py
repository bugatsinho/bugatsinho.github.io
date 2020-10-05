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
import json
import urllib, re, os, xbmc
import urlparse
from resources.modules import cleantitle, client, control

'''''''''
Disables InsecureRequestWarning: Unverified HTTPS request is being made warnings.
'''''''''
import requests

'''
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
'''


class subztv:
    def __init__(self):
        self.list = []
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

        self.s = requests.Session()
        self.s.headers.update(self.hdr)

    def get(self, query):
        try:
            query, imdb = query.split('/imdb=')
            match = re.findall(r'^(?P<title>.+)[\s+\(|\s+](?P<year>\d{4})', query)

            cookie = self.s.get('https://greeksubs.net/', headers=self.hdr).cookies
            cj = requests.utils.dict_from_cookiejar(cookie)

            if len(match) > 0:

                title, year = match[0][0], match[0][1]

                if imdb.startswith('tt'):
                    frame = 'https://greeksubs.net/view/%s' % imdb
                    r = self.s.get(frame)
                    r = re.sub(r'[^\x00-\x7F]+', ' ', r.content)
                else:
                    url = 'https://greeksubs.net/search/%s/movies' % urllib.quote(title)

                    data = self.s.get(url).content
                    data = client.parseDOM(data, 'span', attrs={'class': 'h5'})
                    data = [(client.parseDOM(i, 'a')[0],
                             client.parseDOM(i, 'a', ret='href')[0]) for i in data if i]

                    frame = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]

                    r = self.s.get(frame).text
                    r = re.sub(r'[^\x00-\x7F]+', ' ', r)

                secCode = client.parseDOM(r, 'input', ret='value', attrs={'id': 'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                items = client.parseDOM(items, 'tr')

            else:
                title, season, episode = re.findall(r'^(?P<title>.+)\s+S(\d+)E(\d+)', query, re.I)[0]
                # xbmc.log('$#$MATCH-SUBZ: %s | %s | %s' % (title, season, episode), xbmc.LOGNOTICE)
                hdlr = 'season-{:01d}-episode-{:01d}'.format(int(season), int(episode))

                if imdb.startswith('tt'):
                    r = self.s.get('https://greeksubs.net/view/%s' % imdb).text
                    # r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                    frames = client.parseDOM(r, 'a', ret='href')
                    link = [i for i in frames if hdlr in i]

                    if not link:
                        frame = 'https://greeksubs.net/view/%s' % imdb
                    else:
                        frame = link[0]
                else:
                    if len(imdb) > 1:
                        baseurl = ' https://api.thetvdb.com/login'
                        series_url = 'https://api.thetvdb.com/series/%s'
                        greek_api = '7d4261794838bb48a3122381811ecb42'
                        user_key = 'TJXB86PGDBYN0818'
                        username = 'filmnet'

                        _headers = {'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                    'Connection': 'close'}

                        post = {"apikey": greek_api, "username": username, "userkey": user_key}

                        # data = requests.post(baseurl, data=json.dumps(post), headers=_headers).json()
                        data = client.request(baseurl, post=json.dumps(post), headers=_headers)
                        auth = 'Bearer %s' % urllib.unquote_plus(json.loads(data)['token'])
                        _headers['Authorization'] = auth

                        series_data = client.request(series_url % imdb, headers=_headers)
                        imdb = json.loads(series_data)['data']['imdbId']
                        r = self.s.get('https://greeksubs.net/view/%s' % imdb).content
                        # xbmc.log('$#$MATCH-SUBZ-RRR-source: %s' % r)
                        #r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                        frames = client.parseDOM(r, 'a', ret='href')
                        frame = [i for i in frames if hdlr in i][0]
                    else:
                        url = 'https://greeksubs.net/search/%s/tv' % urllib.quote(title)

                        data = self.s.get(url).content
                        data = client.parseDOM(data, 'span', attrs={'class': 'h5'})
                        data = [(client.parseDOM(i, 'a')[0],
                                 client.parseDOM(i, 'a', ret='href')[0]) for i in data if i]

                        serie_link = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]
                        # xbmc.log('$#$SERIE-LINK: %s' % serie_link)
                        imdbid = re.findall('\/(tt\d+)\/', serie_link)[0]
                        r = self.s.get('https://greeksubs.net/view/%s' % imdbid).content
                        frames = client.parseDOM(r, 'a', ret='href')
                        frame = [i for i in frames if hdlr in i][0]

                frame = client.replaceHTMLCodes(frame)
                frame = frame.encode('utf-8')
                r = self.s.get(frame).text
                # r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                secCode = client.parseDOM(r, 'input', ret='value', attrs={'id': 'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                items = client.parseDOM(items, 'tr')

        except BaseException:
            return

        for item in items:
            try:
                item = item.encode('utf-8')
                # xbmc.log('$#$MATCH-SUBZ-ITEM: {}'.format(item))
                try:
                    imdb = re.search(r'\/(tt\d+)\/', frame).groups()[0]
                except BaseException:
                    imdb = re.search(r'\/(tt\d+)', frame).groups()[0]

                data = re.findall(r'''downloadMe\(['"](\w+\-\w+).+?label.+?>(\d+).+?<td>(.+?)</td''',
                                  str(item), re.I | re.DOTALL)[0]
                name = data[2]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')
                url = 'https://greeksubs.net/dll/{}/0/{}'.format(data[0], secCode)
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                down = data[1]
                rating = self._rating(down)

                self.list.append(
                    {'name': name, 'url': '%s|%s|%s|%s|%s|%s' % (frame, url, cj['__cfduid'], cj['PHPSESSID'], name, imdb),
                     'source': 'subztv', 'rating': rating})

            except BaseException:
                pass

        return self.list

    def _rating(self, downloads):
        try:
            rating = int(downloads)
        except BaseException:
            rating = 0

        if rating < 10:
            rating = 1
        elif 10 >= rating < 20:
            rating = 2
        elif 20 >= rating < 30:
            rating = 3
        elif 30 >= rating < 40:
            rating = 4
        elif rating >= 40:
            rating = 5

        return rating

    def download(self, path, url):

        try:
            frame, url, cjcfduid, cjphp, sub_, imdb_ = url.split('|')
            # xbmc.log('$#$ FRAME: %s | URL: %s | COOKIE: %s | SUB: %s | imdb: %s | ' % (frame, url, cjcfduid, sub_, imdb_))

            sub_ = urllib.unquote_plus(sub_)

            self.s.cookies.update({'__cfduid': cjcfduid, 'PHPSESSID': cjphp})
            # xbmc.log('$#$ FRAME-COOKIES: %s' % self.s.cookies)

            self.s.headers['Referer'] = frame
            init = self.s.get(url).text
            try:
                imdb = client.parseDOM(init, 'input', ret='value', attrs={'name': 'uid'})[0]
            except IndexError:
                imdb = imdb_
            try:
                sub_name = client.parseDOM(init, 'input', ret='value', attrs={'name': 'output'})[0]
            except IndexError:
                sub_name = '{}.srt'.format(sub_)

            self.s.headers.update({'Referer': url, 'Origin': 'https://subztv.online'})

            # xbmc.log('$#$ FRAME-HEADERS: %s' % self.s.headers, xbmc.LOGNOTICE)
            post = {"langcode": "el",
                    "uid": imdb,
                    "output": sub_name.lower(),
                    "dll": "1"}
            # post = urllib.urlencode(post)
            # xbmc.log('$#$ FRAME-POST: %s' % post)

            result = self.s.post(url, data=post)
            #xbmc.log('$#$POST-RESUL: %s' % result.content)
            f = os.path.join(path, urllib.quote(sub_) + '.srt')
            with open(f, 'wb') as subFile:
                subFile.write(result.content)

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

                return subtitle

            else:

                return subtitle

        except BaseException:
            pass

  
