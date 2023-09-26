import argparse
import sys
import re

from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.xl_ast import GlobalScope
from xlang.validation_pass import validation_pass
from xlang.exceptions import ContextException


def run(code: str):
    try:
        parser = Parser()
        ast: GlobalScope = parser.parse(code)
        validation_pass(ast)
        interpreter = Interpreter()
        interpreter.run(ast)
    except ContextException as ex:
        ex.print(code, args.file)
        sys.exit(1)
    except Exception as ex:
        print(ex)
        sys.exit(1)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="xlang interpreter")
    arg_parser.add_argument("file")
    arg_parser.add_argument("--split-input-file", action="store_true")

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
            run(chunk)
    else:
        run(code)
