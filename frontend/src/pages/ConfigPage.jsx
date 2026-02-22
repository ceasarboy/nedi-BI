import { useState, useEffect } from 'react'
import { dataflowAPI } from '../services/api'
import Modal from '../components/Modal'

function ConfigPage() {
  const [dataflows, setDataflows] = useState([])
  const [selectedDataflow, setSelectedDataflow] = useState(null)
  const [selectedDataflowForSettings, setSelectedDataflowForSettings] = useState(null)
  const [fields, setFields] = useState([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLocalModalOpen, setIsLocalModalOpen] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [loading, setLoading] = useState(false)
  const [savingFields, setSavingFields] = useState(false)
  const [importingFields, setImportingFields] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    appkey: '',
    sign: '',
    worksheet_id: '',
    is_private: false,
    private_api_url: ''
  })
  const [localFormData, setLocalFormData] = useState({
    name: ''
  })

  useEffect(() => {
    loadDataflows()
  }, [])

  const loadDataflows = async () => {
    try {
      const response = await dataflowAPI.getAll()
      setDataflows(response.data)
    } catch (error) {
      console.error('加载数据流失败', error)
    }
  }

  const handleAddDataflow = () => {
    setSelectedDataflow(null)
    setFormData({
      name: '',
      appkey: '',
      sign: '',
      worksheet_id: '',
      is_private: false,
      private_api_url: ''
    })
    setIsModalOpen(true)
  }

  const handleAddLocalDataflow = () => {
    setLocalFormData({ name: '' })
    setIsLocalModalOpen(true)
  }

  const handleSaveLocalDataflow = async () => {
    if (!localFormData.name) {
      alert('请输入数据流名称')
      return
    }
    setLoading(true)
    try {
      await dataflowAPI.create({
        name: localFormData.name,
        type: 'local'
      })
      setMessage({ type: 'success', text: '创建成功' })
      setIsLocalModalOpen(false)
      loadDataflows()
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleEditDataflow = (dataflow) => {
    setSelectedDataflow(dataflow)
    setFormData({
      name: dataflow.name,
      appkey: dataflow.appkey,
      sign: dataflow.sign,
      worksheet_id: dataflow.worksheet_id,
      is_private: dataflow.is_private || false,
      private_api_url: dataflow.private_api_url || ''
    })
    setIsModalOpen(true)
  }

  const handleDeleteDataflow = async (id) => {
    if (!window.confirm('确定要删除这个数据流吗？')) return
    try {
      await dataflowAPI.delete(id)
      setMessage({ type: 'success', text: '删除成功' })
      loadDataflows()
    } catch (error) {
      setMessage({ type: 'error', text: '删除失败' })
    }
  }

  const handleTestConnection = async (id) => {
    try {
      await dataflowAPI.testConnection(id)
      setMessage({ type: 'success', text: '连接成功' })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '连接失败' })
    }
  }

  const handleOpenSettings = async (dataflow) => {
    setSelectedDataflowForSettings(dataflow)
    setMessage({ type: '', text: '' })
    try {
      const response = await dataflowAPI.getFields(dataflow.id)
      setFields(response.data.data)
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '获取字段失败' })
      setFields([])
    }
  }

  const handleFieldToggle = (index) => {
    const newFields = [...fields]
    newFields[index] = {
      ...newFields[index],
      is_enabled: newFields[index].is_enabled === 'true' ? 'false' : 'true'
    }
    setFields(newFields)
  }

  const handleFieldTypeChange = (index, value) => {
    const newFields = [...fields]
    newFields[index] = {
      ...newFields[index],
      data_type: value
    }
    setFields(newFields)
  }

  const handleSaveFields = async () => {
    if (!selectedDataflowForSettings) return
    setSavingFields(true)
    try {
      await dataflowAPI.saveFields(selectedDataflowForSettings.id, { fields })
      setMessage({ type: 'success', text: '字段配置保存成功' })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '保存失败' })
    } finally {
      setSavingFields(false)
    }
  }

  const handleImportFields = async (e) => {
    const file = e.target.files[0]
    if (!file || !selectedDataflowForSettings) return
    
    const validExtensions = ['.csv', '.xlsx', '.xls']
    const fileName = file.name.toLowerCase()
    const isValid = validExtensions.some(ext => fileName.endsWith(ext))
    
    if (!isValid) {
      alert('仅支持CSV和Excel格式文件')
      e.target.value = ''
      return
    }
    
    setImportingFields(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await dataflowAPI.importFields(selectedDataflowForSettings.id, formData)
      setFields(response.data.data)
      setMessage({ type: 'success', text: '字段和数据已保存，可在数据页面查看' })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '导入字段失败' })
    } finally {
      setImportingFields(false)
      e.target.value = ''
    }
  }

  const handleSaveDataflow = async () => {
    setLoading(true)
    setMessage({ type: '', text: '' })
    try {
      if (selectedDataflow) {
        await dataflowAPI.update(selectedDataflow.id, formData)
        setMessage({ type: 'success', text: '更新成功' })
      } else {
        await dataflowAPI.create(formData)
        setMessage({ type: 'success', text: '创建成功' })
      }
      setIsModalOpen(false)
      loadDataflows()
    } catch (error) {
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleLocalChange = (e) => {
    setLocalFormData({
      ...localFormData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 className="page-title" style={{ margin: 0 }}>数据流管理</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={handleAddLocalDataflow}>
            + 增加本地数据流
          </button>
          <button className="btn btn-primary" onClick={handleAddDataflow}>
            + 增加明道云数据流
          </button>
        </div>
      </div>

      {message.text && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="dataflow-list">
        {dataflows.length === 0 ? (
          <div className="empty-state">
            <p>暂无数据流，请点击"增加明道云数据流"或"增加本地数据流"添加</p>
          </div>
        ) : (
          dataflows.map((df) => (
            <div key={df.id} className="dataflow-item">
              <div className="dataflow-info">
                <h4>{df.name}</h4>
                <p>
                  类型: {df.type === 'local' ? '本地' : (df.is_private ? '明道云(私有化)' : '明道云')}
                  {df.type !== 'local' && ` | 工作表 ID: ${df.worksheet_id}`}
                </p>
              </div>
              <div className="dataflow-actions">
                {df.type !== 'local' && (
                  <button 
                    className="btn btn-sm btn-default" 
                    onClick={() => handleTestConnection(df.id)}
                  >
                    测试
                  </button>
                )}
                <button 
                  className="btn btn-sm btn-secondary" 
                  onClick={() => handleOpenSettings(df)}
                >
                  设置
                </button>
                <button 
                  className="btn btn-sm btn-primary" 
                  onClick={() => handleEditDataflow(df)}
                >
                  编辑
                </button>
                <button 
                  className="btn btn-sm btn-danger" 
                  onClick={() => handleDeleteDataflow(df.id)}
                >
                  删除
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="data-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 className="section-title" style={{ margin: 0 }}>
            数据设置
            {selectedDataflowForSettings && (
              <span style={{ fontSize: '14px', fontWeight: 'normal', marginLeft: '8px', color: 'var(--text-secondary)' }}>
                - {selectedDataflowForSettings.name}
              </span>
            )}
          </h2>
          <div className="btn-group" style={{ marginTop: 0 }}>
            {selectedDataflowForSettings?.type === 'local' && (
              <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                📂 导入文件获取字段
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleImportFields}
                  style={{ display: 'none' }}
                  disabled={importingFields}
                />
              </label>
            )}
            {fields.length > 0 && (
              <button 
                className="btn btn-primary" 
                onClick={handleSaveFields}
                disabled={savingFields || importingFields}
              >
                {savingFields ? '保存中...' : '保存配置'}
              </button>
            )}
          </div>
        </div>

        {!selectedDataflowForSettings ? (
          <div className="empty-state">
            <p>请点击数据流的"设置"按钮来配置字段</p>
          </div>
        ) : fields.length === 0 ? (
          <div className="empty-state">
            <p>暂无字段数据</p>
          </div>
        ) : (
          <div className="field-list">
            <div className="field-header">
              <div className="field-cell field-check">使用</div>
              <div className="field-cell field-name">字段名称</div>
              <div className="field-cell field-id">字段ID</div>
              <div className="field-cell field-type">字段类型</div>
            </div>
            {fields.map((field, index) => (
              <div key={field.field_id} className="field-item">
                <div className="field-cell field-check">
                  <input
                    type="checkbox"
                    checked={field.is_enabled === 'true'}
                    onChange={() => handleFieldToggle(index)}
                  />
                </div>
                <div className="field-cell field-name">{field.field_name}</div>
                <div className="field-cell field-id">{field.field_id}</div>
                <div className="field-cell field-type">
                  <select
                    className="form-input"
                    style={{ padding: '4px 8px', fontSize: '14px' }}
                    value={field.data_type}
                    onChange={(e) => handleFieldTypeChange(index, e.target.value)}
                  >
                    <option value="text">文本</option>
                    <option value="number">数字</option>
                    <option value="date">日期</option>
                    <option value="boolean">布尔</option>
                    <option value="select">选择</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedDataflow ? '编辑数据流' : '增加数据流'}
      >
        <div className="form-group">
          <label className="form-label">数据流名称</label>
          <input
            type="text"
            name="name"
            className="form-input"
            value={formData.name}
            onChange={handleChange}
            placeholder="请输入数据流名称"
          />
        </div>

        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={formData.is_private}
              onChange={(e) => setFormData({ ...formData, is_private: e.target.checked, private_api_url: e.target.checked ? formData.private_api_url : '' })}
              style={{ marginRight: '8px' }}
            />
            <span>私有化部署</span>
          </label>
          <small style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px', display: 'block' }}>
            勾选后使用自定义API地址，不勾选使用默认明道云地址
          </small>
        </div>

        {formData.is_private && (
          <div className="form-group">
            <label className="form-label">明道云API地址</label>
            <input
              type="text"
              name="private_api_url"
              className="form-input"
              value={formData.private_api_url}
              onChange={handleChange}
              placeholder="例如: https://md.yourcompany.com/api"
            />
            <small style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px', display: 'block' }}>
              只填写基础地址，不要包含 /v3/app 等路径
            </small>
          </div>
        )}

        <div className="form-group">
          <label className="form-label">AppKey</label>
          <input
            type="text"
            name="appkey"
            className="form-input"
            value={formData.appkey}
            onChange={handleChange}
            placeholder="请输入 AppKey"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Sign</label>
          <input
            type="password"
            name="sign"
            className="form-input"
            value={formData.sign}
            onChange={handleChange}
            placeholder="请输入 Sign"
          />
        </div>

        <div className="form-group">
          <label className="form-label">工作表 ID</label>
          <input
            type="text"
            name="worksheet_id"
            className="form-input"
            value={formData.worksheet_id}
            onChange={handleChange}
            placeholder="请输入工作表 ID"
          />
        </div>

        <div className="btn-group">
          <button 
            className="btn btn-default" 
            onClick={() => setIsModalOpen(false)}
            disabled={loading}
          >
            取消
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSaveDataflow}
            disabled={loading}
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </Modal>

      <Modal
        isOpen={isLocalModalOpen}
        onClose={() => setIsLocalModalOpen(false)}
        title="增加本地数据流"
      >
        <div className="form-group">
          <label className="form-label">数据流名称</label>
          <input
            type="text"
            name="name"
            className="form-input"
            value={localFormData.name}
            onChange={handleLocalChange}
            placeholder="请输入数据流名称"
          />
        </div>

        <div className="btn-group">
          <button 
            className="btn btn-default" 
            onClick={() => setIsLocalModalOpen(false)}
            disabled={loading}
          >
            取消
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSaveLocalDataflow}
            disabled={loading}
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </Modal>
    </div>
  )
}

export default ConfigPage
