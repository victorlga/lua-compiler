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
        asm_code = f'MOV EAX, [EBP-{abs(address)}]\n' if address > 0 else f'MOV EAX, [EBP+{abs(address)}]\n'
        ASM.write(asm_code)
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
            print(symbol_table.table, key, value)
            symbol_table.set(key, value + (address,))
            ASM.write(f'MOV [EBP-{address}], EAX\n')

class PrintNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        self.children[0].evaluate(symbol_table)
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
        address = symbol_table.get(key)[2]
        asm_code = f'MOV [EBP-{abs(address)}], EAX\n' if address > 0 else f'MOV [EBP+{abs(address)}], EAX\n'
        ASM.write(asm_code)

class BlockNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        for child in self.children:
            print(child.__class__.__name__)
            if child.__class__.__name__ == 'ReturnNode':
                return child.evaluate(symbol_table)
            child.evaluate(symbol_table)

class BinOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        self.children[1].evaluate(symbol_table)
        ASM.write(f'PUSH EAX\n')
        self.children[0].evaluate(symbol_table)
        ASM.write(f'POP EBX\n')
        if self.value == '+':
            ASM.write(f'ADD EAX, EBX\n')
            return 0, 'INT'
        elif self.value == '-':
            ASM.write(f'SUB EAX, EBX\n')
            return 0, 'INT'
        elif self.value == '*':
            ASM.write(f'IMUL EBX\n')
            return 0, 'INT'
        elif self.value == '/':
            ASM.write(f'DIV EBX\n')
            return 0, 'INT'
        elif self.value == '>':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jg\n')
            return 0, 'INT'
        elif self.value == '<':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jl\n')
            return 0, 'INT'
        elif self.value == '==':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_je\n')
            return 0, 'INT'
        elif self.value == 'and':
            ASM.write(f'AND EAX, EBX\n')
            return 0, 'INT'
        elif self.value == 'or':
            ASM.write(f'OR EAX, EBX\n')
            return 0, 'INT'
        elif self.value == '..':
            # code removed
            return 0, 'STRING'

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
        ASM.write(f'JMP END_FUNC_{self.children[0].value}\n')

        ASM.write(f'{self.children[0].value}:\n')
        ASM.write(f'PUSH EBP\n')
        ASM.write(f'MOV EBP, ESP\n')

        local_symbol_table = SymbolTable()
        for i in range(1, len(self.children) - 1):
            key = self.children[i].children[0].value
            local_symbol_table.create(key, shift_value=4, signal=-1)

        self.children[-1].evaluate(local_symbol_table)

        ASM.write('MOV ESP, EBP\n')
        ASM.write('POP EBP\n')
        ASM.write('RET\n')

        ASM.write(f'END_FUNC_{self.children[0].value}:\n')

class FuncCallNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):

        for i in range(len(self.children)-1, -1, -1):
            self.children[i].evaluate(symbol_table)
            ASM.write('PUSH EAX\n')

        ASM.write(f'CALL {self.value}\n')
        ASM.write(f'ADD ESP, {4 * len(self.children)}\n')

class ReturnNode(Node):

        def __init__(self, value=None):
            super().__init__(value)

        def evaluate(self, symbol_table):
            self.children[0].evaluate(symbol_table)
            ASM.write('MOV ESP, EBP\n')
            ASM.write('POP EBP\n')
            ASM.write(f'RET\n')

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
