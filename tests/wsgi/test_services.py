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


@pytest.mark.parametrize("filename", [
    'invalid_content.jpg'
])
def test_upload_invalid_image(connection, filename):
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


def test_publish_twice_no_crop(connection):
    path = os.path.join(data_folder, 'images', 'violin.jpg')
    body = upload_image(connection, path, expected_status=200)
    filename = body['filename']
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename},
                    expected_status=200)
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename},
                    expected_status=200)


def test_publish_twice_crop(connection):
    path = os.path.join(data_folder, 'images', 'violin.jpg')
    body = upload_image(connection, path, expected_status=200)
    filename = body['filename']
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename, 'crop': '100x100+10+10'},
                    expected_status=200)
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename, 'crop': '200x200+10+10'},
                    expected_status=200)


def test_publish_twice_crop_no_crop(connection):
    path = os.path.join(data_folder, 'images', 'violin.jpg')
    body = upload_image(connection, path, expected_status=200)
    filename = body['filename']
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename, 'crop': '100x100+10+10'},
                    expected_status=200)
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename},
                    expected_status=200)


def test_publish_twice_no_crop_crop(connection):
    path = os.path.join(data_folder, 'images', 'violin.jpg')
    body = upload_image(connection, path, expected_status=200)
    filename = body['filename']
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename},
                    expected_status=200)
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': filename, 'crop': '100x100+10+10'},
                    expected_status=200)
