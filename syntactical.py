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

            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'ASSING':
                raise ValueError('Expected ASSING token type, got: ' + token.type)
            assigment_node = AssigmentNode()
            assigment_node.children.append(identifier_node)

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            assigment_node.children.append(bool_expression)

            token = self.tokenizer.next
            if token.type != 'NEWLINE':
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)

            return assigment_node

        elif token.type == 'PRINT':
            print_node = PrintNode()

            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'OPEN_PAR':
                raise ValueError('Expected OPEN_PAR token type, got: ' + token.type)

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            print_node.children.append(bool_expression)

            token = self.tokenizer.next
            if token.type != 'CLOSE_PAR':
                raise ValueError('Expected CLOSE_PAR token type, got: ' + token.type)
            self.tokenizer.select_next()

            token = self.tokenizer.next
            if token.type not in ('NEWLINE', 'EOF'):
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)

            return print_node

        elif token.type == 'WHILE':
            while_node = WhileNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            while_node.children.append(bool_expression)

            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'DO':
                raise ValueError('Expected DO token type, got: ' + token.type)
            
            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'NEWLINE':
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type != 'END':
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            while_node.children.append(block_node)

        elif token.type == 'IF':
            if_node = IfNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            if_node.children.append(bool_expression)

            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'THEN':
                raise ValueError('Expected THEN token type, got: ' + token.type)
            
            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'NEWLINE':
                raise ValueError('Expected NEWLINE token type, got: ' + token.type)
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type not in ('END', 'ELSE'):
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(block_node)

            if (has_else:=self.tokenizer.next.type == 'ELSE'):
                self.tokenizer.select_next()
                token = self.tokenizer.next
                if token.type != 'NEWLINE':
                    raise ValueError('Expected NEWLINE token type, got: ' + token.type)
                self.tokenizer.select_next()

            else_block_node = BlockNode()

            while self.tokenizer.next.type != 'END' and has_else:
                statement = self._parse_statement()
                else_block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(else_block_node)

        token = self.tokenizer.next
        if token.type != 'NEWLINE':
            raise ValueError('Expected NEWLINE token type, got: ' + token.type)

        return NoOpNode()

    def _parse_bool_expression(self):
        bool_term = self._parse_bool_term()
        bool_expression = bool_term
        token = self.tokenizer.next

        while token.type == 'OR':

            binop = BinOpNode(token.value)
            binop.children.append(bool_expression)

            self.tokenizer.select_next()
            bool_term = self._parse_bool_term()
            binop.children.append(bool_term)

            token = self.tokenizer.next
            bool_expression = binop

        return bool_expression

    def _parse_bool_term(self):
        
        relational_expression = self._parse_relational_expression()
        bool_term = relational_expression
        token = self.tokenizer.next

        while token.type == 'AND':

            binop = BinOpNode(token.value)
            binop.children.append(bool_term)

            self.tokenizer.select_next()
            relational_expression = self._parse_relational_expression()
            binop.children.append(relational_expression)

            token = self.tokenizer.next
            bool_term = binop

        return bool_term

    def _parse_relational_expression(self):
        expression = self._parse_expression()
        relational_expression = expression
        token = self.tokenizer.next

        while token.type in ('BIGGER', 'LOWER', 'EQUAL'):

            binop = BinOpNode(token.value)
            binop.children.append(relational_expression)

            self.tokenizer.select_next()
            expression = self._parse_expression()
            binop.children.append(expression)

            token = self.tokenizer.next
            relational_expression = binop

        return relational_expression


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
            token = self.tokenizer.next
            if token.type != 'CLOSE_PAR':
                raise ValueError('Expected CLOSE_PAR token type, got: ' + token.type)
            self.tokenizer.select_next()
            return expression
        elif token.type == 'READ':
            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'OPEN_PAR':
                raise ValueError('Expected OPEN_PAR token type, got: ' + token.type)
            self.tokenizer.select_next()
            token = self.tokenizer.next
            if token.type != 'CLOSE_PAR':
                raise ValueError('Expected CLOSE_PAR token type, got: ' + token.type)
            self.tokenizer.select_next()
            return ReadNode()

