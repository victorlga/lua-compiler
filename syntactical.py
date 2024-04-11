from lexical import Tokenizer
from preprocessing import filter
from semantic import (
    BinOpNode, IntValNode, UnOpNode, PrintNode, AssigmentNode, BlockNode,
    IdentifierNode, NoOpNode, ReadNode, IfNode, WhileNode
)

class Parser:

    def __init__(self):
        self.tokenizer = None

    def run(self, raw_source):
        source = filter(raw_source)
        self.tokenizer = Tokenizer(source)
        self.tokenizer.select_next()
        ast_root = self._parse_block()
        return ast_root
    
    def _raise_error_unexpected_token(self, select, *expected_tokens):
        if select:
            self.tokenizer.select_next()
        if self.tokenizer.next.type not in expected_tokens:
            raise ValueError(f'Expected one of {expected_tokens} token types, got: {self.tokenizer.next.type}')

    def _parse_block(self):

        block_node = BlockNode()

        while self.tokenizer.next.type != 'EOF':
            statement = self._parse_statement()
            block_node.children.append(statement)
            self.tokenizer.select_next()

        return block_node

    def _parse_statement(self):

        token = self.tokenizer.next

        if token.type == 'IDENTIFIER':
            identifier_node = IdentifierNode(token.value)

            self._raise_error_unexpected_token(True, 'ASSING')

            assigment_node = AssigmentNode()
            assigment_node.children.append(identifier_node)

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            assigment_node.children.append(bool_expression)

            self._raise_error_unexpected_token(False, 'NEWLINE')

            return assigment_node

        elif token.type == 'PRINT':
            print_node = PrintNode()

            self._raise_error_unexpected_token(True, 'OPEN_PAR')

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            print_node.children.append(bool_expression)

            self._raise_error_unexpected_token(False, 'CLOSE_PAR')
            self._raise_error_unexpected_token(True, 'NEWLINE', 'EOF')

            return print_node

        elif token.type == 'WHILE':
            while_node = WhileNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            while_node.children.append(bool_expression)

            self._raise_error_unexpected_token(False, 'DO')
            
            self._raise_error_unexpected_token(True, 'NEWLINE')
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type != 'END':
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            while_node.children.append(block_node)

            self._raise_error_unexpected_token(True, 'NEWLINE', 'EOF')

            return while_node

        elif token.type == 'IF':
            if_node = IfNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            if_node.children.append(bool_expression)

            self._raise_error_unexpected_token(False, 'THEN')

            self._raise_error_unexpected_token(True, 'NEWLINE')
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type not in ('END', 'ELSE'):
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(block_node)

            if (has_else:=self.tokenizer.next.type == 'ELSE'):
                self._raise_error_unexpected_token(True, 'NEWLINE')
                self.tokenizer.select_next()

            else_block_node = BlockNode()

            while self.tokenizer.next.type != 'END' and has_else:
                statement = self._parse_statement()
                else_block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(else_block_node)

            self._raise_error_unexpected_token(True, 'NEWLINE', 'EOF')

            return if_node

        self._raise_error_unexpected_token(False, 'NEWLINE')

        return NoOpNode()
    
    def _binop_parse_template(self, parsing_func, binop_types):
        expression = parsing_func()
        result = expression
        token = self.tokenizer.next

        while token.type in binop_types:
            binop = BinOpNode(token.value)
            binop.children.append(result)

            self.tokenizer.select_next()
            expression = parsing_func()
            binop.children.append(expression)

            token = self.tokenizer.next
            result = binop

        return result

    def _parse_bool_expression(self):
        return self._binop_parse_template(self._parse_bool_term, {'OR'})

    def _parse_bool_term(self):
        return self._binop_parse_template(self._parse_relational_expression, {'AND'})

    def _parse_relational_expression(self):
        return self._binop_parse_template(self._parse_expression, {'BIGGER', 'LOWER', 'EQUAL'})

    def _parse_expression(self):
        return self._binop_parse_template(self._parse_term, {'PLUS', 'MINUS'})

    def _parse_term(self):
        return self._binop_parse_template(self._parse_factor, {'MULT', 'DIV'})

    def _parse_factor(self):

        token = self.tokenizer.next

        if token.type == 'IDENTIFIER':
            self.tokenizer.select_next()
            return IdentifierNode(token.value)
        elif token.type == 'INT':
            self.tokenizer.select_next()
            return IntValNode(token.value)
        elif token.type in ('PLUS', 'MINUS', 'NOT'):
            self.tokenizer.select_next()
            factor = self._parse_factor()
            unop = UnOpNode(token.value)
            unop.children.append(factor)
            return unop
        elif token.type == 'OPEN_PAR':
            self.tokenizer.select_next()
            expression = self._parse_bool_expression()
            self._raise_error_unexpected_token(False, 'CLOSE_PAR')
            self.tokenizer.select_next()
            return expression
        elif token.type == 'READ':
            self._raise_error_unexpected_token(True, 'OPEN_PAR')
            self._raise_error_unexpected_token(True, 'CLOSE_PAR')
            self.tokenizer.select_next()
            return ReadNode()

