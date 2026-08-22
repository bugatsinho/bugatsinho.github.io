# -*- coding: utf-8 -*-
import html
import re

_MOVIE_RE = re.compile(r'^(.*?)\s+\(?(\d{4})\)?\b')
_TV_RE = re.compile(r'^(.*?)\s+S(\d{1,2})E(\d{1,3})\b', re.I)
_JUNK_RE = re.compile(
    r'\b(BRRip|BluRay|WEBRip|WEB.?DL|HDTV|DVDRip|XviD|x264|x265|H\.?264|H\.?265|HEVC|'
    r'AAC|AC3|DTS|720p|1080p|2160p|4K|EXTENDED|REPACK|PROPER)\b', re.I)


_SCRIPT_STYLE_RE = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.I | re.S)


def clean_title(text):
    text = _SCRIPT_STYLE_RE.sub('', text or '')  # drop embedded <script>/<style> blocks
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)  # &amp;/&#8216;/etc -- the site never sends plain text
    return re.sub(r'\s+', ' ', text).strip()


# a labeled field ("Plot:", "Genre:", "Directed by:", ...) always ends at the next
# bold label or the end of its containing paragraph -- some posts put every field in
# its own <p>, others join them all with <br> inside one <p>, so stopping at
# whichever comes first handles both instead of one regex per template
_FIELD_END_RE = r'(?:<strong>|</p>)'


def extract_plot(html):
    """Post pages label their synopsis '<strong>Plot:</strong> ...' -- pull just that
    sentence instead of the whole entry-summary paragraph soup (awards blurbs, genre,
    embedded rating-widget markup, social-share scripts, etc)."""
    match = re.search(r'<strong>\s*Plot:\s*</strong>\s*(.*?)' + _FIELD_END_RE, html or '', re.S | re.I)
    return clean_title(match.group(1)) if match else ''


def extract_genre(html):
    match = re.search(r'<strong>\s*Genre:\s*</strong>\s*(.*?)' + _FIELD_END_RE, html or '', re.S | re.I)
    return clean_title(match.group(1)) if match else ''


_NUMBER_RE = re.compile(r'\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?%?')


_RELEASE_NAME_RE = re.compile(r'<strong>\s*Release Name:', re.I)


def format_description(raw_html):
    """Cleans up a raw post-summary/excerpt blob (the '<strong>Label:</strong> value'
    fields WordPress crams together for the listing description) into readable,
    line-broken text with numbers/ratings highlighted so they stand out at a glance.
    The excerpt mirrors the WHOLE post body, so everything from the first per-release
    "Release Name:" field onward is technical spam repeated once per quality variant --
    cut it there and keep just the actual synopsis/cast/ratings block."""
    raw_html = raw_html or ''
    cutoff = _RELEASE_NAME_RE.search(raw_html)
    if cutoff:
        raw_html = raw_html[:cutoff.start()]
    text = _SCRIPT_STYLE_RE.sub('', raw_html)
    text = re.sub(r'<strong>', '\n[B]', text, flags=re.I)
    text = re.sub(r'</strong>', '[/B]', text, flags=re.I)
    text = re.sub(r'<br\s*/?>|</p>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = _NUMBER_RE.sub(lambda m: '[COLOR yellow]{0}[/COLOR]'.format(m.group(0)), text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    return text.strip()


def parse_title(raw_title):
    """Return {'title', 'year', 'season', 'episode', 'content_type'} parsed from a
    scene release name, e.g. 'The.Matrix.1999...' or 'Show.Name.S01E02...'."""
    title = clean_title(raw_title).replace('.', ' ')

    tv = _TV_RE.match(title)
    if tv:
        return {
            'title': tv.group(1).strip(),
            'year': None,
            'season': int(tv.group(2)),
            'episode': int(tv.group(3)),
            'content_type': 'episode',
        }

    movie = _MOVIE_RE.match(title)
    if movie:
        return {
            'title': movie.group(1).strip(),
            'year': int(movie.group(2)),
            'season': None,
            'episode': None,
            'content_type': 'movie',
        }

    return {
        'title': _JUNK_RE.sub('', title).strip(),
        'year': None,
        'season': None,
        'episode': None,
        'content_type': 'movie',
    }


def extract_imdb_id(html):
    match = re.search(r'imdb\.com/title/(tt\d+)', html or '')
    return match.group(1) if match else None


_QUALITY_COLORS = [
    (re.compile(r'\b(2160p|4K)\b', re.I), 'cyan'),
    (re.compile(r'\b(1080p|1080i)\b', re.I), 'orange'),
    (re.compile(r'\b720p\b', re.I), 'gold'),
    (re.compile(r'\b(540p|480p)\b', re.I), 'coral'),
    (re.compile(r'\b(BluRay|BRRip|WEB[.-]?DL|WEBRip|HDTV|DVDRip)\b', re.I), 'lightskyblue'),
    (re.compile(r'\b(x264|x265|H\.?264|H\.?265|HEVC|XviD)\b', re.I), 'greenyellow'),
    (re.compile(r'\bMKV\b', re.I), 'gold'),
    (re.compile(r'\bAVI\b', re.I), 'pink'),
    (re.compile(r'\bMP4\b', re.I), 'purple'),
]

_HOST_COLORS = {
    'rapidgator': 'lime',
    'rapidgator backup': 'yellow',
    'nitroflare': 'deepskyblue',
}


def colorize_quality(text):
    """Wrap quality/codec/container tokens in a release title with BBCode colors,
    e.g. 'The Matrix 1999 1080p BluRay x264' -> title with 1080p/BluRay/x264 highlighted."""
    for pattern, color in _QUALITY_COLORS:
        text = pattern.sub(
            lambda m, c=color: '[COLOR {0}][B]{1}[/B][/COLOR]'.format(c, m.group(0)), text)
    return text


def colorize_host(label):
    color = _HOST_COLORS.get((label or '').strip().lower())
    if color:
        return '[COLOR {0}][B]{1}[/B][/COLOR]'.format(color, label)
    return label
