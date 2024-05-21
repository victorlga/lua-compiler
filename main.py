import sys

from code.syntactical import Parser
from code.asm import ASM
from code.table import SymbolTable


if __name__ == "__main__":
    filename = sys.argv[1]

    with open(filename, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    asm_file = filename.split('.')[0] + '.asm'
    ASM.initialize(asm_file)
    parser.run(code).evaluate(symbol_table)
    ASM.end()
