from abc import ABC, abstractmethod
from .table import SymbolTable, FuncTable

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
        return int(input()), 'INT'

class WhileNode(Node):

    def evaluate(self, symbol_table):
        while self.children[0].evaluate(symbol_table)[0]:
            self.children[1].evaluate(symbol_table)

class IfNode(Node):

    def evaluate(self, symbol_table):
        if self.children[0].evaluate(symbol_table)[0]:
            self.children[1].evaluate(symbol_table)
        else:
            self.children[2].evaluate(symbol_table)

class VarDecNode(Node):

    def evaluate(self, symbol_table):
        key = self.children[0].value
        symbol_table.create(key)
        if len(self.children) > 1:
            value = self.children[1].evaluate(symbol_table)
            symbol_table.set(key, value)

class PrintNode(Node):

    def evaluate(self, symbol_table):
        print(self.children[0].evaluate(symbol_table)[0])

class AssigmentNode(Node):

    def evaluate(self, symbol_table):
        value = self.children[1].evaluate(symbol_table)
        key = self.children[0].value
        symbol_table.set(key, value)
        self.children[0].evaluate(symbol_table)

class BlockNode(Node):

    def evaluate(self, symbol_table):
        
        for child in self.children:
            if child.__class__.__name__ == 'ReturnNode':
                return child.evaluate(symbol_table)
            child.evaluate(symbol_table)

class BinOpNode(Node):

    def evaluate(self, symbol_table):
        eval_children_0 = self.children[0].evaluate(symbol_table)
        eval_children_1 = self.children[1].evaluate(symbol_table)
        if self.value == '+':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] + eval_children_1[0], 'INT'
        elif self.value == '-':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] - eval_children_1[0], 'INT'
        elif self.value == '*':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] * eval_children_1[0], 'INT'
        elif self.value == '/':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] // eval_children_1[0], 'INT'
        elif self.value == '>':
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] > eval_children_1[0]), 'INT'
        elif self.value == '<':
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] < eval_children_1[0]), 'INT'
        elif self.value == '==':
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] == eval_children_1[0]), 'INT'
        elif self.value == 'and':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return int(eval_children_0[0] and eval_children_1[0]), 'INT'
        elif self.value == 'or':
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return int(eval_children_0[0] or eval_children_1[0]), 'INT'
        elif self.value == '..':
            self._check_data_type(['INT', 'STRING'], eval_children_0, eval_children_1)
            return str(eval_children_0[0]) + str(eval_children_1[0]), 'STRING'

    def _check_data_type(self, data_type, eval_chil_0, eval_chil_1):
        if eval_chil_0[1] not in data_type or eval_chil_1[1] not in data_type:
                raise TypeError(f'"{self.value}" operator is only allowed with ' + data_type + ' data.')
        
    def _check_data_types_is_equal(self, eval_chil_0, eval_chil_1):
        if eval_chil_0[1] != eval_chil_1[1]:
            raise TypeError(f'"{self.value}" operator can\'t be used between data with different types.')


class FuncDecNode(Node):
    
    def __init__(self, value=None):
        super().__init__(value)
    
    def evaluate(self, symbol_table):
        if self.children[0].value in FuncTable.table:
            raise RuntimeError(f'Function {self.children[0].value} already declared.')

        FuncTable.set(self.children[0].value, self)

class FuncCallNode(Node):
    
    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):

        if self.value not in FuncTable.table:
            raise RuntimeError(f'Function {self.value} not declared.')
        
        func = FuncTable.get(self.value)
        if len(func.children) - 2 != len(self.children):
            raise RuntimeError(f'Function {self.value} expects {len(func.children) - 2} arguments, {len(self.children)} given.')
        
        local_symbol_table = SymbolTable()
        for i in range(1, len(func.children) - 1):
            func.children[i].evaluate(local_symbol_table)

        i = 0
        for key in local_symbol_table.table:
            local_symbol_table.set(key, self.children[i].evaluate(symbol_table))
            i += 1
        return func.children[-1].evaluate(local_symbol_table)

class ReturnNode(Node):
    
        def __init__(self, value=None):
            super().__init__(value)
    
        def evaluate(self, symbol_table):
            return self.children[0].evaluate(symbol_table)

class UnOpNode(Node):

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)[0], 'INT'
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)[0], 'INT'
        elif self.value == 'not':
            return not self.children[0].evaluate(symbol_table)[0], 'INT'

class IntValNode(Node):

    def evaluate(self, symbol_table):
        return int(self.value), 'INT'

class StringNode(Node):

    def evaluate(self, symbol_table):
        return str(self.value), 'STRING'

class NoOpNode(Node):

    def evaluate(self, symbol_table):
        pass