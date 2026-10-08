import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getDashboardStats } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';
import StatCard from '../components/dashboard/StatCard';
import ThreatDistribution from '../components/dashboard/ThreatDistribution';
import RiskOverview from '../components/dashboard/RiskOverview';
import RecentDetections from '../components/dashboard/RecentDetections';
import SystemStatus from '../components/dashboard/SystemStatus';

import '../components/dashboard/dashboard.css';

const NetworkIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="6" height="6" rx="1"></rect>
    <rect x="16" y="2" width="6" height="6" rx="1"></rect>
    <rect x="9" y="16" width="6" height="6" rx="1"></rect>
    <path d="M5 8v4h14V8"></path>
    <path d="M12 12v4"></path>
  </svg>
);

const AlertTriangleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

const EyeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const LockIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
  </svg>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);

  useEffect(() => {
    // Verify token validity via /auth/me
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  useEffect(() => {
    // Fetch dashboard stats
    getDashboardStats()
      .then((res) => {
        setStats(res.data);
        setStatsLoading(false);
      })
      .catch(() => {
        setStatsError(true);
        setStatsLoading(false);
      });
  }, []);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  const formatStat = (value) => {
    if (statsLoading) return '…';
    if (statsError) return '—';
    return value.toLocaleString();
  };

  return (
    <div className="soc-dashboard-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />

      <div className="soc-main-layout">
        <Topbar onToggleSidebar={toggleSidebar} user={user} />

        <main className="soc-content">
          {/* Statistics Grid */}
          <section className="stat-cards-grid">
            <StatCard
              title="TOTAL TRAFFIC"
              value={formatStat(stats?.total_traffic ?? 0)}
              icon={NetworkIcon}
              iconColor="#00e5ff"
              badgeText={statsLoading ? 'Loading...' : statsError ? 'Unable to load' : 'Total analyzed flows'}
            />
            <StatCard
              title="THREATS DETECTED"
              value={formatStat(stats?.threats_detected ?? 0)}
              icon={AlertTriangleIcon}
              iconColor="#ffb300"
              badgeText={statsLoading ? 'Loading...' : statsError ? 'Unable to load' : 'Non-BENIGN predictions'}
            />
            <StatCard
              title="ANOMALIES"
              value={formatStat(stats?.anomalies ?? 0)}
              icon={EyeIcon}
              iconColor="#00e676"
              badgeText={statsLoading ? 'Loading...' : statsError ? 'Unable to load' : 'Isolation Forest detections'}
            />
            <StatCard
              title="CRITICAL THREATS"
              value={formatStat(stats?.critical_threats ?? 0)}
              icon={LockIcon}
              iconColor="#ff1744"
              badgeText={statsLoading ? 'Loading...' : statsError ? 'Unable to load' : 'Risk level CRITICAL'}
            />
          </section>

          {/* Threat Distribution & Risk Overview */}
          <section className="middle-grid">
            <ThreatDistribution />
            <RiskOverview />
          </section>

          {/* Recent Detections & System Status */}
          <section className="middle-grid">
            <RecentDetections />
            <SystemStatus />
          </section>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
