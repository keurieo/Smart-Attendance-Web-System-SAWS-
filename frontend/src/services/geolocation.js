/**
 * Geolocation Service
 * Provides robust location services with fallback strategies
 * Uses browser Geolocation API (free, no API key needed)
 */

/**
 * Get current position with enhanced error handling and retry logic
 * @param {Object} options - Configuration options
 * @returns {Promise<Object>} Location object with coordinates
 */
export const getCurrentPosition = async (options = {}) => {
  const {
    enableHighAccuracy = true,
    timeout = 15000,
    maximumAge = 0,
    retries = 2,
  } = options;

  if (!navigator.geolocation) {
    throw new Error('Geolocation is not supported by your browser');
  }

  let lastError = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const position = await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error('Location request timed out'));
        }, timeout);

        navigator.geolocation.getCurrentPosition(
          (pos) => {
            clearTimeout(timeoutId);
            resolve(pos);
          },
          (err) => {
            clearTimeout(timeoutId);
            reject(err);
          },
          {
            enableHighAccuracy,
            timeout,
            maximumAge,
          }
        );
      });

      // Validate the position
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

      // Check for invalid coordinates
      if (coords.latitude === 0 && coords.longitude === 0) {
        throw new Error('Invalid location (0,0) received');
      }

      // Check latitude/longitude ranges
      if (coords.latitude < -90 || coords.latitude > 90) {
        throw new Error(`Invalid latitude: ${coords.latitude}`);
      }

      if (coords.longitude < -180 || coords.longitude > 180) {
        throw new Error(`Invalid longitude: ${coords.longitude}`);
      }

      return coords;
    } catch (error) {
      lastError = error;

      // Don't retry on permission denied
      if (error.code === 1) {
        throw new Error('Location permission denied. Please enable location access in your browser settings.');
      }

      // Wait before retry (except on last attempt)
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }

  // All retries failed
  throw lastError || new Error('Failed to get location after multiple attempts');
};

/**
 * Calculate distance between two points using Haversine formula
 * @param {number} lat1 - Latitude of first point
 * @param {number} lon1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lon2 - Longitude of second point
 * @returns {number} Distance in meters
 */
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371000; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // Distance in meters
};

/**
 * Check if a location is within a specified radius of a target location
 * @param {Object} userLocation - User's location {latitude, longitude}
 * @param {Object} targetLocation - Target location {latitude, longitude}
 * @param {number} radius - Allowed radius in meters
 * @returns {Object} Validation result {isWithinRadius, distance}
 */
export const isWithinRadius = (userLocation, targetLocation, radius) => {
  const distance = calculateDistance(
    userLocation.latitude,
    userLocation.longitude,
    targetLocation.latitude,
    targetLocation.longitude
  );

  return {
    isWithinRadius: distance <= radius,
    distance: Math.round(distance * 10) / 10, // Round to 1 decimal place
  };
};

/**
 * Format distance for display
 * @param {number} meters - Distance in meters
 * @returns {string} Formatted distance string
 */
export const formatDistance = (meters) => {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(2)}km`;
};

/**
 * Get user-friendly error message for geolocation errors
 * @param {Error} error - Geolocation error
 * @returns {string} User-friendly error message
 */
export const getGeolocationErrorMessage = (error) => {
  if (!error) return 'Unknown error occurred';

  if (error.code) {
    switch (error.code) {
      case 1: // PERMISSION_DENIED
        return 'Location permission denied. Please enable location access in your browser settings and reload the page.';
      case 2: // POSITION_UNAVAILABLE
        return 'Location information is unavailable. Please ensure GPS is enabled on your device and you have a clear view of the sky.';
      case 3: // TIMEOUT
        return 'Location request timed out. Please try again or check your internet connection.';
      default:
        return `Location error: ${error.message || 'Unknown error'}`;
    }
  }

  return error.message || 'Failed to get location';
};

/**
 * Check if geolocation is supported
 * @returns {boolean} True if geolocation is supported
 */
export const isGeolocationSupported = () => {
  return 'geolocation' in navigator;
};

/**
 * Check geolocation permission status
 * @returns {Promise<string>} Permission status: 'granted', 'denied', or 'prompt'
 */
export const checkPermissionStatus = async () => {
  if (!navigator.permissions) {
    return 'prompt';
  }

  try {
    const result = await navigator.permissions.query({ name: 'geolocation' });
    return result.state;
  } catch (error) {
    console.warn('Permission API not supported:', error);
    return 'prompt';
  }
};

/**
 * Request location permission (triggers browser permission prompt)
 * @returns {Promise<boolean>} True if permission granted
 */
export const requestLocationPermission = async () => {
  try {
    await getCurrentPosition({ timeout: 5000, maximumAge: 60000 });
    return true;
  } catch (error) {
    if (error.code === 1) {
      return false; // Permission denied
    }
    // Other errors don't necessarily mean permission denied
    return true;
  }
};

/**
 * Watch position for continuous updates
 * @param {Function} callback - Callback function to receive position updates
 * @param {Function} errorCallback - Callback function for errors
 * @param {Object} options - Configuration options
 * @returns {number} Watch ID that can be used to clear the watch
 */
export const watchPosition = (callback, errorCallback, options = {}) => {
  const {
    enableHighAccuracy = true,
    timeout = 15000,
    maximumAge = 5000,
  } = options;

  if (!isGeolocationSupported()) {
    errorCallback(new Error('Geolocation is not supported'));
    return null;
  }

  return navigator.geolocation.watchPosition(
    (position) => {
      callback({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: position.timestamp,
      });
    },
    (error) => {
      errorCallback(error);
    },
    {
      enableHighAccuracy,
      timeout,
      maximumAge,
    }
  );
};

/**
 * Clear position watch
 * @param {number} watchId - Watch ID returned from watchPosition
 */
export const clearWatch = (watchId) => {
  if (watchId && navigator.geolocation) {
    navigator.geolocation.clearWatch(watchId);
  }
};

export default {
  getCurrentPosition,
  calculateDistance,
  isWithinRadius,
  formatDistance,
  getGeolocationErrorMessage,
  isGeolocationSupported,
  checkPermissionStatus,
  requestLocationPermission,
  watchPosition,
  clearWatch,
};
