/**
 * SchemaDisplay Component
 * Shows the database schema (tables and columns).
 */
import React, { useState, useEffect } from 'react';
import { getSchema } from '../api';
import Icon, { SectionTitle } from './Icon';

const SchemaDisplay = () => {
  const [schema, setSchema] = useState(null);
  const [expanded, setExpanded] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const response = await getSchema();
        setSchema(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load schema');
        console.error(err);
      }
    };

    fetchSchema();
  }, []);

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  if (!schema) {
    return <div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div>;
  }

  return (
    <div className="card mb-4">
      <div className="card-header bg-secondary text-white" role="button" onClick={() => setExpanded(!expanded)}>
        <h5 className="mb-0" style={{ cursor: 'pointer' }}>
          <SectionTitle
            icon="database"
            chevron={expanded ? 'chevron-down' : 'chevron-right'}
          >
            Database Schema
          </SectionTitle>
        </h5>
      </div>
      {expanded && (
        <div className="card-body">
          <div className="row">
            {Object.entries(schema).map(([tableName, columns]) => (
              <div key={tableName} className="col-md-6 col-lg-4 mb-3">
                <div className="border rounded p-3">
                  <h6 className="text-primary mb-2 d-flex align-items-center gap-2">
                    <Icon name="table" />
                    {tableName}
                  </h6>
                  <ul className="list-unstyled small">
                    {columns.map((col) => (
                      <li key={col} className="text-muted d-flex align-items-center gap-2">
                        <Icon name="circle-fill" className="text-secondary" size="0.4rem" />
                        {col}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SchemaDisplay;
