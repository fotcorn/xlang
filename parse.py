import parser
from lark import Lark


def main():
    grammar = '''
    ?start: translation_unit

    translation_unit: (enum_def | struct_def | function_def)*

    function_def: IDENTIFIER "(" ")" code_block

    enum_entry: IDENTIFIER","
    enum_def: "enum" IDENTIFIER "{" enum_entry+ "}"

    struct_entry: IDENTIFIER":" type ","
    struct_def: "struct" IDENTIFIER "{" struct_entry+ "}"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
    INTEGER: /[1-9][0-9]*/

    code_block: "{" statement* "}"

    statement: loop | if | (function_call ";") | variable_def | variable_assign
    loop: "loop" code_block
    if: "if" code_block

    variable_def: IDENTIFIER ":" type "=" compare_expr ";"
    variable_assign: IDENTIFIER "=" compare_expr ";"

    function_call: IDENTIFIER "()"
    primary_expression: IDENTIFIER | function_call | INTEGER

    !?mul_div_expr: primary_expression | (mul_div_expr "*" primary_expression) | (mul_div_expr "/" primary_expression)
    !?add_sub_expr: mul_div_expr | (add_sub_expr "+" mul_div_expr) | (add_sub_expr "-" mul_div_expr)
    !?compare_expr: add_sub_expr | (compare_expr "==" add_sub_expr) | (compare_expr "!=" add_sub_expr)

    type: IDENTIFIER

    %import common.WS
    %ignore WS
    '''

    code = '''
    main() {
        loop {
        }
        test();
        a: i64 = 5 + 5 * 3;
        b: bool = a == 3;
    }

    enum MyEnum {
        RED,
        BLUE,
        GREEN,
    }

    struct MyStruct {
        a: u64,
        b: i16,
    }
    '''

    lark = Lark(grammar, parser='lalr')
    tree = lark.parse(code)
    print(tree.pretty())
    print()


if __name__ == '__main__':
    main()
