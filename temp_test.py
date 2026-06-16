from lexer import lex
from parser import parse_sql
from checker import semantic_check
from optimizer import optimize_query
from codegen import to_sql

schema = {"employees": ["id", "name", "dept_id"], "departments": ["id", "dept_name"]}
q = "SELECT name FROM employees JOIN departments ON employees.dept_id = departments.id WHERE departments.dept_name = 'Sales' AND 1=1"

print('TOKENS:', lex(q))
ast = parse_sql(q)
print('AST OK', ast)
errs = semantic_check(ast, schema)
print('errs', errs)
opt = optimize_query(ast)
print('optimized', to_sql(opt))
