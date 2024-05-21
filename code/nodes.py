from abc import ABC, abstractmethod
from .table import SymbolTable, FuncTable         
from code.asm import ASM

class Node(ABC):

    _id = 0

    def __init__(self, value=None):
        self.value = value
        self.children = []
        self.id = Node._id
        Node._id += 1

    @abstractmethod
    def evaluate():
        pass

class IdentifierNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        value = symbol_table.get(self.value)
        address = value[2]
        ASM.write(f'MOV EAX, [EBP-{address}]\n')
        return value

class ReadNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        ASM.write('PUSH scanint\n')
        ASM.write('PUSH formatin\n')
        ASM.write('CALL scanf\n')
        ASM.write('ADD ESP, 8\n')
        ASM.write('MOV EAX, DWORD [scanint]\n')
        return 0, 'INT'

class WhileNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        ASM.write(f'LOOP_{self.id}:\n')

        self.children[0].evaluate(symbol_table)

        ASM.write('CMP EAX, False\n')
        ASM.write(f'JE EXIT_{self.id}\n')

        self.children[1].evaluate(symbol_table)

        ASM.write(f'JMP LOOP_{self.id}\n')
        ASM.write(f'EXIT_{self.id}:\n')

class IfNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        self.children[0].evaluate(symbol_table)

        ASM.write('CMP EAX, False\n')
        ASM.write(f'JE EXIT_{self.id}\n')
        self.children[1].evaluate(symbol_table)

        ASM.write(f'JMP EXIT_ELSE_{self.id}\n')
        ASM.write(f'EXIT_{self.id}:\n')

        self.children[2].evaluate(symbol_table)
        ASM.write(f'EXIT_ELSE_{self.id}:\n')

class VarDecNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        ASM.write(f'PUSH DWORD 0\n')
        key = self.children[0].value
        symbol_table.create(key)
        if len(self.children) > 1:
            value = self.children[1].evaluate(symbol_table)
            address = symbol_table.get(key)[2]
            symbol_table.set(key, value + (address,))
            ASM.write(f'MOV [EBP-{address}], EAX\n')

class PrintNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        self.children[0].evaluate(symbol_table)[0]
        ASM.write('PUSH EAX\n')
        ASM.write('PUSH formatout\n')
        ASM.write('CALL printf\n')
        ASM.write('ADD ESP, 8\n')

class AssigmentNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        value = self.children[1].evaluate(symbol_table)
        if len(value) == 2:
            element, dtype = value
        else:
            element, dtype, _ = value
        key = self.children[0].value
        symbol_table.set(key, (element, dtype,) + (symbol_table.get(key)[2],))
        ASM.write(f'MOV [EBP-{symbol_table.get(key)[2]}], EAX\n')

class BlockNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        for child in self.children:
            if child.__class__.__name__ == 'ReturnNode':
                return child.evaluate(symbol_table)
            child.evaluate(symbol_table)  
          
class BinOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        eval_children_1 = self.children[1].evaluate(symbol_table)
        ASM.write(f'PUSH EAX\n')
        eval_children_0 = self.children[0].evaluate(symbol_table)
        ASM.write(f'POP EBX\n')
        if self.value == '+':
            ASM.write(f'ADD EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] + eval_children_1[0], 'INT'
        elif self.value == '-':
            ASM.write(f'SUB EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] - eval_children_1[0], 'INT'
        elif self.value == '*':
            ASM.write(f'IMUL EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] * eval_children_1[0], 'INT'
        elif self.value == '/':
            ASM.write(f'DIV EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] // eval_children_1[0], 'INT'
        elif self.value == '>':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jg\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] > eval_children_1[0]), 'INT'
        elif self.value == '<':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jl\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] < eval_children_1[0]), 'INT'
        elif self.value == '==':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_je\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] == eval_children_1[0]), 'INT'
        elif self.value == 'and':
            ASM.write(f'AND EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return int(eval_children_0[0] and eval_children_1[0]), 'INT'
        elif self.value == 'or':
            ASM.write(f'OR EAX, EBX\n')
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

class UnOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table)[0], 'INT'
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table)[0], 'INT'
        elif self.value == 'not':
            return not self.children[0].evaluate(symbol_table)[0], 'INT'

class IntValNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        ASM.write(f'MOV EAX, {self.value}\n')
        return int(self.value), 'INT'

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

        for i, key in enumerate(local_symbol_table.table):
            local_symbol_table.set(key, self.children[i].evaluate(symbol_table))
        return func.children[-1].evaluate(local_symbol_table)

class ReturnNode(Node):

        def __init__(self, value=None):
            super().__init__(value)

        def evaluate(self, symbol_table):
            return self.children[0].evaluate(symbol_table)

class StringNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        return str(self.value), 'STRING'

class NoOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        pass
