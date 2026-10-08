import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { getMe, getDetectionById, getRecentDetections } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';

import '../components/dashboard/dashboard.css';

const DetectionDetails = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();

  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Detection data state
  const [detection, setDetection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  useEffect(() => {
    // 1. Check if passed via location.state (e.g. from TrafficAnalysis live predict or table Click)
    const stateDetection = location.state?.detection || location.state?.result;
    if (stateDetection) {
      setDetection(stateDetection);
      setLoading(false);
      return;
    }

    // 2. If ID parameter exists in URL, fetch single detection from backend API
    if (id) {
      getDetectionById(id)
        .then((res) => {
          setDetection(res.data);
          setLoading(false);
        })
        .catch((err) => {
          if (err.response?.status === 404) {
            setError('Detection not found.');
          } else {
            setError('Unable to load detection details.');
          }
          setLoading(false);
        });
      return;
    }

    // 3. Fallback: Fetch most recent detection from recent-detections API
    getRecentDetections()
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setDetection(res.data[0]);
        } else {
          setError('Detection not found.');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Unable to load detection details.');
        setLoading(false);
      });
  }, [id, location.state]);

  const getRiskBadgeClass = (level) => {
    switch (level) {
      case 'CRITICAL': return 'risk-badge-critical';
      case 'HIGH': return 'risk-badge-high';
      case 'MEDIUM': return 'risk-badge-medium';
      case 'LOW': return 'risk-badge-low';
      default: return 'risk-badge-info';
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return '—';
    try {
      const date = new Date(isoString);
      return date.toLocaleString();
    } catch {
      return isoString;
    }
  };

  // Process SHAP features if available
  const rawExplanations = detection?.shap_values || detection?.explanation;
  const explanations = Array.isArray(rawExplanations) ? rawExplanations : [];
  const sortedExplanations = [...explanations].sort(
    (a, b) => Math.abs(b?.shap_value || 0) - Math.abs(a?.shap_value || 0)
  );

  const maxAbsShap = sortedExplanations.length > 0
    ? Math.max(...sortedExplanations.map((exp) => Math.abs(exp.shap_value)), 0.0001)
    : 1;

  const topPositive = sortedExplanations.find((exp) => exp.shap_value > 0);
  const topNegative = sortedExplanations.find((exp) => exp.shap_value < 0);

  return (
    <div className="soc-dashboard-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />

      <div className="soc-main-layout">
        <Topbar onToggleSidebar={() => setSidebarOpen((p) => !p)} user={user} />

        <main className="soc-content">
          {/* Back Action Bar */}
          <div style={{ marginBottom: '16px' }}>
            <button
              type="button"
              onClick={() => navigate('/threat-detection')}
              style={{
                background: '#1e293b',
                color: '#00e5ff',
                border: '1px solid #334155',
                borderRadius: '8px',
                padding: '8px 16px',
                fontSize: '0.875rem',
                cursor: 'pointer',
                fontWeight: '600',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              ← Back to Threat Detection
            </button>
          </div>

          {/* Page Header */}
          <header className="page-header" style={{ marginBottom: '24px' }}>
            <h1 className="page-title" style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff', margin: 0 }}>
              Detection Details
            </h1>
            <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
              Detailed analysis and explainable AI insights for this network detection.
            </p>
          </header>

          {/* Loading State */}
          {loading && (
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '48px 20px', textAlign: 'center', color: '#00e5ff' }}>
              <div style={{ width: '36px', height: '36px', border: '3px solid rgba(0, 229, 255, 0.2)', borderTopColor: '#00e5ff', borderRadius: '50%', margin: '0 auto 16px', animation: 'spin 0.8s linear infinite' }} />
              <p style={{ margin: 0, fontWeight: '600', color: '#cbd5e1' }}>Loading detection details...</p>
            </div>
          )}

          {/* Error / Empty State */}
          {!loading && error && (
            <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '48px 20px', textAlign: 'center', color: '#ff5252' }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: '12px' }}>
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <p style={{ fontSize: '1.1rem', fontWeight: '600', margin: 0 }}>{error}</p>
              <button
                type="button"
                onClick={() => navigate('/threat-detection')}
                style={{ marginTop: '16px', background: '#1e293b', color: '#00e5ff', border: '1px solid #334155', borderRadius: '6px', padding: '8px 16px', cursor: 'pointer' }}
              >
                Return to Threat Detection
              </button>
            </div>
          )}

          {/* Real Detection Content */}
          {!loading && !error && detection && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

              {/* SECTION 1: SUMMARY CARD */}
              <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  Detection Summary {detection.id ? `#${detection.id}` : ''}
                </h2>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px' }}>
                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Prediction</span>
                    <strong style={{ fontSize: '1.25rem', color: detection.prediction === 'BENIGN' ? '#00e676' : '#ff1744' }}>
                      {detection.prediction}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Confidence</span>
                    <strong style={{ fontSize: '1.25rem', color: '#00e5ff' }}>
                      {detection.confidence !== undefined ? `${detection.confidence.toFixed(2)}%` : '—'}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Attack Severity</span>
                    <strong style={{ fontSize: '1.25rem', color: detection.attack_severity > 50 ? '#ffb300' : '#f8fafc' }}>
                      {detection.attack_severity ?? '0'}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Anomaly Score</span>
                    <strong style={{ fontSize: '1.25rem', color: detection.anomaly_score > 0 ? '#ffb300' : '#f8fafc' }}>
                      {detection.anomaly_score !== undefined ? detection.anomaly_score.toFixed(4) : '—'}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Score</span>
                    <strong style={{ fontSize: '1.25rem', color: '#f8fafc' }}>
                      {detection.risk_score !== undefined ? detection.risk_score.toFixed(2) : '—'}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Level</span>
                    <span className={`risk-badge ${getRiskBadgeClass(detection.risk_level)}`} style={{ padding: '4px 10px', borderRadius: '4px', fontWeight: '700', fontSize: '0.85rem', display: 'inline-block' }}>
                      {detection.risk_level || 'LOW'}
                    </span>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: 'span 2' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Timestamp</span>
                    <span style={{ fontSize: '0.9rem', color: '#cbd5e1', fontFamily: 'monospace' }}>
                      {formatTime(detection.timestamp)}
                    </span>
                  </div>
                </div>
              </section>

              {/* SECTIONS 2, 3, 4 GRID */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                
                {/* SECTION 2: THREAT CLASSIFICATION */}
                <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                  <h3 style={{ color: '#00e5ff', fontSize: '1.05rem', fontWeight: '600', margin: '0 0 16px 0' }}>
                    Threat Classification
                  </h3>
                  <div style={{ background: '#0b1329', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontWeight: '700', color: '#f8fafc', fontSize: '1.1rem' }}>{detection.prediction}</span>
                      <span style={{ color: '#00e5ff', fontWeight: '600' }}>
                        {detection.confidence !== undefined ? `${detection.confidence.toFixed(2)}%` : '—'}
                      </span>
                    </div>
                    <div style={{ height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${detection.confidence || 0}%`,
                          height: '100%',
                          background: detection.prediction === 'BENIGN' ? '#00e676' : 'linear-gradient(90deg, #ff9100, #ff1744)',
                          borderRadius: '4px',
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* SECTION 3: RISK ASSESSMENT */}
                <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                  <h3 style={{ color: '#00e5ff', fontSize: '1.05rem', fontWeight: '600', margin: '0 0 16px 0' }}>
                    Risk Assessment
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0b1329', borderRadius: '6px' }}>
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Risk Score</span>
                      <strong style={{ color: '#f8fafc' }}>{detection.risk_score !== undefined ? `${detection.risk_score.toFixed(2)} / 100` : '—'}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0b1329', borderRadius: '6px' }}>
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Risk Level</span>
                      <span className={`risk-badge ${getRiskBadgeClass(detection.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '700' }}>
                        {detection.risk_level || 'LOW'}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0b1329', borderRadius: '6px' }}>
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Attack Severity</span>
                      <strong style={{ color: '#f8fafc' }}>{detection.attack_severity ?? 0} / 100</strong>
                    </div>
                  </div>
                </div>

                {/* SECTION 4: ANOMALY ANALYSIS */}
                <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                  <h3 style={{ color: '#00e5ff', fontSize: '1.05rem', fontWeight: '600', margin: '0 0 16px 0' }}>
                    Anomaly Analysis
                  </h3>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0b1329', borderRadius: '6px', marginBottom: '12px' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Anomaly Status</span>
                    <span style={{ color: detection.anomaly_score > 0 ? '#ffb300' : '#00e676', fontWeight: '700', fontSize: '0.85rem' }}>
                      {detection.anomaly_score > 0 ? 'ANOMALOUS' : 'NORMAL'}
                    </span>
                  </div>
                  <p style={{ color: '#94a3b8', fontSize: '0.8rem', lineHeight: '1.4', margin: 0, background: '#0b1329', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
                    Anomaly detection identifies traffic that deviates from learned benign behavior and provides an additional signal for potentially novel or previously unseen threats.
                  </p>
                </div>

              </div>

              {/* SECTION 5: SHAP EXPLAINABILITY */}
              <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <header style={{ marginBottom: '16px' }}>
                  <h2 style={{ color: '#00e5ff', fontSize: '1.2rem', fontWeight: '600', margin: 0 }}>
                    Why did the model make this prediction?
                  </h2>
                  <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '4px 0 0 0' }}>
                    SHAP-based feature attribution
                  </p>
                </header>

                {sortedExplanations.length > 0 ? (
                  <div>
                    {/* Horizontal Bar Chart */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                      {sortedExplanations.map((exp, idx) => {
                        const isPositive = exp.shap_value > 0;
                        const pct = Math.min(Math.max((Math.abs(exp.shap_value) / maxAbsShap) * 100, 5), 100);
                        const barColor = isPositive ? '#ff5252' : '#00e676';
                        return (
                          <div key={idx} style={{ background: '#0b1329', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.85rem' }}>
                              <span style={{ color: '#f8fafc', fontWeight: '600' }}>{exp.feature}</span>
                              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>Val: {exp.value}</span>
                                <span style={{ color: barColor, fontWeight: '700', fontFamily: 'monospace' }}>
                                  {isPositive ? `+${exp.shap_value.toFixed(4)}` : exp.shap_value.toFixed(4)}
                                </span>
                              </div>
                            </div>
                            <div style={{ height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                              <div
                                style={{
                                  width: `${pct}%`,
                                  height: '100%',
                                  background: barColor,
                                  borderRadius: '4px',
                                }}
                              />
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '4px', textAlign: 'right' }}>
                              Impact: {isPositive ? 'Increased risk contribution' : 'Decreased risk contribution'}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Dynamic Explanation Summary */}
                    <div style={{ background: '#0b1329', padding: '14px', borderRadius: '8px', border: '1px solid #1e293b', fontSize: '0.85rem', color: '#cbd5e1' }}>
                      <p style={{ margin: '0 0 6px 0', fontWeight: '600', color: '#00e5ff' }}>
                        These features had the strongest influence on the model's prediction.
                      </p>
                      {topPositive && (
                        <p style={{ margin: '4px 0 0 0', color: '#94a3b8' }}>
                          • <strong>{topPositive.feature}</strong> (+{topPositive.shap_value.toFixed(4)}) was strongly associated with the model's prediction.
                        </p>
                      )}
                      {topNegative && (
                        <p style={{ margin: '4px 0 0 0', color: '#94a3b8' }}>
                          • <strong>{topNegative.feature}</strong> ({topNegative.shap_value.toFixed(4)}) reduced the overall risk score contribution.
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '24px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', textAlign: 'center', color: '#94a3b8', fontSize: '0.875rem' }}>
                    SHAP feature explanations are generated during live traffic prediction. Run a new analysis in <strong>Traffic Analysis</strong> to view real-time SHAP feature attributions.
                  </div>
                )}
              </section>

              {/* SECTION 6: NETWORK FLOW INFORMATION */}
              <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ color: '#00e5ff', fontSize: '1.05rem', fontWeight: '600', margin: '0 0 12px 0' }}>
                  Network Flow Features
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0, background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  Original flow features are not stored for this detection.
                </p>
              </section>

              {/* SECTION 7: DETECTION TIMELINE */}
              <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ color: '#00e5ff', fontSize: '1.05rem', fontWeight: '600', margin: '0 0 16px 0' }}>
                  SecureNet AI Processing Pipeline
                </h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', padding: '16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <span style={{ background: '#1e293b', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600' }}>
                    1. Traffic Received
                  </span>
                  <span style={{ color: '#64748b' }}>→</span>
                  <span style={{ background: '#1e293b', color: '#00e5ff', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600' }}>
                    2. XGBoost Classification
                  </span>
                  <span style={{ color: '#64748b' }}>→</span>
                  <span style={{ background: '#1e293b', color: '#ffb300', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600' }}>
                    3. Anomaly Detection
                  </span>
                  <span style={{ color: '#64748b' }}>→</span>
                  <span style={{ background: '#1e293b', color: '#00e676', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600' }}>
                    4. SHAP Explanation
                  </span>
                  <span style={{ color: '#64748b' }}>→</span>
                  <span style={{ background: '#1e293b', color: '#ff1744', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '600' }}>
                    5. Risk Assessment
                  </span>
                </div>
              </section>

              {/* SECTION 8: ACTIONS */}
              <section style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '8px' }}>
                <button
                  type="button"
                  onClick={() => navigate('/threat-detection')}
                  style={{
                    padding: '10px 20px',
                    background: '#1e293b',
                    color: '#00e5ff',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600',
                  }}
                >
                  Back to Threat Detection
                </button>

                <button
                  type="button"
                  onClick={() => navigate('/traffic-analysis')}
                  style={{
                    padding: '10px 20px',
                    background: 'linear-gradient(135deg, #00e5ff 0%, #00b0ff 100%)',
                    color: '#090d16',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '700',
                  }}
                >
                  Analyze New Traffic
                </button>

                <button
                  type="button"
                  disabled
                  style={{
                    padding: '10px 20px',
                    background: '#0b1329',
                    color: '#64748b',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                    cursor: 'not-allowed',
                    fontWeight: '600',
                  }}
                >
                  Export Report (Standard)
                </button>
              </section>

            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DetectionDetails;
