import pytest
from xlang.exceptions import ContextException
from .conftest import validate


def test_variable_access_as_statement():
    validate(
        """
        func main() {
            var array: [i32];
            array.append(5);
        }
        """
    )

    with pytest.raises(ContextException):
        validate(
            """
            func main() {
                var x: i32;
                x;
            }
            """
        )

    with pytest.raises(ContextException):
        validate(
            """
            func main() {
                var array: [i32];
                array[0];
            }
            """
        )


def test_nested_variable_access_as_statement():
    validate(
        """
        struct MyStruct {
            x: [i32],
        }
        func main() {
            var s: MyStruct;
            s.x.append(5);
        }
        """
    )

    with pytest.raises(ContextException):
        validate(
            """
            struct MyStruct {
                x: i32,
            }
            func main() {
                var s: MyStruct;
                s.x;
            }
            """
        )
