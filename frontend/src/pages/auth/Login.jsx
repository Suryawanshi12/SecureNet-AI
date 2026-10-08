import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../../components/auth/AuthLayout';
import AuthInput from '../../components/auth/AuthInput';
import PasswordInput from '../../components/auth/PasswordInput';
import { loginUser } from '../../api/authApi';
import { saveAuth } from '../../auth/authUtils';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
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
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setApiError('');

    try {
      const response = await loginUser({
        email: formData.email,
        password: formData.password,
      });

      const { access_token, user } = response.data;
      saveAuth(access_token, user);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      const rawDetail = error.response?.data?.detail;
      let msg = 'Login failed. Please check your credentials.';
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
          <h2 className="auth-title">Welcome Back</h2>
          <p className="auth-subtitle">Sign in to monitor and secure your network.</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
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
            autoComplete="current-password"
          />

          <div className="auth-options">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                name="rememberMe"
                checked={formData.rememberMe}
                onChange={handleChange}
              />
              Remember me
            </label>
            <a href="#" className="forgot-link">Forgot password?</a>
          </div>

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

          <button 
            type="submit" 
            className={`auth-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? '' : 'Sign in'}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Create one</Link>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Login;
