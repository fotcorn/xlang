from lark import Transformer, v_args

from xlang.xl_ast import (
    Break,
    Continue,
    Constant,
    ConstantType,
    FunctionCall,
    Function,
    GlobalScope,
    Loop,
    If,
    VariableDefinition,
    VariableAccess,
    VariableAssign,
    OperatorExpression,
    Return,
)


class ASTTransformer(Transformer):
    @v_args(inline=True)
    def integer_constant(self, value):
        return Constant(ConstantType.INTEGER, int(value))

    def function_call(self, param):
        return FunctionCall(param[0].value, param[1:])

    @v_args(inline=True)
    def function_def(self, name, code_block):
        return Function(name.value, code_block.children)

    @v_args(inline=True)
    def loop(self, code_block):
        return Loop(code_block.children)

    def translation_unit(self, entries):
        global_scope = GlobalScope()
        for entry in entries:
            if isinstance(entry, Function):
                global_scope.functions[entry.name] = entry
        return global_scope

    @v_args(inline=True)
    def variable_def(self, name, var_type, value):
        return VariableDefinition(
            name.value, "".join([t.value for t in var_type.children]), value
        )

    @v_args(inline=True)
    def variable_assign(self, name, value):
        return VariableAssign(name, value)

    @v_args(inline=True)
    def compare_expr(self, op1, operator, op2):
        return OperatorExpression(op1, op2, operator.value)

    @v_args(inline=True)
    def add_sub_expr(self, op1, operator, op2):
        return OperatorExpression(op1, op2, operator.value)

    @v_args(inline=True)
    def mul_div_expr(self, op1, operator, op2):
        return OperatorExpression(op1, op2, operator.value)

    @v_args(inline=True)
    def if_statement(self, compare_expr, code_block):
        return If(compare_expr, code_block.children)

    @v_args(inline=True)
    def control(self, keyword, return_value=None):
        if keyword == 'break':
            return Break()
        elif keyword == 'continue':
            return Continue()
        elif keyword == 'return':
            return Return(return_value)
        else:
            raise Exception('Unknown control keyword')

    @v_args(inline=True)
    def var_access(self, variable, *args):
        assert len(args) in range(0, 3)
        if len(args) == 2:
            array_access, variable_access = args
        elif len(args) == 0:
            array_access, variable_access = None, None
        elif isinstance(args[0], VariableAccess):
            array_access, variable_access = None, args[0]
        else:
            array_access, variable_access = args[0], None

        if array_access:
            array_access = array_access.children[0]
        # if len(params) != 1:
        #    print(params)
        ##    # TODO: implement array and struct access
        #    raise NotImplementedError("struct and array access not implemented")
        # print(params[0].value)
        # raise Exception("bla
        return VariableAccess(variable.value, array_access, variable_access)
