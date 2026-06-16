/**
 * QueryInput Component
 * Allows users to enter and submit SQL queries for optimization.
 */
import React from 'react';
import Icon, { SectionTitle } from './Icon';

const QueryInput = ({ query, onQueryChange, onExecute, onOptimize, loading }) => {

  const handleRunOriginal = () => {
    if (query.trim()) {
      onExecute(query);
    }
  };

  const handleOptimize = () => {
    if (query.trim()) {
      onOptimize(query);
    }
  };

  const handleClear = () => {
    onQueryChange('');
  };

  return (
    <div className="card mb-4">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">
          <SectionTitle icon="terminal">SQL Query Input</SectionTitle>
        </h5>
      </div>
      <div className="card-body">
        <div className="mb-3">
          <label htmlFor="queryInput" className="form-label">
            Enter your SQL query:
          </label>
          <textarea
            id="queryInput"
            className="form-control font-monospace"
            rows="5"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="SELECT ... FROM ... WHERE ..."
            style={{ fontSize: '0.9rem' }}
          />
          <small className="form-text text-muted">
            Supported: SELECT, *, FROM, WHERE, JOIN, ON, AND, OR
          </small>
        </div>
        <div className="d-flex gap-2">
          <button
            className="btn btn-success d-inline-flex align-items-center gap-2"
            onClick={handleRunOriginal}
            disabled={loading || !query.trim()}
          >
            <Icon name="play-fill" />
            {loading ? 'Running...' : 'Run Original'}
          </button>
          <button
            className="btn btn-info d-inline-flex align-items-center gap-2"
            onClick={handleOptimize}
            disabled={loading || !query.trim()}
          >
            <Icon name="lightning-charge-fill" />
            {loading ? 'Optimizing...' : 'Optimize & Run'}
          </button>
          <button
            className="btn btn-secondary d-inline-flex align-items-center gap-2"
            onClick={handleClear}
            disabled={loading}
          >
            <Icon name="x-lg" />
            Clear
          </button>
        </div>
      </div>
    </div>
  );
};

export default QueryInput;
