from xlang.xl_ast import GlobalScope
from xlang.parser import Parser


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            array: [int];
            array.add(5);
            print(array[0]);
        }
        """
    )

    assert len(ast.functions) == 1
    assert len(ast.structs) == 1
    assert "main" in ast.functions
