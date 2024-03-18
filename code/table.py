class SymbolTable:

    def __init__(self):
        self.dict = {}

    def getter(self, key):
        return self.dict[key]

    def setter(self, key, value):
        self.dict[key] = value
