from abc import ABC, abstractmethod           

from textwrap import dedent

class ASM:

    initial_code = dedent('''
        ; constantes
        SYS_EXIT equ 1
        SYS_READ equ 3
        SYS_WRITE equ 4
        STDIN equ 0
        STDOUT equ 1
        True equ 1
        False equ 0

        segment .data

        formatin: db "%d", 0
        formatout: db "%d", 10, 0 ; newline, nul terminator
        scanint: times 4 db 0 ; 32-bits integer = 4 bytes

        segment .bss  ; variaveis
        res RESB 1

        section .text
        global main ; linux
        ;global _main ; windows
        extern scanf ; linux
        extern printf ; linux
        ;extern _scanf ; windows
        ;extern _printf; windows
        extern fflush ; linux
        ;extern _fflush ; windows
        extern stdout ; linux
        ;extern _stdout ; windows

        ; subrotinas if/while
        binop_je:
        JE binop_true
        JMP binop_false

        binop_jg:
        JG binop_true
        JMP binop_false

        binop_jl:
        JL binop_true
        JMP binop_false

        binop_false:
        MOV EAX, False  
        JMP binop_exit
        binop_true:
        MOV EAX, True
        binop_exit:
        RET

        main:

        PUSH EBP ; guarda o base pointer
        MOV EBP, ESP ; estabelece um novo base pointer

        ; codigo gerado pelo compilador abaixo
    ''')

    final_code = dedent('''
        ; interrupcao de saida (default)

        PUSH DWORD [stdout]
        CALL fflush
        ADD ESP, 4

        MOV ESP, EBP
        POP EBP

        MOV EAX, 1
        XOR EBX, EBX
        INT 0x80        
    ''')

    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'w') as file:
            file.write(self.initial_code)

    def write(self, code):
        with open(self.filename, 'a') as file:
            file.write(code)

    def end(self):
        with open(self.filename, 'a') as file:
            file.write(self.final_code)

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