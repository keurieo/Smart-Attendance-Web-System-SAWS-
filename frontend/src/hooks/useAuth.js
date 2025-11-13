import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

// useAuth hook will be fully implemented in task 15.1
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
