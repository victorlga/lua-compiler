class SymbolTable:

    def __init__(self):
        self.table = {}
        self.address = 4

    def create(self, key):
        if key in self.table:
            raise RuntimeError(f'Key {key} already created.')
        self.table[key] = (None, None, self.address)
        self.address += 4

    def get(self, key):
        return self.table[key]

    def set(self, key, value):
        if key in self.table:
            self.table[key] = value
        else:
            raise RuntimeError(f'Key {key} does not exist.')