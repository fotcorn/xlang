from __future__ import annotations

from dataclasses import field
from pydantic.dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Union, Optional

class VariableTypeEnum(Enum):
    PRIMITIVE = auto()
    ARRAY = auto()
    STRUCT = auto()
    ENUM = auto()


@dataclass
class VariableType:
    variable_type: VariableTypeEnum
    primitive_type: str = None
    struct_type: str = None
    enum_type: str = None
    array_type: VariableType = None

    @staticmethod
    def from_string(t: str) -> VariableType:
        if t.endswith("[]"):
            raise NotImplementedError("arrays not implemented")
        if t == "int":
            t = "i64"
        elif t == "uint":
            t = "u64"
        if t in ["i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64"]:
            variable_type = VariableType(VariableTypeEnum.PRIMITIVE)
            variable_type.primitive_type = t
            return variable_type
        else:
            # TODO: implement arrays, structs, enums
            raise NotImplementedError("unknown type")



@dataclass
class Variable:
    variable_type: VariableType
    name: str


@dataclass
class Scope:
    code: str = ""
    register_number: int = 1
    variables: Dict[str, Variable] = field(default_factory=dict)


@dataclass
class StructType:
    pass


@dataclass
class EnumType:
    pass


@dataclass
class GlobalScope:
    structs: Dict[str, StructType] = field(default_factory=dict)
    enums: Dict[str, EnumType] = field(default_factory=dict)
    functions: Dict[str, Function] = field(default_factory=dict)


@dataclass
class BaseExpression:
    pass


class ConstantType(Enum):
    INTEGER = auto()


@dataclass
class Constant(BaseExpression):
    type: ConstantType
    value: Union[int, str]


@dataclass
class OperatorExpression(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


@dataclass
class VariableAccess(BaseExpression):
    variable_name: str
    array_access: OperatorExpression = None
    variable_access: VariableAccess = None


@dataclass
class Statement:
    pass


@dataclass
class FunctionCall(Statement, BaseExpression):
    function_name: str
    params: List[BaseExpression]


@dataclass
class VariableDefinition(Statement):
    name: str
    variable_type: str
    value: BaseExpression


@dataclass
class VariableAssign(Statement):
    name: VariableAccess
    value: BaseExpression


@dataclass
class Function:
    name: str
    statements: List[Statement]


@dataclass
class Loop(Statement):
    statements: List[Statement]


@dataclass
class If(Statement):
    condition: BaseExpression
    statements: List[Statement]


class Continue(Statement):
    pass


class Break(Statement):
    pass


@dataclass
class Return(Statement):
    value: BaseExpression = None


VariableAccess.__pydantic_model__.update_forward_refs()
GlobalScope.__pydantic_model__.update_forward_refs()
