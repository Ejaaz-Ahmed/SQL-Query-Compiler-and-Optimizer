"""Unit tests for the SQL compiler modules."""
import pytest
from compiler.lexer import tokenize, Token
from compiler.parser import parse
from compiler.checker import check
from compiler.optimizer import constant_folding, predicate_pushdown, optimize_query
from compiler.codegen import to_sql
from compiler.ast_nodes import Query, Column, Table, Condition, Constant, Comparison

# Sample schema for testing
TEST_SCHEMA = {
    "employees": ["id", "name", "dept_id", "salary"],
    "departments": ["id", "dept_name", "location"],
    "projects": ["id", "proj_name", "budget", "lead_id"]
}

class TestLexer:
    """Test the SQL lexer/tokenizer."""

    def test_simple_select(self):
        """Test tokenizing a simple SELECT query."""
        tokens = tokenize("SELECT name FROM employees")
        assert len(tokens) > 0
        assert tokens[0].type == 'SELECT'
        assert tokens[1].type == 'ID'

    def test_with_where(self):
        """Test tokenizing a query with WHERE clause."""
        tokens = tokenize("SELECT name FROM employees WHERE salary > 50000")
        token_types = [t.type for t in tokens]
        assert 'WHERE' in token_types
        assert 'GT' in token_types

    def test_with_join(self):
        """Test tokenizing a query with JOIN."""
        tokens = tokenize("SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id")
        token_types = [t.type for t in tokens]
        assert 'JOIN' in token_types
        assert 'ON' in token_types
        assert 'DOT' in token_types

    def test_string_literal(self):
        """Test tokenizing string literals."""
        tokens = tokenize("SELECT name FROM employees WHERE name = 'Alice'")
        string_tokens = [t for t in tokens if t.type == 'STRING']
        assert len(string_tokens) > 0
        assert string_tokens[0].value == 'Alice'

    def test_select_star(self):
        """Test tokenizing SELECT *."""
        tokens = tokenize("SELECT * FROM employees;")
        token_types = [t.type for t in tokens]
        assert token_types[:3] == ['SELECT', 'STAR', 'FROM']
        assert 'SEMICOLON' in token_types

class TestParser:
    """Test the SQL parser."""

    def test_parse_simple_select(self):
        """Test parsing a simple SELECT."""
        query = parse(tokenize("SELECT id, name FROM employees"))
        assert isinstance(query, Query)
        assert len(query.columns) == 2
        assert query.columns[0].name == 'id'
        assert query.columns[1].name == 'name'

    def test_parse_with_where(self):
        """Test parsing a SELECT with WHERE."""
        query = parse(tokenize("SELECT name FROM employees WHERE salary > 50000"))
        assert query.where is not None
        assert query.where.type == 'COMP'

    def test_parse_with_join(self):
        """Test parsing a SELECT with JOIN."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id"
        ))
        assert len(query.from_clause.joins) == 1
        assert query.from_clause.joins[0].table.name == 'departments'
        assert query.from_clause.tables[0].alias == 'e'
        assert query.from_clause.joins[0].table.alias == 'd'

    def test_parse_join_with_where_and_alias(self):
        """Test parsing aliased JOIN query with WHERE clause."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id "
            "WHERE d.dept_name = 'Engineering'"
        ))
        assert query.where is not None
        assert query.columns[0].table == 'e'
        assert query.columns[0].name == 'name'

    def test_parse_qualified_column(self):
        """Test parsing qualified column references."""
        query = parse(tokenize("SELECT e.name FROM employees e"))
        assert query.columns[0].table == 'e'
        assert query.columns[0].name == 'name'

    def test_parse_select_star(self):
        """Test parsing SELECT *."""
        query = parse(tokenize("SELECT * FROM employees;"))
        assert len(query.columns) == 1
        assert query.columns[0].name == '*'
        assert query.columns[0].table is None

    def test_parse_qualified_star(self):
        """Test parsing table.* column references."""
        query = parse(tokenize("SELECT e.* FROM employees e"))
        assert query.columns[0].table == 'e'
        assert query.columns[0].name == '*'

