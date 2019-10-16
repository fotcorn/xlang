import parser
from lark import Lark


def main():
    grammar = '''
    ?start: translation_unit

    translation_unit: (enum_def | struct_def | function_def)*

    function_params: (IDENTIFIER":" type ",")* IDENTIFIER":" type
    function_def: IDENTIFIER "(" function_params? ")" (":" IDENTIFIER)? code_block

    enum_entry: IDENTIFIER","
    enum_def: "enum" IDENTIFIER "{" enum_entry+ "}"

    struct_entry: IDENTIFIER":" type ","
    struct_def: "struct" IDENTIFIER "{" struct_entry+ "}"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
    INTEGER: /[1-9][0-9]*/
    array_access: "[" compare_expr "]"
    var_access: IDENTIFIER array_access? ("." IDENTIFIER array_access?)*

    code_block: "{" statement* "}"

    statement: loop | if | (function_call ";") | variable_dec | variable_def | variable_assign | control ";"
    loop: "loop" code_block
    if: "if" code_block

    variable_dec: IDENTIFIER ":" type ";"
    variable_def: IDENTIFIER ":" type "=" compare_expr ";"
    variable_assign: var_access "=" compare_expr ";"
    !control: ("break" | "continue" | "return" compare_expr?)

    function_call: IDENTIFIER "(" (compare_expr? | compare_expr ("," compare_expr)*) ")"
    primary_expression: var_access | function_call | INTEGER

    !?mul_div_expr: primary_expression | (mul_div_expr "*" primary_expression) | (mul_div_expr "/" primary_expression)
    !?add_sub_expr: mul_div_expr | (add_sub_expr "+" mul_div_expr) | (add_sub_expr "-" mul_div_expr)
    !?compare_expr: add_sub_expr | (compare_expr compare_operator add_sub_expr)

    !compare_operator: "==" | "!=" | ">=" | ">" | "<" "<="

    type: IDENTIFIER

    %import common.WS
    %ignore WS
    '''

    with open('tests/function_call.xl') as f:
        code = f.read()

    lark = Lark(grammar, parser='lalr')
    tree = lark.parse(code)
    print(tree.pretty())
    print()


if __name__ == '__main__':
    main()
