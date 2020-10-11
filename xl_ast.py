from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Union, Type


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
    array_type: Type['Variable'] = None

    @staticmethod
    def from_string(t: str) -> Type['VariableType']:
        if t.endswith('[]'):
            raise NotImplementedError('arrays not implemented')
        if t == 'int':
            t = 'i64'
        elif t == 'uint':
            t = 'u64'
        if t in ['i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64']:
            variable_type = VariableType(VariableTypeEnum.PRIMITIVE)
            variable_type.primitive_type = t
            return variable_type
        else:
            # TODO: implement arrays, structs, enums
            raise NotImplementedError('unknown type')


@dataclass
class Variable:
    variable_type: VariableType
    register: int


@dataclass
class Scope:
    code: str = ''
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
    functions: Dict[str, Type['Function']] = field(default_factory=dict)

    pass


class BaseExpression:
    pass


class ConstantType(Enum):
    INTEGER = auto()


@dataclass
class Constant(BaseExpression):
    type: ConstantType
    value: Union[int, str]


@dataclass
class CompareExpr(BaseExpression):
    expr1: BaseExpression
    expr2: BaseExpression
    operator: str


@dataclass
class VariableAccess(BaseExpression):
    variable_name: str


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
class Function:
    name: str
    statements: List[Statement]
