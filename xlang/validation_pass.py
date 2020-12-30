from xlang.xl_ast import (
    VariableType,
    GlobalScope,
    VariableTypeEnum,
    PrimitiveType,
    VariableDeclaration,
)
from typing import Optional


class ScopeStack:
    def def_variable(self, name: str, variable_type: VariableType):
        pass

    def variable_exists(self, name: str) -> bool:
        pass

    def get_variable_type(self, name: str) -> Optional[VariableType]:
        pass

    def push_scope(self):
        pass

    def pop_scope(self):
        pass


def typeify(base_type: VariableType, global_scope: GlobalScope):
    if base_type.variable_type == VariableTypeEnum.ARRAY:
        assert base_type.array_type.variable_type == VariableTypeEnum.UNKNOWN
        base_type.array_type = get_type_from_string(
            global_scope, base_type.array_type.type_name
        )
    elif base_type.variable_type == VariableTypeEnum.UNKNOWN:
        base_type = get_type_from_string(global_scope, base_type.type_name)
    else:
        raise Exception("Unhandled type in struct validation pass")
    return base_type


def validation_pass(global_scope: GlobalScope):
    for struct in global_scope.structs.values():
        for member in struct.members:
            member.param_type = typeify(member.param_type, global_scope)

    for function in global_scope.functions.values():
        if function.return_type:
            function.return_type = typeify(function.return_type, global_scope)
        for parameter in function.function_params:
            parameter.param_type = typeify(parameter.param_type, global_scope)

        scope_stack = ScopeStack()

        for statement in function.statements:
            if isinstance(statement, VariableDeclaration):
                pass


def primitive(primitive_type: PrimitiveType) -> VariableType:
    return VariableType(VariableTypeEnum.PRIMITIVE, primitive_type=primitive_type)


def get_type_from_string(global_scope: GlobalScope, type_name: str) -> VariableType:
    # int is just an alias for i64
    if type_name == "int":
        type_name = "i64"
    if type_name == "i64":
        return primitive(PrimitiveType.I64)
    elif type_name == "i32":
        return primitive(PrimitiveType.I32)
    elif type_name == "i16":
        return primitive(PrimitiveType.I16)
    elif type_name == "i8":
        return primitive(PrimitiveType.I8)
    elif type_name == "u64":
        return primitive(PrimitiveType.U64)
    elif type_name == "u32":
        return primitive(PrimitiveType.U32)
    elif type_name == "u16":
        return primitive(PrimitiveType.U16)
    elif type_name == "u8":
        return primitive(PrimitiveType.U8)
    elif type_name == "float":
        return primitive(PrimitiveType.FLOAT)
    elif type_name == "string":
        return primitive(PrimitiveType.STRING)
    elif type_name in global_scope.structs:
        return VariableType(VariableTypeEnum.STRUCT, type_name=type_name)
    else:
        raise Exception(f"Unknown type: {type_name}")