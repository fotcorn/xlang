import argparse
import sys
import re
import json

from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.xl_ast import GlobalScope
from xlang.validation_pass import validation_pass
from xlang.exceptions import ContextException, InterpreterAssertionError


def run(code: str, parse_only: bool = False):
    try:
        parser = Parser()
        ast: GlobalScope = parser.parse(code)
        validation_pass(ast)
        if parse_only:
            print(json.dumps(ast.dump(), indent=2))
        else:
            interpreter = Interpreter()
            interpreter.run(ast)
    # assert() is used in tests, so we crash here to detect failed assertions.
    # Other exceptions are fine, we check for those with // CHECK statements.
    except InterpreterAssertionError as ex:
        ex.print(code, args.file)
        sys.exit(2)
    except ContextException as ex:
        ex.print(code, args.file)
        return False
    return True


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="xlang interpreter")
    arg_parser.add_argument("file")
    arg_parser.add_argument("--split-input-file", action="store_true")
    arg_parser.add_argument("--parse-only", action="store_true")

    args = arg_parser.parse_args()

    try:
        with open(args.file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print("Code file does not exist")
        sys.exit(1)

    if args.split_input_file:
        code_chunks = re.split("^//-{3,}$", code, flags=re.MULTILINE)
        for chunk in code_chunks:
            run(chunk, args.parse_only)
    else:
        if not run(code, args.parse_only):
            sys.exit(1)
