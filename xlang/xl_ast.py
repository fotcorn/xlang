from __future__ import annotations

from dataclasses import field
from pydantic.dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Optional, Callable, Any


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
class ParseContext:
    start_pos: int = 0
    end_pos: int = 0
    line: int = 0
    column: int = 0
    builtin: bool = False

    def __init__(self, token, old_format=False):
        if token:
            if old_format:
                self.start_pos = token.pos_in_stream
                self.end_pos = token.pos_in_stream
            else:
                self.start_pos = token.start_pos
                self.end_pos = token.end_pos
            self.line = token.line
            self.column = token.column
        else:
            self.builtin = True

    def __repr__(self) -> str:
        if self.builtin:
            return "<builtin>"
        else:
            return f"line: {self.line}, column: {self.column}"


@dataclass
class VariableType:
    variable_type: VariableTypeEnum
    type_name: Optional[str] = None
    primitive_type: Optional[PrimitiveType] = None
    array_type: Optional[VariableType] = None


@dataclass
class StructType:
    name: str
    members: List[IdentifierAndType]
    context: ParseContext


@dataclass
class GlobalScope:
    structs: Dict[str, StructType] = field(default_factory=dict)
    functions: Dict[str, BaseFunction] = field(default_factory=dict)


@dataclass
class BaseExpression:
    type: VariableType
    context: ParseContext


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
class MathOperation(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


@dataclass
class CompareOperation(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


@dataclass
class VariableAccess(BaseExpression):
    variable_name: str
    array_access: Optional[BaseExpression] = None
    variable_access: Optional[VariableAccess] = None


@dataclass
class Statement:
    context: ParseContext


@dataclass
class FunctionCall(Statement, BaseExpression):
    function_name: str
    params: List[BaseExpression]

    def __init__(self, function_name, params, context):
        self.function_name = function_name
        self.params = params
        self.type = None
        self.context = context


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
    context: ParseContext


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
    context: ParseContext


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
    elif_statements: List[Elif] = field(default_factory=list)
    else_statement: Optional[Else] = None


@dataclass
class Elif(Statement):
    condition: BaseExpression
    statements: List[Statement]


@dataclass
class Else(Statement):
    statements: List[Statement]


class Continue(Statement):
    pass


class Break(Statement):
    pass


@dataclass
class Return(Statement):
    value: Optional[BaseExpression] = None


VariableAccess.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
VariableType.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
StructType.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
Constant.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
GlobalScope.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
If.__pydantic_model__.update_forward_refs()  # type: ignore[attr-defined]
