# -*- coding: utf-8 -*-

'''
    Tulip routine libraries, based on lambda's lamlib
    Author Twilight0

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

import re, sys, gzip, time, random, base64

import xbmc

from resources.lib.modules import cache, dom_parser, control, utils

import six
from six import BytesIO
from six.moves import urllib, urllib_parse, html_parser as HTMLParser
from six.moves.urllib_parse import quote_plus, urlencode, urlparse
from six.moves.urllib_response import addinfourl
if six.PY3:
    from http import cookiejar as cookielib
else:
    import cookielib


def request(url, close=True, redirect=True, error=False, verify=True, proxy=None, post=None, headers=None, mobile=False,
            XHR=False, limit=None, referer=None, cookie=None, compression=True, output='', timeout='20'):
    try:
        if not url:
            return

        handlers = []

        if proxy is not None:
            handlers += [urllib.request.ProxyHandler(
                {'http': '%s' % (proxy)}), urllib.request.HTTPHandler]
            opener = urllib.request.build_opener(*handlers)
            opener = urllib.request.install_opener(opener)

        if output == 'cookie' or output == 'extended' or not close:
            cookies = cookielib.LWPCookieJar()
            handlers += [urllib.request.HTTPHandler(),
                         urllib.request.HTTPSHandler(),
                         urllib.request.HTTPCookieProcessor(cookies)]
            opener = urllib.request.build_opener(*handlers)
            opener = urllib.request.install_opener(opener)

        try:
            import platform
            node = platform.node().lower()
        except BaseException:
            node = ''

        if verify == False and sys.version_info >= (2, 7, 12):
            try:
                import ssl
                ssl_context = ssl._create_unverified_context()
                handlers += [urllib.request.HTTPSHandler(context=ssl_context)]
                opener = urllib.request.build_opener(*handlers)
                opener = urllib.request.install_opener(opener)
            except BaseException:
                pass

        if verify and ((2, 7, 8) < sys.version_info < (2, 7, 12)
                       or platform.uname()[1] == 'XboxOne'):
            try:
                import ssl
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                handlers += [urllib.request.HTTPSHandler(context=ssl_context)]
                opener = urllib.request.build_opener(*handlers)
                opener = urllib.request.install_opener(opener)
            except BaseException:
                pass

        if url.startswith('//'):
            url = 'http:' + url

        _headers = {}

        try:
            _headers.update(headers)
        except BaseException:
            pass

        if 'User-Agent' in _headers:
            pass
        elif mobile:
            _headers['User-Agent'] = cache.get(randommobileagent, 1)
        else:
            _headers['User-Agent'] = cache.get(randomagent, 1)

        if 'Referer' in _headers:
            pass
        elif referer is not None:
            _headers['Referer'] = referer
        if 'Accept-Language' not in _headers:
            _headers['Accept-Language'] = 'en-US'
        if 'X-Requested-With' in _headers:
            pass
        elif XHR:
            _headers['X-Requested-With'] = 'XMLHttpRequest'
        if 'Cookie' in _headers:
            pass
        elif cookie is not None:
            _headers['Cookie'] = cookie
        if 'Accept-Encoding' in _headers:
            pass
        elif compression and limit is None:
            _headers['Accept-Encoding'] = 'gzip'

        if not redirect:
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def http_error_302(self, req, fp, code, msg, headers):
                    infourl = addinfourl(fp, headers, req.get_full_url())
                    infourl.status = code
                    infourl.code = code
                    return infourl
                http_error_300 = http_error_302
                http_error_301 = http_error_302
                http_error_303 = http_error_302
                http_error_307 = http_error_302

            opener = urllib.request.build_opener(NoRedirectHandler())
            urllib.request.install_opener(opener)

            try:
                del _headers['Referer']
            except BaseException:
                pass

        url = utils.byteify(url)
        request = urllib.request.Request(url)

        if post is not None:
            if isinstance(post, dict):
                post = utils.byteify(post)
                post = urlencode(post)
            if len(post) > 0:
                request = urllib.request.Request(url, data=post)
            else:
                request.get_method = lambda: 'POST'
                request.has_header = lambda header_name: (header_name == 'Content-type' or
                                                          urllib.request.Request.has_header(request, header_name))

        if limit == '0':
            request.get_method = lambda: 'HEAD'

        _add_request_header(request, _headers)
        response = urllib.request.urlopen(request, timeout=int(timeout))

        try:
            response = urllib.request.urlopen(request, timeout=int(timeout))
        except urllib.error.HTTPError as response:
            if response.code == 503:
                cf_result = response.read()
                try:
                    encoding = response.info().getheader('Content-Encoding')
                except BaseException:
                    encoding = None
                if encoding == 'gzip':
                    cf_result = gzip.GzipFile(
                        fileobj=BytesIO(cf_result)).read()

                if 'cf-browser-verification' in cf_result:
                    from cloudscraper2 import CloudScraper as cfscrape
                    _cf_lim = 0
                    while 'cf-browser-verification' in cf_result and _cf_lim <= 1:
                        _cf_lim += 1
                        netloc = '%s://%s/' % (urlparse(url).scheme,
                                               urlparse(url).netloc)
                        ua = _headers['User-Agent']

                        try:
                            cf = cache.get(cfscrape.get_cookie_string, 1, netloc, ua)[0]
                        except BaseException:
                            try:
                                cf = cfscrape.get_cookie_string(url, ua)[0]
                            except BaseException:
                                cf = None
                        finally:
                            _headers['Cookie'] = cf

                        request = urllib.request.Request(url, data=post)
                        _add_request_header(request, _headers)

                        try:
                            response = urllib.request.urlopen(
                                request, timeout=int(timeout))
                            cf_result = 'Success'
                        except urllib.error.HTTPError as response:
                            cache.remove(cfscrape.get_cookie_string, netloc, ua)
                            cf_result = response.read()
                else:
                    xbmc.log('Request-Error (%s): %s' %
                                  (str(response.code), url), xbmc.LOGDEBUG)
                    if not error:
                        return
            else:
                xbmc.log('Request-Error (%s): %s' %
                              (str(response.code), url), xbmc.LOGDEBUG)
                if not error:
                    return

        if output == 'cookie':
            try:
                result = '; '.join(['%s=%s' % (i.name, i.value)
                                    for i in cookies])
            except BaseException:
                pass
            try:
                result = cf
            except BaseException:
                pass
            if close:
                response.close()
            return result

        elif output == 'geturl':
            result = response.geturl()
            if close:
                response.close()
            return result

        elif output == 'headers':
            result = response.headers
            if close:
                response.close()
            return result

        elif output == 'location':
            result = response.headers
            if close:
                response.close()
            return result['Location']

        elif output == 'chunk':
            try:
                content = int(response.headers['Content-Length'])
            except BaseException:
                content = (2049 * 1024)
            if content < (2048 * 1024):
                return
            result = response.read(16 * 1024)
            if close:
                response.close()
            return result

        elif output == 'file_size':
            try:
                content = int(response.headers['Content-Length'])
            except BaseException:
                content = '0'
            response.close()
            return content

        if limit == '0':
            result = response.read(1 * 1024)
        elif limit is not None:
            result = response.read(int(limit) * 1024)
        else:
            result = response.read(5242880)

        try:
            encoding = response.headers['Content-Encoding']
        except BaseException:
            encoding = None
        if encoding == 'gzip':
            result = gzip.GzipFile(fileobj=BytesIO(result)).read()

        if b'sucuri_cloudproxy_js' in result:
            su = sucuri().get(result)

            _headers['Cookie'] = su

            request = urllib.request.Request(url, data=post)
            _add_request_header(request, _headers)

            response = urllib.request.urlopen(request, timeout=int(timeout))

            if limit == '0':
                result = response.read(224 * 1024)
            elif limit is not None:
                result = response.read(int(limit) * 1024)
            else:
                result = response.read(5242880)

            try:
                encoding = response.info().getheader('Content-Encoding')
            except BaseException:
                encoding = None
            if encoding == 'gzip':
                result = gzip.GzipFile(
                    fileobj=BytesIO(result)).read()
        
        if six.PY3 and isinstance(result, bytes):
            result = result.decode('utf-8')

        if output == 'extended':
            try:
                response_headers = dict(
                    [(item[0].title(), item[1]) for item in response.info().items()])
            except BaseException:
                response_headers = response.headers
            response_code = str(response.code)
            try:
                cookie = '; '.join(['%s=%s' % (i.name, i.value)
                                    for i in cookies])
            except BaseException:
                pass
            try:
                cookie = cf
            except BaseException:
                pass
            if close:
                response.close()
            return (result, response_code, response_headers, _headers, cookie)
        else:
            if close:
                response.close()
            return result
    except Exception as e:
        xbmc.log(
            'Request-Error: (%s) => %s' %
            (str(e), url), xbmc.LOGDEBUG)
        return


def _basic_request(url, headers=None, post=None, timeout='30', limit=None):
    try:
        try:
            headers.update(headers)
        except:
            headers = {}

        request = urllib.request.Request(url, data=post)
        _add_request_header(request, headers)
        response = urllib.request.urlopen(request, timeout=int(timeout))
        return _get_result(response, limit)
    except:
        return


def _add_request_header(_request, headers):

    try:
        if not headers:
            headers = {}

        if 'https' in _request.get_full_url():
            scheme = 'https'
        else:
            scheme = 'http'

        if six.PY2:
            host = _request.get_host()
        else:
            host = _request.host

        referer = headers.get('Referer') if 'Referer' in headers else '%s://%s/' % (scheme, host)

        _request.add_unredirected_header('Host', host)
        _request.add_unredirected_header('Referer', referer)
        for key in headers:
            _request.add_header(key, headers[key])
    except:
        return


def _get_result(response, limit=None):
    if limit == '0':
        result = response.read(224 * 1024)
    elif limit:
        result = response.read(int(limit) * 1024)
    else:
        result = response.read(5242880)

    try:
        encoding = response.info().getheader('Content-Encoding')
    except:
        encoding = None
    if encoding == 'gzip':
        result = gzip.GzipFile(fileobj=BytesIO(result)).read()

    return result


def parseDOM(html, name='', attrs=None, ret=False):
    if attrs:
        attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.items())

    results = dom_parser.parse_dom(html, name, attrs, ret)

    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]

    return results


def replaceHTMLCodes(txt):
    # txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    if six.PY3:
        from html import unescape
    else:
        from HTMLParser import HTMLParser
        unescape = HTMLParser().unescape
    txt = unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&gt;", ">")
    txt = txt.strip()
    return txt


def randomagent():

    _agents = ['Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
               'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
               'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
               'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0']

    return random.choice(_agents)


def randommobileagent(mobile):
    _mobagents = [
        'Mozilla/5.0 (Linux; Android 7.1; vivo 1716 Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; U; Android 6.0.1; zh-CN; F5121 Build/34.0.A.1.247) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.1.944 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-N920C Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/6.2 Chrome/56.0.2924.87 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1']

    if mobile == 'ios':
        return random.choice(_mobagents[3:5])

    elif mobile == 'android':
        return random.choice(_mobagents[:3])
    else:
        random.choice(_mobagents)


def agent():
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'


class cfcookie:
    def __init__(self):
        self.cookie = None

    def get(self, netloc, ua, timeout):
        try:
            self.netloc = netloc
            self.ua = ua
            self.timeout = timeout
            self.cookie = None
            self._get_cookie(netloc, ua, timeout)
            if self.cookie is None:
                xbmc.log('%s returned an error. Could not collect tokens.' % netloc, xbmc.LOGDEBUG)
            return self.cookie
        except Exception as e:
            xbmc.log('%s returned an error. Could not collect tokens - Error: %s.' % (netloc, str(e)),
                          xbmc.LOGDEBUG)
            return self.cookie

    def _get_cookie(self, netloc, ua, timeout):
        class NoRedirection(urllib.error.HTTPErrorProcessor):
            def http_response(self, request, response):
                return response

        def parseJSString(s):
            try:
                offset = 1 if s[0] == '+' else 0
                val = int(
                    eval(s.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
                return val
            except:
                pass

        cookies = cookielib.LWPCookieJar()
        opener = urllib.request.build_opener(NoRedirection, urllib.request.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-Agent', ua)]
        try:
            response = opener.open(netloc, timeout=int(timeout))
            result = response.read()
        except urllib.error.HTTPError as response:
            result = response.read()
            try:
                encoding = response.info().getheader('Content-Encoding')
            except:
                encoding = None
            if encoding == 'gzip':
                result = gzip.GzipFile(fileobj=BytesIO(result)).read()

        jschl = re.compile('name="jschl_vc" value="(.+?)"/>').findall(result)[0]
        init = re.compile('setTimeout\(function\(\){\s*.*?.*:(.*?)};').findall(result)[0]
        builder = re.compile(r"challenge-form\'\);\s*(.*)a.v").findall(result)[0]

        if '/' in init:
            init = init.split('/')
            decryptVal = parseJSString(init[0]) / float(parseJSString(init[1]))
        else:
            decryptVal = parseJSString(init)

        lines = builder.split(';')
        for line in lines:
            if len(line) > 0 and '=' in line:
                sections = line.split('=')
                if '/' in sections[1]:
                    subsecs = sections[1].split('/')
                    line_val = parseJSString(subsecs[0]) / float(parseJSString(subsecs[1]))
                else:
                    line_val = parseJSString(sections[1])
                decryptVal = float(eval('%.16f' % decryptVal + sections[0][-1] + '%.16f' % line_val))

        answer = float('%.10f' % decryptVal) + len(urlparse(netloc).netloc)

        query = '%scdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

        if 'type="hidden" name="pass"' in result:
            passval = re.findall('name="pass" value="(.*?)"', result)[0]
            query = '%scdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (
            netloc, quote_plus(passval), jschl, answer)
            time.sleep(6)

        opener.addheaders = [('User-Agent', ua),
                             ('Referer', netloc),
                             ('Accept', 'text/html, application/xhtml+xml, application/xml, */*'),
                             ('Accept-Encoding', 'gzip, deflate')]

        response = opener.open(query)
        response.close()

        cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
        if 'cf_clearance' in cookie: self.cookie = cookie


class sucuri:
    def __init__(self):
        self.cookie = None

    def get(self, result):
        try:
            s = re.compile("S\s*=\s*'([^']+)").findall(result)[0]
            s = base64.b64decode(s)
            s = s.replace(' ', '')
            s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
            s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
            s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
            s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
            s = re.sub(';location.reload\(\);', '', s)
            s = re.sub(r'\n', '', s)
            s = re.sub(r'document\.cookie', 'cookie', s)

            cookie = ''
            exec(s)
            self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
            self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])

            return self.cookie
        except:
            pass

def setup_headers(UA=None, referer=None, cookie=None):
    headers = {}
    if UA is None:
        headers.update({'User-Agent': randomagent()})
    if not referer is None:
        headers.update({'Referer': referer})
    if not cookie is None:
        headers.update({'Cookie': cookie})

    return headers


def _get_keyboard(default="", heading="", hidden=False):

    keyboard = control.keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return unicode(keyboard.getText(), "utf-8")
    return default


def removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)
