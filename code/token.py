class Token:

    def __init__(self, type:str, value:str):
        self.type: str = type
        self.value: str = value

class Tokenizer:

    def __init__(self, source:str):
        self.source: str = source
        self.position: int = 0
        self.next: Token = None
        self.reserved_words_types = {
            'print': 'PRINT',
        }

    def select_next(self):

        value = self._define_value()
        while value == ' ' or value == '\n':
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
        elif value == '=':
            ctype = 'EQ'
        elif value.isdigit():
            while value.isdigit():
                self.position += 1
                value += self._define_value(fallback=' ')
            value = value[:-1]
            ctype = 'INT'
            self.position -= 1
        elif value.isalpha():
            while value.isalpha() or value.isdigit():
                self.position += 1
                value += self._define_value(fallback=' ')
            value = value[:-1]
            self.position -= 1
            is_reserved_word = value in self.reserved_words_types.keys()
            ctype = self.reserved_words_types[value] if is_reserved_word else 'IDEN'
        else:
            raise ValueError('Not a valid character: ' + value)

        self.position += 1

        self.next = Token(ctype, value)
    
    def _end_of_file(self):
        return self.position >= len(self.source)
    
    def _define_value(self, fallback=''):
        return fallback if self._end_of_file() else self.source[self.position]
