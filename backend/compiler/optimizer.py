"""Query optimization passes."""
import copy
from typing import List, Optional, Tuple
from .ast_nodes import Column, Comparison, Condition, Constant, Join, Query

def evaluate_constant_comparison(comp: Comparison) -> Optional[bool]:
    """
    Evaluate a comparison if both operands are constants.

    Returns:
        True, False, or None if not evaluable
    """
    left_val = None
    right_val = None

    if isinstance(comp.left, Constant):
        left_val = comp.left.value
    else:
        return None

    if isinstance(comp.right, Constant):
        right_val = comp.right.value
    else:
        return None

    try:
        if comp.op == '=':
            return left_val == right_val
        elif comp.op == '<':
            return left_val < right_val
        elif comp.op == '>':
            return left_val > right_val
    except TypeError:
        # Can't compare different types
        return None

    return None

def simplify_condition(condition: Condition) -> Condition:
    """
    Recursively simplify a condition by constant folding.
    Evaluates constant comparisons and simplifies AND/OR expressions.
    """
    if condition.type in ('TRUE', 'FALSE'):
        return condition

    # Base case: a single comparison
    if condition.comp:
        result = evaluate_constant_comparison(condition.comp)
        if result is True:
            return Condition(type='TRUE')
        elif result is False:
            return Condition(type='FALSE')
        else:
            return condition

    # Recursive case: AND/OR
    left = simplify_condition(condition.left) if condition.left else None
    right = simplify_condition(condition.right) if condition.right else None

    if condition.type == 'AND':
        # FALSE AND anything = FALSE
        if left and left.type == 'FALSE':
            return Condition(type='FALSE')
        if right and right.type == 'FALSE':
            return Condition(type='FALSE')
        # TRUE AND X = X
        if left and left.type == 'TRUE':
            return right if right else Condition(type='TRUE')
        if right and right.type == 'TRUE':
            return left if left else Condition(type='TRUE')
        # Both sides exist
        if left and right:
            return Condition(type='AND', left=left, right=right)
        return left or right or Condition(type='TRUE')

    elif condition.type == 'OR':
        # TRUE OR anything = TRUE
        if left and left.type == 'TRUE':
            return Condition(type='TRUE')
        if right and right.type == 'TRUE':
            return Condition(type='TRUE')
        # FALSE OR X = X
        if left and left.type == 'FALSE':
            return right if right else Condition(type='FALSE')
        if right and right.type == 'FALSE':
            return left if left else Condition(type='FALSE')
        # Both sides exist
        if left and right:
            return Condition(type='OR', left=left, right=right)
        return left or right or Condition(type='FALSE')

    return condition

def constant_folding(query: Query) -> Query:
    """
    Perform constant folding optimization on the query.
    - Evaluates constant-only comparisons
    - Simplifies AND/OR expressions
    - Removes WHERE clause if it becomes TRUE
    - Adds WHERE 1=0 if it becomes FALSE
    """
    if not query.where:
        return query

    folded = simplify_condition(query.where)

    if folded.type == 'TRUE':
        query.where = None
    elif folded.type == 'FALSE':
        # Replace entire WHERE with a contradiction
        query.where = Condition(
            type='COMP',
            comp=Comparison(left=Constant(1), op='=', right=Constant(0))
        )
    else:
        query.where = folded

    return query

def collect_conjuncts(condition: Condition) -> Optional[List[Condition]]:
    """
    If condition is a chain of ANDs, return list of conjuncts.
    Otherwise return None.
    """
    if condition.type == 'AND':
        left_list = collect_conjuncts(condition.left) if condition.left else None
        right_list = collect_conjuncts(condition.right) if condition.right else None
        if left_list is None or right_list is None:
            return None
        return left_list + right_list
    elif condition.type == 'OR':
        return None
    elif condition.type in ('TRUE', 'FALSE'):
        return None
    else:
        return [condition]

def condition_tables(condition: Condition) -> set:
    """Return set of table names referenced in a condition."""
    tables = set()
    if condition.comp:
        if isinstance(condition.comp.left, Column) and condition.comp.left.resolved_table:
            tables.add(condition.comp.left.resolved_table)
        if isinstance(condition.comp.right, Column) and condition.comp.right.resolved_table:
            tables.add(condition.comp.right.resolved_table)
    else:
        if condition.left:
            tables.update(condition_tables(condition.left))
        if condition.right:
            tables.update(condition_tables(condition.right))
    return tables

def rebuild_and(conjuncts: List[Condition]) -> Optional[Condition]:
    """Rebuild a condition from a list of conjuncts."""
    if not conjuncts:
        return None
    if len(conjuncts) == 1:
        return conjuncts[0]
    result = conjuncts[0]
    for conj in conjuncts[1:]:
        result = Condition(type='AND', left=result, right=conj)
    return result

def predicate_pushdown(query: Query) -> Query:
    """
    Perform predicate pushdown optimization.
    - Move WHERE conditions that reference only one joined table into the JOIN ON clause.
    """
    if not query.where or not query.from_clause.joins:
        return query

    # Only pushdown if WHERE is a conjunction
    conjuncts = collect_conjuncts(query.where)
    if not conjuncts:
        return query

    remaining = []
    for conjunct in conjuncts:
        conjunct_tables = condition_tables(conjunct)

        # Try to find a join that involves exactly this table
        pushed = False
        if len(conjunct_tables) == 1:
            table_name = next(iter(conjunct_tables))
            for join in query.from_clause.joins:
                if join.table.name == table_name:
                    # Push this conjunct into the join's ON clause
                    if join.on.type == 'TRUE' or join.on.type == 'FALSE':
                        join.on = conjunct
                    else:
                        join.on = Condition(type='AND', left=join.on, right=conjunct)
                    pushed = True
                    break

        if not pushed:
            remaining.append(conjunct)

    query.where = rebuild_and(remaining)
    return query

def optimize_query(query: Query) -> Query:
    """
    Apply all optimization passes in order.
    """
    optimized, _ = optimize_with_report(query)
    return optimized


def optimize_with_report(query: Query) -> Tuple[Query, List[str]]:
    """
    Apply all optimization passes and return human-readable descriptions of changes.
    """
    from .codegen import to_sql

    report: List[str] = []
    optimized = copy.deepcopy(query)
    before = to_sql(optimized)

    optimized = constant_folding(optimized)
    after_fold = to_sql(optimized)
    if after_fold != before:
        if optimized.where is None and query.where is not None:
            report.append("Constant folding: removed redundant always-true WHERE condition")
        elif (
            optimized.where
            and optimized.where.type == 'COMP'
            and optimized.where.comp
            and isinstance(optimized.where.comp.left, Constant)
            and isinstance(optimized.where.comp.right, Constant)
            and optimized.where.comp.left.value == 1
            and optimized.where.comp.right.value == 0
        ):
            report.append("Constant folding: replaced always-false WHERE with contradiction (1=0)")
        else:
            report.append("Constant folding: simplified constant expressions in the WHERE clause")

    before_push = after_fold
    optimized = predicate_pushdown(optimized)
    after_push = to_sql(optimized)
    if after_push != before_push:
        report.append(
            "Predicate pushdown: moved single-table filters from WHERE into matching JOIN ON clauses"
        )

    if not report:
        report.append("No optimizations were applied — the query is already in an optimal form")

    return optimized, report
