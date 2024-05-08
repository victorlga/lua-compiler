class SymbolTable:

    def __init__(self):
        self.table = {}

    def create(self, key):
        if key in self.table:
            raise RuntimeError(f'Key {key} already created.')
        self.table[key] = None

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        if key in self.table:
            self.table[key] = value
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
