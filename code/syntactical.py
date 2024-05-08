from .tokenizer import Tokenizer
from .preprocessing import filter
from .nodes import (
    BinOpNode, IntValNode, UnOpNode, PrintNode, AssigmentNode, BlockNode,
    IdentifierNode, NoOpNode, ReadNode, IfNode, WhileNode, StringNode,
    VarDecNode, ReturnNode, FuncDecNode, FuncCallNode
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
    
    def _select_and_check_unexpected_token(self, select, *expected_tokens):
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

        # if token.type == 'IDENTIFIER':
        #     identifier_node = IdentifierNode(token.value)

        #     self._select_and_check_unexpected_token(True, 'ASSING')

        #     assigment_node = AssigmentNode()
        #     assigment_node.children.append(identifier_node)

        #     self.tokenizer.select_next()
        #     bool_expression = self._parse_bool_expression()
        #     assigment_node.children.append(bool_expression)

        #     self._select_and_check_unexpected_token(False, 'NEWLINE')
        #     return assigment_node

        if token.type == 'IDENTIFIER':

            self.tokenizer.select_next()
            if self.tokenizer.next.type == 'ASSING':
                identifier_node = IdentifierNode(token.value)
                assigment_node = AssigmentNode()
                assigment_node.children.append(identifier_node)

                self.tokenizer.select_next()
                bool_expression = self._parse_bool_expression()
                assigment_node.children.append(bool_expression)

                self._select_and_check_unexpected_token(False, 'NEWLINE')
                return assigment_node
            elif self.tokenizer.next.type == 'OPEN_PAR':
                func_call_node = FuncCallNode(token.value)
                self.tokenizer.select_next()
                while self.tokenizer.next.type != 'CLOSE_PAR':
                    bool_expression = self._parse_bool_expression()
                    func_call_node.children.append(bool_expression)
                    if self.tokenizer.next.type == 'COMMA':
                        self.tokenizer.select_next()

                self._select_and_check_unexpected_token(True, 'NEWLINE')

                return func_call_node
            else:
                raise ValueError(f'Unexpected token: {self.tokenizer.next.type}')

        elif token.type == 'LOCAL':
            var_dec_node = VarDecNode()

            self._select_and_check_unexpected_token(True, 'IDENTIFIER')

            identifier_node = IdentifierNode(self.tokenizer.next.value)
            var_dec_node.children.append(identifier_node)

            self.tokenizer.select_next()
            if self.tokenizer.next.type == 'ASSING':
                self.tokenizer.select_next()
                bool_expression = self._parse_bool_expression()
                var_dec_node.children.append(bool_expression)
            
            self._select_and_check_unexpected_token(False, 'NEWLINE')
            return var_dec_node

        elif token.type == 'FUNCTION':
            func_dec_node = FuncDecNode()

            self._select_and_check_unexpected_token(True, 'IDENTIFIER')

            identifier_node = IdentifierNode(self.tokenizer.next.value)
            func_dec_node.children.append(identifier_node)

            self._select_and_check_unexpected_token(True, 'OPEN_PAR')

            self.tokenizer.select_next()
            while self.tokenizer.next.type == 'IDENTIFIER':
                identifier_node = IdentifierNode(self.tokenizer.next.value)
                var_dec_node = VarDecNode()
                var_dec_node.children.append(identifier_node)
                func_dec_node.children.append(var_dec_node)
                self.tokenizer.select_next()
                if self.tokenizer.next.type == 'COMMA':
                    self.tokenizer.select_next()
            
            self._select_and_check_unexpected_token(False, 'CLOSE_PAR')
            self._select_and_check_unexpected_token(True, 'NEWLINE')

            block_node = BlockNode()

            self.tokenizer.select_next()
            while self.tokenizer.next.type != 'END':
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            func_dec_node.children.append(block_node)

            return func_dec_node

        elif token.type == 'RETURN':
            ret_node = ReturnNode()
            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            ret_node.children.append(bool_expression)
            self._select_and_check_unexpected_token(False, 'NEWLINE')
            return ret_node

        elif token.type == 'PRINT':
            print_node = PrintNode()

            self._select_and_check_unexpected_token(True, 'OPEN_PAR')

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            print_node.children.append(bool_expression)

            self._select_and_check_unexpected_token(False, 'CLOSE_PAR')
            self._select_and_check_unexpected_token(True, 'NEWLINE', 'EOF')
            return print_node

        elif token.type == 'WHILE':
            while_node = WhileNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            while_node.children.append(bool_expression)

            self._select_and_check_unexpected_token(False, 'DO')
            self._select_and_check_unexpected_token(True, 'NEWLINE')
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type != 'END':
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            while_node.children.append(block_node)

            self._select_and_check_unexpected_token(True, 'NEWLINE', 'EOF')
            return while_node

        elif token.type == 'IF':
            if_node = IfNode()

            self.tokenizer.select_next()
            bool_expression = self._parse_bool_expression()
            if_node.children.append(bool_expression)

            self._select_and_check_unexpected_token(False, 'THEN')
            self._select_and_check_unexpected_token(True, 'NEWLINE')
            
            block_node = BlockNode()
            
            self.tokenizer.select_next()
            while self.tokenizer.next.type not in ('END', 'ELSE'):
                statement = self._parse_statement()
                block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(block_node)

            if (has_else:=self.tokenizer.next.type == 'ELSE'):
                self._select_and_check_unexpected_token(True, 'NEWLINE')
                self.tokenizer.select_next()

            else_block_node = BlockNode()

            while self.tokenizer.next.type != 'END' and has_else:
                statement = self._parse_statement()
                else_block_node.children.append(statement)
                self.tokenizer.select_next()

            if_node.children.append(else_block_node)

            self._select_and_check_unexpected_token(True, 'NEWLINE', 'EOF')
            return if_node

        self._select_and_check_unexpected_token(False, 'NEWLINE')

        return NoOpNode()
    
    def _binop_parse_template(self, parsing_func, binop_types):
        node = parsing_func()
        result = node
        token = self.tokenizer.next

        while token.type in binop_types:
            binop = BinOpNode(token.value)
            binop.children.append(result)

            self.tokenizer.select_next()
            node = parsing_func()
            binop.children.append(node)

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
        return self._binop_parse_template(self._parse_term, {'PLUS', 'MINUS', 'CONCAT'})

    def _parse_term(self):
        return self._binop_parse_template(self._parse_factor, {'MULT', 'DIV'})

    def _parse_factor(self):

        token = self.tokenizer.next

        if token.type == 'IDENTIFIER':
            self.tokenizer.select_next()
            if self.tokenizer.next.type == 'OPEN_PAR':
                func_call_node = FuncCallNode(token.value)
                self.tokenizer.select_next()
                while self.tokenizer.next.type != 'CLOSE_PAR':
                    bool_expression = self._parse_bool_expression()
                    func_call_node.children.append(bool_expression)
                    if self.tokenizer.next.type == 'COMMA':
                        self.tokenizer.select_next()
                self.tokenizer.select_next()
                return func_call_node
            else:
                return IdentifierNode(token.value)
        elif token.type == 'STRING':
            self.tokenizer.select_next()
            return StringNode(token.value)
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
            self._select_and_check_unexpected_token(False, 'CLOSE_PAR')
            self.tokenizer.select_next()
            return expression
        elif token.type == 'READ':
            self._select_and_check_unexpected_token(True, 'OPEN_PAR')
            self._select_and_check_unexpected_token(True, 'CLOSE_PAR')
            self.tokenizer.select_next()
            return ReadNode()
