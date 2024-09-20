import re
from typing import List, Optional

from xlang.xl_ast import ParseContext


# Compiler implementation error, e.g. not handling all cases in an enum
class InternalCompilerError(Exception):
    pass


class ContextException(Exception):
    context: ParseContext
    function_name: Optional[str] = None
    function_parse_context: Optional[ParseContext] = None

    def __init__(self, message: str, context: ParseContext):
        super().__init__(message)
        self.context = context

    def _format_context(self, file_name: str, context: ParseContext):
        return f"{file_name}:{context.line}:{context.column}"

    def print(self, code, file_name="<source>"):
        lines = code.split("\n")

        if self.function_name:
            if self.function_parse_context:
                print(
                    f"In function {self.function_name} @",
                    self._format_context(file_name, self.function_parse_context),
                )
            else:
                print(f"In function {self.function_name}:")

        print(self._format_context(file_name, self.context), str(self))

        start_line = max(0, self.context.line - 5)
        for line in lines[start_line : self.context.line]:
            print(line)
        print(" " * (self.context.column - 1), "^", sep="")


class BaseParseException(ContextException):
    expected_tokens: List[str] = []

    def print(self, code, file_name="<source>"):
        super().print(code, file_name)
        if self.expected_tokens:
            if len(self.expected_tokens) == 1:
                print(f'Expected token "{self.expected_tokens[0]}"')
            else:
                print("Expected one of:")
                for token in self.expected_tokens:
                    print(f"* {token}")

    def process_expected_token(self, ex, accept):
        if ex._terminals_by_name and accept in ex._terminals_by_name:
            terminal = ex._terminals_by_name[accept]
            pattern = terminal.pattern.value
            if len(pattern) == 1 or len(pattern) == 2 or re.match("[a-zA-Z]+", pattern):
                self.expected_tokens.append(pattern)
            else:
                self.expected_tokens.append(terminal.name)

        else:
            self.expected_tokens.append(accept)


class UnexpectedTokenException(BaseParseException):
    def __init__(self, ex):
        super().__init__(
            f'Unexpected token "{ex.token.value}"', ParseContext.from_exception(ex)
        )

        # modeled after UnexpectedInput._format_expected
        accepts = ex.accepts or ex.expected
        for accept in accepts:
            self.process_expected_token(ex, accept)


class UnexpectedCharacterException(BaseParseException):
    def __init__(self, ex):
        super().__init__(f'Cannot parse "{ex.char}"', ParseContext.from_exception(ex))

        # modeled after UnexpectedInput._format_expected
        for accept in ex.allowed:
            self.process_expected_token(ex, accept)


class InterpreterAssertionError(ContextException):
    pass


class FunctionAlreadyDefinedException(ContextException):
    pass


class StructAlreadyDefinedException(ContextException):
    pass


class EnumAlreadyDefinedException(ContextException):
    pass


class TypeMismatchException(ContextException):
    pass
