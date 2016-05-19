"""
Common fixtures for every tests.
"""
import pytest

from tests import Composition


@pytest.fixture(scope="session")
def composition(request):
    """
    Fixture that start/stop the Docker composition used for all the tests.
    """
    return Composition(request)
