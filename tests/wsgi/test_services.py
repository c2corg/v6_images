def test_static_files(connection):
    actual = connection.get('/hello/World', cors=False)
    assert actual == 'Hello World!'


def upload_image(connection, filename):
    with open(filename, 'rb') as img_file:
        files = {'file': img_file}
        return connection.post_file('/upload', files, cors=False)


def test_upload_file(connection):
    import filecmp
    import os
    filename = 'tests/violin.jpg'
    assert os.path.isfile(filename)

    actual = upload_image(connection, filename)
    created_file = 'incoming/' + actual['filename']

    assert os.path.isfile(created_file)
    assert filecmp.cmp(created_file, filename)
