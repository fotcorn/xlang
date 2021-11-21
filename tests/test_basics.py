from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.validation_pass import validation_pass


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            a: int = 5;
            printi(a);
        }
        """
    )

    validation_pass(ast)

    assert "main" in ast.functions

    func = ast.functions["main"]

    assert len(func.statements) == 2


def test_string(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            prints("Hello World!");
            a: string = "Hello World!";
        }
        """
    )
    validation_pass(ast)


def test_add(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            printi(5 + 3);
        }
        """
    )
    validation_pass(ast)


def test_mul(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            printi(5 * 3);
        }
        """
    )
    validation_pass(ast)


def test_compare(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            printi(5 != 3);
        }
        """
    )
    validation_pass(ast)


def test_return(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        a() {
            return;
        }
        b(): int {
            return 5;
        }
        """
    )
    validation_pass(ast)


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
        e(p1: int, p2: int) {
        }
        f(p1: int, p2: int): int {
        }
        """
    )
    validation_pass(ast)


def test_variables(parser: Parser):
    ast: GlobalScope = parser.parse(
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

    validation_pass(ast)
    assert "main" in ast.functions


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
            printi(i);
        }
        """
    )
    validation_pass(ast)
    print(ast)
