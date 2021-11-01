# -*- coding: utf-8 -*-

'''
    CartoonsGR Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
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

from resources.lib.modules import control


def addView(content):
    try:
        skin = control.skin
        record = (skin, content, str(control.getCurrentViewId()))
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.viewsFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS views"
                      " (""skin TEXT, ""view_type TEXT, ""view_id TEXT, ""UNIQUE(skin, view_type)"");")
        dbcur.execute("DELETE FROM views WHERE skin = ? AND view_type = ?", (record[0], record[1],))
        dbcur.execute("INSERT INTO views Values (?, ?, ?)", record)
        dbcon.commit()

        viewName = control.infoLabel('Container.Viewmode')
        skinName = control.addon(skin).getAddonInfo('name')
        skinIcon = control.addon(skin).getAddonInfo('icon')

        control.infoDialog(viewName, heading=skinName, icon=skinIcon)
    except:
        return


def setView(content, viewDict=None):
    for i in range(0, 200):
        if control.condVisibility('Container.Content(%s)' % content):
            try:
                skin = control.skin
                record = (skin, content)
                dbcon = database.connect(control.viewsFile)
                dbcur = dbcon.cursor()
                dbcur.execute("SELECT * FROM views WHERE skin = ? AND view_type = ?", (record[0], record[1],))
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

        control.sleep(5)


def selectView(content, viewtype):
    import xbmcplugin, sys, xbmc
    ''' Why recode whats allready written and works well,
    Thanks go to Eldrado for it '''
    if content:
        content = 'movies'
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if control.setting('auto-view') == 'true':

        print(control.setting(viewtype))
        if control.setting(viewtype) == 'Info':
            VT = '504'
        elif control.setting(viewtype) == 'Info2':
            VT = '503'
        elif control.setting(viewtype) == 'Info3':
            VT = '515'
        elif control.setting(viewtype) == 'Fanart':
            VT = '508'
        elif control.setting(viewtype) == 'Poster Wrap':
            VT = '501'
        elif control.setting(viewtype) == 'Big List':
            VT = '51'
        elif control.setting(viewtype) == 'Low List':
            VT = '724'
        elif control.setting(viewtype) == 'List':
            VT = '50'
        elif control.setting(viewtype) == 'WideList':
            VT = '55'
        elif control.setting(viewtype) == 'Default Menu View':
            VT = control.setting('default-view1')
        elif control.setting(viewtype) == 'Default TV Shows View':
            VT = control.setting('default-view2')
        elif control.setting(viewtype) == 'Default Episodes View':
            VT = control.setting('default-view3')
        elif control.setting(viewtype) == 'Default Movies View':
            VT = control.setting('default-view4')
        elif control.setting(viewtype) == 'Default Docs View':
            VT = control.setting('default-view5')
        elif control.setting(viewtype) == 'Default Cartoons View':
            VT = control.setting('default-view6')
        elif control.setting(viewtype) == 'Default Anime View':
            VT = control.setting('default-view7')

        print(viewtype)
        print(VT)

        xbmc.executebuiltin("Container.SetViewMode(%s)" % (int(VT)))
