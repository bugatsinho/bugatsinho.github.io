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
        line = re.findall(r'(<category label="DOMAINS">.+?</category>)', data)[0]
        paste = cache.get(client.request, 4, 'https://pastebin.com/raw/xTK1nb6J')
        new_data = data.replace(line, paste)
        file.seek(0)
        file.truncate()
        file.write(new_data)
        file.close()
        control.refresh()
else:
    pass
