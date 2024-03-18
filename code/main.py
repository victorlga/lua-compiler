import sys

from syntactical import Parser
from semantic import SymbolTable


if __name__ == "__main__":
    file_name = sys.argv[1]

    with open(file_name, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    print(parser.run(code).evaluate(symbol_table))
