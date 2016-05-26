import pytest


def test_static_files(connection):
    actual = connection.get('/hello/World', cors=False)
    assert actual == 'Hello World!'


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
