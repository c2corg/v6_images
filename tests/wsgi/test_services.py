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
