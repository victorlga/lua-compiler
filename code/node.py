from abc import ABC, abstractmethod
import sys

from table import SymbolTable

class Node(ABC):

    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def evaluate():
        pass

class Identifier(Node):

    def evaluate(self, symbol_table):
        return symbol_table.get(self.value)

class Print(Node):

    def evaluate(self, symbol_table):
        value = str(self.children[0].evaluate(symbol_table))
        sys.stdout.write(value)

class Assigment(Node):

    def evaluate(self, symbol_table):
        key = self.children[0].evaluate(symbol_table)
        value = self.children[1].evaluate(symbol_table)
        symbol_table.set(key, value)

class Block(Node):

    def evaluate(self, symbol_table):
        for child in self.children:
            child.evaluate(symbol_table)

class BinOp(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table) + self.children[1].evaluate(symbol_table)
        elif self.value == '-':
            return self.children[0].evaluate(symbol_table) - self.children[1].evaluate(symbol_table)
        elif self.value == '*':
            return self.children[0].evaluate(symbol_table) * self.children[1].evaluate(symbol_table)
        elif self.value == '/':
            return self.children[0].evaluate(symbol_table) // self.children[1].evaluate(symbol_table)

class UnOp(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)

class IntVal(Node):

    def evaluate(self, symbol_table):
        return int(self.value)

class NoOp(Node):
    pass