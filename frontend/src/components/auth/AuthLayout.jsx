import React from 'react';

const ShieldIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
  </svg>
);

const ActivityIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const CpuIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
    <rect x="9" y="9" width="6" height="6"></rect>
    <line x1="9" y1="1" x2="9" y2="4"></line>
    <line x1="15" y1="1" x2="15" y2="4"></line>
    <line x1="9" y1="20" x2="9" y2="23"></line>
    <line x1="15" y1="20" x2="15" y2="23"></line>
    <line x1="20" y1="9" x2="23" y2="9"></line>
    <line x1="20" y1="14" x2="23" y2="14"></line>
    <line x1="1" y1="9" x2="4" y2="9"></line>
    <line x1="1" y1="14" x2="4" y2="14"></line>
  </svg>
);

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-container">
      {/* Left Sidebar */}
      <div className="auth-sidebar">
        <div className="auth-sidebar-glow"></div>
        <div className="auth-brand">
          <div className="auth-brand-logo"></div>
          <span className="auth-brand-name">SecureNet AI</span>
        </div>
        <h1 className="auth-sidebar-title">AI-Powered Network Security</h1>
        <p className="auth-sidebar-desc">
          Detect known attacks, identify anomalous network behavior, and understand every security decision with explainable AI.
        </p>
        
        <div className="auth-features">
          <div className="feature-item">
            <div className="feature-icon"><ShieldIcon /></div>
            <span className="feature-text">AI Threat Detection</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><ActivityIcon /></div>
            <span className="feature-text">Real-Time Anomaly Monitoring</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><CpuIcon /></div>
            <span className="feature-text">Explainable AI with SHAP</span>
          </div>
        </div>
      </div>

      {/* Right Content */}
      <div className="auth-content">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
