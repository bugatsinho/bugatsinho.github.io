# -*- coding: utf-8 -*-
"""Site scraper for rlsbb.to -- categories, listings, search, post detail, and the play
handoff (protected.to gate -> resolveurl -> trakt ids -> playback)."""
import re
import sqlite3
import time
from urllib.parse import quote_plus, urlparse

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.modules import cache, client, control, init, metadata, rarpack, tmdb, trakt_bridge, view
from resources.lib.modules.resolveurl_bridge import evaluate as resolveurl_evaluate
from resources.lib.resolvers import protected_to

_CATEGORIES = [
    ('Movies', 'movies', 'movies.png'),
    ('TV Shows', 'tv-shows', 'tvshows.png'),
    ('Foreign Movies', 'foreign-movies', 'movies.png'),
]

_ICON_DIR = control.join(control.addonPath, 'resources', 'icons')


def _icon(name):
    return control.join(_ICON_DIR, name) if name else ''

# link labels that are never a playable video download, even when they share the
# protected.to gate (safety net alongside the nfo.protected.to hostname check)
_NON_DOWNLOAD_LABELS = {'nfo', 'subtitles', 'trailer', 'imdb', 'torrent search'}

# maps a post link's own label to the hostname protected.to's post-captcha host-picker
# screen uses, so resolve() can pick the right one when a gate offers several
_HOST_HINTS = {'rapidgator': 'rapidgator.net', 'nitroflare': 'nitroflare.com'}


def _host_hint(label):
    low = label.lower()
    for key, hostname in _HOST_HINTS.items():
        if key in low:
            return hostname
    return None


def _end_directory(content_type='files', apply_saved_view=True):
    xbmcplugin.setContent(init.syshandle, content_type)
    xbmcplugin.endOfDirectory(init.syshandle)
    if apply_saved_view:
        view.apply_view(content_type)


def _view_context_menu(content_type):
    """"Set as Default View" -- reachable from Kodi's own item context menu (right
    click / long-press OK) instead of a dedicated menu entry, since that's easy to
    miss and this only needs doing once per section."""
    action = 'RunPlugin({0}?url={1}&mode=save_view)'.format(init.sysaddon, quote_plus(content_type))
    return [('Set as Default View', action)]


def save_view(content_type):
    view.save_view(content_type)
    xbmc.executebuiltin('Container.Refresh')


def view_reset():
    view.clear_views()


def _mdblist_username_suffix():
    from resources.lib.modules import mdblist
    if not mdblist.is_authenticated():
        return ''
    username = mdblist.get_username()
    return ' [COLOR gold]({0})[/COLOR]'.format(username) if username else ''


def _trakt_username():
    # script.trakt manages its own auth (RunScript action=auth_info) and stores the
    # result in its OWN addon settings -- id="user" (plain trakt username) and
    # id="authorization" (the token blob) -- there's no API of its own to read this,
    # so reading those settings directly is the only way to show connection status.
    if not xbmc.getCondVisibility('System.HasAddon(script.trakt)'):
        return ''
    try:
        import xbmcaddon
        return xbmcaddon.Addon('script.trakt').getSetting('user') or ''
    except Exception:
        return ''


def _trakt_username_suffix():
    username = _trakt_username()
    return ' [COLOR gold]({0})[/COLOR]'.format(username) if username else ''


def main_menu():
    for name, section, icon in _CATEGORIES:
        control.addDir(name, section, 'category', iconimage=_icon(icon))
    control.addDir('Search', '', 'search_menu', iconimage=_icon('search.png'))
    control.addDir('Trakt{0}'.format(_trakt_username_suffix()), '', 'trakt_menu',
                    iconimage=_icon('trakt.png'))
    control.addDir('MDBList{0}'.format(_mdblist_username_suffix()), '', 'mdblist_menu',
                    iconimage=_icon('mdblist.png'))
    control.addDir('Tools', '', 'tools_menu', iconimage=_icon('tools.png'))
    control.addDir('[COLOR orange][B]VERSION: {0}[/B][/COLOR]'.format(control.addonInfo('version')),
                    '', 'force_update_repos', is_folder=False)
    _end_directory()


def force_update_repos():
    xbmc.executebuiltin('UpdateAddonRepos')
    control.infoDialog('Checking repositories for updates')


_VIEW_TOOLS_LABELS = [('Movies', 'movies'), ('Episodes', 'episodes'), ('Links', 'files')]


def tools_menu():
    for label, content_type in _VIEW_TOOLS_LABELS:
        saved = view.get_view(content_type)
        status = ('[COLOR lime]View {0}[/COLOR]'.format(saved) if saved
                   else '[COLOR orange]Not set[/COLOR]')
        control.addDir('Set View -- {0}: {1}'.format(label, status),
                        content_type, 'tools_view_info', iconimage=_icon('tools.png'),
                        is_folder=False)
    control.addDir('Clear Cache [COLOR gray]({0})[/COLOR]'.format(control.cache_size_label()),
                    '', 'cache_clear', is_folder=False, iconimage=_icon('tools.png'))
    control.addDir('Settings', '', 'settings', is_folder=False, iconimage=_icon('tools.png'))
    _end_directory()


def tools_view_info(content_type):
    control.infoDialog('Set the view from any {0} listing -- right-click / long-press '
                        'OK on an item, "Set as Default View"'.format(content_type))


_TRAKT_ADDONS = [
    ('script.trakt', 'Trakt Scrobbler (script.trakt)'),
    ('context.trakt.rate', 'Rate on Trakt'),
    ('context.trakt.watched', 'Mark Watched on Trakt'),
    ('context.trakt.addtowatchlist', 'Add to Trakt Watchlist'),
    ('context.trakt.contextmenu', 'Trakt Context Menu'),
]


