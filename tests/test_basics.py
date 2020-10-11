from xlang.xl_ast import GlobalScope


def test_hello(parser):
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
