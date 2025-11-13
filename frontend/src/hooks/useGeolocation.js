import { useState } from 'react';

// useGeolocation hook will be fully implemented in task 16.1
export const useGeolocation = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = () => {
    // Implementation will be added in task 16.1
    return Promise.resolve(null);
  };

  return { location, error, loading, getCurrentLocation };
};
