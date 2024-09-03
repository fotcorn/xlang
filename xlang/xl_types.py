from xlang.xl_ast import (
    ParseContext,
    VariableType,
    GlobalScope,
    PrimitiveType,
    VariableTypeEnum,
)
from xlang.exceptions import ContextException, InternalCompilerError


def typeify(base_type: VariableType, global_scope: GlobalScope):
    if base_type.variable_type == VariableTypeEnum.ARRAY:
        assert base_type.array_type
        assert base_type.array_type.type_name
        assert base_type.array_type.variable_type == VariableTypeEnum.UNKNOWN
        base_type.array_type = get_type_from_string(
            global_scope, base_type.array_type.type_name
        )
    elif base_type.variable_type == VariableTypeEnum.UNKNOWN:
        assert base_type.type_name
        base_type = get_type_from_string(global_scope, base_type.type_name)
    else:
        raise InternalCompilerError("Unhandled type in struct validation pass")
    return base_type


def primitive(primitive_type: PrimitiveType) -> VariableType:
    return VariableType(
        variable_type=VariableTypeEnum.PRIMITIVE, primitive_type=primitive_type
    )


def get_type_from_string(global_scope: GlobalScope, type_name: str) -> VariableType:
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
    elif type_name == "f32":
        return primitive(PrimitiveType.F32)
    elif type_name == "string":
        return primitive(PrimitiveType.STRING)
    elif type_name == "bool":
        return primitive(PrimitiveType.BOOL)
    elif type_name in global_scope.structs:
        return VariableType(variable_type=VariableTypeEnum.STRUCT, type_name=type_name)
    else:
        raise InternalCompilerError(f"Unknown type: {type_name}")


SIGNED = (
    -128,
    -32768,
    -2147483648,
    -9223372036854775808,
)

UNSIGNED = (
    255,
    65535,
    4294967295,
    18446744073709551615,
)


def primitive_type_from_constant(constant: int, context: ParseContext):
    if constant < 0:
        if constant >= SIGNED[0]:
            return primitive(PrimitiveType.I8)
        elif constant >= SIGNED[1]:
            return primitive(PrimitiveType.I16)
        elif constant >= SIGNED[2]:
            return primitive(PrimitiveType.I32)
        elif constant >= SIGNED[3]:
            return primitive(PrimitiveType.I64)
        else:
            raise ContextException("Constant out of range", context)
    else:
        if constant <= UNSIGNED[0]:
            return primitive(PrimitiveType.U8)
        elif constant <= UNSIGNED[1]:
            return primitive(PrimitiveType.U16)
        elif constant <= UNSIGNED[2]:
            return primitive(PrimitiveType.U32)
        elif constant <= UNSIGNED[3]:
            return primitive(PrimitiveType.U64)
        else:
            raise ContextException("Constant out of range", context)


# target => source
PRIMITIVE_AUTO_CONVERSION = {
    PrimitiveType.U8: [PrimitiveType.U8],
    PrimitiveType.I8: [PrimitiveType.I8],
    PrimitiveType.U16: [PrimitiveType.U8, PrimitiveType.U16],
    PrimitiveType.I16: [PrimitiveType.U8, PrimitiveType.I8, PrimitiveType.I16],
    PrimitiveType.U32: [PrimitiveType.U8, PrimitiveType.U16, PrimitiveType.U32],
    PrimitiveType.I32: [
        PrimitiveType.U8,
        PrimitiveType.U16,
        PrimitiveType.I8,
        PrimitiveType.I16,
        PrimitiveType.I32,
    ],
    PrimitiveType.U64: [
        PrimitiveType.U8,
        PrimitiveType.U16,
        PrimitiveType.U32,
        PrimitiveType.U64,
    ],
    PrimitiveType.I64: [
        PrimitiveType.U8,
        PrimitiveType.U16,
        PrimitiveType.U32,
        PrimitiveType.I8,
        PrimitiveType.I16,
        PrimitiveType.I32,
        PrimitiveType.I64,
    ],
}


def is_type_compatible(target_type: VariableType, source_type: VariableType) -> bool:
    """can source_type be assigned to target_type?"""
    if target_type.variable_type == VariableTypeEnum.BUILTIN_GENERIC:
        return True
    if target_type.variable_type != source_type.variable_type:
        return False
    if target_type.variable_type == VariableTypeEnum.ARRAY:
        assert target_type.array_type
        assert source_type.array_type
        return is_type_compatible(target_type.array_type, source_type.array_type)
    elif target_type.variable_type == VariableTypeEnum.STRUCT:
        return target_type.type_name == source_type.type_name
    elif target_type.variable_type == VariableTypeEnum.PRIMITIVE:
        if target_type.primitive_type in PRIMITIVE_AUTO_CONVERSION:
            return (
                source_type.primitive_type
                in PRIMITIVE_AUTO_CONVERSION[target_type.primitive_type]
            )
        else:
            return target_type.primitive_type == source_type.primitive_type
    else:
        raise InternalCompilerError("Unhandled type in is_type_compatible")
