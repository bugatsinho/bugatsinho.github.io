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


import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
import os, json, six

integer = 1000
lang = xbmcaddon.Addon().getLocalizedString
setting = xbmcaddon.Addon().getSetting
setSetting = xbmcaddon.Addon().setSetting
addon = xbmcaddon.Addon
addonInfo = xbmcaddon.Addon().getAddonInfo

addItem = xbmcplugin.addDirectoryItem
addItems = xbmcplugin.addDirectoryItems
directory = xbmcplugin.endOfDirectory
content = xbmcplugin.setContent
property = xbmcplugin.setProperty
resolve = xbmcplugin.setResolvedUrl
sortmethod = xbmcplugin.addSortMethod

infoLabel = xbmc.getInfoLabel
condVisibility = xbmc.getCondVisibility
jsonrpc = xbmc.executeJSONRPC  # keeping this for compatibility
keyboard = xbmc.Keyboard
sleep = xbmc.sleep
execute = xbmc.executebuiltin
skin = xbmc.getSkinDir()
player = xbmc.Player()
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
monitor = xbmc.Monitor()
wait = monitor.waitForAbort
aborted = monitor.abortRequested

if six.PY2:
    translatePath = xbmc.translatePath
else:
    import xbmcvfs
    translatePath = xbmcvfs.translatePath

skinPath = translatePath('special://skin/')
addonPath = translatePath(addonInfo('path'))
dataPath = translatePath(addonInfo('profile'))


window = xbmcgui.Window(10000)
dialog = xbmcgui.Dialog()
progressDialog = xbmcgui.DialogProgress()
windowDialog = xbmcgui.WindowDialog()
button = xbmcgui.ControlButton
image = xbmcgui.ControlImage
alphanum_input = xbmcgui.INPUT_ALPHANUM
password_input = xbmcgui.INPUT_PASSWORD
hide_input = xbmcgui.ALPHANUM_HIDE_INPUT
verify = xbmcgui.PASSWORD_VERIFY
item = xbmcgui.ListItem

openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
deleteFile = xbmcvfs.delete
deleteDir = xbmcvfs.rmdir
listDir = xbmcvfs.listdir
exists = xbmcvfs.exists
copy = xbmcvfs.copy

join = os.path.join
DatabasePath = translatePath("special://userdata/Database")
settingsFile = join(dataPath, 'settings.xml')
bookmarksFile = join(dataPath, 'bookmarks.db')
viewsFile = join(dataPath, 'views.db')
DBviewsFile = join(DatabasePath, 'ViewModes6.db')
searchFile = join(dataPath, 'search.db')
cacheFile = join(dataPath, 'cache.db')


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


def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)


def openSettings(query=None, id=addonInfo('id')):
    idle()
    execute('Addon.OpenSettings({0})'.format(id))

    if query is not None:

        try:

            c, f = query.split('.')
            if float(addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
                execute('SetFocus(-{0})'.format(100 - int(c)))
                if int(f):
                    execute('SetFocus(-{0})'.format(80 - int(f)))
            else:
                execute('SetFocus({0})'.format(100 + int(c)))
                if int(f):
                    execute('SetFocus({0})'.format(200 + int(f)))

        except Exception:
            pass



# Alternative method
def Settings(id=addonInfo('id')):

    try:
        idle()
        xbmcaddon.Addon(id).openSettings()
    except:
        return


def openPlaylist():

    return execute('ActivateWindow(VideoPlaylist)')


def refresh():
    return execute('Container.Refresh')


def idle():

    if float(addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        execute('Dialog.Close(busydialognocancel)')
    else:
        execute('Dialog.Close(busydialog)')


def busy():

    if float(addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        execute('ActivateWindow(busydialognocancel)')
    else:
        execute('ActivateWindow(busydialog)')


def set_view_mode(vmid):
    return execute('Container.SetViewMode({0})'.format(vmid))


def getKodiVersion():
    return xbmc.getInfoLabel("System.BuildVersion").split(".")[0]


def getCurrentViewId():
    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return str(win.getFocusId())


# for compartmentalized theme addons
def addonmedia(icon, addonid=addonInfo('id'), theme=None, media_subfolder=True):
    if not theme:
        return join(addon(addonid).getAddonInfo('path'), 'resources', 'media' if media_subfolder else '', icon)
    else:
        return join(addon(addonid).getAddonInfo('path'), 'resources', 'media' if media_subfolder else '', theme, icon)



def json_rpc(command):

    # This function was taken from tknorris's kodi.py

    if not isinstance(command, basestring):
        command = json.dumps(command)
    response = jsonrpc(command)

    return json.loads(response)


def addon_details(addon_id, fields=None):

    """
    :param addon_id: Any addon id as string
    :param fields: Possible fields as list [
      "name",
      "version",
      "summary",
      "description",
      "path",
      "author",
      "thumbnail",
      "disclaimer",
      "fanart",
      "dependencies",
      "broken",
      "extrainfo",
      "rating",
      "enabled",
      "installed"
    ]
    Default argument: ["enabled"]
    :return: Dictionary
    """

    if fields is None:
        fields = ["enabled"]

    command = {
        "jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "id": 1, "params": {
            "addonid": addon_id, "properties": fields
        }
    }

    result = json_rpc(command)['result']['addon']

    return result


def enable_addon(addon_id, enable=True):

    command = {
        "jsonrpc":"2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": addon_id, "enabled": enable}, "id": 1
    }

    json_rpc(command)


def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'


def open_git(url=None):
    try:
        if not url:
            git_url = 'https://github.com/bugatsinho/bugatsinho.github.io/tree/master/plugin.video.releaseBB'
        else:
            git_url = url
        if platform() == 'android':  # Android
            return xbmc.executebuiltin('StartAndroidActivity(,android.intent.action.VIEW,,%s)' % git_url)
        else:
            import webbrowser
            return webbrowser.open(git_url)
    except BaseException:
        return




