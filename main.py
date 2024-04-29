import sys

from syntactical import Parser
from semantic import SymbolTable, ASM


if __name__ == "__main__":
    filename = sys.argv[1]

    with open(filename, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    asm_file = filename.split('.')[0] + '.asm'
    asm = ASM(asm_file)
    parser.run(code).evaluate(symbol_table, asm)
    asm.end()
