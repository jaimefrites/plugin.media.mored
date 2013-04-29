"""YouTube views."""

from xbmc import executebuiltin  # pylint: disable=F0401
import directory

def show(video_id):
    """Play given YouTube video."""
    executebuiltin('PlayMedia(plugin://plugin.video.youtube/'
                   '?action=play_video&videoid=%s)' % video_id)
    directory.end()
