from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.validation_pass import validation_pass


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        main() {
            printi(5);
            printi(5 + 1024);
        }
        """
    )

    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)
