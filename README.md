# SQL Query Optimizer - Full-Stack Application

A complete web-based SQL query optimizer that analyzes queries, applies optimization passes, and measures performance improvements. Built with Python/FastAPI backend and React frontend.

## Features

- **Interactive Query Editor**: Write and test SQL queries with real-time feedback
- **Two Optimization Passes**:
  - **Constant Folding**: Evaluates constant-only comparisons and simplifies boolean expressions
  - **Predicate Pushdown**: Moves WHERE conditions into JOIN ON clauses for better performance
- **Real-time Performance Measurement**: Executes both original and optimized queries and compares execution times
- **Visual Schema Display**: Shows all available tables and columns
- **Debug Mode**: View the parsed Abstract Syntax Tree (AST) for debugging
- **Clean UI**: Modern, responsive React interface with Bootstrap styling

## Tech Stack

### Backend
- Python 3.10+
- FastAPI (async REST API)
- SQLite3 (in-memory or file-based database)
- Custom hand-written SQL compiler (lexer, parser, semantic checker, optimizer, code generator)

### Frontend
- React 18
- Axios (HTTP client)
- Bootstrap 5 (CSS framework)
- Modern JavaScript (ES6+)

## Project Structure

```
project-root/
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── requirements.txt        # Python dependencies
│   └── compiler/
│       ├── __init__.py         # Package init
│       ├── lexer.py            # Tokenizer
│       ├── parser.py           # Recursive descent parser
│       ├── ast_nodes.py        # AST dataclass definitions
│       ├── checker.py          # Semantic checker
│       ├── optimizer.py        # Optimization passes
│       └── codegen.py          # SQL code generator
├── frontend/
│   ├── public/
│   │   └── index.html          # HTML entry point
│   ├── src/
│   │   ├── index.js            # React entry point
│   │   ├── App.js              # Main app component
│   │   ├── App.css             # Application styles
│   │   ├── api.js              # Axios API client
│   │   └── components/
│   │       ├── QueryInput.js   # Query input component
│   │       ├── SchemaDisplay.js # Schema display component
│   │       ├── ResultsPanel.js # Results display component
│   │       └── AstViewer.js    # AST viewer component
│   ├── package.json            # NPM dependencies
│   └── .gitignore
└── README.md
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16+ and npm
- Git (optional)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend

From the `backend` directory:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`
API documentation (Swagger UI) will be at `http://localhost:8000/docs`

### Start the Frontend

From the `frontend` directory:
```bash
npm start
```

The frontend will open in your browser at `http://localhost:3000`

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## Database

The application uses SQLite with three pre-populated tables:

### Tables

1. **employees**
   - id: INTEGER PRIMARY KEY
   - name: TEXT
   - dept_id: INTEGER
   - salary: REAL

2. **departments**
   - id: INTEGER PRIMARY KEY
   - dept_name: TEXT
   - location: TEXT

3. **projects**
   - id: INTEGER PRIMARY KEY
   - proj_name: TEXT
   - budget: REAL
   - lead_id: INTEGER

### Sample Data

The database is automatically populated with sample data on startup:
- 5 employees across 3 departments
- 3 departments
- 3 projects with different budgets

Use the "🔄 Reset DB" button in the UI to reset the database to initial state at any time.

## SQL Subset Supported

The compiler supports a limited but useful SQL subset:

```sql
-- Basic SELECT
SELECT col1, col2 FROM table1

-- With WHERE
SELECT * FROM employees WHERE salary > 50000

-- With JOIN
SELECT e.name, d.dept_name 
FROM employees e 
JOIN departments d ON e.dept_id = d.id

-- With complex conditions
SELECT e.name 
FROM employees e 
JOIN projects p ON e.id = p.lead_id 
WHERE e.salary > 60000 AND p.budget > 100000

-- With constant folding
SELECT * FROM employees WHERE salary > 50000 AND 1=1
-- Optimized to: SELECT * FROM employees WHERE salary > 50000
```

### Supported Features
- SELECT with multiple columns
- Multiple FROM tables (comma-separated)
- INNER JOIN with ON clauses
- Multiple JOINs (chained)
- WHERE conditions with AND/OR
- Comparisons: =, <, >
- Column references: both qualified (table.col) and unqualified
- Constants: integers and string literals

### Unsupported Features
- Subqueries
- Aggregates (COUNT, SUM, etc.)
- GROUP BY, HAVING, ORDER BY
- DISTINCT
- Arithmetic expressions
- OUTER JOIN
- UNION

## API Endpoints

### POST /api/execute
Execute a query and get optimization results.

**Request:**
```json
{
  "query": "SELECT name FROM employees WHERE salary > 50000",
  "debug": false
}
```

**Response:**
```json
{
  "original_query": "SELECT name FROM employees WHERE salary > 50000",
  "original_time_ms": 0.45,
  "original_error": null,
  "optimized_query": "SELECT name FROM employees WHERE salary > 50000",
  "optimized_time_ms": 0.42,
  "optimized_error": null,
  "performance_improvement": "Saved 6.7% time",
  "ast": null
}
```

