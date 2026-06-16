# SQL Query Optimizer - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

### Step 3: Start the Backend
From the `backend` directory:
```bash
python main.py
```
✅ Backend running at `http://localhost:8000`

### Step 4: Start the Frontend
From the `frontend` directory:
```bash
npm start
```
✅ Frontend running at `http://localhost:3000`

### Step 5: Open in Browser
Navigate to `http://localhost:3000`

---

## 📝 Try These Sample Queries

### Basic Query
```sql
SELECT name FROM employees WHERE salary > 60000
```

### Query with JOIN
```sql
SELECT e.name, d.dept_name FROM employees e 
JOIN departments d ON e.dept_id = d.id
```

### Query with Optimization Opportunity
```sql
SELECT e.name, d.dept_name FROM employees e 
JOIN departments d ON e.dept_id = d.id 
WHERE d.dept_name = 'Engineering' AND 1=1
```

---

## 🎯 What to Look For

1. **Constant Folding**: Removes `AND 1=1` or simplifies `1=0`
2. **Predicate Pushdown**: Moves WHERE conditions into JOIN ON clauses
3. **Performance Improvement**: Percentage of time saved by optimizations

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Check Python version
python --version  # Should be 3.10+

# Try reinstalling
pip install --upgrade -r requirements.txt

# Run with verbose output
python main.py
```

### Frontend won't start?
```bash
# Check Node version
node --version  # Should be 16+

# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules
npm install
npm start
```

### Can't connect to backend?
- Ensure backend is running on port 8000
- Check browser console (F12) for CORS errors
- Try "Reset DB" button to verify API connection

---

## 📚 Full Documentation

See `README.md` for complete documentation including:
- Full project structure
- API endpoint reference
- Advanced optimization examples
- Production deployment guide
- Extending the compiler

---

## 🧪 Run Backend Tests

```bash
cd backend
pip install pytest
pytest tests.py -v
```

---

**Enjoy exploring SQL optimization! 🎉**
