import sys
import os

from lark import Lark

from transformer import ASTTransformer


def main():
    if len(sys.argv) != 2:
        print(f'{sys.argv[0]} <file.xl>')
        sys.exit(1)
    if not sys.argv[1].endswith('.xl'):
        print('Input file must end with .xl')
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

    code = ast.generate_code()

    with open('stdlib/io.ll') as f:
        stdlib = f.read()

    code = stdlib + '\n\n' + code

    output_file = sys.argv[1][:-2] + 'll'
    with open(output_file, 'w') as f:
        f.write(code)

    executable = sys.argv[1][:-2] + 'elf'
    os.system(f'clang-8 {output_file} stdlib/io.c -o {executable}')


if __name__ == '__main__':
    main()
