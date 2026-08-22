# -*- coding: utf-8 -*-
"""Background service: watches Kodi playback and marks the currently-playing item
watched on MDBList once playback crosses ~90%, mirroring what script.trakt does
for Trakt scrobbling. Only acts on items played through this addon -- identified
via the 'plugin.video.rlsbb.now_playing' window property rlsbb.play() sets."""
import json

import xbmc
import xbmcgui

from resources.lib.modules import mdblist

_PROPERTY = 'plugin.video.rlsbb.now_playing'
_THRESHOLD = 0.90


class _WatchedMonitor(xbmc.Player):
    def __init__(self):
        super().__init__()
        self._marked = False

    def onPlayBackStarted(self):
        self._marked = False

    def onAVStarted(self):
        self._marked = False

    def _maybe_mark(self):
        if self._marked:
            return
        window = xbmcgui.Window(10000)
        raw = window.getProperty(_PROPERTY)
        if not raw:
            return
        try:
            info = json.loads(raw)
            imdb = info.get('imdb')
            if not imdb:
                return
            total = self.getTotalTime()
            current = self.getTime()
        except Exception:
            return
        if total and (current / total) >= _THRESHOLD:
            self._marked = True
            media_type = info.get('type') or 'movie'
            mdblist.mark_watched(media_type, imdb=imdb, season=info.get('season'),
                                  episode_number=info.get('episode'))
            window.clearProperty(_PROPERTY)

    def onPlayBackStopped(self):
        self._maybe_mark()

    def onPlayBackEnded(self):
        self._maybe_mark()


def run():
    player = _WatchedMonitor()
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(30):
            break
    del player


if __name__ == '__main__':
    run()
