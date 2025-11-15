import { useState, useCallback } from 'react';

/**
 * Custom hook for accessing browser geolocation API with enhanced error handling
 * Returns location state (latitude, longitude, accuracy) and error state
 * Handles permission denial, errors, and provides fallback strategies
 */
export const useGeolocation = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [permissionStatus, setPermissionStatus] = useState('prompt'); // 'granted', 'denied', 'prompt'

  /**
   * Check geolocation permission status
   */
  const checkPermission = useCallback(async () => {
    if (!navigator.permissions) {
      return 'prompt';
    }

    try {
      const result = await navigator.permissions.query({ name: 'geolocation' });
      setPermissionStatus(result.state);
      return result.state;
    } catch (err) {
      console.warn('Permission API not supported:', err);
      return 'prompt';
    }
  }, []);

  /**
   * Request current location with high accuracy and retry logic
   * @param {Object} options - Configuration options
   * @param {number} options.timeout - Timeout in milliseconds (default: 15000)
   * @param {number} options.maximumAge - Maximum age of cached position (default: 0)
   * @param {boolean} options.enableHighAccuracy - Request high accuracy (default: true)
   * @param {number} options.retries - Number of retry attempts (default: 2)
   * @returns {Promise<Object>} Promise resolving to location object with latitude, longitude, accuracy
   */
  const getCurrentLocation = useCallback((options = {}) => {
    const {
      timeout = 15000,
      maximumAge = 0,
      enableHighAccuracy = true,
      retries = 2,
    } = options;

    return new Promise((resolve, reject) => {
      // Check if geolocation is supported
      if (!navigator.geolocation) {
        const errorMsg = 'Geolocation is not supported by your browser. Please use a modern browser like Chrome, Firefox, or Safari.';
        setError(errorMsg);
        setLoading(false);
        reject(new Error(errorMsg));
        return;
      }

      setLoading(true);
      setError(null);

      let attemptCount = 0;

      const attemptGetLocation = () => {
        attemptCount++;

        navigator.geolocation.getCurrentPosition(
          (position) => {
            const coords = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              accuracy: position.coords.accuracy,
              altitude: position.coords.altitude,
              altitudeAccuracy: position.coords.altitudeAccuracy,
              heading: position.coords.heading,
              speed: position.coords.speed,
              timestamp: position.timestamp,
            };

            // Validate coordinates
            if (coords.latitude === 0 && coords.longitude === 0) {
              const errorMsg = 'Invalid location received (0,0). Please check your device GPS settings.';
              setError(errorMsg);
              setLoading(false);
              reject(new Error(errorMsg));
              return;
            }

            // Check accuracy threshold
            if (coords.accuracy > 100) {
              console.warn(`Low accuracy: ${coords.accuracy}m. Consider retrying.`);
            }

            setLocation(coords);
            setLoading(false);
            setError(null);
            setPermissionStatus('granted');
            resolve(coords);
          },
          (error) => {
            let errorMsg = 'Failed to get location';
            let shouldRetry = false;

            switch (error.code) {
              case error.PERMISSION_DENIED:
                errorMsg = 'Location permission denied. Please enable location access in your browser settings and reload the page.';
                setPermissionStatus('denied');
                break;
              case error.POSITION_UNAVAILABLE:
                errorMsg = 'Location information is unavailable. Please ensure GPS is enabled on your device.';
                shouldRetry = attemptCount < retries;
                break;
              case error.TIMEOUT:
                errorMsg = `Location request timed out after ${timeout / 1000} seconds. Please try again.`;
                shouldRetry = attemptCount < retries;
                break;
              default:
                errorMsg = `An unknown error occurred: ${error.message}`;
                shouldRetry = attemptCount < retries;
            }

            // Retry if appropriate
            if (shouldRetry) {
              console.log(`Retrying location request (attempt ${attemptCount + 1}/${retries + 1})...`);
              setTimeout(attemptGetLocation, 1000); // Wait 1 second before retry
              return;
            }

            setError(errorMsg);
            setLoading(false);
            setLocation(null);
            reject(new Error(errorMsg));
          },
          {
            enableHighAccuracy,
            timeout,
            maximumAge,
          }
        );
      };

      attemptGetLocation();
    });
  }, []);

  /**
   * Watch position for continuous location updates
   * @param {Function} callback - Callback function to receive location updates
   * @param {Object} options - Configuration options
   * @returns {number} Watch ID that can be used to clear the watch
   */
  const watchPosition = useCallback((callback, options = {}) => {
    const {
      timeout = 15000,
      maximumAge = 5000,
      enableHighAccuracy = true,
    } = options;

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return null;
    }

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const coords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        };
        setLocation(coords);
        setError(null);
        callback(coords);
      },
      (error) => {
        let errorMsg = 'Failed to watch location';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = 'Location permission denied';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMsg = 'Location information is unavailable';
            break;
          case error.TIMEOUT:
            errorMsg = 'Location request timed out';
            break;
          default:
            errorMsg = error.message;
        }
        setError(errorMsg);
      },
      {
        enableHighAccuracy,
        timeout,
        maximumAge,
      }
    );

    return watchId;
  }, []);

  /**
   * Clear position watch
   * @param {number} watchId - Watch ID returned from watchPosition
   */
  const clearWatch = useCallback((watchId) => {
    if (watchId && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId);
    }
  }, []);

  return {
    location,
    error,
    loading,
    permissionStatus,
    getCurrentLocation,
    watchPosition,
    clearWatch,
    checkPermission,
  };
};
