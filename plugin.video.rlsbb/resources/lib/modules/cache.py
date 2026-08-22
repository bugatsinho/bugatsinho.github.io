# -*- coding: utf-8 -*-
import hashlib
import json
import re
import time
from sqlite3 import dbapi2 as database

from resources.lib.modules import control


def _key(definition, args):
    f = re.sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(definition))
    a = hashlib.md5(json.dumps(args, sort_keys=True, default=str).encode('utf-8')).hexdigest()
    return f, a


def get(definition, time_out_hours, *args, table='rel_list'):
    """Call definition(*args), cached in sqlite for time_out_hours. Serves the stale cached
    response if a live re-fetch raises or returns empty."""
    func, argkey = _key(definition, args)
    stale = None

    try:
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = ? AND args = ?" % table, (func, argkey))
        match = dbcur.fetchone()
        if match:
            stale = json.loads(match[2])
            fresh_enough = (abs(int(time.time()) - int(match[3])) / 3600) < time_out_hours
            if fresh_enough:
                return stale
    except Exception:
        pass

    try:
        result = definition(*args)
    except Exception:
        return stale

    if not result and stale is not None:
        return stale
    if not result:
        return result

    try:
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS %s (func TEXT, args TEXT, response TEXT, added TEXT, "
            "UNIQUE(func, args))" % table)
        dbcur.execute("DELETE FROM %s WHERE func = ? AND args = ?" % table, (func, argkey))
        dbcur.execute("INSERT INTO %s VALUES (?, ?, ?, ?)" % table,
                       (func, argkey, json.dumps(result), int(time.time())))
        dbcon.commit()
    except Exception:
        pass

    return result


def clear(table=None, withyes=True):
    if withyes and not control.yesnoDialog('Clear cache?'):
        return
    tables = table if isinstance(table, list) else [table or 'rel_list']
    try:
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
        for t in tables:
            dbcur.execute("DROP TABLE IF EXISTS %s" % t)
        dbcon.commit()
    except Exception:
        pass
    control.infoDialog('Cache cleared')


def delete(dbfile=None, withyes=True):
    dbfile = dbfile or control.cacheFile
    if withyes and not control.yesnoDialog('Clear cache?'):
        return
    control.deleteFile(dbfile)
    control.infoDialog('Cache cleared')
