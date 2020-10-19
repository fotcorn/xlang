from xlang.xl_ast import GlobalScope
from xlang.parser import Parser


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            a: int = 5;
            print(a);
        }
        """
    )

    assert len(ast.functions) == 1
    assert "main" in ast.functions

    func = ast.functions["main"]

    assert len(func.statements) == 2


def test_add(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            print(5 + 3);
        }
        """
    )


def test_mul(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            print(5 * 3);
        }
        """
    )


def test_compare(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            print(5 != 3);
        }
        """
    )
