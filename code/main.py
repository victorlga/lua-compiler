import sys
import re

from token import Tokenizer
from node import (BinOpNode, IntValNode, UnOpNode, PrintNode,
                  AssigmentNode, BlockNode, IdentifierNode, NoOpNode)
from table import SymbolTable

class PreProcessing:

    @staticmethod
    def filter(code):
        pattern = r'--.*'
        return re.sub(pattern, '', code)

class Parser:

    def __init__(self):
        self.tokenizer = None

    def run(self, code):
        code = PreProcessing.filter(code)
        self.tokenizer = Tokenizer(code)
        self.tokenizer.select_next()
        ast_root = self._parse_expression()

        return ast_root
    
    def _parse_block(self):

        block_node = BlockNode()

        while self.tokenizer.next.type != 'EOF':

            self.tokenizer.select_next()
            statement = self._parse_statement()
            block_node.children.append(statement)

        return block_node

    def _parse_statement(self):
        
        token = self.tokenizer.next

        if token.type == 'IDENTIFIER':
            identifier_node = IdentifierNode(token.value)

            self.tokenizer.select_next()
            if token.type != 'EQ':
                raise ValueError('Expected EQ token type, got: ' + token.type)
            assigment_node = AssigmentNode()
            assigment_node.children.append(identifier_node)

            self.tokenizer.select_next()
            expression = self._parse_expression()
            assigment_node.children.append(expression)

            self.tokenizer.select_next()
            if token.type != 'NEWLINE':
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)

            return assigment_node

        elif token.type == 'PRINT':
            print_node = PrintNode()

            self.tokenizer.select_next()
            expression = self._parse_expression()
            print_node.children.append(expression)

            token = self.tokenizer.next
            if token.type != 'CLOSE_PAR':
                raise ValueError('Expected CLOSE_PAR token type, got: ' + token.type)

            self.tokenizer.select_next()
            if token.type != 'NEWLINE':
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)

            return print_node

        self.tokenizer.select_next()
        if token.type != 'NEWLINE':
            raise ValueError('Expected NEWLINE token type, got: ' + token.type)

        return NoOpNode()


    def _parse_expression(self):

        term = self._parse_term()
        expression = term
        token = self.tokenizer.next

        while token.type in ('PLUS', 'MINUS'):

            binop = BinOpNode(token.value)
            binop.children.append(expression)

            self.tokenizer.select_next()
            term = self._parse_term()
            binop.children.append(term)

            token = self.tokenizer.next
            expression = binop

        return expression

    def _parse_term(self):

        factor = self._parse_factor()
        term = factor
        token = self.tokenizer.next

        while token.type in ('MULT', 'DIV'):

            binop = BinOpNode(token.value)
            binop.children.append(term)

            self.tokenizer.select_next()
            factor = self._parse_factor()
            binop.children.append(factor)

            token = self.tokenizer.next
            term = binop

        return term

    def _parse_factor(self):

        token = self.tokenizer.next

        if token.type == 'INT':
            factor = IntValNode(token.value)
            self.tokenizer.select_next()
            return factor
        elif token.type in ('PLUS', 'MINUS'):
            self.tokenizer.select_next()
            factor = self._parse_factor()
            unop = UnOpNode(token.value)
            unop.children.append(factor)
            return unop
        elif token.type == 'OPEN_PAR':
            self.tokenizer.select_next()
            expression = self._parse_expression()
            token = self.tokenizer.next
            if token.type != 'CLOSE_PAR':
                raise ValueError('Expected CLOSE_PAR token type, got: ' + token.type)
            self.tokenizer.select_next()
            return expression


if __name__ == "__main__":
    file_name = sys.argv[1]

    with open(file_name, 'r') as file:
        code = file.read()

    parser = Parser()
    symbol_table = SymbolTable()
    print(parser.run(code).evaluate(symbol_table))
