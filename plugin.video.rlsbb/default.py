# -*- coding: utf-8 -*-
import xbmc

from resources.lib.indexers import rlsbb
from resources.lib.modules import cache, control, init

params = init.params
mode = params.get('mode', '')

xbmc.log('plugin.video.rlsbb :: mode={0} url={1}'.format(mode, params.get('url', '')),
          xbmc.LOGDEBUG)

if mode == '':
    rlsbb.main_menu()

elif mode == 'category':
    rlsbb.category(params['url'])

elif mode == 'recommended_movies':
    rlsbb.recommended_movies()

elif mode == 'listing_movies':
    rlsbb.listing(params['url'], params.get('page', '1'), content_type='movies')

elif mode == 'listing_episodes':
    rlsbb.listing(params['url'], params.get('page', '1'), content_type='episodes')

elif mode == 'search_menu':
    rlsbb.search_menu()

elif mode == 'search_new':
    keyboard = xbmc.Keyboard('', 'Search ReleaseBB')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        rlsbb.search(keyboard.getText())

elif mode == 'search_history_item':
    rlsbb.search(params['url'], poster=params.get('iconimage', ''))

elif mode == 'detail':
    rlsbb.detail(params['url'], poster=params.get('iconimage', ''))

elif mode == 'play':
    rlsbb.play(params['url'])

elif mode == 'season_pack':
    rlsbb.season_pack(params['url'])

elif mode == 'trakt_menu':
    rlsbb.trakt_menu()

elif mode == 'trakt_mdblist_info':
    rlsbb.trakt_mdblist_info()

elif mode == 'trakt_auth':
    rlsbb.trakt_auth()

elif mode == 'trakt_signout':
    rlsbb.trakt_signout()

elif mode == 'trakt_install':
    rlsbb.trakt_install(params['url'])

elif mode == 'mdblist_auth':
    rlsbb.mdblist_auth()

elif mode == 'mdblist_menu':
    rlsbb.mdblist_menu()

elif mode == 'mdblist_signout':
    rlsbb.mdblist_signout()

elif mode == 'mdblist_scrobbler_info':
    rlsbb.mdblist_scrobbler_info()

elif mode == 'mdblist_watchlist':
    rlsbb.mdblist_watchlist()

elif mode == 'mdblist_upnext':
    rlsbb.mdblist_upnext()

elif mode == 'mdblist_watched':
    rlsbb.mdblist_watched()

elif mode == 'mdblist_liked_lists':
    rlsbb.mdblist_liked_lists()

elif mode == 'mdblist_user_lists':
    rlsbb.mdblist_user_lists()

elif mode == 'mdblist_list_items':
    rlsbb.mdblist_list_items(params['url'])

elif mode == 'mdblist_remove_watchlist':
    rlsbb.mdblist_remove_watchlist(params.get('type', 'movie'), params.get('imdb', ''),
                                    params.get('tmdb', ''))

elif mode == 'mdblist_remove_list_item':
    rlsbb.mdblist_remove_list_item(params.get('listid', ''), params.get('type', 'movie'),
                                    params.get('imdb', ''), params.get('tmdb', ''))

elif mode == 'mdblist_unlike':
    rlsbb.mdblist_unlike(params['url'])

elif mode == 'mdblist_mark_watched':
    rlsbb.mdblist_mark_watched(params.get('type', 'movie'), params.get('imdb', ''),
                                params.get('tmdb', ''), params.get('season', ''),
                                params.get('episode', ''))

elif mode == 'mdblist_remove_watched':
    rlsbb.mdblist_remove_watched(params.get('type', 'movie'), params.get('imdb', ''),
                                  params.get('tmdb', ''), params.get('season', ''),
                                  params.get('episode', ''))

elif mode == 'mdblist_rate':
    rlsbb.mdblist_rate(params.get('type', 'movie'), params.get('imdb', ''), params.get('tmdb', ''),
                        params.get('season', ''), params.get('episode', ''))

elif mode == 'force_update_repos':
    rlsbb.force_update_repos()

elif mode == 'save_view':
    rlsbb.save_view(params['url'])

elif mode == 'view_reset':
    rlsbb.view_reset()

elif mode == 'tools_menu':
    rlsbb.tools_menu()

elif mode == 'tools_view_info':
    rlsbb.tools_view_info(params['url'])

elif mode == 'settings':
    control.Settings()

elif mode == 'resolver_settings':
    import resolveurl
    resolveurl.display_settings()

elif mode == 'cache_clear':
    cache.delete(control.cacheFile, withyes=False)
