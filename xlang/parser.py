import sys
import os

from lark import Lark

from xlang.transformer import ASTTransformer


class Parser:
    def __init__(self):
        grammar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grammar.lark')
        with open(grammar_path) as f:
            grammar = f.read()
        self.lark_parser = Lark(grammar, parser='lalr')
        self.transformer = ASTTransformer()

    def parse(self, source_code):
        tree = self.lark_parser.parse(source_code)
        return self.transformer.transform(tree)
