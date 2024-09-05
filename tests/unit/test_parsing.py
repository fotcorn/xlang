import pytest
from .conftest import parse
from xlang.exceptions import UnexpectedCharacterException, UnexpectedTokenException


def test_missing_semicolon():
    with pytest.raises(UnexpectedTokenException):
        parse(
            """
            func main() {
                print(5)
            }
            """
        )


def test_missing_bracket():
    with pytest.raises(UnexpectedTokenException):
        parse(
            """
            func main() {
                print(5);
            """
        )


def test_unclosed_string():
    with pytest.raises(UnexpectedCharacterException):
        parse(
            """
            func main() {
                print("
            """
        )


def test_const_without_value():
    with pytest.raises(UnexpectedTokenException):
        parse(
            """
            func main() {
                const i: i32;
            }
            """
        )
