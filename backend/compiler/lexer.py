"""Lexical analyzer for SQL subset."""
import re
from typing import List, Tuple

# Token type constants
TOKEN_TYPES = {
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'AND', 'OR',
    'ID', 'NUMBER', 'STRING', 'COMMA', 'DOT', 'STAR', 'SEMICOLON',
    'EQ', 'LT', 'GT', 'LPAREN', 'RPAREN', 'EOF'
}

KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'AND', 'OR'
}

class Token:
    """Represents a single token."""
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

def tokenize(source: str) -> List[Token]:
    """
    Tokenize a SQL query string into a list of tokens.

    Args:
        source: The SQL query string

    Returns:
        A list of Token objects

    Raises:
        SyntaxError: If an unexpected character is encountered
    """
    tokens = []
    pos = 0

    # Regex pattern to match tokens
    pattern = re.compile(r"""
        \s*(?P<NUMBER>\d+)
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
        |\s+
    """, re.VERBOSE)

    while pos < len(source):
        match = pattern.match(source, pos)
        if not match:
            raise SyntaxError(f"Unexpected character at position {pos}: {source[pos]}")

        pos = match.end()
        token_type = match.lastgroup

        if token_type is None:  # Whitespace
            continue

        token_value = match.group(token_type)

        if token_type == 'ID':
            upper_value = token_value.upper()
            token_type = upper_value if upper_value in KEYWORDS else 'ID'
        elif token_type == 'STRING':
            # Remove quotes and store the content
            token_value = token_value[1:-1]

        tokens.append(Token(token_type, token_value))

    tokens.append(Token('EOF', ''))
    return tokens
