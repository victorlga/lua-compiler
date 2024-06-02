class SymbolTable:

    def __init__(self):
        self.table = {}
        self.address = 4

    def create(self, key, shift=0, sign=1):
        if key in self.table:
            raise RuntimeError(f'Key {key} already created.')
        self.table[key] = (self.address + shift) * sign
        self.address += 4

    def get(self, key):
        return self.table[key]

    def set(self, key, address):
        if key in self.table:
            self.table[key] = address
        else:
            raise RuntimeError(f'Key {key} does not exist.')
        
class FuncTable:

    table = {}

    @staticmethod
    def set(key, value):
        FuncTable.table[key] = value

    @staticmethod
    def get(key):
        return FuncTable.table.get(key)
