# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# json_tools - JSON load and parse functions with library detection
# --------------------------------------------------------------------------------

import traceback



try:
    import json
except:

    try:
        import simplejson as json
    except: pass


def load(*args, **kwargs):
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = to_utf8

    try:
        value = json.loads(*args, **kwargs)
    except:

        value = {}

    return value


def dump(*args, **kwargs):
    if not kwargs:
        kwargs = {"indent": 4, "skipkeys": True, "sort_keys": True, "ensure_ascii": False}

    try:
        value = json.dumps(*args, **kwargs)
    except:

        value = ""
    return value


def to_utf8(dct):
    if isinstance(dct, dict):
        return dict((to_utf8(key), to_utf8(value)) for key, value in dct.iteritems())
    elif isinstance(dct, list):
        return [to_utf8(element) for element in dct]
    elif isinstance(dct, unicode):
        return dct.encode('utf-8')
    else:
        return dct

