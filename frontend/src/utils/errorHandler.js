/**
 * Error handling utilities for API responses and network errors
 */

// Error code to user-friendly message mapping
const ERROR_MESSAGES = {
  // Authentication errors
  AUTH_001: 'Invalid email or password. Please try again.',
  AUTH_002: 'Your session has expired. Please log in again.',
  AUTH_003: 'You do not have permission to perform this action.',
  
  // Validation errors
  VAL_001: 'Please fill in all required fields.',
  VAL_002: 'The data you entered is not in the correct format.',
  VAL_003: 'This value already exists in the system.',
  
  // Attendance errors
  ATT_001: 'You are too far from the class location to mark attendance.',
  ATT_002: 'The attendance session is not currently active.',
  ATT_003: 'The QR code has expired. Please ask your teacher for a new one.',
  ATT_004: 'You have already marked attendance for this session.',
  ATT_005: 'Your location accuracy is insufficient. Please try again in a better location.',
  
  // Business logic errors
  BIZ_001: 'You are not assigned to teach this course.',
  BIZ_002: 'You are not enrolled in this course.',
  BIZ_003: 'This session has already expired.',
  
  // Generic errors
  NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
  TIMEOUT_ERROR: 'The request took too long. Please try again.',
  SERVER_ERROR: 'Something went wrong on our end. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
};

/**
 * Parse error response from API and extract error code and message
 * @param {Object} error - Error object from axios or API
 * @returns {Object} Parsed error with code, message, and details
 */
export const parseError = (error) => {
  // Handle network errors
  if (error.isNetworkError || !error.response) {
    return {
      code: 'NETWORK_ERROR',
      message: ERROR_MESSAGES.NETWORK_ERROR,
      details: null,
      isNetworkError: true,
    };
  }

  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return {
      code: 'TIMEOUT_ERROR',
      message: ERROR_MESSAGES.TIMEOUT_ERROR,
      details: null,
    };
  }

  const status = error.status || error.response?.status;
  const data = error.data || error.response?.data || {};

  // Extract error code from response
  const errorCode = data.error_code || data.code;
  
  // Extract error message from various possible fields
  const apiMessage = data.message || data.detail || data.error;
  
  // Get user-friendly message based on error code
  const userMessage = errorCode && ERROR_MESSAGES[errorCode] 
    ? ERROR_MESSAGES[errorCode]
    : apiMessage || getDefaultMessageForStatus(status);

  return {
    code: errorCode || `HTTP_${status}`,
    message: userMessage,
    details: data.details || null,
    status,
    originalError: error,
  };
};

/**
 * Get default error message based on HTTP status code
 * @param {number} status - HTTP status code
 * @returns {string} Default error message
 */
const getDefaultMessageForStatus = (status) => {
  switch (status) {
    case 400:
      return 'The request was invalid. Please check your input and try again.';
    case 401:
      return 'You need to log in to access this resource.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 409:
      return 'This action conflicts with existing data.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
    case 502:
    case 503:
    case 504:
      return ERROR_MESSAGES.SERVER_ERROR;
    default:
      return ERROR_MESSAGES.UNKNOWN_ERROR;
  }
};

/**
 * Format validation errors from API response
 * @param {Object} errorData - Error data from API
 * @returns {Object} Field-specific error messages
 */
export const formatValidationErrors = (errorData) => {
  const errors = {};
  
  if (!errorData) return errors;

  // Handle Django REST Framework validation error format
  if (typeof errorData === 'object') {
    Object.keys(errorData).forEach(field => {
      const fieldErrors = errorData[field];
      
      if (Array.isArray(fieldErrors)) {
        // Take the first error message for each field
        errors[field] = fieldErrors[0];
      } else if (typeof fieldErrors === 'string') {
        errors[field] = fieldErrors;
      }
    });
  }

  return errors;
};

/**
 * Retry configuration for network requests
 */
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryableStatuses: [408, 429, 500, 502, 503, 504],
  retryableErrors: ['ECONNABORTED', 'ETIMEDOUT', 'ENOTFOUND', 'ENETUNREACH'],
};

/**
 * Determine if an error is retryable
 * @param {Object} error - Error object
 * @returns {boolean} Whether the error should be retried
 */
export const isRetryableError = (error) => {
  // Network errors are retryable
  if (error.isNetworkError || !error.response) {
    return true;
  }

  // Check if error code is retryable
  if (error.code && RETRY_CONFIG.retryableErrors.includes(error.code)) {
    return true;
  }

  // Check if status code is retryable
  const status = error.status || error.response?.status;
  return RETRY_CONFIG.retryableStatuses.includes(status);
};

/**
 * Calculate delay for retry attempt with exponential backoff
 * @param {number} attemptNumber - Current attempt number (0-indexed)
 * @returns {number} Delay in milliseconds
 */
export const getRetryDelay = (attemptNumber) => {
  // Exponential backoff: 1s, 2s, 4s
  return RETRY_CONFIG.retryDelay * Math.pow(2, attemptNumber);
};

/**
 * Retry a failed request with exponential backoff
 * @param {Function} requestFn - Function that returns a promise for the request
 * @param {number} maxRetries - Maximum number of retry attempts
 * @returns {Promise} Result of the request
 */
export const retryRequest = async (requestFn, maxRetries = RETRY_CONFIG.maxRetries) => {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry if error is not retryable or we've exhausted retries
      if (!isRetryableError(error) || attempt === maxRetries) {
        throw error;
      }
      
      // Wait before retrying
      const delay = getRetryDelay(attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
};

/**
 * Create a user-friendly error message for display
 * @param {Object} error - Parsed error object
 * @returns {string} Formatted error message
 */
export const getErrorMessage = (error) => {
  const parsed = parseError(error);
  
  // Include details if available
  if (parsed.details) {
    if (parsed.details.distance_meters && parsed.details.allowed_radius) {
      return `${parsed.message} You are ${Math.round(parsed.details.distance_meters)}m away (allowed: ${parsed.details.allowed_radius}m).`;
    }
  }
  
  return parsed.message;
};

/**
 * Log error for debugging (can be extended to send to error tracking service)
 * @param {Object} error - Error object
 * @param {Object} context - Additional context about where the error occurred
 */
export const logError = (error, context = {}) => {
  const parsed = parseError(error);
  
  console.error('Error occurred:', {
    ...parsed,
    context,
    timestamp: new Date().toISOString(),
  });
  
  // In production, send to error tracking service (e.g., Sentry)
  // if (process.env.NODE_ENV === 'production') {
  //   Sentry.captureException(error, { extra: context });
  // }
};

export default {
  parseError,
  formatValidationErrors,
  isRetryableError,
  getRetryDelay,
  retryRequest,
  getErrorMessage,
  logError,
};
