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


import re, sys, cookielib, time, random
import urllib, urllib2, urlparse, HTMLParser
import cache

try:
    import requests
    requester = requests.get
except ImportError:
    requester = None


def request(url, close=True, redirect=True, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None,
            referer=None, cookie=None, output='', timeout='30'):

    try:
        handlers = []

        if proxy is not None:

            handlers += [urllib2.ProxyHandler({'http':'{0}'.format(proxy)}), urllib2.HTTPHandler]
            opener = urllib2.build_opener(*handlers)
            urllib2.install_opener(opener)

        if output == 'cookie' or output == 'extended' or close is not True:

            cookies = cookielib.LWPCookieJar()
            handlers += [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
            opener = urllib2.build_opener(*handlers)
            urllib2.install_opener(opener)

        try:

            if sys.version_info < (2, 7, 9):
                raise Exception()

            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            handlers += [urllib2.HTTPSHandler(context=ssl_context)]
            opener = urllib2.build_opener(*handlers)
            urllib2.install_opener(opener)

        except:
            pass

        try:
            headers.update(headers)
        except:
            headers = {}

        if 'User-Agent' in headers:
            pass
        elif not mobile is True:
            #headers['User-Agent'] = agent()
            headers['User-Agent'] = cache.get(randomagent, 1)
        else:
            headers['User-Agent'] = 'Apple-iPhone/701.341'

        if 'Referer' in headers:
            pass
        elif referer is None:
            headers['Referer'] = '%s://%s/' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
        else:
            headers['Referer'] = referer

        if not 'Accept-Language' in headers:
            headers['Accept-Language'] = 'en-US'

        if 'Cookie' in headers:
            pass
        elif cookie is not None:
            headers['Cookie'] = cookie

        if redirect is False:

            class NoRedirection(urllib2.HTTPErrorProcessor):

                def http_response(self, request, response):
                    return response

            opener = urllib2.build_opener(NoRedirection)
            urllib2.install_opener(opener)

            try:
                del headers['Referer']
            except:
                pass

        req = urllib2.Request(url, data=post, headers=headers)

        try:
            response = urllib2.urlopen(req, timeout=int(timeout))

        except urllib2.HTTPError as response:

            if response.code == 503:

                if 'cf-browser-verification' in response.read(5242880):

                    netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)

                    cf = cache.get(cfcookie, 168, netloc, headers['User-Agent'], timeout)

                    headers['Cookie'] = cf

                    request = urllib2.Request(url, data=post, headers=headers)

                    response = urllib2.urlopen(request, timeout=int(timeout))

                elif error is False:
                    return

            elif error is False:
                return

        if output == 'cookie':

            try:
                result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except:
                pass
            try:
                result = cf
            except:
                pass

        elif output == 'response':

            if limit == '0':
                result = (str(response.code), response.read(224 * 1024))
            elif limit is not None:
                result = (str(response.code), response.read(int(limit) * 1024))
            else:
                result = (str(response.code), response.read(5242880))

        elif output == 'chunk':

            try:
                content = int(response.headers['Content-Length'])
            except:
                content = (2049 * 1024)

            if content < (2048 * 1024):
                return
            result = response.read(16 * 1024)

        elif output == 'extended':

            try:
                cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except:
                pass
            try:
                cookie = cf
            except:
                pass
            content = response.headers
            result = response.read(5242880)
            return result, headers, content, cookie

        elif output == 'geturl':
            result = response.geturl()

        elif output == 'headers':
            content = response.headers
            return content

        else:
            if limit == '0':
                result = response.read(224 * 1024)
            elif limit is not None:
                result = response.read(int(limit) * 1024)
            else:
                result = response.read(5242880)

        if close is True:
            response.close()

        return result

    except:
        return


def retriever(source, destination, *args):

    class Opener(urllib.URLopener):
        version = randomagent()

    Opener().retrieve(source, destination, *args)


def parseDOM(html, name=u"", attrs=None, ret=False):

    if attrs is None:
        attrs = {}

    if isinstance(name, str):  # Should be handled
        try:
            name = name  # .decode("utf-8")
        except:
            pass

    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]  # Replace with chardet thingy
        except:
            html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        return u""

    if not name.strip():
        return u""

    ret_lst = []
    for item in html:
        temp_item = re.compile('(<[^>]*?\n[^>]*?>)').findall(item)
        for match in temp_item:
            item = item.replace(match, match.replace("\n", " "))

        lst = _getDOMElements(item, name, attrs)

        if isinstance(ret, str):
            lst2 = []
            for match in lst:
                lst2 += _getDOMAttributes(match, name, ret)
            lst = lst2
        else:
            lst2 = []
            for match in lst:
                temp = _getDOMContent(item, name, match, ret).strip()
                item = item[item.find(temp, item.find(match)) + len(temp):]
                lst2.append(temp)
            lst = lst2
        ret_lst += lst

    return ret_lst


def _getDOMContent(html, name, match, ret):  # Cleanup

    endstr = u"</" + name  # + ">"

    start = html.find(match)
    end = html.find(endstr, start)
    pos = html.find("<" + name, start + 1 )

    while pos < end and pos != -1:  # Ignore too early </endstr> return
        tend = html.find(endstr, end + len(endstr))
        if tend != -1:
            end = tend
        pos = html.find("<" + name, pos + 1)

    if start == -1 and end == -1:
        result = u""
    elif start > -1 and end > -1:
        result = html[start + len(match):end]
    elif end > -1:
        result = html[:end]
    elif start > -1:
        result = html[start + len(match):]

    if ret:
        endstr = html[end:html.find(">", html.find(endstr)) + 1]
        result = match + result + endstr

    return result


