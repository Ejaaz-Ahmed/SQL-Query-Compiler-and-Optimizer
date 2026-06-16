/**
 * SampleQueries Component
 * Clickable example queries that demonstrate supported optimizations.
 */
import { SectionTitle } from './Icon';

export const SAMPLE_QUERIES = [
  {
    label: 'Constant folding — remove AND 1=1',
    optimization: 'Constant folding',
    query: 'SELECT name FROM employees WHERE salary > 50000 AND 1=1',
  },
  {
    label: 'Constant folding — remove always-true WHERE',
    optimization: 'Constant folding',
    query: 'SELECT name FROM employees WHERE 1=1',
  },
  {
    label: 'Predicate pushdown — filter into JOIN',
    optimization: 'Predicate pushdown',
    query:
      "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Engineering'",
  },
  {
    label: 'Both optimizations combined',
    optimization: 'Constant folding + Predicate pushdown',
    query:
      "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE d.dept_name = 'Engineering' AND 1=1",
  },
  {
    label: 'JOIN with salary filter pushdown',
    optimization: 'Predicate pushdown',
    query:
      'SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE e.salary > 60000',
  },
  {
    label: 'Basic SELECT (no optimization expected)',
    optimization: 'None',
    query: 'SELECT * FROM employees',
  },
];

const SampleQueries = ({ onSelect }) => {
  return (
    <div className="card bg-light mb-4">
      <div className="card-header">
        <h6 className="mb-0">
          <SectionTitle icon="journal-code">Optimizable Query Examples</SectionTitle>
        </h6>
      </div>
      <div className="card-body small">
        <p className="text-muted mb-2">
          Click an example to load it, then use <strong>Optimize &amp; Run</strong> to see the
          optimized SQL and comparison.
        </p>
        <div className="list-group list-group-flush">
          {SAMPLE_QUERIES.map((sample) => (
            <button
              key={sample.label}
              type="button"
              className="list-group-item list-group-item-action text-start"
              onClick={() => onSelect(sample.query)}
            >
              <div className="fw-semibold">{sample.label}</div>
              <div className="text-muted mb-1">{sample.optimization}</div>
              <code className="d-block text-break" style={{ fontSize: '0.75rem' }}>
                {sample.query}
              </code>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SampleQueries;
