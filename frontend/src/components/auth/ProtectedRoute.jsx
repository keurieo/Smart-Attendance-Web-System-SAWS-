import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * ProtectedRoute component that wraps routes requiring authentication
 * Optionally checks for specific user roles
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @param {string|string[]} props.allowedRoles - Optional role(s) that can access this route
 * @param {string} props.redirectTo - Optional redirect path (defaults to /login)
 */
const ProtectedRoute = ({ 
  children, 
  allowedRoles = null, 
  redirectTo = '/login' 
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <svg 
            className="animate-spin h-12 w-12 text-blue-600 mx-auto" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check role-based access if allowedRoles is specified
  if (allowedRoles) {
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    const userRole = user?.role;

    if (!userRole || !roles.includes(userRole)) {
      // User doesn't have required role, redirect to unauthorized page or their dashboard
      const dashboardMap = {
        admin: '/admin/dashboard',
        teacher: '/teacher/dashboard',
        student: '/student/dashboard',
      };

      const userDashboard = dashboardMap[userRole] || '/';
      
      return (
        <Navigate 
          to={userDashboard} 
          state={{ 
            error: 'You do not have permission to access this page.',
            from: location 
          }} 
          replace 
        />
      );
    }
  }

  // User is authenticated and has required role (if specified)
  return children;
};

export default ProtectedRoute;
