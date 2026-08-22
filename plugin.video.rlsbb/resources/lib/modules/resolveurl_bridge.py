# -*- coding: utf-8 -*-
def evaluate(host):
    import resolveurl
    try:
        url = None
        if resolveurl.HostedMediaFile(host):
            url = resolveurl.resolve(host)
        return url
    except BaseException:
        return None
