import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/auth/ProtectedRoute';
import './index.css';

import TrafficAnalysis from './pages/TrafficAnalysis';
import ThreatDetection from './pages/ThreatDetection';
import AnomalyMonitoring from './pages/AnomalyMonitoring';
import RealtimeMonitor from './pages/RealtimeMonitor';
import DetectionDetails from './pages/DetectionDetails';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/traffic-analysis"
          element={
            <ProtectedRoute>
              <TrafficAnalysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/threat-detection"
          element={
            <ProtectedRoute>
              <ThreatDetection />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anomaly-monitoring"
          element={
            <ProtectedRoute>
              <AnomalyMonitoring />
            </ProtectedRoute>
          }
        />
        <Route
          path="/realtime-monitor"
          element={
            <ProtectedRoute>
              <RealtimeMonitor />
            </ProtectedRoute>
          }
        />

        <Route
          path="/detection-details"
          element={
            <ProtectedRoute>
              <DetectionDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/detection-details/:id"
          element={
            <ProtectedRoute>
              <DetectionDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
