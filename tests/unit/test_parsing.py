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


def test_unary_minus_parsing():
    parse(
        """
        func main() {
            var a: i32 = -5;
            var b: i32 = -a;
            var c: i32 = -(a + b);
            var d: i32 = -a + b;
            var e: i32 = -1;
        }
        """
    )


def test_unary_minus_operator_precedence():
    # Should be parsed as (-a) * b, not -(a * b)
    # The transformer/interpreter will determine the actual type and value.
    # Here we only care that it parses without error.
    parse(
        """
        func main() {
            var a: i32 = 1;
            var b: i32 = 2;
            var c: i32 = -a * b;
            var d: i32 = -(a * b);
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
