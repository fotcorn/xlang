from lark import Transformer, v_args

from xl_ast import Constant, ConstantType, FunctionCall, Function, GlobalScope, VariableDefinition


class ASTTransformer(Transformer):
    @v_args(inline=True)
    def integer_constant(self, value):
        return Constant(ConstantType.INTEGER, int(value))

    def function_call(self, param):
        return FunctionCall(param[0].value, param[1:])

    @v_args(inline=True)
    def function_def(self, name, code_block):
        return Function(name.value, code_block.children)

    def translation_unit(self, entries):
        global_scope = GlobalScope()
        for entry in entries:
            if isinstance(entry, Function):
                global_scope.functions[entry.name] = entry
        return global_scope

    @v_args(inline=True)
    def variable_def(self, name, var_type, value):
        return VariableDefinition(name.value, ''.join([t.value for t in var_type.children]), value)
