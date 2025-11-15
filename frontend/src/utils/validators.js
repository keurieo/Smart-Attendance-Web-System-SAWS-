/**
 * Form validation utilities
 * Provides validation functions and error messages for form fields
 */

/**
 * Validation rules with error messages
 */
export const validationRules = {
  required: {
    validate: (value) => {
      if (typeof value === 'string') {
        return value.trim() !== '';
      }
      return value !== null && value !== undefined && value !== '';
    },
    message: 'This field is required',
  },

  email: {
    validate: (value) => {
      if (!value) return true; // Let required handle empty values
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(value);
    },
    message: 'Please enter a valid email address',
  },

  password: {
    validate: (value) => {
      if (!value) return true;
      return value.length >= 8;
    },
    message: 'Password must be at least 8 characters',
  },

  passwordStrong: {
    validate: (value) => {
      if (!value) return true;
      // At least 8 chars, 1 uppercase, 1 lowercase, 1 number
      const hasLength = value.length >= 8;
      const hasUpper = /[A-Z]/.test(value);
      const hasLower = /[a-z]/.test(value);
      const hasNumber = /[0-9]/.test(value);
      return hasLength && hasUpper && hasLower && hasNumber;
    },
    message: 'Password must contain at least 8 characters, including uppercase, lowercase, and numbers',
  },

  minLength: (min) => ({
    validate: (value) => {
      if (!value) return true;
      return value.length >= min;
    },
    message: `Must be at least ${min} characters`,
  }),

  maxLength: (max) => ({
    validate: (value) => {
      if (!value) return true;
      return value.length <= max;
    },
    message: `Must be no more than ${max} characters`,
  }),

  min: (min) => ({
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      return Number(value) >= min;
    },
    message: `Must be at least ${min}`,
  }),

  max: (max) => ({
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      return Number(value) <= max;
    },
    message: `Must be no more than ${max}`,
  }),

  range: (min, max) => ({
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      const num = Number(value);
      return num >= min && num <= max;
    },
    message: `Must be between ${min} and ${max}`,
  }),

  numeric: {
    validate: (value) => {
      if (!value) return true;
      return !isNaN(value) && !isNaN(parseFloat(value));
    },
    message: 'Must be a valid number',
  },

  integer: {
    validate: (value) => {
      if (!value) return true;
      return Number.isInteger(Number(value));
    },
    message: 'Must be a whole number',
  },

  coordinates: {
    validate: (lat, lon) => {
      return (
        lat !== null &&
        lon !== null &&
        lat >= -90 &&
        lat <= 90 &&
        lon >= -180 &&
        lon <= 180 &&
        !(lat === 0 && lon === 0)
      );
    },
    message: 'Invalid coordinates',
  },

  latitude: {
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      const num = Number(value);
      return !isNaN(num) && num >= -90 && num <= 90;
    },
    message: 'Latitude must be between -90 and 90',
  },

  longitude: {
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      const num = Number(value);
      return !isNaN(num) && num >= -180 && num <= 180;
    },
    message: 'Longitude must be between -180 and 180',
  },

  radius: {
    validate: (value) => {
      if (value === null || value === undefined || value === '') return true;
      const num = Number(value);
      return !isNaN(num) && num >= 10 && num <= 500;
    },
    message: 'Radius must be between 10 and 500 meters',
  },

  sixDigitCode: {
    validate: (value) => {
      if (!value) return true;
      return /^\d{6}$/.test(value);
    },
    message: 'Must be a 6-digit code',
  },

  dateTime: {
    validate: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return !isNaN(date.getTime());
    },
    message: 'Invalid date/time',
  },

  futureDate: {
    validate: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return date > new Date();
    },
    message: 'Date must be in the future',
  },

  dateRange: {
    validate: (startDate, endDate) => {
      if (!startDate || !endDate) return true;
      return new Date(startDate) < new Date(endDate);
    },
    message: 'End date must be after start date',
  },

  match: (fieldName) => ({
    validate: (value, formData) => {
      if (!value) return true;
      return value === formData[fieldName];
    },
    message: `Must match ${fieldName}`,
  }),

  url: {
    validate: (value) => {
      if (!value) return true;
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },
    message: 'Must be a valid URL',
  },

  phoneNumber: {
    validate: (value) => {
      if (!value) return true;
      // Basic phone number validation (10-15 digits)
      return /^\+?[\d\s-]{10,15}$/.test(value);
    },
    message: 'Please enter a valid phone number',
  },
};

/**
 * Validate a single field against multiple rules
 * @param {*} value - Field value
 * @param {Array|Object} rules - Validation rules to apply
 * @param {Object} formData - Complete form data (for cross-field validation)
 * @returns {string|null} Error message or null if valid
 */
export const validateField = (value, rules, formData = {}) => {
  if (!rules) return null;

  // Convert single rule to array
  const ruleArray = Array.isArray(rules) ? rules : [rules];

  for (const rule of ruleArray) {
    let isValid;
    let message;

    if (typeof rule === 'string') {
      // Rule name from validationRules
      const validationRule = validationRules[rule];
      if (!validationRule) continue;
      
      isValid = validationRule.validate(value, formData);
      message = validationRule.message;
    } else if (typeof rule === 'function') {
      // Custom validation function
      const result = rule(value, formData);
      if (typeof result === 'string') {
        return result; // Custom error message
      }
      isValid = result;
      message = 'Invalid value';
    } else if (typeof rule === 'object' && rule.validate) {
      // Rule object with validate function
      isValid = rule.validate(value, formData);
      message = rule.message || 'Invalid value';
    }

    if (!isValid) {
      return message;
    }
  }

  return null;
};

/**
 * Validate entire form
 * @param {Object} formData - Form data to validate
 * @param {Object} validationSchema - Schema defining validation rules for each field
 * @returns {Object} Object with field names as keys and error messages as values
 */
export const validateForm = (formData, validationSchema) => {
  const errors = {};

  Object.keys(validationSchema).forEach(fieldName => {
    const rules = validationSchema[fieldName];
    const value = formData[fieldName];
    const error = validateField(value, rules, formData);

    if (error) {
      errors[fieldName] = error;
    }
  });

  return errors;
};

/**
 * Check if form has any errors
 * @param {Object} errors - Errors object
 * @returns {boolean} True if form has errors
 */
export const hasErrors = (errors) => {
  return Object.keys(errors).length > 0;
};

/**
 * Legacy validators for backward compatibility
 */
export const validators = {
  email: (email) => validationRules.email.validate(email),
  password: (password) => validationRules.password.validate(password),
  required: (value) => validationRules.required.validate(value),
  coordinates: (lat, lon) => validationRules.coordinates.validate(lat, lon),
};

export default {
  validationRules,
  validateField,
  validateForm,
  hasErrors,
  validators,
};
