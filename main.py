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

    def end_of_file(self):
        return self.position >= len(self.source)
    
    def define_value(self, fallback=''):
        return fallback if self.end_of_file() else self.source[self.position]

    def select_next(self):

        value = self.define_value()
        while value == ' ':
            self.position += 1
            value = self.define_value()

        if self.end_of_file():
            ctype = 'EOF'
        elif value == '-':
            ctype = 'MINUS'
        elif value == '+':
            ctype = 'PLUS'
        elif value.isdigit():
            while value.isdigit():
                self.position += 1
                value += self.define_value(fallback=' ')
            value = value[:-1]
            ctype = 'INT'
            self.position -= 1
        else:
            raise ValueError

        self.position += 1

        self.next = Token(ctype, value)


class Parser:

    def __init__(self):
        self.tokenizer: Tokenizer = None
    
    def parseExpression(self):
        pass

    def run(self, code: str):
        pass


if __name__ == "__main__":
    # code = sys.argv[1]
    # parser = Parser()
    # parser.run(code)
    src = ''
    tokenizer = Tokenizer(src)

    tokenizer.select_next()
    print(tokenizer.next.value)
    tokenizer.select_next()
    print(tokenizer.next.value)
    tokenizer.select_next()
    print(tokenizer.next.value)
