import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getRealtimeStatus, startRealtimePipeline, stopRealtimePipeline } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';
import { getWebSocketUrl } from '../api/axiosInstance';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';
import StatCard from '../components/dashboard/StatCard';

import '../components/dashboard/dashboard.css';

const RealtimeMonitor = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // WebSocket Connection States: 'CONNECTING', 'LIVE', 'DISCONNECTED', 'ERROR'
  const [connectionStatus, setConnectionStatus] = useState('CONNECTING');
  const [wsUrl, setWsUrl] = useState('');

  // Live detection feed (max 200 events, newest first)
  const [detections, setDetections] = useState([]);
  const [selectedDetection, setSelectedDetection] = useState(null);

  // Live Capture Pipeline backend status state
  const [pipelineStatus, setPipelineStatus] = useState('unknown');
  const [pipelineLoading, setPipelineLoading] = useState(false);

  // Refs for managing WebSocket lifecycle without memory leaks or unnecessary re-renders
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const isComponentMounted = useRef(true);

  // Authenticate user on mount
  useEffect(() => {
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        navigate('/login', { replace: true });
      });
  }, [navigate]);

  // Fetch backend capture pipeline status
  const checkPipelineStatus = useCallback(() => {
    getRealtimeStatus()
      .then((res) => {
        if (res.data?.status) {
          setPipelineStatus(res.data.status);
        }
      })
      .catch(() => {
        setPipelineStatus('unknown');
      });
  }, []);

  useEffect(() => {
    checkPipelineStatus();
  }, [checkPipelineStatus]);

  // WebSocket connection & automatic reconnection logic
  const connectWebSocket = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    if (wsRef.current) {
      // Close old connection if open
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    const url = getWebSocketUrl('/ws/realtime-stream');
    setWsUrl(url);
    setConnectionStatus('CONNECTING');

    try {
      const socket = new WebSocket(url);
      wsRef.current = socket;

      socket.onopen = () => {
        if (isComponentMounted.current) {
          setConnectionStatus('LIVE');
        }
      };

      socket.onmessage = (event) => {
        if (!isComponentMounted.current) return;
        try {
          const payload = JSON.parse(event.data);
          
          // Never record or store raw packet payload, credentials or tokens
          const { payload: _p, content: _c, packet_data: _pd, password: _pw, token: _t, jwt: _j, ...safeDetection } = payload;
          
          setDetections((prev) => {
            const updated = [safeDetection, ...prev];
            return updated.slice(0, 200); // Keep max 200 latest frontend events
          });
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      socket.onerror = (err) => {
        console.warn('WebSocket error encountered:', err);
        if (isComponentMounted.current) {
          setConnectionStatus('ERROR');
        }
      };

      socket.onclose = (event) => {
        if (!isComponentMounted.current) return;
        console.log(`WebSocket disconnected (code ${event.code}). Auto-reconnecting...`);
        setConnectionStatus('DISCONNECTED');

        // Automatically reconnect after 3 seconds if unmounted check passes
        reconnectTimerRef.current = setTimeout(() => {
          if (isComponentMounted.current) {
            connectWebSocket();
          }
        }, 3000);
      };
    } catch (err) {
      console.error('WebSocket connection setup failed:', err);
      if (isComponentMounted.current) {
        setConnectionStatus('ERROR');
        reconnectTimerRef.current = setTimeout(() => {
          if (isComponentMounted.current) {
            connectWebSocket();
          }
        }, 3000);
      }
    }
  }, []);

  useEffect(() => {
    isComponentMounted.current = true;
    connectWebSocket();

    return () => {
      isComponentMounted.current = false;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  // Manual Reconnect handler
  const handleReconnect = () => {
    connectWebSocket();
  };

  // Clear Feed handler (Frontend state only - does NOT touch PostgreSQL)
  const handleClearFeed = () => {
    setDetections([]);
  };

  // Pipeline Start/Stop handlers
  const handleStartPipeline = () => {
    setPipelineLoading(true);
    startRealtimePipeline()
      .then(() => checkPipelineStatus())
      .catch((err) => console.error('Failed to start pipeline:', err))
      .finally(() => setPipelineLoading(false));
  };

  const handleStopPipeline = () => {
    setPipelineLoading(true);
    stopRealtimePipeline()
      .then(() => checkPipelineStatus())
      .catch((err) => console.error('Failed to stop pipeline:', err))
      .finally(() => setPipelineLoading(false));
  };

  // Dynamic Card Counters derived from current active feed
  const totalFlows = detections.length;
  const threatsDetected = detections.filter((d) => d.prediction && d.prediction !== 'BENIGN').length;
  const highRisk = detections.filter((d) => d.risk_level === 'HIGH').length;
  const criticalRisk = detections.filter((d) => d.risk_level === 'CRITICAL').length;

  // Format Helpers
  const formatTime = (isoString) => {
    if (!isoString) return '—';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 });
    } catch {
      return isoString;
    }
  };

  const formatConfidence = (conf) => {
    if (conf === undefined || conf === null) return '—';
    // Handle both 0-1 and 0-100 float representations
    const pct = conf <= 1 ? conf * 100 : conf;
    return `${pct.toFixed(2)}%`;
  };

  const formatDuration = (us) => {
    if (us === undefined || us === null) return '—';
    if (us >= 1000000) return `${(us / 1000000).toFixed(2)} s`;
    if (us >= 1000) return `${(us / 1000).toFixed(2)} ms`;
    return `${us} µs`;
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

  const getStatusBadgeStyle = (status) => {
    switch (status) {
      case 'LIVE':
        return { background: 'rgba(0, 230, 118, 0.15)', border: '1px solid rgba(0, 230, 118, 0.4)', color: '#00e676' };
      case 'CONNECTING':
        return { background: 'rgba(255, 179, 0, 0.15)', border: '1px solid rgba(255, 179, 0, 0.4)', color: '#ffb300' };
      case 'ERROR':
        return { background: 'rgba(255, 23, 68, 0.15)', border: '1px solid rgba(255, 23, 68, 0.4)', color: '#ff1744' };
      case 'DISCONNECTED':
      default:
        return { background: 'rgba(148, 163, 184, 0.15)', border: '1px solid rgba(148, 163, 184, 0.4)', color: '#94a3b8' };
    }
  };

  return (
    <div className="soc-dashboard-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />

      <div className="soc-main-layout">
        <Topbar onToggleSidebar={() => setSidebarOpen((p) => !p)} user={user} />

        <main className="soc-content">
          {/* Header Bar */}
          <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <h1 className="page-title" style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff', margin: 0 }}>
                  Real-Time Monitor
                </h1>

                {/* Connection Status Badge */}
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: '700',
                    letterSpacing: '0.5px',
                    ...getStatusBadgeStyle(connectionStatus),
                  }}
                >
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: connectionStatus === 'LIVE' ? '#00e676' : connectionStatus === 'CONNECTING' ? '#ffb300' : connectionStatus === 'ERROR' ? '#ff1744' : '#94a3b8',
                      boxShadow: connectionStatus === 'LIVE' ? '0 0 8px #00e676' : 'none',
                    }}
                  />
                  {connectionStatus}
                </span>
              </div>
              <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
                Live WebSocket stream for continuous network detection monitoring ({wsUrl || 'ws://127.0.0.1:8000/ws/realtime-stream'}).
              </p>
            </div>

            {/* Action Bar */}
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
              {/* Pipeline Status Indicator & Start/Stop Controls */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#0b1329', border: '1px solid #1e293b', borderRadius: '8px', padding: '4px 10px' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Capture Pipeline:</span>
                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: pipelineStatus === 'running' ? '#00e676' : '#ff9100' }}>
                  {pipelineStatus.toUpperCase()}
                </span>
                {pipelineStatus === 'running' ? (
                  <button
                    type="button"
                    onClick={handleStopPipeline}
                    disabled={pipelineLoading}
                    style={{
                      background: 'rgba(255, 23, 68, 0.15)',
                      border: '1px solid rgba(255, 23, 68, 0.4)',
                      color: '#ff1744',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontSize: '0.7rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                    }}
                  >
                    Stop
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleStartPipeline}
                    disabled={pipelineLoading}
                    style={{
                      background: 'rgba(0, 230, 118, 0.15)',
                      border: '1px solid rgba(0, 230, 118, 0.4)',
                      color: '#00e676',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontSize: '0.7rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                    }}
                  >
                    Start Capture
                  </button>
                )}
              </div>

              {/* Retry / Reconnect Button */}
              <button
                type="button"
                onClick={handleReconnect}
                style={{
                  background: '#1e293b',
                  color: '#00e5ff',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '8px 14px',
                  fontSize: '0.825rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 4v6h-6"></path>
                  <path d="M1 20v-6h6"></path>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                </svg>
                Reconnect
              </button>

              {/* Clear Feed Button */}
              <button
                type="button"
                onClick={handleClearFeed}
                style={{
                  background: '#1e293b',
                  color: '#f8fafc',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '8px 14px',
                  fontSize: '0.825rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                Clear Feed
              </button>
            </div>
          </header>

          {/* Live Summary Cards */}
          <section className="stat-cards-grid" style={{ marginBottom: '24px' }}>
            <StatCard
              title="TOTAL FLOWS"
              value={totalFlows}
              badgeText="Active feed count (max 200)"
              iconColor="#00e5ff"
            />
            <StatCard
              title="THREATS DETECTED"
              value={threatsDetected}
              badgeText="Non-BENIGN stream detections"
              iconColor="#ffb300"
            />
            <StatCard
              title="HIGH RISK"
              value={highRisk}
              badgeText="Risk level HIGH"
              iconColor="#ff9100"
            />
            <StatCard
              title="CRITICAL RISK"
              value={criticalRisk}
              badgeText="Risk level CRITICAL"
              iconColor="#ff1744"
            />
          </section>

          {/* Real-Time Detection Feed Table */}
          <section className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#00e5ff', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4.9 19.1C1.9 16.1 1.9 11.3 4.9 8.3"></path>
                  <path d="M7.8 16.2c-1.6-1.6-1.6-4.1 0-5.7"></path>
                  <circle cx="12" cy="12" r="2"></circle>
                  <path d="M16.2 10.5c1.6 1.6 1.6 4.1 0 5.7"></path>
                  <path d="M19.1 7.6c3 3 3 7.8 0 10.8"></path>
                </svg>
                Live Event Stream
              </h2>

              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                {detections.length} events in memory (newest first)
              </span>
            </div>

            {detections.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '64px 20px', color: '#64748b' }}>
                <div style={{ display: 'inline-flex', padding: '16px', background: '#0b1329', borderRadius: '50%', marginBottom: '16px', border: '1px solid #1e293b' }}>
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" strokeWidth="1.5">
                    <path d="M4.9 19.1C1.9 16.1 1.9 11.3 4.9 8.3"></path>
                    <path d="M7.8 16.2c-1.6-1.6-1.6-4.1 0-5.7"></path>
                    <circle cx="12" cy="12" r="2"></circle>
                    <path d="M16.2 10.5c1.6 1.6 1.6 4.1 0 5.7"></path>
                    <path d="M19.1 7.6c3 3 3 7.8 0 10.8"></path>
                  </svg>
                </div>
                <p style={{ margin: 0, fontSize: '1.1rem', color: '#cbd5e1', fontWeight: '600' }}>
                  Waiting for live network traffic...
                </p>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '6px', maxWidth: '420px', marginInLine: 'auto' }}>
                  {pipelineStatus === 'running'
                    ? 'Capture pipeline is running. Real-time network detections will stream here automatically as network flows complete.'
                    : 'Click "Start Capture" above to initiate live network packet sniffing.'}
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="soc-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1e293b', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <th style={{ padding: '12px 16px' }}>Timestamp</th>
                      <th style={{ padding: '12px 16px' }}>Prediction</th>
                      <th style={{ padding: '12px 16px' }}>Confidence</th>
                      <th style={{ padding: '12px 16px' }}>Risk Score</th>
                      <th style={{ padding: '12px 16px' }}>Risk Level</th>
                      <th style={{ padding: '12px 16px' }}>Source IP / Port</th>
                      <th style={{ padding: '12px 16px' }}>Destination IP / Port</th>
                      <th style={{ padding: '12px 16px' }}>Protocol</th>
                      <th style={{ padding: '12px 16px' }}>Packets</th>
                      <th style={{ padding: '12px 16px' }}>Duration</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detections.map((row, idx) => {
                      const isThreat = row.prediction && row.prediction !== 'BENIGN';
                      return (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: '1px solid #1e293b',
                            color: '#e2e8f0',
                            fontSize: '0.85rem',
                            background: isThreat ? 'rgba(255, 23, 68, 0.03)' : 'transparent',
                            cursor: 'pointer',
                          }}
                          onClick={() => setSelectedDetection(row)}
                        >
                          <td style={{ padding: '12px 16px', color: '#94a3b8', fontFamily: 'monospace' }}>
                            {formatTime(row.timestamp)}
                          </td>
                          <td style={{ padding: '12px 16px', fontWeight: '700', color: row.prediction === 'BENIGN' ? '#00e676' : '#ff5252' }}>
                            {row.prediction || 'UNKNOWN'}
                          </td>
                          <td style={{ padding: '12px 16px', color: '#00e5ff' }}>
                            {formatConfidence(row.confidence)}
                          </td>
                          <td style={{ padding: '12px 16px', fontWeight: '600' }}>
                            {row.risk_score !== undefined ? row.risk_score.toFixed(2) : '—'}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span className={`risk-badge ${getRiskBadgeClass(row.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '700' }}>
                              {row.risk_level || 'LOW'}
                            </span>
                          </td>
                          <td style={{ padding: '12px 16px', fontFamily: 'monospace', color: '#cbd5e1' }}>
                            {row.source_ip || '—'}:{row.source_port ?? '—'}
                          </td>
                          <td style={{ padding: '12px 16px', fontFamily: 'monospace', color: '#cbd5e1' }}>
                            {row.destination_ip || '—'}:{row.destination_port ?? '—'}
                          </td>
                          <td style={{ padding: '12px 16px', textTransform: 'uppercase', color: '#94a3b8' }}>
                            {row.protocol || '—'}
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            {row.packet_count ?? '—'}
                          </td>
                          <td style={{ padding: '12px 16px', color: '#94a3b8' }}>
                            {formatDuration(row.flow_duration_us)}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedDetection(row);
                              }}
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
                              Details
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

          {/* Detection Detail Modal */}
          {selectedDetection && (
            <div
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(6, 11, 19, 0.85)',
                backdropFilter: 'blur(6px)',
                zIndex: 1000,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '20px',
              }}
              onClick={() => setSelectedDetection(null)}
            >
              <div
                style={{
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '16px',
                  width: '100%',
                  maxWidth: '650px',
                  maxHeight: '90vh',
                  overflowY: 'auto',
                  padding: '24px',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)',
                  color: '#f8fafc',
                }}
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #1e293b', paddingBottom: '12px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#00e5ff', fontWeight: '700' }}>
                      Real-Time Detection Details
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                      {formatTime(selectedDetection.timestamp)}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedDetection(null)}
                    style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.5rem', cursor: 'pointer' }}
                  >
                    ×
                  </button>
                </div>

                {/* Grid Details */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '24px' }}>
                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Prediction</span>
                    <strong style={{ fontSize: '1.1rem', color: selectedDetection.prediction === 'BENIGN' ? '#00e676' : '#ff1744' }}>
                      {selectedDetection.prediction || '—'}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Confidence</span>
                    <strong style={{ fontSize: '1.1rem', color: '#00e5ff' }}>
                      {formatConfidence(selectedDetection.confidence)}
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Risk Score</span>
                    <strong style={{ fontSize: '1.1rem', color: '#f8fafc' }}>
                      {selectedDetection.risk_score !== undefined ? selectedDetection.risk_score.toFixed(2) : '—'} / 100
                    </strong>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Risk Level</span>
                    <span className={`risk-badge ${getRiskBadgeClass(selectedDetection.risk_level)}`} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '700', display: 'inline-block', marginTop: '4px' }}>
                      {selectedDetection.risk_level || 'LOW'}
                    </span>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Source Sockets</span>
                    <span style={{ fontSize: '0.9rem', fontFamily: 'monospace', color: '#cbd5e1' }}>
                      {selectedDetection.source_ip || '—'}:{selectedDetection.source_port ?? '—'}
                    </span>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Destination Sockets</span>
                    <span style={{ fontSize: '0.9rem', fontFamily: 'monospace', color: '#cbd5e1' }}>
                      {selectedDetection.destination_ip || '—'}:{selectedDetection.destination_port ?? '—'}
                    </span>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Protocol / Packets</span>
                    <span style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
                      {(selectedDetection.protocol || '—').toUpperCase()} ({selectedDetection.packet_count ?? 0} pkts)
                    </span>
                  </div>

                  <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block' }}>Flow Duration</span>
                    <span style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
                      {formatDuration(selectedDetection.flow_duration_us)}
                    </span>
                  </div>
                </div>

                {/* Additional Metrics */}
                <div style={{ background: '#0b1329', padding: '14px', borderRadius: '8px', border: '1px solid #1e293b', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
                    <span style={{ color: '#94a3b8' }}>Attack Severity Score</span>
                    <strong style={{ color: selectedDetection.attack_severity > 50 ? '#ffb300' : '#f8fafc' }}>
                      {selectedDetection.attack_severity ?? 0}
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                    <span style={{ color: '#94a3b8' }}>Anomaly Score</span>
                    <strong style={{ color: selectedDetection.anomaly_score > 0 ? '#ffb300' : '#00e676' }}>
                      {selectedDetection.anomaly_score !== undefined ? selectedDetection.anomaly_score.toFixed(4) : '—'}
                    </strong>
                  </div>
                </div>

                {/* Modal Footer Actions */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                  <button
                    type="button"
                    onClick={() => setSelectedDetection(null)}
                    style={{ background: '#1e293b', color: '#cbd5e1', border: '1px solid #334155', borderRadius: '8px', padding: '8px 16px', cursor: 'pointer', fontWeight: '600' }}
                  >
                    Close
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const det = selectedDetection;
                      setSelectedDetection(null);
                      navigate('/detection-details', { state: { detection: det } });
                    }}
                    style={{ background: 'linear-gradient(135deg, #00e5ff 0%, #00b0ff 100%)', color: '#090d16', border: 'none', borderRadius: '8px', padding: '8px 16px', cursor: 'pointer', fontWeight: '700' }}
                  >
                    View Full AI Analysis
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default RealtimeMonitor;
