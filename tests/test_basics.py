from xlang.exceptions import ContextException
from xlang.xl_ast import Function
from .conftest import validate
import pytest


def test_hello():
    ast = validate(
        """
        main() {
            const a: int = 5;
            printi(a);
        }
        """
    )

    assert "main" in ast.functions

    func = ast.functions["main"]

    assert isinstance(func, Function)
    assert len(func.statements) == 2


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


def test_int_float_literal():
    validate(
        """
        main() {
            const i: int = 5;
            const f: float = 5.0;
        }
        """
    )


def test_invalid_int():
    with pytest.raises(ContextException):
        validate(
            """
            main() {
                const i: int = 5.0;
            }
            """
        )


def test_invalid_float():
    with pytest.raises(ContextException):
        validate(
            """
                main() {
                    const i: float = 5;
                }
                """
        )


def test_invalid_float2():
    with pytest.raises(ContextException):
        validate(
            """
            main() {
                printi(5.0);
            }
            """
        )
