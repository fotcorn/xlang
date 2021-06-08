from __future__ import annotations

from dataclasses import field
from pydantic.dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Union, Optional, Callable, Any


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
    BOOL = auto()


INTEGER_TYPES = (
    PrimitiveType.I64,
    PrimitiveType.I32,
    PrimitiveType.I16,
    PrimitiveType.I8,
    PrimitiveType.U64,
    PrimitiveType.U32,
    PrimitiveType.U16,
    PrimitiveType.U8,
)


NUMBER_TYPES = INTEGER_TYPES + (PrimitiveType.FLOAT,)


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
    functions: Dict[str, BaseFunction] = field(default_factory=dict)


@dataclass
class BaseExpression:
    type: VariableType


class ConstantType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()


@dataclass
class Constant(BaseExpression):
    constant_type: ConstantType
    value: Any


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
        self.function_name = function_name
        self.params = params
        self.type = None


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
    variable_access: VariableAccess
    value: BaseExpression


@dataclass
class IdentifierAndType:
    name: str
    param_type: VariableType


@dataclass
class FunctionParameter(IdentifierAndType):
    inout: bool = False


@dataclass
class BaseFunction:
    name: str
    return_type: Optional[VariableType]
    function_params: List[FunctionParameter]


@dataclass
class Function(BaseFunction):
    statements: List[Statement]


@dataclass
class BuiltinFunction(BaseFunction):
    function_ptr: Callable


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
Constant.__pydantic_model__.update_forward_refs()
GlobalScope.__pydantic_model__.update_forward_refs()
