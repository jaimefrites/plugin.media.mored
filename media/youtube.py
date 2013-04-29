import gdata.service
import gdata.youtube.service

from media.base import addon
from utils import Match

_youtube = gdata.youtube.service.YouTubeService()

def get_hot_links(url):
    url_match = Match(url)

    if (url_match(r'^http(?:s)?://www\.youtube\.com/watch\?.*v=([-_\w]+).*$') or 
        url_match(r'^http(?:s)?://youtu\.be/([-_\w]+)$')):
        id = url_match.group(1)
        urls = ['%smedia/youtube/%s/' % (addon.base_url, id)]
    else:
        raise DoesNotKnowHowToGetUrl
    return urls


def get_thumbnails(url):
    url_match = Match(url)
    if url_match(r'^%smedia/youtube/([-_\w]+)/$' % addon.base_url):
        try:
            video = _youtube.GetYouTubeVideoEntry(video_id=url_match.group(1))
            thumbnail = [tn.url for tn in video.media.thumbnail]
        except gdata.service.RequestError as e:
            raise DoesNotKnowHowToGetUrl
    else:
        raise DoesNotKnowHowToGetUrl
    return thumbnail


class DoesNotKnowHowToGetUrl(Exception):
    pass
