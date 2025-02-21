import pytest

from utils import ImportPathResolver


@pytest.fixture(scope="function")
def import_path_resolver():
    """
    Provides a fresh ImportPathResolver instance for each test.
    """
    return ImportPathResolver()