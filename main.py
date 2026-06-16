from __future__ import annotations
import argparse
import json
import sys

from checker import semantic_check
from codegen import to_sql
from lexer import lex
from optimizer import optimize_query
from parser import parse


def main() -> int:
    parser = argparse.ArgumentParser(description='Mini SQL optimizer compiler')
    parser.add_argument('--schema', required=True, help='Path to schema JSON file')
    parser.add_argument('--query', required=True, help='SQL query string to compile')
    parser.add_argument('--debug', action='store_true', help='Print parsed AST and optimization debug output')
    args = parser.parse_args()

    try:
        with open(args.schema, 'r', encoding='utf-8') as schema_file:
            schema = json.load(schema_file)
    except FileNotFoundError:
        print(f"Schema file not found: {args.schema}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"Invalid schema JSON: {exc}")
        return 1

    try:
        tokens = lex(args.query)
        ast = parse(tokens)
    except Exception as exc:
        print(f"Parse error: {exc}")
        return 1

    if args.debug:
        print('Parsed AST:')
        print(ast)

    errors = semantic_check(ast, schema)
    if errors:
        print('Semantic errors:')
        for error in errors:
            print(f'- {error}')
        return 1

    optimized = optimize_query(ast)
    if args.debug:
        print('Optimized AST:')
        print(optimized)

    output_sql = to_sql(optimized)
    print(output_sql)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
