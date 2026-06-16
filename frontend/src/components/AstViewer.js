/**
 * AstViewer Component
 * Displays the abstract syntax tree (for debugging).
 */
import React, { useState } from 'react';
import { SectionTitle } from './Icon';

const AstViewer = ({ ast }) => {
  const [expanded, setExpanded] = useState(false);

  if (!ast) {
    return null;
  }

  const renderNode = (node, depth = 0) => {
    const indent = depth * 20;

    if (node === null || node === undefined) {
      return <div style={{ marginLeft: indent }} className="text-muted">null</div>;
    }

    if (typeof node !== 'object') {
      return <div style={{ marginLeft: indent }} className="font-monospace">{JSON.stringify(node)}</div>;
    }

    if (Array.isArray(node)) {
      return (
        <div style={{ marginLeft: indent }}>
          <span className="text-muted">[</span>
          {node.map((item, idx) => (
            <div key={idx}>
              {renderNode(item, depth + 1)}
              {idx < node.length - 1 && <span className="text-muted">,</span>}
            </div>
          ))}
          <div style={{ marginLeft: indent }} className="text-muted">]</div>
        </div>
      );
    }

    if (typeof node === 'object') {
      return (
        <div style={{ marginLeft: indent }}>
          <span className="text-primary">{node.type || 'Object'}</span>
          <span className="text-muted"> {'{'}</span>
          <div style={{ marginLeft: '20px' }}>
            {Object.entries(node).map(([key, value]) => (
              <div key={key}>
                <span className="text-secondary">{key}:</span>{' '}
                {typeof value === 'object' ? renderNode(value, depth + 1) : JSON.stringify(value)}
              </div>
            ))}
          </div>
          <span className="text-muted">{'}'}</span>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="card mb-4">
      <div className="card-header bg-warning" role="button" onClick={() => setExpanded(!expanded)}>
        <h5 className="mb-0" style={{ cursor: 'pointer' }}>
          <SectionTitle
            icon="diagram-3"
            chevron={expanded ? 'chevron-down' : 'chevron-right'}
          >
            Abstract Syntax Tree (Debug)
          </SectionTitle>
        </h5>
      </div>
      {expanded && (
        <div className="card-body">
          <div className="bg-dark text-light p-3 rounded font-monospace" style={{ fontSize: '0.8rem', overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
            {renderNode(ast)}
          </div>
        </div>
      )}
    </div>
  );
};

export default AstViewer;
