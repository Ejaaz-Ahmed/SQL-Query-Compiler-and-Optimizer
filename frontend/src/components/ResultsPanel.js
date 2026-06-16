/**
 * ResultsPanel Component
 * Displays the results of query execution and optimization.
 */
import React from 'react';
import { SectionTitle } from './Icon';

const ResultsPanel = ({ results, loading, error }) => {
  if (loading) {
    return (
      <div className="card mb-4">
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Running queries...</span>
          </div>
          <p className="mt-2 text-muted">Running query...</p>
        </div>
      </div>
    );
  }

  if (error && !results) {
    return (
      <div className="alert alert-danger alert-dismissible fade show" role="alert">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (!results) {
    return null;
  }

  const isComparison = results.comparison_mode;

  return (
    <div className="card mb-4">
      <div className="card-header bg-success text-white">
        <h5 className="mb-0">
          <SectionTitle icon={isComparison ? 'columns-gap' : 'check2-circle'}>
            {isComparison ? 'Optimization Comparison' : 'Query Results'}
          </SectionTitle>
        </h5>
      </div>
      <div className="card-body">
        {/* Optimizations applied (comparison mode only) */}
        {isComparison && results.optimizations?.length > 0 && (
          <div className="mb-4">
            <h6 className="text-dark mb-2">
              <SectionTitle icon="tools">Optimizations Applied</SectionTitle>
            </h6>
            <ul className="list-group">
              {results.optimizations.map((step, index) => (
                <li key={index} className="list-group-item">
                  {step}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className={isComparison ? 'row' : ''}>
          {/* Original Query Section */}
          <div className={isComparison ? 'col-md-6 mb-4 mb-md-0' : 'mb-0'}>
            <h6 className="text-dark mb-2">
              <SectionTitle icon="file-earmark-code">Original Query</SectionTitle>
            </h6>
            <div
              className="bg-light border rounded p-3 mb-2 font-monospace"
              style={{ fontSize: '0.85rem', overflowX: 'auto' }}
            >
              {results.original_query}
            </div>
            {results.original_error ? (
              <div className="alert alert-danger mb-0" role="alert">
                <strong>Error:</strong> {results.original_error}
              </div>
            ) : (
              <div className="alert alert-info mb-0" role="alert">
                <strong>Execution Time:</strong> {results.original_time_ms?.toFixed(2)} ms
              </div>
            )}
          </div>

          {/* Optimized Query Section (comparison mode only) */}
          {isComparison && (
            <div className="col-md-6">
              <h6 className="text-dark mb-2">
                <SectionTitle icon="lightning-charge-fill">Optimized Query</SectionTitle>
              </h6>
              <div
                className="bg-light border rounded p-3 mb-2 font-monospace"
                style={{ fontSize: '0.85rem', overflowX: 'auto' }}
              >
                {results.optimized_query || (
                  <span className="text-muted">Optimized query not available</span>
                )}
              </div>
              {results.optimized_error ? (
                <div className="alert alert-danger mb-0" role="alert">
                  <strong>Error:</strong> {results.optimized_error}
                </div>
              ) : results.optimized_query ? (
                <>
                  <div className="alert alert-info mb-2" role="alert">
                    <strong>Execution Time:</strong>{' '}
                    {results.optimized_time_ms != null
                      ? `${results.optimized_time_ms.toFixed(2)} ms`
                      : 'N/A'}
                  </div>
                  {results.performance_improvement && (
                    <div className="alert alert-success mb-0" role="alert">
                      <strong>Performance:</strong> {results.performance_improvement}
                    </div>
                  )}
                </>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;
