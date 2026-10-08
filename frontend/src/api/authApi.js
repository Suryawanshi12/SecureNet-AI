import axiosInstance from './axiosInstance';

export const registerUser = (data) =>
  axiosInstance.post('/auth/register', data);

export const loginUser = (data) =>
  axiosInstance.post('/auth/login', data);

export const getMe = () =>
  axiosInstance.get('/auth/me');

export const getHealth = () =>
  axiosInstance.get('/health');

export const getModelInfo = () =>
  axiosInstance.get('/model-info');

// Dashboard statistics APIs
export const getDashboardStats = () =>
  axiosInstance.get('/dashboard/stats');

export const getThreatDistribution = () =>
  axiosInstance.get('/dashboard/threat-distribution');

export const getRiskDistribution = () =>
  axiosInstance.get('/dashboard/risk-distribution');

export const getRecentDetections = () =>
  axiosInstance.get('/dashboard/recent-detections');

export const getDetectionById = (id) =>
  axiosInstance.get(`/dashboard/detections/${id}`);

// ML Prediction API
export const predictTraffic = (features) =>
  axiosInstance.post('/predict', { features });

// Real-Time Control APIs
export const getRealtimeStatus = () =>
  axiosInstance.get('/realtime/status');

export const startRealtimePipeline = () =>
  axiosInstance.post('/realtime/start');

export const stopRealtimePipeline = () =>
  axiosInstance.post('/realtime/stop');



