from abc import ABC, abstractmethod
import sys

class SymbolTable:

    def __init__(self):
        self.table = {}

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        self.table[key] = value

class Node(ABC):

    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def evaluate():
        pass

class IdentifierNode(Node):

    def evaluate(self, symbol_table):
        return symbol_table.get(self.value)

class PrintNode(Node):

    def evaluate(self, symbol_table):
        value = str(self.children[0].evaluate(symbol_table)) + '\n'
        sys.stdout.write(value)

class AssigmentNode(Node):

    def evaluate(self, symbol_table):
        value = self.children[1].evaluate(symbol_table)
        key = self.children[0].value
        symbol_table.set(key, value)
        self.children[0].evaluate(symbol_table)

class BlockNode(Node):

    def evaluate(self, symbol_table):
        for child in self.children:
            child.evaluate(symbol_table)

class BinOpNode(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table) + self.children[1].evaluate(symbol_table)
        elif self.value == '-':
            return self.children[0].evaluate(symbol_table) - self.children[1].evaluate(symbol_table)
        elif self.value == '*':
            return self.children[0].evaluate(symbol_table) * self.children[1].evaluate(symbol_table)
        elif self.value == '/':
            return self.children[0].evaluate(symbol_table) // self.children[1].evaluate(symbol_table)

class UnOpNode(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)

class IntValNode(Node):

    def evaluate(self, symbol_table):
        return int(self.value)

class NoOpNode(Node):
    
    def evaluate(self, symbol_table):
        pass