import { useState, useCallback } from 'react';
import { validateField, validateForm, hasErrors } from '../utils/validators';

/**
 * Custom hook for form validation
 * @param {Object} initialValues - Initial form values
 * @param {Object} validationSchema - Validation rules for each field
 * @param {Function} onSubmit - Submit handler function
 * @returns {Object} Form state and handlers
 */
export const useFormValidation = (initialValues = {}, validationSchema = {}, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitCount, setSubmitCount] = useState(0);

  /**
   * Handle field value change
   */
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;

    setValues(prev => ({
      ...prev,
      [name]: fieldValue,
    }));

    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  }, [errors]);

  /**
   * Handle field blur (mark as touched and validate)
   */
  const handleBlur = useCallback((e) => {
    const { name } = e.target;

    setTouched(prev => ({
      ...prev,
      [name]: true,
    }));

    // Validate field on blur
    if (validationSchema[name]) {
      const error = validateField(values[name], validationSchema[name], values);
      if (error) {
        setErrors(prev => ({
          ...prev,
          [name]: error,
        }));
      }
    }
  }, [values, validationSchema]);

  /**
   * Set a specific field value programmatically
   */
  const setFieldValue = useCallback((name, value) => {
    setValues(prev => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  }, [errors]);

  /**
   * Set a specific field error
   */
  const setFieldError = useCallback((name, error) => {
    setErrors(prev => ({
      ...prev,
      [name]: error,
    }));
  }, []);

  /**
   * Set multiple field errors (e.g., from API response)
   */
  const setFieldErrors = useCallback((fieldErrors) => {
    setErrors(prev => ({
      ...prev,
      ...fieldErrors,
    }));
  }, []);

  /**
   * Mark a field as touched
   */
  const setFieldTouched = useCallback((name, isTouched = true) => {
    setTouched(prev => ({
      ...prev,
      [name]: isTouched,
    }));
  }, []);

  /**
   * Validate all fields
   */
  const validate = useCallback(() => {
    const validationErrors = validateForm(values, validationSchema);
    setErrors(validationErrors);
    return !hasErrors(validationErrors);
  }, [values, validationSchema]);

  /**
   * Reset form to initial values
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    setSubmitCount(0);
  }, [initialValues]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (e) => {
    if (e) {
      e.preventDefault();
    }

    setSubmitCount(prev => prev + 1);

    // Mark all fields as touched
    const allTouched = Object.keys(validationSchema).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);

    // Validate form
    const validationErrors = validateForm(values, validationSchema);
    setErrors(validationErrors);

    if (hasErrors(validationErrors)) {
      return;
    }

    // Submit form
    if (onSubmit) {
      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } catch (error) {
        // Error handling is done in the onSubmit function
      } finally {
        setIsSubmitting(false);
      }
    }
  }, [values, validationSchema, onSubmit]);

  /**
   * Get field props for easy integration with inputs
   */
  const getFieldProps = useCallback((name) => {
    return {
      name,
      value: values[name] || '',
      onChange: handleChange,
      onBlur: handleBlur,
    };
  }, [values, handleChange, handleBlur]);

  /**
   * Get field meta information
   */
  const getFieldMeta = useCallback((name) => {
    return {
      error: errors[name],
      touched: touched[name],
      hasError: touched[name] && errors[name],
    };
  }, [errors, touched]);

  return {
    // Form state
    values,
    errors,
    touched,
    isSubmitting,
    submitCount,
    isValid: !hasErrors(errors),

    // Handlers
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    setFieldErrors,
    setFieldTouched,
    validate,
    resetForm,

    // Helper functions
    getFieldProps,
    getFieldMeta,
  };
};

export default useFormValidation;
