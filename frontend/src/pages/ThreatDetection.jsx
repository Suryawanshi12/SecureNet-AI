import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getDashboardStats, getRiskDistribution, getRecentDetections } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';
import StatCard from '../components/dashboard/StatCard';

import '../components/dashboard/dashboard.css';

const ATTACK_CLASSES = [
  'All Attack Types',
  'BENIGN',
  'Bot',
  'DDoS',
  'DoS GoldenEye',
  'DoS Hulk',
  'FTP-Patator',
  'DoS slowloris',
  'DoS Slowhttest',
  'Heartbleed',
  'Infiltration',
  'PortScan',
  'SSH-Patator',
  'Web Attack - Brute Force',
  'Web Attack - Sql Injection',
  'Web Attack - XSS',
];

const RISK_LEVELS = ['All Risk Levels', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

const ThreatDetection = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Summary statistics state
  const [stats, setStats] = useState(null);
  const [riskDist, setRiskDist] = useState([]);
  const [statsLoading, setStatsLoading] = useState(true);

  // Detection list state
  const [detections, setDetections] = useState([]);
  const [loadingDetections, setLoadingDetections] = useState(true);

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAttack, setSelectedAttack] = useState('All Attack Types');
  const [selectedRisk, setSelectedRisk] = useState('All Risk Levels');

  useEffect(() => {
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  useEffect(() => {
    // Fetch stats, risk distribution, and detections
    Promise.all([
      getDashboardStats().catch(() => null),
      getRiskDistribution().catch(() => null),
      getRecentDetections().catch(() => null),
    ]).then(([statsRes, riskRes, detectRes]) => {
      if (statsRes) setStats(statsRes.data);
      if (riskRes) setRiskDist(riskRes.data);
      if (detectRes) setDetections(detectRes.data || []);

      setStatsLoading(false);
      setLoadingDetections(false);
    });
  }, []);

  const getHighRiskCount = () => {
    if (!riskDist || riskDist.length === 0) return 0;
    const found = riskDist.find((r) => r.risk_level === 'HIGH');
    return found ? found.count : 0;
  };

  // Filter logic
  const filteredDetections = detections.filter((item) => {
    if (selectedAttack !== 'All Attack Types' && item.prediction !== selectedAttack) {
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
              Threat Detection
            </h1>
            <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
              Monitor and investigate detected network threats.
            </p>
          </header>

          {/* Top Summary Cards */}
          <section className="stat-cards-grid" style={{ marginBottom: '24px' }}>
            <StatCard
              title="TOTAL THREATS"
              value={statsLoading ? '…' : (stats?.threats_detected ?? '—')}
              badgeText="Non-BENIGN detections"
              iconColor="#ffb300"
            />
            <StatCard
              title="HIGH RISK"
              value={statsLoading ? '…' : (getHighRiskCount() ?? '—')}
              badgeText="Risk level HIGH"
              iconColor="#ff9100"
            />
            <StatCard
              title="CRITICAL THREATS"
              value={statsLoading ? '…' : (stats?.critical_threats ?? '—')}
              badgeText="Risk level CRITICAL"
              iconColor="#ff1744"
            />
            <StatCard
              title="ANOMALIES"
              value={statsLoading ? '…' : (stats?.anomalies ?? '—')}
              badgeText="Isolation Forest Detections"
              iconColor="#00e5ff"
            />
          </section>

          {/* Filter Bar & Table Section */}
          <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
              
              {/* Search Box */}
              <div style={{ flex: '1', minWidth: '220px' }}>
                <input
                  type="text"
                  placeholder="Search by prediction or risk level..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '0.875rem',
                    outline: 'none',
                  }}
                />
              </div>

              {/* Attack Type Dropdown */}
              <div style={{ minWidth: '180px' }}>
                <select
                  value={selectedAttack}
                  onChange={(e) => setSelectedAttack(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '0.875rem',
                    outline: 'none',
                  }}
                >
                  {ATTACK_CLASSES.map((cls) => (
                    <option key={cls} value={cls}>
                      {cls}
                    </option>
                  ))}
                </select>
              </div>

              {/* Risk Level Dropdown */}
              <div style={{ minWidth: '160px' }}>
                <select
                  value={selectedRisk}
                  onChange={(e) => setSelectedRisk(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#0b1329',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '0.875rem',
                    outline: 'none',
                  }}
                >
                  {RISK_LEVELS.map((lvl) => (
                    <option key={lvl} value={lvl}>
                      {lvl}
                    </option>
                  ))}
                </select>
              </div>

            </div>

            {/* Detections Table / Empty State */}
            {loadingDetections ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                Loading threat detection history...
              </div>
            ) : filteredDetections.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '48px 20px', color: '#64748b' }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: '12px', color: '#334155' }}>
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <p style={{ margin: 0, fontSize: '1rem', color: '#cbd5e1', fontWeight: '600' }}>
                  No threats detected yet.
                </p>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '6px' }}>
                  Network detections will appear here after traffic analysis.
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="soc-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <th style={{ padding: '12px 16px' }}>Time</th>
                      <th style={{ padding: '12px 16px' }}>Prediction</th>
                      <th style={{ padding: '12px 16px' }}>Confidence</th>
                      <th style={{ padding: '12px 16px' }}>Severity</th>
                      <th style={{ padding: '12px 16px' }}>Risk Score</th>
                      <th style={{ padding: '12px 16px' }}>Risk Level</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDetections.map((row) => (
                      <tr key={row.id} style={{ borderBottom: '1px solid #1e293b', color: '#e2e8f0', fontSize: '0.875rem' }}>
                        <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{formatTime(row.timestamp)}</td>
                        <td style={{ padding: '12px 16px', fontWeight: '600', color: row.prediction === 'BENIGN' ? '#00e676' : '#ff5252' }}>
                          {row.prediction}
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          {row.confidence ? `${row.confidence.toFixed(2)}%` : '—'}
                        </td>
                        <td style={{ padding: '12px 16px' }}>{row.attack_severity ?? 0}</td>
                        <td style={{ padding: '12px 16px' }}>
                          {row.risk_score !== undefined ? row.risk_score.toFixed(2) : '—'}
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <span className={`risk-badge ${getRiskBadgeClass(row.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '700' }}>
                            {row.risk_level || 'LOW'}
                          </span>
                        </td>
                        <td style={{ padding: '12px 16px', color: '#00e5ff' }}>Detected</td>
                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                          <button
                            type="button"
                            onClick={() => navigate(`/detection-details/${row.id}`, { state: { detection: row } })}
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
                    ))}
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

export default ThreatDetection;
