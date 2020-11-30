import pytest

from xlang.xl_ast import GlobalScope, VariableTypeEnum, PrimitiveType
from xlang.parser import Parser
from xlang.validation_pass import validation_pass


def test_validation_pass(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct MyStruct {
            a: int,
        }

        intfunc(): int {
            return 5;
        }

        param_func(a: int, b: u16, c: [int], d: MyStruct): [MyStruct] {}

        main() {
            a: int = 5;
            print(a);
        }
        """
    )
    validation_pass(ast)

    assert len(ast.functions) == 3
    assert "intfunc" in ast.functions
    assert "main" in ast.functions
    assert "param_func" in ast.functions

    # main
    assert ast.functions["main"].return_type == None

    # int_func
    assert (
        ast.functions["intfunc"].return_type.variable_type == VariableTypeEnum.PRIMITIVE
    )
    assert ast.functions["intfunc"].return_type.primitive_type == PrimitiveType.I64

    # param_func return type
    assert (
        ast.functions["param_func"].return_type.variable_type == VariableTypeEnum.ARRAY
    )
    assert ast.functions["param_func"].return_type.primitive_type is None
    assert (
        ast.functions["param_func"].return_type.array_type.variable_type
        == VariableTypeEnum.STRUCT
    )
    assert ast.functions["param_func"].return_type.array_type.type_name == "MyStruct"
    assert ast.functions["param_func"].return_type.array_type.primitive_type is None
    assert ast.functions["param_func"].return_type.array_type.array_type is None

    # param_func parameters
    params = ast.functions["param_func"].function_params
    assert params[0].name == "a"
    assert params[1].name == "b"
    assert params[2].name == "c"
    assert params[3].name == "d"


def test_non_existing_type(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func(): NonExistingType {
            return 5;
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)
