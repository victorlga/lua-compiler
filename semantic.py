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
    
class ReadNode(Node):

    def evaluate(self, symbol_table):
        return int(input())

class WhileNode(Node):

    def evaluate(self, symbol_table):
        while self.children[0].evaluate(symbol_table):
            self.children[1].evaluate(symbol_table)

class IfNode(Node):

    def evaluate(self, symbol_table):
        if self.children[0].evaluate(symbol_table):
            self.children[1].evaluate(symbol_table)
        elif len(self.children) >= 2:
            self.children[2].evaluate(symbol_table)

class PrintNode(Node):

    def evaluate(self, symbol_table):
        print(self.children[0].evaluate(symbol_table))

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
        elif self.value == 'and':
            return self.children[0].evaluate(symbol_table) and self.children[1].evaluate(symbol_table)
        elif self.value == 'or':
            return self.children[0].evaluate(symbol_table) or self.children[1].evaluate(symbol_table)
        elif self.value == '>':
            return self.children[0].evaluate(symbol_table) > self.children[1].evaluate(symbol_table)
        elif self.value == '<':
            return self.children[0].evaluate(symbol_table) < self.children[1].evaluate(symbol_table)
        elif self.value == '==':
            return self.children[0].evaluate(symbol_table) == self.children[1].evaluate(symbol_table)

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