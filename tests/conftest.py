import pytest
from xlang.parser import Parser
from xlang.xl_ast import GlobalScope
from xlang.interpreter import Interpreter
from xlang.validation_pass import validation_pass
from xlang.exceptions import ContextException


@pytest.fixture
def parser():
    return Parser()


def parse(code):
    parser = Parser()
    try:
        parser.parse(code)
    except ContextException as ex:
        ex.print(code)
        raise ex


def run(code):
    try:
        parser = Parser()
        ast: GlobalScope = parser.parse(code)
        validation_pass(ast)
        interpreter = Interpreter()
        interpreter.run(ast)
    except ContextException as ex:
        ex.print(code)
        raise ex
