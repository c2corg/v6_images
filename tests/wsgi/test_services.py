import pytest


def test_service_is_up(connection):
    actual = connection.get('/ping', cors=False)
    assert actual == 'Pong!'


def upload_image(connection, filename, expected_status=200):
    with open(filename, 'rb') as img_file:
        files = {'file': img_file}
        return connection.post_file(
            '/upload', files, expected_status=expected_status, cors=False)


@pytest.mark.parametrize("filename", [
    'tests/music.tiff'
])
def test_upload_unsupported_image(connection, filename):
    import os
    assert os.path.isfile(filename)

    upload_image(connection, filename, expected_status=400)


def test_publish_bad_secret(connection):
    connection.post('/publish',
                    data={'secret': 'bad_secret', 'filename': 'test.png'},
                    expected_status=403)


def test_publish_good_secret(connection):
    connection.post('/publish',
                    data={'secret': 'good_secret', 'filename': 'test.png'},
                    expected_status=200)
