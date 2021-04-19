from typing import List
from xlang.xl_ast import IdentifierAndType, VariableType, VariableTypeEnum, PrimitiveType, BuiltinFunction

class Value:
    pass

def print_builtin(values: List[Value]):
    print(values[0].value)

def append_builtin(values: List[Value]):
    array, value = values
    array.value.append(value.value)

def get_builtins() -> List[BuiltinFunction]:
    return [
        BuiltinFunction("printi", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64))], print_builtin),
        BuiltinFunction("prints", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING))], print_builtin),
        BuiltinFunction("printf", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.FLOAT))], print_builtin),
        BuiltinFunction("appendi", None, [
            IdentifierAndType(name='array', param_type=VariableType(variable_type=VariableTypeEnum.ARRAY, array_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64))),
            IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64))
        ], append_builtin),
        BuiltinFunction("appends", None, [
            IdentifierAndType(name='array', param_type=VariableType(variable_type=VariableTypeEnum.ARRAY, array_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING))),
            IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING))
        ], append_builtin),
        BuiltinFunction("appendf", None, [
            IdentifierAndType(name='array', param_type=VariableType(variable_type=VariableTypeEnum.ARRAY, array_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.FLOAT))),
            IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.FLOAT))
        ], append_builtin),
    ]
