import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../../components/auth/AuthLayout';
import AuthInput from '../../components/auth/AuthInput';
import PasswordInput from '../../components/auth/PasswordInput';
import { registerUser } from '../../api/authApi';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    if (apiError) setApiError('');
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    if (!formData.agreeTerms) {
      newErrors.agreeTerms = 'You must agree to the Terms and Conditions';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setApiError('');
    setSuccessMsg('');

    try {
      await registerUser({
        full_name: formData.fullName,
        email: formData.email,
        password: formData.password,
      });

      setSuccessMsg('Account created! Redirecting to login...');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
    } catch (error) {
      const rawDetail = error.response?.data?.detail;
      let msg = 'Registration failed. Please try again.';
      if (typeof rawDetail === 'string') {
        msg = rawDetail;
      } else if (Array.isArray(rawDetail)) {
        msg = rawDetail.map(err => err.msg || JSON.stringify(err)).join(', ');
      } else if (rawDetail) {
        msg = JSON.stringify(rawDetail);
      }
      setApiError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-card">
        <div className="auth-header-mobile-brand">
          <div className="auth-brand-logo" style={{ width: '24px', height: '24px' }}></div>
          <span className="auth-brand-name" style={{ fontSize: '1.25rem' }}>SecureNet AI</span>
        </div>

        <div className="auth-header">
          <h2 className="auth-title">Create your account</h2>
          <p className="auth-subtitle">Start monitoring your network with SecureNet AI.</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <AuthInput 
            label="Full Name"
            id="fullName"
            name="fullName"
            type="text"
            placeholder="John Doe"
            value={formData.fullName}
            onChange={handleChange}
            error={errors.fullName}
            autoComplete="name"
          />

          <AuthInput 
            label="Email"
            id="email"
            name="email"
            type="email"
            placeholder="admin@securenet.ai"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            autoComplete="email"
          />
          
          <PasswordInput
            label="Password"
            id="password"
            name="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            showStrength={true}
            autoComplete="new-password"
          />

          <PasswordInput
            label="Confirm Password"
            id="confirmPassword"
            name="confirmPassword"
            placeholder="••••••••"
            value={formData.confirmPassword}
            onChange={handleChange}
            error={errors.confirmPassword}
            autoComplete="new-password"
          />

          <div className="auth-options" style={{ marginTop: '0.25rem' }}>
            <label className="checkbox-label" style={{ alignItems: 'flex-start' }}>
              <input 
                type="checkbox" 
                name="agreeTerms"
                checked={formData.agreeTerms}
                onChange={handleChange}
                style={{ marginTop: '0.25rem' }}
              />
              <span style={{ lineHeight: '1.4' }}>
                I agree to the <a href="#">Terms and Conditions</a> and <a href="#">Privacy Policy</a>
              </span>
            </label>
          </div>
          {errors.agreeTerms && <span className="input-error-msg" style={{ marginTop: '-0.5rem' }}>{errors.agreeTerms}</span>}

          {apiError && (
            <div style={{
              background: 'rgba(255,23,68,0.1)',
              border: '1px solid rgba(255,23,68,0.4)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: '#ff1744',
              fontSize: '0.875rem',
            }}>
              {apiError}
            </div>
          )}

          {successMsg && (
            <div style={{
              background: 'rgba(0,230,118,0.1)',
              border: '1px solid rgba(0,230,118,0.4)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: '#00e676',
              fontSize: '0.875rem',
            }}>
              {successMsg}
            </div>
          )}

          <button 
            type="submit" 
            className={`auth-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? '' : 'Register'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Register;
