import React, { useEffect, useState } from 'react';
import { getThreatDistribution } from '../../api/authApi';

const attackCategories = [
  'BENIGN', 'DDoS', 'DoS Hulk', 'DoS GoldenEye', 'PortScan', 'Bot',
  'FTP-Patator', 'SSH-Patator', 'Web Attack - Brute Force',
  'Web Attack - XSS', 'Web Attack - Sql Injection', 'Infiltration', 'Heartbleed',
  'DoS slowloris', 'DoS Slowhttest',
];

const BAR_COLORS = {
  BENIGN: '#00e676',
  DDoS: '#ff1744',
  'DoS Hulk': '#ff5722',
  'DoS GoldenEye': '#ff9100',
  PortScan: '#ffb300',
  Bot: '#e040fb',
  'FTP-Patator': '#00e5ff',
  'SSH-Patator': '#29b6f6',
  'Web Attack - Brute Force': '#ef5350',
  'Web Attack - XSS': '#ab47bc',
  'Web Attack - Sql Injection': '#ec407a',
  Infiltration: '#ff7043',
  Heartbleed: '#b71c1c',
  'DoS slowloris': '#f57c00',
  'DoS Slowhttest': '#ffa726',
};

const DEFAULT_COLOR = '#8b9bb4';

const ThreatDistribution = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getThreatDistribution()
      .then((res) => {
        setData(res.data || []);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  const maxCount = data.length > 0 ? Math.max(...data.map((d) => d.count), 1) : 1;
  const hasData = data.length > 0;

  return (
    <div className="soc-panel threat-distribution-panel">
      <div className="panel-header">
        <h2 className="panel-title">Threat Distribution</h2>
        <span className="panel-badge">
          {loading ? 'Loading...' : hasData ? `${data.length} classes detected` : 'ML Taxonomy Standby'}
        </span>
      </div>

      <div className="panel-body">
        {loading && (
          <div className="status-loading-box">
            <div className="spinner-small" />
            <span>Loading security data...</span>
          </div>
        )}

        {error && !loading && (
          <div className="empty-state-container">
            <div className="empty-state-icon">⚠️</div>
            <p className="empty-state-message">Unable to load security data.</p>
          </div>
        )}

        {!loading && !error && hasData && (
          <div className="threat-bar-list">
            {data.map((item) => {
              const pct = Math.max((item.count / maxCount) * 100, 4);
              const color = BAR_COLORS[item.prediction] || DEFAULT_COLOR;
              return (
                <div key={item.prediction} className="threat-bar-row">
                  <span className="threat-bar-label">{item.prediction}</span>
                  <div className="threat-bar-track">
                    <div
                      className="threat-bar-fill"
                      style={{ width: `${pct}%`, background: color }}
                    />
                  </div>
                  <span className="threat-bar-count" style={{ color }}>{item.count}</span>
                </div>
              );
            })}
          </div>
        )}

        {!loading && !error && !hasData && (
          <div className="empty-state-container">
            <div className="empty-state-icon">📊</div>
            <p className="empty-state-message">No threat data available yet.</p>
            <p className="empty-state-subtext">
              Threat telemetry will populate here dynamically upon network traffic analysis.
            </p>
            <div className="categories-list-container">
              <span className="categories-list-title">Monitored ML Attack Classes:</span>
              <div className="categories-chips">
                {attackCategories.map((cat) => (
                  <span key={cat} className="category-chip">{cat}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatDistribution;
