// Local storage utilities

export const storage = {
  getAccessToken: () => localStorage.getItem('access_token'),
  setAccessToken: token => localStorage.setItem('access_token', token),
  removeAccessToken: () => localStorage.removeItem('access_token'),

  getRefreshToken: () => localStorage.getItem('refresh_token'),
  setRefreshToken: token => localStorage.setItem('refresh_token', token),
  removeRefreshToken: () => localStorage.removeItem('refresh_token'),

  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  setUser: user => localStorage.setItem('user', JSON.stringify(user)),
  removeUser: () => localStorage.removeItem('user'),

  clearAll: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
};
