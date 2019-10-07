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

    statement: loop | if | function_call | variable_def | variable_assign
    loop: "loop" code_block
    if: "if" code_block
    
    variable_def: IDENTIFIER ":" type "=" expression ";"
    variable_assign: IDENTIFIER "=" expression ";"
    
    function_call: IDENTIFIER "()"
    func_call_or_var: IDENTIFIER | function_call | INTEGER
    !mul_div_expr: (func_call_or_var "*" func_call_or_var) | (func_call_or_var "/" func_call_or_var)
    !add_sub_expr: (func_call_or_var|mul_div_expr "+" func_call_or_var|mul_div_expr) | (func_call_or_var|mul_div_expr "-" func_call_or_var|mul_div_expr)
    !compare_expr: (func_call_or_var|add_sub_expr "==" func_call_or_var|add_sub_expr) | (func_call_or_var|add_sub_expr "!=" func_call_or_var|add_sub_expr)

    expression: func_call_or_var | mul_div_expr | add_sub_expr | compare_expr

    type: IDENTIFIER
    
    %import common.WS
    %ignore WS
    '''

    code = '''
    main() {
        loop {
        }
        a: i32 = 5;
        a = test() * 5 + 2;
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

    lark = Lark(grammar)
    tree = lark.parse(code)
    print(tree.pretty())
    print()


if __name__ == '__main__':
    main()
