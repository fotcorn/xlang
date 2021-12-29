import pytest
from xlang.parser import Parser
from xlang.xl_ast import GlobalScope
from xlang.interpreter import Interpreter
from xlang.validation_pass import validation_pass


@pytest.fixture
def parser():
    return Parser()


def run(code):
    parser = Parser()
    ast: GlobalScope = parser.parse(code)
    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)
