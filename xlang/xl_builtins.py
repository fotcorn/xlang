from typing import List
from xlang.xl_ast import (
    FunctionParameter,
    VariableType,
    VariableTypeEnum,
    PrimitiveType,
    BuiltinFunction,
)


class Value:
    pass


def print_builtin(values: List[Value]):
    print(values[0].value)


def append_builtin(values: List[Value]):
    array, value = values
    array.value.append(value)


def get_builtins() -> List[BuiltinFunction]:
    return [
        BuiltinFunction(
            "printi",
            None,
            [
                FunctionParameter(
                    name="value",
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
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.FLOAT,
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
                    param_type=VariableType(
                        variable_type=VariableTypeEnum.PRIMITIVE,
                        primitive_type=PrimitiveType.FLOAT,
                    ),
                ),
            ],
            append_builtin,
        ),
    ]
