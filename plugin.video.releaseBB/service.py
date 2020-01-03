# -*- coding: utf-8 -*-

from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache

import re
import os
import xbmcvfs

_settingsFile = os.path.join(control.addonPath, 'resources', 'settings.xml')
if xbmcvfs.exists(_settingsFile):
    with open(_settingsFile, 'r+') as file:
        data = file.read()
        line = re.findall(r'(<setting id="domain".+?/>)', data)[0]
        paste = cache.get(client.request, 12, 'https://pastebin.com/raw/upztzeGt')
        new_data = data.replace(line, paste)
        file.seek(0)
        file.truncate()
        file.write(new_data)
        file.close()
        control.refresh()
else:
    pass



