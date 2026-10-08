import React from 'react';

const MenuIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="12" x2="21" y2="12"></line>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <line x1="3" y1="18" x2="21" y2="18"></line>
  </svg>
);

const BellIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
  </svg>
);

const ActivityIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const Topbar = ({ onToggleSidebar, user }) => {
  const getInitials = (name) => {
    if (!name) return 'SU';
    return name
      .split(' ')
      .map((part) => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <header className="soc-topbar">
      <div className="topbar-left">
        <button 
          className="mobile-toggle-btn" 
          onClick={onToggleSidebar}
          aria-label="Toggle Navigation"
          type="button"
        >
          <MenuIcon />
        </button>

        <div className="topbar-titles">
          <h1 className="topbar-title">Network Security Dashboard</h1>
          <p className="topbar-subtitle">Real-time network intrusion and anomaly monitoring</p>
        </div>
      </div>

      <div className="topbar-right">
        {/* Quick Action Button */}
        <button 
          type="button" 
          className="quick-action-btn"
          onClick={() => {
            // Visually ready for future integration
          }}
        >
          <ActivityIcon />
          <span>Analyze Network Traffic</span>
        </button>

        {/* Notifications Icon */}
        <div className="topbar-icon-badge" title="Notifications">
          <BellIcon />
          <span className="badge-dot" />
        </div>

        {/* User Pill */}
        <div className="topbar-user-pill">
          <div className="user-avatar-small">
            {getInitials(user?.full_name)}
          </div>
          <div className="user-meta">
            <span className="user-meta-name">{user?.full_name || 'Security Analyst'}</span>
            <span className="user-meta-role">{user?.role ? user.role.toUpperCase() : 'USER'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
