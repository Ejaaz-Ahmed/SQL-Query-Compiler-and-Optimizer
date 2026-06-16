"""Recursive descent parser for SQL subset."""
from typing import List, Union, Optional
from .ast_nodes import (
    Query, Column, Table, Constant, Comparison, Condition,
    Join, TableList
)
from .lexer import Token, tokenize

class ParseError(Exception):
    """Raised when a parse error occurs."""
    pass

class Parser:
    """Recursive descent parser for SQL queries."""
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        """Get the current token."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def eat(self, expected_type: str) -> Token:
        """Consume a token of the expected type."""
        token = self.current
        if token.type != expected_type:
            raise ParseError(
                f"Expected {expected_type}, got {token.type} ('{token.value}')"
            )
        self.pos += 1
        return token

    def parse_query(self) -> Query:
        """Parse a SELECT query."""
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
        """Parse a comma-separated list of columns."""
        columns = [self.parse_column()]
        while self.current.type == 'COMMA':
            self.eat('COMMA')
            columns.append(self.parse_column())
        return columns

    def parse_column(self) -> Column:
        """Parse a single column reference (e.g., 'col', 'table.col', or '*')."""
        if self.current.type == 'STAR':
            self.eat('STAR')
            return Column(table=None, name='*')
        token = self.eat('ID')
        first = token.value
        if self.current.type == 'DOT':
            self.eat('DOT')
            if self.current.type == 'STAR':
                self.eat('STAR')
                return Column(table=first, name='*')
            name_token = self.eat('ID')
            return Column(table=first, name=name_token.value)
        return Column(table=None, name=first)

    def parse_table(self) -> Table:
        """Parse a table reference with an optional alias (e.g., 'employees e')."""
        name = self.eat('ID').value
        alias = None
        if self.current.type == 'ID':
            alias = self.eat('ID').value
        return Table(name=name, alias=alias)

    def parse_table_list(self) -> TableList:
        """Parse the FROM clause (tables and joins)."""
        tables = [self.parse_table()]
        joins = []

        # Parse joins or comma-separated tables
        while self.current.type in ('JOIN', 'COMMA'):
            if self.current.type == 'JOIN':
                joins.append(self.parse_join())
            elif self.current.type == 'COMMA':
                self.eat('COMMA')
                tables.append(self.parse_table())

        return TableList(tables=tables, joins=joins)

    def parse_join(self) -> Join:
        """Parse a JOIN clause."""
        self.eat('JOIN')
        table = self.parse_table()
        self.eat('ON')
        on_condition = self.parse_condition()
        return Join(table=table, on=on_condition)

    def parse_condition(self) -> Condition:
        """Parse a WHERE condition (handles AND/OR precedence)."""
        left = self.parse_or_condition()
        return left

    def parse_or_condition(self) -> Condition:
        """Parse OR conditions."""
        left = self.parse_and_condition()
        while self.current.type == 'OR':
            self.eat('OR')
            right = self.parse_and_condition()
            left = Condition(type='OR', left=left, right=right)
        return left

    def parse_and_condition(self) -> Condition:
        """Parse AND conditions."""
        left = self.parse_comparison()
        while self.current.type == 'AND':
            self.eat('AND')
            right = self.parse_comparison()
            left = Condition(type='AND', left=left, right=right)
        return left

    def parse_comparison(self) -> Condition:
        """Parse a single comparison or parenthesized condition."""
        if self.current.type == 'LPAREN':
            self.eat('LPAREN')
            condition = self.parse_condition()
            self.eat('RPAREN')
            return condition

        left = self.parse_operand()
        op = self.eat('EQ' if self.current.type == 'EQ' else
                      'LT' if self.current.type == 'LT' else
                      'GT' if self.current.type == 'GT' else 'EQ').value
        right = self.parse_operand()

        return Condition(type='COMP', comp=Comparison(left=left, op=op, right=right))

    def parse_operand(self) -> Union[Column, Constant]:
        """Parse a column or constant operand."""
        if self.current.type == 'ID':
            token = self.eat('ID')
            first = token.value
            if self.current.type == 'DOT':
                self.eat('DOT')
                name_token = self.eat('ID')
                return Column(table=first, name=name_token.value)
            return Column(table=None, name=first)
        elif self.current.type == 'NUMBER':
            token = self.eat('NUMBER')
            return Constant(int(token.value))
        elif self.current.type == 'STRING':
            token = self.eat('STRING')
            return Constant(token.value)
        else:
            raise ParseError(
                f"Expected column or constant, got {self.current.type}"
            )

def parse(tokens: List[Token]) -> Query:
    """
    Parse a token list into an AST.

    Args:
        tokens: List of tokens from the lexer

    Returns:
        A Query AST node

    Raises:
        ParseError: If parsing fails
    """
    parser = Parser(tokens)
    query = parser.parse_query()
    if parser.current.type == 'SEMICOLON':
        parser.eat('SEMICOLON')
    if parser.current.type != 'EOF':
        raise ParseError(f"Unexpected token: {parser.current.type}")
    return query

def parse_sql(source: str) -> Query:
    """Parse a SQL query string directly."""
    tokens = tokenize(source)
    return parse(tokens)
