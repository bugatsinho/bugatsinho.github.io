# -*- coding: utf-8 -*-
"""TV show title+year -> imdb/tmdb id lookup, used only when a post page has no direct
IMDB link (movies always do; TV show posts don't reliably). Needs a free API key from
themoviedb.org configured in the addon settings."""
import requests

from resources.lib.modules import control

_SEARCH_URL = 'https://api.themoviedb.org/3/search/tv'
_EXTERNAL_IDS_URL = 'https://api.themoviedb.org/3/tv/{0}/external_ids'


def lookup_show(title, year=None):
    api_key = control.setting('tmdb.apikey')
    if not api_key:
        return None

    try:
        params = {'api_key': api_key, 'query': title}
        if year:
            params['first_air_date_year'] = year
        results = requests.get(_SEARCH_URL, params=params, timeout=10).json().get('results')
        if not results:
            return None

        tmdb_id = results[0]['id']
        ext = requests.get(_EXTERNAL_IDS_URL.format(tmdb_id),
                            params={'api_key': api_key}, timeout=10).json()
        return {'tmdb': str(tmdb_id), 'imdb': ext.get('imdb_id') or None}
    except Exception:
        return None
