"""An adapter for Reddit client."""

from sys import modules

from praw import Reddit
from praw.errors import InvalidSubreddit
from requests.exceptions import ConnectionError, HTTPError

# This module delegates calls to the Reddit object.
_client = Reddit(user_agent='xbmc')
_module = modules[__name__]
for attr in dir(_client):
    if attr.startswith('_'):
        continue
    setattr(_module, attr, getattr(_client, attr))


# Praw objects does not handle a connection error exception, so I should.
class _Subreddit(object):
    def __init__(self, subreddit):
        self._subreddit = subreddit

    def __getattr__(self, name):
        try:
            attr = getattr(self._subreddit, name)
            return attr
        except ConnectionError:
            raise IsUnreachable

    def get_hot(self):
        return _SubredditIter(self._subreddit.get_hot())


# Praw objects does not handle a connection error exception, so I should.
class _SubredditIter(object):
    def __init__(self, iter):
        self._iter = iter

    def next(self):
        try:
            subreddit = next(self._iter)
        except ConnectionError:
            raise IsUnreachable
        return subreddit

    def __iter__(self):
        return _SubredditIter(iter(self._iter))


class IsUnreachable(Exception):
    """Reddit is unreachable."""
    pass


def get_subreddit(subreddit_name, *args, **kwargs):
    """If there is not such subreddit raises InvalidSubreddit.
    If Reddit is unreachable ConnectionError is raised.
    """
    try:
        subreddit = _client.get_subreddit(subreddit_name, *args, **kwargs)

        # I need to touch a subreddit object or praw will not say that the
        # subreddit does not exist.
        subreddit.title
    except TypeError:
        raise InvalidSubreddit('A subreddit name can not be an empty string.')
    except HTTPError:
        raise InvalidSubreddit('The subreddit is not found.')
    except ConnectionError:
        raise IsUnreachable
    return _Subreddit(subreddit)
