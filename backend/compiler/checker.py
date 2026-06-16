"""Semantic checker for SQL queries."""
from typing import Dict, List, Optional
from .ast_nodes import Column, Condition, Query

def check(query: Query, schema: Dict[str, List[str]]) -> List[str]:
    """
    Perform semantic checks on a parsed query.

    Args:
        query: The parsed Query AST
        schema: Dictionary mapping table names to column lists

    Returns:
        List of error strings (empty if no errors)
    """
    errors = []

    # Map aliases (and table names) to actual schema table names
    alias_map: Dict[str, str] = {}
    for table in query.from_clause.tables:
        alias_map[table.name] = table.name
        if table.alias:
            alias_map[table.alias] = table.name
    for join in query.from_clause.joins:
        alias_map[join.table.name] = join.table.name
        if join.table.alias:
            alias_map[join.table.alias] = join.table.name

    # Get all table names in the query
    tables = {table.name for table in query.from_clause.tables}
    for join in query.from_clause.joins:
        tables.add(join.table.name)

    # Check that all tables exist
    for table_name in tables:
        if table_name not in schema:
            errors.append(f"Unknown table: {table_name}")

    if errors:
        return errors

    def resolve_table_ref(table_ref: str) -> Optional[str]:
        return alias_map.get(table_ref)

    def resolve_column(column: Column) -> None:
        """Resolve a column reference to a specific table."""
        if column.name == '*':
            if column.table:
                actual_table = resolve_table_ref(column.table)
                if actual_table is None:
                    errors.append(f"Unknown table: {column.table}")
                else:
                    column.resolved_table = actual_table
            return

        if column.table:
            # Qualified column reference (may use a table alias)
            actual_table = resolve_table_ref(column.table)
            if actual_table is None:
                errors.append(f"Unknown table: {column.table}")
                return
            if column.name not in schema[actual_table]:
                errors.append(f"Unknown column: {column.table}.{column.name}")
                return
            column.resolved_table = actual_table
        else:
            # Unqualified column reference - must appear in exactly one table
            matching_tables = [
                table_name for table_name in tables
                if column.name in schema[table_name]
            ]
            if not matching_tables:
                errors.append(f"Unknown column: {column.name}")
            elif len(matching_tables) > 1:
                errors.append(f"Ambiguous column: {column.name}")
            else:
                column.resolved_table = matching_tables[0]

    def walk_condition(condition: Condition) -> None:
        """Walk and check all column references in a condition."""
        if condition.comp:
            # Check left operand
            if isinstance(condition.comp.left, Column):
                resolve_column(condition.comp.left)
            # Check right operand
            if isinstance(condition.comp.right, Column):
                resolve_column(condition.comp.right)
        else:
            # Recursive walk for AND/OR conditions
            if condition.left:
                walk_condition(condition.left)
            if condition.right:
                walk_condition(condition.right)

    # Check columns in SELECT list
    for column in query.columns:
        resolve_column(column)

    # Check columns in WHERE clause
    if query.where:
        walk_condition(query.where)

    # Check columns in JOIN ON clauses
    for join in query.from_clause.joins:
        if join.on:
            walk_condition(join.on)

    return errors
