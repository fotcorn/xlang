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
            raise Exception("not implemented")
        else:
            raise Exception("Unknown expression")
    
    def value_from_constant(self, constant: Constant) -> Value:
        return Value(type=ValueType.PRIMITIVE, value=constant.value, primitive_type=constant.type.primitive_type)
