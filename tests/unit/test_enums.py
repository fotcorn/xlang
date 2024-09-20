import pytest
from .conftest import validate
from xlang.exceptions import EnumAlreadyDefinedException, ContextException


def test_create_enum_success():
    validate(
        """
        enum Color {
            Red,
            Green,
            Blue,
        }
        """
    )


def test_redefine_enum():
    with pytest.raises(EnumAlreadyDefinedException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Blue,
            }
            enum Color {
                Cyan,
                Magenta,
                Yellow,
            }
            """
        )


def test_duplicate_enum_entry():
    with pytest.raises(ContextException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Red, // Duplicate entry
            }
            """
        )


def test_enum_access():
    validate(
        """
        enum Color {
            Red,
            Green,
            Blue,
        }
        func main() {
            var c: Color = Color.Green;
        }
        """
    )


def test_enum_access_undefined():
    with pytest.raises(ContextException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Blue,
            }
            func main() {
                var c: Color = Color.Yellow;
            }
            """
        )
