import { useState } from 'react';

/**
 * Custom hook for accessing browser geolocation API
 * Returns location state (latitude, longitude, accuracy) and error state
 * Handles permission denial and errors
 */
export const useGeolocation = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  /**
   * Request current location with high accuracy
   * @returns {Promise<Object>} Promise resolving to location object with latitude, longitude, accuracy
   */
  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      // Check if geolocation is supported
      if (!navigator.geolocation) {
        const errorMsg = 'Geolocation is not supported by your browser';
        setError(errorMsg);
        setLoading(false);
        reject(new Error(errorMsg));
        return;
      }

      setLoading(true);
      setError(null);

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          };
          setLocation(coords);
          setLoading(false);
          setError(null);
          resolve(coords);
        },
        (error) => {
          let errorMsg = 'Failed to get location';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMsg = 'Location permission denied. Please enable location access in your browser settings.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMsg = 'Location information is unavailable. Please check your device settings.';
              break;
            case error.TIMEOUT:
              errorMsg = 'Location request timed out. Please try again.';
              break;
            default:
              errorMsg = `An unknown error occurred: ${error.message}`;
          }
          
          setError(errorMsg);
          setLoading(false);
          setLocation(null);
          reject(new Error(errorMsg));
        },
        {
          enableHighAccuracy: true,  // Request high accuracy location
          timeout: 10000,             // 10 second timeout
          maximumAge: 0,              // Don't use cached location
        }
      );
    });
  };

  return { location, error, loading, getCurrentLocation };
};
