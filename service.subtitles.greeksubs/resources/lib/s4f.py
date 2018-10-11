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


import xbmc
import urllib,urlparse,re,os,requests,zipfile, StringIO, urllib2
from resources.modules import client
from resources.modules import control


class s4f:
    def __init__(self):
        self.list = []
        self.base_link = 'http://www.medium-industry.com/'
        self.base_TVlink = 'http://www.subs4series.com/'
        self.search = 'search_report.php?search=%s&searchType=1'


    def get(self, query):

        try:

            match = re.findall('(.+?) \((\d{4})\)/imdb=', query)

            if len(match) > 0:
                hdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

                title, year = match[0][0], match[0][1]

                query =  urllib.quote_plus(title+' '+year)

                url = urlparse.urljoin(self.base_link, self.search % query)

                req = requests.get(url, headers=hdr)
                cj = req.cookies
                r = req.content
                r = re.sub(r'[^\x00-\x7F]+', ' ', r)

                urls = client.parseDOM(r, 'div', attrs={'class': ' seeDark'})
                urls += client.parseDOM(r, 'div', attrs={'class': ' seeMedium'})
                urls = [i for i in urls if 'com/el.gif' in i]
                urls = [(client.parseDOM(i, 'tr')[0], re.findall('<B>(\d+)</B>DLs', i, re.I)[0]) for i in urls if i]
                urls = [(client.parseDOM(i[0], 'a', ret='href')[0],
                         client.parseDOM(i[0], 'a', ret='title')[0], i[1]) for i in urls if i]
                urls = [(urlparse.urljoin(self.base_link, i[0]), i[1].split('for ', 1)[1],
                         i[2]) for i in urls if i]
                urls = [(i[0], i[1], i[2]) for i in urls if i]


            else:
                hdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                       'Referer':'http://www.subs4series.com/'}
                title, season, episode = re.findall('(.+?) S(\d+)E(\d+)/imdb=', query)[0]

                hdlr = 'S%02dE%02d' % (int(season),int(episode))

                query = urllib.quote(title+' '+hdlr)

                url = urlparse.urljoin(self.base_TVlink, self.search % query)

                req = requests.get(url, headers=hdr)

                cj = req.cookies
                r = req.content
                r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                xbmc.log('@@URL:%s' % r)

                urls = client.parseDOM(r, 'div', attrs={'class': ' seeDark'})
                urls += client.parseDOM(r, 'div', attrs={'class': ' seeMedium'})
                urls = [i for i in urls if not 'com/en.gif' in i]
                urls = [(client.parseDOM(i, 'tr')[0], re.findall('<B>(\d+)</B>DLs', i, re.I)[0]) for i in urls if i]
                urls = [(client.parseDOM(i[0], 'a', ret='href')[0],
                         client.parseDOM(i[0], 'a', ret='title')[0], i[1]) for i in urls if i]
                urls = [(urlparse.urljoin(self.base_TVlink, i[0]), re.sub('Greek subtitle[s] for ', '', i[1]),
                         i[2]) for i in urls if i]
                urls = [(i[0], i[1], i[2]) for i in urls if i]

        except:
            return

        for i in urls:
            try:
                rating = self._rating(i[2])
                name = i[1].replace('_', '').replace('%20', '.')
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = i[0]
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': '%s|%s|%s'%(url, cj['PHPSESSID'], cj['__cfduid']), 'source': 's4f', 'rating': rating})
            except:
                pass


        return self.list


    def _rating(self, downloads):

        try:
            rating = int(downloads)
        except:
            rating = 0

        if rating < 100:
            rating = 1
        elif rating >= 100 and rating < 200:
            rating = 2
        elif rating >= 200 and rating < 300:
            rating = 3
        elif rating >= 300 and rating < 400:
            rating = 4
        elif rating >= 400:
            rating = 5

        return rating

    def download(self, path, url):

        try:
            url, php, cfd = url.split('|')
            if 'subs4series' in url:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                           'Referer': url,
                           'Origin': 'http://www.subs4series.com/'}
                cj = {'PHPSESSID': php,
                  '__cfduid': cfd}

                r = requests.get(url, headers=headers, cookies=cj).content
                r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                xbmc.log('@#@DATA:%s'%r)

                pos = re.findall('\/(getSub-\w+\.html)', r, re.I|re.DOTALL)[0]
                post_url = urlparse.urljoin('http://www.subs4series.com',pos)
                r = requests.get(post_url, headers=headers, cookies=cj)
                result = r.content
                surl = r.url


            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                           'Referer': url,
                           'Origin': 'http://www.medium-industry.com'}
                cj = {'PHPSESSID': php,
                  '__cfduid': cfd}
                post_url = 'http://www.medium-industry.com/getSub.html'

                r = requests.get(url, headers=headers, cookies=cj).content
                r = re.sub(r'[^\x00-\x7F]+', ' ', r)
                #pos = client.parseDOM(r, 'tr', attrs={'class':'stylepps'})[0]
                pos = re.findall('getSub-(\w+)\.html', r, re.I|re.DOTALL)[0]
                post = {'id':pos,
                        'x':'107',
                        'y':'35'}

                r = requests.post(post_url, headers=headers, data=post, cookies=cj)
                result = r.content
                surl = r.url




            f = os.path.join(path, surl.rpartition('/')[2])

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
                    except:
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

        except:
            pass
