# Custom React Hooks

This directory contains custom React hooks for common functionality.

## useAuth

Hook for accessing authentication context and methods.

```javascript
import { useAuth } from '../hooks/useAuth';

const MyComponent = () => {
  const { user, login, logout, isAuthenticated } = useAuth();

  const handleLogin = async () => {
    const result = await login(email, password);
    if (result.success) {
      // Handle success
    }
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user.full_name}!</p>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
};
```

## useGeolocation

Hook for accessing device geolocation with error handling.

```javascript
import { useGeolocation } from '../hooks/useGeolocation';

const MyComponent = () => {
  const { location, error, loading, getCurrentLocation } = useGeolocation();

  const handleGetLocation = async () => {
    try {
      const coords = await getCurrentLocation();
      console.log(coords.latitude, coords.longitude, coords.accuracy);
    } catch (err) {
      console.error('Location error:', err);
    }
  };

  return (
    <div>
      {loading && <p>Getting location...</p>}
      {error && <p>Error: {error}</p>}
      {location && (
        <p>
          Location: {location.latitude}, {location.longitude}
          (Accuracy: {location.accuracy}m)
        </p>
      )}
      <button onClick={handleGetLocation}>Get Location</button>
    </div>
  );
};
```

## useFormValidation

Hook for managing form state with validation.

```javascript
import { useFormValidation } from '../hooks/useFormValidation';

const MyForm = () => {
  const {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    setFieldErrors,
    resetForm,
    getFieldProps,
    getFieldMeta,
  } = useFormValidation(
    // Initial values
    {
      email: '',
      password: '',
      radius: 50,
    },
    // Validation schema
    {
      email: ['required', 'email'],
      password: ['required', 'password'],
      radius: ['required', 'radius'],
    },
    // Submit handler
    async (values) => {
      await api.post('/endpoint', values);
    }
  );

  return (
    <form onSubmit={handleSubmit}>
      {/* Manual field binding */}
      <input
        name="email"
        value={values.email}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      {touched.email && errors.email && <span>{errors.email}</span>}

      {/* Or use helper functions */}
      <input {...getFieldProps('password')} />
      {getFieldMeta('password').hasError && (
        <span>{getFieldMeta('password').error}</span>
      )}

      {/* Programmatic field updates */}
      <button type="button" onClick={() => setFieldValue('radius', 100)}>
        Set Radius to 100m
      </button>

      <button type="submit" disabled={isSubmitting || !isValid}>
        Submit
      </button>
    </form>
  );
};
```

### useFormValidation API

**State:**
- `values`: Current form values
- `errors`: Validation errors for each field
- `touched`: Fields that have been touched (blurred)
- `isSubmitting`: Whether form is currently submitting
- `submitCount`: Number of times form has been submitted
- `isValid`: Whether form has no errors

**Handlers:**
- `handleChange(e)`: Handle input change events
- `handleBlur(e)`: Handle input blur events
- `handleSubmit(e)`: Handle form submission
- `setFieldValue(name, value)`: Set a field value programmatically
- `setFieldError(name, error)`: Set a field error
- `setFieldErrors(errors)`: Set multiple field errors (e.g., from API)
- `setFieldTouched(name, touched)`: Mark a field as touched
- `validate()`: Manually validate all fields
- `resetForm()`: Reset form to initial state

**Helpers:**
- `getFieldProps(name)`: Get props for input binding (name, value, onChange, onBlur)
- `getFieldMeta(name)`: Get field metadata (error, touched, hasError)

## useAsync

Hook for managing async operations with loading, error, and data states.

```javascript
import { useAsync } from '../hooks/useAsync';
import { attendanceAPI } from '../services/api';

const MyComponent = () => {
  const {
    execute,
    reset,
    status,
    data,
    error,
    isLoading,
    isSuccess,
    isError,
    errorMessage,
  } = useAsync(attendanceAPI.getSession);

  const loadSession = async (sessionId) => {
    try {
      const session = await execute(sessionId);
      console.log('Session loaded:', session);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  return (
    <div>
      {isLoading && <LoadingSpinner />}
      {isError && <p>Error: {errorMessage}</p>}
      {isSuccess && <SessionDetails data={data} />}
      
      <button onClick={() => loadSession(123)}>Load Session</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
};
```

