from abc import ABC, abstractmethod           

from textwrap import dedent

class ASM:

    initial_code = '''
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
    '''

    final_code = '''
        ; interrupcao de saida (default)

        PUSH DWORD [stdout]
        CALL fflush
        ADD ESP, 4

        MOV ESP, EBP
        POP EBP

        MOV EAX, 1
        XOR EBX, EBX
        INT 0x80        
    '''

    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'w') as file:
            file.write(dedent(self.initial_code))

    def write(self, code):
        with open(self.filename, 'a') as file:
            file.write(dedent(code))

    def end(self):
        with open(self.filename, 'a') as file:
            file.write(dedent(self.final_code))

class SymbolTable:

    def __init__(self):
        self.table = {}
        self.address = 4

    def create(self, key):
        if key in self.table:
            raise RuntimeError(f'Key {key} already created.')
        self.table[key] = (None, None, self.address)
        self.address += 4

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        if key in self.table:
            self.table[key] = value
        else:
            raise RuntimeError(f'Key {key} does not exist.')

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

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        value = symbol_table.get(self.value)
        address = value[2]
        asm.write(f'MOV EAX, [EBP-{address}]\n')
        return value
    
class ReadNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write('PUSH scanint\n')
        asm.write('PUSH formatin\n')
        asm.write('CALL scanf\n')
        asm.write('ADD ESP, 8\n')
        asm.write('MOV EAX, DWORD [scanint]\n')
        return 0, 'INT'

class WhileNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write(f'LOOP_{self._id}\n')
        
        self.children[0].evaluate(symbol_table, asm)
        asm.write('CMP EAX, False\n')
        asm.write(f'JE EXIT_{self._id}\n')

        self.children[1].evaluate(symbol_table, asm)

        asm.write(f'JMP LOOP_{self._id}\n')
        asm.write(f'EXIT_{self._id}:\n')

class IfNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        if self.children[0].evaluate(symbol_table, asm)[0]:
            self.children[1].evaluate(symbol_table, asm)
        else:
            self.children[2].evaluate(symbol_table, asm)

class VarDecNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write(f'PUSH DWORD 0\n')
        key = self.children[0].value
        symbol_table.create(key)
        if len(self.children) > 1:
            value = self.children[1].evaluate(symbol_table, asm)
            symbol_table.set(key, value + (symbol_table.get(key)[2],))

class PrintNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        self.children[0].evaluate(symbol_table, asm)[0]
        asm.write('PUSH EAX\n')
        asm.write('PUSH formatout\n')
        asm.write('CALL printf\n')
        asm.write('ADD ESP, 8\n')

class AssigmentNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        value = self.children[1].evaluate(symbol_table, asm)
        key = self.children[0].value
        symbol_table.set(key, value + (symbol_table.get(key)[2],))
        asm.write(f'MOV [EBP-{symbol_table.get(key)[2]}], EAX\n')

class BlockNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        for child in self.children:
            child.evaluate(symbol_table, asm)

class BinOpNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        eval_children_1 = self.children[1].evaluate(symbol_table, asm)
        asm.write(f'PUSH EAX\n')
        eval_children_0 = self.children[0].evaluate(symbol_table, asm)
        asm.write(f'POP EBX\n')
        if self.value == '+':
            asm.write(f'ADD EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] + eval_children_1[0], 'INT'
        elif self.value == '-':
            asm.write(f'SUB EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] - eval_children_1[0], 'INT'
        elif self.value == '*':
            asm.write(f'IMUL EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] * eval_children_1[0], 'INT'
        elif self.value == '/':
            asm.write(f'IDIV EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] // eval_children_1[0], 'INT'
        elif self.value == '>':
            asm.write(f'CMP EAX, EBX\n')
            # asm.write(f'JG binop_jg\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] > eval_children_1[0]), 'INT'
        elif self.value == '<':
            asm.write(f'CMP EAX, EBX\n')
            # asm.write(f'JL binop_jl\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] < eval_children_1[0]), 'INT'
        elif self.value == '==':
            asm.write(f'CMP EAX, EBX\n')
            # asm.write(f'JE binop_je\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] == eval_children_1[0]), 'INT'
        elif self.value == 'and':
            asm.write(f'AND EAX, EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return int(eval_children_0[0] and eval_children_1[0]), 'INT'
        elif self.value == 'or':
            asm.write(f'OR EAX, EBX\n')
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

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table, asm)[0], 'INT'
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table, asm)[0], 'INT'
        elif self.value == 'not':
            return not self.children[0].evaluate(symbol_table, asm)[0], 'INT'

class IntValNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write(f'MOV EAX, {self.value}\n')
        return int(self.value), 'INT'

class StringNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        return str(self.value), 'STRING'

class NoOpNode(Node):

    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        pass
