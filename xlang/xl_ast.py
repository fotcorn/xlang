from __future__ import annotations

from dataclasses import field
from pydantic.dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Union, Optional


class VariableTypeEnum(Enum):
    UNKNOWN = auto()  # in the first parsing phase, we do not know the exact type yet
    PRIMITIVE = auto()
    ARRAY = auto()
    STRUCT = auto()
    ENUM = auto()


class PrimitiveType(Enum):
    I64 = auto()
    I32 = auto()
    I16 = auto()
    I8 = auto()
    U64 = auto()
    U32 = auto()
    U16 = auto()
    U8 = auto()
    STRING = auto()
    FLOAT = auto()


@dataclass
class VariableType:
    variable_type: VariableTypeEnum
    type_name: str = None
    primitive_type: PrimitiveType = None
    array_type: VariableType = None


@dataclass
class StructType:
    name: str
    members: List[IdentifierAndType]


@dataclass
class GlobalScope:
    structs: Dict[str, StructType] = field(default_factory=dict)
    functions: Dict[str, Function] = field(default_factory=dict)


@dataclass
class BaseExpression:
    type: VariableType


class ConstantType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()


@dataclass
class Constant(BaseExpression):
    constant_type: ConstantType
    value: Union[int, str]


@dataclass
class OperatorExpression(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


@dataclass
class VariableAccess(BaseExpression):
    variable_name: str
    array_access: BaseExpression = None
    variable_access: VariableAccess = None


@dataclass
class Statement:
    pass


@dataclass
class FunctionCall(Statement, BaseExpression):
    function_name: str
    params: List[BaseExpression]

    def __init__(self, function_name, params):
        self.type = None
        self.function_name = function_name
        self.params = params


@dataclass
class VariableDeclaration(Statement):
    name: str
    variable_type: VariableType


@dataclass
class VariableDefinition(Statement):
    name: str
    variable_type: VariableType
    value: BaseExpression


@dataclass
class VariableAssign(Statement):
    name: VariableAccess
    value: BaseExpression


@dataclass
class IdentifierAndType:
    name: str
    param_type: VariableType


@dataclass
class Function:
    name: str
    return_type: Optional[VariableType]
    function_params: List[IdentifierAndType]
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
VariableType.__pydantic_model__.update_forward_refs()
StructType.__pydantic_model__.update_forward_refs()
GlobalScope.__pydantic_model__.update_forward_refs()
