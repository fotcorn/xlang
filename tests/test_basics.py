from xlang.xl_ast import Function
from .conftest import validate


def test_hello():
    ast = validate(
        """
        main() {
            a: int = 5;
            printi(a);
        }
        """
    )

    assert "main" in ast.functions

    func = ast.functions["main"]

    assert isinstance(func, Function)
    assert len(func.statements) == 2


def test_string():
    validate(
        """
        main() {
            prints("Hello World!");
            a: string = "Hello World!";
        }
        """
    )


def test_add():
    validate(
        """
        main() {
            printi(5 + 3);
        }
        """
    )


def test_mul():
    validate(
        """
        main() {
            printi(5 * 3);
        }
        """
    )


def test_compare():
    validate(
        """
        main() {
            printb(5 != 3);
        }
        """
    )


def test_return():
    validate(
        """
        a() {
            return;
        }
        b(): int {
            return 5;
        }
        """
    )


def test_function():
    validate(
        """
        a() {
        }
        b(): int {
        }
        c(p1: int) {
        }
        d(p1: int): int {
        }
        e(p1: int, p2: int) {
        }
        f(p1: int, p2: int): int {
        }
        """
    )


def test_variables():
    ast = validate(
        """
        test(): int {
            return 5;
        }
        main() {
            a: int = 1 + 2;
            b: int = 5;
            c: int = a + b;
            b = a + b;
            a = a * b;
            a = a * b + c;
            a = a + b * c;
            a = test();
            a = b + 1;
            a = 1 + b;
        }
        """
    )

    assert "main" in ast.functions


def test_loop():
    validate(
        """
        main() {
            i: int = 0;
            loop {
                i = i + 1;
                if (i == 5) {
                    break;
                }
            }
            printi(i);
        }
        """
    )


def test_parens():
    validate(
        """
        main() {
            printi(1 + 2 * 3);
            printi((1 + 2) * 3);
        }
        """
    )
