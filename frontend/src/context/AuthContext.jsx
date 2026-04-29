import React, { createContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { storage } from '../utils/storage';

export const AuthContext = createContext(null);
const SESSION_EXPIRED_KEY = 'session_expired';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load user from storage on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedUser = storage.getUser();
      const accessToken = storage.getAccessToken();
      
      if (storedUser && accessToken) {
        setUser(storedUser);
        setIsAuthenticated(true);
        
        // Optionally verify token is still valid by fetching user profile
        try {
          const response = await api.get('/accounts/users/me/');
          setUser(response.data);
          storage.setUser(response.data);
          } catch (error) {
            // Token invalid, clear auth state with message
            logoutWithMessage('Your session has expired. Please log in again.');
          }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = useCallback(async (email, password) => {
    try {
      // Call login API endpoint
      const response = await api.post('/accounts/token/', {
        email,
        password,
      });

      const { access, refresh, user: userData } = response.data;

      // Store tokens and user data
      storage.setAccessToken(access);
      storage.setRefreshToken(refresh);
      storage.setUser(userData);

      // Update state
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true, user: userData };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Login failed. Please check your credentials.';
      return { success: false, error: errorMessage };
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    // Clear tokens and user data
    storage.clearAll();
    
    // Update state
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const logoutWithMessage = useCallback((message) => {
    if (message) {
      sessionStorage.setItem(SESSION_EXPIRED_KEY, message);
    }
    logout();
  }, [logout]);

  // Refresh token function
  const refreshToken = useCallback(async () => {
    try {
      const refresh = storage.getRefreshToken();
      
      if (!refresh) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/accounts/token/refresh/', {
        refresh,
      });

      const { access } = response.data;
      storage.setAccessToken(access);

      return { success: true, access };
    } catch (error) {
      // Refresh failed, logout user
      logout();
      return { success: false, error: 'Session expired. Please login again.' };
    }
  }, [logout]);

  // Update user data
  const updateUser = useCallback((userData) => {
    setUser(userData);
    storage.setUser(userData);
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    logoutWithMessage,
    refreshToken,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
