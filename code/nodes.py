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
        address = symbol_table.get(self.value)
        asm_code = f'MOV EAX, [EBP-{abs(address)}]\n' if address > 0 else f'MOV EAX, [EBP+{abs(address)}]\n'
        ASM.write(asm_code)

class ReadNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        ASM.write('PUSH scanint\n')
        ASM.write('PUSH formatin\n')
        ASM.write('CALL scanf\n')
        ASM.write('ADD ESP, 8\n')
        ASM.write('MOV EAX, DWORD [scanint]\n')

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
            self.children[1].evaluate(symbol_table)
            address = symbol_table.get(key)
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
        self.children[1].evaluate(symbol_table)
        key = self.children[0].value
        address = symbol_table.get(key)
        asm_code = f'MOV [EBP-{abs(address)}], EAX\n' if address > 0 else f'MOV [EBP+{abs(address)}], EAX\n'
        ASM.write(asm_code)

class BlockNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        for child in self.children:
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
        elif self.value == '-':
            ASM.write(f'SUB EAX, EBX\n')
        elif self.value == '*':
            ASM.write(f'IMUL EBX\n')
        elif self.value == '/':
            ASM.write(f'DIV EBX\n')
        elif self.value == '>':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jg\n')
        elif self.value == '<':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_jl\n')
        elif self.value == '==':
            ASM.write(f'CMP EAX, EBX\n')
            ASM.write(f'CALL binop_je\n')
        elif self.value == 'and':
            ASM.write(f'AND EAX, EBX\n')
        elif self.value == 'or':
            ASM.write(f'OR EAX, EBX\n')
        elif self.value == '..':
            # Operator .. ASM code generation not implemented
            pass

class UnOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        # This node does not do ASM code generation
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

class FuncDecNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        FuncTable.set(self.children[0].value, self)
        ASM.write(f'JMP END_FUNC_{self.children[0].value}\n')

        ASM.write(f'{self.children[0].value}:\n')
        ASM.write(f'PUSH EBP\n')
        ASM.write(f'MOV EBP, ESP\n')

        local_symbol_table = SymbolTable()
        for i in range(1, len(self.children) - 1):
            key = self.children[i].children[0].value
            local_symbol_table.create(key, shift=4, signal=-1)

        self.children[-1].evaluate(local_symbol_table)

        ASM.write('MOV ESP, EBP\n')
        ASM.write('POP EBP\n')
        ASM.write('RET\n')

        ASM.write(f'END_FUNC_{self.children[0].value}:\n')

class FuncCallNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):

        func = FuncTable.get(self.value)
        if len(func.children) - 2 != len(self.children):
            raise RuntimeError(f'Function {self.value} expects {len(func.children) - 2} arguments, {len(self.children)} given.')

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
        # This node does not do ASM code generation
        return str(self.value), 'STRING'

class NoOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table):
        pass
