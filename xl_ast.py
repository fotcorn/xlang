from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Union, Type


class VariableType(Enum):
    PRIMITIVE = auto()
    ARRAY = auto()
    STRUCT = auto()
    ENUM = auto()


@dataclass
class Variable:
    type: VariableType
    primitive_type: str
    struct_type: str
    enum_type: str
    array_type: Type['Variable']


@dataclass
class Scope:
    code: str = ''
    register_number: int = 0
    variables: Dict[str, Variable] = field(default_factory=dict)

    def add_code(self, new_code: str):
        self.code += new_code + '\n'

    def next_register(self):
        reg = self.register_number
        self.register_number += 1
        return reg


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


class BaseExpression:
    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> VariableType:
        raise NotImplementedError()


class ConstantType(Enum):
    INTEGER = auto()


@dataclass
class Constant(BaseExpression):
    type: ConstantType
    value: Union[int, str]

    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> VariableType:
        if self.type == ConstantType.INTEGER:
            reg = scope.next_register()
            scope.add_code(f'store i64 {self.value}, i64* {reg}, align 4')
            return reg
        else:
            raise ValueError('Unknown constant type')


@dataclass
class CompareExpr(BaseExpression):
    expr1: BaseExpression
    expr2: BaseExpression
    operator: str

    def generate_code(self, scope: Scope, global_scope: GlobalScope):
        var1 = self.expr1.generate_code(scope, global_scope)
        var2 = self.expr2.generate_code(scope, global_scope)
        if self.operator == '==':

            scope.add_code(f'{scope.next_register()} = icmp eq i32 {var1.register}, {var2.register}')
        else:
            raise ValueError(f'Unknown operator: {self.operator}')


class Statement:
    pass


@dataclass
class FunctionCall(Statement):
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
