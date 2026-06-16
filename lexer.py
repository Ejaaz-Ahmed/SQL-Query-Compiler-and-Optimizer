from __future__ import annotations
from dataclasses import dataclass
import re
from typing import List

KEYWORDS = {
    'SELECT': 'SELECT',
    'FROM': 'FROM',
    'WHERE': 'WHERE',
    'JOIN': 'JOIN',
    'ON': 'ON',
    'AND': 'AND',
    'OR': 'OR',
}

TOKEN_REGEX = re.compile(r"""
\s*(?P<NUMBER>[0-9]+)
|\s*(?P<STRING>'[^']*')
|\s*(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)
|\s*(?P<COMMA>,)
|\s*(?P<DOT>\.)
|\s*(?P<STAR>\*)
|\s*(?P<SEMICOLON>;)
|\s*(?P<EQ>=)
|\s*(?P<LT><)
|\s*(?P<GT>>)
|\s*(?P<LPAREN>\()
|\s*(?P<RPAREN>\))
""", re.VERBOSE)

@dataclass
class Token:
    type: str
    value: str


def lex(source: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0

    while pos < len(source):
        match = TOKEN_REGEX.match(source, pos)
        if not match:
            raise ValueError(f"Unexpected token at position {pos}: {source[pos:]}")

        pos = match.end()
        token_type = match.lastgroup
        token_value = match.group(token_type)

        if token_type == 'ID':
            upper_value = token_value.upper()
            token_type = KEYWORDS.get(upper_value, 'ID')
            token_value = token_value
        elif token_type == 'STRING':
            token_value = token_value[1:-1]

        tokens.append(Token(token_type, token_value))

    tokens.append(Token('EOF', ''))
    return tokens
