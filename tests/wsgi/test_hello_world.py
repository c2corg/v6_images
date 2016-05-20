"""
A simple check the service is running.
"""


def test_static_files(connection):
    actual = connection.get('/hello/World', cors=False)
    assert actual == 'Hello World!'


def test_upload_file(connection):
    import filecmp
    with open('tests/violin.jpg', 'rb') as img_file:
        files = {'file': img_file}
        actual = connection.post_file('/upload', files, cors=False)
        assert filecmp.cmp('incoming/' + actual['filename'], 'tests/violin.jpg')
