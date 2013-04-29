"""A directory with subreddit media."""

from xbmcgui import Dialog, ListItem  # pylint: disable=F0401

import addon
import directory
import media
from reddit import get_subreddit, InvalidSubreddit, IsUnreachable
from translation import ugettext as _

def show(subreddit):
    """Show media of the given subreddit."""
    try:
        userlinks = get_subreddit(subreddit).get_hot()
        media_list = _get_media(userlinks)
        _add_media_to_dir(media_list)
    except InvalidSubreddit:
        pass
    except IsUnreachable:
        Dialog().ok(_('Information'), _('Reddit is unreachable.\n'
                    'Please check your internet connection.'))
    finally:
        directory.end(cache_to_disk=True)


def _add_media_to_dir(media_list):
    """Add given list of direct links to the directory."""
    for media in media_list:
        directory.add_item(
            media['url'], 
            ListItem(media['title'], thumbnailImage=media['thumbnail_url'])
        )


def _get_media(userlinks):
    """Yield list of direct media links for every user's post.
    
    Every direct link is a dict {
        title: title of the post,
        url: direct link to a media,
        thumbnail_url: direct link to a thumbnail
    }.

    """
    for userlink in userlinks:
        try:
            hot_links = media.get_hot_links(userlink.url)
        except media.DoesNotKnowHowToGetUrl:
            continue

        for hot_link in hot_links:
            try:
                thumbnail = media.get_thumbnails(hot_link)[0]
            except media.DoesNotKnowHowToGetUrl:
                thumbnail = addon.icon
            yield {'title': userlink.title, 'url': hot_link, 
                   'thumbnail_url': thumbnail}
