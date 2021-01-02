from xlang.xl_ast import VariableType, GlobalScope, PrimitiveType, VariableTypeEnum


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


def is_type_compatible(
    variable_type_a: VariableType, variable_type_b: VariableType
) -> bool:
    if variable_type_a.variable_type != variable_type_b.variable_type:
        return False
    if variable_type_a.variable_type == VariableTypeEnum.ARRAY:
        return is_type_compatible(
            variable_type_a.array_type, variable_type_b.array_type
        )
    elif variable_type_a.variable_type == VariableTypeEnum.STRUCT:
        return variable_type_a.type_name == variable_type_b.type_name
    elif variable_type_a.variable_type == VariableTypeEnum.PRIMITIVE:
        # todo i32 is also compatible to i64, i32 is compatible with u64 etc.
        return variable_type_a.primitive_type == variable_type_b.primitive_type
    else:
        raise Exception("Unhandled type in is_type_compatible")
