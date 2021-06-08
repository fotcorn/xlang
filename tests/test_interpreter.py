from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.interpreter import Interpreter
from xlang.validation_pass import validation_pass


def run(code):
    parser = Parser()
    ast: GlobalScope = parser.parse(code)
    validation_pass(ast)
    interpreter = Interpreter()
    interpreter.run(ast)


def test_hello():
    run("""
        struct A {
            a: int,
            b: int,
        }
        test() {
            prints("Hello from function");
        }
        add(a: int, b: int): int {
            return a + b;
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
            printi(add(3, 4));

            i: int = 0;
            loop {
                i = i + 1;
                if (i == 5) {
                    break;
                }
                if (i == 3) {
                    continue;
                }
                printi(i);
            }
        }
    """)


def test_array():
    run("""
        main() {
            array: [int];
            appendi(array, 42);
            appendi(array, 1337);
            printi(array[0]);
            printi(array[1]);
        }
    """)
