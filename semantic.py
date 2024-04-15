from abc import ABC, abstractmethod
import sys

class SymbolTable:

    def __init__(self):
        self.table = {}

    def create(self, key):
        if key in self.table:
            raise RuntimeError(f'Key {key} already created.')
        self.table[key] = None

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        if key in self.table:
            self.table[key] = value
        else:
            raise RuntimeError(f'Key {key} does not exist.')

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
        else:
            self.children[2].evaluate(symbol_table)

class VarDecNode(Node):

    def evaluate(self, symbol_table):
        key = self.children[0].evaluate(symbol_table)
        symbol_table.create(key)
        if len(self.children) > 1:
            value = self.children[1].evaluate(symbol_table)
            symbol_table.set(key, value)

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
        eval_children_0 = self.children[0].evaluate(symbol_table)
        eval_children_1 = self.children[1].evaluate(symbol_table)
        if self.value == '+':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 + eval_children_1
        elif self.value == '-':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 - eval_children_1
        elif self.value == '*':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 * eval_children_1
        elif self.value == '/':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 // eval_children_1
        elif self.value == '>':
            self._check_data_type(['INT', 'STRING'], eval_children_0, eval_children_1)
            return eval_children_0 > eval_children_1
        elif self.value == '<':
            self._check_data_type(['INT', 'STRING'], eval_children_0, eval_children_1)
            return eval_children_0 < eval_children_1
        elif self.value == '==':
            self._check_data_type(['INT', 'STRING'], eval_children_0, eval_children_1)
            return eval_children_0 == eval_children_1
        elif self.value == 'and':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 and eval_children_1
        elif self.value == 'or':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0 or eval_children_1
        elif self.value == '..':
            self._check_data_type(['INT', 'STRING'], eval_children_0, eval_children_1)
            return str(eval_children_0) + str(eval_children_1)

    def _check_data_type(self, data_type, eval_chil_0, eval_chil_1):
        if eval_chil_0[1] not in data_type or eval_chil_1[1] not in data_type:
                raise TypeError(f'"{self.value}" operator is only allowed with ' + data_type + ' data.')


class UnOpNode(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)
        elif self.value == 'not':
            return not self.children[0].evaluate(symbol_table)

class IntValNode(Node):

    def evaluate(self, symbol_table):
        return int(self.value)

class StringNode(Node):

    def evaluate(self, symbol_table):
        return str(self.value)

class NoOpNode(Node):

    def evaluate(self, symbol_table):
        pass