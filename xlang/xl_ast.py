from __future__ import annotations

from pydantic import BaseModel
from enum import Enum, auto
from typing import List, Dict, Optional, Callable, Any


class VariableTypeEnum(Enum):
    UNKNOWN = auto()  # in the first parsing phase, we do not know the exact type yet
    PRIMITIVE = auto()
    ARRAY = auto()
    STRUCT = auto()
    ENUM = auto()
    BUILTIN_GENERIC = auto()


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
    F32 = auto()
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


NUMBER_TYPES = INTEGER_TYPES + (PrimitiveType.F32,)


class ParseContext(BaseModel):
    start_pos: int = 0
    end_pos: int = 0
    line: int = 0
    column: int = 0
    builtin: bool = False

    @staticmethod
    def from_builtin():
        return ParseContext(builtin=True)

    @staticmethod
    def from_token(token: Any):
        return ParseContext(
            start_pos=token.start_pos,
            end_pos=token.end_pos,
            line=token.line,
            column=token.column,
        )

    @staticmethod
    def from_exception(exception: Any):
        return ParseContext(
            start_pos=exception.pos_in_stream,
            end_pos=exception.pos_in_stream,
            line=exception.line,
            column=exception.column,
        )

    def __repr__(self) -> str:
        if self.builtin:
            return "<builtin>"
        else:
            return f"line: {self.line}, column: {self.column}"


class VariableType(BaseModel):
    variable_type: VariableTypeEnum
    type_name: Optional[str] = None
    primitive_type: Optional[PrimitiveType] = None
    array_type: Optional[VariableType] = None


class StructType(BaseModel):
    name: str
    members: List[IdentifierAndType]
    context: ParseContext


class GlobalScope(BaseModel):
    structs: Dict[str, StructType] = {}
    functions: Dict[str, BaseFunction] = {}

    def dump(self):
        def dump_base_model(scope):
            d = {"ast_type": scope.__class__.__name__}
            d.update(cleanup_dict(scope.__dict__))
            return d

        def cleanup_dict(scope):
            new_dict = {}
            for k, v in scope.items():
                if k != "context" and v is not None:
                    if isinstance(v, dict):
                        new_dict[k] = cleanup_dict(v)
                    elif isinstance(v, Enum):
                        new_dict[k] = v.name
                    elif isinstance(v, VariableType):
                        if v.variable_type == VariableTypeEnum.PRIMITIVE:
                            new_dict[k] = v.primitive_type.name
                        else:
                            new_dict[k] = dump_base_model(v)
                    elif isinstance(v, BaseModel):
                        new_dict[k] = dump_base_model(v)
                    elif isinstance(v, list):
                        new_list = []
                        for item in v:
                            if isinstance(item, BaseModel):
                                new_list.append(dump_base_model(item))
                            else:
                                new_list.append(item)
                        new_dict[k] = new_list
                    else:
                        new_dict[k] = v
            return new_dict

        return dump_base_model(self)


class BaseExpression(BaseModel):
    type: Optional[VariableType]
    context: ParseContext


class ConstantType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()


class Constant(BaseExpression):
    constant_type: ConstantType
    value: Any


class MathOperation(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


class CompareOperation(BaseExpression):
    operand1: BaseExpression
    operand2: BaseExpression
    operator: str


class ArrayAccess(BaseExpression):
    expression: BaseExpression


class Statement(BaseModel):
    context: ParseContext


class VariableAccess(Statement, BaseExpression):
    variable_name: str
    array_access: Optional[BaseExpression] = None
    variable_access: Optional[VariableAccess] = None
    method_call: Optional[FunctionCall] = None


class FunctionCall(Statement, BaseExpression):
    function_name: str
    params: List[BaseExpression]


class VariableDeclaration(Statement):
    name: str
    variable_type: VariableType


class VariableDefinition(Statement):
    name: str
    variable_type: VariableType
    value: BaseExpression
    const: bool


class VariableAssign(Statement):
    variable_access: VariableAccess
    value: BaseExpression


class IdentifierAndType(BaseModel):
    name: str
    param_type: VariableType
    context: ParseContext


class FunctionParameter(IdentifierAndType):
    reference: bool


class BaseFunction(BaseModel):
    name: str
    return_type: Optional[VariableType]
    function_params: List[FunctionParameter]


class Function(BaseFunction):
    statements: List[Statement]
    context: ParseContext


class BuiltinFunction(BaseFunction):
    function_ptr: Callable


class Loop(Statement):
    statements: List[Statement]


class If(Statement):
    condition: BaseExpression
    statements: List[Statement]
    elif_statements: List[Elif] = []
    else_statement: Optional[Else] = None


class Elif(Statement):
    condition: BaseExpression
    statements: List[Statement]


class Else(Statement):
    statements: List[Statement]


class Continue(Statement):
    pass


class Break(Statement):
    pass


class Return(Statement):
    value: Optional[BaseExpression] = None
