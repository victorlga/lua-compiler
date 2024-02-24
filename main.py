import sys

class Token:

    def __init__(self, type:str, value:str):
        self.type: str = type
        self.value: str = value


class Tokenizer:

    def __init__(self, source:str):
        self.source: str = source
        self.position: int = 0
        self.next: Token = None

    def select_next(self):

        value = self._define_value()
        while value == ' ':
            self.position += 1
            value = self._define_value()

        if self._end_of_file():
            ctype = 'EOF'
        elif value == '-':
            ctype = 'MINUS'
        elif value == '+':
            ctype = 'PLUS'
        elif value.isdigit():
            while value.isdigit():
                self.position += 1
                value += self._define_value(fallback=' ')
            value = value[:-1]
            ctype = 'INT'
            self.position -= 1
        else:
            raise ValueError('Not a valid character: ' + value)

        self.position += 1

        self.next = Token(ctype, value)
    
    def _end_of_file(self):
        return self.position >= len(self.source)
    
    def _define_value(self, fallback=''):
        return fallback if self._end_of_file() else self.source[self.position]


class Parser:

    def __init__(self):
        self.tokenizer: Tokenizer = None

    def run(self, code: str):
        self.tokenizer = Tokenizer(code)
        self.tokenizer.select_next()
        res = self._parse_expression()

        if self.tokenizer.next.type != 'EOF':
            raise ValueError('Unexpected final token type')

        return res
    
    def _parse_expression(self):
        result = 0
        sign = 1

        # Initial state: expecting a number
        token = self.tokenizer.next
        result += sign * self._parse_number(token)

        # State transition: Expecting an operator or end of expression
        while True:
            self.tokenizer.select_next()
            token = self.tokenizer.next

            if token.type == 'EOF':
                break  # End of expression

            self._expect_operator(token)  # State: expecting operator

            # Apply sign based on operator
            if token.type == 'PLUS':
                sign = 1
            elif token.type == 'MINUS':
                sign = -1

            # Next expected state: Number
            self.tokenizer.select_next()
            token = self.tokenizer.next
            result += sign * self._parse_number(token)

        return result

    def _parse_number(self, token):
        if token.type != 'INT':
            raise ValueError('Expected a number, got: ' + token.type)
        return int(token.value)

    def _expect_operator(self, token):
        if token.type not in ['PLUS', 'MINUS']:
            raise ValueError('Expected an operator, got: ' + token.type)


if __name__ == "__main__":
    code = sys.argv[1]
    parser = Parser()
    print(parser.run(code))
