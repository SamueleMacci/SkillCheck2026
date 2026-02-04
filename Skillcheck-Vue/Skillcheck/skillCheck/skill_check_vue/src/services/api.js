// src/services/api.js
import axios from 'axios';

// Base URL letta da ambiente, fallback a /api/ (Django API Bridge)
const baseURL = process.env.VUE_APP_API_BASE || '/api/';

const api = axios.create({
  baseURL,
  withCredentials: true,          // stesso dominio → manda i cookie (csrftoken, sessione)
  xsrfCookieName: 'csrftoken',    // naming Django
  xsrfHeaderName: 'X-CSRFToken',
  headers: { 'Content-Type': 'application/json' },
});

// — opzionale: Authorization se usi un token lato SPA —
const bootToken = localStorage.getItem('auth_token');
if (bootToken) {
  api.defaults.headers.common.Authorization = `Token ${bootToken}`;
}

// Interceptor request: aggiunge il token se presente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

// Interceptor response: se 401, pulisci token e manda al login
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common.Authorization;
      if (!window.location.pathname.includes('/login')) {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?next=${next}`;
      }
    }
    return Promise.reject(err);
  }
);

export default api;
