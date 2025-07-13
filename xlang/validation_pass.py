from typing import List, Optional

from xlang.xl_ast import (
    BaseFunction,
    FunctionParameter,
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
    UnaryOperation,
    VariableAssign,
    Function,
    Loop,
    If,
    Return,
    Continue,
    Break,
    StructInitialization,
)
from xlang.xl_builtins import (
    get_builtin_functions,
    get_builtin_array_methods,
    get_builtin_primitive_methods,
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
        self, name: str, variable_type: VariableType, const: bool, context: ParseContext
    ):
        if name in self.stack[-1]:
            raise ContextException(f"Variable {name} already defined", context)
        self.stack[-1][name] = (variable_type, const)

    def get_variable_type(self, name: str) -> Optional[VariableType]:
        for stack in reversed(self.stack):
            if name in stack:
                return stack[name][0]
        return None  # variable not found

    def is_const(self, name: str) -> Optional[bool]:
        for stack in reversed(self.stack):
            if name in stack:
                return stack[name][1]
        return None

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        self.stack.pop()


class Typeifier:
    def __init__(self, global_scope: GlobalScope, function: Function):
        self.global_scope = global_scope
        self.scope_stack = ScopeStack()
        for param in function.function_params:
            # Params are const by default, except reference params.
            self.scope_stack.def_variable(
                param.name, param.param_type, not param.reference, param.context
            )
        self.function = function
        self.inside_loop = False

    def statements(self, statements):
        for statement in statements:
            self.statement(statement)

    def statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            statement.variable_type = typeify(
                statement.variable_type, self.global_scope, statement.context
            )
            self.scope_stack.def_variable(
                statement.name, statement.variable_type, False, statement.context
            )
        elif isinstance(statement, VariableDefinition):
            statement.variable_type = typeify(
                statement.variable_type, self.global_scope, statement.context
            )
            self.scope_stack.def_variable(
                statement.name,
                statement.variable_type,
                statement.const,
                statement.context,
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
            variable_name = statement.variable_access.variable_name
            if self.scope_stack.is_const(variable_name):
                raise ContextException(
                    f"Cannot assign {variable_name}, variable is const",
                    statement.context,
                )
        elif isinstance(statement, FunctionCall):
            self.function_call(statement)
        elif isinstance(statement, VariableAccess):
            current_access = statement
            while current_access.variable_access is not None:
                current_access = current_access.variable_access
            if current_access.method_call is None:
                raise ContextException(
                    "Variable access as statement must end with a method call",
                    statement.context,
                )
            self.variable_access(statement)
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
                        elif_statement.condition.context,
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

    def variable_access(self, variable_access: VariableAccess):
        variable_type = self.scope_stack.get_variable_type(
            variable_access.variable_name
        )
        if not variable_type:
            variable_type = get_enum_type(variable_access, self.global_scope)
            if variable_type:
                return variable_type
        if not variable_type:
            raise ContextException(
                f"Unknown variable: {variable_access.variable_name}",
                variable_access.context,
            )

        # handle array access
        if variable_access.array_access is not None:
            expression_type = self.array_access(
                variable_type, variable_access.array_access
            )
        else:
            expression_type = variable_type

        # handle struct access
        if variable_access.variable_access is not None:
            expression_type = self.struct_access(
                expression_type, variable_access.variable_access
            )

        if variable_access.method_call is not None:
            expression_type = self.method_call(
                variable_access.method_call, expression_type
            )

        variable_access.type = expression_type
        return expression_type

    def math_operation(self, expression: MathOperation) -> VariableType:
        operand1_type = self.expression(expression.operand1)
        operand2_type = self.expression(expression.operand2)

        # TODO: We currently don't do real constant folding (replacing AST nodes),
        # we just evaluate constants for type checking purposes. Real constant folding
        # would replace the MathOperation node with a Constant node in the AST.

        # Constant folding: if both operands are constants, evaluate at compile time
        if isinstance(expression.operand1, Constant) and isinstance(
            expression.operand2, Constant
        ):
            const1, const2 = expression.operand1, expression.operand2

            # Handle integer constant folding
            if (
                const1.constant_type == ConstantType.INTEGER
                and const2.constant_type == ConstantType.INTEGER
            ):
                if expression.operator == "+":
                    result_value = const1.value + const2.value
                elif expression.operator == "-":
                    result_value = const1.value - const2.value
                elif expression.operator == "*":
                    result_value = const1.value * const2.value
                elif expression.operator == "/":
                    if const2.value == 0:
                        raise ContextException("Division by zero", expression.context)
                    result_value = const1.value // const2.value  # Integer division
                elif expression.operator == "%":
                    if const2.value == 0:
                        raise ContextException("Division by zero", expression.context)
                    result_value = const1.value % const2.value
                else:
                    raise InternalCompilerError(
                        f"Unknown math operator: {expression.operator}"
                    )

                return primitive_type_from_constant(result_value, expression.context)

            # Handle float constant folding
            elif (
                const1.constant_type == ConstantType.FLOAT
                and const2.constant_type == ConstantType.FLOAT
            ):
                val1 = float(const1.value)
                val2 = float(const2.value)

                if expression.operator == "+":
                    result_value = val1 + val2
                elif expression.operator == "-":
                    result_value = val1 - val2
                elif expression.operator == "*":
                    result_value = val1 * val2
                elif expression.operator == "/":
                    if val2 == 0.0:
                        raise ContextException("Division by zero", expression.context)
                    result_value = val1 / val2
                elif expression.operator == "%":
                    if val2 == 0.0:
                        raise ContextException("Division by zero", expression.context)
                    result_value = val1 % val2
                else:
                    raise InternalCompilerError(
                        f"Unknown math operator: {expression.operator}"
                    )

                return VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.F32,
                )
            else:
                # Mixed types that can't be folded, fall back to normal type checking
                if is_type_compatible(operand1_type, operand2_type):
                    return operand1_type
                elif is_type_compatible(operand2_type, operand1_type):
                    return operand2_type
                else:
                    raise ContextException(
                        "Incompatible type in operator expressions", expression.context
                    )
        else:
            # Normal type compatibility checking for non-constant expressions
            if is_type_compatible(operand1_type, operand2_type):
                return operand1_type
            elif is_type_compatible(operand2_type, operand1_type):
                return operand2_type
            else:
                raise ContextException(
                    "Incompatible type in operator expressions", expression.context
                )

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

    def array_access(self, variable_type: VariableType, array_access: BaseExpression):
        access_type = self.expression(array_access)
        if variable_type.variable_type == VariableTypeEnum.ARRAY:
            if (
                access_type.variable_type != VariableTypeEnum.PRIMITIVE
                or access_type.primitive_type not in INTEGER_TYPES
            ):
                raise TypeMismatchException(
                    "Array index must be an integer",
                    array_access.context,
                )
            return variable_type.array_type
        elif (
            variable_type.variable_type == VariableTypeEnum.PRIMITIVE
            and variable_type.primitive_type == PrimitiveType.STRING
        ):
            if (
                access_type.variable_type != VariableTypeEnum.PRIMITIVE
                or access_type.primitive_type not in INTEGER_TYPES
            ):
                raise TypeMismatchException(
                    "String index must be an integer",
                    array_access.context,
                )
            return VariableType(
                variable_type=VariableTypeEnum.PRIMITIVE,
                primitive_type=PrimitiveType.CHAR,
            )
        else:
            raise TypeMismatchException(
                "Indexing not supported for this type",
                array_access.context,
            )

    def expression(self, expression: BaseExpression):
        if isinstance(expression, FunctionCall):
            expression.type = self.function_call(expression)
        elif isinstance(expression, VariableAccess):
            expression.type = self.variable_access(expression)
        elif isinstance(expression, Constant):
            expression.type = get_constant_type(expression)
        elif isinstance(expression, MathOperation):
            expression.type = self.math_operation(expression)
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
        elif isinstance(expression, UnaryOperation):
            operand_type = self.expression(expression.operand)
            if expression.operator == "not":
                if (
                    operand_type.variable_type != VariableTypeEnum.PRIMITIVE
                    or operand_type.primitive_type != PrimitiveType.BOOL
                ):
                    raise TypeMismatchException(
                        "not operator only works on bool values", expression.context
                    )
                expression.type = VariableType(
                    variable_type=VariableTypeEnum.PRIMITIVE,
                    primitive_type=PrimitiveType.BOOL,
                )
            elif expression.operator == "-":
                if operand_type.variable_type != VariableTypeEnum.PRIMITIVE:
                    raise TypeMismatchException(
                        "unary minus operator only works on primitive numeric types",
                        expression.context,
                    )
                # Only allow signed integer types and f32
                allowed_types = (
                    PrimitiveType.I8,
                    PrimitiveType.I16,
                    PrimitiveType.I32,
                    PrimitiveType.I64,
                    PrimitiveType.F32,
                )
                if operand_type.primitive_type not in allowed_types:
                    if operand_type.primitive_type in (
                        PrimitiveType.U8,
                        PrimitiveType.U16,
                        PrimitiveType.U32,
                        PrimitiveType.U64,
                    ):
                        raise TypeMismatchException(
                            "unary minus operator cannot be used with unsigned integer types",
                            expression.context,
                        )
                    else:
                        raise TypeMismatchException(
                            "unary minus operator only works on signed integers and f32",
                            expression.context,
                        )
                # Result type is the same as operand type
                expression.type = operand_type
            else:
                raise InternalCompilerError(
                    f"Unknown unary operator: {expression.operator}"
                )
        elif isinstance(expression, StructInitialization):
            expression.type = self.struct_initialization(expression)
        else:
            raise InternalCompilerError("Unknown expression")
        return expression.type

    def function_call(self, expression: FunctionCall):
        # check if function actually exists
        function: BaseFunction
        if expression.function_name in self.global_scope.functions:
            function = self.global_scope.functions[expression.function_name]
        elif expression.function_name in get_builtin_functions():
            function = get_builtin_functions()[expression.function_name]
        else:
            raise ContextException(
                f"Unknown function called: {expression.function_name}",
                expression.context,
            )
        self.check_call_arguments(expression, function.function_params)
        return function.return_type

    def check_call_arguments(
        self,
        expression: FunctionCall,
        function_params: List[FunctionParameter],
    ):
        # check correct count of params given in call
        if len(expression.params) != len(function_params):
            raise ContextException(
                f"function {expression.function_name} takes "
                f"{len(function_params)} params, "
                f"{len(expression.params)} given",
                expression.context,
            )

        # evaluate parameters and check if type matches
        for param_expr, param_type in zip(expression.params, function_params):
            if param_type.reference:
                if not isinstance(param_expr, VariableAccess):
                    raise TypeMismatchException(
                        "Only variables allowed for reference parameters",
                        param_expr.context,
                    )
                if self.scope_stack.is_const(param_expr.variable_name):
                    raise ContextException(
                        "Variables passed as reference parameters cannot be const",
                        param_expr.context,
                    )
            expression_type = self.expression(param_expr)
            if not is_type_compatible(param_type.param_type, expression_type):
                raise TypeMismatchException(
                    f"Invalid function parameter type. Expected {param_type.param_type}, but got {expression_type}",
                    param_expr.context,
                )

    def method_call(self, method_call: FunctionCall, variable_type: VariableType):
        method_name = method_call.function_name

        if variable_type.variable_type == VariableTypeEnum.ARRAY:
            methods = get_builtin_array_methods()
            if method_name not in methods:
                raise ContextException(
                    f"Unknown array method: {method_name}",
                    method_call.context,
                )
            method = methods[method_name]
        elif variable_type.variable_type == VariableTypeEnum.PRIMITIVE:
            primitive_methods = get_builtin_primitive_methods()
            if (
                variable_type.primitive_type not in primitive_methods
                or method_name not in primitive_methods[variable_type.primitive_type]
            ):
                raise ContextException(
                    f"Unknown primitive method: {method_name} for type {variable_type.primitive_type}",
                    method_call.context,
                )
            method = primitive_methods[variable_type.primitive_type][method_name]
        elif variable_type.variable_type == VariableTypeEnum.ENUM:
            raise ContextException(
                f"Enum types do not support method calls: {method_name}",
                method_call.context,
            )
        elif variable_type.variable_type == VariableTypeEnum.STRUCT:
            raise ContextException(
                f"Struct methods are not currently supported: {variable_type}",
                method_call.context,
            )
        else:
            raise ContextException(
                f"Method calls not supported for this type: {variable_type}",
                method_call.context,
            )

        self.check_call_arguments(method_call, method.function_params)
        return method.return_type

    def struct_initialization(self, expression: StructInitialization):
        # Check if struct exists
        if expression.struct_name not in self.global_scope.structs:
            raise ContextException(
                f"Unknown struct: {expression.struct_name}",
                expression.context,
            )

        struct_type = self.global_scope.structs[expression.struct_name]

        # Create a map of field names to their types for quick lookup
        struct_fields = {member.name: member for member in struct_type.members}

        # Track which fields have been initialized
        initialized_fields = set()

        # Validate each field initialization
        for field_init in expression.field_inits:
            field_name = field_init.field_name

            # Check if field exists in struct
            if field_name not in struct_fields:
                raise ContextException(
                    f"Unknown field '{field_name}' in struct '{expression.struct_name}'",
                    field_init.context,
                )

            # Check for duplicate field initialization
            if field_name in initialized_fields:
                raise ContextException(
                    f"Field '{field_name}' is initialized multiple times",
                    field_init.context,
                )

            initialized_fields.add(field_name)

            # Type check the field value
            field_type = struct_fields[field_name].param_type
            value_type = self.expression(field_init.value)

            if not is_type_compatible(field_type, value_type):
                raise TypeMismatchException(
                    f"Field '{field_name}' expects type {field_type}, got {value_type}",
                    field_init.context,
                )

        # Check if all required fields are initialized
        # Only enum fields without explicit defaults must be initialized
        # Other types (primitives, structs) get automatic default values
        for member in struct_type.members:
            if (
                member.name not in initialized_fields
                and member.default_value is None
                and member.param_type.variable_type == VariableTypeEnum.ENUM
            ):
                raise ContextException(
                    f"Enum field '{member.name}' must be explicitly initialized",
                    expression.context,
                )

        # Return the struct type
        return VariableType(
            variable_type=VariableTypeEnum.STRUCT,
            type_name=expression.struct_name,
        )


