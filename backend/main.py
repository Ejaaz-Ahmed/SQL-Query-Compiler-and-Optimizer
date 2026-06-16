"""FastAPI backend for SQL Query Optimizer."""
import sqlite3
import time
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from compiler import tokenize, parse, check, optimize_with_report, to_sql

# ============================================================================
# Configuration
# ============================================================================

DATABASE_NAME = "query_optimizer.db"

SCHEMA = {
    "employees": ["id", "name", "dept_id", "salary"],
    "departments": ["id", "dept_name", "location"],
    "projects": ["id", "proj_name", "budget", "lead_id"]
}

INIT_SQL = """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    dept_id INTEGER,
    salary REAL
);

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL,
    location TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    proj_name TEXT NOT NULL,
    budget REAL,
    lead_id INTEGER
);
"""

SAMPLE_DATA = [
    "INSERT INTO departments (id, dept_name, location) VALUES (1, 'Engineering', 'Building A');",
    "INSERT INTO departments (id, dept_name, location) VALUES (2, 'Sales', 'Building B');",
    "INSERT INTO departments (id, dept_name, location) VALUES (3, 'HR', 'Building A');",
    "INSERT INTO employees (id, name, dept_id, salary) VALUES (1, 'Alice', 1, 75000);",
    "INSERT INTO employees (id, name, dept_id, salary) VALUES (2, 'Bob', 1, 80000);",
    "INSERT INTO employees (id, name, dept_id, salary) VALUES (3, 'Charlie', 2, 60000);",
    "INSERT INTO employees (id, name, dept_id, salary) VALUES (4, 'Diana', 2, 65000);",
    "INSERT INTO employees (id, name, dept_id, salary) VALUES (5, 'Eve', 3, 55000);",
    "INSERT INTO projects (id, proj_name, budget, lead_id) VALUES (1, 'Project Alpha', 200000, 1);",
    "INSERT INTO projects (id, proj_name, budget, lead_id) VALUES (2, 'Project Beta', 150000, 2);",
    "INSERT INTO projects (id, proj_name, budget, lead_id) VALUES (3, 'Project Gamma', 50000, 4);",
]

# ============================================================================
# Database Management
# ============================================================================

_db_connection: Optional[sqlite3.Connection] = None

