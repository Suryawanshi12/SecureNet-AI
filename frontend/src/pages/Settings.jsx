import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getHealth, getModelInfo } from '../api/authApi';
import { clearAuth, getUser } from '../auth/authUtils';

import Sidebar from '../components/dashboard/Sidebar';
import Topbar from '../components/dashboard/Topbar';

import '../components/dashboard/dashboard.css';

const Settings = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Profile loading & error state
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState(null);

  // System health & model info state
  const [healthStatus, setHealthStatus] = useState({ loading: true, online: false, error: false });
  const [modelInfo, setModelInfo] = useState({ loading: true, data: null, error: false });

  // Notification preference (frontend state)
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  useEffect(() => {
    // 1. Fetch authenticated user profile via /auth/me
    getMe()
      .then((res) => {
        setUser(res.data);
        setProfileLoading(false);
      })
      .catch(() => {
        setProfileError('Unable to load profile.');
        setProfileLoading(false);
      });

    // 2. Fetch backend system health via /health
    getHealth()
      .then((res) => {
        const isHealthy = res.data?.status === 'healthy';
        setHealthStatus({ loading: false, online: isHealthy, error: !isHealthy });
      })
      .catch(() => {
        setHealthStatus({ loading: false, online: false, error: true });
      });

    // 3. Fetch model information via /model-info
    getModelInfo()
      .then((res) => {
        setModelInfo({ loading: false, data: res.data, error: false });
      })
      .catch(() => {
        setModelInfo({ loading: false, data: null, error: true });
      });
  }, []);

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
    <div className="soc-dashboard-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />

      <div className="soc-main-layout">
        <Topbar onToggleSidebar={() => setSidebarOpen((p) => !p)} user={user} />

        <main className="soc-content">
          {/* Page Header */}
          <header className="page-header" style={{ marginBottom: '24px' }}>
            <h1 className="page-title" style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff', margin: 0 }}>
              Settings
            </h1>
            <p className="page-subtitle" style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '4px' }}>
              Manage your SecureNet AI profile and account settings.
            </p>
          </header>

          {/* Two Column Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', alignItems: 'start' }}>
            
            {/* LEFT COLUMN */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              
              {/* SECTION 1: PROFILE */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  Profile
                </h2>

                {profileLoading ? (
                  <div style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                    Loading profile...
                  </div>
                ) : profileError ? (
                  <div style={{ padding: '16px', background: 'rgba(255, 23, 68, 0.1)', border: '1px solid #ff1744', borderRadius: '8px', color: '#ff5252', fontSize: '0.875rem' }}>
                    {profileError}
                  </div>
                ) : (
                  <div>
                    {/* User Avatar Badge Header */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px', padding: '12px', background: '#0b1329', borderRadius: '10px', border: '1px solid #1e293b' }}>
                      <div
                        style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #00e5ff 0%, #00b0ff 100%)',
                          color: '#090d16',
                          fontWeight: '800',
                          fontSize: '1.2rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        {getInitials(user?.full_name)}
                      </div>
                      <div>
                        <h3 style={{ margin: 0, color: '#f8fafc', fontSize: '1.1rem', fontWeight: '600' }}>
                          {user?.full_name || 'Security Analyst'}
                        </h3>
                        <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{user?.email}</span>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Full Name</span>
                        <strong style={{ color: '#f8fafc', fontSize: '0.9rem' }}>{user?.full_name || '—'}</strong>
                      </div>

                      <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Role</span>
                        <strong style={{ color: '#00e5ff', fontSize: '0.9rem', textTransform: 'capitalize' }}>{user?.role || 'User'}</strong>
                      </div>

                      <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: 'span 2' }}>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Email Address</span>
                        <span style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>{user?.email || '—'}</span>
                      </div>

                      {user?.id !== undefined && (
                        <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: 'span 2' }}>
                          <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Account ID</span>
                          <span style={{ color: '#cbd5e1', fontSize: '0.85rem', fontFamily: 'monospace' }}>#{user.id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 2 & 3: ACCOUNT INFORMATION & SECURITY */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  Account & Security
                </h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Authentication Status</span>
                    <span style={{ color: '#00e676', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#00e676' }} />
                      Authenticated
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Account Status</span>
                    <span style={{ color: '#00e5ff', fontWeight: '700', fontSize: '0.85rem' }}>Active</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Auth Token Type</span>
                    <span style={{ color: '#cbd5e1', fontSize: '0.85rem', fontFamily: 'monospace' }}>Bearer JWT</span>
                  </div>
                </div>

                {/* Password Change Button (Disabled as per instructions) */}
                <div style={{ background: '#0b1329', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                    <div>
                      <strong style={{ color: '#f8fafc', fontSize: '0.9rem', display: 'block' }}>Change Password</strong>
                      <span style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '2px', display: 'block' }}>
                        Password change is not currently available.
                      </span>
                    </div>
                    <button
                      type="button"
                      disabled
                      style={{
                        padding: '8px 16px',
                        background: '#1e293b',
                        color: '#64748b',
                        border: '1px solid #334155',
                        borderRadius: '6px',
                        cursor: 'not-allowed',
                        fontSize: '0.8rem',
                        fontWeight: '600',
                      }}
                    >
                      Change Password
                    </button>
                  </div>
                </div>
              </div>

              {/* SECTION 4: CURRENT SESSION & LOGOUT */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  Current Session
                </h2>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <div>
                    <strong style={{ color: '#f8fafc', fontSize: '0.9rem', display: 'block' }}>Active Session</strong>
                    <span style={{ color: '#94a3b8', fontSize: '0.8rem', marginTop: '2px', display: 'block' }}>
                      Logged in as {user?.email}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleLogout}
                    style={{
                      padding: '10px 20px',
                      background: 'rgba(255, 23, 68, 0.15)',
                      color: '#ff1744',
                      border: '1px solid rgba(255, 23, 68, 0.4)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '700',
                      fontSize: '0.85rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                      <polyline points="16 17 21 12 16 7"></polyline>
                      <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    Logout
                  </button>
                </div>
              </div>

            </div>

            {/* RIGHT COLUMN */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              
              {/* SECTION 5: APPLICATION INFORMATION */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                  </svg>
                  About SecureNet AI
                </h2>

                {modelInfo.loading ? (
                  <div style={{ textAlign: 'center', padding: '20px', color: '#94a3b8' }}>
                    Loading model information...
                  </div>
                ) : modelInfo.error ? (
                  <div style={{ padding: '12px', background: 'rgba(255, 23, 68, 0.1)', border: '1px solid #ff1744', borderRadius: '8px', color: '#ff5252', fontSize: '0.85rem' }}>
                    Unable to load model information.
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: 'span 2' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>System Title</span>
                      <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>SecureNet AI Platform</strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Supervised Model</span>
                      <strong style={{ color: '#00e5ff', fontSize: '0.85rem' }}>
                        {modelInfo.data?.supervised_model || 'XGBoost Model 5'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Anomaly Detection</span>
                      <strong style={{ color: '#ffb300', fontSize: '0.85rem' }}>
                        {modelInfo.data?.anomaly_model || 'Isolation Forest V3'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Explainability</span>
                      <strong style={{ color: '#00e676', fontSize: '0.85rem' }}>
                        {modelInfo.data?.explainability || 'SHAP'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Scoring</span>
                      <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>
                        {modelInfo.data?.risk_scoring || 'Risk Scoring V2'}
                      </strong>
                    </div>

                    <div style={{ background: '#0b1329', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: 'span 2' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '4px' }}>Monitored Classes</span>
                      <strong style={{ color: '#f8fafc', fontSize: '0.85rem' }}>
                        {modelInfo.data?.classes ? `${modelInfo.data.classes} Network Attack Taxonomy Classes` : '15 Classes'}
                      </strong>
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 6: SYSTEM STATUS */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                  System Status
                </h2>

                {healthStatus.loading ? (
                  <div style={{ textAlign: 'center', padding: '20px', color: '#94a3b8' }}>
                    Checking system status...
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                      <span style={{ color: '#f8fafc', fontSize: '0.875rem' }}>Backend API</span>
                      <span style={{ color: healthStatus.online ? '#00e676' : '#ff5252', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: healthStatus.online ? '#00e676' : '#ff5252' }} />
                        {healthStatus.online ? 'Online' : 'Backend API unavailable'}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                      <span style={{ color: '#f8fafc', fontSize: '0.875rem' }}>ML Pipeline</span>
                      <span style={{ color: healthStatus.online ? '#00e676' : '#ffb300', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: healthStatus.online ? '#00e676' : '#ffb300' }} />
                        {healthStatus.online ? 'Pipeline Available' : 'Standby'}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                      <span style={{ color: '#f8fafc', fontSize: '0.875rem' }}>Authentication Service</span>
                      <span style={{ color: '#00e676', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#00e676' }} />
                        Authentication Active
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 7: PREFERENCES */}
              <div className="soc-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: '#00e5ff', fontSize: '1.1rem', fontWeight: '600', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                  </svg>
                  Preferences
                </h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                    <span style={{ color: '#f8fafc', fontSize: '0.875rem' }}>Active UI Theme</span>
                    <span style={{ color: '#00e5ff', fontWeight: '600', fontSize: '0.85rem' }}>Dark SOC Theme</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#0b1329', borderRadius: '8px', border: '1px solid #1e293b', alignItems: 'center' }}>
                    <div>
                      <span style={{ color: '#f8fafc', fontSize: '0.875rem', display: 'block' }}>Session Notifications</span>
                      <span style={{ color: '#64748b', fontSize: '0.75rem' }}>(Frontend session preference)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setNotificationsEnabled((prev) => !prev)}
                      style={{
                        padding: '6px 12px',
                        background: notificationsEnabled ? 'rgba(0, 230, 118, 0.15)' : '#1e293b',
                        color: notificationsEnabled ? '#00e676' : '#94a3b8',
                        border: notificationsEnabled ? '1px solid rgba(0, 230, 118, 0.3)' : '1px solid #334155',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        fontWeight: '600',
                      }}
                    >
                      {notificationsEnabled ? 'Enabled' : 'Disabled'}
                    </button>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </main>
      </div>
    </div>
  );
};

export default Settings;
