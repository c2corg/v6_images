"""
Fixtures for WSGI tests
"""
import logging
import pytest

from tests import wait_wsgi, WsgiConnection

LOG = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def wsgi_composition(composition):
    """
    Fixture that provides a composition with a running WSGI container
    """
    wait_wsgi()
    return composition


@pytest.fixture
def connection(wsgi_composition):
    """
    Fixture that returns a connection to a running batch container.
    """
    return WsgiConnection(wsgi_composition)
