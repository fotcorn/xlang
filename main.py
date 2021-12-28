import argparse
import sys

from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.xl_ast import GlobalScope
from xlang.validation_pass import validation_pass


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="xlang interpreter")
    arg_parser.add_argument("file", type=str)

    args = arg_parser.parse_args()

    try:
        with open(args.file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print("Code file does not exist")
        sys.exit(1)

    parser = Parser()
    ast: GlobalScope = parser.parse(code)
    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)
