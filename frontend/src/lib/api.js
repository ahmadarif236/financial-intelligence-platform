import axios from 'axios';

// If deploying backend to HuggingFace, VITE_API_URL should look like "https://[username]-[space-name].hf.space"
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = BASE.endsWith('/api') ? BASE : `${BASE}/api`;
const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
