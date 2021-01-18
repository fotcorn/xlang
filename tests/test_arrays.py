from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.validation_pass import validation_pass


def test_definition(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            array: [int];
        }
        """
    )
    validation_pass(ast)

    assert len(ast.functions) == 1
    assert "main" in ast.functions


def test_access(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        print(value: int) {}
        struct MyStruct {
            a: int,
        }
        main() {
            array: [int];
            struct_array: [MyStruct];
            my_struct: MyStruct;
            print(my_struct.a);
            print(array[0]);
            print(struct_array[0].a);
        }
        """
    )
    validation_pass(ast)
