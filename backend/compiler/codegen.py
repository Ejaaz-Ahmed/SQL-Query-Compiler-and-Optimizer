"""Code generator: convert optimized AST back to SQL."""
from typing import List, Union
from .ast_nodes import Column, Comparison, Condition, Constant, Join, Query, Table, TableList

def format_table(table: Table) -> str:
    """Format a table reference with optional alias."""
    if table.alias:
        return f"{table.name} {table.alias}"
    return table.name


def format_column(column: Column, need_table_prefix: bool = False) -> str:
    """
    Format a column reference.
    If need_table_prefix is True, always qualify with table name.
    """
    if column.name == '*':
        if column.table:
            return f"{column.table}.*"
        return '*'
    if column.table:
        return f"{column.table}.{column.name}"
    if need_table_prefix and column.resolved_table:
        return f"{column.resolved_table}.{column.name}"
    return column.name

def format_constant(constant: Constant) -> str:
    """Format a constant value."""
    if isinstance(constant.value, str):
        return f"'{constant.value}'"
    return str(constant.value)

def format_comparison(comp: Comparison, need_table_prefix: bool = False) -> str:
    """Format a comparison expression."""
    if isinstance(comp.left, Column):
        left_str = format_column(comp.left, need_table_prefix)
    else:
        left_str = format_constant(comp.left)

    if isinstance(comp.right, Column):
        right_str = format_column(comp.right, need_table_prefix)
    else:
        right_str = format_constant(comp.right)

    return f"{left_str} {comp.op} {right_str}"

def format_condition(condition: Condition, need_table_prefix: bool = False, parent_type: str = None) -> str:
    """
    Format a condition expression.
    Parenthesizes OR inside AND when needed.
    """
    if condition.type == 'TRUE':
        return '1=1'
    elif condition.type == 'FALSE':
        return '1=0'
    elif condition.comp:
        return format_comparison(condition.comp, need_table_prefix)
    elif condition.type == 'AND':
        left_str = format_condition(condition.left, need_table_prefix, 'AND') if condition.left else ''
        right_str = format_condition(condition.right, need_table_prefix, 'AND') if condition.right else ''
        result = f"{left_str} AND {right_str}"
        return result
    elif condition.type == 'OR':
        left_str = format_condition(condition.left, need_table_prefix, 'OR') if condition.left else ''
        right_str = format_condition(condition.right, need_table_prefix, 'OR') if condition.right else ''
        result = f"{left_str} OR {right_str}"
        # Parenthesize if parent is AND
        if parent_type == 'AND':
            result = f"({result})"
        return result
    else:
        return '1=1'

def to_sql(query: Query) -> str:
    """
    Convert an optimized AST back to SQL.
    Returns a formatted SQL string.
    """
    # Determine all table names in the query
    all_tables = [table.name for table in query.from_clause.tables]
    for join in query.from_clause.joins:
        all_tables.append(join.table.name)

    # Format columns
    need_qualify = len(all_tables) > 1
    columns_str = ', '.join(
        format_column(col, need_qualify) for col in query.columns
    )

    # Format FROM clause
    from_str = format_table(query.from_clause.tables[0])
    for join in query.from_clause.joins:
        on_str = format_condition(join.on, need_qualify)
        from_str += f" JOIN {format_table(join.table)} ON {on_str}"

    # Add comma-separated tables if any
    if len(query.from_clause.tables) > 1:
        from_str += ', ' + ', '.join(format_table(t) for t in query.from_clause.tables[1:])

    sql = f"SELECT {columns_str} FROM {from_str}"

    # Format WHERE clause
    if query.where:
        where_str = format_condition(query.where, need_qualify)
        sql += f" WHERE {where_str}"

    return sql
