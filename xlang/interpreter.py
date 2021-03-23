from enum import Enum, auto
from typing import List, Dict, Union, Optional, Any
from pydantic.dataclasses import dataclass

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


class ScopeStack:
    def __init__(self):
        self.stack = [{}]

    def set_variable(self, name: str, variable_type: VariableType):
        self.stack[-1][name] = variable_type

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
            raise Exception("not implemented")
        elif isinstance(statement, VariableDefinition):
            raise Exception("not implemented")
        elif isinstance(statement, VariableAssign):
            raise Exception("not implemented")
        elif isinstance(statement, FunctionCall):
            params = [self.expression(param) for param in statement.params]
            function = self.global_scope.functions[statement.function_name]
            if isinstance(function, BuiltinFunction):
                function.function_ptr(params)
            else:
                old_scope_stack = self.scope_stack
                self.scope_stack = ScopeStack()
                # todo: add params to scope stack
                self.statements(function.statements)
                self.scope_stack = old_scope_stack
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
            raise Exception("not implemented")
        elif isinstance(expression, VariableAccess):
            raise Exception("not implemented")
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
                raise Exception(f'unimplemented operator: {expression.operator}')
        else:
            raise Exception("Unknown expression")
    
    def value_from_constant(self, constant: Constant) -> Value:
        return Value(type=ValueType.PRIMITIVE, value=constant.value, primitive_type=constant.type.primitive_type)
