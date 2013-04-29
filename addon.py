"""General addon interface."""

from os import path
import re
import sys
from UserDict import DictMixin

# pylint: disable=F0401
from xbmcaddon import Addon

try:
    import StorageServer
except ImportError:
    import storageserverdummy as StorageServer
# pylint: enable=F0401


class _Settings(DictMixin):  # pylint: disable=W0232
    """The settings of this addon with a dict-like interface."""
    def __getitem__(self, name):
        str_value = _addon.getSetting(name)
        if str_value != '':
            value = eval(str_value)
        else:
            raise KeyError
        return value

    def __setitem__(self, name, value):
        str_value = repr(value)
        _addon.setSetting(name, str_value)


class _UrlMatcher(object):
    """Match current addon url with regular expressions.

    For example,

    url = _UrlMatcher('http://www.yandex.ru/')

    url.match(r'^users/(\w+)/$') will return a match object, if current url 
    is matching with 'http://www.yandex.ru/users/fan/'.

    And if I call url.group(1) after that, it will be 'fan'.

    """
    _url_re = re.compile(r'^(?P<scheme>\w+)://(?P<domain>[.\w]+)/(?P<path>.*)$')

    def __init__(self, base_url):
        self._base_url = base_url
        self._match = None

    def match(self, regexp):
        """Match current addon url with the given regexp.

        Return an instance of re.Match when the url is matching, 
        and None when it is not.

        """
        # Check if the current url is a url.
        cururl = sys.argv[0]
        match = self._url_re.match(cururl)
        if match is None:
            assert False
        
        scheme, domain = match.group('scheme'), match.group('domain')

        # Check if base of the current url equals to expected base_url.
        assert '%s://%s/' % (scheme, domain) == self._base_url

        path = match.group('path')
        self._match = re.match(regexp, path)
        return self._match

    def group(self, name):
        """Return the captured group of the last successful matching."""
        ret = self._match.group(name)
        return ret

    def __str__(self):
        return sys.argv[0]


def get_handle():
    """A handle addon is called with."""
    handle = int(sys.argv[1])
    return handle


def connect_resources():
    """Add the path to the addon libraries to PYTHONPATH."""
    libs = path.join(path.abspath(path.dirname(__file__)), 'resources', 'lib')
    sys.path.insert(0, libs)


_addon = Addon('plugin.media.mored')
icon = _addon.getAddonInfo('icon')
base_url = 'plugin://plugin.media.mored/'
current_url = _UrlMatcher(base_url)
settings = _Settings()
cache = StorageServer.StorageServer("plugin_media_mored", 24)
