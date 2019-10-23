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

    def generate_code(self):
        code = ''
        for function in self.functions.values():
            code += function.generate_code(self)
        return code


class BaseExpression:
    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> int:
        raise NotImplementedError()


class ConstantType(Enum):
    INTEGER = auto()


@dataclass
class Constant(BaseExpression):
    type: ConstantType
    value: Union[int, str]

    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> int:
        if self.type == ConstantType.INTEGER:
            reg = scope.next_register()
            scope.add_code(f'store i64 {self.value}, i64* %{reg}, align 4')
            return reg
        else:
            raise ValueError('Unknown constant type')


@dataclass
class CompareExpr(BaseExpression):
    expr1: BaseExpression
    expr2: BaseExpression
    operator: str

    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> int:
        var1 = self.expr1.generate_code(scope, global_scope)
        var2 = self.expr2.generate_code(scope, global_scope)
        if self.operator == '==':
            reg = scope.next_register()
            scope.add_code(f'{reg} = icmp eq i64 {var1.register}, {var2.register}')
            return reg
        else:
            raise ValueError(f'Unknown operator: {self.operator}')


@dataclass
class VariableAccess(BaseExpression):
    variable_name: str

    def generate_code(self, scope: Scope, global_scope: GlobalScope) -> int:
        try:
            variable = scope.variables[self.variable_name]
        except KeyError:
            raise ValueError(f'Unknown variable: {self.variable_name}')
        return variable.register


class Statement:
    def generate_code(self, scope: Scope, global_scope: GlobalScope):
        raise NotImplementedError()


@dataclass
class FunctionCall(Statement, BaseExpression):
    function_name: str
    params: List[BaseExpression]

    def generate_code(self, scope: Scope, global_scope: GlobalScope):
        param_regs = [param.generate_code(scope, global_scope) for param in self.params]
        params = ','.join([f'i32 %{reg}' for reg in param_regs])
        scope.add_code(f'call void @{self.function_name}({params})')


@dataclass
class VariableDefinition(Statement):
    name: str
    variable_type: str
    value: BaseExpression

    def generate_code(self, scope: Scope, global_scope: GlobalScope):
        if self.name in scope.variables:
            raise ValueError(f'Variable with name {self.name} is already defined.')
        reg = self.value.generate_code(scope, global_scope)
        scope.variables[self.name] = Variable(VariableType.from_string(self.variable_type), reg)


@dataclass
class Function:
    name: str
    statements: List[Statement]

    def generate_code(self, global_scope: GlobalScope):
        code = f'define dso_local i32 @{self.name}() #0 {{\n'

        scope = Scope()
        for statement in self.statements:
            statement.generate_code(scope, global_scope)
        code += scope.code

        code += 'ret i32 0\n}\n\n'
        return code
