from .conftest import run


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
