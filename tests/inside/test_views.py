import unittest
from unittest.mock import patch
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

    @patch('c2corg_images.views.publish_')
    def test_publish_good_secret(self, publish_mock):
        """Test publish with good secret"""
        self.app.post('/publish',
                      {'secret': 'good_secret',
                       'filename': 'test.png'},
                      status=200)
