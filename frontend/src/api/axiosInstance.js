import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const TOKEN_KEY = 'securenet_access_token';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT to every request automatically
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// On 401, clear storage and redirect to login
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('securenet_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
export { TOKEN_KEY };

export const getWebSocketUrl = (path = '/ws/realtime-stream') => {
  const envWsUrl = import.meta.env.VITE_WS_URL;
  if (envWsUrl) {
    const cleanWs = envWsUrl.replace(/\/$/, '');
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${cleanWs}${cleanPath}`;
  }
  const httpUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  const wsProtocol = httpUrl.startsWith('https') ? 'wss:' : 'ws:';
  const host = httpUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${wsProtocol}//${host}${cleanPath}`;
};

