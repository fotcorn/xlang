import copy

from xlang.exceptions import ContextException, InternalCompilerError
from xlang.interpreter_datatypes import ScopeStack, Value, ValueType
from xlang.xl_ast import (
    INTEGER_TYPES,
    NUMBER_TYPES,
    PrimitiveType,
    GlobalScope,
    VariableTypeEnum,
    VariableAccess,
    VariableDeclaration,
    VariableAssign,
    VariableDefinition,
    Loop,
    Function,
    FunctionCall,
    If,
    Return,
    Continue,
    Break,
    BaseExpression,
    MathOperation,
    CompareOperation,
    Constant,
    BuiltinFunction,
)
from xlang.xl_builtins import (
    BUILTIN_FUNCTIONS,
    get_builtin_array_methods,
    get_builtin_primitive_methods,
)


class Interpreter:
    def run(self, ast: GlobalScope):
        self.global_scope = ast
        if "main" not in ast.functions:
            raise Exception("No main function found")
        main_function = ast.functions["main"]
        self.scope_stack = ScopeStack()

        assert isinstance(main_function, Function)

        for statement in main_function.statements:
            execution_change = self.statement(statement)
            if execution_change:
                change_type, value = execution_change
                if change_type == "return":
                    break
                else:
                    raise Exception(
                        f"invalid execution change type in main function: {change_type}"
                    )

    def statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            value = self.default_variable_value(statement.variable_type)
            self.scope_stack.set_variable(statement.name, value)
        elif isinstance(statement, VariableDefinition):
            value = self.expression(statement.value)
            self.scope_stack.set_variable(statement.name, value)
        elif isinstance(statement, VariableAssign):
            value = self.expression(statement.value)
            variable = self.lookup_variable(statement.variable_access)
            if variable.type == ValueType.ENUM:
                variable.type = ValueType.ENUM
                variable.type_name = value.type_name
            else:
                variable.__dict__.update(value.__dict__)
        elif isinstance(statement, FunctionCall):
            self.function_call(statement)
        elif isinstance(statement, Loop):
            execution_change = None
            self.scope_stack.push_scope()

            counter = 0
            while True:
                execution_change = self.statement(statement.statements[counter])
                if execution_change:  # break, continue or return
                    change_type, value = execution_change
                    if change_type == "break":
                        execution_change = None
                        break
                    elif change_type == "continue":
                        counter = 0
                        execution_change = None
                        continue
                    else:  # return
                        break
                counter += 1
                if counter == len(statement.statements):
                    counter = 0

            self.scope_stack.pop_scope()
            return execution_change
        elif isinstance(statement, If):
            value = self.expression(statement.condition)
            if (
                value.type != ValueType.PRIMITIVE
                or value.primitive_type != PrimitiveType.BOOL
            ):
                raise InternalCompilerError(
                    "Returned value from if expression is not bool, "
                    "should have been checked by validation pass"
                )
            if value.value is True:
                execution_change = None
                self.scope_stack.push_scope()
                for statement in statement.statements:
                    execution_change = self.statement(statement)
                    if execution_change:  # break, continue or return
                        break
                self.scope_stack.pop_scope()
                return execution_change

            for elif_statement in statement.elif_statements:
                value = self.expression(elif_statement.condition)
                if (
                    value.type != ValueType.PRIMITIVE
                    or value.primitive_type != PrimitiveType.BOOL
                ):
                    raise InternalCompilerError(
                        "Returned value from elif expression is not bool, "
                        "should have been checked by validation pass"
                    )
                if value.value is True:
                    execution_change = None
                    self.scope_stack.push_scope()
                    for statement in elif_statement.statements:
                        execution_change = self.statement(statement)
                        if execution_change:  # break, continue or return
                            break
                    self.scope_stack.pop_scope()
                    return execution_change

            if statement.else_statement:
                execution_change = None
                self.scope_stack.push_scope()
                for statement in statement.else_statement.statements:
                    execution_change = self.statement(statement)
                    if execution_change:  # break, continue or return
                        break
                self.scope_stack.pop_scope()
                return execution_change
        elif isinstance(statement, Return):
            if statement.value:
                value = self.expression(statement.value)
            else:
                value = None
            return "return", value
        elif isinstance(statement, Continue):
            return "continue", None
        elif isinstance(statement, Break):
            return "break", None
        elif isinstance(statement, VariableAccess):
            self.lookup_variable(statement)
        else:
            raise InternalCompilerError("unhandled statement")

    def index_lookup(
        self,
        value: Value,
        array_access: BaseExpression,
    ) -> Value:
        index = self.expression(array_access)
        if value.is_array:
            if index.value < 0 or index.value >= len(value.value):
                raise Exception("Array index out of bounds")
            return value.value[index.value]
        elif (
            value.type == ValueType.PRIMITIVE
            and value.primitive_type == PrimitiveType.STRING
        ):
            if index.value < 0 or index.value >= len(value.value):
                raise Exception("String index out of bounds")
            return Value(type=value.type, value=ord(value.value[index.value]))
        else:
            raise Exception("Indexing not supported for this type")

    def struct_lookup(self, struct: Value, variable_access: VariableAccess) -> Value:
        value = struct.value[variable_access.variable_name]
        if variable_access.variable_access is not None:
            value = self.struct_lookup(value, variable_access.variable_access)

        if variable_access.array_access is not None:
            value = self.index_lookup(value, variable_access.array_access)
        return value

    def lookup_variable(self, variable_access: VariableAccess) -> Value:
        if (
            variable_access.type is not None
            and variable_access.type.variable_type == VariableTypeEnum.ENUM
            and variable_access.variable_access is not None
        ):
            enum_def = self.global_scope.enums[variable_access.variable_name]
            enum_value = enum_def.entries[
                variable_access.variable_access.variable_name
            ].name
            return Value(
                type=ValueType.ENUM,
                value=enum_value,
                type_name=variable_access.type.type_name,
            )
        else:
            value = self.scope_stack.get_variable(variable_access.variable_name)
        # handle struct access
        if variable_access.variable_access is not None:
            if value.type == ValueType.STRUCT:
                value = self.struct_lookup(value, variable_access.variable_access)

        if variable_access.array_access is not None:
            value = self.index_lookup(value, variable_access.array_access)

        if variable_access.method_call is not None:
            value = self.method_call(value, variable_access.method_call)

        return value

    def expression(self, expression: BaseExpression):
        if isinstance(expression, FunctionCall):
            return self.function_call(expression)
        elif isinstance(expression, VariableAccess):
            return self.lookup_variable(expression)
        elif isinstance(expression, Constant):
            return self.value_from_constant(expression)
        elif isinstance(expression, MathOperation):
            operand1_value = self.expression(expression.operand1)
            operand2_value = self.expression(expression.operand2)
            if (
                not operand1_value.type == ValueType.PRIMITIVE
                or operand1_value.primitive_type not in NUMBER_TYPES
                or operand1_value.is_array
            ):
                raise Exception(
                    f"{expression.operator} operator not supported on type: {operand1_value}"
                )
            if (
                not operand2_value.type == ValueType.PRIMITIVE
                or operand2_value.primitive_type not in NUMBER_TYPES
                or operand2_value.is_array
            ):
                raise Exception(
                    f"{expression.operator} operator not supported on type: {operand2_value}"
                )
            if (
                operand1_value.primitive_type == PrimitiveType.F32
                or operand2_value.primitive_type == PrimitiveType.F32
            ) and operand1_value.primitive_type != operand2_value.primitive_type:
                raise Exception(
                    f"{expression.operator} operator only works between int types"
                    " or float types, not float and int."
                )
            if expression.operator == "+":
                value = operand1_value.value + operand2_value.value
            elif expression.operator == "-":
                value = operand1_value.value - operand2_value.value
            elif expression.operator == "*":
                value = operand1_value.value * operand2_value.value
            elif expression.operator == "/":
                value = operand1_value.value // operand2_value.value
            elif expression.operator == "%":
                value = operand1_value.value % operand2_value.value
            else:
                raise InternalCompilerError("Unknown operator")
            if not expression.type:
                raise InternalCompilerError("Expression type not set")
            return Value(
                type=ValueType.PRIMITIVE,
                value=value,
                primitive_type=expression.type.primitive_type,
            )
        elif isinstance(expression, CompareOperation):
            operand1_value = self.expression(expression.operand1)
            operand2_value = self.expression(expression.operand2)

            if (
                operand1_value.type == ValueType.ENUM
                and operand2_value.type == ValueType.ENUM
            ):
                return self.enum_compare(
                    operand1_value, operand2_value, expression.operator
                )

            if (
                not operand1_value.type == ValueType.PRIMITIVE
                or operand1_value.is_array
            ):
                raise Exception(
                    f"{expression.operator} operator not supported on type: {operand1_value}"
                )
            if (
                not operand2_value.type == ValueType.PRIMITIVE
                or operand2_value.is_array
            ):
                raise Exception(
                    f"{expression.operator} operator not supported on type: {operand2_value}"
                )
            if not (
                operand1_value.primitive_type in INTEGER_TYPES
                and operand2_value.primitive_type in INTEGER_TYPES
                or operand1_value.primitive_type == operand2_value.primitive_type
            ):
                # integer types can be compared to all other integer types,
                # but string, float and bool can only compare to itself
                raise Exception(
                    "comparision operator between two incompatible primitive types: "
                    f"{operand1_value.primitive_type}, {operand2_value.primitive_type}"
                )
            if operand1_value.primitive_type in (
                PrimitiveType.STRING,
                PrimitiveType.BOOL,
            ) and expression.operator not in ("==", "!="):
                raise Exception(
                    f"invalid operator for type {operand1_value.primitive_type}"
                )
            if expression.operator == "==":
                value = operand1_value.value == operand2_value.value
            elif expression.operator == "!=":
                value = operand1_value.value != operand2_value.value
            elif expression.operator == ">=":
                value = operand1_value.value >= operand2_value.value
            elif expression.operator == ">":
                value = operand1_value.value > operand2_value.value
            elif expression.operator == "<":
                value = operand1_value.value < operand2_value.value
            elif expression.operator == "<=":
                value = operand1_value.value <= operand2_value.value
            else:
                raise InternalCompilerError("Unknown operator")
            return Value(
                type=ValueType.PRIMITIVE,
                value=value,
                primitive_type=PrimitiveType.BOOL,
            )
        else:
            raise InternalCompilerError("Unknown expression")

    def function_call(self, func_call):
        if func_call.function_name in self.global_scope.functions:
            function = self.global_scope.functions[func_call.function_name]
        elif func_call.function_name in BUILTIN_FUNCTIONS:
            function = BUILTIN_FUNCTIONS[func_call.function_name]
        else:
            raise Exception(f"Unknown function called: {func_call.function_name}")

        evaluated_params = self.evaluate_call_parameters(function, func_call)

        if isinstance(function, BuiltinFunction):
            return function.function_ptr(evaluated_params, context=func_call.context)
        else:
            old_scope_stack = self.scope_stack
            self.scope_stack = ScopeStack()
            for i, param_type in enumerate(function.function_params):
                self.scope_stack.set_variable(param_type.name, evaluated_params[i])

            return_value = None
            for statement in function.statements:
                execution_change = self.statement(statement)
                if execution_change:
                    change_type, value = execution_change
                    if change_type == "return":
                        return_value = value
                        break
                    else:
                        raise Exception(
                            f"invalid execution change type in function: {change_type}"
                        )

            self.scope_stack = old_scope_stack
            return return_value

    def method_call(self, value: Value, method_call: FunctionCall) -> Value:
        if value.is_array:
            methods = get_builtin_array_methods()
        elif value.type == ValueType.PRIMITIVE:
            methods = get_builtin_primitive_methods()[value.primitive_type]
        elif value.type == ValueType.ENUM:
            raise Exception("Method calls not supported for enum types")
        else:
            raise Exception(f"Method calls not supported for type: {value.type}")

        if method_call.function_name not in methods:
            raise Exception(f"Unknown method: {method_call.function_name}")

        method = methods[method_call.function_name]
        evaluated_params = self.evaluate_call_parameters(method, method_call)
        evaluated_params.insert(
            0, value
        )  # Add the object itself as the first parameter

        return method.function_ptr(evaluated_params, context=method_call.context)

    def enum_compare(
        self, operand1_value: Value, operand2_value: Value, operator: str
    ) -> Value:
        if operand1_value.type_name != operand2_value.type_name:
            raise Exception("Cannot compare enums of different types")
        if operator == "==":
            result = operand1_value.value == operand2_value.value
        elif operator == "!=":
            result = operand1_value.value != operand2_value.value
        else:
            raise Exception(f"Invalid operator for enum comparison: {operator}")
        return Value(
            type=ValueType.PRIMITIVE,
            value=result,
            primitive_type=PrimitiveType.BOOL,
        )

    def evaluate_call_parameters(self, function, func_call):
        evaluated_params = []
        for i, param in enumerate(func_call.params):
            is_ref_param = function.function_params[i].reference
            if is_ref_param and not isinstance(param, VariableAccess):
                raise ContextException(
                    "Reference parameters can only be variables", param.context
                )
            evaluated_param = self.expression(param)
            if not is_ref_param:
                evaluated_param = copy.deepcopy(evaluated_param)
            evaluated_params.append(evaluated_param)
        return evaluated_params

    def default_variable_value(self, variable_type):
        base_type = variable_type.variable_type
        if base_type == VariableTypeEnum.PRIMITIVE:
            primitive_type = variable_type.primitive_type
            if primitive_type in INTEGER_TYPES:
                return Value(
                    type=ValueType.PRIMITIVE, value=0, primitive_type=primitive_type
                )
            elif primitive_type == PrimitiveType.F32:
                return Value(
                    type=ValueType.PRIMITIVE, value=0.0, primitive_type=primitive_type
                )
            elif primitive_type == PrimitiveType.STRING:
                return Value(
                    type=ValueType.PRIMITIVE, value="", primitive_type=primitive_type
                )
            elif primitive_type == PrimitiveType.BOOL:
                return Value(
                    type=ValueType.PRIMITIVE, value=False, primitive_type=primitive_type
                )
            else:
                raise InternalCompilerError("primitive type not handled")
        elif base_type == VariableTypeEnum.ARRAY:
            if variable_type.array_type.variable_type == VariableTypeEnum.PRIMITIVE:
                return Value(
                    type=ValueType.PRIMITIVE,
                    value=[],
                    primitive_type=variable_type.array_type.primitive_type,
                    is_array=True,
                )
            elif variable_type.array_type.variable_type == VariableTypeEnum.STRUCT:
                return Value(
                    type=ValueType.STRUCT,
                    value=[],
                    type_name=variable_type.array_type.type_name,
                    is_array=True,
                )
            elif variable_type.array_type.variable_type == VariableTypeEnum.ENUM:
                return Value(
                    type=ValueType.ENUM,
                    value=[],
                    type_name=variable_type.array_type.type_name,
                    is_array=True,
                )
            else:
                raise NotImplementedError(
                    "array type not implemented"
                )  # multidimensional arrays
        elif base_type == VariableTypeEnum.STRUCT:
            struct_def = self.global_scope.structs[variable_type.type_name]
            struct_data = {}
            for member in struct_def.members:
                struct_data[member.name] = self.default_variable_value(
                    member.param_type
                )
            return Value(
                type=ValueType.STRUCT,
                value=struct_data,
                type_name=variable_type.type_name,
            )
        else:
            raise InternalCompilerError("Unknown variable type")

    def value_from_constant(self, constant: Constant) -> Value:
        if not constant.type:
            raise InternalCompilerError("Expression type not set")
        return Value(
            type=ValueType.PRIMITIVE,
            value=constant.value,
            primitive_type=constant.type.primitive_type,
        )
