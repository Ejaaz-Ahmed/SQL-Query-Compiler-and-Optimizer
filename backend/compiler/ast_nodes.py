"""Abstract Syntax Tree (AST) node definitions for SQL queries."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union

@dataclass
class Column:
    """Represents a column reference in a query."""
    table: Optional[str]
    name: str
    resolved_table: Optional[str] = None  # Filled by semantic checker

    def to_dict(self):
        return asdict(self)

@dataclass
class Table:
    """Represents a table reference."""
    name: str
    alias: Optional[str] = None

    def to_dict(self):
        result = {'name': self.name}
        if self.alias:
            result['alias'] = self.alias
        return result

@dataclass
class Constant:
    """Represents a constant value (integer or string)."""
    value: Union[int, str]

    def to_dict(self):
        return {'value': self.value}

@dataclass
class Comparison:
    """Represents a comparison expression (e.g., col = const, col < col)."""
    left: Union[Column, Constant]
    op: str  # '=', '<', '>'
    right: Union[Column, Constant]

    def to_dict(self):
        left_dict = self.left.to_dict() if hasattr(self.left, 'to_dict') else {'type': type(self.left).__name__}
        right_dict = self.right.to_dict() if hasattr(self.right, 'to_dict') else {'type': type(self.right).__name__}
        return {
            'type': 'Comparison',
            'left': left_dict,
            'op': self.op,
            'right': right_dict
        }

@dataclass
class Condition:
    """Represents a logical condition (AND, OR, comparisons, etc.)."""
    type: str  # 'AND', 'OR', 'COMP', 'TRUE', 'FALSE'
    left: Optional[Condition] = None
    right: Optional[Condition] = None
    comp: Optional[Comparison] = None  # Set when type == 'COMP'

    def to_dict(self):
        result = {'type': self.type}
        if self.comp:
            result['comp'] = self.comp.to_dict()
        if self.left:
            result['left'] = self.left.to_dict()
        if self.right:
            result['right'] = self.right.to_dict()
        return result

@dataclass
class Join:
    """Represents a JOIN clause."""
    table: Table
    on: Condition

    def to_dict(self):
        return {
            'table': self.table.to_dict(),
            'on': self.on.to_dict()
        }

@dataclass
class TableList:
    """Represents the FROM clause (tables and joins)."""
    tables: List[Table]
    joins: List[Join] = field(default_factory=list)

    def to_dict(self):
        return {
            'tables': [t.to_dict() for t in self.tables],
            'joins': [j.to_dict() for j in self.joins]
        }

@dataclass
class Query:
    """Root AST node representing a complete SELECT query."""
    columns: List[Column]
    from_clause: TableList
    where: Optional[Condition] = None

    def to_dict(self):
        return {
            'type': 'Query',
            'columns': [c.to_dict() for c in self.columns],
            'from_clause': self.from_clause.to_dict(),
            'where': self.where.to_dict() if self.where else None
        }
