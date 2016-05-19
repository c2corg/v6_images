"""
A simple check the service is running.
"""


def test_static_files(connection):
    actual = connection.get('/', cors=False)
    assert actual == 'Hello, World!\n'