def trakt_menu():
    control.addDir('[COLOR gold]Trakt sync issues? Try MDBList instead[/COLOR]', '',
                    'trakt_mdblist_info', is_folder=False, iconimage=_icon('trakt.png'))
    username = _trakt_username()
    if username:
        control.addDir('[COLOR gold][B]Connected as {0}[/B][/COLOR]'.format(username), '',
                        'trakt_auth', is_folder=False, iconimage=_icon('trakt.png'))
        control.addDir('Sign Out of Trakt', '', 'trakt_signout', is_folder=False,
                        iconimage=_icon('trakt.png'))
    else:
        control.addDir('Authenticate with Trakt', '', 'trakt_auth', is_folder=False,
                        iconimage=_icon('trakt.png'))
    for addon_id, label in _TRAKT_ADDONS:
        installed = xbmc.getCondVisibility('System.HasAddon({0})'.format(addon_id))
        if installed:
            try:
                import xbmcaddon
                version = xbmcaddon.Addon(addon_id).getAddonInfo('version')
            except Exception:
                version = '?'
            status = '[COLOR cyan][B]INSTALLED v{0}[/B][/COLOR]'.format(version)
        else:
            status = '[COLOR gold][B]INSTALL[/B][/COLOR]'
        control.addDir('{0} - {1}'.format(label, status), addon_id, 'trakt_install', is_folder=False,
                        iconimage=_icon('trakt.png'))
    _end_directory()


def trakt_mdblist_info():
    control.okDialog(
        'Trakt Sync via MDBList',
        "Trakt's own sync can be unreliable. MDBList.com offers a free, more reliable "
        "way to sync your watchlist/history -- no Trakt VIP needed.\n\n"
        "1. Go to mdblist.com and sign in\n"
        "2. In your account settings, connect/sync your Trakt account (\"Trakt Sync\")\n"
        "3. Come back here and use the MDBList menu (not Trakt) for your watchlist\n\n"
        "Note: building full native Trakt integration into this addon would require "
        "the developer to pay for a Trakt VIP subscription just to register the API "
        "app -- that's why MDBList (free) is the recommended path instead.")


def trakt_auth():
    if xbmc.getCondVisibility('System.HasAddon(script.trakt)'):
        xbmc.executebuiltin('RunScript(script.trakt, action=auth_info)')
    elif control.yesnoDialog('script.trakt is not installed. Install it now?'):
        xbmc.executebuiltin('InstallAddon(script.trakt)')


def trakt_signout():
    # script.trakt has no logout action of its own (only auth_info, which
    # re-authenticates) -- clearing its own stored user/authorization settings
    # directly is the only way to sign it out from here.
    if not xbmc.getCondVisibility('System.HasAddon(script.trakt)'):
        return
    if not control.yesnoDialog('Sign out of Trakt?'):
        return
    import xbmcaddon
    addon = xbmcaddon.Addon('script.trakt')
    addon.setSetting('user', '')
    addon.setSetting('authorization', '')
    control.infoDialog('Signed out of Trakt')
    xbmc.executebuiltin('Container.Refresh')


def trakt_install(addon_id):
    if xbmc.getCondVisibility('System.HasAddon({0})'.format(addon_id)):
        control.infoDialog('{0} is already installed'.format(addon_id))
    else:
        xbmc.executebuiltin('InstallAddon({0})'.format(addon_id))


def mdblist_auth():
    from resources.lib.modules import mdblist
    mdblist.authenticate()
    xbmc.executebuiltin('Container.Refresh')


def mdblist_menu():
    # MDBList can sync a user's Trakt watchlist/history on their own account (set
    # up once on mdblist.com), sidestepping Trakt's own VIP-gated app
    # registration -- see resources/lib/modules/mdblist.py for the full auth flow
    from resources.lib.modules import mdblist
    if not mdblist.is_authenticated():
        control.addDir('Authenticate with MDBList', '', 'mdblist_auth', is_folder=False,
                        iconimage=_icon('mdblist.png'))
        _end_directory()
        return
    control.addDir('Watchlist', '', 'mdblist_watchlist', iconimage=_icon('mdblist.png'))
    control.addDir('Up Next', '', 'mdblist_upnext', iconimage=_icon('mdblist.png'))
    control.addDir('Recently Watched', '', 'mdblist_watched', iconimage=_icon('mdblist.png'))
    control.addDir('Liked Lists', '', 'mdblist_liked_lists', iconimage=_icon('mdblist.png'))
    control.addDir('My Lists', '', 'mdblist_user_lists', iconimage=_icon('mdblist.png'))
    control.addDir('Sign Out', '', 'mdblist_signout', is_folder=False, iconimage=_icon('mdblist.png'))
    control.addDir(_mdblist_scrobbler_status_label(), '', 'mdblist_scrobbler_info', is_folder=False,
                    iconimage=_icon('mdblist.png'))
    _end_directory()


_MDBLIST_SCROBBLER_ID = 'service.mdblist-scrobbler'


def _mdblist_scrobbler_status_label():
    # this addon's own service.py already marks watched at ~90% via the same
    # imdb/season/episode it sets on the ListItem's VideoInfoTag -- that's ALSO
    # exactly what this companion addon reads via Kodi's own Player.GetItem, so no
    # extra wiring is needed on our side for it to pick up what we're playing. Not
    # in Kodi's official repo, so InstallAddon() can't just pull it -- point to the
    # manual steps instead of pretending a one-click install works.
    if xbmc.getCondVisibility('System.HasAddon({0})'.format(_MDBLIST_SCROBBLER_ID)):
        try:
            import xbmcaddon
            version = xbmcaddon.Addon(_MDBLIST_SCROBBLER_ID).getAddonInfo('version')
        except Exception:
            version = '?'
        status = '[COLOR cyan][B]INSTALLED v{0}[/B][/COLOR]'.format(version)
    else:
        status = '[COLOR gold][B]NOT INSTALLED[/B][/COLOR]'
    return 'MDBList Scrobbler (real-time progress) - {0}'.format(status)


