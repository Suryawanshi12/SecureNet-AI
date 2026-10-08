import React from 'react';
import { clearAuth } from '../../auth/authUtils';
import { useNavigate, useLocation } from 'react-router-dom';

const ShieldLogo = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
  </svg>
);

const DashboardIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="9" rx="1"></rect>
    <rect x="14" y="3" width="7" height="5" rx="1"></rect>
    <rect x="14" y="12" width="7" height="9" rx="1"></rect>
    <rect x="3" y="16" width="7" height="5" rx="1"></rect>
  </svg>
);

const ActivityIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const AlertShieldIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12.01" y2="16"></line>
  </svg>
);

const EyeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const FileTextIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);

const RadioIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.9 19.1C1.9 16.1 1.9 11.3 4.9 8.3"></path>
    <path d="M7.8 16.2c-1.6-1.6-1.6-4.1 0-5.7"></path>
    <circle cx="12" cy="12" r="2"></circle>
    <path d="M16.2 10.5c1.6 1.6 1.6 4.1 0 5.7"></path>
    <path d="M19.1 7.6c3 3 3 7.8 0 10.8"></path>
  </svg>
);

const SettingsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
  </svg>
);

const LogOutIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16 17 21 12 16 7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  </svg>
);

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon, path: '/dashboard' },
  { id: 'traffic', label: 'Traffic Analysis', icon: ActivityIcon, path: '/traffic-analysis' },
  { id: 'threats', label: 'Threat Detection', icon: AlertShieldIcon, path: '/threat-detection' },
  { id: 'anomalies', label: 'Anomaly Monitoring', icon: EyeIcon, path: '/anomaly-monitoring' },
  { id: 'realtime', label: 'Real-Time Monitor', icon: RadioIcon, path: '/realtime-monitor' },
  { id: 'details', label: 'Detection Details', icon: FileTextIcon, path: '/detection-details' },
  { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' },
];

const Sidebar = ({ isOpen, onClose, user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    clearAuth();
    navigate('/login', { replace: true });
  };

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
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={onClose} 
          aria-hidden="true"
        />
      )}

      <aside className={`soc-sidebar ${isOpen ? 'open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-icon-box">
            <ShieldLogo />
          </div>
          <div className="brand-text-box">
            <span className="brand-title">SecureNet AI</span>
            <span className="brand-tagline">SOC Platform</span>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="sidebar-nav">
          <div className="nav-group-label">NAVIGATION</div>
          {navItems.map((item) => {
            const IconComp = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.id}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => {
                  if (onClose) onClose();
                  if (item.path) navigate(item.path);
                }}
                type="button"
              >
                <span className="nav-icon">
                  <IconComp />
                </span>
                <span className="nav-label">{item.label}</span>
                {isActive && <span className="nav-active-indicator" />}
              </button>
            );
          })}
        </nav>

        {/* User Profile & Logout Bottom Section */}
        <div className="sidebar-footer">
          <div className="user-profile-card">
            <div className="user-avatar">
              {getInitials(user?.full_name)}
            </div>
            <div className="user-info">
              <span className="user-name">{user?.full_name || 'Security User'}</span>
              <span className="user-email">{user?.email || 'admin@securenet.ai'}</span>
            </div>
          </div>

          <button 
            type="button" 
            className="sidebar-logout-btn" 
            onClick={handleLogout}
            title="Logout"
          >
            <LogOutIcon />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
