import pytest
from .conftest import parse
from xlang.exceptions import UnexpectedCharacterException, UnexpectedTokenException


def test_missing_semicolon():
    with pytest.raises(UnexpectedTokenException):
        parse(
            """
            main() {
                printi(5)
            }
            """
        )


def test_missing_bracket():
    with pytest.raises(UnexpectedTokenException):
        parse(
            """
            main() {
                printi(5);
            """
        )


def test_unclosed_string():
    with pytest.raises(UnexpectedCharacterException):
        parse(
            """
            main() {
                prints("
            """
        )
