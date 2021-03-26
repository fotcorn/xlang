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

            if (true) {
                prints("true is true");
            }
            if (false) {
                prints("false is false");
            }
            if (a == 5) {
                prints("a is 5!");
            }
            if (a != 4) {
                prints("a is not 4!");
            }
            if (a > 2) {
                prints("a is bigger than 2!");
            }
        }
        """
    )

    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)