def get_constant_type(constant: Constant) -> VariableType:
    if constant.constant_type == ConstantType.STRING:
        return VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=PrimitiveType.STRING,
        )
    elif constant.constant_type == ConstantType.FLOAT:
        return VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=PrimitiveType.F32,
        )
    elif constant.constant_type == ConstantType.BOOL:
        return VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=PrimitiveType.BOOL,
        )
    elif constant.constant_type == ConstantType.CHAR:
        return VariableType(
            variable_type=VariableTypeEnum.PRIMITIVE,
            primitive_type=PrimitiveType.CHAR,
        )
    elif constant.constant_type == ConstantType.INTEGER:
        return primitive_type_from_constant(constant.value, constant.context)
    else:
        raise InternalCompilerError("Unknown constant type")


def get_enum_type(
    variable_access: VariableAccess, global_scope: GlobalScope
) -> Optional[VariableType]:
    enum_type = global_scope.enums.get(variable_access.variable_name)
    if not enum_type:
        return None
    if variable_access.variable_access is None:
        raise ContextException(
            "Enum access must specify a member", variable_access.context
        )
    enum_member_name = variable_access.variable_access.variable_name
    if enum_member_name not in enum_type.entries:
        raise ContextException(
            f"Unknown enum member: {enum_member_name}",
            variable_access.context,
        )
    return VariableType(variable_type=VariableTypeEnum.ENUM, type_name=enum_type.name)


