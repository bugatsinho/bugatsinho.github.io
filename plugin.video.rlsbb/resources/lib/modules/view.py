# -*- coding: utf-8 -*-
"""Kodi doesn't reliably keep a chosen view mode across this addon's own listings --
every paginated/query-string plugin:// URL counts as its own distinct path to Kodi's
view-memory, so picking "Poster" on page 1 and hitting Next Page drops back to the
skin's default view. This remembers the user's last-picked view per (skin, content
type) and reapplies it at the end of every listing -- the same approach used across
most Kodi scraper addons (Covenant/Exodus-style forks), still the standard fix.

Container.SetViewMode is known to silently no-op when called immediately after
endOfDirectory() -- https://github.com/xbmc/xbmc/issues/18576 -- Kodi hasn't actually
finished switching the container to the new listing yet, so its own view-restore
logic runs AFTER our call and overwrites it. A fixed short sleep isn't long enough
for that to reliably settle -- waiting until Container.Content() actually matches
the new listing (confirming Kodi has switched over) before firing SetViewMode is
what actually works; this is the same idea the old releaseBB addon's polling loop
used, just via Monitor.waitForAbort() instead of a raw sleep loop."""
import sqlite3

import xbmc
import xbmcgui

from resources.lib.modules import control


def _skin():
    return xbmc.getSkinDir()


def _table(dbcur):
    dbcur.execute('CREATE TABLE IF NOT EXISTS views (skin TEXT, content_type TEXT, '
                  'view_id TEXT, UNIQUE(skin, content_type))')


def get_view(content_type):
    try:
        dbcon = sqlite3.connect(control.viewsFile)
        dbcur = dbcon.cursor()
        _table(dbcur)
        dbcur.execute('SELECT view_id FROM views WHERE skin = ? AND content_type = ?',
                       (_skin(), content_type))
        row = dbcur.fetchone()
        return row[0] if row else None
    except Exception:
        return None


def apply_view(content_type):
    view_id = get_view(content_type)
    if not view_id:
        return
    monitor = xbmc.Monitor()
    for _ in range(50):  # up to ~5s -- generous but bounded, only hit on a slow load
        if xbmc.getCondVisibility('Container.Content({0})'.format(content_type)):
            break
        if monitor.waitForAbort(0.1):
            return  # Kodi shutting down -- nothing left to apply a view to
    # Container.Content() matches instantly when the new listing's content type is the
    # SAME as the previous one (e.g. moving between two 'movies' folders) -- it doesn't
    # mean the container has actually finished switching. A single SetViewMode call here
    # still loses the race to Kodi's own per-path default-view restore, which runs right
    # after. Re-firing for a bit guarantees ours is the last write.
    for _ in range(6):
        xbmc.executebuiltin('Container.SetViewMode({0})'.format(view_id))
        if monitor.waitForAbort(0.15):
            return


def save_view(content_type):
    # Container.Viewmode infolabel returns the localized MODE NAME ("List", "Wall"),
    # not the numeric id Container.SetViewMode() needs -- the focused control's id in
    # the skin window IS that numeric view id (same trick the old releaseBB addon used).
    view_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
    if not view_id:
        return
    try:
        control.makeFile(control.dataPath)
        dbcon = sqlite3.connect(control.viewsFile)
        dbcur = dbcon.cursor()
        _table(dbcur)
        dbcur.execute('INSERT OR REPLACE INTO views VALUES (?, ?, ?)',
                       (_skin(), content_type, view_id))
        dbcon.commit()
    except Exception:
        pass
    control.infoDialog('This view is now the default for this section')


def clear_views():
    try:
        dbcon = sqlite3.connect(control.viewsFile)
        dbcur = dbcon.cursor()
        _table(dbcur)
        dbcur.execute('DELETE FROM views')
        dbcon.commit()
    except Exception:
        pass
    control.infoDialog('Saved view types cleared')
