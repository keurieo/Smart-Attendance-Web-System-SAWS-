# Frontend Authentication Implementation

## Overview
This document describes the implementation of the React frontend authentication system for the Smart Attendance System.

## Implemented Components

### 1. Authentication Context (`src/context/AuthContext.jsx`)
- **AuthProvider**: React context provider that manages authentication state
- **Features**:
  - User state management
  - JWT token storage in localStorage
  - Login function with API integration
  - Logout function with state cleanup
  - Token refresh functionality
  - Automatic token validation on mount
  - User profile updates

### 2. useAuth Hook (`src/hooks/useAuth.js`)
- Custom React hook for accessing authentication context
- Provides easy access to:
  - `user`: Current user object
  - `loading`: Loading state during initialization
  - `isAuthenticated`: Boolean authentication status
  - `login(email, password)`: Login function
  - `logout()`: Logout function
  - `refreshToken()`: Manual token refresh
  - `updateUser(userData)`: Update user data

### 3. LoginForm Component (`src/components/auth/LoginForm.jsx`)
- Full-featured login form with:
  - Email and password inputs
  - Client-side validation
  - Error display (field-level and API errors)
  - Loading state during submission
  - Role-based redirect after successful login
  - Responsive design with Tailwind CSS

### 4. ProtectedRoute Component (`src/components/auth/ProtectedRoute.jsx`)
- Route wrapper for authenticated pages
- **Features**:
  - Authentication check with redirect to login
  - Role-based access control
  - Loading state display
  - Automatic redirect to appropriate dashboard if user lacks permission
  - Preserves intended destination in location state

### 5. API Client (`src/services/api.js`)
- Axios instance with authentication interceptors
- **Features**:
  - Automatic JWT token injection in request headers
  - Token refresh on 401 errors
  - Request queuing during token refresh
  - Network error handling
  - Timeout configuration (30 seconds)
  - Helper functions for common API endpoints:
    - `authAPI`: Authentication endpoints
    - `userAPI`: User management
    - `attendanceAPI`: Attendance operations
    - `adminAPI`: Admin operations
    - `reportAPI`: Reporting endpoints

## Application Structure

### Updated App.jsx
- Wrapped with `AuthProvider` for global auth state
- Configured routing with:
  - Public route: `/login`
  - Protected teacher route: `/teacher/dashboard`
  - Protected student route: `/student/dashboard`
  - Protected admin route: `/admin/dashboard`
  - Default redirect to login
  - 404 page

### Dashboard Pages
Updated all dashboard pages with:
- User welcome message
- Logout button
- Consistent header layout
- Auth context integration

## Authentication Flow

### Login Flow
1. User enters credentials in LoginForm
2. Form validates input client-side
3. Calls `login()` from useAuth hook
4. AuthContext makes API call to `/api/accounts/token/`
5. On success:
   - Stores access and refresh tokens in localStorage
   - Stores user data in localStorage
   - Updates context state
   - Redirects to role-appropriate dashboard
6. On failure:
   - Displays error message to user

### Token Refresh Flow
1. API request receives 401 response
2. Response interceptor catches error
3. Checks if refresh is already in progress
4. If not, attempts token refresh with refresh token
5. On success:
   - Updates access token in localStorage
   - Retries original request with new token
   - Processes any queued requests
6. On failure:
   - Clears all tokens
   - Redirects to login page

### Protected Route Flow
1. User navigates to protected route
2. ProtectedRoute checks authentication status
3. If not authenticated:
   - Redirects to login with return URL
4. If authenticated but wrong role:
   - Redirects to user's appropriate dashboard
5. If authenticated with correct role:
   - Renders protected content

## Storage Utilities

### localStorage Keys
- `access_token`: JWT access token (15 min expiration)
- `refresh_token`: JWT refresh token (7 day expiration)
- `user`: Serialized user object with profile data

### Storage Helper Functions (`src/utils/storage.js`)
- `getAccessToken()`, `setAccessToken(token)`, `removeAccessToken()`
- `getRefreshToken()`, `setRefreshToken(token)`, `removeRefreshToken()`
- `getUser()`, `setUser(user)`, `removeUser()`
- `clearAll()`: Clears all auth data

## Security Features

1. **JWT Token Management**
   - Short-lived access tokens (15 minutes)
   - Long-lived refresh tokens (7 days)
   - Automatic token refresh before expiration

2. **Request Queuing**
   - Prevents multiple simultaneous refresh attempts
   - Queues requests during token refresh
   - Processes all queued requests after successful refresh

3. **Role-Based Access Control**
   - Route-level role checking
   - Automatic redirect for unauthorized access
   - Prevents privilege escalation

4. **Secure Storage**
   - Tokens stored in localStorage (consider httpOnly cookies for production)
   - Automatic cleanup on logout
   - Token validation on app initialization

## API Endpoints Used

- `POST /api/accounts/token/` - Login
- `POST /api/accounts/token/refresh/` - Refresh access token
- `GET /api/accounts/users/me/` - Get current user profile

## Requirements Satisfied

✅ **Requirement 1.1**: User authentication with JWT tokens
✅ **Requirement 1.2**: Role-based access control (Admin, Teacher, Student)
✅ **Requirement 1.4**: Automatic token refresh on expiration

## Next Steps

The authentication system is now complete and ready for integration with:
- Task 16: Teacher session creation interface
- Task 17: Student QR scanning interface
- Task 18: Admin management interface

All subsequent tasks can use the `useAuth` hook to access user data and authentication state.
