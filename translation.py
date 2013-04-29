"""A translation api for the plugin."""

import gettext
from os import path

import xbmc  # pylint: disable=F0401

_localedir = path.join(path.dirname(__file__), 'resources', 'locale')
_active_lang = None
_translation = None
_domain = 'mored'


def ugettext(message):
    _update_lang()
    trans = _translation.ugettext(message)
    return trans


def _update_lang():
    global _active_lang, _translation

    xbmclang = xbmc.getLanguage()
    if xbmclang != _active_lang:
        _active_lang = xbmclang
        _translation = gettext.translation(_domain, _localedir, [_active_lang], 
                                           fallback=True)
