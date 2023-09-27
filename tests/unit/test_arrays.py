from .conftest import validate


def test_access():
    validate(
        """
        struct MyStruct {
            a: i32,
        }
        main() {
            var struct_array: [MyStruct];
            var my_struct: MyStruct;
            printi(my_struct.a);
            printi(struct_array[0].a);
        }
        """
    )
