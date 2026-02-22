import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ConfigPage from './pages/ConfigPage'
import DataPage from './pages/DataPage'
import AnalysisPage from './pages/AnalysisPage'
import VisualPage from './pages/VisualPage'
import GuidePage from './pages/GuidePage'
import CorrelationPage from './pages/CorrelationPage'
import MonteCarloPage from './pages/MonteCarloPage'
import LoginPage from './pages/LoginPage'
import './App.css'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontSize: '1.25rem'
      }}>
        加载中...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

const AppContent = () => {
  const { user, logout, isAdmin } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-brand">
          PB-BI 数据分析平台
          {isAdmin && <span style={{ fontSize: '0.75rem', marginLeft: '0.5rem', color: '#10b981' }}>(管理员)</span>}
        </div>
        <div className="nav-links">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>配置</NavLink>
          <NavLink to="/data" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>数据</NavLink>
          <NavLink to="/analysis" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>高级统计</NavLink>
          <NavLink to="/montecarlo" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>蒙特卡洛</NavLink>
          <NavLink to="/correlation" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>相关性</NavLink>
          <NavLink to="/visual" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>可视化</NavLink>
          <NavLink to="/guide" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} style={{ background: '#10b981', color: 'white', borderRadius: '6px' }}>操作指南</NavLink>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            {user?.username}
          </span>
          <button
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            登出
          </button>
        </div>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={
            <ProtectedRoute>
              <ConfigPage />
            </ProtectedRoute>
          } />
          <Route path="/data" element={
            <ProtectedRoute>
              <DataPage />
            </ProtectedRoute>
          } />
          <Route path="/analysis" element={
            <ProtectedRoute>
              <AnalysisPage />
            </ProtectedRoute>
          } />
          <Route path="/montecarlo" element={
            <ProtectedRoute>
              <MonteCarloPage />
            </ProtectedRoute>
          } />
          <Route path="/correlation" element={
            <ProtectedRoute>
              <CorrelationPage />
            </ProtectedRoute>
          } />
          <Route path="/visual" element={
            <ProtectedRoute>
              <VisualPage />
            </ProtectedRoute>
          } />
          <Route path="/guide" element={
            <ProtectedRoute>
              <GuidePage />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  )
}

const LoginRedirect = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return null;
  }
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <LoginPage />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginRedirect />} />
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
