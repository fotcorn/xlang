# Compiler implementation error, e.g. not handling all cases in an enum
from typing import Optional
from xlang.xl_ast import ParseContext


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


class InterpreterAssertionError(ContextException):
    pass
