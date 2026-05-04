from typing import List

from xlang.exceptions import ContextException
from xlang.xl_ast import BaseExpression, FunctionCall, FunctionParameter


def bind_call_arguments(
    expression: FunctionCall,
    function_params: List[FunctionParameter],
    function_name: str,
) -> List[tuple[BaseExpression, FunctionParameter]]:
    positional_params = [param for param in function_params if param.positional_only]
    keyword_params = [param for param in function_params if not param.positional_only]
    keyword_params_by_name = {param.name: param for param in keyword_params}
    positional_param_names = {param.name for param in positional_params}

    bound_arguments = []
    positional_args = []
    keyword_args = {}
    seen_keyword_argument = False

    for argument in expression.params:
        if argument.name is None:
            if seen_keyword_argument:
                raise ContextException(
                    "Positional arguments must appear before keyword arguments",
                    argument.context,
                )
            positional_args.append(argument)
            continue
        seen_keyword_argument = True
        if argument.name in keyword_args:
            raise ContextException(
                f"Duplicate keyword argument: {argument.name}",
                argument.context,
            )
        if argument.name in positional_param_names:
            raise ContextException(
                f"Positional-only parameter '{argument.name}' cannot be passed by keyword",
                argument.context,
            )
        if argument.name not in keyword_params_by_name:
            raise ContextException(
                f"Unknown keyword argument: {argument.name}",
                argument.context,
            )
        keyword_args[argument.name] = argument

    if len(positional_args) > len(positional_params):
        raise ContextException(
            f"function {function_name} takes at most "
            f"{len(positional_params)} positional arguments, "
            f"{len(positional_args)} given",
            expression.context,
        )

    for index, parameter in enumerate(positional_params):
        if index < len(positional_args):
            bound_arguments.append((positional_args[index].value, parameter))
        elif parameter.default_value is not None:
            bound_arguments.append((parameter.default_value, parameter))
        else:
            raise ContextException(
                f"Missing required positional argument: {parameter.name}",
                expression.context,
            )

    for parameter in keyword_params:
        if parameter.name in keyword_args:
            bound_arguments.append((keyword_args[parameter.name].value, parameter))
        elif parameter.default_value is not None:
            bound_arguments.append((parameter.default_value, parameter))
        else:
            raise ContextException(
                f"Missing required keyword argument: {parameter.name}",
                expression.context,
            )

    return bound_arguments
