import sys
from dataclasses import dataclass

class Compiler:

    def __init__(self, arithmetic_op):
        self.arithmetic_op = arithmetic_op.strip()
        self.len_arith_op = len(self.arithmetic_op)
        self.result = None
        self._tokens = None

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

        tokens += [token]
        self.tokens = tokens

    def syntactic(self):

        def is_int(s):
            try:
                int(s)  # Try converting the string to an integer
                return True
            except ValueError:
                return False

        def define_token_type(token):
            if is_int(token):
                return 'number'
            if ' ' in token:
                return 'space'
            return 'operation'

        prev_token = self.tokens[0]
        prev_token_type = define_token_type(prev_token)
        if prev_token_type == 'operation':
            raise ValueError()
        num_foll_space = False

        for i in range(1, len(self.tokens)):
            token = self.tokens[i]
            token_type = define_token_type(token)

            if token_type == prev_token_type:
                raise ValueError()

            if num_foll_space:
                if token_type == 'number':
                    raise ValueError()

            num_foll_space = prev_token_type == 'number' and token_type == 'space'

            prev_token = token
            prev_token_type = token_type

        if token_type == 'operation':
            raise ValueError()

    def semantic(self):
        return

if __name__ == "__main__":
    arithmetic_op = sys.argv[1]

    compiler = Compiler(arithmetic_op)

    compiler.lexical()
    compiler.syntactic()
    compiler.semantic()
    compiler.calculate()

    print(compiler.result)
