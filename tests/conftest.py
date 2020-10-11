import pytest
from xlang.parser import Parser


@pytest.fixture
def parser():
    return Parser()
