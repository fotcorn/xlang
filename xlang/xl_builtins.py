from collections import defaultdict
import functools
from typing import Dict, List, Optional
from xlang.exceptions import InterpreterAssertionError
from xlang.xl_ast import (
    FunctionParameter,
    ParseContext,
    VariableType,
    VariableTypeEnum,
    PrimitiveType,
    BuiltinFunction,
)
from xlang.interpreter_datatypes import Value

BUILTIN_FUNCTIONS = {}
BUILTIN_ARRAY_METHODS = {}
BUILTIN_PRIMITIVE_METHODS: Dict = defaultdict(dict)


def builtin_function(
    name: str,
    return_type: Optional[VariableType],
    params: List[FunctionParameter],
    context: bool = False,
):
    def decorate(func):
        global BUILTIN_FUNCTIONS

        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
                return func(*params)

        BUILTIN_FUNCTIONS[name] = BuiltinFunction(
            name=name,
            return_type=return_type,
            function_params=params,
            function_ptr=wrapper,
        )
        return wrapper

    return decorate


def builtin_method_array(
    name: str,
    return_type: Optional[VariableType],
    params: List[FunctionParameter],
    context=False,
):
    def decorate(func):
        global BUILTIN_METHODS

        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
                return func(*params)

        func = BuiltinFunction(
            name=name,
            return_type=return_type,
            function_params=params,
            function_ptr=wrapper,
        )
        BUILTIN_ARRAY_METHODS[name] = func

        return wrapper

    return decorate


def builtin_method_primitive(
    primitive_type: PrimitiveType,
    name: str,
    return_type: VariableType,
    params: List[FunctionParameter],
    context=False,
):
    def decorate(func):
        global BUILTIN_ARRAY_METHODS

        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
                return func(*params)

        func = BuiltinFunction(
            name=name,
            return_type=return_type,
            function_params=params,
            function_ptr=wrapper,
        )
        BUILTIN_PRIMITIVE_METHODS[primitive_type][name] = func

        return wrapper

    return decorate


def prim(param_name: str, primitive_type: PrimitiveType):
    return FunctionParameter(
        name=param_name,
        context=ParseContext.from_builtin(),
        param_type=VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=primitive_type,
        ),
        reference=False,
    )


@builtin_function("prints", None, [prim("value", PrimitiveType.STRING)])
def builtin_prints(value: Value):
    print(value.value)


@builtin_function("printi", None, [prim("value", PrimitiveType.I64)])
def builtin_printi(value: Value):
    print(value.value)


@builtin_function("printf", None, [prim("value", PrimitiveType.F32)])
def builtin_printf(value: Value):
    print(value.value)


@builtin_function("printb", None, [prim("value", PrimitiveType.BOOL)])
def builtin_printb(value: Value):
    print("true" if value.value else "false")


@builtin_function("assert", None, [prim("value", PrimitiveType.BOOL)], True)
def builtin_assert(value, context):
    if value.value is not True:
        raise InterpreterAssertionError("assertion failed", context)


@builtin_method_array(
    "append",
    None,
    [
        FunctionParameter(
            name="value",
            param_type=VariableType(variable_type=VariableTypeEnum.BUILTIN_GENERIC),
            context=ParseContext.from_builtin(),
            reference=False,
        )
    ],
)
def builtin_append(array, value):
    array.value.append(value)


@builtin_method_primitive(
    PrimitiveType.STRING,
    "toLowerCase",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING
    ),
    [],
)
def builtin_string_toLowerCase(string):
    return string.lower()


@builtin_method_primitive(
    PrimitiveType.STRING,
    "toUpperCase",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING
    ),
    [],
)
def builtin_string_toUpperCase(string):
    return string.upper()


def get_builtin_functions() -> Dict[str, BuiltinFunction]:
    return BUILTIN_FUNCTIONS


def get_builtin_array_methods() -> Dict[str, BuiltinFunction]:
    return BUILTIN_ARRAY_METHODS


def get_builtin_primitive_methods():
    return BUILTIN_PRIMITIVE_METHODS
