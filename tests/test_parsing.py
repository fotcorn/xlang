import pytest
from xlang.exceptions import UnexpectedCharacterException, UnexpectedTokenException
from xlang.parser import Parser


def test_missing_semicolon(parser: Parser):
    with pytest.raises(UnexpectedTokenException):
        parser.parse(
            """
            main() {
                printi(5)
            }
            """
        )


def test_missing_bracket(parser: Parser):
    with pytest.raises(UnexpectedTokenException):
        parser.parse(
            """
            main() {
                printi(5);
            """
        )


def test_unclosed_string(parser: Parser):
    with pytest.raises(UnexpectedCharacterException):
        parser.parse(
            """
            main() {
                prints("
            """
        )