class TestChecker:
    """Test the semantic checker."""

    def test_unknown_table_error(self):
        """Test that unknown tables are caught."""
        query = parse(tokenize("SELECT name FROM unknown_table"))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) > 0
        assert "Unknown table" in errors[0]

    def test_unknown_column_error(self):
        """Test that unknown columns are caught."""
        query = parse(tokenize("SELECT unknown_col FROM employees"))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) > 0
        assert "Unknown column" in errors[0]

    def test_ambiguous_column_error(self):
        """Test that ambiguous columns are caught."""
        query = parse(tokenize(
            "SELECT id FROM employees, departments"
        ))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) > 0
        assert "Ambiguous column" in errors[0]

    def test_valid_qualified_column(self):
        """Test that qualified columns resolve correctly."""
        query = parse(tokenize("SELECT e.id FROM employees e, departments d"))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) == 0
        assert query.columns[0].resolved_table == 'employees'

    def test_select_star_passes_semantic_check(self):
        """Test that SELECT * is accepted by the semantic checker."""
        query = parse(tokenize("SELECT * FROM employees"))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) == 0

    def test_aliased_join_passes_semantic_check(self):
        """Test that aliased JOIN queries pass semantic checking."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id "
            "WHERE d.dept_name = 'Engineering'"
        ))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) == 0
        assert query.columns[0].resolved_table == 'employees'

class TestOptimizer:
    """Test the query optimizer."""

    def test_constant_folding_true(self):
        """Test that TRUE conditions are removed."""
        query = parse(tokenize("SELECT name FROM employees WHERE 1=1"))
        check(query, TEST_SCHEMA)
        optimized = constant_folding(query)
        assert optimized.where is None

    def test_constant_folding_false(self):
        """Test that FALSE conditions are handled."""
        query = parse(tokenize("SELECT name FROM employees WHERE 1=0"))
        check(query, TEST_SCHEMA)
        optimized = constant_folding(query)
        assert optimized.where is not None
        assert optimized.where.type == 'COMP'

    def test_constant_folding_and_true(self):
        """Test that TRUE AND X simplifies to X."""
        query = parse(tokenize("SELECT name FROM employees WHERE salary > 50000 AND 1=1"))
        check(query, TEST_SCHEMA)
        optimized = constant_folding(query)
        assert optimized.where is not None
        sql = to_sql(optimized)
        assert "1=1" not in sql

    def test_predicate_pushdown(self):
        """Test that predicates are pushed down into JOIN."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id "
            "WHERE d.dept_name = 'Engineering'"
        ))
        check(query, TEST_SCHEMA)
        optimized = predicate_pushdown(query)
        sql = to_sql(optimized)
        assert "ON" in sql
        assert "Engineering" in sql.split("WHERE")[0]  # Engineering is now in ON clause

    def test_full_optimization(self):
        """Test full optimization pipeline."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id "
            "WHERE d.dept_name = 'Sales' AND 1=1"
        ))
        errors = check(query, TEST_SCHEMA)
        assert len(errors) == 0
        
        optimized = optimize_query(query)
        sql = to_sql(optimized)
        
        # Should have no constant TRUE/FALSE
        assert "1=1" not in sql
        # Should have department condition in ON clause
        assert "Sales" in sql.split("WHERE")[0] or "WHERE" not in sql

class TestCodegen:
    """Test the SQL code generator."""

    def test_simple_select(self):
        """Test generating SQL for simple SELECT."""
        query = parse(tokenize("SELECT name FROM employees"))
        check(query, TEST_SCHEMA)
        sql = to_sql(query)
        assert "SELECT" in sql.upper()
        assert "name" in sql.lower()
        assert "employees" in sql.lower()

    def test_select_star_codegen(self):
        """Test generating SQL for SELECT *."""
        query = parse(tokenize("SELECT * FROM employees"))
        check(query, TEST_SCHEMA)
        sql = to_sql(query)
        assert sql == "SELECT * FROM employees"

    def test_with_where(self):
        """Test generating SQL with WHERE clause."""
        query = parse(tokenize("SELECT name FROM employees WHERE salary > 50000"))
        check(query, TEST_SCHEMA)
        sql = to_sql(query)
        assert "WHERE" in sql.upper()
        assert "50000" in sql

    def test_with_join(self):
        """Test generating SQL with JOIN."""
        query = parse(tokenize(
            "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id"
        ))
        check(query, TEST_SCHEMA)
        sql = to_sql(query)
        assert "JOIN" in sql.upper()
        assert "ON" in sql.upper()

class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_full_pipeline(self):
        """Test the complete lexer -> parser -> checker -> optimizer -> codegen pipeline."""
        original_query = (
            "SELECT e.name, d.dept_name FROM employees e "
            "JOIN departments d ON e.dept_id = d.id "
            "WHERE d.location = 'Building A' AND 1=1"
        )
        
        # Lex and parse
        tokens = tokenize(original_query)
        query = parse(tokens)
        
        # Check
        errors = check(query, TEST_SCHEMA)
        assert len(errors) == 0
        
        # Optimize
        optimized = optimize_query(query)
        
        # Codegen
        optimized_sql = to_sql(optimized)
        
        # Verify optimizations were applied
        assert "1=1" not in optimized_sql  # Constant folding
        assert optimized_sql != original_query  # Something changed

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