def mdblist_scrobbler_info():
    if xbmc.getCondVisibility('System.HasAddon({0})'.format(_MDBLIST_SCROBBLER_ID)):
        control.infoDialog('MDBList Scrobbler is already installed')
        return
    control.okDialog(
        'MDBList Scrobbler (optional)',
        "This addon already marks things watched on MDBList automatically around "
        "90% playback -- no setup needed for that.\n\n"
        "For real-time progress (live % while playing, pause/resume sync, a rating "
        "prompt after watching), install the community 'MDBList Scrobbler' addon:\n\n"
        "1. Settings > File manager > Add source\n"
        "2. Add: https://linaspurinis.github.io/repository.mdblist/\n"
        "3. Add-ons > Install from zip file > that source > repository.mdblist\n"
        "4. Add-ons > Install from repository > MDBList Kodi Repository > "
        "MDBList Scrobbler\n"
        "5. Authenticate it with your MDBList account (its own separate sign-in)\n\n"
        "It reads what's playing straight from Kodi -- title, imdb id, season/"
        "episode -- which this addon already sets, so there's nothing else to wire "
        "up on this end.")


def mdblist_signout():
    from resources.lib.modules import mdblist
    mdblist.sign_out()
    control.infoDialog('Signed out of MDBList')
    control.refresh()


def _mdblist_item_url(item):
    title = item.get('title') or ''
    # for episodes, mdblist.py already bakes "S03E08" into the title itself, which
    # disambiguates on its own -- the site's episode posts never mention the show's
    # premiere year, so appending it (verified live) drops the search to ZERO results.
    # For movies there's no such marker, so a title-only query for e.g. "Denial" also
    # surfaces unrelated same-named releases from other years -- appending the year
    # narrows it the same way a user typing the search box themselves would.
    if item.get('type') == 'movie' and item.get('year'):
        return '{0} {1}'.format(title, item['year'])
    return title


def _mdblist_context_menu(item, extra=None):
    """Remove/mark-watched/rate context actions, shared by every MDBList-sourced
    item listing (watchlist, list items, ...)."""
    media_type = item.get('type', 'movie')
    imdb = item.get('imdb') or ''
    tmdb = item.get('tmdb') or ''
    # for an episode, tmdb/imdb above are the SHOW's own ids -- watched/rate/remove
    # identify the specific episode by nesting season+episode NUMBER underneath
    # those (see mdblist.py: mark_watched), not a separate per-episode id.
    season = item.get('season') or ''
    episode = item.get('episode') or ''
    base = ('plugin://plugin.video.rlsbb/?mode={0}&type={1}&imdb={2}&tmdb={3}'
             '&season={4}&episode={5}')
    menu = [
        ('Mark Watched (MDBList)',
         'RunPlugin({0})'.format(base.format('mdblist_mark_watched', media_type, imdb, tmdb, season, episode))),
        ('Remove Watched (MDBList)',
         'RunPlugin({0})'.format(base.format('mdblist_remove_watched', media_type, imdb, tmdb, season, episode))),
        ('Rate (MDBList)',
         'RunPlugin({0})'.format(base.format('mdblist_rate', media_type, imdb, tmdb, season, episode))),
    ]
    if extra:
        menu = extra + menu
    return menu


def _mdblist_label(item):
    label = item.get('title') or 'Untitled'
    if item.get('year'):
        label = '{0} ({1})'.format(label, item['year'])
    return label


def _mdblist_list_items(items):
    for item in items:
        control.addDir(_mdblist_label(item), _mdblist_item_url(item), 'search_history_item',
                        iconimage=item.get('poster', ''), description=item.get('plot', ''),
                        context_menu=_mdblist_context_menu(item))
    _end_directory()


def mdblist_watchlist():
    from resources.lib.modules import mdblist
    items = mdblist.get_watchlist()
    if items is None:
        control.infoDialog('Not authenticated with MDBList, or the request failed')
        _end_directory()
        return
    if not items:
        control.infoDialog('Your MDBList watchlist is empty')
        _end_directory()
        return
    for item in items:
        media_type = item.get('type', 'movie')
        remove = ('Remove from Watchlist (MDBList)',
                  'RunPlugin(plugin://plugin.video.rlsbb/?mode=mdblist_remove_watchlist'
                  '&type={0}&imdb={1}&tmdb={2})'.format(media_type, item.get('imdb') or '',
                                                          item.get('tmdb') or ''))
        control.addDir(_mdblist_label(item), _mdblist_item_url(item), 'search_history_item',
                        iconimage=item.get('poster', ''), description=item.get('plot', ''),
                        context_menu=_mdblist_context_menu(item, extra=[remove]))
    _end_directory()


def mdblist_upnext():
    from resources.lib.modules import mdblist
    items = mdblist.get_upnext()
    if items is None:
        control.infoDialog('Not authenticated with MDBList, or the request failed')
        _end_directory()
        return
    if not items:
        control.infoDialog('Nothing in progress right now')
    _mdblist_list_items(items or [])


def mdblist_watched():
    from resources.lib.modules import mdblist
    items = mdblist.get_watched()
    if items is None:
        control.infoDialog('Not authenticated with MDBList, or the request failed')
        _end_directory()
        return
    if not items:
        control.infoDialog('No watch history yet')
    _mdblist_list_items(items or [])


def _mdblist_lists_menu(lists, mode, unlike=False):
    if not lists:
        control.infoDialog('Nothing here yet')
    for lst in lists:
        name = lst.get('name') or 'Untitled list'
        context_menu = None
        if unlike:
            context_menu = [('Unlike List (MDBList)',
                              'RunPlugin(plugin://plugin.video.rlsbb/?mode=mdblist_unlike&url={0})'
                              .format(lst.get('id')))]
        control.addDir(name, str(lst.get('id')), mode, context_menu=context_menu)
    _end_directory()


