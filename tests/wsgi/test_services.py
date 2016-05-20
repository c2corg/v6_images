def test_static_files(connection):
    actual = connection.get('/hello/World', cors=False)
    assert actual == 'Hello World!'


def upload_image(connection, filename):
    with open(filename, 'rb') as img_file:
        files = {'file': img_file}
        return connection.post_file('/upload', files, cors=False)


def activate_image(connection, key):
    return connection.get('/activate/' + key, cors=False)


def test_upload_image(connection):
    import filecmp
    import os
    filename = 'tests/violin.jpg'
    assert os.path.isfile(filename)

    actual = upload_image(connection, filename)
    key = actual['filename']

    created_file = 'incoming/' + key
    created_file_mini = 'incoming/mini_' + key
    assert os.path.isfile(created_file)
    assert os.path.isfile(created_file_mini)

    assert filecmp.cmp(created_file, filename)
    assert os.stat(created_file).st_size == os.stat(filename).st_size
    assert os.stat(created_file_mini).st_size < os.stat(created_file).st_size


def test_activate(connection):
    import os
    filename = 'tests/violin.jpg'
    assert os.path.isfile(filename)

    actual = upload_image(connection, filename)
    key = actual['filename']

    assert os.path.isfile('incoming/' + key)
    assert os.path.isfile('incoming/mini_' + key)

    activate_image(connection, key)
    assert not os.path.isfile('incoming/' + key)
    assert not os.path.isfile('incoming/mini_' + key)
    assert os.path.isfile('active/' + key)
    assert os.path.isfile('active/mini_' + key)