### useAsync with Immediate Execution

```javascript
const { data, isLoading, error } = useAsync(
  () => attendanceAPI.getSessions(),
  true // Execute immediately on mount
);
```

### useAsync API

**State:**
- `status`: Current status ('idle', 'loading', 'success', 'error')
- `data`: Response data (null until success)
- `error`: Parsed error object (null until error)
- `isIdle`: Status is idle
- `isLoading`: Status is loading
- `isSuccess`: Status is success
- `isError`: Status is error
- `errorMessage`: User-friendly error message

**Methods:**
- `execute(...params)`: Execute the async function with parameters
- `reset()`: Reset state to idle

## useAsyncMultiple

Hook for managing multiple independent async operations.

```javascript
import { useAsyncMultiple } from '../hooks/useAsync';

const MyComponent = () => {
  const { register, getOperation, isAnyLoading } = useAsyncMultiple();

  useEffect(() => {
    register('courses', () => api.get('/courses'));
    register('sessions', () => api.get('/sessions'));
  }, []);

  const loadData = async () => {
    const coursesOp = getOperation('courses');
    const sessionsOp = getOperation('sessions');

    await Promise.all([
      coursesOp.execute(),
      sessionsOp.execute(),
    ]);
  };

  const coursesOp = getOperation('courses');
  const sessionsOp = getOperation('sessions');

  return (
    <div>
      {isAnyLoading() && <LoadingOverlay loading />}
      
      {coursesOp.status === 'success' && (
        <CourseList courses={coursesOp.data} />
      )}
      
      {sessionsOp.status === 'success' && (
        <SessionList sessions={sessionsOp.data} />
      )}
      
      <button onClick={loadData}>Load All Data</button>
    </div>
  );
};
```

## Complete Example: Form with Async Submission

```javascript
import { useFormValidation } from '../hooks/useFormValidation';
import { useToast } from '../components/shared';
import { FormInput, LoadingButton } from '../components/shared';
import { formatValidationErrors, getErrorMessage } from '../utils/errorHandler';
import { userAPI } from '../services/api';

const UserForm = ({ onSuccess }) => {
  const toast = useToast();

  const form = useFormValidation(
    {
      email: '',
      full_name: '',
      password: '',
      role: 'student',
    },
    {
      email: ['required', 'email'],
      full_name: ['required', validationRules.minLength(2)],
      password: ['required', 'passwordStrong'],
      role: ['required'],
    },
    async (values) => {
      try {
        const user = await userAPI.createUser(values);
        toast.showSuccess('User created successfully!');
        form.resetForm();
        onSuccess?.(user);
      } catch (error) {
        if (error.status === 400) {
          // Handle validation errors from API
          const fieldErrors = formatValidationErrors(error.data);
          form.setFieldErrors(fieldErrors);
        } else {
          // Show generic error
          toast.showError(getErrorMessage(error));
        }
        throw error;
      }
    }
  );

  return (
    <form onSubmit={form.handleSubmit} className="space-y-4">
      <FormInput
        label="Email"
        type="email"
        {...form.getFieldProps('email')}
        {...form.getFieldMeta('email')}
        required
      />

      <FormInput
        label="Full Name"
        {...form.getFieldProps('full_name')}
        {...form.getFieldMeta('full_name')}
        required
      />

      <FormInput
        label="Password"
        type="password"
        {...form.getFieldProps('password')}
        {...form.getFieldMeta('password')}
        required
      />

      <FormSelect
        label="Role"
        {...form.getFieldProps('role')}
        {...form.getFieldMeta('role')}
        options={[
          { value: 'admin', label: 'Administrator' },
          { value: 'teacher', label: 'Teacher' },
          { value: 'student', label: 'Student' },
        ]}
        required
      />

      <LoadingButton
        type="submit"
        loading={form.isSubmitting}
        disabled={!form.isValid}
        variant="primary"
        fullWidth
      >
        Create User
      </LoadingButton>
    </form>
  );
};
```
