# Compiler implementation error, e.g. not handling all cases in an enum
from xlang.xl_ast import ParseContext


class InternalCompilerError(Exception):
    pass


class ContextException(Exception):
    context: ParseContext

    def __init__(self, message: str, context: ParseContext):
        super().__init__(message)
        self.context = context

    def print(self, code):
        lines = code.split("\n")

        start_line = max(0, self.context.line - 5)

        for line in lines[start_line : self.context.line]:
            print(line)
        print(" " * (self.context.column - 1), "^", sep="")
        print(" " * (self.context.column - 1), str(self), sep="")


class InterpreterAssertionError(ContextException):
    pass
