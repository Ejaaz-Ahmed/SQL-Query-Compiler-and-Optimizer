from __future__ import annotations
from typing import List, Optional

from ast_nodes import Column, Comparison, Condition, Join, Query, Table, TableList


def table_to_sql(table: Table) -> str:
    if table.alias:
        return f"{table.name} {table.alias}"
    return table.name


def column_to_sql(column: Column, all_tables: List[Table]) -> str:
    if column.name == '*':
        if column.table:
            return f"{column.table}.*"
        return '*'
    if column.table:
        return f"{column.table}.{column.name}"
    if column.resolved_table and len(all_tables) > 1:
        return f"{column.resolved_table}.{column.name}"
    return column.name


def constant_to_sql(constant: object) -> str:
    if isinstance(constant, str):
        return f"'{constant}'"
    return str(constant)


def comparison_to_sql(comp: Comparison, all_tables: List[Table]) -> str:
    left_sql = column_to_sql(comp.left, all_tables) if isinstance(comp.left, Column) else constant_to_sql(comp.left.value)
    right_sql = column_to_sql(comp.right, all_tables) if isinstance(comp.right, Column) else constant_to_sql(comp.right.value)
    return f"{left_sql} {comp.op} {right_sql}"


def condition_to_sql(condition: Condition, all_tables: List[Table], parent_type: Optional[str] = None) -> str:
    if condition.type == 'TRUE':
        return '1=1'
    if condition.type == 'FALSE':
        return '1=0'
    if condition.comp is not None:
        return comparison_to_sql(condition.comp, all_tables)
    if condition.type == 'PAREN' and condition.left is not None and condition.comp is None:
        inner = condition_to_sql(condition.left, all_tables)
        return f"({inner})"
    left_sql = condition_to_sql(condition.left, all_tables, condition.type) if condition.left else ''
    right_sql = condition_to_sql(condition.right, all_tables, condition.type) if condition.right else ''
    connector = f" {condition.type} "
    sql = f"{left_sql}{connector}{right_sql}"
    if parent_type == 'AND' and condition.type == 'OR':
        return f"({sql})"
    return sql


def tablelist_to_sql(table_list: TableList) -> str:
    if table_list.joins:
        sql = table_to_sql(table_list.tables[0])
        for join in table_list.joins:
            sql += f" JOIN {table_to_sql(join.table)} ON {condition_to_sql(join.on, table_list.tables + [join.table])}"
        return sql
    return ', '.join(table_to_sql(table) for table in table_list.tables)


def to_sql(query: Query) -> str:
    all_tables = query.from_clause.tables + [join.table for join in query.from_clause.joins]
    columns = ', '.join(column_to_sql(col, all_tables) for col in query.columns)
    sql = f"SELECT {columns} FROM {tablelist_to_sql(query.from_clause)}"
    if query.where is not None:
        sql += f" WHERE {condition_to_sql(query.where, all_tables)}"
    return sql
