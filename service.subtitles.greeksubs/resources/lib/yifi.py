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

import re
import os
import six
import xbmc
from six.moves.urllib_parse import urljoin, quote_plus, quote

from resources.modules import client, cleantitle
from resources.modules import control


class yifi:
    def __init__(self):
        self.list = []
        self.base_link = 'https://yifysubtitles.ch/' #https://yts-subs.net/ajax/search/?q=tt1365519
        self.search = 'search?q={}'
        #https://yifysubtitles.org/movie-imdb/tt4566758


    def get(self, query):
        try:
            query, imdb = query.split('/imdb=')
            match = re.findall(r'^(?P<title>.+)[\s+\(|\s+](?P<year>\d{4})', query)
            if len(match) > 0:
                title, year = match[0][0], match[0][1]
                if imdb.startswith('tt'):
                    url = 'https://yifysubtitles.org/movie-imdb/{}'.format(imdb)
                    r = six.ensure_text(client.request(url))

                else:
                    url = urljoin(self.base_link, self.search.format(quote_plus(title)))
                    r = six.ensure_text(client.request(url))
                    data = client.parseDOM(r, 'div', attrs={'class': 'media-body'})  # <div class="media-body">
                    for i in data:
                        try:
                            name = client.parseDOM(i, 'h3')[0].encode('utf-8')
                            if not cleantitle.get(title) == cleantitle.get(client.replaceHTMLCodes(name)):
                                raise Exception()
                            y = re.search(r'">(\d{4})<small>year</small>', i).groups()[0]
                            if not year == y:
                                raise Exception()
                            url = client.parseDOM(i, 'a', ret='href')[0]
                            url = url.encode('utf-8')
                            url = urljoin(self.base_link, url)
                            r = client.request(url)
                        except BaseException:
                            pass

                data = client.parseDOM(r, 'tr', attrs={'data-id': r'\d+'})
                items = [i for i in data if 'greek' in i.lower()]
                # xbmc.log('$#$MATCH-YIFI-RRR: %s' % items)
                urls = []
                for item in items:
                    try:
                        # rating = client.parseDOM(item, 'span', attrs={'title': 'rating'})[0]
                        name = client.parseDOM(item, 'a')[0]
                        name = re.sub(r'<.+?>', '', name).replace('subtitle', '')
                        name = client.replaceHTMLCodes(name)


                        url = client.parseDOM(item, 'a', ret='href')[0]
                        url = client.replaceHTMLCodes(url)

                        if six.PY2:
                            url = url.encode('utf-8')
                            name = name.encode('utf-8')
                        urls += [(name, url)]
                    except BaseException:
                        pass
            else:
                return self.list

        except BaseException:
            return

        for i in urls:
            try:
                r = six.ensure_text(client.request(urljoin(self.base_link, i[1])))
                url = client.parseDOM(r, 'a', ret='href', attrs={'class': 'btn-icon download-subtitle'})[0]
                url = 'https://yifysubtitles.org/' + url if url.startswith('/') else url
                self.list.append({'name': i[0], 'url': url, 'source': 'yifi', 'rating': '5'})
            except BaseException:
                pass

        return self.list

    def download(self, path, url):

        try:
            result = client.request(url)
            # f = os.path.splitext(urlparse(url).path)[1][1:]
            f = os.path.join(path, url.rpartition('/')[2])

            with open(f, 'wb') as subFile:
                subFile.write(result)

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
                # Multi-method RAR extraction for maximum compatibility
                extracted = False
                
                # Method 1: Try vfs.libarchive (Kodi 18+)
                if control.kodi_version() >= 18 and control.conditional_visibility('System.HasAddon(vfs.libarchive)'):
                    try:
                        # Use proper path encoding based on OS
                        if control.condVisibility('system.platform.windows'):
                            rar_path = f.replace('\\', '/')
                        else:
                            rar_path = f
                        
                        import xbmc, xbmcvfs
                        src = 'archive://' + quote(rar_path, safe='') + '/'
                        xbmc.log('GreekSubs: Attempting archive protocol: %s' % src, xbmc.LOGINFO)
                        
                        (dirs, files) = xbmcvfs.listdir(src)
                        for file in files:
                            if file.endswith(('.srt', '.sub')):
                                fsrc = src + file
                                fdst = os.path.join(path, file)
                                xbmc.log('GreekSubs: Copying %s to %s' % (fsrc, fdst), xbmc.LOGINFO)
                                xbmcvfs.copy(fsrc, fdst)
                        extracted = True
                        xbmc.log('GreekSubs: RAR extracted successfully via archive protocol', xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log('GreekSubs: Archive protocol failed: %s' % str(e), xbmc.LOGWARNING)
                        extracted = False
                
                # Method 2: Try built-in Extract command (Kodi 17+)
                if not extracted:
                    try:
                        xbmc.log('GreekSubs: Attempting Extract command', xbmc.LOGINFO)
                        control.execute('Extract("%s","%s")' % (f, path))
                        control.sleep(2000)  # Wait for extraction
                        # Check if files were extracted
                        dirs, files = control.listDir(path)
                        if any(file.endswith(('.srt', '.sub')) for file in files):
                            extracted = True
                            xbmc.log('GreekSubs: RAR extracted successfully via Extract command', xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log('GreekSubs: Extract command failed: %s' % str(e), xbmc.LOGWARNING)
                
                # Method 3: Try legacy rar:// protocol (may not work on all systems)
                if not extracted:
                    try:
                        xbmc.log('GreekSubs: Attempting legacy rar:// protocol', xbmc.LOGINFO)
                        uri = "rar://{0}/".format(conversion(f))
                        dirs, files = control.listDir(uri)
                        if files:
                            # Copy files from rar to path
                            for file in files:
                                if file.endswith(('.srt', '.sub')):
                                    content = control.openFile(uri + file).read()
                                    fdst = os.path.join(path, file)
                                    with open(fdst, 'wb') as subFile:
                                        subFile.write(content)
                            extracted = True
                            xbmc.log('GreekSubs: RAR extracted successfully via rar:// protocol', xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log('GreekSubs: rar:// protocol failed: %s' % str(e), xbmc.LOGWARNING)
                
                # If all methods failed, show error to user
                if not extracted:
                    xbmc.log('GreekSubs: All RAR extraction methods failed', xbmc.LOGERROR)
                    import xbmc
                    control.infoDialog('Σφάλμα: Αδυναμία εξαγωγής RAR αρχείου.\nΔοκιμάστε άλλον υπότιτλο.', time=5000)
                    control.deleteFile(f)
                    return None

            else:
                # Wait for ZIP extraction to complete
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

            # Get list of extracted subtitle files
            dirs, files = control.listDir(path)
            filenames = [i for i in files if any(i.endswith(x) for x in ['.srt', '.sub'])]
            
            if not filenames:
                xbmc.log('GreekSubs: No subtitle files found after extraction', xbmc.LOGERROR)
                control.deleteFile(f)
                return None
            
            filename = filenames[0]  # Get first subtitle file

            try:
                filename = filename.decode('utf-8')
            except Exception:
                pass

            subtitle = os.path.join(path, filename)
            control.deleteFile(f)  # Clean up downloaded archive
            return subtitle

        except BaseException:

            pass
