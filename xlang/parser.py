import os

from lark import Lark
from lark.exceptions import UnexpectedCharacters, UnexpectedToken, VisitError
from xlang.exceptions import (
    ContextException,
    UnexpectedCharacterException,
    UnexpectedTokenException,
)

from xlang.transformer import ASTTransformer


class Parser:
    def __init__(self):
        grammar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "grammar.lark"
        )
        with open(grammar_path) as f:
            grammar = f.read()
        self.lark_parser = Lark(grammar, parser="lalr")
        self.transformer = ASTTransformer()

    def parse(self, source_code):
        try:
            tree = self.lark_parser.parse(source_code)
        except UnexpectedToken as ex:
            raise UnexpectedTokenException(ex)
        except UnexpectedCharacters as ex:
            raise UnexpectedCharacterException(ex)

        # transform into our own ast
        try:
            return self.transformer.transform(tree)
        except VisitError as ex:
            if isinstance(ex.orig_exc, ContextException):
                raise ex.orig_exc
            else:
                raise ex
