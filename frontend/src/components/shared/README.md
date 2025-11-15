# Shared UI Components

This directory contains reusable UI components used throughout the Smart Attendance System.

## Components

### DataTable

A feature-rich data table component with sorting, pagination, and row actions.

**Props:**
- `columns` (array, required): Column definitions with `key`, `label`, `sortable`, and optional `render` function
- `data` (array, required): Array of data objects to display
- `pagination` (boolean, default: true): Enable/disable pagination
- `pageSize` (number, default: 10): Number of rows per page
- `onRowAction` (object): Action handlers for edit, delete, and custom actions
- `loading` (boolean, default: false): Show loading spinner
- `emptyMessage` (string): Message to display when no data

**Example:**
```jsx
import { DataTable } from '../components/shared';

const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email' },
  { key: 'status', label: 'Status', render: (value) => <Badge>{value}</Badge> },
];

<DataTable
  columns={columns}
  data={users}
  onRowAction={{
    edit: (row) => handleEdit(row),
    delete: (row) => handleDelete(row),
  }}
/>
```

### Modal

A flexible modal dialog component with backdrop and keyboard support.

**Props:**
- `isOpen` (boolean, required): Control modal visibility
- `onClose` (function, required): Handler for closing modal
- `title` (string, required): Modal title
- `children` (node): Modal content
- `actions` (node): Action buttons (typically in footer)
- `size` (string, default: 'md'): Modal size ('sm', 'md', 'lg', 'xl', 'full')
- `closeOnBackdrop` (boolean, default: true): Close on backdrop click
- `closeOnEscape` (boolean, default: true): Close on Escape key

**Example:**
```jsx
import { Modal } from '../components/shared';

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Create User"
  size="lg"
  actions={
    <>
      <button onClick={() => setIsOpen(false)}>Cancel</button>
      <button onClick={handleSubmit}>Save</button>
    </>
  }
>
  <form>{/* form fields */}</form>
</Modal>
```

### Toast

A toast notification system with context provider and hook.

**Setup:**
Wrap your app with `ToastProvider`:
```jsx
import { ToastProvider } from './components/shared';

<ToastProvider>
  <App />
</ToastProvider>
```

**Usage:**
```jsx
import { useToast } from '../components/shared';

const MyComponent = () => {
  const toast = useToast();

  const handleSuccess = () => {
    toast.showSuccess('Operation completed successfully!');
  };

  const handleError = () => {
    toast.showError('Something went wrong', 10000); // 10 second duration
  };

  const handleInfo = () => {
    toast.showInfo('Here is some information');
  };

  const handleWarning = () => {
    toast.showWarning('Please be careful');
  };
};
```

**Methods:**
- `showSuccess(message, duration)`: Show success toast
- `showError(message, duration)`: Show error toast
- `showInfo(message, duration)`: Show info toast
- `showWarning(message, duration)`: Show warning toast
- `addToast(message, type, duration)`: Generic toast method
- `removeToast(id)`: Manually remove a toast

### MapPreview

A map component using Leaflet to display teacher and student locations with radius overlay.

**Props:**
- `teacherLocation` (object, required): Teacher coordinates `{ latitude, longitude }`
- `studentLocation` (object, optional): Student coordinates `{ latitude, longitude }`
- `radius` (number, default: 50): Radius in meters
- `height` (string, default: '400px'): Map container height
- `zoom` (number, default: 16): Initial zoom level

**Example:**
```jsx
import { MapPreview } from '../components/shared';

<MapPreview
  teacherLocation={{ latitude: 40.7128, longitude: -74.0060 }}
  studentLocation={{ latitude: 40.7130, longitude: -74.0058 }}
  radius={100}
  height="500px"
/>
```

## Form Components

### FormInput

A reusable text input component with built-in validation display.

**Props:**
- `label` (string): Input label
- `name` (string, required): Input name
- `type` (string, default: 'text'): Input type
- `value` (any, required): Input value
- `onChange` (function, required): Change handler
- `onBlur` (function): Blur handler
- `error` (string): Error message
- `touched` (boolean): Whether field has been touched
- `required` (boolean, default: false): Show required indicator
- `disabled` (boolean, default: false): Disable input
- `placeholder` (string): Placeholder text