def mdblist_liked_lists():
    from resources.lib.modules import mdblist
    lists = mdblist.get_liked_lists()
    if lists is None:
        control.infoDialog('Not authenticated with MDBList, or the request failed')
        _end_directory()
        return
    _mdblist_lists_menu(lists, 'mdblist_list_items', unlike=True)


def mdblist_user_lists():
    from resources.lib.modules import mdblist
    lists = mdblist.get_user_lists()
    if lists is None:
        control.infoDialog('Not authenticated with MDBList, or the request failed')
        _end_directory()
        return
    _mdblist_lists_menu(lists, 'mdblist_list_items')


def mdblist_list_items(list_id):
    from resources.lib.modules import mdblist
    items = mdblist.get_list_items(list_id)
    if items is None:
        control.infoDialog('Could not load this list')
        _end_directory()
        return
    for item in items:
        media_type = item.get('type', 'movie')
        remove = ('Remove from List (MDBList)',
                  'RunPlugin(plugin://plugin.video.rlsbb/?mode=mdblist_remove_list_item'
                  '&listid={0}&type={1}&imdb={2}&tmdb={3})'.format(
                      list_id, media_type, item.get('imdb') or '', item.get('tmdb') or ''))
        control.addDir(_mdblist_label(item), _mdblist_item_url(item), 'search_history_item',
                        iconimage=item.get('poster', ''), description=item.get('plot', ''),
                        context_menu=_mdblist_context_menu(item, extra=[remove]))
    _end_directory()


def mdblist_remove_watchlist(media_type, imdb, tmdb):
    from resources.lib.modules import mdblist
    ok = mdblist.remove_from_watchlist(media_type, imdb=imdb or None, tmdb=tmdb or None)
    control.infoDialog('Removed from watchlist' if ok else 'Could not remove from watchlist')
    xbmc.executebuiltin('Container.Refresh')


def mdblist_remove_list_item(list_id, media_type, imdb, tmdb):
    from resources.lib.modules import mdblist
    ok = mdblist.remove_from_list(list_id, media_type, imdb=imdb or None, tmdb=tmdb or None)
    control.infoDialog('Removed from list' if ok else 'Could not remove from list')
    xbmc.executebuiltin('Container.Refresh')


def mdblist_unlike(list_id):
    from resources.lib.modules import mdblist
    ok = mdblist.unlike_list(list_id)
    control.infoDialog('Unliked' if ok else 'Could not unlike this list')
    xbmc.executebuiltin('Container.Refresh')


def mdblist_mark_watched(media_type, imdb, tmdb, season='', episode=''):
    from resources.lib.modules import mdblist
    ok = mdblist.mark_watched(media_type, imdb=imdb or None, tmdb=tmdb or None,
                               season=season or None, episode_number=episode or None)
    # MDBList's /upnext is server-cached ~15 min (verified live) -- the watched
    # write above applies instantly, but /upnext can still show the old
    # next_episode for a while after. Guess the advance locally (same episode+1)
    # and prefer that guess over a still-stale /upnext until the API catches up
    # (get_upnext() drops the guess once it does) -- avoids the user having to
    # wait out someone else's cache TTL to see this work.
    if ok and media_type == 'episode' and tmdb and season and episode:
        mdblist.set_upnext_override(tmdb, int(season), int(episode) + 1)
    control.infoDialog('Marked watched' if ok else 'Could not mark watched')
    xbmc.executebuiltin('Container.Refresh')


def mdblist_remove_watched(media_type, imdb, tmdb, season='', episode=''):
    from resources.lib.modules import mdblist
    ok = mdblist.remove_watched(media_type, imdb=imdb or None, tmdb=tmdb or None,
                                 season=season or None, episode_number=episode or None)
    control.infoDialog('Removed from watched' if ok else 'Could not remove from watched')
    xbmc.executebuiltin('Container.Refresh')


def mdblist_rate(media_type, imdb, tmdb, season='', episode=''):
    from resources.lib.modules import mdblist
    choice = control.selectDialog([str(n) for n in range(10, 0, -1)], heading='Rate 1-10')
    if choice < 0:
        return
    rating = 10 - choice
    ok = mdblist.rate(media_type, rating, imdb=imdb or None, tmdb=tmdb or None,
                       season=season or None, episode_number=episode or None)
    control.infoDialog('Rated {0}/10'.format(rating) if ok else 'Could not rate')
    xbmc.executebuiltin('Container.Refresh')


def category(section):
    # cached 1h -- a subcategory listing barely changes minute to minute, and this
    # avoids refetching the whole page every time the user goes back and forth
    html, domain = cache.get(client.request_with_fallback, 1, '/category/{0}/'.format(section))
    items = client.parseDOM(html, 'aside', attrs={'id': 'categories-2'})
    links = client.parseDOM(items[0] if items else html, 'a', ret='href')
    labels = client.parseDOM(items[0] if items else html, 'a')

    # Estuary (and most skins) only offer poster/wall view types for content types
    # like "movies"/"episodes" -- "files" is list-view only. TV Shows posts are each
    # one episode release rather than a show->season->episode hierarchy, so
    # "episodes" fits better there than "tvshows".
    list_mode = 'listing_episodes' if section == 'tv-shows' else 'listing_movies'
    section_icon = _icon('tvshows.png' if section == 'tv-shows' else 'movies.png')

    # a plain substring check on "movies" also matches "foreign-movies" (it contains
    # "movies"), leaking Foreign Movies' own subcategories into the Movies menu -- a
    # path-prefix check keeps each section's subcategories to itself
    prefix = '/category/{0}/'.format(section)
    if section == 'movies':
        control.addDir('Recommended Movies', '', 'recommended_movies', iconimage=_icon('movies.png'))
    seen = set()
    for label, href in zip(labels, links):
        path = urlparse(href).path
        if not path.startswith(prefix) or path == prefix:  # skip the section's own self-link
            continue
        if 'RSS' in label or href in seen:
            continue
        seen.add(href)
        control.addDir(metadata.clean_title(label), href, list_mode, iconimage=section_icon)

    if not seen:
        # no sub-categories parsed -- fall back to the section root itself
        control.addDir('All {0}'.format(section.replace('-', ' ').title()),
                        'https://{0}/category/{1}/'.format(domain, section), list_mode,
                        iconimage=section_icon)
    # these are category FOLDER names, not real posts -- always List, no matter what
    # the user picked for the (unrelated) download-links listing inside a post, which
    # shares this same 'files' content type/view-memory key otherwise
    _end_directory(apply_saved_view=False)


