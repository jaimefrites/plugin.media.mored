"""Module for resolving media links."""

from functools import wraps
import addon

def _register(module):
    _media_list.append(module)

_media_list = []


from media import imgur
_register(imgur)
from media import youtube
_register(youtube)


def _cached(func):
    @wraps(func)
    def wrapper(*args):
        id = str((func.__module__ + '.' + func.__name__,) + args)
        value = addon.cache.get(id)
        if not value:
            value = list(func(*args))
            if value:
                addon.cache.set(id, repr(value))
        else:
            value = eval(value)
        return value
    return wrapper


@_cached
def get_hot_links(url):
    """Return list of direct links to media or raise DoesNotKnowHowToGetUrl."""
    for media in _media_list:
        try:
            links = media.get_hot_links(url)
            break
        except media.DoesNotKnowHowToGetUrl:
            continue
    else:
        raise DoesNotKnowHowToGetUrl
    return links


@_cached
def get_thumbnails(url):
    """Return list of direct links to thumbnails or raise 
    DoesNotKnowHowToGetUrl.
    
    """
    for media in _media_list:
        try:
            links = media.get_thumbnails(url)
            break
        except media.DoesNotKnowHowToGetUrl:
            continue
    else:
        raise DoesNotKnowHowToGetUrl
    return links


class DoesNotKnowHowToGetUrl(Exception):
    pass
