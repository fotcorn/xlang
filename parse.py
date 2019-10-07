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

    code_block: "{" statement* "}"

    statement: loop | if // | variable_def | variable_assign | function_call
    loop: "loop" code_block
    if: "if" code_block

    type: IDENTIFIER
    
    
    
    %import common.WS
    %ignore WS
    '''

    code = '''
    main() {
        loop {
        }
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
