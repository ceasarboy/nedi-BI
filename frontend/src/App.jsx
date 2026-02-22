import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import ConfigPage from './pages/ConfigPage'
import DataPage from './pages/DataPage'
import AnalysisPage from './pages/AnalysisPage'
import VisualPage from './pages/VisualPage'
import GuidePage from './pages/GuidePage'
import CorrelationPage from './pages/CorrelationPage'
import MonteCarloPage from './pages/MonteCarloPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">NEDI数据分析平台</div>
          <div className="nav-links">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>配置</NavLink>
            <NavLink to="/data" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>数据</NavLink>
            <NavLink to="/analysis" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>高级统计</NavLink>
            <NavLink to="/montecarlo" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>蒙特卡洛</NavLink>
            <NavLink to="/correlation" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>相关性</NavLink>
            <NavLink to="/visual" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>可视化</NavLink>
            <NavLink to="/guide" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} style={{ background: '#10b981', color: 'white', borderRadius: '6px' }}>操作指南</NavLink>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ConfigPage />} />
            <Route path="/data" element={<DataPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/montecarlo" element={<MonteCarloPage />} />
            <Route path="/correlation" element={<CorrelationPage />} />
            <Route path="/visual" element={<VisualPage />} />
            <Route path="/guide" element={<GuidePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
