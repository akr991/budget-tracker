import axios from 'axios';

const inferredApiUrl =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000/api`
    : 'http://localhost:8000/api';

const baseURL = import.meta.env.VITE_API_URL || inferredApiUrl;

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem('token');
  }
}

const existingToken = localStorage.getItem('token');
if (existingToken) {
  setAuthToken(existingToken);
}
