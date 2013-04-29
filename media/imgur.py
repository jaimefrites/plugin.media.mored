import parsley
import requests

from utils import Match

class _Imgur(object):
    def __init__(self, client_id):
        self._headers = {'Authorization': 'Client-ID %s' % client_id}

    def _get(self, url):
        try:
            resp = requests.get(url, headers=self._headers)
        except requests.ConnectionError:
            raise self.IsUnreachable

        try:
            ret = resp.json()
        except ValueError:
            # Imgur returned response in non-JSON
            raise self.GetsUnexpectedResponse

        status = ret['status']
        if status == 200:
            pass
        elif status == 400:
            raise self.DoesNotUnderstandRequest
        elif status == 401:
            raise self.RequiresAuthentication
        elif status == 403:
            raise self.ForbidsAccess
        elif status == 404:
            raise self.DoesNotFindResource
        elif status == 429:
            raise self.LimitsRate
        elif status == 500:
            raise self.HaveGotInternalError
        else:
            assert False, 'Imgur returned unexpected status: %d' % status

        return ret


    def album_images(self, id):
        resp = self._get('https://api.imgur.com/3/album/%s/images' % id)
        images = resp['data']
        return [image['link'] for image in images]

    def image(self, id):
        resp = self._get('https://api.imgur.com/3/image/%s' % id)
        image = resp['data']
        return image['link']

    def gallery_image(self, id):
        resp = self._get('https://api.imgur.com/3/gallery/image/%s' % id)
        image = resp['data']
        return image['link']

    def gallery_album(self, id):
        resp = self._get('https://api.imgur.com/3/gallery/album/%s' % id)
        images = resp['data']['images']
        if not images:
            raise self.DoesNotFindAlbum(id)
        return [image['link'] for image in images]

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


def get_hot_links(url):
    normal_url = _norm_url(url)
    url_match = Match(normal_url)

    try:
        if url_match(r'^(http://i\.imgur\.com/[.\w]+)$'):
            urls = [url_match.group(1)]

        elif (url_match(r'^http://imgur\.com/a/(\w+)$') or
              url_match(r'^http://imgur\.com/a/(\w+)/.+$')):
            urls = _imgur.album_images(url_match.group(1))

        elif url_match(r'^http://imgur\.com/gallery/(\w+)$'):
            id = url_match.group(1)
            try:
                urls = _imgur.gallery_album(id)
            except _imgur.DoesNotFindAlbum:
                urls = [_imgur.gallery_image(id)]

        elif _image_link.match(normal_url):
            urls = map(_imgur.image, _image_link.id_list)

        else:
            raise DoesNotKnowHowToGetUrl
    except (_imgur.GetsUnexpectedResponse, _imgur.IsUnreachable, 
            _imgur.DoesNotUnderstandRequest, _imgur.RequiresAuthentication, 
            _imgur.ForbidsAccess, _imgur.DoesNotFindResource, 
            _imgur.LimitsRate, _imgur.HaveGotInternalError):
        urls = []
    return urls


def get_thumbnails(url):
    url_match = Match(url)
    if url_match(r'^http://i\.imgur\.com/(?P<id>\w+)\.(?P<ext>\w+)$'):
        thumbnail = 'http://i.imgur.com/%(id)st.%(ext)s' % {
            'id': url_match.group('id'), 'ext': url_match.group('ext')}
    else:
        raise DoesNotKnowHowToGetUrl
    return [thumbnail]


def _norm_url(url):
    # remove last # anchor
    url = url.rsplit('#', 1)[0]
    # remove params
    url = url.split('?', 1)[0]
    return url


class _ImageLink(object):
    _grammar = staticmethod(parsley.makeGrammar("""
    image_link = 'http://imgur.com/' id:head_id ('&' id)*:tail_ids extra_path? -> [head_id] + tail_ids
    id = <(letter | digit)+>
    extra_path = '/' anything+
    """, {}))

    def __init__(self):
        self.id_list = None

    def match(self, url):
        try:
            self.id_list = self._grammar(url).image_link()
            ret = True
        except parsley.ParseError:
            ret = False
        return ret


class DoesNotKnowHowToGetUrl(Exception):
    pass


_imgur = _Imgur(client_id='164d659fbcdfd67')
_image_link = _ImageLink()
