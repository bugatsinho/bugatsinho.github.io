# -*- coding: utf-8 -*-
'''
    Based on Covenant's viewtypes
    Author Bugatsinho

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

try:
    from sqlite3 import dbapi2 as database
except ImportError:
    from pysqlite2 import dbapi2 as database

from resources.lib.modules import control, cache


def addView(content):
    #try:
        skin = control.skin
        record = (skin, content, str(control.getCurrentViewId()))
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.viewsFile)
        dbcur = dbcon.cursor()
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS views ("
            "skin TEXT, "
            "view_type TEXT, "
            "view_id TEXT, "
            "UNIQUE(skin, view_type)"
            ");")
        dbcur.execute(
            "DELETE FROM views WHERE skin = '%s' AND view_type = '%s'" %
            (record[0], record[1]))
        dbcur.execute("INSERT INTO views Values (?, ?, ?)", record)
        dbcon.commit()

        viewName = control.infoLabel('Container.Viewmode')
        if content == 'addons':
            control.setSetting('menu-view', viewName)
        elif content == 'movies':
            control.setSetting('movie-view', viewName)
        else:
            control.setSetting('links-view', viewName)
        skinName = control.addon(skin).getAddonInfo('name')
        skinIcon = control.addon().getAddonInfo('icon')

        control.infoDialog(viewName, heading=skinName, icon=skinIcon, time=3000)
    # except BaseException:
    #     return


def setView(content, viewDict=None):

    if content == 'search':
        content2 = content
        content = 'movies'
    else:
        content2 = content

    for i in range(0, 200):
        if control.condVisibility('Container.Content(%s)' % content):
            try:
                skin = control.skin
                record = (skin, content2)
                dbcon = database.connect(control.viewsFile)
                dbcur = dbcon.cursor()
                dbcur.execute(
                    "SELECT * FROM views WHERE skin = '%s' AND view_type = '%s'" %
                    (record[0], record[1]))
                view = dbcur.fetchone()
                view = view[2]
                if view is None:
                    raise Exception()
                return control.execute('Container.SetViewMode(%s)' % str(view))
            except BaseException:
                try:
                    return control.execute('Container.SetViewMode(%s)' % str(viewDict[skin]))
                except BaseException:
                    return
        control.sleep(100)
    skin = control.skin
    try:
        return control.execute(
            'Container.SetViewMode(%s)' % str(viewDict[skin]))
    except BaseException:
        return


def view_clear():
    cache.delete(control.viewsFile, withyes=False)
    control.refresh()
    control.idle()
