from xlang.xl_ast import GlobalScope
from xlang.parser import Parser


def test_struct(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct Test {
            a: [int],
            b: int,
            c: int,
        }

        main() {
            test: Test;
            test.a[0].c.d[test() + 5] = 5;
            test.b = 3 * 5;
            test.c = test.a + test.b;
        }
        """
    )

    assert len(ast.functions) == 1
    assert len(ast.structs) == 1
    assert "main" in ast.functions
