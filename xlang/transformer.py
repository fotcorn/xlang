from lark import Transformer, v_args

from xlang.xl_ast import (
    Break,
    Continue,
    Constant,
    ConstantType,
    FunctionCall,
    FunctionParameter,
    IdentifierAndType,
    Function,
    GlobalScope,
    StructType,
    Loop,
    If,
    VariableDefinition,
    VariableDeclaration,
    VariableAccess,
    VariableAssign,
    VariableType,
    VariableTypeEnum,
    OperatorExpression,
    Return,
    BaseExpression,
)
from xlang.xl_builtins import get_builtins


class ArrayAccess:
    expression: BaseExpression


class ASTTransformer(Transformer):
    @v_args(inline=True)
    def integer_constant(self, value):
        return Constant(
            VariableType(VariableTypeEnum.UNKNOWN),
            ConstantType.INTEGER,
            int(value.value),
        )

    @v_args(inline=True)
    def string_literal(self, value):
        return Constant(
            VariableType(VariableTypeEnum.UNKNOWN),
            ConstantType.STRING,
            value.value[1:-1],
        )

    @v_args(inline=True)
    def boolean_literal(self, value):
        return Constant(
            VariableType(VariableTypeEnum.UNKNOWN),
            ConstantType.BOOL,
            value.value == "true",
        )

    def function_call(self, param):
        return FunctionCall(param[0].value, param[1:])

    @v_args(inline=True)
    def function_param(self, identifier, param_type):
        return FunctionParameter(identifier.value, param_type, False)

    def function_params(self, params):
        assert len(params) in [1, 2]
        if len(params) == 1:
            return params
        else:
            return params[0] + [params[1]]

    def function_def(self, params):
        name = params[0]
        code_block = params[-1]
        return_type = None
        function_params = None
        if len(params) == 3:
            a = params[1]
            if isinstance(params[1], list):
                function_params = params[1]
            else:
                return_type = params[1]
        elif len(params) == 4:
            function_params = params[1]
            return_type = params[2]

        if function_params is None:
            function_params = []

        return Function(name.value, return_type, function_params, code_block.children)

    def type(self, params):
        if len(params) == 1:
            return VariableType(VariableTypeEnum.UNKNOWN, params[0].value)
        elif len(params) == 3:
            assert params[0].value == "[" and params[2].value == "]"
            return VariableType(
                VariableTypeEnum.ARRAY,
                array_type=VariableType(
                    VariableTypeEnum.UNKNOWN, type_name=params[1].value
                ),
            )

    @v_args(inline=True)
    def struct_entry(self, identifier, type):
        return IdentifierAndType(identifier.value, type)

    @v_args(inline=True)
    def struct_def(self, name, *entries):
        return StructType(name.value, entries)

    @v_args(inline=True)
    def loop(self, code_block):
        return Loop(code_block.children)

    def translation_unit(self, entries):
        global_scope = GlobalScope()
        for builtin in get_builtins():
            global_scope.functions[builtin.name] = builtin
        for entry in entries:
            if isinstance(entry, Function):
                if entry.name in global_scope.functions:
                    raise Exception(
                        f"function with name {entry.name} is already defined"
                    )
                global_scope.functions[entry.name] = entry
            elif isinstance(entry, StructType):
                if entry.name in global_scope.structs:
                    raise Exception(f"struct with name {entry.name} is already defined")
                global_scope.structs[entry.name] = entry
            else:
                raise Exception(
                    "Internal compiler error: unknown entry in global scope"
                )
        return global_scope

    @v_args(inline=True)
    def variable_def(self, name, var_type, value):
        return VariableDefinition(name.value, var_type, value)

    @v_args(inline=True)
    def variable_dec(self, name, var_type):
        return VariableDeclaration(name.value, var_type)

    @v_args(inline=True)
    def variable_assign(self, variable_access, value):
        return VariableAssign(variable_access, value)

    @v_args(inline=True)
    def compare_expr(self, op1, operator, op2):
        return OperatorExpression(
            VariableType(VariableTypeEnum.UNKNOWN), op1, op2, operator.value
        )

    @v_args(inline=True)
    def add_sub_expr(self, op1, operator, op2):
        return OperatorExpression(
            VariableType(VariableTypeEnum.UNKNOWN), op1, op2, operator.value
        )

    @v_args(inline=True)
    def mul_div_expr(self, op1, operator, op2):
        return OperatorExpression(
            VariableType(VariableTypeEnum.UNKNOWN), op1, op2, operator.value
        )

    @v_args(inline=True)
    def if_statement(self, compare_expr, code_block):
        return If(compare_expr, code_block.children)

    @v_args(inline=True)
    def control(self, keyword, return_value=None):
        if keyword == "break":
            return Break()
        elif keyword == "continue":
            return Continue()
        elif keyword == "return":
            return Return(return_value)
        else:
            raise Exception("Unknown control keyword")

    @v_args(inline=True)
    def array_access(self, expression):
        aa = ArrayAccess()
        aa.expression = expression
        return aa

    @v_args(inline=True)
    def var_access(self, variable, *args):
        assert len(args) in range(0, 3)
        if len(args) == 2:
            array_access, variable_access = args[0].expression, args[1]
        elif len(args) == 0:
            array_access, variable_access = None, None
        elif isinstance(args[0], VariableAccess):
            array_access, variable_access = None, args[0]
        else:
            array_access, variable_access = args[0].expression, None

        return VariableAccess(
            VariableType(VariableTypeEnum.UNKNOWN),
            variable.value,
            array_access,
            variable_access,
        )
