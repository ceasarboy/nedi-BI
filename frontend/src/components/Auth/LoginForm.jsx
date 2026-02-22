import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginForm = ({ onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '100%' }}>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '0.5rem', 
            fontWeight: '500',
            color: '#374151',
            fontSize: '0.875rem'
          }}>
            用户名
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid #e5e7eb',
              borderRadius: '10px',
              fontSize: '1rem',
              background: '#ffffff',
              color: '#111827',
              transition: 'all 200ms ease',
              outline: 'none'
            }}
            placeholder="请输入用户名"
            onFocus={(e) => {
              e.target.style.borderColor = '#2563eb';
              e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e5e7eb';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '0.5rem', 
            fontWeight: '500',
            color: '#374151',
            fontSize: '0.875rem'
          }}>
            密码
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              border: '1px solid #e5e7eb',
              borderRadius: '10px',
              fontSize: '1rem',
              background: '#ffffff',
              color: '#111827',
              transition: 'all 200ms ease',
              outline: 'none'
            }}
            placeholder="请输入密码"
            onFocus={(e) => {
              e.target.style.borderColor = '#2563eb';
              e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e5e7eb';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
        {error && (
          <div style={{
            color: '#dc2626',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            padding: '0.875rem 1rem',
            borderRadius: '10px',
            marginBottom: '1.5rem',
            fontSize: '0.875rem'
          }}>
            {error}
          </div>
        )}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '0.875rem 1.5rem',
            background: loading ? '#93c5fd' : 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 200ms ease',
            boxShadow: loading ? 'none' : '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
          }}
        >
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <p style={{ color: '#6b7280', fontSize: '0.9375rem', margin: '0' }}>
          还没有账号？{' '}
          <button
            onClick={onSwitchToRegister}
            style={{
              background: 'none',
              border: 'none',
              color: '#2563eb',
              cursor: 'pointer',
              fontSize: '0.9375rem',
              fontWeight: '600',
              textDecoration: 'none'
            }}
          >
            立即注册
          </button>
        </p>
        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem 1.25rem', 
          backgroundColor: '#f9fafb', 
          borderRadius: '12px',
          border: '1px solid #e5e7eb'
        }}>
          <p style={{ fontSize: '0.875rem', color: '#4b5563', margin: '0', lineHeight: '1.6' }}>
            <strong style={{ color: '#111827' }}>内置管理员账号：</strong><br />
            用户名：admin<br />
            密码：admin123
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
