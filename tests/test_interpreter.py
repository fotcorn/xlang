from xlang.exceptions import InterpreterAssertionError
from .conftest import run

import pytest


def test_hello():
    run(
        """
        struct A {
            a: int,
            b: int,
        }
        test() {
            prints("Hello from function");
        }
        add(a: int, b: int): int {
            return a + b;
        }
        main() {
            printi(5);
            printi(5 + 1024);
            a: int = 5;
            b: int;
            c: A;
            printi(a);
            printi(a + 3);
            printi(7 + a);
            str: string = "Hello World!";
            prints(str);
            test();
            prints("Hello from main");

            if (true) {
                prints("true is true");
            }
            if (false) {
                prints("false is false");
            }
            if (a == 5) {
                prints("a is 5!");
            }
            if (a != 4) {
                prints("a is not 4!");
            }
            if (a > 2) {
                prints("a is bigger than 2!");
            }
            printi(add(3, 4));

            i: int = 0;
            loop {
                i = i + 1;
                if (i == 5) {
                    break;
                }
                if (i == 3) {
                    continue;
                }
                printi(i);
            }
        }
    """
    )


def test_array():
    run(
        """
        main() {
            array: [int];
            appendi(array, 42);
            appendi(array, 1337);
            printi(array[0]);
            printi(array[1]);
        }
    """
    )


def test_set_struct_member():
    run(
        """
        struct MyStruct {
            i: int,
            s: string,
        }
        main() {
            s: MyStruct;
            printi(s.i);
        }
    """
    )


def test_assert():
    run(
        """
        main() {
            assert(true);
        }
    """
    )

    with pytest.raises(InterpreterAssertionError):
        run(
            """
            main() {
                assert(false);
            }
        """
        )


def test_parens():
    run(
        """
        main() {
            assert(1 + 2 * 3 == 7);
            assert((1 + 2 * 3) == 7);
            assert(1 + 2 * 3 == (7));
            assert((1 + 2 * 3 == 7));
            assert((1 + 2) * 3 == 9);
            assert(1 + (2 * 3) == 7);
            assert(1 + (2) * 3 == 7);
        }
    """
    )


def test_variable_declare():
    run(
        """
        main() {
            i: int;
            assert(i == 0);
        }
        """
    )


def test_variable_define():
    run(
        """
        main() {
            i: int = 3;
            assert(i == 3);
        }
        """
    )


def test_variable_assign():
    run(
        """
        main() {
            i: int;
            i = 5;
            assert(i == 5);
        }
        """
    )
