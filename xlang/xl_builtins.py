from typing import List
from xlang.xl_ast import IdentifierAndType, VariableType, VariableTypeEnum, PrimitiveType, BuiltinFunction

class Value:
    pass

def print_builtin(values: List[Value]):
    print(values[0].value)


def get_builtins() -> List[BuiltinFunction]:
    return [
        BuiltinFunction("printi", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64))], print_builtin),
        BuiltinFunction("prints", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING))], print_builtin),
        BuiltinFunction("printf", None, [IdentifierAndType(name='value', param_type=VariableType(variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.FLOAT))], print_builtin),
    ]