# the site's own sidebar "Recommended movies" widget -- an id="text-9" text widget of
# bare poster <a><img> pairs, no title text anywhere (alt is empty), so the only title
# source is the post URL's own slug (e.g. "at-work-2026-1080p-amzn-web-dl-h264-phallus")
_RECOMMENDED_WIDGET_ID = 'text-9'


def recommended_movies():
    html, _domain = cache.get(client.request_with_fallback, 1, '/category/movies/')
    widgets = client.parseDOM(html, 'aside', attrs={'id': _RECOMMENDED_WIDGET_ID})
    widget_html = widgets[0] if widgets else ''
    hrefs = client.parseDOM(widget_html, 'a', ret='href')
    thumbs = client.parseDOM(widget_html, 'img', ret='src')
    seen = set()
    for href, thumb in zip(hrefs, thumbs):
        if href in seen:
            continue
        seen.add(href)
        slug = urlparse(href).path.rstrip('/').rsplit('/', 1)[-1]
        meta = metadata.parse_title(slug.replace('-', ' '))
        title = ('{0} ({1})'.format(meta['title'].title(), meta['year']) if meta['year']
                  else meta['title'].title())
        control.addDir(title, href, 'detail', iconimage=thumb,
                        context_menu=_view_context_menu('movies'))
    _end_directory('movies')


def listing(url, page='1', content_type='files'):
    page_url = url if page == '1' else _paginate(url, page)
    # cached 1h -- same reasoning as category(): a listing page rarely gets new posts
    # within an hour, and this makes back-and-forth navigation instant
    html = cache.get(client.request, 1, page_url)

    articles = client.parseDOM(html, 'article')
    for article in articles:
        titles = client.parseDOM(article, 'a', ret='href')
        title_texts = client.parseDOM(article, 'a')
        if not titles or not title_texts:
            continue
        href = titles[0]
        if '/support-us/' in href:  # sitewide sticky post, not real content
            continue
        title = metadata.clean_title(title_texts[0])
        thumbs = client.parseDOM(article, 'img', ret='src')
        thumb = thumbs[1] if len(thumbs) > 1 else (thumbs[0] if thumbs else '')
        summary = client.parseDOM(article, 'div', attrs={'class': 'entry-summary'})
        plot = metadata.format_description(summary[0]) if summary else ''
        control.addDir(title, href, 'detail', iconimage=thumb, description=plot,
                        context_menu=_view_context_menu(content_type))

    if 'next page-numbers' in html:
        _add_next_page(url, page, content_type)

    _end_directory(content_type)


def _paginate(url, page):
    base = url.rstrip('/')
    return '{0}/page/{1}/'.format(base, page)


def _add_next_page(url, page, content_type):
    next_page = str(int(page) + 1)
    mode = 'listing_episodes' if content_type == 'episodes' else 'listing_movies'
    liz = xbmcgui.ListItem('Next Page >>')
    next_icon = _icon('nextpage.png')
    liz.setArt({'icon': next_icon, 'thumb': next_icon})
    u = '{0}?url={1}&mode={2}&name=&iconimage=&description=&page={3}'.format(
        init.sysaddon, quote_plus(url), mode, next_page)
    xbmcplugin.addDirectoryItem(handle=init.syshandle, url=u, listitem=liz, isFolder=True)


def search_menu():
    control.addDir('New Search', '', 'search_new')
    for term in _search_history():
        control.addDir(term, term, 'search_history_item')
    _end_directory()


def search(query, poster=''):
    """Uses the site's own "Light Search" (log.<domain>), which indexes individual
    release rows rather than WordPress's native post-level ?s= search. A post bundles
    many release variants (see detail()), so the native search only ever returns one
    row per matching post -- for a query that names one exact release, that's a single
    result even though 20 differently-named variants exist. The log search surfaces
    each variant by its own title, matching what the site's nav labels "Light Search".

    poster, when given (a search triggered from an MDBList item), carries that
    item's poster through to every result and on into detail() -- the search results
    page itself has no poster art of its own to show instead."""
    _save_search_term(query)
    domain = control.setting('domain.main') or 'rlsbb.to'
    html = client.request('https://log.{0}/'.format(domain), params={'s': query})

    posts = client.parseDOM(html, 'div', attrs={'class': 'post'})
    for post in posts:
        headings = client.parseDOM(post, 'h2')
        if not headings:
            continue
        title_texts = client.parseDOM(headings[0], 'a')
        hrefs = client.parseDOM(headings[0], 'a', ret='href')
        if not title_texts or not hrefs:
            continue
        control.addDir(metadata.clean_title(title_texts[0]), hrefs[0], 'detail', iconimage=poster)
    _end_directory('files')


