from mock import Mock

class Directory(object):
    def __init__(self):
        self._mem = []

    def add_dir(self, url, li):
        self._mem.append((str(li) + '/', url))

    def add_item(self, url, li):
        self._mem.append((str(li), url))

    def __repr__(self):
        ret = repr(self._mem)
        return ret

    def __eq__(self, that):
        return self._mem == that

    def __iter__(self):
        return iter(self._mem)

    end = Mock()
    sort_by = Mock()


class Media(object):
    def get_hot_links(self, url):
        try:
            ret = {
                'foo_userlink':  ['foo_hotlink'],
                'bar_userlink':  ['bar_hotlink1', 'bar_hotlink2'],
                'spam_userlink': ['spam_hotlink'],
            }[url]
        except KeyError:
            raise self.DoesNotKnowHowToGetUrl
        return ret

    def get_thumbnails(self, url):
        try:
            ret = {
                'foo_hotlink': ['foo_thumbnail'],
                'bar_hotlink1': ['bar_thumbnail1'],
                'bar_hotlink2': ['bar_thumbnail2'],
            }[url]
        except KeyError:
            raise self.DoesNotKnowHowToGetUrl
        return ret

    class DoesNotKnowHowToGetUrl(Exception):
        pass


class Imgur(object):
    foo_album = {
        'xyzxyz': 'http://i.imgur.com/xyzxyz.jpg',
        'xyzxyy': 'http://i.imgur.com/xyzxyy.png',
    }

    albums = {
        'foo': foo_album,
    }

    def image(self, id):
        image = self.foo_album[id]
        return image

    def album_images(self, id):
        album = self.albums[id]
        images = album.values()
        return images

    def gallery_image(self, id):
        return self.image(id)

    def gallery_album(self, id):
        try:
            images = self.album_images(id)
        except KeyError:
            raise self.DoesNotFindAlbum
        return images

    class DoesNotFindAlbum(Exception):
        pass

    class GetsUnexpectedResponse(Exception):
        pass

    class IsUnreachable(Exception):
        pass

    class DoesNotUnderstandRequest(Exception):
        pass

    class RequiresAuthentication(Exception):
        pass

    class ForbidsAccess(Exception):
        pass

    class DoesNotFindResource(Exception):
        pass

    class LimitsRate(Exception):
        pass

    class HaveGotInternalError(Exception):
        pass


class Addon(object):
    base_url = 'plugin://test.the.plugin/'


class YouTube(object):
    def GetYouTubeVideoEntry(self, video_id=None):
        if video_id == 'foo':
            ve = Mock()
            ve.media.thumbnail = [
                Mock(url='http://thumbnails.youtube.com/foo.ggg')]
            return ve
        else:
            raise GdataService.RequestError()


class GdataService(object):
    class RequestError(Exception):
        pass
