from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.validation_pass import validation_pass


def test_hello(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct A {
            a: int,
            b: int,
        }
        test() {
            prints("Hello from function");
        }
        main() {
            printi(5);
            printi(5 + 1024);
            a: int = 5;
            b: int;
            c: A;
            printi(a);
            printi(a + 3);
            printi(7 + a);
            str: string = "Hello World!";
            prints(str);
            test();
            prints("Hello from main");
        }
        """
    )

    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)
