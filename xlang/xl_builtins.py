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


def builtin(name, return_type, params, context=False):
    def decorate(func):
        global BUILTINS

        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
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


@builtin("assert", None, [prim("value", PrimitiveType.BOOL)], True)
def builtin_assert(value, context):
    if value.value is not True:
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
]


def get_builtins() -> List[BuiltinFunction]:
    return BUILTINS
