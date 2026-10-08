import React, { useEffect, useState } from 'react';
import { getRecentDetections } from '../../api/authApi';

const RISK_COLORS = {
  LOW:      '#00e676',
  MEDIUM:   '#ffb300',
  HIGH:     '#ff9100',
  CRITICAL: '#ff1744',
};

const formatTime = (isoStr) => {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return isoStr;
  }
};

const RecentDetections = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getRecentDetections()
      .then((res) => {
        setRows(res.data || []);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  return (
    <div className="soc-panel detections-panel">
      <div className="panel-header">
        <h2 className="panel-title">Recent Detections</h2>
        <span className="panel-badge">
          {loading ? 'Loading...' : rows.length > 0 ? `Latest ${rows.length}` : 'Live Stream'}
        </span>
      </div>

      <div className="panel-body table-container-wrapper">
        {loading && (
          <div className="status-loading-box" style={{ padding: '2.5rem' }}>
            <div className="spinner-small" />
            <span>Loading security data...</span>
          </div>
        )}

        {error && !loading && (
          <div className="table-empty-state" style={{ padding: '2.5rem' }}>
            <span>⚠️</span>
            <p className="empty-message">Unable to load security data.</p>
          </div>
        )}

        {!loading && !error && (
          <div className="table-responsive">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                  <th>Severity</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="table-empty-cell">
                      <div className="table-empty-state">
                        <span>🛡️</span>
                        <p className="empty-message">No recent detections.</p>
                        <p className="empty-subtext">
                          Network flow evaluation results will appear here in real time.
                        </p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  rows.map((row) => {
                    const riskColor = RISK_COLORS[row.risk_level] || '#8b9bb4';
                    return (
                      <tr key={row.id}>
                        <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#8b9bb4' }}>
                          {formatTime(row.timestamp)}
                        </td>
                        <td style={{ fontWeight: 600 }}>{row.prediction}</td>
                        <td>{row.confidence.toFixed(2)}%</td>
                        <td>{row.attack_severity}</td>
                        <td>{row.risk_score.toFixed(2)}</td>
                        <td>
                          <span
                            style={{
                              color: riskColor,
                              background: `${riskColor}18`,
                              border: `1px solid ${riskColor}50`,
                              padding: '0.2rem 0.55rem',
                              borderRadius: '5px',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                            }}
                          >
                            {row.risk_level}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentDetections;
