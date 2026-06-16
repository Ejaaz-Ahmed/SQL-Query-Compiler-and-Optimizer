from __future__ import annotations
from typing import Dict, List, Optional

from ast_nodes import Column, Condition, Query, Table, TableList


def semantic_check(query: Query, schema: Dict[str, List[str]]) -> List[str]:
    errors: List[str] = []
    tables = list(query.from_clause.tables)
    for join in query.from_clause.joins:
        tables.append(join.table)

    table_names = {table.name for table in tables}

    alias_map: Dict[str, str] = {}
    for table in tables:
        alias_map[table.name] = table.name
        if table.alias:
            alias_map[table.alias] = table.name

    def check_table(table: Table) -> None:
        if table.name not in schema:
            errors.append(f"Unknown table: {table.name}")

    for table in tables:
        check_table(table)

    def resolve_table_ref(table_ref: str) -> Optional[str]:
        return alias_map.get(table_ref)

    def resolve_column(column: Column) -> None:
        if column.name == '*':
            if column.table:
                actual_table = resolve_table_ref(column.table)
                if actual_table is None:
                    errors.append(f"Unknown table in column reference: {column.table}")
                else:
                    column.resolved_table = actual_table
            return

        if column.table:
            actual_table = resolve_table_ref(column.table)
            if actual_table is None:
                errors.append(f"Unknown table in column reference: {column.table}")
                return
            if column.name not in schema[actual_table]:
                errors.append(f"Unknown column: {column.table}.{column.name}")
                return
            column.resolved_table = actual_table
            return

        matches = [table.name for table in tables if table.name in schema and column.name in schema[table.name]]
        if not matches:
            errors.append(f"Unknown column: {column.name}")
            return
        if len(matches) > 1:
            errors.append(f"Ambiguous column: {column.name}")
            return
        column.resolved_table = matches[0]

    def walk_condition(condition: Condition) -> None:
        if condition.comp is not None:
            if isinstance(condition.comp.left, Column):
                resolve_column(condition.comp.left)
            if isinstance(condition.comp.right, Column):
                resolve_column(condition.comp.right)
            return
        if condition.left:
            walk_condition(condition.left)
        if condition.right:
            walk_condition(condition.right)

    for column in query.columns:
        resolve_column(column)

    if query.where is not None:
        walk_condition(query.where)

    for join in query.from_clause.joins:
        if join.on is not None:
            walk_condition(join.on)

    return errors
