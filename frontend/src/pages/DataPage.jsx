import { useState, useEffect } from 'react'
import { dataflowAPI, dataAPI } from '../services/api'
import Modal from '../components/Modal'

function DataPage() {
  const [activeTab, setActiveTab] = useState('import')
  
  const [dataflows, setDataflows] = useState([])
  const [dataflowsMap, setDataflowsMap] = useState({})
  
  const [selectedDataflow, setSelectedDataflow] = useState(null)
  
  const [snapshots, setSnapshots] = useState([])
  const [snapshotsPage, setSnapshotsPage] = useState(1)
  const [snapshotsTotal, setSnapshotsTotal] = useState(0)
  const [snapshotsPageSize] = useState(10)
  
  const [selectedSnapshot, setSelectedSnapshot] = useState(null)
  
  const [fields, setFields] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false)
  const [snapshotName, setSnapshotName] = useState('')

  useEffect(() => {
    if (activeTab === 'import') {
      loadDataflowsForImport()
    } else {
      loadAllSnapshots()
    }
  }, [activeTab])

  useEffect(() => {
    if (activeTab === 'existing' && snapshotsPage > 0) {
      loadAllSnapshots()
    }
  }, [snapshotsPage, activeTab])

  const loadDataflowsForImport = async () => {
    setLoading(true)
    try {
      const response = await dataflowAPI.getAll(1, 100)
      setDataflows(response.data)
    } catch (error) {
      setMessage({ type: 'error', text: '加载数据流失败' })
    } finally {
      setLoading(false)
    }
  }

  const loadAllSnapshots = async () => {
    setLoading(true)
    try {
      const [dataflowsRes, snapshotsRes, countRes] = await Promise.all([
        dataflowAPI.getAll(1, 1000),
        dataAPI.getAllSnapshots(snapshotsPage, snapshotsPageSize),
        dataAPI.getSnapshotsCount()
      ])
      
      const dfMap = {}
      dataflowsRes.data.forEach(df => {
        dfMap[df.id] = df
      })
      setDataflowsMap(dfMap)
      
      setSnapshots(snapshotsRes.data.data)
      setSnapshotsTotal(countRes.data.data.count)
    } catch (error) {
      setMessage({ type: 'error', text: '加载快照失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleSelectDataflowForImport = async (dataflow) => {
    setSelectedDataflow(dataflow)
    setFields([])
    setRows([])
    setMessage({ type: '', text: '' })
    
    if (dataflow.type === 'local') {
      await loadLocalDataflowData(dataflow.id)
    }
  }

  const loadLocalDataflowData = async (dataflowId) => {
    setLoadingData(true)
    try {
      const snapshotsRes = await dataAPI.getSnapshots(dataflowId, 1, 1)
      const snapshots = snapshotsRes.data.data
      
      if (snapshots && snapshots.length > 0) {
        const latestSnapshot = snapshots[0]
        const snapshotRes = await dataAPI.getSnapshot(latestSnapshot.id)
        setFields(snapshotRes.data.data.fields)
        setRows(snapshotRes.data.data.rows)
        setMessage({ type: 'success', text: '数据加载成功' })
      } else {
        setMessage({ type: 'info', text: '暂无数据，请先在配置页面导入文件' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '加载数据失败' })
    } finally {
      setLoadingData(false)
    }
  }

  const handleLoadData = async () => {
    if (!selectedDataflow) return
    
    setLoadingData(true)
    setMessage({ type: '', text: '' })
    
    try {
      const response = await dataAPI.queryData({
        dataflow_id: selectedDataflow.id,
        page_size: 100
      })
      
      setFields(response.data.data.fields)
      setRows(response.data.data.rows)
      setMessage({ type: 'success', text: '数据加载成功' })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '加载数据失败' })
      setFields([])
      setRows([])
    } finally {
      setLoadingData(false)
    }
  }

  const handleOpenSaveModal = () => {
    if (selectedDataflow) {
      setSnapshotName(selectedDataflow.worksheet_id)
    }
    setIsSaveModalOpen(true)
  }

  const handleSaveSnapshot = async () => {
    if (!selectedDataflow || rows.length === 0) return
    
    try {
      await dataAPI.createSnapshot({
        dataflow_id: selectedDataflow.id,
        name: snapshotName,
        fields: JSON.stringify(fields),
        data: JSON.stringify(rows)
      })
      
      setMessage({ type: 'success', text: '快照保存成功' })
      setIsSaveModalOpen(false)
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '保存失败' })
    }
  }

  const handleSelectSnapshot = async (snapshot) => {
    setSelectedSnapshot(snapshot)
    setLoadingData(true)
    
    try {
      const response = await dataAPI.getSnapshot(snapshot.id)
      setFields(response.data.data.fields)
      setRows(response.data.data.rows)
      setMessage({ type: 'success', text: '快照加载成功' })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '加载快照失败' })
    } finally {
      setLoadingData(false)
    }
  }

  const handleDeleteSnapshot = async (snapshotId) => {
    if (!window.confirm('确定要删除这个快照吗？')) return
    
    try {
      await dataAPI.deleteSnapshot(snapshotId)
      setMessage({ type: 'success', text: '快照删除成功' })
      
      if (selectedSnapshot?.id === snapshotId) {
        setSelectedSnapshot(null)
        setFields([])
        setRows([])
      }
      
      await loadAllSnapshots()
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '删除失败' })
    }
  }

  const formatValue = (value) => {
    if (value === null || value === undefined) return ''
    if (Array.isArray(value)) {
      return value.map(v => {
        if (typeof v === 'object' && v !== null) {
          return v.value || v.name || JSON.stringify(v)
        }
        return String(v)
      }).join(', ')
    }
    if (typeof value === 'object') {
      return value.value || value.name || JSON.stringify(value)
    }
    return String(value)
  }

  const renderPagination = (currentPage, total, pageSize, onPageChange) => {
    const totalPages = Math.ceil(total / pageSize)
    if (totalPages <= 1) return null
    
    return (
      <div className="pagination">
        <button
          className="btn btn-sm btn-default"
          disabled={currentPage === 1}
          onClick={() => onPageChange(currentPage - 1)}
        >
          上一页
        </button>
        <span className="pagination-info">
          第 {currentPage} 页 / 共 {totalPages} 页
        </span>
        <button
          className="btn btn-sm btn-default"
          disabled={currentPage === totalPages}
          onClick={() => onPageChange(currentPage + 1)}
        >
          下一页
        </button>
      </div>
    )
  }

  return (
    <div className="page-container">
      <h1 className="page-title">数据管理</h1>

      {message.text && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'import' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('import')
            setSelectedSnapshot(null)
            setFields([])
            setRows([])
          }}
        >
          导入数据
        </button>
        <button
          className={`tab-btn ${activeTab === 'existing' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('existing')
            setSelectedDataflow(null)
            setSelectedSnapshot(null)
            setFields([])
            setRows([])
            setSnapshotsPage(1)
          }}
        >
          已有数据
        </button>
      </div>

      {activeTab === 'import' && (
        <div className="tab-content">
          <div className="data-section">
            <h2 className="section-title" style={{ margin: 0, marginBottom: '16px' }}>选择数据流</h2>
            {loading ? (
              <div className="empty-state">
                <p>加载中...</p>
              </div>
            ) : dataflows.length === 0 ? (
              <div className="empty-state">
                <p>暂无数据流，请先到配置页面创建</p>
              </div>
            ) : (
              <div className="dataflow-selector">
                {dataflows.map((df) => (
                  <div
                    key={df.id}
                    className={`dataflow-option ${selectedDataflow?.id === df.id ? 'active' : ''}`}
                    onClick={() => handleSelectDataflowForImport(df)}
                  >
                    <div className="dataflow-option-name">{df.name}</div>
                    <div className="dataflow-option-id">
                      类型: {df.type === 'local' ? '本地' : '明道云'}
                      {df.type !== 'local' && ` | 工作表: ${df.worksheet_id}`}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedDataflow && (
            <div className="data-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 className="section-title" style={{ margin: 0 }}>
                  数据 - {selectedDataflow.name}
                </h2>
                <div className="btn-group" style={{ marginTop: 0 }}>
                  {rows.length > 0 && selectedDataflow.type !== 'local' && (
                    <button
                      className="btn btn-secondary"
                      onClick={handleOpenSaveModal}
                    >
                      保存
                    </button>
                  )}
                  {selectedDataflow.type !== 'local' && (
                    <button
                      className="btn btn-primary"
                      onClick={handleLoadData}
                      disabled={loadingData}
                    >
                      {loadingData ? '加载中...' : '从明道云加载'}
                    </button>
                  )}
                </div>
              </div>

              {rows.length === 0 ? (
                <div className="empty-state">
                  <p>
                    {selectedDataflow.type === 'local' 
                      ? '暂无数据，请先在配置页面导入文件' 
                      : '点击"从明道云加载"按钮查看数据'}
                  </p>
                </div>
              ) : (
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th style={{ width: '60px', textAlign: 'center' }}>#</th>
                        {fields.map((field) => (
                          <th key={field.field_id}>{field.field_name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={index}>
                          <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            {index + 1}
                          </td>
                          {fields.map((field) => (
                            <td key={field.field_id}>
                              {formatValue(row[field.field_name])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'existing' && (
        <div className="tab-content">
          <div className="data-section">
            <h2 className="section-title">数据快照列表</h2>
            {loading ? (
              <div className="empty-state">
                <p>加载中...</p>
              </div>
            ) : snapshots.length === 0 ? (
              <div className="empty-state">
                <p>暂无数据快照，请先到"导入数据"页面保存数据</p>
              </div>
            ) : (
              <>
                <div className="snapshot-list">
                  {snapshots.map((snapshot) => {
                    const dataflow = dataflowsMap[snapshot.data_flow_id]
                    return (
                      <div
                        key={snapshot.id}
                        className={`snapshot-item ${selectedSnapshot?.id === snapshot.id ? 'active' : ''}`}
                        onClick={() => handleSelectSnapshot(snapshot)}
                      >
                        <div className="snapshot-info">
                          <div className="snapshot-name">
                            {dataflow ? dataflow.name : '未知数据流'}
                          </div>
                          <div className="snapshot-time">
                            快照: {snapshot.name} | {new Date(snapshot.created_at).toLocaleString('zh-CN')}
                          </div>
                        </div>
                        <div className="snapshot-actions">
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteSnapshot(snapshot.id)
                            }}
                          >
                            删除
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
                {renderPagination(snapshotsPage, snapshotsTotal, snapshotsPageSize, (page) => {
                  setSnapshotsPage(page)
                })}
              </>
            )}
          </div>

          {selectedSnapshot && (
            <div className="data-section">
              <h2 className="section-title">
                数据明细 - {selectedSnapshot.name}
              </h2>
              {rows.length === 0 ? (
                <div className="empty-state">
                  <p>暂无数据</p>
                </div>
              ) : (
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th style={{ width: '60px', textAlign: 'center' }}>#</th>
                        {fields.map((field) => (
                          <th key={field.field_id}>{field.field_name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, index) => (
                        <tr key={index}>
                          <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                            {index + 1}
                          </td>
                          {fields.map((field) => (
                            <td key={field.field_id}>
                              {formatValue(row[field.field_name])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <Modal
        isOpen={isSaveModalOpen}
        onClose={() => setIsSaveModalOpen(false)}
        title="保存数据快照"
      >
        <div className="form-group">
          <label className="form-label">快照名称</label>
          <input
            type="text"
            className="form-input"
            value={snapshotName}
            onChange={(e) => setSnapshotName(e.target.value)}
            placeholder="请输入快照名称"
          />
        </div>
        <div className="btn-group">
          <button
            className="btn btn-default"
            onClick={() => setIsSaveModalOpen(false)}
          >
            取消
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSaveSnapshot}
          >
            保存
          </button>
        </div>
      </Modal>
    </div>
  )
}

export default DataPage
