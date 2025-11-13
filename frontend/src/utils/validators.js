// Form validation utilities

export const validators = {
  email: email => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  password: password => {
    // Minimum 8 characters
    return password && password.length >= 8;
  },

  required: value => {
    return value !== null && value !== undefined && value !== '';
  },

  coordinates: (lat, lon) => {
    return (
      lat !== null &&
      lon !== null &&
      lat >= -90 &&
      lat <= 90 &&
      lon >= -180 &&
      lon <= 180 &&
      !(lat === 0 && lon === 0)
    );
  },
};
