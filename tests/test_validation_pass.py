import pytest
from xlang.xl_ast import VariableTypeEnum, PrimitiveType
from xlang.exceptions import TypeMismatchException
from .conftest import validate


def test_validation_pass():
    ast = validate(
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


def test_non_existing_type():
    with pytest.raises(Exception):
        validate(
            """
            func(): NonExistingType {
                return 5;
            }
            """
        )


def test_inside_loop_continue():
    validate(
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


def test_inside_loop_break():
    validate(
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


def test_inside_loop_continue_fail():
    with pytest.raises(Exception):
        validate(
            """
            func() {
                continue;
            }
            """
        )


def test_inside_loop_break_fail():
    with pytest.raises(Exception):
        validate(
            """
            func() {
                break;
            }
            """
        )


def test_bool():
    validate(
        """
        main() {
            b: bool = false;
        }
        """
    )


def test_array_access():
    validate(
        """
        append(array: [int], value: int) {}

        main() {
            b: [int];
            append(b, 5);
            printi(b[0]);
        }
        """
    )


def test_struct_access():
    validate(
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


def test_function_param_access():
    validate(
        """
        main(a: int) {
            printi(a);
        }
        """
    )


def test_function_param_override_error():
    with pytest.raises(Exception):
        validate(
            """
            main(a: int) {
                a: int = 5;
            }
            """
        )


def test_variable_type_declaration_mismatch():
    with pytest.raises(Exception):
        validate(
            """
            main(a: int) {
                a: int = "test";
            }
            """
        )


def test_variable_type_declaration_mismatch2():
    with pytest.raises(Exception):
        validate(
            """
            main(a: int) {
                a: string = 1;
            }
            """
        )


def test_variable_type_set_mismatch():
    with pytest.raises(Exception):
        validate(
            """
            main(a: int) {
                a: int;
                a = "string";
            }
            """
        )


def test_variable_type_declaration_mismatch_func():
    with pytest.raises(Exception):
        validate(
            """
            func(): int {
                return 5;
            }
            main(a: int) {
                a: string = func();
            }
            """
        )


def test_variable_type_set_mismatch_func():
    with pytest.raises(Exception):
        validate(
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


def test_compare_operator_type_ok():
    validate(
        """
        main() {
            a: bool = 1 == 1;
        }
        """
    )


def test_compare_operator_type_fail():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            main() {
                a: int = 1 == 1;
            }
            """
        )


def test_compare_operator_type_fail2():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            main() {
                s: string = "test";
                a: bool = 1 == s;
            }
            """
        )
