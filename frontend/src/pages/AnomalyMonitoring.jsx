import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getDashboardStats, getRecentDetections, getModelInfo } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';
import StatCard from '../components/dashboard/StatCard';

import '../components/dashboard/dashboard.css';

const RISK_LEVELS = ['All Risk Levels', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const STATUS_OPTIONS = ['All Statuses', 'ANOMALOUS', 'NORMAL'];

const AnomalyMonitoring = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Stats & Backend metadata state
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [modelInfo, setModelInfo] = useState(null);
  const [isDetectorReady, setIsDetectorReady] = useState(false);

  // Detections state
  const [detections, setDetections] = useState([]);
  const [detectionsLoading, setDetectionsLoading] = useState(true);

  // Filters state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('All Risk Levels');
  const [selectedStatus, setSelectedStatus] = useState('All Statuses');

  useEffect(() => {
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  useEffect(() => {
    // Fetch stats, model info, and recent detections
    Promise.all([
      getDashboardStats().catch(() => null),
      getModelInfo().catch(() => null),
      getRecentDetections().catch(() => null),
    ]).then(([statsRes, modelRes, detectRes]) => {
      if (statsRes) setStats(statsRes.data);
      if (modelRes) {
        setModelInfo(modelRes.data);
        setIsDetectorReady(true);
      }
      if (detectRes) setDetections(detectRes.data || []);

      setStatsLoading(false);
      setDetectionsLoading(false);
    });
  }, []);

  const totalFlows = stats?.total_traffic ?? 0;
  const anomalousFlows = stats?.anomalies ?? 0;
  const normalFlows = Math.max(0, totalFlows - anomalousFlows);
  const anomalyRate = totalFlows > 0 ? ((anomalousFlows / totalFlows) * 100).toFixed(1) + '%' : '0.0%';

  // Determine anomaly status for each row
  const getRowAnomalyStatus = (item) => {
    if (item.anomaly_score !== undefined && item.anomaly_score !== null) {
      return item.anomaly_score > 0 ? 'ANOMALOUS' : 'NORMAL';
    }
    // Fallback based on risk / prediction if anomaly score field isn't returned
    return (item.risk_level === 'HIGH' || item.risk_level === 'CRITICAL' || item.prediction !== 'BENIGN') ? 'ANOMALOUS' : 'NORMAL';
  };

  const getRowAnomalyScore = (item) => {
    if (item.anomaly_score !== undefined && item.anomaly_score !== null) {
      return item.anomaly_score.toFixed(4);
    }
    return '—';
  };

  // Filtered detections list
  const filteredDetections = detections.filter((item) => {
    const status = getRowAnomalyStatus(item);
    if (selectedStatus !== 'All Statuses' && status !== selectedStatus) {
      return false;
    }
    if (selectedRisk !== 'All Risk Levels' && item.risk_level !== selectedRisk) {
      return false;
    }
    if (searchTerm.trim() !== '') {
      const term = searchTerm.toLowerCase();
      const pred = (item.prediction || '').toLowerCase();
      const risk = (item.risk_level || '').toLowerCase();
      if (!pred.includes(term) && !risk.includes(term)) {
        return false;
      }
    }
    return true;
  });

  const formatTime = (isoString) => {
    if (!isoString) return '—';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return isoString;
    }
  };

  const getRiskBadgeClass = (level) => {
    switch (level) {
      case 'CRITICAL': return 'risk-badge-critical';
      case 'HIGH': return 'risk-badge-high';
      case 'MEDIUM': return 'risk-badge-medium';
      case 'LOW': return 'risk-badge-low';
      default: return 'risk-badge-info';
    }
  };

  return (
    <div className="soc-dashboard-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />

      <div className="soc-main-layout">
        <Topbar onToggleSidebar={() => setSidebarOpen((p) => !p)} user={user} />

        <main className="soc-content">
          {/* Page Header */}
          <header className="page-header" style={{ marginBottom: '24px' }}>
            <h1 className="page-title" style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff', margin: 0 }}>
              Anomaly Monitoring
            </h1>
            <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
              Identify network traffic that deviates from learned benign behavior.
            </p>
          </header>

          {/* Top Stat Cards */}
          <section className="stat-cards-grid" style={{ marginBottom: '24px' }}>
            <StatCard
              title="TOTAL FLOWS"
              value={statsLoading ? '…' : totalFlows.toLocaleString()}
              badgeText="All analyzed traffic flows"
              iconColor="#00e5ff"
            />
            <StatCard
              title="NORMAL TRAFFIC"
              value={statsLoading ? '…' : normalFlows.toLocaleString()}
              badgeText="Standard behavior flows"
              iconColor="#00e676"
            />
            <StatCard
              title="ANOMALOUS TRAFFIC"
              value={statsLoading ? '…' : anomalousFlows.toLocaleString()}
              badgeText="Flagged by Isolation Forest"
              iconColor="#ffb300"
            />
            <StatCard
              title="ANOMALY RATE"
              value={statsLoading ? '…' : anomalyRate}
              badgeText="Percentage of anomalous flows"
              iconColor="#ff1744"
            />
          </section>

          {/* Anomaly Overview & System Info Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
            
            {/* Anomaly Overview Card */}
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
              <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                Anomaly Overview
              </h2>

              {/* Progress Bar Split */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px', color: '#cbd5e1' }}>
                  <span>Normal: {normalFlows.toLocaleString()}</span>
                  <span>Anomalous: {anomalousFlows.toLocaleString()}</span>
                </div>
                <div style={{ height: '10px', background: '#1e293b', borderRadius: '5px', overflow: 'hidden', display: 'flex' }}>
                  <div
                    style={{
                      width: `${totalFlows > 0 ? (normalFlows / totalFlows) * 100 : 100}%`,
                      background: '#00e676',
                      transition: 'width 0.3s ease',
                    }}
                  />
                  <div
                    style={{
                      width: `${totalFlows > 0 ? (anomalousFlows / totalFlows) * 100 : 0}%`,
                      background: '#ffb300',
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
              </div>

              <p style={{ color: '#94a3b8', fontSize: '0.85rem', lineHeight: '1.5', margin: 0, background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                Anomaly detection identifies traffic that deviates from learned benign behavior and provides an additional signal for potentially novel or previously unseen threats.
              </p>
            </div>

            {/* System Info & Anomaly Score Config Card */}
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
              <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                  <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                  <line x1="6" y1="6" x2="6.01" y2="6"></line>
                  <line x1="6" y1="18" x2="6.01" y2="18"></line>
                </svg>
                Detector System Configuration
              </h2>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Anomaly Detector</span>
                  <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>
                    {modelInfo?.anomaly_model || 'Isolation Forest V3'}
                  </strong>
                </div>

                <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Detection Threshold</span>
                  <strong style={{ fontSize: '0.95rem', color: '#00e5ff' }}>
                    Score &gt; 0.0
                  </strong>
                </div>

                <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Engine Status</span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '700', color: isDetectorReady ? '#00e676' : '#ffb300' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: isDetectorReady ? '#00e676' : '#ffb300' }} />
                    {isDetectorReady ? 'Ready' : 'Connecting...'}
                  </span>
                </div>

                <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Supervised Classify</span>
                  <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>
                    {modelInfo?.supervised_model || 'XGBoost Model 5'}
                  </strong>
                </div>
              </div>
            </div>

          </div>

          {/* Recent Anomalies Section */}
          <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ color: '#f8fafc', fontSize: '1.05rem', fontWeight: '600', margin: 0 }}>
                Recent Traffic Detections & Anomalies
              </h3>

              {/* Filters */}
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', flex: '1', justifyContent: 'flex-end' }}>
                <input
                  type="text"
                  placeholder="Search prediction / risk..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    outline: 'none',
                    minWidth: '180px',
                  }}
                />

                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  style={{
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                >
                  {STATUS_OPTIONS.map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>

                <select
                  value={selectedRisk}
                  onChange={(e) => setSelectedRisk(e.target.value)}
                  style={{
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    outline: 'none',
                  }}
                >
                  {RISK_LEVELS.map((lvl) => (
                    <option key={lvl} value={lvl}>{lvl}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Table or Empty State */}
            {detectionsLoading ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                Loading anomaly detection logs...
              </div>
            ) : filteredDetections.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '48px 20px', color: '#64748b' }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: '12px', color: '#334155' }}>
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <p style={{ margin: 0, fontSize: '1rem', color: '#cbd5e1', fontWeight: '600' }}>
                  No anomalous traffic detected yet.
                </p>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '6px' }}>
                  Network flows analyzed by Isolation Forest will appear here.
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="soc-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <th style={{ padding: '12px 16px' }}>Time</th>
                      <th style={{ padding: '12px 16px' }}>Prediction</th>
                      <th style={{ padding: '12px 16px' }}>Anomaly Score</th>
                      <th style={{ padding: '12px 16px' }}>Risk Score</th>
                      <th style={{ padding: '12px 16px' }}>Risk Level</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDetections.map((row) => {
                      const status = getRowAnomalyStatus(row);
                      const isAnomalous = status === 'ANOMALOUS';
                      return (
                        <tr key={row.id} style={{ borderBottom: '1px solid #1e293b', color: '#e2e8f0', fontSize: '0.875rem' }}>
                          <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{formatTime(row.timestamp)}</td>
                          <td style={{ padding: '12px 16px', fontWeight: '600', color: row.prediction === 'BENIGN' ? '#00e676' : '#ff5252' }}>
                            {row.prediction}
                          </td>
                          <td style={{ padding: '12px 16px', color: isAnomalous ? '#ffb300' : '#cbd5e1' }}>
                            {getRowAnomalyScore(row)}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            {row.risk_score !== undefined ? row.risk_score.toFixed(2) : '—'}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span className={`risk-badge ${getRiskBadgeClass(row.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '700' }}>
                              {row.risk_level || 'LOW'}
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span
                              style={{
                                display: 'inline-block',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                fontWeight: '700',
                                background: isAnomalous ? 'rgba(255, 179, 0, 0.15)' : 'rgba(0, 230, 118, 0.15)',
                                color: isAnomalous ? '#ffb300' : '#00e676',
                                border: isAnomalous ? '1px solid rgba(255, 179, 0, 0.3)' : '1px solid rgba(0, 230, 118, 0.3)',
                              }}
                            >
                              {status}
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                            <button
                              type="button"
                              onClick={() => navigate('/detection-details')}
                              style={{
                                background: '#1e293b',
                                color: '#00e5ff',
                                border: '1px solid #334155',
                                borderRadius: '6px',
                                padding: '4px 12px',
                                fontSize: '0.75rem',
                                cursor: 'pointer',
                                fontWeight: '600',
                              }}
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
};

export default AnomalyMonitoring;
