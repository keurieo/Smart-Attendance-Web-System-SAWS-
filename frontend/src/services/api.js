import axios from 'axios';
import { storage } from '../utils/storage';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Track if we're currently refreshing the token to avoid multiple refresh calls
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Request interceptor to add JWT token to all requests
api.interceptors.request.use(
  config => {
    const token = storage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      return Promise.reject({
        message: 'Network error. Please check your internet connection.',
        isNetworkError: true,
      });
    }

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = storage.getRefreshToken();

      if (!refreshToken) {
        // No refresh token available, redirect to login
        storage.clearAll();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Use base axios instance to avoid interceptor loop
        const response = await axios.post(`${API_URL}/accounts/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        storage.setAccessToken(access);

        // Update authorization header
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers.Authorization = `Bearer ${access}`;

        // Process queued requests
        processQueue(null, access);
        isRefreshing = false;

        // Retry original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        processQueue(refreshError, null);
        isRefreshing = false;
        
        storage.clearAll();
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      }
    }

    // Handle other error responses
    const errorResponse = {
      status: error.response?.status,
      message: error.response?.data?.message || 
               error.response?.data?.detail || 
               error.response?.data?.error ||
               'An error occurred. Please try again.',
      data: error.response?.data,
    };

    return Promise.reject(errorResponse);
  }
);

// Helper functions for common API calls

/**
 * Authentication endpoints
 */
export const authAPI = {
  login: (email, password) => api.post('/accounts/token/', { email, password }),
  refresh: (refreshToken) => api.post('/accounts/token/refresh/', { refresh: refreshToken }),
  getProfile: () => api.get('/accounts/users/me/'),
};

/**
 * User management endpoints
 */
export const userAPI = {
  getProfile: () => api.get('/accounts/users/me/'),
  updateProfile: (data) => api.patch('/accounts/users/me/', data),
};

/**
 * Attendance endpoints
 */
export const attendanceAPI = {
  // Teacher endpoints
  createSession: (data) => api.post('/teacher/sessions/', data),
  getSession: (sessionId) => api.get(`/teacher/sessions/${sessionId}/`),
  getSessions: (params) => api.get('/teacher/sessions/', { params }),
  
  // Student endpoints
  markAttendance: (data) => api.post('/student/attendance/scan/', data),
  getAttendanceHistory: (params) => api.get('/student/attendance/', { params }),
};

/**
 * Teacher endpoints
 */
export const teacherAPI = {
  getCourses: () => api.get('/teacher/courses/'),
  getSchedules: (params) => api.get('/teacher/schedules/', { params }),
};

/**
 * Admin endpoints
 */
export const adminAPI = {
  // User management
  getUsers: (params) => api.get('/admin/users/', { params }),
  createUser: (data) => api.post('/admin/users/', data),
  updateUser: (userId, data) => api.patch(`/admin/users/${userId}/`, data),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}/`),
  
  // Course management
  getCourses: (params) => api.get('/admin/courses/', { params }),
  createCourse: (data) => api.post('/admin/courses/', data),
  updateCourse: (courseId, data) => api.patch(`/admin/courses/${courseId}/`, data),
  
  // Enrollment management
  createEnrollment: (data) => api.post('/admin/enrollments/', data),
  deleteEnrollment: (enrollmentId) => api.delete(`/admin/enrollments/${enrollmentId}/`),
  
  // Attendance override
  overrideAttendance: (recordId, data) => api.patch(`/admin/attendance/${recordId}/`, data),
  
  // Audit logs
  getAuditLogs: (params) => api.get('/admin/audit/', { params }),
};

/**
 * Reporting endpoints
 */
export const reportAPI = {
  getAttendanceReport: (params) => api.get('/teacher/reports/', { params }),
  exportAttendanceCSV: (params) => api.get('/teacher/reports/', { 
    params,
    responseType: 'blob',
    headers: {
      'Accept': 'text/csv',
    },
  }),
};

export default api;
