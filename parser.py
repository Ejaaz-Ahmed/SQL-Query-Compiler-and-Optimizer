from __future__ import annotations
from typing import List

from ast_nodes import Column, Comparison, Condition, Constant, Join, Query, Table, TableList
from lexer import Token, lex

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def eat(self, expected_type: str) -> Token:
        token = self.current
        if token.type != expected_type:
            raise ParseError(f"Expected {expected_type}, found {token.type} ('{token.value}')")
        self.pos += 1
        return token

    def parse(self) -> Query:
        query = self.parse_query()
        if self.current.type == 'SEMICOLON':
            self.eat('SEMICOLON')
        if self.current.type != 'EOF':
            raise ParseError(f"Unexpected token after end of query: {self.current.type}")
        return query

    def parse_query(self) -> Query:
        self.eat('SELECT')
        columns = self.parse_column_list()
        self.eat('FROM')
        from_clause = self.parse_table_list()
        where_clause = None
        if self.current.type == 'WHERE':
            self.eat('WHERE')
            where_clause = self.parse_condition()
        return Query(columns=columns, from_clause=from_clause, where=where_clause)

    def parse_column_list(self) -> List[Column]:
        columns = [self.parse_column()]
        while self.current.type == 'COMMA':
            self.eat('COMMA')
            columns.append(self.parse_column())
        return columns

    def parse_column(self) -> Column:
        if self.current.type == 'STAR':
            self.eat('STAR')
            return Column(table=None, name='*')
        token = self.eat('ID')
        table = token.value
        name = None
        if self.current.type == 'DOT':
            self.eat('DOT')
            if self.current.type == 'STAR':
                self.eat('STAR')
                return Column(table=table, name='*')
            name_token = self.eat('ID')
            name = name_token.value
        else:
            name = table
            table = None
        return Column(table=table, name=name)

    def parse_table(self) -> Table:
        name = self.eat('ID').value
        alias = None
        if self.current.type == 'ID':
            alias = self.eat('ID').value
        return Table(name=name, alias=alias)

    def parse_table_list(self) -> TableList:
        tables = [self.parse_table()]
        joins: List[Join] = []

        if self.current.type == 'JOIN':
            joins.append(self.parse_join())
            while self.current.type == 'JOIN':
                joins.append(self.parse_join())
        else:
            while self.current.type == 'COMMA':
                self.eat('COMMA')
                tables.append(self.parse_table())
        return TableList(tables=tables, joins=joins)

    def parse_join(self) -> Join:
        self.eat('JOIN')
        table = self.parse_table()
        self.eat('ON')
        on_condition = self.parse_condition()
        return Join(table=table, on=on_condition)

    def parse_condition(self) -> Condition:
        left = self.parse_comparison()
        while self.current.type in ('AND', 'OR'):
            op = self.current.type
            self.eat(op)
            right = self.parse_comparison()
            left = Condition(type=op, left=left, right=right)
        return left

    def parse_comparison(self) -> Condition:
        if self.current.type == 'LPAREN':
            self.eat('LPAREN')
            condition = self.parse_condition()
            self.eat('RPAREN')
            return Condition(type='PAREN', left=condition)

        left_operand = self.parse_operand()
        if self.current.type not in ('EQ', 'LT', 'GT'):
            raise ParseError(f"Expected comparison operator, found {self.current.type}")
        op = self.current.value
        self.pos += 1
        right_operand = self.parse_operand()
        return Condition(type='PAREN', comp=Comparison(left=left_operand, op=op, right=right_operand))

    def parse_operand(self) -> Column | Constant:
        if self.current.type == 'ID':
            token = self.eat('ID')
            table = token.value
            if self.current.type == 'DOT':
                self.eat('DOT')
                name_token = self.eat('ID')
                return Column(table=table, name=name_token.value)
            return Column(table=None, name=table)
        if self.current.type == 'NUMBER':
            token = self.eat('NUMBER')
            return Constant(int(token.value))
        if self.current.type == 'STRING':
            token = self.eat('STRING')
            return Constant(token.value)
        raise ParseError(f"Expected column or constant, found {self.current.type}")


def parse(tokens: List[Token]) -> Query:
    return Parser(tokens).parse()


def parse_sql(source: str) -> Query:
    return parse(lex(source))
