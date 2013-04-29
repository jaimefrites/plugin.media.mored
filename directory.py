"""The current plugin directory."""

# pylint: disable=F0401
import xbmc
import xbmcplugin
# pylint: enable=F0401

import addon

def add_item(url, listitem):
    """Return True, when item was added successfully, otherwise False."""
    ret = xbmcplugin.addDirectoryItem(addon.get_handle(), url, listitem)
    return ret


def add_dir(url, listitem):
    """Return True, when item was added successfully, otherwise False."""
    ret = xbmcplugin.addDirectoryItem(addon.get_handle(), url, listitem, True)
    return ret


def end(cache_to_disk=False):
    xbmcplugin.endOfDirectory(addon.get_handle(), cacheToDisc=cache_to_disk)


def refresh():
    xbmc.executebuiltin('Container.Refresh()')
