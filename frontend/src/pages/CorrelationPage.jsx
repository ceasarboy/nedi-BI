import { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { analysisAPI, dataAPI } from '../services/api'

function CorrelationPage() {
  const [activeTab, setActiveTab] = useState('analysis')
  const [snapshots, setSnapshots] = useState([])
  const [selectedSnapshots, setSelectedSnapshots] = useState([])
  const [snapshotDataMap, setSnapshotDataMap] = useState({})
  const [selectedFields, setSelectedFields] = useState([])
  const [correlationMethod, setCorrelationMethod] = useState('pearson')
  const [correlationThresholdForAnalysis, setCorrelationThresholdForAnalysis] = useState(0.7)
  const [correlationThresholdForExplore, setCorrelationThresholdForExplore] = useState(0.8)
  const [correlationResult, setCorrelationResult] = useState(null)
  const [exploreResult, setExploreResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadSnapshots()
  }, [])

  const loadSnapshots = async () => {
    try {
      const response = await dataAPI.getAllSnapshots(1, 100)
      setSnapshots(response.data.data || [])
    } catch (error) {
      console.error('加载快照失败', error)
    }
  }

  const toggleSnapshot = async (snapshot) => {
    const isSelected = selectedSnapshots.find(s => s.id === snapshot.id)
    
    if (isSelected) {
      setSelectedSnapshots(prev => prev.filter(s => s.id !== snapshot.id))
      setSnapshotDataMap(prev => {
        const newMap = { ...prev }
        delete newMap[snapshot.id]
        return newMap
      })
      setSelectedFields(prev => prev.filter(f => f.snapshot_id !== snapshot.id))
    } else {
      setSelectedSnapshots(prev => [...prev, snapshot])
      try {
        const response = await analysisAPI.getSnapshot(snapshot.id)
        setSnapshotDataMap(prev => ({
          ...prev,
          [snapshot.id]: response.data.data
        }))
      } catch (error) {
        console.error('加载快照数据失败', error)
      }
    }
  }

  const toggleField = (snapshotId, fieldName) => {
    const existingIndex = selectedFields.findIndex(
      f => f.snapshot_id === snapshotId && f.field_name === fieldName
    )
    
    if (existingIndex >= 0) {
      setSelectedFields(prev => prev.filter((_, i) => i !== existingIndex))
    } else {
      const snapshot = selectedSnapshots.find(s => s.id === snapshotId)
      setSelectedFields(prev => [...prev, {
        snapshot_id: snapshotId,
        snapshot_name: snapshot?.name,
        field_name: fieldName
      }])
    }
  }

  const getNumericFields = (snapshotId) => {
    const data = snapshotDataMap[snapshotId]
    if (!data || !data.fields) return []
    return data.fields.filter(f => f.data_type === 'number' || f.data_type === 'numeric')
  }

  const isFieldSelected = (snapshotId, fieldName) => {
    return selectedFields.some(
      f => f.snapshot_id === snapshotId && f.field_name === fieldName
    )
  }

  const runCorrelationAnalysis = async () => {
    if (selectedFields.length < 2) {
      alert('请至少选择2个字段')
      return
    }

    setLoading(true)
    try {
      const requestData = {
        fields: selectedFields.map(f => ({
          snapshot_id: f.snapshot_id,
          field_name: f.field_name
        })),
        correlation_method: correlationMethod,
        correlation_threshold: correlationThresholdForAnalysis
      }

      const response = await analysisAPI.multiCorrelationAnalysis(requestData)
      setCorrelationResult(response.data)
      setExploreResult(null)
    } catch (error) {
      console.error('相关性分析失败', error)
      alert('相关性分析失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runCorrelationExplore = async () => {
    if (selectedFields.length < 2) {
      alert('请至少选择2个字段')
      return
    }

    setLoading(true)
    try {
      const requestData = {
        fields: selectedFields.map(f => ({
          snapshot_id: f.snapshot_id,
          field_name: f.field_name
        })),
        correlation_method: correlationMethod,
        correlation_threshold: correlationThresholdForExplore
      }

      const response = await analysisAPI.correlationExplore(requestData)
      setExploreResult(response.data)
      setCorrelationResult(null)
    } catch (error) {
      console.error('相关性探索失败', error)
      alert('相关性探索失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const getCorrelationChartOption = (chartData) => {
    if (!chartData || !chartData.values) return {}
    
    return {
      title: {
        text: '相关系数热力图',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function(params) {
          if (params && params.length > 0) {
            const data = params[0]
            return `${chartData.x[data.value[1]]} & ${chartData.y[data.value[0]]}<br/>相关系数: ${data.value[2]?.toFixed(4) || 'N/A'}`
          }
          return ''
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        top: '15%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.x,
        splitArea: { show: true },
        axisLabel: {
          interval: 0,
          rotate: 45
        }
      },
      yAxis: {
        type: 'category',
        data: chartData.y,
        splitArea: { show: true }
      },
      visualMap: {
        min: -1,
        max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
          color: ['#3b82f6', '#ffffff', '#ef4444']
        }
      },
      series: [
        {
          name: '相关系数',
          type: 'heatmap',
          data: chartData.values.map((row, i) => 
            row.map((value, j) => [j, i, value])
          ).flat(),
          label: {
            show: true,
            formatter: function(params) {
              return params.value[2]?.toFixed(2) || ''
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  }

  const correlationMethods = [
    { value: 'pearson', label: '皮尔逊 Pearson' },
    { value: 'spearman', label: '斯皮尔曼 Spearman' },
    { value: 'kendall', label: '肯德尔 Kendall' }
  ]

  return (
    <div className="page">
      <h1 className="page-title">相关性分析</h1>
      
      <div style={{ marginBottom: '16px', display: 'flex', gap: '8px' }}>
        {['analysis', 'explore'].map(tab => (
          <div
            key={tab}
            style={{
              padding: '10px 20px',
              borderRadius: '6px',
              cursor: 'pointer',
              background: activeTab === tab ? '#3b82f6' : '#f3f4f6',
              color: activeTab === tab ? '#fff' : '#374151',
              fontSize: '14px',
              fontWeight: activeTab === tab ? 600 : 400
            }}
            onClick={() => setActiveTab(tab)}>
            {tab === 'analysis' ? '相关性分析' : '相关性探索'}
          </div>
        ))}
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '16px', height: 'calc(100vh - 320px)' }}>
        {/* 左侧选择区域 */}
        <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择数据快照</h3>
          <div style={{ marginBottom: '16px' }}>
            {snapshots.map(s => (
              <div
                key={s.id}
                style={{
                  padding: '10px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  background: selectedSnapshots.find(ss => ss.id === s.id) ? '#eff6ff' : '#f9fafb',
                  border: selectedSnapshots.find(ss => ss.id === s.id) ? '2px solid #3b82f6' : '2px solid transparent',
                  marginBottom: '6px'
                }}
                onClick={() => toggleSnapshot(s)}>
                <span style={{ fontSize: '13px' }}>{s.name}</span>
              </div>
            ))}
          </div>

          {selectedSnapshots.length > 0 && (
            <>
              <div style={{ marginBottom: '16px', borderBottom: '1px solid #e5e7eb', paddingBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>已选字段</h3>
                <div style={{ marginBottom: '12px' }}>
                  {selectedSnapshots.map(snapshot => {
                    const numericFields = getNumericFields(snapshot.id)
                    if (numericFields.length === 0) return null
                    
                    return (
                      <div key={snapshot.id} style={{ marginBottom: '12px' }}>
                        <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '6px' }}>
                          {snapshot.name}
                        </div>
                        {numericFields.map(field => (
                          <label key={field.field_id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', cursor: 'pointer' }}>
                            <input
                              type="checkbox"
                              checked={isFieldSelected(snapshot.id, field.field_name)}
                              onChange={() => toggleField(snapshot.id, field.field_name)}
                            />
                            <span style={{ fontSize: '12px' }}>{field.field_name}</span>
                          </label>
                        ))}
                      </div>
                    )
                  })}
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>相关系数类型</h3>
                {correlationMethods.map(method => (
                  <label key={method.value} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="correlationMethod"
                      value={method.value}
                      checked={correlationMethod === method.value}
                      onChange={(e) => setCorrelationMethod(e.target.value)}
                    />
                    <span style={{ fontSize: '12px' }}>{method.label}</span>
                  </label>
                ))}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>相关性阈值</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={activeTab === 'analysis' ? correlationThresholdForAnalysis : correlationThresholdForExplore}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value) || 0
                      if (activeTab === 'analysis') {
                        setCorrelationThresholdForAnalysis(val)
                      } else {
                        setCorrelationThresholdForExplore(val)
                      }
                    }}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                  />
                </div>
                <p style={{ margin: '8px 0 0 0', fontSize: '11px', color: '#6b7280' }}>
                  默认: {activeTab === 'analysis' ? '0.7' : '0.8'}
                </p>
              </div>

              <button
                className="btn btn-primary"
                onClick={activeTab === 'analysis' ? runCorrelationAnalysis : runCorrelationExplore}
                disabled={selectedFields.length < 2 || loading}
                style={{ width: '100%' }}>
                {loading ? '分析中...' : (activeTab === 'analysis' ? '执行相关性分析' : '执行相关性探索')}
              </button>
            </>
          )}
        </div>

        {/* 右侧结果展示区域 */}
        <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
          {selectedSnapshots.length === 0 ? (
            <div className="empty-state" style={{ height: '100%' }}>
              <p>请选择数据快照开始{activeTab === 'analysis' ? '相关性分析' : '相关性探索'}</p>
            </div>
          ) : activeTab === 'analysis' && correlationResult ? (
            <div>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
                相关性分析结果 - {correlationMethods.find(m => m.value === correlationResult.correlation_method)?.label}
              </h3>

              <p style={{ margin: '0 0 16px 0', fontSize: '13px', color: '#6b7280' }}>
                相关性阈值: {correlationResult.correlation_threshold}
              </p>

              {/* 高相关变量对 */}
              {correlationResult.high_correlations && correlationResult.high_correlations.length > 0 && (
                <div style={{ background: '#fef3c7', border: '1px solid #fbbf24', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#92400e' }}>高相关变量对（|r| &gt; {correlationResult.correlation_threshold}）</h4>
                  <table style={{ width: '100%', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #fbbf24' }}>
                        <th style={{ textAlign: 'left', padding: '8px 0' }}>变量1</th>
                        <th style={{ textAlign: 'left', padding: '8px 0' }}>变量2</th>
                        <th style={{ textAlign: 'right', padding: '8px 0' }}>相关系数</th>
                        <th style={{ textAlign: 'center', padding: '8px 0' }}>类型</th>
                      </tr>
                    </thead>
                    <tbody>
                      {correlationResult.high_correlations.map((item, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #fef3c7' }}>
                          <td style={{ padding: '8px 0' }}>{item.field1}</td>
                          <td style={{ padding: '8px 0' }}>{item.field2}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>{item.correlation}</td>
                          <td style={{ textAlign: 'center' }}>
                            <span style={{ 
                              color: item.type === '强正相关' ? '#16a34a' : '#dc2626',
                              fontWeight: 600
                            }}>
                              {item.type}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* 相关系数热力图 */}
              {correlationResult.chart_data && (
                <div style={{ marginBottom: '20px', height: '500px' }}>
                  <ReactECharts 
                    option={getCorrelationChartOption(correlationResult.chart_data)}
                    style={{ height: '100%', width: '100%' }}
                  />
                </div>
              )}

              {/* 相关系数矩阵 */}
              <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>相关系数矩阵</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                        <th style={{ textAlign: 'left', padding: '8px' }}></th>
                        {correlationResult.fields.map((field, idx) => (
                          <th key={idx} style={{ textAlign: 'center', padding: '8px', fontSize: '11px' }}>
                            {field.snapshot_name}-{field.field_name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {correlationResult.correlation_matrix.map((row, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                          <td style={{ padding: '8px', fontWeight: 600, fontSize: '11px' }}>
                            {correlationResult.fields[i]?.snapshot_name}-{correlationResult.fields[i]?.field_name}
                          </td>
                          {row.map((value, j) => (
                            <td 
                              key={j} 
                              style={{ 
                                textAlign: 'center', 
                                padding: '8px',
                                background: value > correlationResult.correlation_threshold ? 'rgba(239, 68, 68, 0.2)' : 
                                           value < -correlationResult.correlation_threshold ? 'rgba(59, 130, 246, 0.2)' : 'transparent'
                              }}>
                              {value?.toFixed(4) || 'N/A'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : activeTab === 'explore' && exploreResult ? (
            <div>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
                相关性探索结果 - {correlationMethods.find(m => m.value === exploreResult.correlation_method)?.label}
              </h3>

              <div style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1e40af' }}>分析统计</h4>
                <p style={{ margin: '0', fontSize: '13px' }}>
                  总共分析了 <strong>{exploreResult.total_pairs}</strong> 对字段组合，
                  发现 <strong>{exploreResult.high_correlation_count}</strong> 对高相关字段
                  （|r| &gt; {exploreResult.correlation_threshold}）
                </p>
              </div>

              {exploreResult.high_correlation_pairs && exploreResult.high_correlation_pairs.length > 0 ? (
                <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>高相关字段对（按相关系数排序）</h4>
                  <table style={{ width: '100%', fontSize: '13px', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                        <th style={{ textAlign: 'left', padding: '10px 8px' }}>字段1</th>
                        <th style={{ textAlign: 'left', padding: '10px 8px' }}>字段2</th>
                        <th style={{ textAlign: 'right', padding: '10px 8px' }}>相关系数</th>
                        <th style={{ textAlign: 'center', padding: '10px 8px' }}>类型</th>
                      </tr>
                    </thead>
                    <tbody>
                      {exploreResult.high_correlation_pairs.map((item, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                          <td style={{ padding: '10px 8px' }}>
                            <div style={{ fontSize: '12px', color: '#6b7280' }}>{item.field1.snapshot_name}</div>
                            <div style={{ fontSize: '13px', fontWeight: 500 }}>{item.field1.field_name}</div>
                          </td>
                          <td style={{ padding: '10px 8px' }}>
                            <div style={{ fontSize: '12px', color: '#6b7280' }}>{item.field2.snapshot_name}</div>
                            <div style={{ fontSize: '13px', fontWeight: 500 }}>{item.field2.field_name}</div>
                          </td>
                          <td style={{ textAlign: 'right', padding: '10px 8px', fontWeight: 600, fontSize: '14px' }}>
                            {item.correlation}
                          </td>
                          <td style={{ textAlign: 'center', padding: '10px 8px' }}>
                            <span style={{ 
                              padding: '4px 12px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: 600,
                              background: item.type === '强正相关' ? '#dcfce7' : '#fee2e2',
                              color: item.type === '强正相关' ? '#166534' : '#991b1b'
                            }}>
                              {item.type}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state" style={{ height: '100%' }}>
                  <p>没有发现高相关字段对（|r| &gt; {exploreResult.correlation_threshold}）</p>
                  <p style={{ fontSize: '13px', color: '#6b7280' }}>尝试降低相关性阈值</p>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state" style={{ height: '100%' }}>
              <p>选择字段并执行{activeTab === 'analysis' ? '相关性分析' : '相关性探索'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CorrelationPage