def _getDOMAttributes(match, name, ret):

    lst = re.compile('<' + name + '.*?' + ret + '=([\'"].[^>]*?[\'"])>', re.M | re.S).findall(match)
    if len(lst) == 0:
        lst = re.compile('<' + name + '.*?' + ret + '=(.[^>]*?)>', re.M | re.S).findall(match)
    ret = []
    for tmp in lst:
        cont_char = tmp[0]
        if cont_char in "'\"":

            # Limit down to next variable.
            if tmp.find('=' + cont_char, tmp.find(cont_char, 1)) > -1:
                tmp = tmp[:tmp.find('=' + cont_char, tmp.find(cont_char, 1))]

            # Limit to the last quotation mark
            if tmp.rfind(cont_char, 1) > -1:
                tmp = tmp[1:tmp.rfind(cont_char)]
        else:

            if tmp.find(" ") > 0:
                tmp = tmp[:tmp.find(" ")]
            elif tmp.find("/") > 0:
                tmp = tmp[:tmp.find("/")]
            elif tmp.find(">") > 0:
                tmp = tmp[:tmp.find(">")]

        ret.append(tmp.strip())

    return ret


def _getDOMElements(item, name, attrs):

    lst = []
    for key in attrs:
        lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=[\'"]' + attrs[key] + '[\'"].*?>))', re.M | re.S).findall(item)
        if len(lst2) == 0 and attrs[key].find(" ") == -1:  # Try matching without quotation marks
            lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=' + attrs[key] + '.*?>))', re.M | re.S).findall(item)

        if len(lst) == 0:
            lst = lst2
            lst2 = []
        else:

            test = range(len(lst))
            test.reverse()
            for i in test:  # Delete anything missing from the next list.
                if not lst[i] in lst2:
                    del(lst[i])

    if len(lst) == 0 and attrs == {}:
        lst = re.compile('(<' + name + '>)', re.M | re.S).findall(item)
        if len(lst) == 0:
            lst = re.compile('(<' + name + ' .*?>)', re.M | re.S).findall(item)

    return lst


def replaceHTMLCodes(txt):

    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&#38;", "&")
    txt = txt.replace("&nbsp;", "")
    return txt


def randomagent():

    BR_VERS = [['%s.0' % i for i in xrange(18, 43)], ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101',
                                                      '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95',
                                                      '39.0.2171.99', '40.0.2214.93', '40.0.2214.111', '40.0.2214.115',
                                                      '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81',
                                                      '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101',
                                                      '45.0.2454.85', '46.0.2490.71', '46.0.2490.80', '46.0.2490.86',
                                                      '47.0.2526.73', '47.0.2526.80'], ['11.0']]

    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0',
                'Windows NT 5.1', 'Windows NT 5.0']

    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']

    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']

    index = random.randrange(len(RAND_UAS))

    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))


def agent():
    return 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'


def mobile_agent():
    return 'Mozilla/5.0 (Android 4.4; Mobile; rv:18.0) Gecko/18.0 Firefox/18.0'


def ios_agent():
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'


def spoofer(_agent=True, age_str=randomagent(), referer=False, ref_str=''):

    if _agent and referer:
        return '|User-Agent=' + urllib.quote_plus(age_str) + '&Referer=' + urllib.quote_plus(ref_str)
    elif _agent:
        return '|User-Agent=' + urllib.quote_plus(age_str)
    elif referer:
        return '|Referer=' + urllib.quote_plus(ref_str)


def cfcookie(netloc, ua, timeout):
    try:
        headers = {'User-Agent': ua}

        req = urllib2.Request(netloc, headers=headers)

        try:
            urllib2.urlopen(req, timeout=int(timeout))
        except urllib2.HTTPError as response:
            result = response.read(5242880)

        jschl = re.findall('name="jschl_vc" value="(.+?)"/>', result)[0]

        init = re.findall('setTimeout\(function\(\){\s*.*?.*:(.*?)};', result)[-1]

        builder = re.findall(r"challenge-form\'\);\s*(.*)a.v", result)[0]

        decryptVal = parseJSString(init)

        lines = builder.split(';')

        for line in lines:

            if len(line) > 0 and '=' in line:

                sections=line.split('=')
                line_val = parseJSString(sections[1])
                decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

        answer = decryptVal + len(urlparse.urlparse(netloc).netloc)

        query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

        if 'type="hidden" name="pass"' in result:
            passval = re.findall('name="pass" value="(.*?)"', result)[0]
            query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (netloc, urllib.quote_plus(passval), jschl, answer)
            time.sleep(5)

        cookies = cookielib.LWPCookieJar()
        handlers = [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)

        try:
            request = urllib2.Request(query, headers=headers)
            urllib2.urlopen(request, timeout=int(timeout))
        except:
            pass

        cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])

        return cookie
    except:
        pass


def parseJSString(s):
    try:
        offset=1 if s[0]=='+' else 0
        val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
        return val
    except:
        pass
