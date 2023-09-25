from lark import Transformer, v_args

from xlang.exceptions import (
    FunctionAlreadyDefinedException,
    InternalCompilerError,
    StructAlreadyDefinedException,
)
from xlang.xl_ast import (
    ArrayAccess,
    Break,
    CompareOperation,
    Constant,
    ConstantType,
    Continue,
    Elif,
    Else,
    Function,
    FunctionCall,
    FunctionParameter,
    GlobalScope,
    IdentifierAndType,
    If,
    Loop,
    MathOperation,
    ParseContext,
    Return,
    StructType,
    VariableAccess,
    VariableAssign,
    VariableDeclaration,
    VariableDefinition,
    VariableType,
    VariableTypeEnum,
)
from xlang.xl_builtins import get_builtins


class ASTTransformer(Transformer):
    @v_args(inline=True)
    def integer_constant(self, value):
        return Constant(
            type=VariableType(VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.INTEGER,
            value=int(value.value),
        )

    @v_args(inline=True)
    def float_constant(self, value):
        return Constant(
            type=VariableType(VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.FLOAT,
            value=float(value.value),
        )

    @v_args(inline=True)
    def string_literal(self, value):
        return Constant(
            type=VariableType(VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.STRING,
            value=value.value[1:-1],
        )

    @v_args(inline=True)
    def boolean_literal(self, value):
        return Constant(
            type=VariableType(VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.BOOL,
            value=value.value == "true",
        )

    def function_call(self, param):
        return FunctionCall(
            function_name=param[0].value,
            params=param[1:],
            context=ParseContext.from_token(param[0]),
        )

    def function_param(self, params):
        assert len(params) in [3, 4]
        identifier = params[0]
        if len(params) == 4:
            reference = True
            param_type = params[3]
        else:
            reference = False
            param_type = params[2]
        return FunctionParameter(
            name=identifier.value,
            param_type=param_type,
            context=ParseContext.from_token(identifier),
            reference=reference,
        )

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
            if isinstance(params[1], list):
                function_params = params[1]
            else:
                return_type = params[1]
        elif len(params) == 4:
            function_params = params[1]
            return_type = params[2]

        if function_params is None:
            function_params = []

        return Function(
            name=name.value,
            return_type=return_type,
            function_params=function_params,
            statements=code_block.children,
            context=ParseContext.from_token(params[0]),
        )

    def type(self, params):
        if len(params) == 1:
            return VariableType(
                variable_type=VariableTypeEnum.UNKNOWN, type_name=params[0].value
            )
        elif len(params) == 3:
            assert params[0].value == "[" and params[2].value == "]"
            return VariableType(
                variable_type=VariableTypeEnum.ARRAY,
                array_type=VariableType(
                    variable_type=VariableTypeEnum.UNKNOWN, type_name=params[1].value
                ),
            )

    @v_args(inline=True)
    def struct_entry(self, identifier, type):
        return IdentifierAndType(
            name=identifier.value,
            param_type=type,
            context=ParseContext.from_token(identifier),
        )

    @v_args(inline=True)
    def struct_def(self, name, *entries):
        return StructType(
            name=name.value, members=entries, context=ParseContext.from_token(name)
        )

    @v_args(inline=True)
    def loop(self, keyword, code_block):
        return Loop(
            context=ParseContext.from_token(keyword), statements=code_block.children
        )

    def translation_unit(self, entries):
        global_scope = GlobalScope()
        for builtin in get_builtins():
            global_scope.functions[builtin.name] = builtin
        for entry in entries:
            if isinstance(entry, Function):
                if entry.name in global_scope.functions:
                    raise FunctionAlreadyDefinedException(
                        f'Function with name "{entry.name}" is already defined',
                        entry.context,
                    )
                global_scope.functions[entry.name] = entry
            elif isinstance(entry, StructType):
                if entry.name in global_scope.structs:
                    raise StructAlreadyDefinedException(
                        f'Struct with name "{entry.name}" is already defined',
                        entry.context,
                    )
                global_scope.structs[entry.name] = entry
            else:
                raise InternalCompilerError("Unknown entry in global scope")
        return global_scope

    @v_args(inline=True)
    def variable_def(self, name, var_type, value):
        return VariableDefinition(
            ParseContext.from_token(name), name.value, var_type, value
        )

    @v_args(inline=True)
    def variable_dec(self, name, var_type):
        return VariableDeclaration(ParseContext.from_token(name), name.value, var_type)

    @v_args(inline=True)
    def variable_assign(self, variable_access, value):
        return VariableAssign(variable_access.context, variable_access, value)

    @v_args(inline=True)
    def compare_expr(self, op1, operator, op2):
        return CompareOperation(
            VariableType(VariableTypeEnum.UNKNOWN),
            op1.context,
            op1,
            op2,
            operator.value,
        )

    @v_args(inline=True)
    def add_sub_expr(self, op1, operator, op2):
        return MathOperation(
            VariableType(VariableTypeEnum.UNKNOWN),
            op1.context,
            op1,
            op2,
            operator.value,
        )

    @v_args(inline=True)
    def mul_div_expr(self, op1, operator, op2):
        return MathOperation(
            VariableType(VariableTypeEnum.UNKNOWN),
            op1.context,
            op1,
            op2,
            operator.value,
        )

    @v_args(inline=True)
    def if_statement(self, compare_expr, code_block, *elif_else):
        if len(elif_else) > 0:
            if isinstance(elif_else[-1], Else):
                return If(
                    compare_expr.context,
                    compare_expr,
                    code_block.children,
                    else_statement=elif_else[-1],
                    elif_statements=elif_else[:-1],
                )
            else:
                return If(
                    compare_expr.context,
                    compare_expr,
                    code_block.children,
                    elif_statements=elif_else,
                )
        else:
            return If(compare_expr.context, compare_expr, code_block.children)

    @v_args(inline=True)
    def elif_statement(self, compare_expr, code_block):
        return Elif(compare_expr.context, compare_expr, code_block.children)

    @v_args(inline=True)
    def else_statement(self, keyword, code_block):
        return Else(ParseContext.from_token(keyword), code_block.children)

    @v_args(inline=True)
    def control(self, keyword, return_value=None):
        if keyword == "break":
            return Break(ParseContext.from_token(keyword))
        elif keyword == "continue":
            return Continue(ParseContext.from_token(keyword))
        elif keyword == "return":
            return Return(ParseContext.from_token(keyword), return_value)
        else:
            raise InternalCompilerError("Unknown control keyword")

    @v_args(inline=True)
    def array_access(self, expression):
        return ArrayAccess(expression, expression.context)

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
            ParseContext.from_token(variable),
            variable.value,
            array_access,
            variable_access,
        )
