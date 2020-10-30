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

def test_return(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        a() {
            return;
        }
        b() {
            return 5;
        }
        """
    )

def test_function(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        a() {
        }
        b(): int {
        }
        c(p1: int) {
        }
        d(p1: int): int {
        }
        c(p1: int, p2: int) {
        }
        d(p1: int, p2: int): int {
        }
        """
    )


def test_variables(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            b: int = 5;
            a = 1 + 2;
            b = a + b;
            a = 1 * 2;
            b = a * b;
            a = a * b + c;
            a = a + b * c;
            a = a == b;
            a = a * 2 != 2 + 5;
            a = print(a);
        }
        """
    )
    assert 'main' in ast.functions
    assert len(ast.functions['main'].statements) == 10

def test_loop(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            i: int = 0;
            loop {
                i = i + 1;
                if (i == 5) {
                    break;
                }
            }
            print(i);
        }
        """
    )
