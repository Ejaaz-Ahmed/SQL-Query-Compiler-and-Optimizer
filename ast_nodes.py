from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Column:
    table: Optional[str]
    name: str
    resolved_table: Optional[str] = None

@dataclass
class Table:
    name: str
    alias: Optional[str] = None

@dataclass
class Constant:
    value: int | str

@dataclass
class Comparison:
    left: Column | Constant
    op: str
    right: Column | Constant

@dataclass
class Condition:
    type: str  # 'AND', 'OR', 'PAREN', 'TRUE', 'FALSE'
    left: Optional['Condition'] = None
    right: Optional['Condition'] = None
    comp: Optional[Comparison] = None

@dataclass
class Join:
    table: Table
    on: Condition

@dataclass
class TableList:
    tables: List[Table]
    joins: List[Join]

@dataclass
class Query:
    columns: List[Column]
    from_clause: TableList
    where: Optional[Condition]
