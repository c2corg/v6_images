import os
import pytest
from tests import data_folder


def test_service_is_up(connection):
    actual = connection.get('/ping', cors=False)
    assert actual == 'Pong!'


def upload_image(connection, filename, expected_status=200):
    with open(filename, 'rb') as img_file:
        files = {'file': img_file}
        return connection.post_file(
            '/upload', files, expected_status=expected_status, cors=False)


@pytest.mark.parametrize("filename", [
    'music.tiff'
])
def test_upload_unsupported_image(connection, filename):
    path = os.path.join(data_folder, 'images', filename)
    assert os.path.isfile(path)
    upload_image(connection, path, expected_status=400)


def test_publish_bad_secret(connection):
    connection.post('/publish',
                    data={'secret': 'bad_secret', 'filename': 'test.png'},
                    expected_status=403)


def test_publish_good_secret(connection):
    path = os.path.join(data_folder, 'images', 'violin.jpg')
    body = upload_image(connection, path, expected_status=200)
    filename = body['filename']
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename},
                    expected_status=200)
