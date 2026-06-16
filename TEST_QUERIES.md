# SQL Query Optimizer — Test Queries

This document lists test queries for the SQL Query Optimizer application. Use **Optimize & Run** in the UI to see the optimized SQL, applied optimizations, and execution-time comparison.

## Database Schema

| Table | Columns |
|-------|---------|
| `employees` | `id`, `name`, `dept_id`, `salary` |
| `departments` | `id`, `dept_name`, `location` |
| `projects` | `id`, `proj_name`, `budget`, `lead_id` |

## Supported SQL Subset

- `SELECT`, `*`, `FROM`, `WHERE`, `JOIN`, `ON`, `AND`, `OR`
- Table aliases (e.g. `employees e`)
- Qualified columns (e.g. `e.name`, `d.dept_name`)
- Comparisons: `=`, `<`, `>`
- Integer and string literals

## Optimizations Implemented

| Optimization | Description |
|--------------|-------------|
| **Constant folding** | Evaluates constant expressions in `WHERE` and removes redundant conditions such as `AND 1=1` or an entire always-true `WHERE` clause |
| **Predicate pushdown** | Moves single-table filters from `WHERE` into the matching `JOIN ON` clause |

---

## 1. Constant Folding

### 1.1 Remove redundant `AND 1=1`

**Original**
```sql
SELECT name FROM employees WHERE salary > 50000 AND 1=1
```

**Expected optimized**
```sql
SELECT name FROM employees WHERE salary > 50000
```

**Optimization applied:** Constant folding — simplified constant expressions in the `WHERE` clause.

---

### 1.2 Remove always-true `WHERE` clause

**Original**
```sql
SELECT name FROM employees WHERE 1=1
```

**Expected optimized**
```sql
SELECT name FROM employees
```

**Optimization applied:** Constant folding — removed redundant always-true `WHERE` condition.

---

### 1.3 Simplify `OR` with constant false

**Original**
```sql
SELECT name FROM employees WHERE 1=0 OR salary > 60000
```

**Expected optimized**
```sql
SELECT name FROM employees WHERE salary > 60000
```

**Optimization applied:** Constant folding — simplified constant expressions in the `WHERE` clause.

---

### 1.4 Fold constant comparison in `AND`

**Original**
```sql
SELECT name FROM employees WHERE salary > 50000 AND 2=2
```

**Expected optimized**
```sql
SELECT name FROM employees WHERE salary > 50000
```

**Optimization applied:** Constant folding — simplified constant expressions in the `WHERE` clause.

---

### 1.5 Constant folding with `SELECT *`

**Original**
```sql
SELECT * FROM employees WHERE salary > 50000 AND 1=1
```

**Expected optimized**
```sql
SELECT * FROM employees WHERE salary > 50000
```

**Optimization applied:** Constant folding — simplified constant expressions in the `WHERE` clause.

---

## 2. Predicate Pushdown

Predicate pushdown applies when a query has at least one `JOIN` and a `WHERE` condition that references columns from only one joined table.

### 2.1 Push department filter into `JOIN`

**Original**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Engineering'
```

**Expected optimized**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id AND d.dept_name = 'Engineering'
```

**Optimization applied:** Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses.

---

### 2.2 Push employee salary filter into `JOIN`

**Original**
```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE e.salary > 60000
```

**Expected optimized**
```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id AND e.salary > 60000
```

**Optimization applied:** Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses.

---

### 2.3 Pushdown with string equality on department location

**Original**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.location = 'Building A'
```

**Expected optimized**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id AND d.location = 'Building A'
```

**Optimization applied:** Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses.

---

### 2.4 Pushdown with project budget filter

**Original**
```sql
SELECT e.name FROM employees e JOIN projects p ON e.id = p.lead_id WHERE p.budget > 100000
```

**Expected optimized**
```sql
SELECT e.name FROM employees e JOIN projects p ON e.id = p.lead_id AND p.budget > 100000
```

**Optimization applied:** Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses.

---

## 3. Combined Optimizations

These queries should trigger **both** constant folding and predicate pushdown.

