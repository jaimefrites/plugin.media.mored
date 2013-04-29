from mock import Mock, patch

from media.youtube import DoesNotKnowHowToGetUrl, get_hot_links, get_thumbnails
from tests import stubs
from tests.base import TestCase

class GetHotLinksTest(TestCase):
    def setUp(self):
        super(GetHotLinksTest, self).setUp()
        self.apply_patch('media.youtube.addon', stubs.Addon())

    def test_typical(self):
        self.assertEqual(
            get_hot_links('http://www.youtube.com/watch?v=x-x_xxxxxxx'),
            ['plugin://test.the.plugin/media/youtube/x-x_xxxxxxx/']
        )

    def test_https(self):
        self.assertEqual(
            get_hot_links('https://www.youtube.com/watch?v=x-x_xxxxxxx'),
            ['plugin://test.the.plugin/media/youtube/x-x_xxxxxxx/']
        )

    def test_short(self):
        self.assertEqual(
            get_hot_links('http://youtu.be/x-x_xxxxxxx'),
            ['plugin://test.the.plugin/media/youtube/x-x_xxxxxxx/']
        )

    def test_parameters(self):
        self.assertEqual(
            get_hot_links('http://www.youtube.com/watch?foo=bar&'
                          'v=x-x_xxxxxxx&bar=foo'),
            ['plugin://test.the.plugin/media/youtube/x-x_xxxxxxx/']
        )

    def test_non_youtube(self):
        with self.assertRaises(DoesNotKnowHowToGetUrl):
            get_hot_links('http://www.wetube.com/watch?v=x-x_xxxxxxx')


class GetThumbnailsTest(TestCase):
    def setUp(self):
        super(GetThumbnailsTest, self).setUp()
        self.apply_patch('media.youtube.addon', stubs.Addon())
        self.apply_patch('media.youtube._youtube', stubs.YouTube())
        self.apply_patch('media.youtube.gdata.service', stubs.GdataService())

    def test_internal_link(self):
        self.assertItemsEqual(
            get_thumbnails('plugin://test.the.plugin/media/youtube/foo/'),
            ['http://thumbnails.youtube.com/foo.ggg']
        )

    def test_non_youtube(self):
        with self.assertRaises(DoesNotKnowHowToGetUrl):
            get_thumbnails('plugin://kill.the.bill/media/youtube/foo/')

    def test_request_error(self):
        with self.assertRaises(DoesNotKnowHowToGetUrl):
            get_thumbnails('plugin://test.the.plugin/media/youtube/bar/')
