import sys
from dataclasses import dataclass

class Compiler:

    def __init__(self, arithmetic_op):
        self.arithmetic_op = arithmetic_op
        self.len_arith_op = len(arithmetic_op)
        self.result = None
        self._lexical_res = None
        self._syntactic_res = None
        self._semantic_res = None

    def lexical(self):
        valid_characters = (' ', '+', '-', '1', '2', '3', '4', '5', '6', '7', '8', '9')

        for character in self.arithmetic_op:
            if character not in valid_characters:
                raise ValueError()
            
        def define_char_type(char):
            if char.isdigit():
                return 'digit'
            if char == ' ':
                return 'space'
            return 'operation'

        tokens = []

        prev_char = self.arithmetic_op[0]
        prev_char_type = define_char_type(prev_char)
        token = prev_char
        for i in range(1, self.len_arith_op):
            char = self.arithmetic_op[i]
            char_type = define_char_type(char)

            if char_type != prev_char_type:
                tokens.append(token)
                prev_char = char
                prev_char_type = define_char_type(prev_char)
                token = prev_char
                continue

            token += char
            prev_char = char
            prev_char_type = define_char_type(prev_char)

        tokens += token

        self._lexical_res = tokens

    def syntactic(self):
        return

    def semantic(self):
        return

if __name__ == "__main__":
    arithmetic_op = sys.argv[1]

    compiler = Compiler(arithmetic_op)

    compiler.lexical()
    compiler.syntactic()
    compiler.semantic()

    print(compiler._lexical_res)