### 3.1 Constant folding + predicate pushdown

**Original**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Engineering' AND 1=1
```

**Expected optimized**
```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id AND d.dept_name = 'Engineering'
```

**Optimizations applied:**
1. Constant folding — simplified constant expressions in the `WHERE` clause
2. Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses

---

### 3.2 Combined optimization with salary and constant

**Original**
```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE e.salary > 60000 AND 1=1
```

**Expected optimized**
```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id AND e.salary > 60000
```

**Optimizations applied:**
1. Constant folding — simplified constant expressions in the `WHERE` clause
2. Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses

---

### 3.3 Combined optimization with `SELECT *`

**Original**
```sql
SELECT * FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Sales' AND 1=1
```

**Expected optimized**
```sql
SELECT * FROM employees e JOIN departments d ON e.dept_id = d.id AND d.dept_name = 'Sales'
```

**Optimizations applied:**
1. Constant folding — simplified constant expressions in the `WHERE` clause
2. Predicate pushdown — moved single-table filters from `WHERE` into matching `JOIN ON` clauses

---

## 4. Queries With No Optimization Expected

Use these as baseline tests. The optimizer should report that no changes were applied.

### 4.1 Simple `SELECT` without `WHERE`

```sql
SELECT * FROM employees
```

### 4.2 `SELECT` with a non-constant `WHERE` and no `JOIN`

```sql
SELECT name FROM employees WHERE salary > 60000
```

### 4.3 `JOIN` without pushable `WHERE` predicate

```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id
```

### 4.4 Multi-table `WHERE` condition (not pushable)

```sql
SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE e.salary > 60000 AND d.dept_name = 'Engineering'
```

**Reason:** Predicate pushdown only moves conditions that reference a single table. This `WHERE` clause references both `employees` and `departments`, so it stays in `WHERE`.

---

## 5. Valid Queries (Run Only)

These queries are valid in the application but are useful mainly for **Run Original** or semantic/parser testing rather than optimization demos.

### 5.1 Qualified columns with aliases

```sql
SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id
```

### 5.2 `SELECT` with `WHERE` and comparison operators

```sql
SELECT name FROM employees WHERE salary > 50000
```

```sql
SELECT name FROM employees WHERE salary < 40000
```

```sql
SELECT name FROM employees WHERE name = 'Alice'
```

### 5.3 Qualified wildcard

```sql
SELECT e.* FROM employees e JOIN departments d ON e.dept_id = d.id
```

---

## 6. How to Test in the Application

1. Start the backend and frontend.
2. Paste a query from this file into **SQL Query Input**.
3. Click **Optimize & Run**.
4. Verify:
   - **Optimizations Applied** lists the expected optimization(s)
   - **Original Query** matches the input
   - **Optimized Query** matches the expected output in this document
   - Execution times are shown for both versions

## 7. Quick Reference

| Test case | Optimization expected |
|-----------|----------------------|
| `... WHERE ... AND 1=1` | Constant folding |
| `... WHERE 1=1` | Constant folding |
| `... JOIN ... WHERE single_table_filter` | Predicate pushdown |
| `... JOIN ... WHERE filter AND 1=1` | Both |
| `SELECT * FROM table` | None |
| `... WHERE col > value` (no JOIN) | None |
| `... WHERE t1.col AND t2.col` (JOIN) | None |

---

## 8. CLI Testing (Optional)

You can also test parsing and optimization from the project root:

```bash
cd backend
python -c "
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.checker import check
from compiler.optimizer import optimize_with_report
from compiler.codegen import to_sql

SCHEMA = {
    'employees': ['id', 'name', 'dept_id', 'salary'],
    'departments': ['id', 'dept_name', 'location'],
    'projects': ['id', 'proj_name', 'budget', 'lead_id'],
}

query = '''SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Engineering' AND 1=1'''
ast = parse(tokenize(query))
check(ast, SCHEMA)
optimized, report = optimize_with_report(ast)
print('Report:', report)
print('Optimized:', to_sql(optimized))
"
```
