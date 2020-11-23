from xlang.xl_ast import VariableType, GlobalScope, VariableTypeEnum, PrimitiveType
from typing import Optional

class ScopeStack:
    def def_variable(name: str, type: VariableType):
        pass

    def variable_exists(name: str) -> bool:
        pass

    def get_variable_type(name: str) -> Optional[VariableType]:
        pass

    def push_scope():
        pass

    def pop_scope():
        pass


def validation_pass(global_scope: GlobalScope):
    for struct in global_scope.structs.values():
        for member in struct.members:
            if member.param_type.variable_type == VariableTypeEnum.ARRAY:
                assert member.param_type.array_type.variable_type == VariableTypeEnum.UNKNOWN
                member.param_type.array_type = get_type_from_string(global_scope, member.param_type.array_type.type_name)
            elif member.param_type.variable_type == VariableTypeEnum.UNKNOWN:
                member.param_type = get_type_from_string(global_scope, member.param_type.type_name)
            else:
                raise Exception("Unhandled type in struct validation pass")


def primitive(primitive_type: PrimitiveType) -> VariableType:
    return VariableType(
        VariableTypeEnum.PRIMITIVE, primitive_type=primitive_type
    )


def get_type_from_string(global_scope: GlobalScope, type_name: str) -> VariableType:
    # int is just an alias for i64
    if type_name == "int":
        type_name = "i64"
    if type_name == "i64":
        return primitive(PrimitiveType.I64)
    elif type_name == "i32":
        return primitive(PrimitiveType.I64)
    elif type_name == "i16":
        return primitive(PrimitiveType.I64)
    elif type_name == "i8":
        return primitive(PrimitiveType.I64)
    elif type_name == "i8":
        return primitive(PrimitiveType.I64)
    elif type_name == "u64":
        return primitive(PrimitiveType.I64)
    elif type_name == "u32":
        return primitive(PrimitiveType.I64)
    elif type_name == "u16":
        return primitive(PrimitiveType.I64)
    elif type_name == "u8":
        return primitive(PrimitiveType.I64)
    elif type_name == "float":
        return primitive(PrimitiveType.FLOAT)
    elif type_name == "string":
        return primitive(PrimitiveType.STRING)
    elif type_name in global_scope.structs:
        return VariableType(VariableTypeEnum.STRUCT, type_name=type_name)
    else:
        raise Exception(f"Unknown type: {type_name}")