**Example:**
```jsx
import { FormInput } from '../components/shared';

<FormInput
  label="Email"
  name="email"
  type="email"
  value={formData.email}
  onChange={handleChange}
  onBlur={handleBlur}
  error={errors.email}
  touched={touched.email}
  required
/>
```

### FormSelect

A reusable select dropdown component with validation display.

**Props:**
- `label` (string): Select label
- `name` (string, required): Select name
- `value` (any, required): Selected value
- `onChange` (function, required): Change handler
- `onBlur` (function): Blur handler
- `error` (string): Error message
- `touched` (boolean): Whether field has been touched
- `options` (array, required): Array of `{ value, label, disabled }` objects
- `placeholder` (string): Placeholder option text
- `required` (boolean, default: false): Show required indicator
- `disabled` (boolean, default: false): Disable select

**Example:**
```jsx
import { FormSelect } from '../components/shared';

<FormSelect
  label="Role"
  name="role"
  value={formData.role}
  onChange={handleChange}
  options={[
    { value: 'admin', label: 'Administrator' },
    { value: 'teacher', label: 'Teacher' },
    { value: 'student', label: 'Student' },
  ]}
  error={errors.role}
  touched={touched.role}
  required
/>
```

### FormTextarea

A reusable textarea component with validation display.

**Props:**
- `label` (string): Textarea label
- `name` (string, required): Textarea name
- `value` (any, required): Textarea value
- `onChange` (function, required): Change handler
- `onBlur` (function): Blur handler
- `error` (string): Error message
- `touched` (boolean): Whether field has been touched
- `rows` (number, default: 4): Number of rows
- `required` (boolean, default: false): Show required indicator
- `disabled` (boolean, default: false): Disable textarea
- `placeholder` (string): Placeholder text

## Loading Components

### LoadingSpinner

A simple animated spinner component.

**Props:**
- `size` (string, default: 'md'): Spinner size ('sm', 'md', 'lg', 'xl')
- `color` (string, default: 'blue'): Spinner color ('blue', 'white', 'gray', 'green', 'red')

**Example:**
```jsx
import { LoadingSpinner } from '../components/shared';

<LoadingSpinner size="lg" color="blue" />
```

### LoadingButton

A button component with integrated loading state.

**Props:**
- `loading` (boolean, default: false): Show loading state
- `disabled` (boolean, default: false): Disable button
- `variant` (string, default: 'primary'): Button style ('primary', 'secondary', 'success', 'danger', 'outline')
- `size` (string, default: 'md'): Button size ('sm', 'md', 'lg')
- `fullWidth` (boolean, default: false): Full width button
- `loadingText` (string, default: 'Loading...'): Text to show when loading
- `type` (string, default: 'button'): Button type
- `onClick` (function): Click handler

**Example:**
```jsx
import { LoadingButton } from '../components/shared';

<LoadingButton
  loading={isSubmitting}
  onClick={handleSubmit}
  variant="primary"
  size="md"
>
  Submit
</LoadingButton>
```

### LoadingOverlay

A full-screen or container overlay with loading indicator.

**Props:**
- `loading` (boolean, default: false): Show overlay
- `message` (string, default: 'Loading...'): Loading message
- `fullScreen` (boolean, default: false): Cover entire screen vs container

**Example:**
```jsx
import { LoadingOverlay } from '../components/shared';

<div className="relative">
  <LoadingOverlay loading={isLoading} message="Fetching data..." />
  {/* Your content */}
</div>
```

### SkeletonLoader

Skeleton loading placeholders for various content types.

**Components:**
- `SkeletonLoader.Text`: Text placeholder
- `SkeletonLoader.Card`: Card placeholder
- `SkeletonLoader.Table`: Table placeholder
- `SkeletonLoader.Avatar`: Avatar placeholder
- `SkeletonLoader.Button`: Button placeholder

**Example:**
```jsx
import SkeletonLoader from '../components/shared/SkeletonLoader';

{isLoading ? (
  <>
    <SkeletonLoader.Card />
    <SkeletonLoader.Table rows={5} columns={4} />
  </>
) : (
  <YourContent />
)}
```

## Import

All components can be imported from the shared directory:

```jsx
import { 
  DataTable, 
  Modal, 
  Toast, 
  useToast, 
  ToastProvider, 
  MapPreview,
  FormInput,
  FormSelect,
  FormTextarea,
  LoadingSpinner,
  LoadingButton,
  LoadingOverlay,
  SkeletonLoader
} from './components/shared';
```
