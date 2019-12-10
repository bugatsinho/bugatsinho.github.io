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


import re, hashlib, time, xbmcvfs, os, xbmc, xbmcaddon, xbmcgui

try:
    from sqlite3 import dbapi2 as database
except:
    # noinspection PyUnresolvedReferences
    from pysqlite2 import dbapi2 as database

execute = xbmc.executebuiltin
dialog = xbmcgui.Dialog()
addonInfo = xbmcaddon.Addon().getAddonInfo
addonPath = xbmc.translatePath(addonInfo('path'))
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
join = os.path.join
openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
deleteFile = xbmcvfs.delete
deleteDir = xbmcvfs.rmdir
listDir = xbmcvfs.listdir
exists = xbmcvfs.exists
copy = xbmcvfs.copy
cacheFile = join(dataPath, 'cache.db')



def get(definition, time_out, *args, **table):
    try:
        response = None

        f = repr(definition)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        makeFile(dataPath)
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()

        response = eval(match[2].encode('utf-8'))

        t1 = int(match[3])
        t2 = int(time.time())
        update = (abs(t2 - t1) / 3600) >= int(time_out)
        if not update:
            return response
    except:
        pass

    try:
        r = definition(*args)
        if (r is None or r == []) and response is not None:
            return response
        elif r is None or r == []:
            return r
    except:
        return

    try:
        r = repr(r)
        t = int(time.time())
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");" % table)
        dbcur.execute("DELETE FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        dbcur.execute("INSERT INTO %s Values (?, ?, ?, ?)" % table, (f, a, r, t))
        dbcon.commit()
    except:
        pass

    try:
        return eval(r.encode('utf-8'))
    except:
        pass


def timeout(definition, *args, **table):

    try:
        response = None

        f = repr(definition)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        makeFile(dataPath)
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()
        return int(match[3])
    except:
        return


def clear(table=None, withyes=True):

    try:
        idle()

        if table is None:
            table = ['rel_list', 'rel_lib']
        elif not type(table) == list:
            table = [table]

        if withyes:

            yes = yesnoDialog(control.lang(30401).encode('utf-8'), '', '')

            if not yes:
                return

        else:

            pass

        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS %s" % t)
                dbcur.execute("VACUUM")
                dbcon.commit()
            except:
                pass

        infoDialog('You are ready to go!!')
    except:
        pass

def idle():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    else:
        xbmc.executebuiltin('Dialog.Close(busydialog)')


def busy():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    else:
        xbmc.executebuiltin('ActivateWindow(busydialog)')


def infoDialog(message, heading=addonInfo('name'), icon='', time=3000, sound=True):

    if icon == '':
        icon = addonInfo('icon')

    try:
        dialog.notification(heading, message, icon, time, sound=sound)
    except:
        execute("Notification(%s, %s, %s, %s)" % (heading, message, time, icon))


def okDialog(heading, line1):
    return dialog.ok(heading, line1)


def yesnoDialog(line1, line2='', line3='', heading=addonInfo('name'), nolabel=None, yeslabel=None):
    return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def delete(dbfile=cacheFile):

    deleteFile(dbfile)

    infoDialog('You are ready to go!!!')


