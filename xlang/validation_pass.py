from typing import Optional

from xlang.xl_ast import (
    ParseContext,
    VariableType,
    GlobalScope,
    VariableTypeEnum,
    PrimitiveType,
    INTEGER_TYPES,
    VariableDeclaration,
    VariableDefinition,
    BaseExpression,
    FunctionCall,
    VariableAccess,
    Constant,
    ConstantType,
    MathOperation,
    CompareOperation,
    VariableAssign,
    Function,
    Loop,
    If,
    Return,
    Continue,
    Break,
    BuiltinFunction,
)
from xlang.xl_types import typeify, is_type_compatible, primitive_type_from_constant
from xlang.exceptions import (
    ContextException,
    InternalCompilerError,
    TypeMismatchException,
)


class ScopeStack:
    def __init__(self):
        self.stack = [{}]

    def def_variable(
        self, name: str, variable_type: VariableType, context: ParseContext
    ):
        if name in self.stack[-1]:
            raise ContextException(f"Variable {name} already defined", context)
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
        for param in function.function_params:
            self.scope_stack.def_variable(param.name, param.param_type, param.context)
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
            self.scope_stack.def_variable(
                statement.name, statement.variable_type, statement.context
            )
        elif isinstance(statement, VariableDefinition):
            statement.variable_type = typeify(
                statement.variable_type, self.global_scope
            )
            self.scope_stack.def_variable(
                statement.name, statement.variable_type, statement.context
            )
            value_type = self.expression(statement.value)
            if not is_type_compatible(statement.variable_type, value_type):
                raise TypeMismatchException(
                    "Incompatible value type", statement.context
                )
        elif isinstance(statement, VariableAssign):
            value_type = self.expression(statement.value)
            variable_type = self.expression(statement.variable_access)
            if not variable_type:
                raise ContextException(
                    f"Unknown variable {statement.variable_access.variable_name}",
                    statement.context,
                )
            if not is_type_compatible(variable_type, value_type):
                raise TypeMismatchException(
                    "Incompatible value type", statement.context
                )
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
            if (
                value_type.variable_type != VariableTypeEnum.PRIMITIVE
                or value_type.primitive_type != PrimitiveType.BOOL
            ):
                raise TypeMismatchException(
                    "If statement expression is not bool", statement.condition.context
                )
            self.scope_stack.push_scope()
            self.statements(statement.statements)
            self.scope_stack.pop_scope()
            if statement.else_statement:
                self.scope_stack.push_scope()
                self.statements(statement.else_statement.statements)
                self.scope_stack.pop_scope()
            for elif_statement in statement.elif_statements:
                value_type = self.expression(elif_statement.condition)
                if (
                    value_type.variable_type != VariableTypeEnum.PRIMITIVE
                    or value_type.primitive_type != PrimitiveType.BOOL
                ):
                    raise TypeMismatchException(
                        "Elif statement expression is not bool",
                        statement.condition.context,
                    )
                self.scope_stack.push_scope()
                self.statements(elif_statement.statements)
                self.scope_stack.pop_scope()
        elif isinstance(statement, Return):
            if statement.value:
                if not self.function.return_type:
                    raise ContextException(
                        f"Function has no return type: {self.function.name}",
                        statement.context,
                    )
                value_type = self.expression(statement.value)
                if not is_type_compatible(self.function.return_type, value_type):
                    raise ContextException(
                        "Returned value is incompatible with function return type",
                        statement.context,
                    )
        elif isinstance(statement, Continue):
            if not self.inside_loop:
                raise ContextException("Continue outside loop", statement.context)
        elif isinstance(statement, Break):
            if not self.inside_loop:
                raise ContextException("Break outside loop", statement.context)
        else:
            raise InternalCompilerError("Unhandled statement")

    def struct_access(self, variable: VariableType, struct_access: VariableAccess):
        if variable.variable_type != VariableTypeEnum.STRUCT:
            raise ContextException(
                "Struct access on non-variable type", struct_access.context
            )
        assert variable.type_name
        struct_type = self.global_scope.structs[variable.type_name]

        for member in struct_type.members:
            if struct_access.variable_name == member.name:
                break
        else:
            raise ContextException(
                f"Unknown struct field: {struct_access.variable_name}",
                struct_access.context,
            )

        if struct_access.array_access is not None:
            expression_type = self.array_access(
                member.param_type, struct_access.array_access
            )
        else:
            expression_type = member.param_type

        if struct_access.variable_access:
            expression_type = self.struct_access(
                expression_type, struct_access.variable_access
            )

        return expression_type

    def array_access(self, variable_type, array_access):
        access_type = self.expression(array_access)
        if variable_type.variable_type != VariableTypeEnum.ARRAY:
            raise ContextException(
                "Array access on non-array type", array_access.context
            )
        if (
            access_type.variable_type != VariableTypeEnum.PRIMITIVE
            or access_type.primitive_type not in INTEGER_TYPES
        ):
            raise ContextException(
                "Invalid type for array access", array_access.context
            )
        return variable_type.array_type

    def expression(self, expression: BaseExpression):
        if isinstance(expression, FunctionCall):
            expression.type = self.function_call(expression)
        elif isinstance(expression, VariableAccess):
            variable_type = self.scope_stack.get_variable_type(expression.variable_name)
            if not variable_type:
                raise ContextException(
                    f"Unknown variable: {expression.variable_name}", expression.context
                )

            # handle array access
            if expression.array_access is not None:
                expression_type = self.array_access(
                    variable_type, expression.array_access
                )
            else:
                expression_type = variable_type

            # handle struct access
            if expression.variable_access is not None:
                expression_type = self.struct_access(
                    expression_type, expression.variable_access
                )

            expression.type = expression_type

        elif isinstance(expression, Constant):
            if expression.constant_type == ConstantType.STRING:
                expression.type = VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.STRING,
                )
            elif expression.constant_type == ConstantType.FLOAT:
                expression.type = VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.FLOAT,
                )
            elif expression.constant_type == ConstantType.BOOL:
                expression.type = VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.BOOL,
                )
            elif expression.constant_type == ConstantType.INTEGER:
                expression.type = primitive_type_from_constant(
                    expression.value, expression.context
                )
            else:
                raise InternalCompilerError("Unknown constant type")

        elif isinstance(expression, MathOperation):
            operand1_type = self.expression(expression.operand1)
            operand2_type = self.expression(expression.operand2)
            if is_type_compatible(operand1_type, operand2_type):
                expression.type = operand1_type
            elif is_type_compatible(operand2_type, operand1_type):
                expression.type = operand2_type
            else:
                raise ContextException(
                    "Incompatible type in operator expressions", expression.context
                )
        elif isinstance(expression, CompareOperation):
            operand1_type = self.expression(expression.operand1)
            operand2_type = self.expression(expression.operand2)
            if not is_type_compatible(
                operand1_type, operand2_type
            ) and not is_type_compatible(operand2_type, operand1_type):
                raise TypeMismatchException(
                    "Operands cannot be compared", expression.context
                )
            expression.type = VariableType(
                variable_type=VariableTypeEnum.PRIMITIVE,
                primitive_type=PrimitiveType.BOOL,
            )
        else:
            raise InternalCompilerError("Unknown expression")
        return expression.type

    def function_call(self, expression):
        # check if function actually exists
        if expression.function_name not in self.global_scope.functions:
            raise ContextException(
                f"Unknown function called: {expression.function_name}",
                expression.context,
            )
        function = self.global_scope.functions[expression.function_name]

        # check correct count of params given in call
        if len(expression.params) != len(function.function_params):
            raise ContextException(
                f"function {expression.function_name} takes "
                f"{len(function.function_params)} params, "
                f"{len(expression.params)} given",
                expression.context,
            )

        # evaluate parameters and check if type matches
        for param, param_type_name in zip(expression.params, function.function_params):
            expression_type = self.expression(param)
            if not is_type_compatible(param_type_name.param_type, expression_type):
                raise TypeMismatchException(
                    "Invalid function parameter type", param.context
                )
        return function.return_type


def validation_pass(global_scope: GlobalScope):
    for struct in global_scope.structs.values():
        for member in struct.members:
            member.param_type = typeify(member.param_type, global_scope)

    for function in global_scope.functions.values():
        if isinstance(function, BuiltinFunction):
            continue
        if function.return_type:
            function.return_type = typeify(function.return_type, global_scope)
        for parameter in function.function_params:
            parameter.param_type = typeify(parameter.param_type, global_scope)

    for function in global_scope.functions.values():
        if isinstance(function, BuiltinFunction):
            continue
        assert isinstance(function, Function)
        try:
            typeifier = Typeifier(global_scope, function)
            typeifier.statements(function.statements)
        except ContextException as ex:
            ex.function_name = function.name
            ex.function_parse_context = function.context
            raise ex
