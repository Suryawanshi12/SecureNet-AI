import React from 'react';

const StatCard = ({ title, value = '—', icon: Icon, badgeText = 'No data available yet', iconColor = '#00e5ff' }) => {
  return (
    <div className="soc-stat-card">
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        <div className="stat-card-icon" style={{ color: iconColor, background: `${iconColor}15` }}>
          {Icon && <Icon />}
        </div>
      </div>
      <div className="stat-card-body">
        <div className="stat-card-value">{value}</div>
      </div>
      <div className="stat-card-footer">
        <span className="stat-card-badge">{badgeText}</span>
      </div>
    </div>
  );
};

export default StatCard;
