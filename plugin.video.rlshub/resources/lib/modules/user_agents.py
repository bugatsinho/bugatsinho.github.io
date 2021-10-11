# -*- coding: utf-8 -*-

'''
    Tulip library
    Author Twilight0

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/GPL-3.0-only for more information.
'''

from resources.lib.modules.compat import urlencode
from random import choice


ANDROID = "Mozilla/5.0 (Linux; Android 10; STK-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"
BRAVE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/83.0.4103.116 Safari/537.36"
CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36"
EDGE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4346.0 Safari/537.36 Edg/89.0.731.0"
FIREFOX = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
FIREFOX_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:85.0) Gecko/20100101 Firefox/85.0"
IE_6 = "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)"
IE_11 = "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko"
IPAD = "Mozilla/5.0 (iPad; CPU OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Tablet/15E148 Safari/604.1"
IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)'
OPERA = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.27 Safari/537.36 OPR/74.0.3904.0 (Edition developer)"
SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15"
VIVALDI = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.116 Safari/537.36"
PY_URLLIB_2 = "Python-urllib/2.7"
PY_URLLIB_3 = "Python-urllib/3.8"


def randomagent():

    agents = [ANDROID, BRAVE, CHROME, EDGE, FIREFOX, FIREFOX_MAC, SAFARI, VIVALDI, IE_11]

    return choice(agents)


def agent():

    return 'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'


def mobile_agent():

    return 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G531M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Mobile Safari/537.36'


def random_mobile_agent():

    agents = [
        'Mozilla/5.0 (Linux; Android 7.0; SM-J710MN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
        'Mozilla/5.0 (Android 10; Mobile; rv:84.0) Gecko/84.0 Firefox/84.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)',
        'Mozilla/5.0 (iPad; CPU OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1'
    ]

    return choice(agents)


def ios_agent():

    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'


def spoofer(headers=None, _agent=True, age_str=None, referer=False, ref_str='', url=None):

    if age_str is None:
        age_str = randomagent()

    pipe = '|'

    if not headers:
        headers = {}

    if _agent and age_str and not headers:
        headers.update({'User-Agent': age_str})

    if referer and ref_str:
        headers.update({'Referer': ref_str})

    if headers:
        string = pipe + urlencode(headers)
        if url:
            url += string
            return url
        else:
            return string
    else:
        return ''