def get_db():
    """Get or create the database connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect(DATABASE_NAME)
        _db_connection.row_factory = sqlite3.Row
    return _db_connection

def init_db():
    """Initialize the database with schema and sample data."""
    db = get_db()
    cursor = db.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS employees;")
    cursor.execute("DROP TABLE IF EXISTS projects;")
    cursor.execute("DROP TABLE IF EXISTS departments;")

    # Create tables
    for statement in INIT_SQL.strip().split(';'):
        if statement.strip():
            cursor.execute(statement)

    # Insert sample data
    for statement in SAMPLE_DATA:
        cursor.execute(statement)

    db.commit()

def reset_db():
    """Reset the database to initial state."""
    init_db()

# ============================================================================
# Query Execution
# ============================================================================

def execute_query(sql: str, num_runs: int = 5) -> float:
    """
    Execute a query multiple times and return average execution time in milliseconds.

    Args:
        sql: The SQL query to execute
        num_runs: Number of times to run the query (default 5)

    Returns:
        Average execution time in milliseconds

    Raises:
        sqlite3.Error: If query execution fails
    """
    db = get_db()
    cursor = db.cursor()
    times = []

    for _ in range(num_runs):
        start = time.perf_counter()
        cursor.execute(sql)
        result = cursor.fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    # Remove highest and lowest, average the rest
    times.sort()
    if len(times) > 2:
        times = times[1:-1]

    return sum(times) / len(times)

# ============================================================================
# Pydantic Models
# ============================================================================

class ExecuteRequest(BaseModel):
    """Request model for query execution."""
    query: str
    debug: bool = False
    optimize: bool = False

class ExecuteResponse(BaseModel):
    """Response model for query execution."""
    original_query: str
    original_time_ms: Optional[float]
    original_error: Optional[str]
    optimized_query: Optional[str] = None
    optimized_time_ms: Optional[float] = None
    optimized_error: Optional[str] = None
    ast: Optional[Dict[str, Any]] = None
    performance_improvement: Optional[str] = None
    optimizations: Optional[List[str]] = None
    comparison_mode: bool = False

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="SQL Query Optimizer")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

@app.get("/api/schema")
async def get_schema():
    """Get the database schema."""
    return SCHEMA

@app.post("/api/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """
    Execute a SQL query and its optimized version.

    Returns execution times and query texts.
    """
    original_query = request.query.strip()
    original_error = None
    original_time_ms = None
    optimized_query = None
    optimized_error = None
    optimized_time_ms = None
    ast_dict = None
    performance_improvement = None

    # Step 1: Tokenize and parse
    try:
        tokens = tokenize(original_query)
        ast = parse(tokens)
        if request.debug:
            ast_dict = ast.to_dict()
    except Exception as e:
        original_error = f"Parse Error: {str(e)}"
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=None,
            original_error=original_error,
            optimized_query=None,
            optimized_time_ms=None,
            optimized_error=None,
            ast=ast_dict
        )

    # Step 2: Semantic check
    try:
        errors = check(ast, SCHEMA)
        if errors:
            original_error = "; ".join(errors)
            return ExecuteResponse(
                original_query=original_query,
                original_time_ms=None,
                original_error=original_error,
                optimized_query=None,
                optimized_time_ms=None,
                optimized_error=None,
                ast=ast_dict
            )
    except Exception as e:
        original_error = f"Semantic Error: {str(e)}"
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=None,
            original_error=original_error,
            optimized_query=None,
            optimized_time_ms=None,
            optimized_error=None,
            ast=ast_dict
        )

    # Step 3: Execute original query
    try:
        original_time_ms = execute_query(original_query)
    except sqlite3.Error as e:
        original_error = f"Execution Error: {str(e)}"
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=None,
            original_error=original_error,
            ast=ast_dict,
            comparison_mode=request.optimize
        )

    if not request.optimize:
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=original_time_ms,
            original_error=None,
            ast=ast_dict,
            comparison_mode=False
        )

    # Step 4: Optimize query (only when comparison mode is requested)
    optimizations = None
    try:
        optimized_ast, optimizations = optimize_with_report(ast)
        optimized_query = to_sql(optimized_ast)
    except Exception as e:
        optimized_error = f"Optimization Error: {str(e)}"
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=original_time_ms,
            original_error=None,
            optimized_query=to_sql(ast),
            optimized_error=optimized_error,
            ast=ast_dict,
            comparison_mode=True
        )

    # Step 5: Execute optimized query
    try:
        optimized_time_ms = execute_query(optimized_query)
    except sqlite3.Error as e:
        optimized_error = f"Execution Error: {str(e)}"
        return ExecuteResponse(
            original_query=original_query,
            original_time_ms=original_time_ms,
            original_error=None,
            optimized_query=optimized_query,
            optimized_time_ms=None,
            optimized_error=optimized_error,
            ast=ast_dict,
            optimizations=optimizations,
            comparison_mode=True
        )

    # Step 6: Calculate performance improvement
    if original_time_ms > 0:
        improvement_percent = ((original_time_ms - optimized_time_ms) / original_time_ms) * 100
        if improvement_percent > 0:
            performance_improvement = f"Saved {improvement_percent:.1f}% time"
        else:
            performance_improvement = f"Slower by {-improvement_percent:.1f}%"

    return ExecuteResponse(
        original_query=original_query,
        original_time_ms=original_time_ms,
        original_error=None,
        optimized_query=optimized_query,
        optimized_time_ms=optimized_time_ms,
        optimized_error=None,
        ast=ast_dict,
        performance_improvement=performance_improvement,
        optimizations=optimizations,
        comparison_mode=True
    )

@app.post("/api/reset")
async def reset():
    """Reset the database to initial state."""
    try:
        reset_db()
        return {"status": "success", "message": "Database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SQL Query Optimizer Backend API"}

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)
