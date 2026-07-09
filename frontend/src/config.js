// API Configuration for Budget Tracker App
// Change the API_BASE_URL to your deployed backend URL

const isDevelopment = !window.location.hostname.includes('localhost') && process.env.NODE_ENV === 'development';

// For Capacitor builds (native app), use your actual server URL
// For web development, use localhost
export const API_BASE_URL = isDevelopment
  ? 'http://localhost:8000' // Development
  : process.env.REACT_APP_API_URL || 'https://your-production-server.railway.app'; // Production

// For Capacitor apps connecting to remote server
export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;
