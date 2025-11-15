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

## Import

All components can be imported from the shared directory:

```jsx
import { DataTable, Modal, Toast, useToast, ToastProvider, MapPreview } from './components/shared';
```
