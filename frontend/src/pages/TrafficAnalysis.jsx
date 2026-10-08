import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, predictTraffic } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';

import '../components/dashboard/dashboard.css';

// 10 Collapsible Groups mapping all 78 exact features
const FEATURE_GROUPS = [
  {
    id: 'flow_info',
    title: '1. Flow Information',
    features: [
      { name: 'Destination Port', label: 'Destination Port', default: 80, tooltip: 'Target port number (0-65535)' },
      { name: 'Flow Duration', label: 'Flow Duration', default: 1000, tooltip: 'Total duration of flow in microseconds' },
      { name: 'Flow Bytes/s', label: 'Flow Bytes/s', default: 500.0, tooltip: 'Bytes transferred per second' },
      { name: 'Flow Packets/s', label: 'Flow Packets/s', default: 10.0, tooltip: 'Packets transferred per second' },
      { name: 'Down/Up Ratio', label: 'Down/Up Ratio', default: 1.0, tooltip: 'Download/Upload ratio' },
      { name: 'Average Packet Size', label: 'Average Packet Size', default: 64.0, tooltip: 'Average packet size in bytes' },
    ],
  },
  {
    id: 'fwd_traffic',
    title: '2. Forward Traffic',
    features: [
      { name: 'Total Fwd Packets', label: 'Total Fwd Packets', default: 5 },
      { name: 'Total Length of Fwd Packets', label: 'Total Length of Fwd Packets', default: 320 },
      { name: 'Fwd Packet Length Max', label: 'Fwd Packet Length Max', default: 128 },
      { name: 'Fwd Packet Length Min', label: 'Fwd Packet Length Min', default: 40 },
      { name: 'Fwd Packet Length Mean', label: 'Fwd Packet Length Mean', default: 64.0 },
      { name: 'Fwd Packet Length Std', label: 'Fwd Packet Length Std', default: 12.5 },
      { name: 'Fwd Packets/s', label: 'Fwd Packets/s', default: 5.0 },
      { name: 'Avg Fwd Segment Size', label: 'Avg Fwd Segment Size', default: 64.0 },
      { name: 'Fwd Avg Bytes/Bulk', label: 'Fwd Avg Bytes/Bulk', default: 0 },
      { name: 'Fwd Avg Packets/Bulk', label: 'Fwd Avg Packets/Bulk', default: 0 },
      { name: 'Fwd Avg Bulk Rate', label: 'Fwd Avg Bulk Rate', default: 0 },
    ],
  },
  {
    id: 'bwd_traffic',
    title: '3. Backward Traffic',
    features: [
      { name: 'Total Backward Packets', label: 'Total Backward Packets', default: 5 },
      { name: 'Total Length of Bwd Packets', label: 'Total Length of Bwd Packets', default: 320 },
      { name: 'Bwd Packet Length Max', label: 'Bwd Packet Length Max', default: 128 },
      { name: 'Bwd Packet Length Min', label: 'Bwd Packet Length Min', default: 40 },
      { name: 'Bwd Packet Length Mean', label: 'Bwd Packet Length Mean', default: 64.0 },
      { name: 'Bwd Packet Length Std', label: 'Bwd Packet Length Std', default: 12.5 },
      { name: 'Bwd Packets/s', label: 'Bwd Packets/s', default: 5.0 },
      { name: 'Avg Bwd Segment Size', label: 'Avg Bwd Segment Size', default: 64.0 },
      { name: 'Bwd Avg Bytes/Bulk', label: 'Bwd Avg Bytes/Bulk', default: 0 },
      { name: 'Bwd Avg Packets/Bulk', label: 'Bwd Avg Packets/Bulk', default: 0 },
      { name: 'Bwd Avg Bulk Rate', label: 'Bwd Avg Bulk Rate', default: 0 },
    ],
  },
  {
    id: 'pkt_len',
    title: '4. Packet Length',
    features: [
      { name: 'Min Packet Length', label: 'Min Packet Length', default: 40 },
      { name: 'Max Packet Length', label: 'Max Packet Length', default: 128 },
      { name: 'Packet Length Mean', label: 'Packet Length Mean', default: 64.0 },
      { name: 'Packet Length Std', label: 'Packet Length Std', default: 12.5 },
      { name: 'Packet Length Variance', label: 'Packet Length Variance', default: 156.25 },
    ],
  },
  {
    id: 'iat_info',
    title: '5. Inter-Arrival Time',
    features: [
      { name: 'Flow IAT Mean', label: 'Flow IAT Mean', default: 100.0 },
      { name: 'Flow IAT Std', label: 'Flow IAT Std', default: 20.0 },
      { name: 'Flow IAT Max', label: 'Flow IAT Max', default: 200.0 },
      { name: 'Flow IAT Min', label: 'Flow IAT Min', default: 10.0 },
      { name: 'Fwd IAT Total', label: 'Fwd IAT Total', default: 1000.0 },
      { name: 'Fwd IAT Mean', label: 'Fwd IAT Mean', default: 200.0 },
      { name: 'Fwd IAT Std', label: 'Fwd IAT Std', default: 30.0 },
      { name: 'Fwd IAT Max', label: 'Fwd IAT Max', default: 300.0 },
      { name: 'Fwd IAT Min', label: 'Fwd IAT Min', default: 20.0 },
      { name: 'Bwd IAT Total', label: 'Bwd IAT Total', default: 1000.0 },
      { name: 'Bwd IAT Mean', label: 'Bwd IAT Mean', default: 200.0 },
      { name: 'Bwd IAT Std', label: 'Bwd IAT Std', default: 30.0 },
      { name: 'Bwd IAT Max', label: 'Bwd IAT Max', default: 300.0 },
      { name: 'Bwd IAT Min', label: 'Bwd IAT Min', default: 20.0 },
    ],
  },
  {
    id: 'tcp_flags',
    title: '6. TCP Flags',
    features: [
      { name: 'Fwd PSH Flags', label: 'Fwd PSH Flags', default: 0 },
      { name: 'Bwd PSH Flags', label: 'Bwd PSH Flags', default: 0 },
      { name: 'Fwd URG Flags', label: 'Fwd URG Flags', default: 0 },
      { name: 'Bwd URG Flags', label: 'Bwd URG Flags', default: 0 },
      { name: 'FIN Flag Count', label: 'FIN Flag Count', default: 0 },
      { name: 'SYN Flag Count', label: 'SYN Flag Count', default: 1 },
      { name: 'RST Flag Count', label: 'RST Flag Count', default: 0 },
      { name: 'PSH Flag Count', label: 'PSH Flag Count', default: 0 },
      { name: 'ACK Flag Count', label: 'ACK Flag Count', default: 1 },
      { name: 'URG Flag Count', label: 'URG Flag Count', default: 0 },
      { name: 'CWE Flag Count', label: 'CWE Flag Count', default: 0 },
      { name: 'ECE Flag Count', label: 'ECE Flag Count', default: 0 },
    ],
  },
  {
    id: 'hdr_info',
    title: '7. Header Information',
    features: [
      { name: 'Fwd Header Length', label: 'Fwd Header Length', default: 160 },
      { name: 'Bwd Header Length', label: 'Bwd Header Length', default: 160 },
      { name: 'Fwd Header Length.1', label: 'Fwd Header Length.1', default: 160 },
    ],
  },
  {
    id: 'subflow_info',
    title: '8. Subflow Information',
    features: [
      { name: 'Subflow Fwd Packets', label: 'Subflow Fwd Packets', default: 5 },
      { name: 'Subflow Fwd Bytes', label: 'Subflow Fwd Bytes', default: 320 },
      { name: 'Subflow Bwd Packets', label: 'Subflow Bwd Packets', default: 5 },
      { name: 'Subflow Bwd Bytes', label: 'Subflow Bwd Bytes', default: 320 },
    ],
  },
  {
    id: 'win_info',
    title: '9. Window Information',
    features: [
      { name: 'Init_Win_bytes_forward', label: 'Init Win Bytes Fwd', default: 8192 },
      { name: 'Init_Win_bytes_backward', label: 'Init Win Bytes Bwd', default: 8192 },
      { name: 'act_data_pkt_fwd', label: 'Act Data Pkt Fwd', default: 3 },
      { name: 'min_seg_size_forward', label: 'Min Seg Size Fwd', default: 32 },
    ],
  },
  {
    id: 'idle_info',
    title: '10. Activity / Idle Information',
    features: [
      { name: 'Active Mean', label: 'Active Mean', default: 0.0 },
      { name: 'Active Std', label: 'Active Std', default: 0.0 },
      { name: 'Active Max', label: 'Active Max', default: 0.0 },
      { name: 'Active Min', label: 'Active Min', default: 0.0 },
      { name: 'Idle Mean', label: 'Idle Mean', default: 0.0 },
      { name: 'Idle Std', label: 'Idle Std', default: 0.0 },
      { name: 'Idle Max', label: 'Idle Max', default: 0.0 },
      { name: 'Idle Min', label: 'Idle Min', default: 0.0 },
    ],
  },
];

