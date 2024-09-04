import pytest
from xlang.xl_ast import VariableTypeEnum, PrimitiveType
from xlang.exceptions import TypeMismatchException
from .conftest import validate


def test_validation_pass():
    ast = validate(
        """
        struct MyStruct {
            a: i32,
        }

        func intfunc(a: i32): i32 {
            return 5;
        }

        func param_func(a: i32, b: u16, c: [i32], d: MyStruct): [MyStruct] {}

        func main() {
            const a: i32 = 5;
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
    assert ast.functions["intfunc"].return_type.primitive_type == PrimitiveType.I32

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
            func func(): NonExistingType {
                return 5;
            }
            """
        )


def test_inside_loop_continue():
    validate(
        """
        func main() {
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
        func main() {
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
            func main() {
                continue;
            }
            """
        )


def test_inside_loop_break_fail():
    with pytest.raises(Exception):
        validate(
            """
            func main() {
                break;
            }
            """
        )


def test_bool():
    validate(
        """
        func main() {
            const b: bool = false;
        }
        """
    )


def test_array_access():
    validate(
        """
        func append(array: [i32], value: i32) {}

        func main() {
            var b: [i32];
            append(b, 5);
            print(b[0]);
        }
        """
    )


def test_struct_access():
    validate(
        """
        struct B {
            c: f32,
            d: [f32],
        }

        struct A {
            a: i32,
            b: [i32],
            subStruct: B,
            subStructArray: [B],
        }

        func main() {
            var s: A;
            print(s.a);
            print(s.b[0]);

            print(s.subStruct.c);
            print(s.subStruct.d[0]);

            print(s.subStructArray[0].c);
            print(s.subStructArray[0].d[0]);
        }
        """
    )


def test_function_param_access():
    validate(
        """
        func main(a: i32) {
            print(a);
        }
        """
    )


def test_function_param_override_error():
    with pytest.raises(Exception):
        validate(
            """
            func main(a: i32) {
                const a: i32 = 5;
            }
            """
        )


def test_variable_type_declaration_mismatch():
    with pytest.raises(Exception):
        validate(
            """
            func main(a: i32) {
                const a: i32 = "test";
            }
            """
        )


def test_variable_type_declaration_mismatch2():
    with pytest.raises(Exception):
        validate(
            """
            func main(a: i32) {
                const a: string = 1;
            }
            """
        )


def test_variable_type_set_mismatch():
    with pytest.raises(Exception):
        validate(
            """
            func main(a: i32) {
                var a: i32;
                a = "string";
            }
            """
        )


def test_variable_type_declaration_mismatch_func():
    with pytest.raises(Exception):
        validate(
            """
            func func(): i32 {
                return 5;
            }
            func main(a: i32) {
                const a: string = func();
            }
            """
        )


def test_variable_type_set_mismatch_func():
    with pytest.raises(Exception):
        validate(
            """
            func func(): i32 {
                return 5;
            }
            func main(a: i32) {
                var a: string;
                a = func();
            }
            """
        )


def test_compare_operator_type_ok():
    validate(
        """
        func main() {
            const a: bool = 1 == 1;
        }
        """
    )


def test_compare_operator_type_fail():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            func main() {
                const a: i32 = 1 == 1;
            }
            """
        )


def test_compare_operator_type_fail2():
    with pytest.raises(TypeMismatchException):
        validate(
            """
            func main() {
                const s: string = "test";
                const a: bool = 1 == s;
            }
            """
        )
