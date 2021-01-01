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

        intfunc(a: int): int {
            return 5;
        }

        param_func(a: int, b: u16, c: [int], d: MyStruct): [MyStruct] {}

        main() {
            a: int = 5;
            intfunc(a);
        }
        """
    )

    validation_pass(ast)

    assert len(ast.functions) == 3
    assert "intfunc" in ast.functions
    assert "main" in ast.functions
    assert "param_func" in ast.functions

    # main
    assert ast.functions["main"].return_type is None

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


def test_inside_loop_continue(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func() {
            loop {
                continue;
            }
            loop {
                loop {
                    continue;
                }
                continue;
            }
        }
        """
    )
    validation_pass(ast)


def test_inside_loop_break(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func() {
            loop {
                break;
            }
             loop {
                loop {
                    break;
                }
                break;
            }
        }
        """
    )
    validation_pass(ast)


def test_inside_loop_continue_fail(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func() {
            continue;
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_inside_loop_break_fail(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func() {
            break;
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)
