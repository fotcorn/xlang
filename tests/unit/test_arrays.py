from .conftest import validate


def test_access():
    validate(
        """
        struct MyStruct {
            a: i32,
        }
        func main() {
            var struct_array: [MyStruct];
            var my_struct: MyStruct;
            print(my_struct.a);
            print(struct_array[0].a);
        }
        """
    )