_COMMENT_BODY_RE = re.compile(r'<div id="commentbody-\d+"[^>]*>(.*?)</div>', re.S)
# unlike the post body, comments don't bold "Release Name:" as its own label -- users
# just paste it as plain text -- so match the text directly instead of requiring a
# <strong> wrapper, up to the next <br> (a comment can list several releases in a row,
# each needing its own split, same idea as the post body's marker split above)
_COMMENT_RELEASE_MARKER_RE = re.compile(r'Release Name:\s*([^<]+?)\s*<br', re.I)
_COMMENT_FILENAME_RE = re.compile(r'([\w.-]+\.(?:mp4|mkv|avi|m4v|mov))', re.I)
_A_TAG_RE = re.compile(r'<a\b[^>]*>.*?</a>', re.S | re.I)
_COMMENT_LINE_SPLIT_RE = re.compile(r'<br\s*/?>', re.I)
# a season-pack comment often lists one episode's title per PLAIN-TEXT line, with its
# link(s) on the following line(s) (season/episode-only text like "S01" or a divider
# line doesn't count -- needs an actual episode number, filename, or quality/codec
# tag to be a real title -- a movie release line like "Foo 2026 1080p WEB-DL HEVC
# x265-GROUP" has none of the first two, so without the quality-tag branch it's
# mistaken for filler and every link under it silently falls back to the post's own
# title, making a genuinely different release invisible next to the post's own listing)
_COMMENT_TITLE_LINE_RE = re.compile(
    r'S\d{1,2}E\d{1,3}\b|[\w.-]+\.(?:mp4|mkv|avi|m4v|mov)\b|'
    r'\b(?:BRRip|BluRay|WEBRip|WEB.?DL|HDTV|DVDRip|720p|1080p|2160p|4K|HEVC|x264|x265)\b',
    re.I)


def _comment_blocks(html, fallback_title):
    """Users repost fresh mirror links in comments (rapidgator/nitroflare re-uploads,
    or embed-host links like doodstream/streamwish/voe) when the post's own links go
    dead over time -- same convention as the old releaseBB addon. A comment names its
    release(s) via one or more "Release Name:" markers when it's a single release with
    several host mirrors. Without a marker, a comment can still take two shapes: several
    DIFFERENT releases with the filename right in each link's own text (e.g. a Matrix
    trilogy comment posted under just the first movie's post), or -- common on season-
    pack posts -- one episode's title as its own plain-text line followed by that
    episode's bare-URL link(s), repeated per episode. Try the link's own text first,
    then fall back to whichever title line most recently preceded it, then the post's
    own title as a last resort."""
    blocks = []
    for m in _COMMENT_BODY_RE.finditer(html):
        comment_html = m.group(1)
        markers = list(_COMMENT_RELEASE_MARKER_RE.finditer(comment_html))
        if markers:
            for i, marker in enumerate(markers):
                release_title = metadata.clean_title(marker.group(1))
                end = markers[i + 1].start() if i + 1 < len(markers) else len(comment_html)
                blocks.append((release_title, comment_html[marker.start():end], True))
            continue

        current_title = None
        for line in _COMMENT_LINE_SPLIT_RE.split(comment_html):
            a_tags = _A_TAG_RE.findall(line)
            if a_tags:
                for a_html in a_tags:
                    file_match = _COMMENT_FILENAME_RE.search(metadata.clean_title(a_html))
                    release_title = (file_match.group(1) if file_match
                                      else current_title or fallback_title)
                    blocks.append((release_title, a_html, True))
                continue
            text = metadata.clean_title(line)
            if _COMMENT_TITLE_LINE_RE.search(text):
                current_title = text
    return blocks


