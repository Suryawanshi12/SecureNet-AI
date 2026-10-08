import React, { useState } from 'react';

const EyeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const EyeOffIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>
);

const PasswordInput = ({ label, id, error, showStrength, value, ...props }) => {
  const [showPassword, setShowPassword] = useState(false);

  const calculateStrength = (password) => {
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
  };

  const strength = showStrength ? calculateStrength(value || '') : 0;

  const getStrengthText = () => {
    switch(strength) {
      case 0: return '';
      case 1: return 'Weak';
      case 2: return 'Fair';
      case 3: return 'Good';
      case 4: return 'Strong';
      default: return '';
    }
  };

  return (
    <div className="input-group">
      <label htmlFor={id} className="input-label">{label}</label>
      <div className="input-wrapper">
        <input 
          id={id}
          type={showPassword ? 'text' : 'password'}
          className={`input-field has-icon-right ${error ? 'error' : ''}`}
          value={value}
          {...props}
        />
        <button 
          type="button"
          className="password-toggle"
          onClick={() => setShowPassword(!showPassword)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? <EyeOffIcon /> : <EyeIcon />}
        </button>
      </div>
      
      {showStrength && value && (
        <div className="password-strength">
          <div className="strength-bar-container">
            <div className={`strength-bar ${strength >= 1 ? 'active-weak' : ''}`}></div>
            <div className={`strength-bar ${strength >= 2 ? 'active-fair' : ''}`}></div>
            <div className={`strength-bar ${strength >= 3 ? 'active-good' : ''}`}></div>
            <div className={`strength-bar ${strength >= 4 ? 'active-strong' : ''}`}></div>
          </div>
          <div className="strength-text">{getStrengthText()}</div>
        </div>
      )}
      
      {error && <span className="input-error-msg">{error}</span>}
    </div>
  );
};

export default PasswordInput;