// Helper to generate default zeroed/preset feature state
const getDefaultFeatures = (isSampleDDoS = false) => {
  const initial = {};
  FEATURE_GROUPS.forEach((group) => {
    group.features.forEach((feat) => {
      if (isSampleDDoS) {
        // High traffic / abnormal values for DDoS sample demonstration
        if (feat.name === 'Flow Packets/s') initial[feat.name] = 50000.0;
        else if (feat.name === 'Total Fwd Packets') initial[feat.name] = 1200;
        else if (feat.name === 'Flow Duration') initial[feat.name] = 200;
        else if (feat.name === 'SYN Flag Count') initial[feat.name] = 1200;
        else initial[feat.name] = feat.default;
      } else {
        initial[feat.name] = feat.default;
      }
    });
  });
  return initial;
};

const TrafficAnalysis = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Form feature values state
  const [features, setFeatures] = useState(() => getDefaultFeatures(false));

  // Accordion collapsed state (open first 2 by default)
  const [openGroups, setOpenGroups] = useState({ flow_info: true, fwd_traffic: true });

  // Analysis result state
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  const toggleGroup = (groupId) => {
    setOpenGroups((prev) => ({
      ...prev,
      [groupId]: !prev[groupId],
    }));
  };

  const handleInputChange = (featureName, val) => {
    const num = parseFloat(val);
    setFeatures((prev) => ({
      ...prev,
      [featureName]: isNaN(num) ? 0 : num,
    }));
  };

  const handleReset = () => {
    setFeatures(getDefaultFeatures(false));
    setResult(null);
    setError(null);
  };

  const handleLoadSample = (ddos = false) => {
    setFeatures(getDefaultFeatures(ddos));
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await predictTraffic(features);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete network flow prediction.');
    } finally {
      setLoading(false);
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
              Traffic Analysis
            </h1>
            <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
              Analyze network traffic using the SecureNet AI detection engine.
            </p>
          </header>

          {/* Two Column Grid */}
          <div className="traffic-analysis-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px', alignItems: 'start' }}>
            
            {/* LEFT COLUMN: FLOW INPUT FORM */}
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                  Network Flow Input
                </h2>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    onClick={() => handleLoadSample(false)}
                    style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: '6px', padding: '4px 10px', fontSize: '0.75rem', cursor: 'pointer' }}
                    title="Load Benign Flow Sample"
                  >
                    Sample (Benign)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleLoadSample(true)}
                    style={{ background: 'rgba(255, 23, 68, 0.15)', color: '#ff1744', border: '1px solid rgba(255, 23, 68, 0.4)', borderRadius: '6px', padding: '4px 10px', fontSize: '0.75rem', cursor: 'pointer' }}
                    title="Load Attack Flow Sample"
                  >
                    Sample (DDoS)
                  </button>
                </div>
              </div>

              <form onSubmit={handleAnalyze}>
                {FEATURE_GROUPS.map((group) => {
                  const isOpen = !!openGroups[group.id];
                  return (
                    <div key={group.id} style={{ marginBottom: '12px', border: '1px solid #1e293b', borderRadius: '8px', overflow: 'hidden' }}>
                      <button
                        type="button"
                        onClick={() => toggleGroup(group.id)}
                        style={{
                          width: '100%',
                          display: 'flex',
                          justify: 'space-between',
                          alignItems: 'center',
                          padding: '12px 16px',
                          background: isOpen ? '#1e293b' : '#0b1329',
                          color: isOpen ? '#00e5ff' : '#cbd5e1',
                          border: 'none',
                          cursor: 'pointer',
                          fontWeight: '600',
                          fontSize: '0.875rem',
                          textAlign: 'left',
                        }}
                      >
                        <span>{group.title}</span>
                        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{isOpen ? '▲' : '▼'}</span>
                      </button>

                      {isOpen && (
                        <div style={{ padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '12px', background: '#0b1120' }}>
                          {group.features.map((feat) => (
                            <div key={feat.name} style={{ display: 'flex', flexDirection: 'column' }}>
                              <label
                                htmlFor={feat.name}
                                title={feat.tooltip || feat.label}
                                style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                              >
                                {feat.label}
                              </label>
                              <input
                                id={feat.name}
                                type="number"
                                step="any"
                                value={features[feat.name] ?? 0}
                                onChange={(e) => handleInputChange(feat.name, e.target.value)}
                                style={{
                                  background: '#0f172a',
                                  border: '1px solid #334155',
                                  color: '#f8fafc',
                                  borderRadius: '6px',
                                  padding: '6px 8px',
                                  fontSize: '0.85rem',
                                  outline: 'none',
                                }}
                              />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Bottom Actions */}
                <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                  <button
                    type="submit"
                    disabled={loading}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: loading ? '#334155' : 'linear-gradient(135deg, #00e5ff 0%, #00b0ff 100%)',
                      color: '#090d16',
                      fontWeight: '700',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontSize: '0.95rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                    }}
                  >
                    {loading ? (
                      <>
                        <span className="spinner" style={{ width: '16px', height: '16px', border: '2px solid rgba(0,0,0,0.2)', borderTopColor: '#000', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                        Analyzing Traffic...
                      </>
                    ) : (
                      'Analyze Traffic'
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={handleReset}
                    disabled={loading}
                    style={{
                      padding: '12px 20px',
                      background: '#1e293b',
                      color: '#cbd5e1',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                    }}
                  >
                    Reset
                  </button>
                </div>
              </form>
            </div>

            {/* RIGHT COLUMN: ANALYSIS RESULT */}
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px', position: 'sticky', top: '90px' }}>
              <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', marginBottom: '16px', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                Analysis Result
              </h2>

              {/* Initial State */}
              {!loading && !result && !error && (
                <div style={{ textAlign: 'center', padding: '48px 20px', color: '#64748b' }}>
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: '12px', color: '#334155' }}>
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                  <p style={{ margin: 0, fontSize: '0.95rem', color: '#94a3b8' }}>Submit network traffic for analysis.</p>
                  <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '6px' }}>
                    Configure flow features or click a sample preset, then press "Analyze Traffic".
                  </p>
                </div>
              )}

              {/* Loading State */}
              {loading && (
                <div style={{ textAlign: 'center', padding: '48px 20px', color: '#00e5ff' }}>
                  <div style={{ width: '36px', height: '36px', border: '3px solid rgba(0, 229, 255, 0.2)', borderTopColor: '#00e5ff', borderRadius: '50%', margin: '0 auto 16px', animation: 'spin 0.8s linear infinite' }} />
                  <p style={{ fontWeight: '600', color: '#f8fafc', margin: 0 }}>Evaluating Flow Features</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>Running XGBoost, Isolation Forest, and SHAP explainability...</p>
                </div>
              )}

              {/* Error State */}
              {error && (
                <div style={{ padding: '16px', background: 'rgba(255, 23, 68, 0.1)', border: '1px solid #ff1744', borderRadius: '8px', color: '#ff5252', fontSize: '0.9rem', marginTop: '16px' }}>
                  <strong>Error:</strong> {error}
                </div>
              )}

              {/* Result State */}
              {result && !loading && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Prediction</span>
                      <strong style={{ fontSize: '1.2rem', color: result.prediction === 'BENIGN' ? '#00e676' : '#ff1744' }}>
                        {result.prediction}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Confidence</span>
                      <strong style={{ fontSize: '1.2rem', color: '#00e5ff' }}>
                        {result.confidence ? `${result.confidence.toFixed(2)}%` : '—'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Attack Severity</span>
                      <strong style={{ fontSize: '1.2rem', color: result.attack_severity > 50 ? '#ffb300' : '#f8fafc' }}>
                        {result.attack_severity ?? '0'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Anomaly Score</span>
                      <strong style={{ fontSize: '1.2rem', color: result.anomaly_score > 0 ? '#ffb300' : '#f8fafc' }}>
                        {result.anomaly_score !== undefined ? result.anomaly_score.toFixed(4) : '—'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Score</span>
                      <strong style={{ fontSize: '1.2rem', color: '#f8fafc' }}>
                        {result.risk_score !== undefined ? result.risk_score.toFixed(2) : '—'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Level</span>
                      <span
                        className={`risk-badge ${getRiskBadgeClass(result.risk_level)}`}
                        style={{ display: 'inline-block', padding: '4px 10px', borderRadius: '4px', fontWeight: '700', fontSize: '0.85rem' }}
                      >
                        {result.risk_level || 'LOW'}
                      </span>
                    </div>
                  </div>

                  {/* SHAP Explanation Section if available */}
                  {result.explanation && result.explanation.length > 0 && (
                    <div style={{ marginTop: '20px', background: '#0b1329', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <h4 style={{ color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>
                          SHAP Feature Attribution
                        </h4>
                        <button
                          type="button"
                          onClick={() => navigate('/detection-details', { state: { result } })}
                          style={{
                            background: '#1e293b',
                            color: '#00e5ff',
                            border: '1px solid #334155',
                            borderRadius: '6px',
                            padding: '4px 10px',
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            fontWeight: '600',
                          }}
                        >
                          View Full Details →
                        </button>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
                        {result.explanation.map((exp, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', padding: '4px 8px', background: '#0f172a', borderRadius: '4px' }}>
                            <span style={{ color: '#cbd5e1' }}>{exp.feature}</span>
                            <span style={{ color: exp.direction === 'INCREASE_RISK' ? '#ff5252' : '#00e676', fontWeight: '600' }}>
                              {exp.shap_value > 0 ? `+${exp.shap_value.toFixed(4)}` : exp.shap_value.toFixed(4)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

          </div>
        </main>
      </div>
    </div>
  );
};

export default TrafficAnalysis;
