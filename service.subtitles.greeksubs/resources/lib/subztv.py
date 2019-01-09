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
        self.hdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

    def get(self, query):
        try:
            query, imdb = query.split('/imdb=')
            match = re.findall('^(?P<title>.+)[\s+\(|\s+](?P<year>\d{4})', query)
            #xbmc.log('$#$MATCH-SUBZ: %s' % match, xbmc.LOGNOTICE)

            if len(match) > 0:
    
                title, year = match[0][0], match[0][1]
                cj = requests.get('https://subztv.online/rainbow/master-js', headers=self.hdr).cookies
                
                if imdb.startswith('tt'):
                    r = requests.get('https://subztv.online/view/%s' % imdb, headers=self.hdr, cookies=cj).content
                    r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                else:
                    url = 'https://subztv.online/search/%s/movies' % urllib.quote(title)
                    
                    data = requests.get(url, headers=self.hdr).content
                    data = client.parseDOM(data, 'span', attrs={'class': 'h5'})
                    data = [(client.parseDOM(i, 'a')[0],
                             client.parseDOM(i, 'a', ret='href')[0]) for i in data if i]
    
                    link = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]
    
                    cj = requests.get('https://subztv.online/rainbow/master-js', headers=self.hdr).cookies
                    
                    r = requests.get(link, headers=self.hdr, cookies=cj).content
                    r = re.sub(r'[^\x00-\x7F]+', ' ', r)

                secCode = client.parseDOM(r,'input', ret='value', attrs={'id':'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                items = client.parseDOM(items, 'tr')

            else:
                title, season, episode = re.findall('^(?P<title>.+)\s+S(\d+)E(\d+)', query, re.I)[0]
                #xbmc.log('$#$MATCH-SUBZ: %s | %s | %s' % (title, season, episode), xbmc.LOGNOTICE)
    
                season, episode = '%01d' % int(season), '%01d' % int(episode)
                hdlr = 'season-%s-episode-%s' % (season, episode)
                url = 'https://subztv.online/search/%s/tv' % urllib.quote(title)
                data = requests.get(url, headers=self.hdr).content
                data = client.parseDOM(data, 'span', attrs={'class':'h5'})
                data = [(client.parseDOM(i, 'a')[0],
                         client.parseDOM(i, 'a', ret='href')[0])for i in data if i]
                try:
                    url = [i[1] for i in data if hdlr in i[1]][0]
                except BaseException:
                        link = [i[1] for i in data if cleantitle.get(i[0]) == cleantitle.get(title)][0]
    
                        cj = requests.get('https://subztv.online/rainbow/master-js', headers=self.hdr).cookies
                        r = requests.get(link, headers=self.hdr, cookies=cj).content
                        r = re.sub(r'[^\x00-\x7F]+', ' ', r)
    
                        url = client.parseDOM(r, 'section',)
                        url = [i for i in url if 'sessaon' in i][0]
                        url = client.parseDOM(url, 'a', ret='href')
                        url = [i for i in url if hdlr in i][0]
                imdb = re.findall('(tt\d+)', url)[0]
                cj = requests.get('https://subztv.online/rainbow/master-js', headers=self.hdr).cookies
    
                r = requests.get(url, headers=self.hdr, cookies=cj).content
                r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                secCode = client.parseDOM(r,'input', ret='value', attrs={'id':'secCode'})[0]
                items = client.parseDOM(r, 'tbody')[0]
                items = client.parseDOM(items, 'tr')

        except BaseException:
            return

        for item in items:
            try:
                
                data = re.compile('''downloadMe\(['"](\w+\-\w+).+?label.+?>(\d+).+?<td>(.+?)</td''', re.I|re.DOTALL).findall(str(item))[0]
                name = data[2]
                
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = 'https://subztv.online/' + 'dll/' + data[0] + '/0/' + secCode
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                down = data[1]
                rating = self._rating(down)

                self.list.append({'name': name, 'url': '%s|%s|%s|%s' % (url, name, cj['PHPSESSID'], imdb), 'source': 'subztv', 'rating': rating})
                
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
        elif rating >= 10 and rating < 20:
            rating = 2
        elif rating >= 20 and rating < 30:
            rating = 3
        elif rating >= 30 and rating < 40:
            rating = 4
        elif rating >= 40:
            rating = 5

        return rating


    def download(self, path, url):

        try:
            url, sub_, php, imdb = url.split('|')

            headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 
                       'Referer': url}

            cj = {'PHPSESSID': php,
                  'share_show_hide_status':'active'}   
            
            post = {'langcode': 'el',
                    'uid': imdb,
                    'output': '%s.srt' % sub_,
                    'dll': '1'}
            
            r = requests.get(url, headers=headers, cookies=cj)
            result = requests.post(url, headers=headers, data=post, cookies=cj).content

            f = os.path.join(path, sub_ + '.srt')

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

                return subtitle

            else:
                
                return subtitle

        except BaseException:
            pass
