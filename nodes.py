from abc import ABC, abstractmethod           

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

    def evaluate(self, symbol_table, asm):
        value = symbol_table.get(self.value)
        address = value[2]
        asm.write(f'MOV EAX, [EBP-{address}]\n')
        return value

class ReadNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write('PUSH scanint\n')
        asm.write('PUSH formatin\n')
        asm.write('CALL scanf\n')
        asm.write('ADD ESP, 8\n')
        asm.write('MOV EAX, DWORD [scanint]\n')
        return 0, 'INT'

class WhileNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        _id = self.children[0].id
        asm.write(f'LOOP_{_id}:\n')
        
        self.children[0].evaluate(symbol_table, asm)

        asm.write('CMP EAX, False\n')
        asm.write(f'JE EXIT_{_id}\n')

        self.children[1].evaluate(symbol_table, asm)

        asm.write(f'JMP LOOP_{_id}\n')
        asm.write(f'EXIT_{_id}:\n')

class IfNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        self.children[0].evaluate(symbol_table, asm)
        asm.write('CMP EAX, False\n')
        asm.write(f'JE EXIT_{self._id}\n')
        self.children[1].evaluate(symbol_table, asm)
        asm.write(f'JMP EXIT_ELSE_{self._id}\n')
        asm.write(f'EXIT_{self._id}:\n')
        self.children[2].evaluate(symbol_table, asm)
        asm.write(f'EXIT_ELSE_{self._id}:\n')

class VarDecNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write(f'PUSH DWORD 0\n')
        key = self.children[0].value
        symbol_table.create(key)
        if len(self.children) > 1:
            value = self.children[1].evaluate(symbol_table, asm)
            address = symbol_table.get(key)[2]
            symbol_table.set(key, value + (address,))
            asm.write(f'MOV [EBP-{address}], EAX\n')

class PrintNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        self.children[0].evaluate(symbol_table, asm)[0]
        asm.write('PUSH EAX\n')
        asm.write('PUSH formatout\n')
        asm.write('CALL printf\n')
        asm.write('ADD ESP, 8\n')

class AssigmentNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        value = self.children[1].evaluate(symbol_table, asm)
        key = self.children[0].value
        symbol_table.set(key, value + (symbol_table.get(key)[2],))
        asm.write(f'MOV [EBP-{symbol_table.get(key)[2]}], EAX\n')

class BlockNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        for child in self.children:
            child.evaluate(symbol_table, asm)

class BinOpNode(Node):

    def __init__(self, value=None):
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
            asm.write(f'DIV EBX\n')
            self._check_data_type('INT', eval_children_0, eval_children_1)
            return eval_children_0[0] // eval_children_1[0], 'INT'
        elif self.value == '>':
            asm.write(f'CMP EAX, EBX\n')
            asm.write(f'CALL binop_jg\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] > eval_children_1[0]), 'INT'
        elif self.value == '<':
            asm.write(f'CMP EAX, EBX\n')
            asm.write(f'CALL binop_jl\n')
            self._check_data_types_is_equal(eval_children_0, eval_children_1)
            return int(eval_children_0[0] < eval_children_1[0]), 'INT'
        elif self.value == '==':
            asm.write(f'CMP EAX, EBX\n')
            asm.write(f'CALL binop_je\n')
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

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        if self.value == '+':
            return self.children[0].evaluate(symbol_table, asm)[0], 'INT'
        elif self.value == '-':
            return -self.children[0].evaluate(symbol_table, asm)[0], 'INT'
        elif self.value == 'not':
            return not self.children[0].evaluate(symbol_table, asm)[0], 'INT'

class IntValNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        asm.write(f'MOV EAX, {self.value}\n')
        return int(self.value), 'INT'

class StringNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        return str(self.value), 'STRING'

class NoOpNode(Node):

    def __init__(self, value=None):
        super().__init__(value)

    def evaluate(self, symbol_table, asm):
        pass
