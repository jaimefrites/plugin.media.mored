from mock import call, Mock, patch

from subreddit_details import (_add_media_to_dir, _get_media, InvalidSubreddit, 
                               IsUnreachable, show)
from tests import stubs
from tests.base import TestCase

@patch('subreddit_details.get_subreddit')
@patch('subreddit_details._get_media')
@patch('subreddit_details._add_media_to_dir')
@patch('subreddit_details.directory')
class ShowTest(TestCase):
    def test_valid_subreddit(self, directory, _add_media_to_dir, _get_media,
                             get_subreddit):
        show('valid')
        self.assertEqual(get_subreddit.mock_calls, 
                         call('valid').get_hot().call_list())
        _get_media.assert_called_with(
            get_subreddit.return_value.get_hot.return_value)
        _add_media_to_dir.assert_called_with(_get_media.return_value)
        directory.end.assert_called_with(cache_to_disk=True)

    def test_invalid_subreddit(self, directory, _add_media_to_dir, _get_media,
                               get_subreddit):
        get_subreddit.side_effect = InvalidSubreddit('Test')
        show('invalid')
        self.assertTrue(directory.end.called)

    @patch('subreddit_details.Dialog')
    def test_unrechable_reddit(self, Dialog, directory, _add_media_to_dir, 
                               _get_media, get_subreddit):
        _get_media.side_effect = IsUnreachable
        show('valid')
        self.assertTrue(Dialog.return_value.ok.called)


class AddMediaToDirTest(TestCase):
    def setUp(self):
        super(AddMediaToDirTest, self).setUp()
        self.directory = stubs.Directory()
        self.apply_patch('subreddit_details.directory', self.directory)

    def test_empty_media_list(self):
        _add_media_to_dir([])
        self.assertItemsEqual(self.directory, [])

    def test_one_picture(self):
        _add_media_to_dir([{
            'url': 'http://localhost/picture.png',
            'title': 'A picture for test',
            'thumbnail_url': 'https://localhost/thumbnails/picture.png',
        }])
        self.assertItemsEqual(self.directory, [
            ('A picture for test', 'http://localhost/picture.png'),
        ])

    def test_two_pictures(self):
        _add_media_to_dir([{
            'url': 'http://localhost/picture.png',
            'title': 'A picture for test',
            'thumbnail_url': 'https://localhost/thumbnails/picture.png',
        }] * 2)
        self.assertItemsEqual(self.directory, [
            ('A picture for test', 'http://localhost/picture.png'),
        ] * 2)


class GetMediaTest(TestCase):
    def setUp(self):
        super(GetMediaTest, self).setUp()
        self.media = stubs.Media()
        self.apply_patch('subreddit_details.media', self.media)

    def test_no_userlinks(self):
        media = _get_media([])
        self.assertItemsEqual(media, [])

    def test_one_userlink(self):
        foo_userlink = Mock(title='foo_title', url='foo_userlink')
        media = _get_media([foo_userlink])
        self.assertItemsEqual(media, [{
            'title':         'foo_title',
            'url':           'foo_hotlink',
            'thumbnail_url': 'foo_thumbnail',
        }])

    def test_two_userlinks(self):
        foo_userlink = Mock(title='foo_title', url='foo_userlink')
        media = _get_media([foo_userlink] * 2)
        self.assertItemsEqual(media, [{
            'title':         'foo_title',
            'url':           'foo_hotlink',
            'thumbnail_url': 'foo_thumbnail',
        }] * 2)

    def test_unmanagable_userlink(self):
        media = _get_media([Mock()])
        self.assertItemsEqual(media, [])

    def test_two_hotlinks(self):
        bar_userlink = Mock(title='bar_title', url='bar_userlink')
        media = _get_media([bar_userlink])
        self.assertItemsEqual(media, [{
            'title':         'bar_title',
            'url':           'bar_hotlink1',
            'thumbnail_url': 'bar_thumbnail1',
        }, {
            'title':         'bar_title',
            'url':           'bar_hotlink2',
            'thumbnail_url': 'bar_thumbnail2',
        }])

    @patch('subreddit_details.addon')
    def test_hotlink_without_thumbnail(self, addon):
        spam_userlink = Mock(title='spam_title', url='spam_userlink')
        media = _get_media([spam_userlink])
        self.assertItemsEqual(media, [{
            'title':         'spam_title',
            'url':           'spam_hotlink',
            'thumbnail_url': addon.icon,
        }])
