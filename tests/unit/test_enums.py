import pytest
from .conftest import validate
from xlang.exceptions import EnumAlreadyDefinedException, ContextException


def test_create_enum_success():
    validate(
        """
        enum Color {
            Red,
            Green,
            Blue,
        }
        """
    )


def test_redefine_enum():
    with pytest.raises(EnumAlreadyDefinedException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Blue,
            }
            enum Color {
                Cyan,
                Magenta,
                Yellow,
            }
            """
        )


def test_duplicate_enum_entry():
    with pytest.raises(ContextException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Red, // Duplicate entry
            }
            """
        )


def test_enum_access():
    validate(
        """
        enum Color {
            Red,
            Green,
            Blue,
        }
        func main() {
            var c: Color = Color.Green;
        }
        """
    )


def test_enum_access_undefined():
    with pytest.raises(ContextException):
        validate(
            """
            enum Color {
                Red,
                Green,
                Blue,
            }
            func main() {
                var c: Color = Color.Yellow;
            }
            """
        )


def test_tagged_enum_simple():
    validate(
        """
        enum Shape {
            Circle {radius: f32},
            Rectangle {width: f32, height: f32},
            Point,
        }
        """
    )


def test_tagged_enum_complex_types():
    validate(
        """
        struct Point {
            x: f32,
            y: f32,
        }
        enum GraphicElement {
            Text {content: string, font_size: i32},
            Shape {vertices: [Point]},
            Simple,
        }
        """
    )


def test_tagged_enum_duplicate_field_names():
    with pytest.raises(ContextException):
        validate(
            """
            enum BadEnum {
                Entry {field: i32, field: f32},
            }
            """
        )


def test_tagged_enum_invalid_field_type():
    with pytest.raises(ContextException):
        validate(
            """
            enum BadEnum {
                Entry {field: NonExistentType},
            }
            """
        )


def test_mixed_simple_and_tagged_enum():
    validate(
        """
        enum MixedEnum {
            Simple,
            Tagged {value: i32},
            AnotherSimple,
            AnotherTagged {x: f32, y: f32},
        }
        """
    )


def test_tagged_enum_with_default_values():
    validate(
        """
        enum Settings {
            WindowSize {width: i32 = 800, height: i32 = 600},
            Theme {name: string = "dark", accent: bool = true},
            Simple,
        }
        """
    )