def detail(url, poster=''):
    html = client.request(url)
    titles = client.parseDOM(html, 'h1', attrs={'class': 'entry-title'})
    title = metadata.clean_title(titles[0]) if titles else ''
    # the site's post body wrapper -- was "postContent" in the old (2023-era) markup,
    # the current theme uses "entry-content" instead (verified live, 2026)
    body = client.parseDOM(html, 'div', attrs={'class': 'entry-content'})
    body_html = body[0] if body else html

    meta = metadata.parse_title(title)
    # the played item's own title should read as "Movie (Year)" / "Show S01E02", not
    # whichever scene-release filename happened to be clicked (colorized_release is
    # still built from the release name below, for the browsing list itself)
    if meta['content_type'] == 'episode' and meta.get('season') and meta.get('episode'):
        play_title = '{0} S{1:02d}E{2:02d}'.format(meta['title'], meta['season'], meta['episode'])
    elif meta.get('year'):
        play_title = '{0} ({1})'.format(meta['title'], meta['year'])
    else:
        play_title = meta['title']

    imdb_id = metadata.extract_imdb_id(html)
    if not imdb_id and meta['content_type'] == 'episode':
        looked_up = cache.get(tmdb.lookup_show, 24 * 7, meta['title'], meta['year'])
        if looked_up:
            imdb_id = looked_up.get('imdb')

    plot = metadata.extract_plot(body_html)
    genre = metadata.extract_genre(body_html)

    # each post bundles several release-group/quality variants, and links belong to
    # THAT release, not the post's own h1 title (which is just one arbitrary variant's
    # name) -- but the site uses two different templates for where a release starts:
    # TV posts wrap the whole release (name, links, RAR backup) in one centered <p>
    # with the release name as its own bold text, while movie posts spread it across
    # several plain <p> tags with no shared wrapper, headed by a "Release Name:" label.
    # Splitting the body at each marker's position (regardless of which template) and
    # taking everything up to the next marker handles both uniformly.
    marker_re = re.compile(
        r'<p style="text-align:\s*center;">\s*<strong>(?P<tv>.*?)</strong>'
        r'|<strong>Release Name:</strong>\s*(?P<movie>[^<]+?)\s*<br',
        re.S | re.I)
    markers = list(marker_re.finditer(body_html))
    if not markers:
        blocks = [(title, body_html, False)]
    else:
        blocks = []
        for i, m in enumerate(markers):
            release_title = metadata.clean_title(m.group('tv') or m.group('movie'))
            end = markers[i + 1].start() if i + 1 < len(markers) else len(body_html)
            blocks.append((release_title, body_html[m.start():end], False))

    # users repost mirror/backup links in comments when the post's own links die --
    # same per-link filtering below handles them (rar/torrent/unsupported hosts all
    # fail the direct-hoster or rar checks and get skipped automatically, since
    # comment links are always plain, ungated URLs, never a protected.to gate)
    blocks += _comment_blocks(html, title)

    for release_title, block, is_comment in blocks:
        colorized_release = metadata.colorize_quality(release_title)
        # the site marks season packs right in the release's own info line (e.g.
        # "MKV | AC3 | 6EP [6.4 GB]") -- catching that up front means a gated link's
        # season-pack-ness is known BEFORE the click, so it can be listed as a folder
        # instead of a playable item. That distinction matters to Kodi: an item
        # opened via the strict playback path must call setResolvedUrl or Kodi shows
        # "Playback failed" -- it won't fall back to browsing a directory instead.
        is_season_pack = bool(_EPISODE_COUNT_RE.search(block))

        hrefs = client.parseDOM(block, 'a', ret='href')
        link_texts = client.parseDOM(block, 'a')
        for href, text in zip(hrefs, link_texts):
            if not href:
                continue
            label = metadata.clean_title(text) or 'Download'
            if label.lower() in _NON_DOWNLOAD_LABELS:
                continue

            # links come in two flavors: gated through the bare protected.to captcha
            # wall, or -- for some releases -- a direct rapidgator.net/nitroflare.com/
            # etc link with no gate at all. Subdomains like nfo.protected.to/
            # img.protected.to are separate gates for NFO/subtitle/screenshot files,
            # not video, and must not be treated as either case.
            hostname = urlparse(href).hostname or ''
            if hostname == 'protected.to':
                kind = 'gate'
            elif _is_direct_hoster(href):
                kind = 'direct'
            else:
                continue

            # comment links are pasted freeform (bare URL, or "filename.mp4 - 2.6 GB",
            # or whatever the commenter typed) -- unlike the post body's own clean
            # labeled buttons, so always show the hostname instead of that raw text.
            # _is_direct_hoster() above already validated the host via
            # HostedMediaFile(href) -- exactly what .valid_url() checks (a local
            # pattern match, no network call) -- same as the old releaseBB addon
            # used to decide what to list. A full resolveurl.resolve() here would
            # be redundant AND expensive (needs live captcha/auth for some hosts),
            # dropping good links and re-running that live check on every open
            # since cache.py never stores a falsy result.
            if is_comment:
                label = hostname.split('.')[0].upper() if hostname else 'Download'

            display = '{0} - {1}'.format(metadata.colorize_host(label), colorized_release)
            # direct links expose the real filename, so the extension/part-number regex
            # applies; gated links don't, but a few labels are *always* rar regardless
            # of filename (site-confirmed convention -- see rarpack.is_known_rar_label).
            # rar:// VFS playback works (verified live) but Kodi's automatic
            # external-subtitle scan tries to list the remote host's parent folder
            # afterwards and hangs for minutes on hosts that don't support directory
            # listing (e.g. debrid.it) -- not worth it, so these are skipped entirely
            if kind == 'direct' and rarpack.is_rar_pack(href, label):
                continue
            if kind == 'gate' and rarpack.is_known_rar_label(label):
                continue
            play_url = _play_url(href, kind, _host_hint(label), play_title, meta,
                                  imdb_id, poster, plot, genre)
            if kind == 'gate' and is_season_pack:
                control.addDir(display, play_url, 'season_pack', iconimage=poster,
                                description=plot, is_folder=True,
                                context_menu=_view_context_menu('files'))
            else:
                control.addDir(display, play_url, 'play', iconimage=poster, description=plot,
                                is_playable=True, is_folder=False,
                                context_menu=_view_context_menu('files'))

    _end_directory('files')


def _is_direct_hoster(href):
    try:
        import resolveurl
        return bool(resolveurl.HostedMediaFile(href))
    except Exception:
        return False


def _play_url(href, kind, host_hint, title, meta, imdb_id, poster='', plot='', genre=''):
    parts = [
        'gate={0}'.format(quote_plus(href)),
        'kind={0}'.format(kind),
        'title={0}'.format(quote_plus(title)),
        'content_type={0}'.format(meta['content_type']),
    ]
    if host_hint:
        parts.append('host={0}'.format(host_hint))
    if imdb_id:
        parts.append('imdb={0}'.format(imdb_id))
    if meta.get('season'):
        parts.append('season={0}'.format(meta['season']))
    if meta.get('episode'):
        parts.append('episode={0}'.format(meta['episode']))
    if poster:
        parts.append('poster={0}'.format(quote_plus(poster)))
    if plot:
        parts.append('plot={0}'.format(quote_plus(plot)))
    if genre:
        parts.append('genre={0}'.format(quote_plus(genre)))
    return '&'.join(parts)


_EPISODE_RE = re.compile(r'S(\d{1,2})E(\d{1,3})', re.I)
_EPISODE_COUNT_RE = re.compile(r'\b(\d{1,2})\s*EP\b', re.I)


def _season_pack_listing(urls, p):
    """A season-pack gate resolves (after its captcha chain) straight to one hoster
    link per episode instead of a single file -- no further gate/captcha needed for
    any of them, so this just lists them as a folder of playable episodes."""
    base_title = p.get('title') or 'Season Pack'
    poster, plot, genre = p.get('poster', ''), p.get('plot', ''), p.get('genre', '')
    for u in urls:
        ep_match = _EPISODE_RE.search(u)
        if ep_match:
            season, episode = int(ep_match.group(1)), int(ep_match.group(2))
            label = '{0} S{1:02d}E{2:02d}'.format(base_title, season, episode)
        else:
            season = episode = None
            label = u.rsplit('/', 1)[-1] or base_title
        ep_meta = {'content_type': 'episode', 'season': season, 'episode': episode}
        control.addDir(label, _play_url(u, 'direct', None, label, ep_meta, p.get('imdb'),
                                         poster, plot, genre),
                        'play', iconimage=poster, description=plot,
                        is_playable=True, is_folder=False)
    xbmcplugin.setContent(init.syshandle, 'episodes')
    xbmcplugin.endOfDirectory(init.syshandle)


