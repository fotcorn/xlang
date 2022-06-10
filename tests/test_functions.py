from xlang.exceptions import ContextException, FunctionAlreadyDefinedException
from .conftest import run
import pytest


def test_function_int_return():
    run(
        """
        myfunc(): int {
            return 5;
        }
        main() {
            i: int = myfunc();
            assert(i == 5);
        }
    """
    )


def test_function_struct_return():
    run(
        """
        struct MyStruct {
            a: int,
            b: int,
        }

        myfunc(): MyStruct {
            s: MyStruct;
            s.a = 5;
            s.b = 7;
            return s;
        }
        main() {
            s: MyStruct = myfunc();
            assert(s.a == 5);
            assert(s.b == 7);
        }
    """
    )


def test_function_struct_param_copy():
    run(
        """
        struct MyStruct {
            a: int,
            b: int,
        }

        myfunc(s: MyStruct) {
            assert(s.a == 5);
            assert(s.b == 7);
            s.a = 11;
            s.b = 12;
        }

        main() {
            s: MyStruct;
            s.a = 5;
            s.b = 7;
            myfunc(s);
            assert(s.a == 5);
            assert(s.b == 7);
        }
        """
    )


def test_duplicate_function():
    with pytest.raises(FunctionAlreadyDefinedException):
        run(
            """
            a() {}
            a() {}
            """
        )


def test_reference_func():
    run(
        """
        struct X {
            a: int,
        }
        func_ref(x: *X) {
            x.a = 5;
        }
        func_copy(x: X) {
            x.a = 6;
        }
        main() {
            x: X;
            x.a = 1;
            func_ref(x);
            assert(x.a == 5);
            x.a = 2;
            func_copy(x);
            assert(x.a == 2);
        }
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
