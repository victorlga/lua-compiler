import sys

from code.syntactical import Parser
from code.nodes import SymbolTable


if __name__ == "__main__":
    file_name = sys.argv[1]

    with open(file_name, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    parser.run(code).evaluate(symbol_table)
