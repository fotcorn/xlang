from enum import Enum, auto
from typing import List, Dict, Union, Optional, Any
from pydantic.dataclasses import dataclass
import copy

from xlang.xl_ast import *

class ValueType(Enum):
    PRIMITIVE = auto()
    STRUCT = auto()

@dataclass
class Value:
    type: ValueType
    value: Any
    primitive_type: PrimitiveType = None
    is_array: bool = False
    type_name: str = None # for structs and enums


class ScopeStack:
    def __init__(self):
        self.stack = [{}]

    def set_variable(self, name: str, value):
        self.stack[-1][name] = value

    def get_variable(self, name: str):
        for stack in reversed(self.stack):
            if name in stack:
                return stack[name]
        return None

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        self.stack.pop()


class Interpreter:
    def run(self, ast: GlobalScope):
        self.global_scope = ast
        if not 'main' in ast.functions:
            raise Exception("No main function found")
        main_function = ast.functions['main']
        self.scope_stack = ScopeStack()
        self.statements(main_function.statements)

    def statements(self, statements):
        for statement in statements:
            self.statement(statement)

    def statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            value = self.default_variable_value(statement.variable_type)
            self.scope_stack.set_variable(statement.name, None)
        elif isinstance(statement, VariableDefinition) or isinstance(statement, VariableAssign):
            value = self.expression(statement.value)
            self.scope_stack.set_variable(statement.name, value)
        elif isinstance(statement, FunctionCall):
            self.function_call(statement)
        elif isinstance(statement, Loop):
            raise Exception("not implemented")
        elif isinstance(statement, If):
            raise Exception("not implemented")
        elif isinstance(statement, Return):
            raise Exception("not implemented")
        elif isinstance(statement, Continue):
            raise Exception("not implemented")
        elif isinstance(statement, Break):
            raise Exception("not implemented")
        else:
            raise Exception("Unhandled statement")

    def expression(self, expression: BaseExpression):
        if isinstance(expression, FunctionCall):
            return self.function_call(expression)
        elif isinstance(expression, VariableAccess):
            if expression.variable_access:
                raise Exception("struct access not implemented")
            if expression.array_access:
                raise Exception("array access not implemented")
            return self.scope_stack.get_variable(expression.variable_name)
        elif isinstance(expression, Constant):
            return self.value_from_constant(expression)
        elif isinstance(expression, OperatorExpression):
            operand1_value = self.expression(expression.operand1)
            operand2_value = self.expression(expression.operand2)
            if expression.operator in ('+', '-', '*', '/', '%'):
                if not operand1_value.type == ValueType.PRIMITIVE or operand1_value.primitive_type not in NUMBER_TYPES or operand1_value.is_array:
                    raise Exception(f'+ operator not supported on type: {operand1_value}')
                if not operand2_value.type == ValueType.PRIMITIVE or operand2_value.primitive_type not in NUMBER_TYPES or operand2_value.is_array:
                    raise Exception(f'+ operator not supported on type: {operand1_value}')
                if operand1_value.primitive_type == PrimitiveType.FLOAT or operand2_value.primitive_type == PrimitiveType.FLOAT and not operand1_value.primitive_type == operand2_value.primitive_type:
                    raise Exception(f'+ operator only works beween int types or float, not float and int.')
                if expression.operator == '+':
                    value = operand1_value.value + operand2_value.value
                elif expression.operator == '-':
                    value = operand1_value.value - operand2_value.value
                elif expression.operator == '*':
                    value = operand1_value.value * operand2_value.value
                elif expression.operator == '/':
                    value = operand1_value.value // operand2_value.value
                elif expression.operator == '%':
                    value = operand1_value.value % operand2_value.value
                return Value(type=ValueType.PRIMITIVE, value=value, primitive_type=expression.type.primitive_type)
            else:
                raise Exception(f'not implemented operator: {expression.operator}')
        else:
            raise Exception("internal compiler error: Unknown expression")

    def function_call(self, func_call):
        params = [self.expression(param) for param in func_call.params]
        params_copy = copy.deepcopy(params) # call by value
        function = self.global_scope.functions[func_call.function_name]
        if isinstance(function, BuiltinFunction):
            function.function_ptr(params_copy)
        else:
            old_scope_stack = self.scope_stack
            self.scope_stack = ScopeStack()
            for i, param_type in enumerate(function.function_params):
                self.scope_stack.set_variable(param_type.name, params_copy[i])
            self.statements(function.statements)
            self.scope_stack = old_scope_stack

    def default_variable_value(self, variable_type):
        base_type = variable_type.variable_type
        if base_type == VariableTypeEnum.PRIMITIVE:
            primitive_type = variable_type.primitive_type
            if primitive_type in INTEGER_TYPES:
                return Value(type=ValueType.PRIMITIVE, value=0, primitive_type=primitive_type)
            elif primitive_type == PrimitiveType.FLOAT:
                return Value(type=ValueType.PRIMITIVE, value=0.0, primitive_type=primitive_type)
            elif primitive_type == PrimitiveType.STRING:
                return Value(type=ValueType.PRIMITIVE, value="", primitive_type=primitive_type)
            elif primitive_type == PrimitiveType.BOOL:
                return Value(type=ValueType.PRIMITIVE, value=False, primitive_type=primitive_type)
            else:
                raise Exception("internal compiler error: primitive type not handled")
        elif base_type == VariableTypeEnum.ARRAY:
            if statement.variable_type.array_type.variable_type == VariableTypeEnum.PRIMITIVE:
                return Value(type=ValueType.PRIMITIVE, value=[], primitive_type=statement.variable_type.array_type.primitive_type, is_array=True)
            elif statement.variable_type.array_type.variable_type == VariableTypeEnum.STRUCT:
                return Value(type=ValueType.STRUCT, value=[], type_name=statement.variable_type.array_type.type_name, is_array=True)
            else:
                raise Exception("array type not implemented")  # multidimensional arrays
        elif base_type == VariableTypeEnum.STRUCT:
            struct_def = self.global_scope.structs[variable_type.type_name]
            struct_data = {}
            for member in struct_def.members:
                struct_data[member.name] = self.default_variable_value(member.param_type)
            return struct_data
        else:
            raise Exception("internal compiler error: unknown variable type")

    def value_from_constant(self, constant: Constant) -> Value:
        return Value(type=ValueType.PRIMITIVE, value=constant.value, primitive_type=constant.type.primitive_type)
