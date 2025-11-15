import { useState, useCallback, useEffect, useRef } from 'react';
import { parseError, getErrorMessage } from '../utils/errorHandler';

/**
 * Custom hook for managing async operations with loading, error, and data states
 * @param {Function} asyncFunction - Async function to execute
 * @param {boolean} immediate - Whether to execute immediately on mount
 * @returns {Object} State and control functions
 */
export const useAsync = (asyncFunction, immediate = false) => {
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const isMountedRef = useRef(true);

  // Track if component is mounted to avoid state updates after unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  /**
   * Execute the async function
   */
  const execute = useCallback(
    async (...params) => {
      setStatus('loading');
      setData(null);
      setError(null);

      try {
        const response = await asyncFunction(...params);
        
        if (isMountedRef.current) {
          setData(response);
          setStatus('success');
        }
        
        return response;
      } catch (err) {
        const parsedError = parseError(err);
        
        if (isMountedRef.current) {
          setError(parsedError);
          setStatus('error');
        }
        
        throw parsedError;
      }
    },
    [asyncFunction]
  );

  /**
   * Reset state to idle
   */
  const reset = useCallback(() => {
    setStatus('idle');
    setData(null);
    setError(null);
  }, []);

  /**
   * Execute immediately on mount if requested
   */
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    execute,
    reset,
    status,
    data,
    error,
    isIdle: status === 'idle',
    isLoading: status === 'loading',
    isSuccess: status === 'success',
    isError: status === 'error',
    errorMessage: error ? getErrorMessage(error) : null,
  };
};

/**
 * Custom hook for managing multiple async operations
 * Useful for forms or pages with multiple independent API calls
 */
export const useAsyncMultiple = () => {
  const [operations, setOperations] = useState({});

  const register = useCallback((key, asyncFunction) => {
    setOperations(prev => ({
      ...prev,
      [key]: {
        status: 'idle',
        data: null,
        error: null,
        execute: async (...params) => {
          setOperations(prev => ({
            ...prev,
            [key]: { ...prev[key], status: 'loading', error: null },
          }));

          try {
            const response = await asyncFunction(...params);
            setOperations(prev => ({
              ...prev,
              [key]: { ...prev[key], status: 'success', data: response },
            }));
            return response;
          } catch (err) {
            const parsedError = parseError(err);
            setOperations(prev => ({
              ...prev,
              [key]: { ...prev[key], status: 'error', error: parsedError },
            }));
            throw parsedError;
          }
        },
      },
    }));
  }, []);

  const getOperation = useCallback((key) => {
    return operations[key] || { status: 'idle', data: null, error: null };
  }, [operations]);

  const isAnyLoading = useCallback(() => {
    return Object.values(operations).some(op => op.status === 'loading');
  }, [operations]);

  return {
    register,
    getOperation,
    isAnyLoading,
    operations,
  };
};

export default useAsync;
