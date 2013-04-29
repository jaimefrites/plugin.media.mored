"""A directory with the list of subreddits."""

# pylint: disable=F0401
from xbmc import Keyboard
from xbmcgui import Dialog, ListItem
# pylint: enable=F0401

import addon
from addon import settings
import directory
from reddit import get_subreddit, InvalidSubreddit, IsUnreachable
from translation import ugettext as _
from utils import KeyboardView

_DEFAULT_SUBREDDITS = {
    'funny': 'funny',
    'funnypics': 'Funny Pics',
    'pics': '/r/Pics',
    'videos': 'Videos',
}

if 'subreddits' not in settings:
    settings['subreddits'] = _DEFAULT_SUBREDDITS


def show():
    """Show user's list of subreddits."""
    subreddits = settings['subreddits']
    _show_subreddits(subreddits)


def _show_subreddits(subreddit_dict):
    """Show given given subreddit_dict.
    
    Keys of dict are subreddit names, values are subreddit titles.

    """
    for subreddit in sorted(subreddit_dict):
        directory.add_dir(
            addon.base_url + 'r/%s/' % subreddit, _subreddit_item(subreddit))

    directory.add_item(
        addon.base_url + 'add_subreddit/', ListItem(_('Add subreddit')))
    directory.add_item(
        addon.base_url + 'remove_subreddit/', ListItem(_('Remove subreddit')))
    directory.end()


def _subreddit_item(title, subreddit_name=None):
    """Return ListItem for given subreddit name with context menu."""
    listitem = ListItem(title)

    if subreddit_name is None:
        subreddit_name = title
    listitem.addContextMenuItems([
        (_('Remove'), 'RunPlugin(%sremove_subreddit/%s/)' % (
            addon.base_url, subreddit_name
        ))
    ])
    return listitem


class _SubredditKeyboard(Keyboard):
    """Common keyboard dialog."""
    def __init__(self):  # pylint: disable=E1002
        super(Keyboard, self).__init__()
        self.setHeading(_('Enter a subreddit name'))  # pylint: disable=E1101


class _AddView(KeyboardView):
    """The view provides a keyboard to enter a subreddit and adds the subreddit 
    to the user's preference list.
    
    """
    keyboard_class = _SubredditKeyboard

    def process(self, subreddit):
        try:
            _add_subreddit(subreddit)
            directory.refresh()
        except InvalidSubreddit:
            Dialog().ok(_('Error'), _('There is not such subreddit.'))
            raise self.AskAgain
        except IsUnreachable:
            Dialog().ok(_('Information'), _('Reddit is unreachable.\n'
                        'Please check your internet connection.'))


def _add_subreddit(name):
    """Add given subreddit to the user's preference list.

    Raise InvalidSubreddit when it does not exist on Reddit.
    Raise IsUnreachable when Reddit is unreachable.

    """
    try:
        subreddit = get_subreddit(name)
    except InvalidSubreddit:
        raise
    except IsUnreachable:
        raise
    subreddits = settings['subreddits']
    subreddits[name] = subreddit.title
    settings['subreddits'] = subreddits


add_subreddit = _AddView()


class _RemoveView(KeyboardView):
    """The view provides a keyboard to enter a subreddit and removes the 
    subreddit from the user's preference list.
    
    """
    keyboard_class = _SubredditKeyboard

    def process(self, subreddit):
        try:
            _remove_subreddit(subreddit)
            directory.refresh()
        except InvalidSubreddit:
            dlg = Dialog()
            dlg.ok(_('Error'), _('There is not such subreddit.'))
            raise self.AskAgain


def _remove_subreddit(name):
    """Remove given subreddit from the user's preference list.

    Raise InvalidSubreddit when it is not found in the user's prefence list.

    """
    subreddits = settings['subreddits']
    try:
        del subreddits[name]
    except KeyError:
        raise InvalidSubreddit('The subreddit is not found.')
    settings['subreddits'] = subreddits


def remove_subreddit(subreddit=None):
    """The View removes given subreddit from user's preference list when the
    name is given.  In other case it provides a keyboard to enter a name.
    
    """
    if subreddit is not None:
        try:
            _remove_subreddit(subreddit)
            directory.refresh()
        except InvalidSubreddit:
            pass
    else:
        _RemoveView()()
