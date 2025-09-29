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


def test_enum_variant_instantiation_basic():
    validate(
        """
        enum Shape {
            Circle {radius: f32},
            Rectangle {width: f32, height: f32},
            Point,
        }
        func main() {
            var s: Shape = Shape.Circle { radius: 3.5 };
        }
        """
    )


def test_enum_variant_instantiation_multiple_fields():
    validate(
        """
        enum Shape {
            Circle {radius: f32},
            Rectangle {width: f32, height: f32},
            Point,
        }
        func main() {
            var r: Shape = Shape.Rectangle { width: 2.0, height: 4.0 };
        }
        """
    )


def test_enum_variant_instantiation_unknown_enum():
    with pytest.raises(ContextException):
        validate(
            """
            func main() {
                var s: Shape = Shape.Circle { radius: 3.5 };
            }
            """
        )


def test_enum_variant_instantiation_unknown_variant():
    with pytest.raises(ContextException):
        validate(
            """
            enum Shape {
                Circle {radius: f32},
                Point,
            }
            func main() {
                var s: Shape = Shape.Square { side: 2.0 };
            }
            """
        )


def test_enum_variant_instantiation_unknown_field():
    with pytest.raises(ContextException):
        validate(
            """
            enum Shape {
                Circle {radius: f32},
            }
            func main() {
                var s: Shape = Shape.Circle { radius: 3.5, diameter: 7.0 };
            }
            """
        )


def test_enum_variant_instantiation_duplicate_field():
    with pytest.raises(ContextException):
        validate(
            """
            enum Shape {
                Circle {radius: f32},
            }
            func main() {
                var s: Shape = Shape.Circle { radius: 3.5, radius: 4.0 };
            }
            """
        )


def test_enum_variant_instantiation_missing_required_field():
    with pytest.raises(ContextException):
        validate(
            """
            enum Shape {
                Rectangle {width: f32, height: f32},
            }
            func main() {
                var s: Shape = Shape.Rectangle { width: 2.0 };
            }
            """
        )


def test_enum_variant_instantiation_with_defaults():
    validate(
        """
        enum Settings {
            WindowSize {width: i32 = 800, height: i32 = 600},
        }
        func main() {
            var s: Settings = Settings.WindowSize { width: 1024 };
        }
        """
    )


def test_enum_variant_instantiation_type_mismatch():
    with pytest.raises(ContextException):
        validate(
            """
            enum Shape {
                Circle {radius: f32},
            }
            func main() {
                var s: Shape = Shape.Circle { radius: "not a number" };
            }
            """
        )
