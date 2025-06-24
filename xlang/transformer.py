import lark # Added import
from lark import Transformer, v_args

from xlang.exceptions import (
    FunctionAlreadyDefinedException,
    InternalCompilerError,
    StructAlreadyDefinedException,
    EnumAlreadyDefinedException,
    ContextException,
)
from xlang.xl_ast import (
    ArrayAccess,
    Break,
    StructInitializer,
    StructInitializerMember,
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
    UnaryOperation,
    VariableAccess,
    VariableAssign,
    VariableDeclaration,
    VariableDefinition,
    VariableType,
    VariableTypeEnum,
    EnumType,
    EnumEntry,
)


class ASTTransformer(Transformer):
    @v_args(inline=True)
    def integer_constant(self, value):
        return Constant(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.INTEGER,
            value=int(value.value),
        )

    @v_args(inline=True)
    def float_constant(self, value):
        return Constant(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.FLOAT,
            value=float(value.value),
        )

    @v_args(inline=True)
    def string_literal(self, value):
        string_content = value.value[1:-1]  # Remove quotes

        # Handle escape sequences
        result = ""
        i = 0
        while i < len(string_content):
            if string_content[i] == "\\" and i + 1 < len(string_content):
                escape_char = string_content[i + 1]
                if escape_char == "t":
                    result += "\t"
                elif escape_char == "n":
                    result += "\n"
                elif escape_char == "r":
                    result += "\r"
                elif escape_char == '"':
                    result += '"'
                elif escape_char == "\\":
                    result += "\\"
                elif escape_char == "0":
                    result += "\0"
                else:
                    raise InternalCompilerError("Unhandled escape sequence")
                i += 2  # Skip both the backslash and escape character
            else:
                result += string_content[i]
                i += 1

        return Constant(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.STRING,
            value=result,
        )

    @v_args(inline=True)
    def boolean_literal(self, value):
        return Constant(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.BOOL,
            value=value.value == "true",
        )

    @v_args(inline=True)
    def char_literal(self, value):
        char_content = value.value[1:-1]  # Remove quotes

        # Handle escape sequences
        if len(char_content) == 2 and char_content[0] == "\\":
            escape_char = char_content[1]
            if escape_char == "t":
                char_content = "\t"
            elif escape_char == "n":
                char_content = "\n"
            elif escape_char == "r":
                char_content = "\r"
            elif escape_char == "'":
                char_content = "'"
            elif escape_char == "\\":
                char_content = "\\"
            elif escape_char == "0":
                char_content = "\0"
            else:
                raise InternalCompilerError("Unhandled escape sequence")

        return Constant(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(value),
            constant_type=ConstantType.CHAR,
            value=char_content,
        )

    def function_call(self, param):
        return FunctionCall(
            type=None,
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
        params = params[1:-1]
        return_type = None
        function_params = None
        if len(params) == 1:
            if isinstance(params[0], list):
                function_params = params[0]
            else:
                return_type = params[0]
        elif len(params) == 2:
            function_params = params[0]
            return_type = params[1]

        if function_params is None:
            function_params = []

        return Function(
            name=name.value,
            return_type=return_type,
            function_params=function_params,
            statements=code_block.children,
            context=ParseContext.from_token(name),
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
    def struct_entry(self, identifier, type, *args):
        default_value = args[0] if args else None
        return IdentifierAndType(
            name=identifier.value,
            param_type=type,
            context=ParseContext.from_token(identifier),
            default_value=default_value,
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

    @v_args(inline=True)
    def enum_entry(self, identifier, comma=None):
        return EnumEntry(
            name=identifier.value, context=ParseContext.from_token(identifier)
        )

    @v_args(inline=True)
    def enum_def(self, name, *entries):
        entries_dict = {}
        for entry in entries:
            if entry.name in entries_dict:
                raise ContextException(
                    f'Duplicate enum entry "{entry.name}"', entry.context
                )
            entries_dict[entry.name] = entry
        return EnumType(
            name=name.value,
            entries=entries_dict,
            context=ParseContext.from_token(name),
        )

    def translation_unit(self, entries):
        global_scope = GlobalScope()
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
            elif isinstance(entry, EnumType):
                if entry.name in global_scope.enums:
                    raise EnumAlreadyDefinedException(
                        f'Enum with name "{entry.name}" is already defined',
                        entry.context,
                    )
                global_scope.enums[entry.name] = entry
            else:
                raise InternalCompilerError("Unknown entry in global scope")
        return global_scope

    @v_args(inline=True)
    def variable_def(self, name, var_type, value):
        return VariableDefinition(
            context=ParseContext.from_token(name),
            name=name.value,
            variable_type=var_type,
            value=value,
            const=False,
        )

    @v_args(inline=True)
    def const_def(self, name, var_type, value):
        return VariableDefinition(
            context=ParseContext.from_token(name),
            name=name.value,
            variable_type=var_type,
            value=value,
            const=True,
        )

    @v_args(inline=True)
    def variable_dec(self, name, var_type):
        return VariableDeclaration(
            context=ParseContext.from_token(name),
            name=name.value,
            variable_type=var_type,
        )

    @v_args(inline=True)
    def variable_assign(self, variable_access, value):
        return VariableAssign(
            context=variable_access.context,
            variable_access=variable_access,
            value=value,
        )

    @v_args(inline=True)
    def compare_expr(self, op1, operator, op2):
        return CompareOperation(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=op1.context,
            operand1=op1,
            operand2=op2,
            operator=operator.value,
        )

    @v_args(inline=True)
    def add_sub_expr(self, op1, operator, op2):
        return MathOperation(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=op1.context,
            operand1=op1,
            operand2=op2,
            operator=operator.value,
        )

    @v_args(inline=True)
    def mul_div_expr(self, op1, operator, op2):
        return MathOperation(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=op1.context,
            operand1=op1,
            operand2=op2,
            operator=operator.value,
        )

    @v_args(inline=True)
    def not_expr(self, operator, operand):
        return UnaryOperation(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(operator),
            operand=operand,
            operator=operator.value,
        )

    @v_args(inline=True)
    def if_statement(self, compare_expr, code_block, *elif_else):
        if len(elif_else) > 0:
            if isinstance(elif_else[-1], Else):
                return If(
                    context=compare_expr.context,
                    condition=compare_expr,
                    statements=code_block.children,
                    else_statement=elif_else[-1],
                    elif_statements=elif_else[:-1],
                )
            else:
                return If(
                    context=compare_expr.context,
                    condition=compare_expr,
                    statements=code_block.children,
                    elif_statements=elif_else,
                )
        else:
            return If(
                context=compare_expr.context,
                condition=compare_expr,
                statements=code_block.children,
            )

    @v_args(inline=True)
    def elif_statement(self, compare_expr, code_block):
        return Elif(
            context=compare_expr.context,
            condition=compare_expr,
            statements=code_block.children,
        )

    @v_args(inline=True)
    def else_statement(self, keyword, code_block):
        return Else(
            context=ParseContext.from_token(keyword), statements=code_block.children
        )

    @v_args(inline=True)
    def control(self, keyword, return_value=None):
        if keyword == "break":
            return Break(context=ParseContext.from_token(keyword))
        elif keyword == "continue":
            return Continue(context=ParseContext.from_token(keyword))
        elif keyword == "return":
            return Return(context=ParseContext.from_token(keyword), value=return_value)
        else:
            raise InternalCompilerError("Unknown control keyword")

    @v_args(inline=True)
    def array_access(self, expression):
        return ArrayAccess(type=None, expression=expression, context=expression.context)

    @v_args(inline=True)
    def var_access(self, variable, *args):
        array_access, variable_access, method_call = None, None, None
        if len(args) == 0:
            # Simple variable only.
            pass
        elif len(args) == 1:
            # Array access, variable access or method call.
            if isinstance(args[0], VariableAccess):
                variable_access = args[0]
            elif isinstance(args[0], ArrayAccess):
                array_access = args[0].expression
            elif isinstance(args[0], FunctionCall):
                method_call = args[0]
            else:
                raise InternalCompilerError("Invalid type in variable access")
        elif len(args) == 2:
            if isinstance(args[1], VariableAccess):
                array_access = args[0].expression
                variable_access = args[1]
            elif isinstance(args[1], FunctionCall):
                array_access = args[0].expression
                method_call = args[1]
            else:
                raise InternalCompilerError("Invalid type in variable access")
        else:
            raise InternalCompilerError("Invalid number of args in variable access")

        return VariableAccess(
            type=VariableType(variable_type=VariableTypeEnum.UNKNOWN),
            context=ParseContext.from_token(variable),
            variable_name=variable.value,
            array_access=array_access,
            method_call=method_call,
            variable_access=variable_access,
        )

    @v_args(inline=True)
    def struct_initializer_member(self, identifier, value):
        return StructInitializerMember(
            name=identifier.value,
            value=value,
            context=ParseContext.from_token(identifier),
        )

    def struct_initializer(self, children):
        name_token = children[0]
        members_ast_nodes = []

        # Iterate over all children after the name_token
        # Children could be StructInitializerMember nodes or Token(',')
        for child_node in children[1:]:
            if isinstance(child_node, StructInitializerMember):
                members_ast_nodes.append(child_node)
            elif isinstance(child_node, list):
                # This case handles if Lark groups (A ("," A)*) into a list.
                # Should not happen with current grammar for the members part,
                # but good to be defensive or aware.
                for item in child_node:
                    if isinstance(item, StructInitializerMember):
                        members_ast_nodes.append(item)

        # Check for duplicate members
        member_names = set()
        for member_node in members_ast_nodes:
            if member_node.name in member_names:
                raise ContextException(
                    f"Duplicate member '{member_node.name}' in struct initializer",
                    member_node.context,
                )
            member_names.add(member_node.name)

        return StructInitializer(
            type=None, # Type will be filled in by validation pass
            name=name_token.value,
            members=members_ast_nodes,
            context=ParseContext.from_token(name_token),
        )
