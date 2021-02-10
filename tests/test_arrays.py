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


def test_access(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct MyStruct {
            a: int,
        }
        main() {
            array: [int];
            struct_array: [MyStruct];
            my_struct: MyStruct;
            printi(my_struct.a);
            printi(array[0]);
            printi(struct_array[0].a);
        }
        """
    )
    validation_pass(ast)
