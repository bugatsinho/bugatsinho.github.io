# -*- coding: utf-8 -*-

import re, xbmc
from resources.lib.modules import client


def get_video(url):
    try:
        data = client.request(url)
        try:
            #<track kind="captions" src="https://aparat.cam/srt/00057/xhqn264cgp3r_Greek.vtt" srclang="en" label="Greek" default>
            sub = client.parseDOM(data, 'track', ret='src', attrs={'label': 'Greek'})[0]
            # xbmc.log('SUBS: {}'.format(sub))
        except IndexError:
            sub = 'nosub'

        link = re.findall(r'''sources:\s*\[\{src:\s*['"](.+?)['"]\,''', data, re.DOTALL)[0]
        link += '|{}'.format(sub)
        # xbmc.log('LINKKK: {}'.format(link))

        return link
    except BaseException:
        return ''