def validation_pass(global_scope: GlobalScope):
    for struct in global_scope.structs.values():
        for member in struct.members:
            member.param_type = typeify(member.param_type, global_scope, member.context)
            if member.default_value:
                if isinstance(member.default_value, Constant):
                    value_type = get_constant_type(member.default_value)
                elif isinstance(member.default_value, VariableAccess):
                    enum_type = get_enum_type(member.default_value, global_scope)
                    if enum_type is None:
                        raise ContextException(
                            f"Unknown enum type: {member.default_value.variable_name}",
                            member.default_value.context,
                        )
                    value_type = enum_type
                else:
                    raise ContextException(
                        f"Invalid default value type: {type(member.default_value)}",
                        member.default_value.context,
                    )
                if not is_type_compatible(member.param_type, value_type):
                    raise TypeMismatchException(
                        f"Default value type mismatch for struct member {member.name}",
                        member.default_value.context,
                    )
                member.default_value.type = value_type
            else:
                # Check if enum field lacks required default value
                if member.param_type.variable_type == VariableTypeEnum.ENUM:
                    raise ContextException(
                        f"Enum field '{member.name}' in struct '{struct.name}' must have a default value",
                        member.context,
                    )

    for function in global_scope.functions.values():
        if function.return_type:
            function.return_type = typeify(
                function.return_type, global_scope, function.context
            )
        for parameter in function.function_params:
            parameter.param_type = typeify(
                parameter.param_type, global_scope, parameter.context
            )

    for function in global_scope.functions.values():
        assert isinstance(function, Function)
        try:
            typeifier = Typeifier(global_scope, function)
            typeifier.statements(function.statements)
        except ContextException as ex:
            ex.function_name = function.name
            ex.function_parse_context = function.context
            raise ex
