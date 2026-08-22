# -*- coding: utf-8 -*-
import json

import xbmc
import xbmcgui

from resources.lib.modules import control


def set_ids(imdb=None, tmdb=None, tvdb=None):
    """Set the window property script.trakt reads to scrobble non-library plugin playback.
    No-op if the user disabled it or script.trakt isn't installed."""
    if control.setting('trakt.scrobble') != 'true':
        return
    if not xbmc.getCondVisibility('System.HasAddon(script.trakt)'):
        return
    ids = {k: v for k, v in (('imdb', imdb), ('tmdb', tmdb), ('tvdb', tvdb)) if v}
    if ids:
        xbmcgui.Window(10000).setProperty('script.trakt.ids', json.dumps(ids))


def clear_ids():
    xbmcgui.Window(10000).clearProperty('script.trakt.ids')