### GET /api/schema
Get the database schema.

**Response:**
```json
{
  "employees": ["id", "name", "dept_id", "salary"],
  "departments": ["id", "dept_name", "location"],
  "projects": ["id", "proj_name", "budget", "lead_id"]
}
```

### POST /api/reset
Reset the database to initial state.

**Response:**
```json
{
  "status": "success",
  "message": "Database reset successfully"
}
```

## Optimization Examples

### Example 1: Constant Folding

**Original Query:**
```sql
SELECT name FROM employees WHERE salary > 50000 AND 1=1
```

**Optimized Query:**
```sql
SELECT name FROM employees WHERE salary > 50000
```

**Explanation:** The condition `1=1` is always true, so it's removed by constant folding.

### Example 2: Predicate Pushdown

**Original Query:**
```sql
SELECT e.name 
FROM employees e 
JOIN departments d ON e.dept_id = d.id 
WHERE d.dept_name = 'Engineering'
```

**Optimized Query:**
```sql
SELECT e.name 
FROM employees e 
JOIN departments d ON e.dept_id = d.id AND d.dept_name = 'Engineering'
```

**Explanation:** The WHERE condition that references only the departments table is pushed down into the JOIN ON clause.

### Example 3: Combined Optimizations

**Original Query:**
```sql
SELECT e.name, p.proj_name 
FROM employees e 
JOIN projects p ON e.id = p.lead_id 
WHERE p.budget > 100000 AND 1=1 AND e.salary > 60000
```

**Optimized Query:**
```sql
SELECT e.name, p.proj_name 
FROM employees e 
JOIN projects p ON e.id = p.lead_id AND p.budget > 100000 AND e.salary > 60000
```

**Explanation:** 
- Constant folding removes `1=1`
- Predicate pushdown moves `p.budget > 100000` and `e.salary > 60000` into the JOIN ON clause

## Testing

### Run Unit Tests (Backend)

From the backend directory:
```bash
pytest tests.py -v  # If tests.py exists
```

### Manual Testing

1. Use sample queries from the Tips panel
2. Try modifying conditions to see how optimizations work
3. Toggle Debug mode to view the parsed AST
4. Use Reset DB to restore initial state

## Features Explained

### Query Input
- **Run Original**: Execute the query as written and measure its execution time
- **Optimize & Run**: Apply optimizations and execute the optimized query
- **Clear**: Clear the textarea

### Schema Display
- Shows all tables and their columns
- Collapsible panel for space-saving
- Refreshes on page load

### Results Panel
- Shows original query execution time
- Shows optimized query and its execution time
- Displays performance improvement percentage
- Shows any errors that occurred

### Debug Mode
- Toggle with the 🔍 button in the navbar
- Shows the parsed Abstract Syntax Tree (AST) in JSON format
- Helpful for understanding how queries are parsed and optimized

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed: `python --version`
- Check that all dependencies are installed: `pip list`
- Try running with verbose output: `python main.py --log-level debug`

### Frontend won't start
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Ensure Node 16+ is installed: `node --version`

### API calls failing
- Check that the backend is running on port 8000
- Check browser console for CORS errors
- Verify the API_BASE_URL in `frontend/src/api.js`

### Database errors
- Use "Reset DB" button to restore initial state
- Check that the database file has write permissions
- Try deleting `query_optimizer.db` and restarting

## Performance Considerations

1. **Query Execution Times**: Times are averaged over 5 runs with highest and lowest values dropped to reduce noise
2. **Optimization Impact**: The impact depends on query complexity:
   - Simple queries: minimal improvement (overhead might outweigh benefits)
   - Complex queries with many JOINs: significant improvements possible
3. **Database Size**: The demo uses a small dataset. Larger datasets would show more dramatic optimization benefits

## Development Notes

### Code Organization
- **Compiler Module**: All parsing and optimization logic in `backend/compiler/`
- **API Layer**: FastAPI endpoints in `backend/main.py`
- **UI Layer**: React components in `frontend/src/`

### Adding New Optimizations
To add a new optimization pass:
1. Create a new function in `backend/compiler/optimizer.py`
2. Add it to the `optimize_query()` function
3. Call it from the `/api/execute` endpoint

### Extending SQL Support
To support more SQL features:
1. Update the grammar in comments
2. Add tokens to the lexer
3. Extend the parser
4. Update the AST nodes
5. Update the semantic checker

## Production Deployment

### Backend
- Use a production ASGI server like Gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
- Use a persistent database or cloud storage
- Enable HTTPS and proper CORS configuration
- Add rate limiting and request validation

### Frontend
- Build for production: `npm run build`
- Deploy to a static hosting service or CDN
- Update API_BASE_URL for production backend
- Enable gzip compression and caching

## License

This project is for educational purposes as part of a Compiler Construction course.

## Author

Created as a Compiler Construction course project.

---

**Happy optimizing! 🚀**
