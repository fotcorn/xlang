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
from xlang.interpreter_datatypes import Value, ValueType

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
        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
                return func(*params)

        BUILTIN_ARRAY_METHODS[name] = BuiltinFunction(
            name=name,
            return_type=return_type,
            function_params=params,
            function_ptr=wrapper,
        )

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
        @functools.wraps(func)
        def wrapper(params, **kwargs):
            if context:
                return func(*params, context=kwargs["context"])
            else:
                return func(*params)

        BUILTIN_PRIMITIVE_METHODS[primitive_type][name] = BuiltinFunction(
            name=name,
            return_type=return_type,
            function_params=params,
            function_ptr=wrapper,
        )
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


def builtin_generic(param_name: str):
    return FunctionParameter(
        name=param_name,
        context=ParseContext.from_builtin(),
        param_type=VariableType(
            variable_type=VariableTypeEnum.BUILTIN_GENERIC,
        ),
        reference=False,
    )


@builtin_function("print", None, [builtin_generic("value")])
def builtin_print(value: Value):
    if value.type == ValueType.PRIMITIVE:
        if value.primitive_type == PrimitiveType.BOOL:
            print("true" if value.value else "false")
        else:
            print(value.value)
    elif value.type == ValueType.ENUM:
        print(value.value)  # Prints the enum member name
    else:
        print(str(value.value))


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


@builtin_method_array(
    "length",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I32
    ),
    [],
)
def builtin_array_length(array):
    return Value(
        type=ValueType.PRIMITIVE,
        primitive_type=PrimitiveType.I32,
        value=len(array.value),
    )


@builtin_method_primitive(
    PrimitiveType.STRING,
    "toLowerCase",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING
    ),
    [],
)
def builtin_string_toLowerCase(string):
    return Value(
        type=ValueType.PRIMITIVE,
        primitive_type=PrimitiveType.STRING,
        value=string.value.lower(),
    )


@builtin_method_primitive(
    PrimitiveType.STRING,
    "toUpperCase",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING
    ),
    [],
)
def builtin_string_toUpperCase(string: Value):
    return Value(
        type=ValueType.PRIMITIVE,
        primitive_type=PrimitiveType.STRING,
        value=string.value.upper(),
    )


@builtin_method_primitive(
    PrimitiveType.STRING,
    "length",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I32
    ),
    [],
)
def builtin_string_length(string: Value):
    return Value(
        type=ValueType.PRIMITIVE,
        primitive_type=PrimitiveType.I32,
        value=len(string.value),
    )


@builtin_method_primitive(
    PrimitiveType.CHAR,
    "int",
    VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.U32
    ),
    [],
)
def builtin_char_to_int(char_val: Value):
    return Value(
        type=ValueType.PRIMITIVE,
        primitive_type=PrimitiveType.U32,
        value=ord(char_val.value),
    )


def get_builtin_functions() -> Dict[str, BuiltinFunction]:
    return BUILTIN_FUNCTIONS


def get_builtin_array_methods() -> Dict[str, BuiltinFunction]:
    return BUILTIN_ARRAY_METHODS


def get_builtin_primitive_methods():
    return BUILTIN_PRIMITIVE_METHODS
