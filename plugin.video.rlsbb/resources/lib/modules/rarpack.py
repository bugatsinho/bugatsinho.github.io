# -*- coding: utf-8 -*-
import re

_RAR_RE = re.compile(r'\.(r\d{2,3}|part\d+\.rar)(\W|$)', re.I)
_RAR_WORD_RE = re.compile(r'\brar\b', re.I)


def is_rar_pack(url_or_filename, description=''):
    text = '{0} {1}'.format(url_or_filename or '', description or '')
    return bool(_RAR_RE.search(text)) or bool(_RAR_WORD_RE.search(text))


# the site's own convention (verified live for both movies and TV episodes): a link
# labeled "RAPiDGATOR Backup" is always a single-file rar, so it can be tagged before
# ever spending a captcha solve on it
_ALWAYS_RAR_LABELS = {'rapidgator backup'}


def is_known_rar_label(label):
    return (label or '').strip().lower() in _ALWAYS_RAR_LABELS
