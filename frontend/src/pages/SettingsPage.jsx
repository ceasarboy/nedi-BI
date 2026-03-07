import { useState, useEffect, createContext, useContext } from 'react'
import '../styles/SettingsPage.css'
import MemoryManager from '../components/MemoryManager'
import '../components/MemoryManager.css'

const SettingsContext = createContext()
const LOCAL_STORAGE_KEY = 'pb-bi-settings'

export const useSettings = () => useContext(SettingsContext)

const getLocalSettings = () => {
  try {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('Failed to load local settings:', e)
  }
  return null
}

const saveLocalSettings = (settings) => {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(settings))
  } catch (e) {
    console.error('Failed to save local settings:', e)
  }
}

export const applyUISettingsFromLocal = () => {
  const localSettings = getLocalSettings()
  if (localSettings) {
    const root = document.documentElement
    if (localSettings.ui_primary_color) {
      root.style.setProperty('--primary-color', localSettings.ui_primary_color)
      const darkerColor = adjustColorStatic(localSettings.ui_primary_color, -20)
      root.style.setProperty('--primary-hover', darkerColor)
      const lighterColor = adjustColorStatic(localSettings.ui_primary_color, 80)
      root.style.setProperty('--primary-light', lighterColor)
    }
    if (localSettings.ui_font_size) {
      const fontSizes = { small: '14px', medium: '16px', large: '18px' }
      root.style.setProperty('--font-size-base', fontSizes[localSettings.ui_font_size] || '16px')
    }
    if (localSettings.ui_style) {
      document.body.setAttribute('data-theme', localSettings.ui_style)
    }
  }
}

