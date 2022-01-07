from .conftest import validate


def test_definition():
    validate(
        """
        main() {
            array: [int];
        }
        """
    )


def test_access():
    validate(
        """
        struct MyStruct {
            a: int,
        }
        main() {
            array: [int];
            struct_array: [MyStruct];
            my_struct: MyStruct;
            printi(my_struct.a);
            printi(array[0]);
            printi(struct_array[0].a);
        }
        """
    )
