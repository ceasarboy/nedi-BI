import React, { useState } from 'react';
import LoginForm from '../components/Auth/LoginForm';
import RegisterForm from '../components/Auth/RegisterForm';

const LoginPage = () => {
  const [mode, setMode] = useState('login');

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
      padding: '2rem'
    }}>
      <div style={{
        display: 'flex',
        width: '100%',
        maxWidth: '1000px',
        backgroundColor: 'white',
        borderRadius: '24px',
        overflow: 'hidden',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        <div style={{
          flex: '1',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '3rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          color: 'white'
        }}>
          <div style={{ marginBottom: '2rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.5rem',
              backdropFilter: 'blur(10px)'
            }}>
              <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>PB</span>
            </div>
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: '700',
              margin: '0 0 1rem 0',
              letterSpacing: '-0.5px'
            }}>
              PB-BI
            </h1>
            <p style={{
              fontSize: '1.125rem',
              opacity: '0.9',
              lineHeight: '1.7',
              margin: '0'
            }}>
              强大的商业数据分析平台<br />
              让数据驱动决策，洞察未来趋势
            </p>
          </div>
          
          <div style={{
            marginTop: 'auto',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1.5rem',
            paddingTop: '2rem'
          }}>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.25rem' }}>99%</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.8' }}>数据准确性</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.25rem' }}>10+</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.8' }}>图表类型</div>
            </div>
          </div>
        </div>

        <div style={{
          flex: '1',
          padding: '3rem',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.875rem',
              fontWeight: '700',
              color: '#111827',
              margin: '0 0 0.5rem 0',
              letterSpacing: '-0.3px'
            }}>
              {mode === 'login' ? '欢迎回来' : '创建账户'}
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: '1rem',
              margin: '0'
            }}>
              {mode === 'login' ? '登录您的账户以继续' : '注册新账户开始使用'}
            </p>
          </div>
          
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ 
              display: 'flex', 
              gap: '0.5rem',
              background: '#f9fafb',
              padding: '0.375rem',
              borderRadius: '12px'
            }}>
              <button
                onClick={() => setMode('login')}
                style={{
                  flex: 1,
                  padding: '0.75rem 1rem',
                  border: 'none',
                  backgroundColor: mode === 'login' ? 'white' : 'transparent',
                  color: mode === 'login' ? '#2563eb' : '#6b7280',
                  cursor: 'pointer',
                  fontSize: '0.9375rem',
                  fontWeight: mode === 'login' ? '600' : '500',
                  borderRadius: '8px',
                  transition: 'all 200ms ease',
                  boxShadow: mode === 'login' ? '0 1px 2px rgba(0, 0, 0, 0.05)' : 'none'
                }}
              >
                登录
              </button>
              <button
                onClick={() => setMode('register')}
                style={{
                  flex: 1,
                  padding: '0.75rem 1rem',
                  border: 'none',
                  backgroundColor: mode === 'register' ? 'white' : 'transparent',
                  color: mode === 'register' ? '#2563eb' : '#6b7280',
                  cursor: 'pointer',
                  fontSize: '0.9375rem',
                  fontWeight: mode === 'register' ? '600' : '500',
                  borderRadius: '8px',
                  transition: 'all 200ms ease',
                  boxShadow: mode === 'register' ? '0 1px 2px rgba(0, 0, 0, 0.05)' : 'none'
                }}
              >
                注册
              </button>
            </div>
          </div>
          
          {mode === 'login' ? (
            <LoginForm onSwitchToRegister={() => setMode('register')} />
          ) : (
            <RegisterForm 
              onSwitchToLogin={() => setMode('login')} 
              onRegisterSuccess={() => setMode('login')}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
