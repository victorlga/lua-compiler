class SymbolTable:

    def __init__(self):
        self.table = {}

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        self.table[key] = value
