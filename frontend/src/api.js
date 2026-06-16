/**
 * Axios API client for SQL Optimizer backend.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Execute a SQL query.
 * @param {string} query - The SQL query to execute
 * @param {object} options - Execution options
 * @param {boolean} options.debug - Whether to include AST in response
 * @param {boolean} options.optimize - Whether to optimize and compare queries
 * @returns {Promise} Response with original/optimized query times
 */
export const executeQuery = (query, { debug = false, optimize = false } = {}) => {
  return client.post('/api/execute', { query, debug, optimize });
};

/**
 * Get the database schema.
 * @returns {Promise} Schema object
 */
export const getSchema = () => {
  return client.get('/api/schema');
};

/**
 * Reset the database to initial state.
 * @returns {Promise} Success message
 */
export const resetDatabase = () => {
  return client.post('/api/reset');
};

export default client;
