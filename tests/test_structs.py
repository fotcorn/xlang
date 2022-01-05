import pytest
from xlang.exceptions import StructAlreadyDefinedException

from xlang.xl_ast import GlobalScope
from xlang.parser import Parser
from xlang.validation_pass import validation_pass


def test_struct(parser: Parser):
    ast: GlobalScope = parser.parse(
        """
        struct SubStruct {
            x: int,
        }
        struct Test {
            a: int,
            b: [int],
            c: SubStruct,
            d: [SubStruct],
            e: i64,
            f: [i64],
            g: i32,
            h: [i32],
            i: i16,
            j: [i16],
            k: i8,
            l: [i8],
            m: u64,
            n: [u64],
            o: u32,
            p: [u32],
            q: u16,
            r: [u16],
            s: u8,
            t: [u8],
            u: float,
            v: [float],
            w: string,
            x: [string],
        }

        main() {
            test: Test;
            test.a = 5;
            a: int = test.a + test.b[0];
        }
        """
    )

    validation_pass(ast)

    assert len(ast.structs) == 2
    assert "main" in ast.functions


def test_duplicate_struct(parser: Parser):
    with pytest.raises(StructAlreadyDefinedException):
        parser.parse(
            """
            struct MyStruct {
                a: int,
            }
            struct MyStruct {
                b: int,
            }
            """
        )
