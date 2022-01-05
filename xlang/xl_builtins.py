from typing import List
from xlang.exceptions import InterpreterAssertionError
from xlang.xl_ast import (
    FunctionParameter,
    ParseContext,
    VariableType,
    VariableTypeEnum,
    PrimitiveType,
    BuiltinFunction,
)
from xlang.interpreter import Value


def print_builtin(values: List[Value], *args, **kwargs):
    print(values[0].value)


def append_builtin(values: List[Value], *args, **kwargs):
    array, value = values
    array.value.append(value)


def assert_builtin(values: List[Value], context, *args, **kwargs):
    assert len(values) == 1
    if values[0].primitive_type != PrimitiveType.BOOL:
        raise Exception("assert: expression is not a boolean")
    if values[0].value is not True:
        raise InterpreterAssertionError("assertion failed", context)


def get_builtins() -> List[BuiltinFunction]:
    return [
        BuiltinFunction(
            "printi",
            None,
            [
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.I64,
                    ),
                )
            ],
            print_builtin,
        ),
        BuiltinFunction(
            "prints",
            None,
            [
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.STRING,
                    ),
                )
            ],
            print_builtin,
        ),
        BuiltinFunction(
            "printf",
            None,
            [
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.FLOAT,
                    ),
                )
            ],
            print_builtin,
        ),
        BuiltinFunction(
            "printb",
            None,
            [
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.BOOL,
                    ),
                )
            ],
            print_builtin,
        ),
        BuiltinFunction(
            "appendi",
            None,
            [
                FunctionParameter(
                    name="array",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.ARRAY,
                        array_type=VariableType(
                            variable_type=VariableTypeEnum.PRIMITIVE,
                            primitive_type=PrimitiveType.I64,
                        ),
                    ),
                    inout=True,
                ),
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.I64,
                    ),
                ),
            ],
            append_builtin,
        ),
        BuiltinFunction(
            "appends",
            None,
            [
                FunctionParameter(
                    name="array",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.ARRAY,
                        array_type=VariableType(
                            variable_type=VariableTypeEnum.PRIMITIVE,
                            primitive_type=PrimitiveType.STRING,
                        ),
                    ),
                    inout=True,
                ),
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.STRING,
                    ),
                ),
            ],
            append_builtin,
        ),
        BuiltinFunction(
            "appendf",
            None,
            [
                FunctionParameter(
                    name="array",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.ARRAY,
                        array_type=VariableType(
                            variable_type=VariableTypeEnum.PRIMITIVE,
                            primitive_type=PrimitiveType.FLOAT,
                        ),
                    ),
                    inout=True,
                ),
                FunctionParameter(
                    name="value",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.FLOAT,
                    ),
                ),
            ],
            append_builtin,
        ),
        BuiltinFunction(
            "assert",
            None,
            [
                FunctionParameter(
                    name="test",
                    context=ParseContext(None),
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.BOOL,
                    ),
                )
            ],
            assert_builtin,
        ),
    ]
