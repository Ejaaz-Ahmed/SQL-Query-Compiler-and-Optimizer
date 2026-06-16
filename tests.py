import unittest

from checker import semantic_check
from codegen import to_sql
from lexer import lex
from optimizer import optimize_query
from parser import parse_sql

SCHEMA = {
    "employees": ["id", "name", "dept_id"],
    "departments": ["id", "dept_name"],
}

class SqlCompilerTests(unittest.TestCase):
    def test_parse_simple_select(self):
        query = "SELECT id, name FROM employees"
        ast = parse_sql(query)
        self.assertEqual(len(ast.columns), 2)
        self.assertEqual(ast.from_clause.tables[0].name, 'employees')
        self.assertIsNone(ast.where)

    def test_semantic_errors_unknown_table(self):
        query = "SELECT name FROM unknown"
        ast = parse_sql(query)
        errors = semantic_check(ast, SCHEMA)
        self.assertIn('Unknown table: unknown', errors)

    def test_semantic_errors_ambiguous_column(self):
        query = "SELECT id FROM employees, departments"
        ast = parse_sql(query)
        errors = semantic_check(ast, SCHEMA)
        self.assertIn('Ambiguous column: id', errors)

    def test_constant_folding_removes_true(self):
        query = "SELECT name FROM employees WHERE 1=1"
        ast = parse_sql(query)
        semantic_check(ast, SCHEMA)
        optimized = optimize_query(ast)
        self.assertIsNone(optimized.where)

    def test_predicate_pushdown_to_join(self):
        query = "SELECT name FROM employees JOIN departments ON employees.dept_id = departments.id WHERE departments.dept_name = 'Sales'"
        ast = parse_sql(query)
        errors = semantic_check(ast, SCHEMA)
        self.assertEqual(errors, [])
        optimized = optimize_query(ast)
        sql = to_sql(optimized)
        self.assertIn("ON employees.dept_id = departments.id AND departments.dept_name = 'Sales'", sql)

if __name__ == '__main__':
    unittest.main()
