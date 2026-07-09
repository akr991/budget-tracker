import axios from 'axios';

// For native Capacitor builds, configure your backend URL here
// For web builds, it will use the same server as the frontend
const getApiUrl = () => {
  // Check if running in Capacitor (native app)
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    // Development in browser
    return `${window.location.protocol}//${window.location.hostname}:8000/api`;
  }
  
  // Capacitor app or production web build
  const viteUrl = import.meta.env.VITE_API_URL;
  if (viteUrl) return viteUrl;
  
  // Default fallback
  return typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000/api`
    : 'http://localhost:8000/api';
};

const baseURL = getApiUrl();

console.log('[API Client] Base URL:', baseURL);

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('[API Error]', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    localStorage.setItem('token', token);
    console.log('[Auth] Token set');
  } else {
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem('token');
    console.log('[Auth] Token cleared');
  }
}

const existingToken = localStorage.getItem('token');
if (existingToken) {
  console.log('[Auth] Restoring existing token');
  setAuthToken(existingToken);
}
