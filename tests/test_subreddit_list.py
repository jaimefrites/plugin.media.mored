from __future__ import absolute_import

from mock import Mock, patch

from subreddit_list import (
    _add_subreddit, _AddView, _DEFAULT_SUBREDDITS, InvalidSubreddit,
    IsUnreachable, ListItem, _remove_subreddit, remove_subreddit, _RemoveView, 
    settings, show, _show_subreddits)
from tests import stubs
from tests.base import TestCase


class ShowTest(TestCase):
    @patch('subreddit_list.settings')
    @patch('subreddit_list._show_subreddits')
    def test(self, _show_subreddits, settings):
        settings['subreddits'] = ['hello', 'world']
        show()
        _show_subreddits.assert_called_with(settings['subreddits'])


class ShowSubredditsTest(TestCase):
    def assertDirectoryEquals(self, that_directory):
        self.assertItemsEqual(self.directory, that_directory)
        self.assertTrue(self.directory.end.called)

    def setUp(self):
        super(ShowSubredditsTest, self).setUp()
        self.directory = stubs.Directory()
        self.apply_patch('subreddit_list.directory', self.directory)
        
        addon = self.apply_patch('subreddit_list.addon')
        addon.base_url = '/'

    def test_empty_dict(self):
        _show_subreddits({})
        self.assertDirectoryEquals([
            ('Add subreddit',    '/add_subreddit/'),
            ('Remove subreddit', '/remove_subreddit/'),
        ])

    def test_one_subreddit(self):
        _show_subreddits({'funnypics': 'Funny Pics'})
        self.assertDirectoryEquals([
            ('funnypics/',       '/r/funnypics/'),
            ('Add subreddit',    '/add_subreddit/'),
            ('Remove subreddit', '/remove_subreddit/'),
        ])

    def test_two_subreddits(self):
        _show_subreddits({'funnypics': 'Funny Pics', 'videos': 'Videos'})
        self.assertDirectoryEquals([
            ('funnypics/',       '/r/funnypics/'),
            ('videos/',          '/r/videos/'),
            ('Add subreddit',    '/add_subreddit/'),
            ('Remove subreddit', '/remove_subreddit/'),
        ])


@patch('subreddit_list._add_subreddit')
@patch('subreddit_list.directory')
class AddViewTest(TestCase):
    def setUp(self):
        super(AddViewTest, self).setUp()
        self.add_view = _AddView()

    def test_valid_subreddit(self, directory, _add_subreddit):
        self.add_view.process('valid')
        _add_subreddit.assert_called_with('valid')
        self.assertTrue(directory.refresh.called)

    @patch('subreddit_list.Dialog')
    def test_invalid_subreddit(self, Dialog, directory, _add_subreddit):
        _add_subreddit.side_effect = InvalidSubreddit('Test')
        with self.assertRaises(self.add_view.AskAgain):
            self.add_view.process('invalid')
        self.assertTrue(Dialog().ok.called)

    @patch('subreddit_list.Dialog')
    def test_unreachable_reddit(self, Dialog, directory, _add_subreddit):
        _add_subreddit.side_effect = IsUnreachable
        self.add_view.process('valid')
        self.assertTrue(Dialog().ok.called)


@patch('subreddit_list.get_subreddit')
class AddSubredditTest(TestCase):
    def setUp(self):
        super(AddSubredditTest, self).setUp()
        self.settings = {'subreddits': {
            'old': 'old'
        }}
        self.apply_patch('subreddit_list.settings', self.settings)

    def test_valid_subreddit(self, get_subreddit):
        _add_subreddit('new')
        self.assertIn('new', self.settings['subreddits'])

    def test_invalid_subreddit(self, get_subreddit):
        get_subreddit.side_effect = InvalidSubreddit('Test')
        with self.assertRaises(InvalidSubreddit):
            _add_subreddit('invalid')

    def test_existing_subreddit(self, get_subreddit):
        get_subreddit.return_value.title = 'new'
        _add_subreddit('old')
        self.assertIn('old', self.settings['subreddits'])
        self.assertEqual('new', self.settings['subreddits']['old'])


@patch('subreddit_list._remove_subreddit')
@patch('subreddit_list.directory')
class RemoveViewTest(TestCase):
    def setUp(self):
        super(RemoveViewTest, self).setUp()
        self.remove_view = _RemoveView()

    def test_valid_subreddit(self, directory, _remove_subreddit):
        self.remove_view.process('valid')
        _remove_subreddit.assert_called_with('valid')
        self.assertTrue(directory.refresh.called)

    @patch('subreddit_list.Dialog')
    def test_invalid_subreddit(self, Dialog, directory, _remove_subreddit):
        _remove_subreddit.side_effect = InvalidSubreddit('Test')
        with self.assertRaises(self.remove_view.AskAgain):
            self.remove_view.process('invalid')
        self.assertTrue(Dialog().ok.called)


class ModuleTest(TestCase):
    def test_default_subreddits(self):
        self.assertEqual(settings['subreddits'], _DEFAULT_SUBREDDITS)


class RemoveSubredditPrivateTest(TestCase):
    def setUp(self):
        super(RemoveSubredditPrivateTest, self).setUp()
        self.settings = {'subreddits': {
            'old': 'old',
        }}
        self.apply_patch('subreddit_list.settings', self.settings)

    def test_existing_subreddit(self):
        _remove_subreddit('old')
        self.assertNotIn('old', self.settings['subreddits'])

    def test_non_existing_subreddit(self):
        with self.assertRaises(InvalidSubreddit):
            _remove_subreddit('new')


class RemoveSubreddit(TestCase):
    @patch('subreddit_list._remove_subreddit')
    @patch('subreddit_list.directory')
    def test_valid_subreddit(self, directory, _remove_subreddit):
        remove_subreddit('old')
        _remove_subreddit.assert_called_with('old')
        self.assertTrue(directory.refresh.called)

    @patch('subreddit_list._remove_subreddit')
    @patch('subreddit_list.directory')
    def test_invalid_subreddit(self, directory, _remove_subreddit):
        _remove_subreddit.side_effect = InvalidSubreddit('Test')
        remove_subreddit('new')
        _remove_subreddit.assert_called_with('new')
        self.assertFalse(directory.refresh.called)

    @patch('subreddit_list._RemoveView')
    def test_skipped_subreddit(self, _RemoveView):
        remove_subreddit()
        self.assertTrue(_RemoveView().called)
