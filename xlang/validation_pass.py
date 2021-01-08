from xlang.xl_ast import (
    VariableType,
    GlobalScope,
    VariableTypeEnum,
    PrimitiveType,
    VariableDeclaration,
    VariableDefinition,
    BaseExpression,
    FunctionCall,
    VariableAccess,
    Constant,
    ConstantType,
    OperatorExpression,
    VariableAssign,
    Function,
    Loop,
    If,
    Return,
    Continue,
    Break,
)
from xlang.xl_types import typeify, is_type_compatible, primitive_type_from_constant
from typing import Optional


class ScopeStack:
    def __init__(self):
        self.stack = [{}]

    def def_variable(self, name: str, variable_type: VariableType):
        if name in self.stack[-1]:
            raise Exception(f"Variable {name} already defined")
        self.stack[-1][name] = variable_type

    def get_variable_type(self, name: str) -> Optional[VariableType]:
        for stack in reversed(self.stack):
            if name in stack:
                return stack[name]
        return None  # variable not found

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        self.stack.pop()


class Typeifier:
    def __init__(self, global_scope: GlobalScope, function: Function):
        self.global_scope = global_scope
        self.scope_stack = ScopeStack()
        self.function = function
        self.inside_loop = False

    def statements(self, statements):
        for statement in statements:
            self.statement(statement)

    def statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            statement.variable_type = typeify(
                statement.variable_type, self.global_scope
            )
            self.scope_stack.def_variable(statement.name, statement.variable_type)
        elif isinstance(statement, VariableDefinition):
            statement.variable_type = typeify(
                statement.variable_type, self.global_scope
            )
            self.scope_stack.def_variable(statement.name, statement.variable_type)
            value_type = self.expression(statement.value)
            if not is_type_compatible(statement.variable_type, value_type):
                raise Exception("Incompatible value type")
        elif isinstance(statement, VariableAssign):
            value_type = self.expression(statement.value)
            variable_type = self.scope_stack.get_variable_type(
                statement.variable_access.variable_name
            )
            if not variable_type:
                raise Exception(f"Unknown variable {statement.name}")
            if not is_type_compatible(value_type, variable_type):
                raise Exception("Incompatible value type")
        elif isinstance(statement, FunctionCall):
            self.function_call(statement)
        elif isinstance(statement, Loop):
            inner_loop = self.inside_loop
            self.inside_loop = True
            self.scope_stack.push_scope()
            self.statements(statement.statements)
            self.scope_stack.pop_scope()
            if not inner_loop:
                self.inside_loop = False
        elif isinstance(statement, If):
            value_type = self.expression(statement.condition)
            # todo: check if value_type is bool or convertable to bool
            self.scope_stack.push_scope()
            self.statements(statement.statements)
            self.scope_stack.pop_scope()
        elif isinstance(statement, Return):
            if statement.value:
                if not self.function.return_type:
                    raise Exception(
                        f"Function has no return type: {self.function.name}"
                    )
                value_type = self.expression(statement.value)
                if not is_type_compatible(self.function.return_type, value_type):
                    raise Exception(
                        "Returned value is incompatible with function return type"
                    )
        elif isinstance(statement, Continue):
            if not self.inside_loop:
                raise Exception("Continue outside loop")
        elif isinstance(statement, Break):
            if not self.inside_loop:
                raise Exception("Break outside loop")
        else:
            raise Exception("Unhandled statement")

    def expression(self, expression: BaseExpression):
        if isinstance(expression, FunctionCall):
            expression.type = self.function_call(expression)
        elif isinstance(expression, VariableAccess):
            if expression.variable_access is not None:
                raise NotImplementedError("Recursive variable access not implemented")
            if expression.array_access is not None:
                raise NotImplementedError("Array access not implemented")

            variable_type = self.scope_stack.get_variable_type(expression.variable_name)
            if not variable_type:
                raise Exception(f"Unknown variable {expression.variable_name}")
            expression.type = variable_type

        elif isinstance(expression, Constant):
            if expression.constant_type == ConstantType.STRING:
                expression.type = VariableType(
                    VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.STRING
                )
            elif expression.constant_type == ConstantType.FLOAT:
                expression.type = VariableType(
                    VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.FLOAT
                )
            elif expression.constant_type == ConstantType.BOOL:
                expression.type = VariableType(
                    VariableTypeEnum.PRIMITIVE, primitive_type=PrimitiveType.BOOL
                )
            elif expression.constant_type == ConstantType.INTEGER:
                expression.type = primitive_type_from_constant(expression.value)
            else:
                raise Exception("Internal compiler error: Unknown constant type")

        elif isinstance(expression, OperatorExpression):
            operand1_type = self.expression(expression.operand1)
            operand2_type = self.expression(expression.operand2)
            if not is_type_compatible(operand1_type, operand2_type):
                raise Exception("Incompatible type in operator expressions")
            expression.type = operand1_type
        else:
            raise Exception("Unknown expression")
        return expression.type

    def function_call(self, expression):
        # check if function actually exists
        if not expression.function_name in self.global_scope.functions:
            raise Exception(f"Unknown function called: {expression.function_name}")
        function = self.global_scope.functions[expression.function_name]

        # check correct count of params given in call
        if len(expression.params) != len(function.function_params):
            raise Exception(
                f"function {expression.function_name} takes {len(function.function_params)} params,"
                f"{len(expression.params)} given"
            )

        # evaluate parameters and check if type matches
        for (param, param_type_name) in zip(
            expression.params, function.function_params
        ):
            expression_type = self.expression(param)
            if not is_type_compatible(param_type_name.param_type, expression_type):
                raise Exception("Invalid function parameter type")
        return function.return_type


def validation_pass(global_scope: GlobalScope):
    for struct in global_scope.structs.values():
        for member in struct.members:
            member.param_type = typeify(member.param_type, global_scope)

    for function in global_scope.functions.values():
        if function.return_type:
            function.return_type = typeify(function.return_type, global_scope)
        for parameter in function.function_params:
            parameter.param_type = typeify(parameter.param_type, global_scope)

    for function in global_scope.functions.values():
        typeifier = Typeifier(global_scope, function)
        typeifier.statements(function.statements)
