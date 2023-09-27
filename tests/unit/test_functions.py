from xlang.exceptions import ContextException, FunctionAlreadyDefinedException
from .conftest import run
import pytest


def test_duplicate_function():
    with pytest.raises(FunctionAlreadyDefinedException):
        run(
            """
            a() {}
            a() {}
            """
        )


def test_fail_ref_param():
    with pytest.raises(ContextException):
        run(
            """
            func(a: *int) {
            }
            main() {
                func(5);
            }
        """
        )