const adjustColorStatic = (color, amount) => {
  const clamp = (num) => Math.min(255, Math.max(0, num))
  const hex = color.replace('#', '')
  const num = parseInt(hex, 16)
  const r = clamp((num >> 16) + amount)
  const g = clamp(((num >> 8) & 0x00FF) + amount)
  const b = clamp((num & 0x0000FF) + amount)
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

function SettingsPage() {
  const [settingsTab, setSettingsTab] = useState('ui')
  const [settings, setSettings] = useState(() => {
    const localSettings = getLocalSettings()
    return localSettings || {
      ui_style: 'modern',
      ui_primary_color: '#3b82f6',
      ui_font_size: 'medium',
      ui_dark_mode: false,
      ai_provider: 'deepseek',
      ai_model: 'deepseek-chat',
      ai_temperature: 0.7,
      ai_max_tokens: 4096,
      has_api_key: false
    }
  })
  
  const [providers, setProviders] = useState([])
  const [styles, setStyles] = useState([
    {
      id: 'bloomberg-dark',
      name: 'Bloomberg终端',
      description: '极简暗色调、等宽字体、橙绿配色、专业金融风格',
      preview: {
        primary_color: '#ff6600',
        background: '#000000'
      }
    },
    {
      id: 'modern-light',
      name: '现代专业',
      description: '简洁明亮、专业配色、清晰层次',
      preview: {
        primary_color: '#2563eb',
        background: '#f8fafc'
      }
    }
  ])
  const [colors, setColors] = useState([])
  const [selectedProviderModels, setSelectedProviderModels] = useState([])
  const [availableModels, setAvailableModels] = useState([])
  const [apiKey, setApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [saving, setSaving] = useState(false)
  const [loadingModels, setLoadingModels] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadSettings()
    loadProviders()
    loadStyles()
    loadColors()
  }, [])

  useEffect(() => {
    applyUISettings()
  }, [settings.ui_style, settings.ui_primary_color, settings.ui_font_size])

  const applyUISettings = () => {
    const root = document.documentElement
    
    root.style.setProperty('--primary-color', settings.ui_primary_color)
    
    const darkerColor = adjustColor(settings.ui_primary_color, -20)
    root.style.setProperty('--primary-hover', darkerColor)
    
    const lighterColor = adjustColor(settings.ui_primary_color, 80)
    root.style.setProperty('--primary-light', lighterColor)
    
    const fontSizes = { small: '14px', medium: '16px', large: '18px' }
    root.style.setProperty('--font-size-base', fontSizes[settings.ui_font_size] || '16px')
    
    document.body.setAttribute('data-theme', settings.ui_style)
  }

  const adjustColor = (color, amount) => {
    const clamp = (num) => Math.min(255, Math.max(0, num))
    const hex = color.replace('#', '')
    const num = parseInt(hex, 16)
    const r = clamp((num >> 16) + amount)
    const g = clamp(((num >> 8) & 0x00FF) + amount)
    const b = clamp((num & 0x0000FF) + amount)
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
  }

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings')
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      }
    } catch (error) {
      console.error('Load settings error:', error)
    }
  }

  const loadProviders = async () => {
    try {
      const response = await fetch('/api/settings/providers')
      if (response.ok) {
        const data = await response.json()
        setProviders(data)
      }
    } catch (error) {
      console.error('Load providers error:', error)
    }
  }

  const loadStyles = async () => {
    try {
      const response = await fetch('/api/settings/styles')
      if (response.ok) {
        const data = await response.json()
        setStyles(data)
      }
    } catch (error) {
      console.error('Load styles error:', error)
    }
  }

  const loadColors = async () => {
    try {
      const response = await fetch('/api/settings/colors')
      if (response.ok) {
        const data = await response.json()
        setColors(data)
      }
    } catch (error) {
      console.error('Load colors error:', error)
    }
  }

  const loadAvailableModels = async (providerName) => {
    setLoadingModels(true)
    try {
      const response = await fetch(`/api/settings/providers/${providerName}/available-models`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setAvailableModels(data.models)
          if (data.models.length > 0) {
            setSettings(prev => ({ ...prev, ai_model: data.models[0].id }))
          }
        } else {
          setMessage({ type: 'warning', text: data.message || '获取模型列表失败' })
          setTimeout(() => setMessage(null), 3000)
        }
      }
    } catch (error) {
      console.error('Load available models error:', error)
    } finally {
      setLoadingModels(false)
    }
  }

  const handleProviderChange = (providerName) => {
    const provider = providers.find(p => p.name === providerName)
    if (provider) {
      setSettings(prev => ({
        ...prev,
        ai_provider: providerName,
        ai_model: provider.default_model
      }))
      setSelectedProviderModels(provider.models)
      setAvailableModels([])
    }
  }

  const handleApiKeySave = async () => {
    if (!apiKey.trim()) {
      setMessage({ type: 'warning', text: '请输入API密钥' })
      return
    }
    
    setSaving(true)
    try {
      const response = await fetch('/api/settings/ai', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: settings.ai_provider,
          api_key: apiKey
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
        setApiKey('')
        setMessage({ type: 'success', text: 'API密钥已保存，正在获取可用模型...' })
        setTimeout(() => setMessage(null), 2000)
        
        await loadAvailableModels(settings.ai_provider)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setSaving(false)
    }
  }

  const saveUISettings = async () => {
    setSaving(true)
    try {
      const response = await fetch('/api/settings/ui', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          style: settings.ui_style,
          primary_color: settings.ui_primary_color,
          font_size: settings.ui_font_size,
          dark_mode: settings.ui_dark_mode
        })
      })
      
      if (response.ok) {
        saveLocalSettings(settings)
        setMessage({ type: 'success', text: 'UI设置已保存并全局生效' })
        applyUISettings()
        setTimeout(() => setMessage(null), 3000)
      }
    } catch (error) {
      saveLocalSettings(settings)
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setSaving(false)
    }
  }

  const saveAISettings = async () => {
    setSaving(true)
    try {
      const response = await fetch('/api/settings/ai', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: settings.ai_provider,
          model: settings.ai_model,
          temperature: settings.ai_temperature,
          max_tokens: settings.ai_max_tokens
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
        setMessage({ type: 'success', text: 'AI设置已保存' })
        setTimeout(() => setMessage(null), 3000)
      }
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>系统设置</h1>
        <p>自定义您的PB-BI体验</p>
      </div>

      {message && (
        <div className={`settings-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="settings-tabs">
        <button
          className={`settings-tab-btn ${settingsTab === 'ui' ? 'active' : ''}`}
          onClick={() => setSettingsTab('ui')}
        >
          🎨 界面风格
        </button>
        <button
          className={`settings-tab-btn ${settingsTab === 'ai' ? 'active' : ''}`}
          onClick={() => setSettingsTab('ai')}
        >
          🤖 AI模型
        </button>
        <button
          className={`settings-tab-btn ${settingsTab === 'memory' ? 'active' : ''}`}
          onClick={() => setSettingsTab('memory')}
        >
          🧠 记忆管理
        </button>
      </div>

      <div className="settings-content">
        {settingsTab === 'memory' ? (
          <MemoryManager />
        ) : (
          <>
            {/* UI风格设置 */}
            {settingsTab === 'ui' && (
              <section className="settings-section">
                <div className="section-header">
                  <h2>🎨 界面风格</h2>
                  <span className="section-desc">选择您喜欢的界面风格（实时预览，自动生效）</span>
                </div>
                
                <div className="style-cards">
                  {styles.map(style => (
                    <div 
                      key={style.id}
                      className={`style-card ${settings.ui_style === style.id ? 'active' : ''}`}
                      onClick={() => {
                        setSettings(prev => ({ ...prev, ui_style: style.id }))
                        document.body.setAttribute('data-theme', style.id)
                      }}
                    >
                      <div className="style-preview" style={{
                        background: style.preview.background,
                        borderColor: settings.ui_style === style.id ? settings.ui_primary_color : 'transparent'
                      }}>
                        <div className="preview-header" style={{ background: style.preview.primary_color }}></div>
                        <div className="preview-content">
                          <div className="preview-line"></div>
                          <div className="preview-line short"></div>
                        </div>
                      </div>
                      <div className="style-info">
                        <h3>{style.name}</h3>
                        <p>{style.description}</p>
                      </div>
                      {settings.ui_style === style.id && (
                        <div className="style-check">✓</div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="settings-group">
                  <label>主色调</label>
                  <div className="color-palette">
                    {colors.map(color => (
                      <div
                        key={color.id}
                        className={`color-option ${settings.ui_primary_color === color.id ? 'active' : ''}`}
                        style={{ background: color.id }}
                        onClick={() => setSettings(prev => ({ ...prev, ui_primary_color: color.id }))}
                        title={color.name}
                      >
                        {settings.ui_primary_color === color.id && <span>✓</span>}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="settings-group">
                  <label>字体大小</label>
                  <div className="font-size-options">
                    {['small', 'medium', 'large'].map(size => (
                      <button
                        key={size}
                        className={`font-size-btn ${settings.ui_font_size === size ? 'active' : ''}`}
                        onClick={() => setSettings(prev => ({ ...prev, ui_font_size: size }))}
                      >
                        {size === 'small' ? '小' : size === 'medium' ? '中' : '大'}
                      </button>
                    ))}
                  </div>
                </div>

                <button className="save-btn primary" onClick={saveUISettings} disabled={saving}>
                  {saving ? '保存中...' : '保存UI设置'}
                </button>
              </section>
            )}

            {/* AI设置 */}
            {settingsTab === 'ai' && (
              <section className="settings-section">
                <div className="section-header">
                  <h2>🤖 AI模型设置</h2>
                  <span className="section-desc">配置AI模型和API密钥</span>
                </div>

                <div className="settings-group">
                  <label>AI提供商</label>
                  <div className="provider-cards">
                    {providers.map(provider => (
                      <div
                        key={provider.name}
                        className={`provider-card ${settings.ai_provider === provider.name ? 'active' : ''}`}
                        onClick={() => handleProviderChange(provider.name)}
                      >
                        <span className="provider-icon">{provider.icon}</span>
                        <div className="provider-info">
                          <h4>{provider.display_name}</h4>
                          <p>{provider.description}</p>
                        </div>
                        {settings.ai_provider === provider.name && (
                          <div className="provider-check">✓</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="settings-group">
                  <label>
                    API密钥
                    {settings.has_api_key && <span className="api-key-status">已设置</span>}
                  </label>
                  <div className="api-key-input">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder={settings.has_api_key ? '输入新密钥以更新' : '请输入API密钥'}
                    />
                    <button 
                      className="toggle-visibility"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? '🙈' : '👁️'}
                    </button>
                  </div>
                  <div className="api-key-actions">
                    <button 
                      className="save-api-key-btn"
                      onClick={handleApiKeySave}
                      disabled={saving || !apiKey.trim()}
                    >
                      {saving ? '保存中...' : '保存密钥并获取模型'}
                    </button>
                  </div>
                  <p className="input-hint">
                    保存API密钥后将自动获取您账号下可用的模型列表
                  </p>
                </div>

                <div className="settings-group">
                  <label>选择模型</label>
                  {loadingModels ? (
                    <div className="loading-models">
                      <span className="spinner-small"></span>
                      正在获取可用模型...
                    </div>
                  ) : availableModels.length > 0 ? (
                    <div className="model-list">
                      {availableModels.map(model => (
                        <div 
                          key={model.id} 
                          className={`model-option ${settings.ai_model === model.id ? 'selected' : ''}`}
                          onClick={() => setSettings(prev => ({ ...prev, ai_model: model.id }))}
                        >
                          <div className="model-name">{model.name || model.id}</div>
                          {model.description && <div className="model-desc">{model.description}</div>}
                          {model.price_input !== undefined && (
                            <div className="model-price">
                              输入: {model.price_input} {model.price_unit} | 输出: {model.price_output} {model.price_unit}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="model-list">
                      {selectedProviderModels.map(model => (
                        <div 
                          key={model.id} 
                          className={`model-option ${settings.ai_model === model.id ? 'selected' : ''}`}
                          onClick={() => setSettings(prev => ({ ...prev, ai_model: model.id }))}
                        >
                          <div className="model-name">{model.name}</div>
                          <div className="model-desc">{model.description}</div>
                          {model.price_input !== undefined && (
                            <div className="model-price">
                              输入: {model.price_input} {model.price_unit} | 输出: {model.price_output} {model.price_unit}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="input-hint">
                    {availableModels.length > 0 
                      ? `已获取 ${availableModels.length} 个可用模型` 
                      : '请先保存API密钥以获取可用模型'}
                  </p>
                </div>

                <div className="settings-row">
                  <div className="settings-group half">
                    <label>温度 (Temperature)</label>
                    <div className="slider-container">
                      <input
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={settings.ai_temperature}
                        onChange={(e) => setSettings(prev => ({ ...prev, ai_temperature: parseFloat(e.target.value) }))}
                      />
                      <span className="slider-value">{settings.ai_temperature}</span>
                    </div>
                    <p className="input-hint">较低的值使输出更确定，较高的值更有创意</p>
                  </div>

                  <div className="settings-group half">
                    <label>最大Token数</label>
                    <input
                      type="number"
                      value={settings.ai_max_tokens}
                      onChange={(e) => setSettings(prev => ({ ...prev, ai_max_tokens: parseInt(e.target.value) }))}
                      min={1}
                      max={32000}
                      className="number-input"
                    />
                    <p className="input-hint">控制回复的最大长度</p>
                  </div>
                </div>

                <button className="save-btn primary" onClick={saveAISettings} disabled={saving}>
                  {saving ? '保存中...' : '保存AI设置'}
                </button>
              </section>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default SettingsPage
