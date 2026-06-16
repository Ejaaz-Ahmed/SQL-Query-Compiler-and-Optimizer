/**
 * App.js - Main Application Component
 * Orchestrates the SQL Query Optimizer application.
 */
import React, { useState } from 'react';
import QueryInput from './components/QueryInput';
import SchemaDisplay from './components/SchemaDisplay';
import ResultsPanel from './components/ResultsPanel';
import AstViewer from './components/AstViewer';
import SampleQueries from './components/SampleQueries';
import Icon, { SectionTitle } from './components/Icon';
import { executeQuery, resetDatabase } from './api';
import './App.css';

function App() {
  const [query, setQuery] = useState('SELECT * FROM employees');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  const runQuery = async (query, optimize = false) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await executeQuery(query, { debug: showDebug, optimize });
      setResults(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (query) => {
    await runQuery(query, false);
  };

  const handleOptimize = async (query) => {
    await runQuery(query, true);
  };

  const handleReset = async () => {
    if (window.confirm('Reset the database to initial state?')) {
      try {
        await resetDatabase();
        setResults(null);
        setError(null);
        alert('Database reset successfully');
      } catch (err) {
        setError('Failed to reset database');
        console.error('Error:', err);
      }
    }
  };

  return (
    <div className="app-container">
      <nav className="navbar navbar-dark bg-dark mb-4">
        <div className="container-fluid">
          <a className="navbar-brand fw-bold d-inline-flex align-items-center gap-2" href="/">
            <Icon name="rocket-takeoff" size="1.25rem" />
            SQL Query Optimizer
          </a>
          <div className="d-flex gap-2">
            <button
              className="btn btn-outline-light btn-sm d-inline-flex align-items-center gap-2"
              onClick={() => setShowDebug(!showDebug)}
              title="Show AST for debugging"
            >
              <Icon name="bug" />
              {showDebug ? 'Debug ON' : 'Debug OFF'}
            </button>
            <button
              className="btn btn-outline-warning btn-sm d-inline-flex align-items-center gap-2"
              onClick={handleReset}
            >
              <Icon name="arrow-clockwise" />
              Reset DB
            </button>
          </div>
        </div>
      </nav>

      <div className="container-fluid mb-5">
        <div className="row">
          {/* Main Content */}
          <div className="col-lg-8">
            <QueryInput
              query={query}
              onQueryChange={setQuery}
              onExecute={handleExecute}
              onOptimize={handleOptimize}
              loading={loading}
            />
            <ResultsPanel results={results} loading={loading} error={error} />
            {showDebug && results?.ast && <AstViewer ast={results.ast} />}
          </div>

          {/* Sidebar */}
          <div className="col-lg-4">
            <SchemaDisplay />
            <SampleQueries onSelect={setQuery} />
            <div className="card bg-light">
              <div className="card-header">
                <h6 className="mb-0">
                  <SectionTitle icon="lightbulb">How to use</SectionTitle>
                </h6>
              </div>
              <div className="card-body small text-muted">
                <p className="mb-2">
                  <strong>Run Original</strong> — executes your query only.
                </p>
                <p className="mb-2">
                  <strong>Optimize &amp; Run</strong> — shows the original query, the optimized
                  query, which optimizations were applied, and a timing comparison.
                </p>
                <p className="mb-0">
                  Supported optimizations: <strong>constant folding</strong> and{' '}
                  <strong>predicate pushdown</strong>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer className="bg-light text-center py-4 mt-5 border-top">
        <p className="mb-0 text-muted">
          SQL Query Optimizer &copy; 2024 | Compiler Construction Project
        </p>
      </footer>
    </div>
  );
}

export default App;
