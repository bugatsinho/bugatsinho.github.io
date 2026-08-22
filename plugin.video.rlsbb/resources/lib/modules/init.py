# -*- coding: utf-8 -*-
from sys import argv
from urllib.parse import parse_qsl

# service.py runs standalone at Kodi startup (not invoked as plugin://...), so it
# only gets argv[0] -- no handle/query. Default those instead of crashing on import.
sysaddon = argv[0]
syshandle = int(argv[1]) if len(argv) > 1 else -1
params = dict(parse_qsl(argv[2].replace('?', ''))) if len(argv) > 2 else {}
