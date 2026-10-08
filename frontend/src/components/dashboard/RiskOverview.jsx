import React, { useEffect, useState } from 'react';
import { getRiskDistribution } from '../../api/authApi';

const riskMeta = [
  { level: 'LOW',      color: '#00e676', range: '0 – 25',  desc: 'Normal traffic activity' },
  { level: 'MEDIUM',   color: '#ffb300', range: '26 – 50', desc: 'Low-severity anomaly' },
  { level: 'HIGH',     color: '#ff9100', range: '51 – 75', desc: 'High-risk intrusion' },
  { level: 'CRITICAL', color: '#ff1744', range: '76 – 100',desc: 'Severe threat detected' },
];

const RiskOverview = () => {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getRiskDistribution()
      .then((res) => {
        const map = {};
        (res.data || []).forEach((item) => {
          map[item.risk_level] = item.count;
        });
        setData(map);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  const displayValue = (level) => {
    if (loading) return '…';
    if (error) return '—';
    return (data[level] ?? 0).toLocaleString();
  };

  return (
    <div className="soc-panel risk-overview-panel">
      <div className="panel-header">
        <h2 className="panel-title">Risk Overview</h2>
        <span className="panel-badge">Risk Scoring V2</span>
      </div>

      <div className="panel-body">
        {loading ? (
          <div className="status-loading-box">
            <div className="spinner-small" />
            <span>Loading security data...</span>
          </div>
        ) : (
          <div className="risk-grid">
            {riskMeta.map((item) => (
              <div
                key={item.level}
                className="risk-card"
                style={{ borderColor: `${item.color}35` }}
              >
                <div className="risk-card-top">
                  <span
                    className="risk-badge"
                    style={{
                      color: item.color,
                      background: `${item.color}15`,
                      borderColor: `${item.color}40`,
                    }}
                  >
                    {item.level}
                  </span>
                  <span className="risk-range">Score {item.range}</span>
                </div>
                <div className="risk-card-count">{displayValue(item.level)}</div>
                <div className="risk-card-desc">{item.desc}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskOverview;
