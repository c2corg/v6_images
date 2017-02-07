import unittest
from unittest.mock import patch, call
from webtest import TestApp
from c2corg_images import app


class TestViews(unittest.TestCase):

    def setUp(self):  # NOQA
        self.app = TestApp(app)

    def test_publish_bad_secret(self):
        """Test publish with bad secret"""
        self.app.post('/publish',
                      {'secret': 'bad_secret',
                       'filename': 'test.png'},
                      status=403)

    @patch('c2corg_images.views.incoming_storage.move')
    def test_publish_good_secret(self, publish_mock):
        """Test publish with good secret"""
        self.app.post('/publish',
                      {'secret': 'good_secret',
                       'filename': 'test.png'},
                      status=200)

    @patch('c2corg_images.views.active_storage.delete')
    def test_delete_svg(self, delete_mock):
        """Test delete with one svg filename"""
        self.app.post('/delete',
                      {'secret': 'good_secret',
                       'filenames': ['test.svg']},
                      status=200)
        delete_mock.assert_has_calls([
            call('test.svg'),
            call('testBI.jpg'),
            call('testMI.jpg'),
            call('testSI.jpg')])

    @patch('c2corg_images.views.active_storage.delete')
    def test_delete_multi(self, delete_mock):
        """Test delete with multiple filenames"""
        self.app.post('/delete',
                      {'secret': 'good_secret',
                       'filenames': ['test1.jpg', 'test2.jpg']},
                      status=200)
        delete_mock.assert_has_calls([
            call('test1.jpg'),
            call('test1BI.jpg'),
            call('test1MI.jpg'),
            call('test1SI.jpg'),
            call('test2.jpg'),
            call('test2BI.jpg'),
            call('test2MI.jpg'),
            call('test2SI.jpg')])
