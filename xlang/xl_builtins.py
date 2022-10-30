import functools
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

BUILTINS = []


def builtin(name, return_type, params):
    def decorate(func):
        global BUILTINS

        @functools.wraps(func)
        def wrapper(params, **kwargs):
            return func(*params)

        BUILTINS.append(
            BuiltinFunction(
                name,
                return_type,
                params,
                wrapper,
            )
        )

        return wrapper

    return decorate


def prim(param_name: str, primitive_type: PrimitiveType):
    return FunctionParameter(
        name=param_name,
        context=ParseContext(None),
        param_type=VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=primitive_type,
        ),
        reference=False,
    )


@builtin("prints", None, [prim("value", PrimitiveType.STRING)])
def builtin_prints(value: Value):
    print(value.value)


@builtin("printi", None, [prim("value", PrimitiveType.I64)])
def builtin_printi(value: Value):
    print(value.value)


@builtin("printf", None, [prim("value", PrimitiveType.FLOAT)])
def builtin_printf(value: Value):
    print(value.value)


@builtin("printb", None, [prim("value", PrimitiveType.BOOL)])
def builtin_printb(value: Value):
    print(value.value)


def append_builtin(values: List[Value], *args, **kwargs):
    array, value = values
    array.value.append(value)


def assert_builtin(values: List[Value], context, *args, **kwargs):
    assert len(values) == 1
    if values[0].primitive_type != PrimitiveType.BOOL:
        raise Exception("assert: expression is not a boolean")
    if values[0].value is not True:
        raise InterpreterAssertionError("assertion failed", context)


BUILTINS += [
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
                reference=True,
            ),
            FunctionParameter(
                name="value",
                context=ParseContext(None),
                param_type=VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.I64,
                ),
                reference=False,
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
                reference=True,
            ),
            FunctionParameter(
                name="value",
                context=ParseContext(None),
                param_type=VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.STRING,
                ),
                reference=False,
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
                reference=True,
            ),
            FunctionParameter(
                name="value",
                context=ParseContext(None),
                param_type=VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.FLOAT,
                ),
                reference=False,
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
                reference=False,
            )
        ],
        assert_builtin,
    ),
]


def get_builtins() -> List[BuiltinFunction]:
    return BUILTINS
