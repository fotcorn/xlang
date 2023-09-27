import pytest
from xlang.exceptions import TypeMismatchException
from .conftest import validate


def test_if_working_with_bool_only():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            func main() {
                if (5) {}
            }
            """
        )


def test_elif_working_with_bool_only():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            func main() {
                if (false) {}
                elif (5) {}
            }
            """
        )
