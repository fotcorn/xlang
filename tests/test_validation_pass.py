import pytest
from xlang.exceptions import TypeMismatchException

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

    assert "intfunc" in ast.functions
    assert "main" in ast.functions
    assert "param_func" in ast.functions

    # main
    assert ast.functions["main"].return_type is None

    # int_func
    assert ast.functions["intfunc"].return_type
    assert (
        ast.functions["intfunc"].return_type.variable_type == VariableTypeEnum.PRIMITIVE
    )
    assert ast.functions["intfunc"].return_type.primitive_type == PrimitiveType.I64

    # param_func return type
    assert ast.functions["param_func"].return_type
    assert (
        ast.functions["param_func"].return_type.variable_type == VariableTypeEnum.ARRAY
    )
    assert ast.functions["param_func"].return_type.primitive_type is None
    assert ast.functions["param_func"].return_type.array_type
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


def test_bool(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            b: bool = false;
        }
        """
    )
    validation_pass(ast)


def test_array_access(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        append(array: [int], value: int) {}

        main() {
            b: [int];
            append(b, 5);
            printi(b[0]);
        }
        """
    )
    validation_pass(ast)


def test_struct_access(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct B {
            c: float,
            d: [float],
        }

        struct A {
            a: int,
            b: [int],
            subStruct: B,
            subStructArray: [B],
        }

        main() {
            s: A;
            printi(s.a);
            printi(s.b[0]);

            printf(s.subStruct.c);
            printf(s.subStruct.d[0]);

            printf(s.subStructArray[0].c);
            printf(s.subStructArray[0].d[0]);
        }
        """
    )
    validation_pass(ast)


def test_function_param_access(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main(a: int) {
            printi(a);
        }
        """
    )
    validation_pass(ast)


def test_function_param_override_error(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main(a: int) {
            a: int = 5;
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_variable_type_declaration_mismatch(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main(a: int) {
            a: int = "test";
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_variable_type_declaration_mismatch2(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main(a: int) {
            a: string = 1;
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_variable_type_set_mismatch(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main(a: int) {
            a: int;
            a = "string";
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_variable_type_declaration_mismatch_func(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func(): int {
            return 5;
        }
        main(a: int) {
            a: string = func();
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_variable_type_set_mismatch_func(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        func(): int {
            return 5;
        }
        main(a: int) {
            a: string;
            a = func();
        }
        """
    )
    with pytest.raises(Exception):
        validation_pass(ast)


def test_compare_operator_type_ok(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            a: bool = 1 == 1;
        }
        """
    )
    validation_pass(ast)


def test_compare_operator_type_fail(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            a: int = 1 == 1;
        }
        """
    )
    with pytest.raises(TypeMismatchException):
        validation_pass(ast)


def test_compare_operator_type_fail2(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            s: string = "test";
            a: bool = 1 == s;
        }
        """
    )
    with pytest.raises(TypeMismatchException):
        validation_pass(ast)