def season_pack(encoded_params):
    """Entry point for gated links pre-detected as season packs (see is_season_pack
    in detail()) -- listed as a folder instead of a playable item specifically so
    this can safely resolve the gate and then open a directory of episodes; Kodi's
    strict playback path (see play() below) doesn't allow that."""
    from urllib.parse import parse_qsl
    p = dict(parse_qsl(encoded_params))

    href = p.get('gate')
    if not href:
        control.infoDialog('Broken link')
        return

    # re-opening this same season pack (e.g. picking the next episode after one
    # finishes) would otherwise re-run the whole captcha chain from scratch every
    # time -- the resolved links themselves don't go stale quickly, and a 7-20
    # episode season can take a lot longer than a day to get through, so cache
    # these for a month rather than the usual day
    real_url = cache.get(protected_to.resolve, 24 * 30, href, p.get('host'))
    if not real_url:
        return  # protected_to already showed the failure dialog
    urls = real_url if isinstance(real_url, list) else [real_url]
    _season_pack_listing(urls, p)


def play(encoded_params):
    from urllib.parse import parse_qsl
    p = dict(parse_qsl(encoded_params))

    href = p.get('gate')
    if not href:
        control.infoDialog('Broken link')
        return

    if p.get('kind', 'gate') == 'gate':
        # same reasoning as season_pack() -- replaying this link (retry, or picking
        # it again after Back) shouldn't force a fresh captcha chain every time
        real_url = cache.get(protected_to.resolve, 24, href, p.get('host'))
        if not real_url:
            return  # protected_to already showed the failure dialog
        if isinstance(real_url, list):
            # this item was clicked as a normal playable file (not a season pack --
            # those are pre-detected and routed through season_pack() instead, which
            # can safely open a folder). Kodi's strict playback path only accepts a
            # setResolvedUrl call here, not a directory listing, so the best this can
            # do is play the first link and say so, rather than fail outright.
            control.infoDialog('This resolved to {0} links -- playing the first'.format(
                len(real_url)))
            real_url = real_url[0]
        # a gated link's real filename is only known AFTER solving the captcha -- a
        # "regular" (non-"Backup"-labeled) link can still turn out to be a rar pack
        # underneath. Playing a raw rar archive as if it were a video plays audio
        # only (FFmpeg stumbles onto valid audio frames in the raw bytes, video
        # frames just come out as garbage), so bail here instead of attempting it.
        if rarpack.is_rar_pack(real_url):
            control.infoDialog('This link is a RAR archive and cannot be streamed')
            return
    else:
        real_url = href  # direct hoster link, no captcha gate to solve

    stream_url = resolveurl_evaluate(real_url)
    if not stream_url:
        control.infoDialog('Use a debrid service, not ResolveUrl')
        return

    trakt_bridge.set_ids(imdb=p.get('imdb'))
    _set_mdblist_now_playing(p.get('content_type'), p.get('imdb'), p.get('season'), p.get('episode'))

    liz = xbmcgui.ListItem(p.get('title', ''))
    liz.setPath(stream_url)
    liz.setProperty('IsPlayable', 'true')
    if p.get('poster'):
        liz.setArt({'poster': p['poster'], 'thumb': p['poster'], 'icon': p['poster'],
                    'fanart': p['poster']})
    info = liz.getVideoInfoTag()
    info.setTitle(p.get('title', ''))
    if p.get('plot'):
        info.setPlot(p['plot'])
    if p.get('genre'):
        info.setGenres([g.strip() for g in p['genre'].split('|') if g.strip()])
    if p.get('content_type'):
        info.setMediaType(p['content_type'])
    if p.get('imdb'):
        info.setUniqueIDs({'imdb': p['imdb']}, 'imdb')
        info.setIMDBNumber(p['imdb'])
    if p.get('season'):
        info.setSeason(int(p['season']))
    if p.get('episode'):
        info.setEpisode(int(p['episode']))

    xbmcplugin.setResolvedUrl(init.syshandle, True, liz)


def _set_mdblist_now_playing(content_type, imdb, season=None, episode=None):
    """Lets service.py's playback monitor know what's playing (and its imdb id, plus
    season/episode for a TV episode -- mark_watched() needs those to identify the
    specific episode, not just the show) so it can auto-mark it watched on MDBList
    once playback crosses ~90%."""
    if not imdb:
        return
    import json
    info = {'type': content_type, 'imdb': imdb}
    if content_type == 'episode':
        info['season'] = season
        info['episode'] = episode
    xbmcgui.Window(10000).setProperty('plugin.video.rlsbb.now_playing', json.dumps(info))


def _search_db():
    control.makeFile(control.dataPath)
    dbcon = sqlite3.connect(control.searchFile)
    dbcon.execute('CREATE TABLE IF NOT EXISTS terms (term TEXT UNIQUE, added INTEGER)')
    return dbcon


def _search_history():
    try:
        dbcon = _search_db()
        rows = dbcon.execute('SELECT term FROM terms ORDER BY added DESC LIMIT 20').fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []


def _save_search_term(term):
    try:
        dbcon = _search_db()
        dbcon.execute('DELETE FROM terms WHERE term = ?', (term,))
        dbcon.execute('INSERT INTO terms VALUES (?, ?)', (term, int(time.time())))
        dbcon.commit()
    except Exception:
        pass
