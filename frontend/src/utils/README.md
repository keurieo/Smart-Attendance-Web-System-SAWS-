# Utility Functions

This directory contains utility functions for error handling, validation, and storage.

## Error Handler

Comprehensive error handling utilities for API responses and network errors.

### parseError(error)

Parse error response from API and extract error code and message.

```javascript
import { parseError } from '../utils/errorHandler';

try {
  await api.post('/endpoint', data);
} catch (error) {
  const parsed = parseError(error);
  console.log(parsed.code);    // Error code (e.g., 'ATT_001')
  console.log(parsed.message);  // User-friendly message
  console.log(parsed.details);  // Additional details
}
```

### getErrorMessage(error)

Get a user-friendly error message for display.

```javascript
import { getErrorMessage } from '../utils/errorHandler';

try {
  await api.post('/endpoint', data);
} catch (error) {
  const message = getErrorMessage(error);
  toast.showError(message);
}
```

### formatValidationErrors(errorData)

Format validation errors from API response into field-specific errors.

```javascript
import { formatValidationErrors } from '../utils/errorHandler';

try {
  await api.post('/users/', userData);
} catch (error) {
  const fieldErrors = formatValidationErrors(error.data);
  setFieldErrors(fieldErrors);
  // { email: 'This email is already taken', password: 'Password too short' }
}
```

### retryRequest(requestFn, maxRetries)

Retry a failed request with exponential backoff.

```javascript
import { retryRequest } from '../utils/errorHandler';

const data = await retryRequest(
  () => api.get('/endpoint'),
  3 // max retries
);
```

### Error Codes

The system uses standardized error codes:

- **AUTH_xxx**: Authentication errors
  - AUTH_001: Invalid credentials
  - AUTH_002: Token expired
  - AUTH_003: Insufficient permissions

- **VAL_xxx**: Validation errors
  - VAL_001: Missing required field
  - VAL_002: Invalid format
  - VAL_003: Constraint violation

- **ATT_xxx**: Attendance errors
  - ATT_001: Outside allowed radius
  - ATT_002: Outside time window
  - ATT_003: Token expired
  - ATT_004: Duplicate submission
  - ATT_005: Location accuracy insufficient

- **BIZ_xxx**: Business logic errors
  - BIZ_001: Teacher not assigned to course
  - BIZ_002: Student not enrolled in course
  - BIZ_003: Session already expired

## Validators

Form validation utilities with comprehensive validation rules.

### Validation Rules

```javascript
import { validationRules, validateField, validateForm } from '../utils/validators';

// Single field validation
const error = validateField(email, ['required', 'email']);
if (error) {
  console.log(error); // "Please enter a valid email address"
}

// Form validation with schema
const schema = {
  email: ['required', 'email'],
  password: ['required', 'password'],
  radius: ['required', 'radius'],
};

const errors = validateForm(formData, schema);
// { email: 'This field is required', ... }
```

### Available Validation Rules

- `required`: Field must not be empty
- `email`: Valid email format
- `password`: Minimum 8 characters
- `passwordStrong`: 8+ chars with uppercase, lowercase, and numbers
- `minLength(n)`: Minimum length
- `maxLength(n)`: Maximum length
- `min(n)`: Minimum numeric value
- `max(n)`: Maximum numeric value
- `range(min, max)`: Value within range
- `numeric`: Valid number
- `integer`: Whole number
- `coordinates`: Valid lat/lon coordinates
- `latitude`: Valid latitude (-90 to 90)
- `longitude`: Valid longitude (-180 to 180)
- `radius`: Valid radius (10 to 500 meters)
- `sixDigitCode`: 6-digit numeric code
- `dateTime`: Valid date/time
- `futureDate`: Date in the future
- `dateRange`: End date after start date
- `match(fieldName)`: Match another field
- `url`: Valid URL
- `phoneNumber`: Valid phone number

### Custom Validation

```javascript
// Custom validation function
const customRule = (value, formData) => {
  if (value !== formData.password) {
    return 'Passwords do not match';
  }
  return true; // Valid
};

const error = validateField(confirmPassword, [customRule]);
```

### Using with Forms

```javascript
import { useFormValidation } from '../hooks/useFormValidation';

const MyForm = () => {
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    getFieldProps,
    getFieldMeta,
  } = useFormValidation(
    { email: '', password: '' }, // initial values
    {
      email: ['required', 'email'],
      password: ['required', 'password'],
    }, // validation schema
    async (values) => {
      // submit handler
      await api.post('/login', values);
    }
  );

  return (
    <form onSubmit={handleSubmit}>
      <FormInput
        label="Email"
        {...getFieldProps('email')}
        {...getFieldMeta('email')}
      />
      <LoadingButton loading={isSubmitting} type="submit">
        Submit
      </LoadingButton>
    </form>
  );
};
```

## Storage

Local storage utilities for managing authentication tokens and user data.

```javascript
import { storage } from '../utils/storage';

// Access token
storage.setAccessToken(token);
const token = storage.getAccessToken();
storage.removeAccessToken();

// Refresh token
storage.setRefreshToken(token);
const refreshToken = storage.getRefreshToken();
storage.removeRefreshToken();

// User data
storage.setUser(userData);
const user = storage.getUser();
storage.removeUser();

// Clear all
storage.clearAll();
```

## Complete Example

Here's a complete example combining error handling, validation, and loading states:

```javascript
import { useState } from 'react';
import { useFormValidation } from '../hooks/useFormValidation';
import { useToast } from '../components/shared';
import { FormInput, LoadingButton } from '../components/shared';
import { formatValidationErrors, getErrorMessage } from '../utils/errorHandler';
import { attendanceAPI } from '../services/api';

const CreateSessionForm = () => {
  const toast = useToast();
  
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldErrors,
    getFieldProps,
    getFieldMeta,
  } = useFormValidation(
    {
      course_id: '',
      radius_meters: 50,
      start_at: '',
      end_at: '',
    },
    {
      course_id: ['required'],
      radius_meters: ['required', 'radius'],
      start_at: ['required', 'dateTime'],
      end_at: ['required', 'dateTime'],
    },
    async (values) => {
      try {
        const response = await attendanceAPI.createSession(values);
        toast.showSuccess('Session created successfully!');
        return response;
      } catch (error) {
        // Handle validation errors from API
        if (error.status === 400 && error.data) {
          const fieldErrors = formatValidationErrors(error.data);
          setFieldErrors(fieldErrors);
        } else {
          // Show generic error message
          toast.showError(getErrorMessage(error));
        }
        throw error;
      }
    }
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormInput
        label="Course ID"
        type="text"
        {...getFieldProps('course_id')}
        {...getFieldMeta('course_id')}
        required
      />
      
      <FormInput
        label="Radius (meters)"
        type="number"
        {...getFieldProps('radius_meters')}
        {...getFieldMeta('radius_meters')}
        required
      />
      
      <FormInput
        label="Start Time"
        type="datetime-local"
        {...getFieldProps('start_at')}
        {...getFieldMeta('start_at')}
        required
      />
      
      <FormInput
        label="End Time"
        type="datetime-local"
        {...getFieldProps('end_at')}
        {...getFieldMeta('end_at')}
        required
      />
      
      <LoadingButton
        type="submit"
        loading={isSubmitting}
        variant="primary"
        fullWidth
      >
        Create Session
      </LoadingButton>
    </form>
  );
};
```
