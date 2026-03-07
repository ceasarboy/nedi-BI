import { useState, useEffect } from 'react'

const PREFERENCE_TEMPLATES = [
  {
    id: 'concise',
    name: '简洁风格',
    description: '回复简洁，避免冗余',
    preferences: [
      { type: 'style', key: 'response_length', value: 'concise' },
      { type: 'style', key: 'detail_level', value: 'low' }
    ]
  },
  {
    id: 'detailed',
    name: '详细风格',
    description: '回复详细，包含解释',
    preferences: [
      { type: 'style', key: 'response_length', value: 'detailed' },
      { type: 'style', key: 'detail_level', value: 'high' }
    ]
  },
  {
    id: 'technical',
    name: '技术风格',
    description: '使用专业术语',
    preferences: [
      { type: 'style', key: 'terminology', value: 'technical' }
    ]
  },
  {
    id: 'chart_first',
    name: '图表优先',
    description: '优先使用图表展示',
    preferences: [
      { type: 'priority', key: 'chart_preference', value: 'always' }
    ]
  }
]

const MemoryManager = () => {
  const [activeTab, setActiveTab] = useState('preferences')
  const [stats, setStats] = useState({
    preferences_count: 0,
    success_cases_count: 0,
    failure_lessons_count: 0
  })
  const [preferences, setPreferences] = useState([])
  const [successCases, setSuccessCases] = useState([])
  const [failureLessons, setFailureLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [newPreference, setNewPreference] = useState({
    preference_type: 'style',
    preference_key: '',
    preference_value: '',
    confidence: 0.8
  })

  useEffect(() => {
    loadAllData()
  }, [])

  const loadAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        loadStats(),
        loadPreferences(),
        loadSuccessCases(),
        loadFailureLessons()
      ])
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/feedback/memory/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Load stats error:', error)
    }
  }

  const loadPreferences = async () => {
    try {
      const response = await fetch('/api/feedback/memory/preferences?limit=50')
      if (response.ok) {
        const data = await response.json()
        setPreferences(data)
      }
    } catch (error) {
      console.error('Load preferences error:', error)
    }
  }

  const loadSuccessCases = async () => {
    try {
      const response = await fetch('/api/feedback/memory/success-cases?limit=50')
      if (response.ok) {
        const data = await response.json()
        setSuccessCases(data)
      }
    } catch (error) {
      console.error('Load success cases error:', error)
    }
  }

  const loadFailureLessons = async () => {
    try {
      const response = await fetch('/api/feedback/memory/failure-lessons?limit=50')
      if (response.ok) {
        const data = await response.json()
        setFailureLessons(data)
      }
    } catch (error) {
      console.error('Load failure lessons error:', error)
    }
  }

  const deletePreference = async (id) => {
    try {
      const response = await fetch(`/api/feedback/memory/preferences/${id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setPreferences(prev => prev.filter(p => p.id !== id))
        setStats(prev => ({ ...prev, preferences_count: prev.preferences_count - 1 }))
        setMessage({ type: 'success', text: '偏好已删除' })
        setTimeout(() => setMessage(null), 2000)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除失败' })
    }
    setDeleteConfirm(null)
  }

  const deleteSuccessCase = async (id) => {
    try {
      const response = await fetch(`/api/feedback/memory/success-cases/${id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setSuccessCases(prev => prev.filter(c => c.id !== id))
        setStats(prev => ({ ...prev, success_cases_count: prev.success_cases_count - 1 }))
        setMessage({ type: 'success', text: '案例已删除' })
        setTimeout(() => setMessage(null), 2000)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除失败' })
    }
    setDeleteConfirm(null)
  }

  const deleteFailureLesson = async (id) => {
    try {
      const response = await fetch(`/api/feedback/memory/failure-lessons/${id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setFailureLessons(prev => prev.filter(l => l.id !== id))
        setStats(prev => ({ ...prev, failure_lessons_count: prev.failure_lessons_count - 1 }))
        setMessage({ type: 'success', text: '教训已删除' })
        setTimeout(() => setMessage(null), 2000)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '删除失败' })
    }
    setDeleteConfirm(null)
  }

  const addPreference = async () => {
    if (!newPreference.preference_key || !newPreference.preference_value) {
      setMessage({ type: 'error', text: '请填写完整的偏好信息' })
      return
    }

    try {
      const response = await fetch('/api/feedback/memory/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newPreference,
          source: 'manual'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setPreferences(prev => [data, ...prev])
        setStats(prev => ({ ...prev, preferences_count: prev.preferences_count + 1 }))
        setMessage({ type: 'success', text: '偏好已添加' })
        setTimeout(() => setMessage(null), 2000)
        setShowAddModal(false)
        setNewPreference({
          preference_type: 'style',
          preference_key: '',
          preference_value: '',
          confidence: 0.8
        })
      }
    } catch (error) {
      setMessage({ type: 'error', text: '添加失败' })
    }
  }

  const applyTemplate = async (template) => {
    try {
      let addedCount = 0
      for (const pref of template.preferences) {
        const response = await fetch('/api/feedback/memory/preferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            preference_type: pref.type,
            preference_key: pref.key,
            preference_value: pref.value,
            confidence: 1.0,
            source: 'template'
          })
        })
        if (response.ok) addedCount++
      }
      
      if (addedCount > 0) {
        await loadPreferences()
        await loadStats()
        setMessage({ type: 'success', text: `已应用模板: ${template.name}` })
        setTimeout(() => setMessage(null), 2000)
        setShowTemplateModal(false)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '应用模板失败' })
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filterBySearch = (items, field) => {
    if (!searchTerm) return items
    return items.filter(item => {
      const value = item[field]
      if (typeof value === 'string') {
        return value.toLowerCase().includes(searchTerm.toLowerCase())
      }
      return false
    })
  }

  if (loading) {
    return (
      <div className="memory-manager loading">
        <div className="spinner"></div>
        <span>加载记忆数据...</span>
      </div>
    )
  }

  return (
    <div className="memory-manager">
      <div className="memory-header">
        <h2>🧠 记忆管理</h2>
        <p>管理AI的三层记忆系统：用户偏好、成功案例、失败教训</p>
      </div>

      {message && (
        <div className={`memory-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="memory-stats">
        <div className="stat-card preference">
          <div className="stat-icon">👤</div>
          <div className="stat-info">
            <div className="stat-value">{stats.preferences_count}</div>
            <div className="stat-label">用户偏好</div>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{stats.success_cases_count}</div>
            <div className="stat-label">成功案例</div>
          </div>
        </div>
        <div className="stat-card failure">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <div className="stat-value">{stats.failure_lessons_count}</div>
            <div className="stat-label">失败教训</div>
          </div>
        </div>
      </div>

      <div className="memory-tabs">
        <button
          className={`tab-btn ${activeTab === 'preferences' ? 'active' : ''}`}
          onClick={() => setActiveTab('preferences')}
        >
          👤 用户偏好
        </button>
        <button
          className={`tab-btn ${activeTab === 'success' ? 'active' : ''}`}
          onClick={() => setActiveTab('success')}
        >
          ✅ 成功案例
        </button>
        <button
          className={`tab-btn ${activeTab === 'failure' ? 'active' : ''}`}
          onClick={() => setActiveTab('failure')}
        >
          ⚠️ 失败教训
        </button>
      </div>

      <div className="memory-search">
        <input
          type="text"
          placeholder="搜索..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        {activeTab === 'preferences' && (
          <div className="preference-actions">
            <button className="add-pref-btn" onClick={() => setShowAddModal(true)}>
              ➕ 添加偏好
            </button>
            <button className="template-btn" onClick={() => setShowTemplateModal(true)}>
              📋 应用模板
            </button>
          </div>
        )}
      </div>

      <div className="memory-content">
        {activeTab === 'preferences' && (
          <div className="memory-list">
            {filterBySearch(preferences, 'preference_key').length === 0 ? (
              <div className="empty-state">暂无用户偏好数据</div>
            ) : (
              filterBySearch(preferences, 'preference_key').map(pref => (
                <div key={pref.id} className="memory-item preference-item">
                  <div className="item-main">
                    <div className="item-header">
                      <span className="item-type">{pref.preference_type}</span>
                      <span className="item-key">{pref.preference_key}</span>
                    </div>
                    <div className="item-value">{pref.preference_value}</div>
                    <div className="item-meta">
                      <span className="confidence">
                        置信度: {(pref.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="source">来源: {pref.source === 'manual' ? '手动' : '自动'}</span>
                      <span className="date">{formatDate(pref.created_at)}</span>
                    </div>
                  </div>
                  <div className="item-actions">
                    {deleteConfirm === `pref-${pref.id}` ? (
                      <div className="confirm-delete">
                        <span>确认删除?</span>
                        <button onClick={() => deletePreference(pref.id)}>是</button>
                        <button onClick={() => setDeleteConfirm(null)}>否</button>
                      </div>
                    ) : (
                      <button
                        className="delete-btn"
                        onClick={() => setDeleteConfirm(`pref-${pref.id}`)}
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'success' && (
          <div className="memory-list">
            {filterBySearch(successCases, 'query').length === 0 ? (
              <div className="empty-state">暂无成功案例数据</div>
            ) : (
              filterBySearch(successCases, 'query').map(item => (
                <div key={item.id} className="memory-item success-item">
                  <div className="item-main">
                    <div className="item-header">
                      <span className="item-intent">{item.query_intent || 'general'}</span>
                      {item.chart_generated && <span className="badge chart">📊 图表</span>}
                    </div>
                    <div className="item-query">{item.query}</div>
                    <div className="item-response">{item.response?.substring(0, 150)}...</div>
                    <div className="item-meta">
                      {item.tool_sequence && (
                        <span className="tools">工具: {item.tool_sequence}</span>
                      )}
                      <span className="date">{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                  <div className="item-actions">
                    {deleteConfirm === `success-${item.id}` ? (
                      <div className="confirm-delete">
                        <span>确认删除?</span>
                        <button onClick={() => deleteSuccessCase(item.id)}>是</button>
                        <button onClick={() => setDeleteConfirm(null)}>否</button>
                      </div>
                    ) : (
                      <button
                        className="delete-btn"
                        onClick={() => setDeleteConfirm(`success-${item.id}`)}
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'failure' && (
          <div className="memory-list">
            {filterBySearch(failureLessons, 'query').length === 0 ? (
              <div className="empty-state">暂无失败教训数据</div>
            ) : (
              filterBySearch(failureLessons, 'query').map(item => (
                <div key={item.id} className="memory-item failure-item">
                  <div className="item-main">
                    <div className="item-header">
                      <span className="item-reason">{item.failure_reason || 'general'}</span>
                    </div>
                    <div className="item-query">{item.query}</div>
                    <div className="item-correction">
                      <strong>正确做法:</strong> {item.correct_approach}
                    </div>
                    {item.user_correction && (
                      <div className="item-user-correction">
                        <strong>用户修正:</strong> {item.user_correction}
                      </div>
                    )}
                    <div className="item-meta">
                      <span className="date">{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                  <div className="item-actions">
                    {deleteConfirm === `failure-${item.id}` ? (
                      <div className="confirm-delete">
                        <span>确认删除?</span>
                        <button onClick={() => deleteFailureLesson(item.id)}>是</button>
                        <button onClick={() => setDeleteConfirm(null)}>否</button>
                      </div>
                    ) : (
                      <button
                        className="delete-btn"
                        onClick={() => setDeleteConfirm(`failure-${item.id}`)}
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* 添加偏好模态框 */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>➕ 添加用户偏好</h3>
              <button className="close-btn" onClick={() => setShowAddModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>偏好类型</label>
                <select
                  value={newPreference.preference_type}
                  onChange={(e) => setNewPreference(prev => ({ ...prev, preference_type: e.target.value }))}
                >
                  <option value="style">风格</option>
                  <option value="format">格式</option>
                  <option value="priority">优先级</option>
                </select>
              </div>
              <div className="form-group">
                <label>偏好键</label>
                <input
                  type="text"
                  placeholder="例如: response_length"
                  value={newPreference.preference_key}
                  onChange={(e) => setNewPreference(prev => ({ ...prev, preference_key: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label>偏好值</label>
                <input
                  type="text"
                  placeholder="例如: concise"
                  value={newPreference.preference_value}
                  onChange={(e) => setNewPreference(prev => ({ ...prev, preference_value: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label>置信度: {(newPreference.confidence * 100).toFixed(0)}%</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={newPreference.confidence}
                  onChange={(e) => setNewPreference(prev => ({ ...prev, confidence: parseFloat(e.target.value) }))}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="cancel-btn" onClick={() => setShowAddModal(false)}>取消</button>
              <button className="save-btn" onClick={addPreference}>保存</button>
            </div>
          </div>
        </div>
      )}

      {/* 模板选择模态框 */}
      {showTemplateModal && (
        <div className="modal-overlay" onClick={() => setShowTemplateModal(false)}>
          <div className="modal-content template-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📋 选择偏好模板</h3>
              <button className="close-btn" onClick={() => setShowTemplateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="template-list">
                {PREFERENCE_TEMPLATES.map(template => (
                  <div 
                    key={template.id} 
                    className="template-item"
                    onClick={() => applyTemplate(template)}
                  >
                    <div className="template-name">{template.name}</div>
                    <div className="template-desc">{template.description}</div>
                    <div className="template-prefs">
                      {template.preferences.map((p, i) => (
                        <span key={i} className="template-pref-tag">{p.key}: {p.value}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MemoryManager
