import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected routes - Teacher */}
            <Route
              path="/teacher/dashboard"
              element={
                <ProtectedRoute allowedRoles="teacher">
                  <TeacherDashboard />
                </ProtectedRoute>
              }
            />
            
            {/* Protected routes - Student */}
            <Route
              path="/student/dashboard"
              element={
                <ProtectedRoute allowedRoles="student">
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            
            {/* Protected routes - Admin */}
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute allowedRoles="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* 404 - Not Found */}
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <h1 className="text-6xl font-bold text-gray-900">404</h1>
                    <p className="mt-4 text-xl text-gray-600">Page not found</p>
                    <a
                      href="/login"
                      className="mt-6 inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Go to Login
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
