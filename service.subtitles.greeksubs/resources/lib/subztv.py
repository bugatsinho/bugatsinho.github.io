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
from __future__ import print_function
import json
import os
import re
import six
import xbmc
from resources.modules import cleantitle, client, control
from six.moves.urllib_parse import unquote_plus, quote_plus, quote

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
        self.baseurl = 'https://greeksubs.net/'
        self.list = []
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

        self.s = requests.Session()
        self.s.headers.update(self.hdr)

    def get(self, query):
        try:
            query, imdb = query.split('/imdb=')
            match = re.findall(r'^(?P<title>.+)[\s+\(|\s+](?P<year>\d{4})', query)
            # xbmc.log('MATCH: {}'.format(match))
            cookie = self.s.get(self.baseurl, headers=self.hdr)

            cj = requests.utils.dict_from_cookiejar(cookie.cookies)

            if len(match) > 0:

                title, year = match[0][0], match[0][1]

                if imdb.startswith('tt'):
                    frame = self.baseurl + 'view/{}'.format(imdb)
                    r = self.s.get(frame).text
                    if six.PY2:
                        r = re.sub(r'[^\x00-\x7F]+', ' ', r)

                    # try:
                    #     r = r.decode('utf-8', errors='replace')
                    # except AttributeError:
                    #     pass
                else:
                    url = self.baseurl + 'search/{}/movies'.format(quote(title))

                    data = self.s.get(url).text
                    data = client.parseDOM(data, 'span', attrs={'class': 'h5'})
                    data = [(client.parseDOM(i, 'a')[0],
                             client.parseDOM(i, 'a', ret='href')[0]) for i in data if i]
                    frame = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]

                    r = self.s.get(frame).text
                    if six.PY2:
                        r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                    # try:
                    #     r = r.decode('utf-8', errors='replace')
                    # except AttributeError:
                    #     pass
                secCode = client.parseDOM(r, 'input', ret='value', attrs={'id': 'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                # xbmc.log('ITEMS: {}'.format(items))
                items = client.parseDOM(items, 'tr')

            else:
                title, season, episode = re.findall(r'^(?P<title>.+)\s+S(\d+)E(\d+)', query, re.I)[0]
                hdlr = 'season-{}-episode-{}'.format(int(season), int(episode))
                if imdb.startswith('tt'):
                    r = self.s.get(self.baseurl + 'view/{}'.format(imdb)).text
                    # r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                    frames = client.parseDOM(r, 'a', ret='href')
                    link = [i for i in frames if hdlr in i]

                    if not link:
                        frame = self.baseurl + 'view/{}'.format(imdb)
                    else:
                        frame = link[0]
                else:
                    if len(imdb) > 1:
                        baseurl = 'https://api.thetvdb.com/login'
                        series_url = 'https://api.thetvdb.com/episodes/%s'
                        greek_api = '7d4261794838bb48a3122381811ecb42'
                        user_key = 'TJXB86PGDBYN0818'
                        username = 'filmnet'

                        _headers = {'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                    'Connection': 'close'}

                        post = {"apikey": greek_api, "username": username, "userkey": user_key}

                        # data = client.request(baseurl, post=json.dumps(post), headers=_headers)
                        data = requests.post(baseurl, data=json.dumps(post), headers=_headers).json()
                        auth = 'Bearer {}'.format(unquote_plus(data['token']))
                        _headers['Authorization'] = auth

                        series_data = client.request(series_url % imdb, headers=_headers)
                        imdb = json.loads(series_data)['data']['imdbId']
                        r = self.s.get(self.baseurl + 'view/{}'.format(imdb)).text
                        # r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                        frames = client.parseDOM(r, 'a', ret='href')
                        frame = [i for i in frames if imdb in i][0]
                    else:
                        url = self.baseurl + 'search/{}/tv'.format(quote(title))
                        data = self.s.get(url).text
                        data = client.parseDOM(data, 'span', attrs={'class': 'h5'})
                        data = [(client.parseDOM(i, 'a')[0],
                                 client.parseDOM(i, 'a', ret='href')[0]) for i in data if i]

                        serie_link = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]
                        imdbid = re.findall(r'\/(tt\d+)\/', serie_link)[0]
                        r = self.s.get(self.baseurl + 'view/{}'.format(imdbid)).text
                        frames = client.parseDOM(r, 'a', ret='href')
                        frame = [i for i in frames if hdlr in i][0]

                frame = client.replaceHTMLCodes(frame)
                frame = six.ensure_str(frame, errors='replace')
                frame = quote(frame, safe=':/?')
                r = self.s.get(frame).text
                # r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                secCode = client.parseDOM(r, 'input', ret='value', attrs={'id': 'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                items = client.parseDOM(items, 'tr')
                # xbmc.log('ITEMS: {}'.format(items))

        except BaseException:
            return

        for item in items:
            try:
                item = six.ensure_str(item, errors='replace')
                # xbmc.log('$#$MATCH-SUBZ-ITEM: {}'.format(item))
                try:
                    imdb = re.search(r'\/(tt\d+)\/', str(frame)).groups()[0]
                except BaseException:
                    imdb = re.search(r'\/(tt\d+)', str(frame)).groups()[0]

                data = re.findall(r'''downloadMe\(['"](\w+-\w+).+?label.+?>(\d+).+?<td>(.+?)</td''',
                                  item, re.I | re.DOTALL)[0]
                name = data[2]
                name = client.replaceHTMLCodes(name)

                url = self.baseurl + 'dll/{}/0/{}'.format(data[0], secCode)
                url = client.replaceHTMLCodes(url)
                url = quote(url, safe=':/?')

                down = data[1]
                rating = str(self._rating(down))

                self.list.append(
                    {'name': name,
                     'url': '{}|{}|{}|{}|{}'.format(frame, url, cj['PHPSESSID'], name, imdb),
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
            frame, url, cjphp, sub_, imdb_ = url.split('|')
            # xbmc.log('$#$ FRAME: %s | URL: %s | COOKIE: %s | SUB: %s | imdb: %s | ' % (frame, url, cjcfduid, sub_, imdb_))

            sub_ = unquote_plus(sub_)

            # self.s.cookies.update({'__cfduid': cjcfduid, 'PHPSESSID': cjphp})
            self.s.cookies.update({'PHPSESSID': cjphp})
            # xbmc.log('$#$ FRAME-COOKIES: %s' % self.s.cookies)

            self.s.headers['Referer'] = frame
            init = six.ensure_text(self.s.get(url).content, errors='replace')
            try:
                imdb = client.parseDOM(init, 'input', ret='value', attrs={'name': 'uid'})[0]
            except IndexError:
                imdb = imdb_
            try:
                sub_name = client.parseDOM(init, 'input', ret='value', attrs={'name': 'output'})[0]
            except IndexError:
                sub_name = '{}.srt'.format(sub_)

            self.s.headers.update({'Referer': url, 'Origin': self.baseurl})

            # xbmc.log('$#$ FRAME-HEADERS: %s' % self.s.headers, xbmc.LOGNOTICE)
            post = {"langcode": "el",
                    "uid": imdb,
                    "output": sub_name.lower(),
                    "dll": "1"}
            # post = urllib.urlencode(post)
            # xbmc.log('$#$ FRAME-POST: %s' % post)

            result = self.s.post(url, data=post)
            f = os.path.join(path, quote(sub_) + '.srt')
            with open(f, 'wb') as subFile:
                subFile.write(result.content)

            dirs, files = control.listDir(path)

            if len(files) == 0:
                return

            if not f.lower().endswith('.rar'):
                control.execute('Extract("%s","%s")' % (f, path))

            if control.infoLabel('System.Platform.Windows'):
                conversion = quote
            else:
                conversion = quote_plus

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

            filename = [i for i in files if any(i.endswith(x) for x in ['.srt', '.sub'])][0]

            try:
                filename = filename.decode('utf-8')
            except Exception:
                pass

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


