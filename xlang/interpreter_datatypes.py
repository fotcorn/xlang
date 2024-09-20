from enum import Enum, auto
from typing import Optional, Any
from pydantic import BaseModel

from xlang.exceptions import InternalCompilerError
from xlang.xl_ast import (
    PrimitiveType,
)


class ValueType(Enum):
    PRIMITIVE = auto()
    STRUCT = auto()
    ENUM = auto()


class Value(BaseModel):
    type: ValueType
    value: Any
    primitive_type: Optional[PrimitiveType] = None
    is_array: bool = False
    type_name: Optional[str] = None  # for structs and enums


class ScopeStack:
    def __init__(self):
        self.stack = [{}]

    def set_variable(self, name: str, value: Value):
        self.stack[-1][name] = value

    def get_variable(self, name: str) -> Value:
        for stack in reversed(self.stack):
            if name in stack:
                return stack[name]
        # this should have been detected by the validation pass
        raise InternalCompilerError(f"Unknown variable: {name}")

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        self.stack.pop()
