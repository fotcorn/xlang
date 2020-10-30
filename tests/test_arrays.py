from xlang.xl_ast import GlobalScope
from xlang.parser import Parser


def test_definition(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            array: [int] = 5;
        }
        """
    )

    assert len(ast.functions) == 1
    assert "main" in ast.functions
