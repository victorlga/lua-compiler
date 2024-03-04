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
        elif value == '(':
            ctype = 'OPAR'
        elif value == ')':
            ctype = 'CPAR'
        elif value == '-':
            ctype = 'MINUS'
        elif value == '+':
            ctype = 'PLUS'
        elif value == '*':
            ctype = 'MULT'
        elif value == '/':
            ctype = 'DIV'
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
        result = self._parse_expression()

        if self.tokenizer.next.type != 'EOF':
            raise ValueError('Unexpected final token type: ' + self.tokenizer.next.type)

        return result

    def _parse_expression(self):

        term = self._parse_term()

        result = term
        token = self.tokenizer.next

        while token.type in ('PLUS', 'MINUS'):
            operator_type = token.type
            self.tokenizer.select_next()
            token = self.tokenizer.next

            term = self._parse_term()

            if operator_type == 'PLUS':
                result += term
            elif operator_type == 'MINUS':
                result -= term

            token = self.tokenizer.next

        return result

    def _parse_term(self):

        factor = self._parse_factor()

        result = factor
        token = self.tokenizer.next

        while token.type in ('MULT', 'DIV'):
            operator_type = token.type
            self.tokenizer.select_next()
            token = self.tokenizer.next

            factor = self._parse_factor()

            if operator_type == 'MULT':
                result *= factor
            elif operator_type == 'DIV':
                result //= factor

            token = self.tokenizer.next
        
        return result

    def _parse_factor(self):

        token = self.tokenizer.next

        if token.type == 'INT':
            result = self._parse_number(token)
        elif token.type == 'PLUS':
            self.tokenizer.select_next()
            factor = self._parse_factor()
            result = +factor
        elif token.type == 'MINUS':
            self.tokenizer.select_next()
            factor = self._parse_factor()
            result = -factor
        elif token.type == 'OPAR':
            self.tokenizer.select_next()
            result = self._parse_expression()
            token = self.tokenizer.next
            if token.type != 'CPAR':
                raise ValueError('Expected CPAR token type, got: ' + token.type)

        self.tokenizer.select_next()

        return result

    def _parse_number(self, token):
        if token.type != 'INT':
            raise ValueError('Expected a number, got: ' + token.type)
        return int(token.value)


if __name__ == "__main__":
    code = sys.argv[1]
    parser = Parser()
    print(parser.run(code))
