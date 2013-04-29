from media.imgur import (DoesNotKnowHowToGetUrl, get_hot_links, get_thumbnails,
    _imgur)
from tests import stubs
from tests.base import TestCase

from mock import Mock, patch
import requests

class GetHotLinksTest(TestCase):
    def setUp(self):
        super(GetHotLinksTest, self).setUp()
        self.apply_patch('media.imgur._imgur', stubs.Imgur())

    def test_jpeg(self):
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyz.jpg'),
                         ['http://i.imgur.com/xyzxyz.jpg'])
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyx.jpeg'),
                         ['http://i.imgur.com/xyzxyx.jpeg'])

    def test_png(self):
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyy.png'),
                         ['http://i.imgur.com/xyzxyy.png'])

    def test_gif(self):
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyx.gif'),
                         ['http://i.imgur.com/xyzxyx.gif'])

    def test_image_id(self):
        self.assertEqual(get_hot_links('http://imgur.com/xyzxyz'),
                         ['http://i.imgur.com/xyzxyz.jpg'])

    def test_many_image_ids(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/xyzxyz&xyzxyy'), [
            'http://i.imgur.com/xyzxyz.jpg',
            'http://i.imgur.com/xyzxyy.png',
        ])

    def test_album(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/a/foo'), [
            'http://i.imgur.com/xyzxyy.png',
            'http://i.imgur.com/xyzxyz.jpg',
        ])

    def test_album_with_extra_things(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/a/foo/titledesc'), 
        [
            'http://i.imgur.com/xyzxyy.png',
            'http://i.imgur.com/xyzxyz.jpg',
        ])

    def test_anchor(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/a/foo#0'), [
            'http://i.imgur.com/xyzxyy.png',
            'http://i.imgur.com/xyzxyz.jpg',
        ])

    def test_parameters(self):
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyz.jpg?1'), 
                         ['http://i.imgur.com/xyzxyz.jpg'])
        self.assertEqual(get_hot_links('http://i.imgur.com/xyzxyz.jpg?1?4214'), 
                         ['http://i.imgur.com/xyzxyz.jpg'])

    def test_gallery_album(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/gallery/foo'), [
            'http://i.imgur.com/xyzxyz.jpg',
            'http://i.imgur.com/xyzxyy.png',
        ])

    def test_gallery_image(self):
        self.assertItemsEqual(get_hot_links('http://imgur.com/gallery/xyzxyz'), 
                              ['http://i.imgur.com/xyzxyz.jpg'])

    def test_non_imgur(self):
        with self.assertRaises(DoesNotKnowHowToGetUrl):
            get_hot_links('http://google.com/xyzxyz')

    def test_imgur_is_unreachable(self):
        with patch('media.imgur._imgur.image', 
                   Mock(side_effect=stubs.Imgur.IsUnreachable)):
            self.assertEqual(get_hot_links('http://imgur.com/xyzxyz'), [])


class GetThumbnailsTest(TestCase):
    def test_jpeg(self):
        self.assertItemsEqual(get_thumbnails('http://i.imgur.com/xyzxyz.jpg'),
                              ['http://i.imgur.com/xyzxyzt.jpg'])

    def test_png(self):
        self.assertItemsEqual(get_thumbnails('http://i.imgur.com/xyzxyz.png'),
                              ['http://i.imgur.com/xyzxyzt.png'])

    def test_non_imgur(self):
        with self.assertRaises(DoesNotKnowHowToGetUrl):
            get_thumbnails('http://google.com/xyzxyz.jpg')



@patch('media.imgur.requests')
class ImgurTest(TestCase):
    def setUp(self):
        super(ImgurTest, self).setUp()
        self.imgur = _imgur

    def test_unreachable_network(self, requests_mock):
        requests_mock.ConnectionError = \
        requests_mock.get.side_effect = requests.ConnectionError
        
        with self.assertRaises(self.imgur.IsUnreachable):
            self.imgur.image('hello')

    def test_non_json_response(self, requests):
        requests.get.return_value.json.side_effect = ValueError
        with self.assertRaises(self.imgur.GetsUnexpectedResponse):
            self.imgur.image('hello')

    def test_succeed(self, requests):
        requests.get.return_value.json.return_value = {
            'status': 200, 
            'data': {'link': Mock()},
        }
        self.imgur.image('hello')
        requests.get.assert_called_with('https://api.imgur.com/3/image/hello',
                                        headers=self.imgur._headers)

    def test_bad_request(self, requests):
        requests.get.return_value.json.return_value = {'status': 400}
        with self.assertRaises(self.imgur.DoesNotUnderstandRequest):
            self.imgur.image('hello')

    def test_request_requires_authentication(self, requests):
        requests.get.return_value.json.return_value = {'status': 401}
        with self.assertRaises(self.imgur.RequiresAuthentication):
            self.imgur.image('hello')

    def test_forbidden(self, requests):
        requests.get.return_value.json.return_value = {'status': 403}
        with self.assertRaises(self.imgur.ForbidsAccess):
            self.imgur.image('hello')

    def test_resource_does_not_exist(self, requests):
        requests.get.return_value.json.return_value = {'status': 404}
        with self.assertRaises(self.imgur.DoesNotFindResource):
            self.imgur.image('hello')

    def test_rate_limit(self, requests):
        requests.get.return_value.json.return_value = {'status': 429}
        with self.assertRaises(self.imgur.LimitsRate):
            self.imgur.image('hello')

    def test_imgur_internal_error(self, requests):
        requests.get.return_value.json.return_value = {'status': 500}
        with self.assertRaises(self.imgur.HaveGotInternalError):
            self.imgur.image('hello')
