import sys
import re
from abc import ABC, abstractmethod


class PrePro:

    @staticmethod
    def filter(code):
        pattern = r'--.*'
        return re.sub(pattern, '', code)

class SymbolTable:

    def __init__(self):
        self.dict = {}

    def getter(self, key):
        return self.dict[key]

    def setter(self, key, value):
        self.dict[key] = value

class Node(ABC):

    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def evaluate():
        pass

class BinOp(Node):

    def evaluate(self, symbol_table: SymbolTable):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table) + self.children[1].evaluate(symbol_table)
        elif self.value == '-':
            return self.children[0].evaluate(symbol_table) - self.children[1].evaluate(symbol_table)
        elif self.value == '*':
            return self.children[0].evaluate(symbol_table) * self.children[1].evaluate(symbol_table)
        elif self.value == '/':
            return self.children[0].evaluate(symbol_table) // self.children[1].evaluate(symbol_table)

class UnOp(Node):

    def evaluate(self, symbol_table: SymbolTable):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)

class IntVal(Node):

    def evaluate(self, symbol_table: SymbolTable):
        return int(self.value)

class NoOp(Node):
    pass

class Token:

    def __init__(self, type:str, value:str):
        self.type: str = type
        self.value: str = value

class Tokenizer:

    def __init__(self, source:str):
        self.source: str = source
        self.position: int = 0
        self.next: Token = None

    def select_next(self):

        value = self._define_value()
        while value == ' ' or value == '\n':
            self.position += 1
            value = self._define_value()

        if self._end_of_file():
            ctype = 'EOF'
        elif value == '(':
            ctype = 'OPAR'
        elif value == ')':
            ctype = 'CPAR'
        elif value == '-':
            ctype = 'MINUS'
        elif value == '+':
            ctype = 'PLUS'
        elif value == '*':
            ctype = 'MULT'
        elif value == '/':
            ctype = 'DIV'
        elif value.isdigit():
            while value.isdigit():
                self.position += 1
                value += self._define_value(fallback=' ')
            value = value[:-1]
            ctype = 'INT'
            self.position -= 1
        else:
            raise ValueError('Not a valid character: ' + value)

        self.position += 1

        self.next = Token(ctype, value)
    
    def _end_of_file(self):
        return self.position >= len(self.source)
    
    def _define_value(self, fallback=''):
        return fallback if self._end_of_file() else self.source[self.position]

class Parser:

    def __init__(self):
        self.tokenizer: Tokenizer = None

    def run(self, code: str) -> Node:
        code = PrePro.filter(code)
        self.tokenizer = Tokenizer(code)
        self.tokenizer.select_next()
        ast = self._parse_expression()

        if self.tokenizer.next.type != 'EOF':
            raise ValueError('Unexpected final token type: ' + self.tokenizer.next.type)

        return ast

    def _parse_expression(self) -> Node:

        term = self._parse_term()
        expression = term
        token = self.tokenizer.next

        while token.type in ('PLUS', 'MINUS'):

            binop = BinOp(token.value)
            binop.children.append(expression)

            self.tokenizer.select_next()
            term = self._parse_term()
            binop.children.append(term)

            token = self.tokenizer.next
            expression = binop

        return expression

    def _parse_term(self) -> Node:

        factor = self._parse_factor()
        term = factor
        token = self.tokenizer.next

        while token.type in ('MULT', 'DIV'):

            binop = BinOp(token.value)
            binop.children.append(term)

            self.tokenizer.select_next()
            factor = self._parse_factor()
            binop.children.append(factor)


            token = self.tokenizer.next
            term = binop

        return term

    def _parse_factor(self) -> Node:

        token = self.tokenizer.next

        if token.type == 'INT':
            factor = IntVal(token.value)
            self.tokenizer.select_next()
            return factor
        elif token.type in ('PLUS', 'MINUS'):
            self.tokenizer.select_next()
            factor = self._parse_factor()
            unop = UnOp(token.value)
            unop.children.append(factor)
            return unop
        elif token.type == 'OPAR':
            self.tokenizer.select_next()
            expression = self._parse_expression()
            token = self.tokenizer.next
            if token.type != 'CPAR':
                raise ValueError('Expected CPAR token type, got: ' + token.type)
            self.tokenizer.select_next()
            return expression


if __name__ == "__main__":
    file_name = sys.argv[1]

    with open(file_name, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    print(parser.run(code).evaluate(symbol_table))
