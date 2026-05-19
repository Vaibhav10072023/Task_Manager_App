import axios from 'axios';

let base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
if (!base.endsWith('/')) {
  base += '/';
}

const api = axios.create({
  baseURL: base,
});

api.interceptors.request.use((config) => {
  if (config.url && config.url.startsWith('/')) {
    config.url = config.url.substring(1);
  }
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
