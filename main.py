import sys

from syntactical import Parser
from semantic import SymbolTable, ASM


if __name__ == "__main__":
    file_name = sys.argv[1]

    with open(file_name, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    asm = ASM(file_name)
    parser.run(code).evaluate(symbol_table, asm)
    asm.end()
