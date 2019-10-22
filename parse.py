import sys

from lark import Lark

from transformer import ASTTransformer


def main():
    if len(sys.argv) != 2:
        print(f'{sys.argv[0]} <file.asm>')
        sys.exit(1)
    with open(sys.argv[1]) as f:
        source_code = f.read()

    with open('grammar.lark') as f:
        grammar = f.read()

    lark = Lark(grammar, parser='lalr')
    tree = lark.parse(source_code)
    print(tree.pretty())

    transformer = ASTTransformer()
    ast = transformer.transform(tree)
    print(ast)


if __name__ == '__main__':
    main()
