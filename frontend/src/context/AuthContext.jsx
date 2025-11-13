import React, { createContext, useState, useEffect } from 'react';

// AuthContext will be fully implemented in task 15.1
export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored tokens on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      // TODO: Validate token and fetch user data
    }
    setLoading(false);
  }, []);

  const value = {
    user,
    setUser,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
