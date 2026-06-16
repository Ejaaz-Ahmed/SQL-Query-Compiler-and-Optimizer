from __future__ import annotations
from typing import List, Optional

from ast_nodes import Column, Comparison, Condition, Constant, Join, Query, TableList


def evaluate_comparison(comp: Comparison) -> Optional[bool]:
    left_value = comp.left.value if isinstance(comp.left, Constant) else None
    right_value = comp.right.value if isinstance(comp.right, Constant) else None
    if left_value is None or right_value is None:
        return None
    if comp.op == '=':
        return left_value == right_value
    if comp.op == '<':
        return left_value < right_value
    if comp.op == '>':
        return left_value > right_value
    return None


def simplify_condition(condition: Condition) -> Condition:
    if condition.type in ('TRUE', 'FALSE'):
        return condition
    if condition.comp is not None:
        result = evaluate_comparison(condition.comp)
        if result is True:
            return Condition(type='TRUE')
        if result is False:
            return Condition(type='FALSE')
        return condition

    left = simplify_condition(condition.left) if condition.left else None
    right = simplify_condition(condition.right) if condition.right else None
    if left is None or right is None:
        if left is not None:
            return left
        if right is not None:
            return right
        return condition

    if condition.type == 'AND':
        if left.type == 'FALSE' or right.type == 'FALSE':
            return Condition(type='FALSE')
        if left.type == 'TRUE':
            return right
        if right.type == 'TRUE':
            return left
        return Condition(type='AND', left=left, right=right)

    if condition.type == 'OR':
        if left.type == 'TRUE' or right.type == 'TRUE':
            return Condition(type='TRUE')
        if left.type == 'FALSE':
            return right
        if right.type == 'FALSE':
            return left
        return Condition(type='OR', left=left, right=right)

    return Condition(type='PAREN', left=left, comp=None)


def fold_constants(query: Query) -> Query:
    if query.where is None:
        return query
    folded = simplify_condition(query.where)
    if folded.type == 'TRUE':
        query.where = None
    elif folded.type == 'FALSE':
        query.where = Condition(type='PAREN', comp=Comparison(left=Constant(1), op='=', right=Constant(0)))
    else:
        query.where = folded
    return query


def collect_conjuncts(condition: Condition) -> Optional[List[Condition]]:
    if condition.type == 'AND':
        left = collect_conjuncts(condition.left) if condition.left else None
        right = collect_conjuncts(condition.right) if condition.right else None
        if left is None or right is None:
            return None
        return left + right
    if condition.type == 'OR':
        return None
    return [condition]


def condition_tables(condition: Condition) -> set[str]:
    tables: set[str] = set()
    if condition.comp is not None:
        if isinstance(condition.comp.left, Column) and condition.comp.left.resolved_table:
            tables.add(condition.comp.left.resolved_table)
        if isinstance(condition.comp.right, Column) and condition.comp.right.resolved_table:
            tables.add(condition.comp.right.resolved_table)
        return tables
    if condition.left is not None:
        tables.update(condition_tables(condition.left))
    if condition.right is not None:
        tables.update(condition_tables(condition.right))
    return tables


def rebuild_and(conjuncts: List[Condition]) -> Optional[Condition]:
    if not conjuncts:
        return None
    if len(conjuncts) == 1:
        return conjuncts[0]
    left = conjuncts[0]
    right = rebuild_and(conjuncts[1:])
    return Condition(type='AND', left=left, right=right)


def pushdown_predicates(query: Query) -> Query:
    if query.where is None:
        return query

    conjuncts = collect_conjuncts(query.where)
    if conjuncts is None:
        return query

    if not query.from_clause.joins:
        return query

    remaining: List[Condition] = []
    for conjunct in conjuncts:
        target_join: Optional[Join] = None
        tables = condition_tables(conjunct)
        if len(tables) == 1:
            table_name = next(iter(tables))
            for join in query.from_clause.joins:
                if join.table.name == table_name:
                    target_join = join
                    break
        if target_join is not None:
            if target_join.on.type == 'TRUE' or target_join.on.type == 'FALSE':
                target_join.on = conjunct
            else:
                target_join.on = Condition(type='AND', left=target_join.on, right=conjunct)
        else:
            remaining.append(conjunct)

    query.where = rebuild_and(remaining)
    return query


def optimize_query(query: Query) -> Query:
    query = fold_constants(query)
    query = pushdown_predicates(query)
    return query
