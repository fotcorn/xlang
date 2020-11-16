from xl_ast import VariableType, GlobalScope, VariableTypeEnum, PrimitiveType


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


def validation_pass():
    scope_stack = ScopeStack()


def get_type_from_string(global_scope: GlobalScope, type_name: str) -> VariableType:
    # int is just an alias for i64
    if type_name == "int":
        type_name = "i64"
    if type_name == "i64":
        return VariableType(
            VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64
        )
    elif type_name == "i32":
        return VariableType(
            VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64
        )
    elif type_name == "i16":
        return VariableType(
            VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64
        )
    elif type_name == "i8":
        return VariableType(
            VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.I64
        )