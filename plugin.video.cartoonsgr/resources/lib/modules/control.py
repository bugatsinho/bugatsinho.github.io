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
import os, json
from init import syshandle


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

transPath = xbmc.translatePath
skinPath = xbmc.translatePath('special://skin/')
addonPath = xbmc.translatePath(addonInfo('path'))
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')

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
settingsFile = os.path.join(dataPath, 'settings.xml')
bookmarksFile = os.path.join(dataPath, 'bookmarks.db')
cacheFile = os.path.join(dataPath, 'cache.db')


def infoDialog(message, heading=addonInfo('name'), icon='', time=3000):

    if icon == '':
        icon = addonInfo('icon')

    try:

        dialog.notification(heading, message, icon, time, sound=False)

    except:

        execute("Notification(%s, %s, %s, %s)" % (heading, message, time, icon))


def okDialog(heading, line1):
    return dialog.ok(heading, line1)


def yesnoDialog(line1, line2='', line3='', heading=addonInfo('name'), nolabel=None, yeslabel=None):
    return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)


def openSettings(query=None, id=addonInfo('id')):

    try:

        idle()
        execute('Addon.OpenSettings({0})'.format(id))
        if query is None:
            raise Exception()
        c, f = query.split('.')
        execute('SetFocus(%i)' % (int(c) + 100))
        execute('SetFocus(%i)' % (int(f) + 200))

    except:

        return


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
    return execute('Dialog.Close(busydialog)')


def set_view_mode(vmid):
    return execute('Container.SetViewMode({0})'.format(vmid))


# for compartmentalized theme addons
def addonmedia(icon, addonid=addonInfo('id'), theme=None, media_subfolder=True):
    if not theme:
        return join(addon(addonid).getAddonInfo('path'), 'resources', 'media' if media_subfolder else '', icon)
    else:
        return join(addon(addonid).getAddonInfo('path'), 'resources', 'media' if media_subfolder else '', theme, icon)


def sortmethods(method='unsorted', mask='%D'):

    """
    Function to sort directory items

    :param method: acceptable values are: TODO
    :param mask: acceptable values are: TODO
    :type method: str
    :type mask: str
    :return: call existing function and pass parameters
    :rtype: xbmcplugin.addSortMethod(handle=syshandle, sortMethod=int)
    :note: Method to sort directory items
    """

    #  "%A" "%B" "%C" "%D" ...

    if method == 'none':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask=mask)
    elif method == 'label':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_LABEL, label2Mask=mask)
    elif method == 'label_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, label2Mask=mask)
    elif method == 'date':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    elif method == 'size':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_SIZE)
    elif method == 'file':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_FILE, label2Mask=mask)
    elif method == 'drive_type':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_DRIVE_TYPE)
    elif method == 'tracknum':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_TRACKNUM, label2Mask=mask)
    elif method == 'duration':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_DURATION)
    elif method == 'title':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask=mask)
    elif method == 'title_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE, label2Mask=mask)
    elif method == 'artist':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_ARTIST)
    elif method == 'artist_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_ARTIST_IGNORE_THE)
    elif method == 'album':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_ALBUM)
    elif method == 'album_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_ALBUM_IGNORE_THE)
    elif method == 'genre':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
    elif method == 'year':
        try:
            return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_YEAR)
        except:
            return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    elif method == 'video_rating':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING)
    elif method == 'program_count':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
    elif method == 'playlist_order':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
    elif method == 'episode':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_EPISODE)
    elif method == 'video_title':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE, label2Mask=mask)
    elif method == 'video_sort_title':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE, label2Mask=mask)
    elif method == 'video_sort_title_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE, label2Mask=mask)
    elif method == 'production_code':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_PRODUCTIONCODE)
    elif method == 'song_rating':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_SONG_RATING)
    elif method == 'mpaa_rating':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING)
    elif method == 'video_runtime':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    elif method == 'studio':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
    elif method == 'studio_ignore_the':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
    elif method == 'unsorted':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED, label2Mask=mask)
    elif method == 'bitrate':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_BITRATE)
    elif method == 'listeners':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_LISTENERS)
    elif method == 'country':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_COUNTRY)
    elif method == 'date_added':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_DATEADDED)
    elif method == 'full_path':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_FULLPATH, label2Mask=mask)
    elif method == 'label_ignore_folders':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS, label2Mask=mask)
    elif method == 'last_played':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_LASTPLAYED)
    elif method == 'play_count':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_PLAYCOUNT)
    elif method == 'channel':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_CHANNEL, label2Mask=mask)
    elif method == 'date_taken':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_DATE_TAKEN)
    elif method == 'video_user_rating':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_USER_RATING)
    elif method == 'song_user_rating':
        return sortmethod(handle=syshandle, sortMethod=xbmcplugin.SORT_METHOD_SONG_USER_RATING)
    else:
        pass


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
