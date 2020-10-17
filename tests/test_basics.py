from xlang.xl_ast import GlobalScope
from xlang.parser import Parser


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse('''
        main() {
            a: int = 5;
            print(a);
        }
    ''')

    assert len(ast.functions) == 1
    assert 'main' in ast.functions

    func = ast.functions['main']

    assert len(func.statements) == 2
