import os

from lark import Lark
from lark.exceptions import VisitError
from xlang.exceptions import ContextException

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
        tree = self.lark_parser.parse(source_code)
        try:
            return self.transformer.transform(tree)
        except VisitError as ex:
            if isinstance(ex.orig_exc, ContextException):
                raise ex.orig_exc
