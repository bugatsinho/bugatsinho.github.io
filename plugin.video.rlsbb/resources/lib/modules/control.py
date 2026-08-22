# -*- coding: utf-8 -*-
"""
Kodi API alias grab-bag, matching the shape used by sibling addons
(plugin.video.cartoonsgr resources/lib/modules/control.py) minus the Python 2 shims.
"""
import json
import os
import sys
from urllib.parse import quote_plus, unquote

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources.lib.modules import init
from resources.lib.modules.init import syshandle

lang = xbmcaddon.Addon().getLocalizedString
setting = xbmcaddon.Addon().getSetting
setSetting = xbmcaddon.Addon().setSetting
addon = xbmcaddon.Addon
addonInfo = xbmcaddon.Addon().getAddonInfo

addItem = xbmcplugin.addDirectoryItem
addItems = xbmcplugin.addDirectoryItems
directory = xbmcplugin.endOfDirectory
content = xbmcplugin.setContent
resolve = xbmcplugin.setResolvedUrl
sortmethod = xbmcplugin.addSortMethod

infoLabel = xbmc.getInfoLabel
condVisibility = xbmc.getCondVisibility
jsonrpc = xbmc.executeJSONRPC
keyboard = xbmc.Keyboard
sleep = xbmc.sleep
execute = xbmc.executebuiltin
player = xbmc.Player()
monitor = xbmc.Monitor()
wait = monitor.waitForAbort
aborted = monitor.abortRequested

transPath = xbmcvfs.translatePath
addonPath = transPath(addonInfo('path'))
dataPath = transPath(addonInfo('profile'))

window = xbmcgui.Window(10000)
dialog = xbmcgui.Dialog()
progressDialog = xbmcgui.DialogProgress()
windowDialog = xbmcgui.WindowDialog
image = xbmcgui.ControlImage
item = xbmcgui.ListItem

openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
deleteFile = xbmcvfs.delete
exists = xbmcvfs.exists

join = os.path.join
cacheFile = join(dataPath, 'cache.db')
searchFile = join(dataPath, 'search.db')
viewsFile = join(dataPath, 'views.db')
upnextOverrideFile = join(dataPath, 'upnext_override.db')


def infoDialog(message, heading=None, icon='', time=3000):
    if heading is None:
        heading = addonInfo('name')
    if icon == '':
        icon = addonInfo('icon')
    try:
        dialog.notification(heading, message, icon, time, sound=False)
    except Exception:
        execute("Notification(%s, %s, %s, %s)" % (heading, message, time, icon))


def okDialog(heading, line1):
    return dialog.ok(heading, line1)


def yesnoDialog(line1, line2='', line3='', heading=None):
    if heading is None:
        heading = addonInfo('name')
    return dialog.yesno(heading, line1, line2, line3)


def selectDialog(items, heading=None):
    if heading is None:
        heading = addonInfo('name')
    return dialog.select(heading, items)


def _human_size(num_bytes):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if num_bytes < 1024:
            return '{0:.1f} {1}'.format(num_bytes, unit)
        num_bytes /= 1024.0
    return '{0:.1f} TB'.format(num_bytes)


def cache_size_label():
    size = os.path.getsize(cacheFile) if exists(cacheFile) else 0
    return _human_size(size)


def _view_summary(content_type):
    """Read-only lookup for settings.xml's Set View display fields -- kept inline
    (rather than importing the views module) since that module imports control,
    and a plain sqlite3 SELECT is little enough code to not be worth the circular
    import."""
    try:
        import sqlite3
        dbcon = sqlite3.connect(viewsFile)
        dbcur = dbcon.cursor()
        dbcur.execute('SELECT view_id FROM views WHERE skin = ? AND content_type = ?',
                       (xbmc.getSkinDir(), content_type))
        row = dbcur.fetchone()
        return 'View {0}'.format(row[0]) if row else 'Not set'
    except Exception:
        return 'Not set'


def Settings(id=None):
    try:
        idle()
        if not id:
            # settings.xml has read-only display fields just to show these -- there's
            # no InfoLabel support in the addon's (legacy, flat) settings.xml schema
            # for a live-updating value, so they're refreshed here each time Settings()
            # is about to open
            setSetting('cache_size_display', cache_size_label())
            setSetting('view_movies_display', _view_summary('movies'))
            setSetting('view_episodes_display', _view_summary('episodes'))
            setSetting('view_files_display', _view_summary('files'))
        xbmcaddon.Addon(id or addonInfo('id')).openSettings()
    except Exception:
        return


def refresh():
    return execute('Container.Refresh')


def idle():
    execute('Dialog.Close(busydialognocancel)')


def busy():
    execute('ActivateWindow(busydialognocancel)')


def json_rpc(command):
    if not isinstance(command, str):
        command = json.dumps(command)
    response = jsonrpc(command)
    return json.loads(response)


def addDir(name, url, mode, iconimage='', fanart='', description='', is_folder=True,
           is_playable=False, context_menu=None):
    """Build one directory/playable ListItem and add it to the current listing."""
    u = '%s?url=%s&mode=%s&name=%s&iconimage=%s&description=%s' % (
        init.sysaddon, quote_plus(url), quote_plus(str(mode)), quote_plus(name),
        quote_plus(iconimage), quote_plus(description))

    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    info = liz.getVideoInfoTag()
    info.setTitle(name)
    info.setPlot(description)
    if is_playable:
        liz.setProperty('IsPlayable', 'true')
    if context_menu:
        liz.addContextMenuItems(context_menu)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=is_folder)
