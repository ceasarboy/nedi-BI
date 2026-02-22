import { useState, useEffect } from 'react'
import { dataAPI, analysisAPI, dataflowAPI } from '../services/api'
import Modal from '../components/Modal'
import AdvancedStats from '../components/AdvancedStats'

function AnalysisPage() {
  const [activeTab, setActiveTab] = useState('aggregate')
  const [snapshots, setSnapshots] = useState([])
  const [dataflows, setDataflows] = useState([])
  const [dataflowsMap, setDataflowsMap] = useState({})
  const [selectedSnapshots, setSelectedSnapshots] = useState([])
  const [aggregateType, setAggregateType] = useState('union_all')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false)
  const [snapshotName, setSnapshotName] = useState('')
  const [saving, setSaving] = useState(false)
  
  const [selectedSnapshotForFilter, setSelectedSnapshotForFilter] = useState(null)
  const [snapshotData, setSnapshotData] = useState(null)
  const [filterConditions, setFilterConditions] = useState([])
  const [filterResult, setFilterResult] = useState(null)
  
  const [selectedSnapshotForStats, setSelectedSnapshotForStats] = useState(null)
  const [snapshotDataForStats, setSnapshotDataForStats] = useState(null)
  const [groupByField, setGroupByField] = useState(null)
  const [statsFields, setStatsFields] = useState([])
  const [statsResult, setStatsResult] = useState(null)
  const [allowConvertToNumber, setAllowConvertToNumber] = useState(false)
  
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [snapshotsRes, dataflowsRes] = await Promise.all([
        dataAPI.getAllSnapshots(1, 1000),
        dataflowAPI.getAll(1, 1000)
      ])
      setSnapshots(snapshotsRes.data.data)
      setDataflows(dataflowsRes.data)
      
      const dfMap = {}
      dataflowsRes.data.forEach(df => {
        dfMap[df.id] = df
      })
      setDataflowsMap(dfMap)
    } catch (error) {
      console.error('加载数据失败', error)
    }
  }

  const toggleSnapshot = (snapshot) => {
    setSelectedSnapshots(prev => {
      if (prev.find(s => s.id === snapshot.id)) {
        return prev.filter(s => s.id !== snapshot.id)
      } else {
        return [...prev, snapshot]
      }
    })
  }

  const handleAggregate = async () => {
    if (selectedSnapshots.length < 2) {
      alert('请至少选择两个数据快照')
      return
    }
    setLoading(true)
    try {
      const response = await analysisAPI.aggregate({
        snapshot_ids: selectedSnapshots.map(s => s.id),
        aggregate_type: aggregateType
      })
      setResult(response.data)
    } catch (error) {
      console.error('聚合失败', error)
      alert('聚合失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleOpenSaveModal = () => {
    const names = selectedSnapshots.map(s => s.name).join(' + ')
    setSnapshotName(`聚合结果 - ${names}`)
    setIsSaveModalOpen(true)
  }

  const handleSaveSnapshot = async () => {
    if (!result || !result.fields || !result.rows) {
      alert('没有可保存的数据')
      return
    }
    
    setSaving(true)
    try {
      await dataAPI.createSnapshot({
        dataflow_id: 0,
        name: snapshotName,
        fields: JSON.stringify(result.fields),
        data: JSON.stringify(result.rows)
      })
      
      alert('保存成功！')
      setIsSaveModalOpen(false)
    } catch (error) {
      console.error('保存失败', error)
      alert('保存失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
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

  const handleSelectSnapshotForFilter = async (snapshot) => {
    setSelectedSnapshotForFilter(snapshot)
    setSnapshotData(null)
    setFilterConditions([])
    setFilterResult(null)
  }

  const loadSnapshotDataForFilter = async () => {
    if (!selectedSnapshotForFilter) return
    
    setLoading(true)
    try {
      const response = await dataAPI.getSnapshot(selectedSnapshotForFilter.id)
      let snapshotDataFromAPI = response.data.data
      
      const dataflowId = selectedSnapshotForFilter.data_flow_id
      if (dataflowId && dataflowId > 0) {
        try {
          const fieldsRes = await dataAPI.getEnabledFields(dataflowId)
          const dataflowFields = fieldsRes.data.data
          
          const fieldTypeMap = {}
          dataflowFields.forEach(f => {
            fieldTypeMap[f.field_id] = f.data_type
          })
          
          snapshotDataFromAPI = {
            ...snapshotDataFromAPI,
            fields: snapshotDataFromAPI.fields.map(f => ({
              ...f,
              data_type: f.data_type || fieldTypeMap[f.field_id] || 'text'
            }))
          }
        } catch (e) {
          console.error('加载数据流字段失败', e)
        }
      }
      
      setSnapshotData(snapshotDataFromAPI)
    } catch (error) {
      console.error('加载快照数据失败', error)
    } finally {
      setLoading(false)
    }
  }

  const addFilterCondition = () => {
    if (!snapshotData || snapshotData.fields.length === 0) return
    setFilterConditions(prev => [...prev, {
      field_id: snapshotData.fields[0].field_id,
      operator: 'equals',
      value: ''
    }])
  }

  const removeFilterCondition = (index) => {
    setFilterConditions(prev => prev.filter((_, i) => i !== index))
  }

  const updateFilterCondition = (index, field, value) => {
    setFilterConditions(prev => {
      const newConditions = [...prev]
      newConditions[index][field] = value
      return newConditions
    })
  }

  const getOperatorsByType = (dataType) => {
    switch (dataType) {
      case 'text':
        return [
          { value: 'equals', label: '等于' },
          { value: 'not_equals', label: '不等于' },
          { value: 'contains', label: '包含' },
          { value: 'not_contains', label: '不包含' },
          { value: 'is_null', label: '为空' },
          { value: 'is_not_null', label: '不为空' }
        ]
      case 'number':
        return [
          { value: 'equals', label: '等于' },
          { value: 'not_equals', label: '不等于' },
          { value: 'greater_than', label: '大于' },
          { value: 'greater_equal', label: '大于等于' },
          { value: 'less_than', label: '小于' },
          { value: 'less_equal', label: '小于等于' },
          { value: 'is_null', label: '为空' },
          { value: 'is_not_null', label: '不为空' }
        ]
      case 'date':
      case 'datetime':
        return [
          { value: 'is_null', label: '为空' },
          { value: 'is_not_null', label: '不为空' },
          { value: 'before', label: '之前' },
          { value: 'after', label: '之后' },
          { value: 'equals', label: '是' },
          { value: 'before_or_equal', label: '之前（包含）' },
          { value: 'after_or_equal', label: '之后（包含）' }
        ]
      default:
        return [
          { value: 'equals', label: '等于' },
          { value: 'not_equals', label: '不等于' },
          { value: 'is_null', label: '为空' },
          { value: 'is_not_null', label: '不为空' }
        ]
    }
  }

  const getFieldUniqueValues = (fieldName) => {
    if (!snapshotData) return []
    const values = [...new Set(snapshotData.rows.map(row => row[fieldName]).filter(v => v !== null && v !== undefined))]
    return values.slice(0, 50)
  }

  const parseDate = (dateStr) => {
    if (!dateStr) return null
    
    if (dateStr instanceof Date) return dateStr
    
    const str = String(dateStr).trim()
    
    const chineseMatch = str.match(/^(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/)
    if (chineseMatch) {
      const [, year, month, day, hour, minute, second] = chineseMatch
      const date = new Date(
        parseInt(year), 
        parseInt(month) - 1, 
        parseInt(day), 
        parseInt(hour), 
        parseInt(minute), 
        second ? parseInt(second) : 0
      )
      return date
    }
    
    const dateOnlyMatch = str.match(/^(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})$/)
    if (dateOnlyMatch) {
      const [, year, month, day] = dateOnlyMatch
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    }
    
    const datetimeLocalMatch = str.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
    if (datetimeLocalMatch) {
      const [, year, month, day, hour, minute] = datetimeLocalMatch
      const date = new Date(
        parseInt(year), 
        parseInt(month) - 1, 
        parseInt(day), 
        parseInt(hour), 
        parseInt(minute)
      )
      return date
    }
    
    const date = new Date(str)
    if (!isNaN(date.getTime())) {
      return date
    }
    
    return null
  }

  const executeFilter = () => {
    if (!snapshotData) {
      alert('请先选择数据快照并加载数据')
      return
    }
    
    let filteredRows = [...snapshotData.rows]
    
    filterConditions.forEach(condition => {
      const field = snapshotData.fields.find(f => f.field_id === condition.field_id)
      if (!field) return
      
      const fieldName = field.field_name
      const operator = condition.operator
      const conditionValue = condition.value
      const dataType = field.data_type
      
      filteredRows = filteredRows.filter(row => {
        const rowValue = row[fieldName]
        
        if (dataType === 'date' || dataType === 'datetime') {
          const rowDate = parseDate(rowValue)
          const condDate = parseDate(conditionValue)
          
          switch (operator) {
            case 'equals':
              if (!rowDate || !condDate) return false
              return rowDate.getTime() === condDate.getTime()
            case 'not_equals':
              if (!rowDate || !condDate) return true
              return rowDate.getTime() !== condDate.getTime()
            case 'before':
              if (!rowDate || !condDate) return false
              return rowDate < condDate
            case 'after':
              if (!rowDate || !condDate) return false
              return rowDate > condDate
            case 'before_or_equal':
              if (!rowDate || !condDate) return false
              return rowDate <= condDate
            case 'after_or_equal':
              if (!rowDate || !condDate) return false
              return rowDate >= condDate
            case 'is_null':
              return rowValue === null || rowValue === undefined
            case 'is_not_null':
              return rowValue !== null && rowValue !== undefined
            default:
              return true
          }
        } else if (dataType === 'number') {
          const rowNum = Number(rowValue)
          const condNum = Number(conditionValue)
          
          switch (operator) {
            case 'equals':
              return rowNum === condNum
            case 'not_equals':
              return rowNum !== condNum
            case 'greater_than':
              return rowNum > condNum
            case 'greater_equal':
              return rowNum >= condNum
            case 'less_than':
              return rowNum < condNum
            case 'less_equal':
              return rowNum <= condNum
            case 'is_null':
              return rowValue === null || rowValue === undefined
            case 'is_not_null':
              return rowValue !== null && rowValue !== undefined
            default:
              return true
          }
        } else {
          const rowStr = String(rowValue || '')
          const condStr = String(conditionValue || '')
          
          switch (operator) {
            case 'equals':
              return rowStr === condStr
            case 'not_equals':
              return rowStr !== condStr
            case 'contains':
              return rowStr.includes(condStr)
            case 'not_contains':
              return !rowStr.includes(condStr)
            case 'is_null':
              return rowValue === null || rowValue === undefined
            case 'is_not_null':
              return rowValue !== null && rowValue !== undefined
            default:
              return true
          }
        }
      })
    })
    
    setFilterResult({
      fields: snapshotData.fields,
      rows: filteredRows
    })
  }

  const handleSelectSnapshotForStats = async (snapshot) => {
    setSelectedSnapshotForStats(snapshot)
    setSnapshotDataForStats(null)
    setGroupByField(null)
    setStatsFields([])
    setStatsResult(null)
    
    setLoading(true)
    try {
      const response = await dataAPI.getSnapshot(snapshot.id)
      let snapshotDataFromAPI = response.data.data
      
      const dataflowId = snapshot.data_flow_id
      if (dataflowId && dataflowId > 0) {
        try {
          const fieldsRes = await dataAPI.getEnabledFields(dataflowId)
          const dataflowFields = fieldsRes.data.data
          
          const fieldTypeMap = {}
          dataflowFields.forEach(f => {
            fieldTypeMap[f.field_id] = f.data_type
          })
          
          snapshotDataFromAPI = {
            ...snapshotDataFromAPI,
            fields: snapshotDataFromAPI.fields.map(f => ({
              ...f,
              data_type: f.data_type || fieldTypeMap[f.field_id] || 'text'
            }))
          }
        } catch (e) {
          console.error('加载数据流字段失败', e)
        }
      }
      
      setSnapshotDataForStats(snapshotDataFromAPI)
    } catch (error) {
      console.error('加载快照数据失败', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleStatsField = (fieldId) => {
    setStatsFields(prev => {
      if (prev.includes(fieldId)) {
        return prev.filter(id => id !== fieldId)
      } else {
        return [...prev, fieldId]
      }
    })
  }

  const executeStats = async () => {
    if (!selectedSnapshotForStats || !snapshotDataForStats) {
      alert('请先选择数据快照')
      return
    }
    
    if (statsFields.length === 0) {
      alert('请至少选择一个要统计的字段')
      return
    }
    
    setLoading(true)
    try {
      const { fields, rows } = snapshotDataForStats
      
      const selectedFieldsList = fields.filter(f => statsFields.includes(f.field_id))
      
      if (selectedFieldsList.length === 0) {
        alert('没有可统计的字段')
        setLoading(false)
        return
      }
      
      let groupedData = {}
      
      if (groupByField) {
        const groupField = fields.find(f => f.field_id === groupByField)
        if (groupField) {
          rows.forEach(row => {
            const key = row[groupField.field_name] || '空值'
            if (!groupedData[key]) {
              groupedData[key] = []
            }
            groupedData[key].push(row)
          })
        }
      } else {
        groupedData['全部'] = rows
      }
      
      const statsResults = []
      
      Object.keys(groupedData).forEach(groupKey => {
        const groupRows = groupedData[groupKey]
        const result = {}
        
        if (groupByField) {
          const groupField = fields.find(f => f.field_id === groupByField)
          result[groupField.field_name] = groupKey
        }
        
        selectedFieldsList.forEach(field => {
          const values = groupRows.map(row => {
            const v = row[field.field_name]
            if (v === null || v === undefined) return null
            const num = Number(v)
            return isNaN(num) ? null : num
          }).filter(v => v !== null)
          
          if (values.length > 0) {
            const nums = values
            const sum = nums.reduce((a, b) => a + b, 0)
            const mean = sum / nums.length
            const min = Math.min(...nums)
            const max = Math.max(...nums)
            
            result[`${field.field_name}_计数`] = nums.length
            result[`${field.field_name}_求和`] = sum
            result[`${field.field_name}_平均值`] = parseFloat(mean.toFixed(2))
            result[`${field.field_name}_最小值`] = min
            result[`${field.field_name}_最大值`] = max
          }
        })
        
        statsResults.push(result)
      })
      
      const resultFields = []
      if (groupByField) {
        const groupField = fields.find(f => f.field_id === groupByField)
        resultFields.push({ field_id: groupField.field_id, field_name: groupField.field_name, data_type: groupField.data_type })
      }
      
      selectedFieldsList.forEach(field => {
        resultFields.push({ field_id: `${field.field_id}_count`, field_name: `${field.field_name}_计数`, data_type: 'number' })
        resultFields.push({ field_id: `${field.field_id}_sum`, field_name: `${field.field_name}_求和`, data_type: 'number' })
        resultFields.push({ field_id: `${field.field_id}_mean`, field_name: `${field.field_name}_平均值`, data_type: 'number' })
        resultFields.push({ field_id: `${field.field_id}_min`, field_name: `${field.field_name}_最小值`, data_type: 'number' })
        resultFields.push({ field_id: `${field.field_id}_max`, field_name: `${field.field_name}_最大值`, data_type: 'number' })
      })
      
      setStatsResult({
        fields: resultFields,
        rows: statsResults
      })
    } catch (error) {
      console.error('统计失败', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenSaveModalForResult = (resultData, defaultName) => {
    setResult(resultData)
    setSnapshotName(defaultName)
    setIsSaveModalOpen(true)
  }

  return (
    <div className="page-container" style={{ padding: '16px', height: 'calc(100vh - 100px)' }}>
      <div>
        <h1 className="page-title">数据分析</h1>
        
        <div style={{ marginBottom: '20px', borderBottom: '2px solid #e5e7eb' }}>
          <div style={{ display: 'flex', gap: '4px' }}>
            <div
              style={{
                padding: '12px 24px',
                borderRadius: '6px 6px 0 0',
                cursor: 'pointer',
                background: activeTab === 'aggregate' ? '#3b82f6' : 'transparent',
                color: activeTab === 'aggregate' ? '#fff' : '#374151',
                fontWeight: activeTab === 'aggregate' ? 600 : 400
              }}
              onClick={() => setActiveTab('aggregate')}>
              多表聚合
            </div>
            <div
              style={{
                padding: '12px 24px',
                borderRadius: '6px 6px 0 0',
                cursor: 'pointer',
                background: activeTab === 'filter' ? '#3b82f6' : 'transparent',
                color: activeTab === 'filter' ? '#fff' : '#374151',
                fontWeight: activeTab === 'filter' ? 600 : 400
              }}
              onClick={() => setActiveTab('filter')}>
              字段筛选
            </div>
            <div
              style={{
                padding: '12px 24px',
                borderRadius: '6px 6px 0 0',
                cursor: 'pointer',
                background: activeTab === 'stats' ? '#3b82f6' : 'transparent',
                color: activeTab === 'stats' ? '#fff' : '#374151',
                fontWeight: activeTab === 'stats' ? 600 : 400
              }}
              onClick={() => setActiveTab('stats')}>
              数据统计
            </div>
            <div
              style={{
                padding: '12px 24px',
                borderRadius: '6px 6px 0 0',
                cursor: 'pointer',
                background: activeTab === 'advanced' ? '#3b82f6' : 'transparent',
                color: activeTab === 'advanced' ? '#fff' : '#374151',
                fontWeight: activeTab === 'advanced' ? 600 : 400
              }}
              onClick={() => setActiveTab('advanced')}>
              高级统计
            </div>
          </div>
        </div>

        {activeTab === 'aggregate' && (
          <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '16px', height: 'calc(100vh - 260px)' }}>
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
                      background: selectedSnapshots.find(snap => snap.id === s.id) ? '#eff6ff' : '#f9fafb',
                      border: selectedSnapshots.find(snap => snap.id === s.id) ? '2px solid #3b82f6' : '2px solid transparent',
                      marginBottom: '6px'
                    }}
                    onClick={() => toggleSnapshot(s)}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        checked={selectedSnapshots.find(snap => snap.id === s.id) ? true : false}
                        onChange={() => toggleSnapshot(s)}
                        style={{ marginRight: '4px' }}
                      />
                      <span style={{ fontSize: '13px' }}>{s.name}</span>
                    </div>
                  </div>
                ))}
              </div>

              <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>聚合方式</h3>
              <div style={{ marginBottom: '16px' }}>
                {[
                  { id: 'union_all', name: 'UNION ALL（合并所有）', desc: '合并所有数据，包括重复记录。保留所有快照中的所有数据行。' },
                  { id: 'union', name: 'UNION（合并去重）', desc: '合并数据并去除重复记录。相同的数据行只保留一份。' },
                  { id: 'join', name: 'JOIN（内连接）', desc: '通过共同列连接，只保留在所有快照中都存在的记录。' },
                  { id: 'left_join', name: 'LEFT JOIN（左连接）', desc: '保留第一个快照的所有记录，匹配其他快照的数据，不匹配的字段为空。' },
                  { id: 'right_join', name: 'RIGHT JOIN（右连接）', desc: '保留最后一个快照的所有记录，匹配其他快照的数据，不匹配的字段为空。' },
                  { id: 'full_join', name: 'FULL JOIN（全连接）', desc: '保留所有快照的所有记录，匹配到的数据合并，不匹配的字段为空。' }
                ].map(type => (
                  <div
                    key={type.id}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: aggregateType === type.id ? '#eff6ff' : 'transparent',
                      border: aggregateType === type.id ? '1px solid #3b82f6' : '1px solid transparent',
                      marginBottom: '4px',
                      position: 'relative'
                    }}
                    onClick={() => setAggregateType(type.id)}
                    onMouseEnter={(e) => {
                      const tooltip = document.createElement('div')
                      tooltip.id = `tooltip-${type.id}`
                      tooltip.style.cssText = `
                        position: fixed;
                        background: #1f2937;
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        max-width: 250px;
                        z-index: 9999;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        pointer-events: none;
                      `
                      tooltip.textContent = type.desc
                      document.body.appendChild(tooltip)
                      
                      const rect = e.currentTarget.getBoundingClientRect()
                      tooltip.style.left = `${rect.right + 12}px`
                      tooltip.style.top = `${rect.top}px`
                    }}
                    onMouseLeave={() => {
                      const tooltip = document.getElementById(`tooltip-${type.id}`)
                      if (tooltip) {
                        tooltip.remove()
                      }
                    }}>
                    <span style={{ fontSize: '13px' }}>{type.name}</span>
                    <span style={{ fontSize: '11px', color: '#9ca3af', marginLeft: '4px' }}>ⓘ</span>
                  </div>
                ))}
              </div>

              <button
                className="btn btn-primary"
                onClick={handleAggregate}
                disabled={loading || selectedSnapshots.length < 2}
                style={{ width: '100%' }}>
                {loading ? '聚合中...' : '执行聚合'}
              </button>
            </div>

            <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
              {result && result.fields && result.rows ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                      聚合结果 ({result.rows.length} 行)
                    </h3>
                    <button
                      className="btn btn-primary"
                      onClick={handleOpenSaveModal}
                    >
                      保存为新快照
                    </button>
                  </div>
                  <div className="data-table-container" style={{ maxHeight: 'calc(100vh - 320px)' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th style={{ width: '60px', textAlign: 'center' }}>#</th>
                          {result.fields.map((field) => (
                            <th key={field.field_id}>{field.field_name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.rows.slice(0, 100).map((row, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                              {index + 1}
                            </td>
                            {result.fields.map((field) => (
                              <td key={field.field_id}>
                                {formatValue(row[field.field_name])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {result.rows.length > 100 && (
                    <div style={{ textAlign: 'center', padding: '8px', color: '#64748b', fontSize: '12px' }}>
                      仅显示前 100 行，保存为快照可查看完整数据
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-state" style={{ height: '100%' }}>
                  <p>请选择数据快照和聚合方式</p>
                  <p style={{ fontSize: '12px', color: '#64748b', marginTop: '8px' }}>至少需要选择 2 个数据快照</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'filter' && (
          <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '16px', height: 'calc(100vh - 260px)' }}>
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
                      background: selectedSnapshotForFilter?.id === s.id ? '#eff6ff' : '#f9fafb',
                      border: selectedSnapshotForFilter?.id === s.id ? '2px solid #3b82f6' : '2px solid transparent',
                      marginBottom: '6px'
                    }}
                    onClick={() => handleSelectSnapshotForFilter(s)}>
                    <span style={{ fontSize: '13px' }}>{s.name}</span>
                  </div>
                ))}
              </div>
              
              {selectedSnapshotForFilter && !snapshotData && (
                <button
                  className="btn btn-primary"
                  onClick={loadSnapshotDataForFilter}
                  disabled={loading}
                  style={{ width: '100%', marginBottom: '16px' }}>
                  {loading ? '加载中...' : '加载数据'}
                </button>
              )}

              {snapshotData && (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '16px 0 12px 0' }}>
                    <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>筛选条件</h3>
                    <button
                      className="btn btn-default"
                      onClick={addFilterCondition}
                      style={{ padding: '4px 12px', fontSize: '12px' }}>
                      + 添加条件
                    </button>
                  </div>
                  
                  <div style={{ marginBottom: '16px' }}>
                    {filterConditions.length === 0 ? (
                      <div style={{ padding: '16px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
                        点击"添加条件"开始筛选
                      </div>
                    ) : (
                      filterConditions.map((condition, index) => {
                        const field = snapshotData.fields.find(f => f.field_id === condition.field_id)
                        const dataType = field?.data_type || 'text'
                        const operators = getOperatorsByType(dataType)
                        const needsValue = condition.operator !== 'is_null' && condition.operator !== 'is_not_null'
                        
                        return (
                          <div key={index} style={{ padding: '12px', background: '#f9fafb', borderRadius: '6px', marginBottom: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                              <span style={{ fontSize: '12px', color: '#64748b' }}>条件 {index + 1}</span>
                              <button
                                onClick={() => removeFilterCondition(index)}
                                style={{ border: 'none', background: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '12px' }}>
                                删除
                              </button>
                            </div>
                            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                              <select
                                value={condition.field_id}
                                onChange={(e) => {
                                  const newField = snapshotData.fields.find(f => f.field_id === e.target.value)
                                  const newOperators = getOperatorsByType(newField?.data_type || 'text')
                                  updateFilterCondition(index, 'field_id', e.target.value)
                                  updateFilterCondition(index, 'operator', newOperators[0]?.value || 'equals')
                                }}
                                style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}>
                                {snapshotData.fields.map(f => (
                                  <option key={f.field_id} value={f.field_id}>{f.field_name} ({f.data_type})</option>
                                ))}
                              </select>
                            </div>
                            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                              <select
                                value={condition.operator}
                                onChange={(e) => updateFilterCondition(index, 'operator', e.target.value)}
                                style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}>
                                {operators.map(op => (
                                  <option key={op.value} value={op.value}>{op.label}</option>
                                ))}
                              </select>
                            </div>
                            {needsValue && (
                              <input
                                type={dataType === 'date' || dataType === 'datetime' ? 'datetime-local' : 'text'}
                                value={condition.value}
                                onChange={(e) => updateFilterCondition(index, 'value', e.target.value)}
                                placeholder={dataType === 'date' || dataType === 'datetime' ? '选择日期时间' : '输入值...'}
                                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                              />
                            )}
                          </div>
                        )
                      })
                    )}
                  </div>

                  <button
                    className="btn btn-primary"
                    onClick={executeFilter}
                    disabled={filterConditions.length === 0}
                    style={{ width: '100%' }}>
                    执行筛选
                  </button>
                </>
              )}
            </div>

            <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
              {filterResult && filterResult.fields && filterResult.rows ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                      筛选结果 ({filterResult.rows.length} 行 / 共 {snapshotData?.rows?.length || 0} 行)
                    </h3>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleOpenSaveModalForResult(filterResult, `筛选结果 - ${selectedSnapshotForFilter?.name}`)}
                    >
                      保存为新快照
                    </button>
                  </div>
                  <div className="data-table-container" style={{ maxHeight: 'calc(100vh - 320px)' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th style={{ width: '60px', textAlign: 'center' }}>#</th>
                          {filterResult.fields.map((field) => (
                            <th key={field.field_id}>{field.field_name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {filterResult.rows.slice(0, 100).map((row, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                              {index + 1}
                            </td>
                            {filterResult.fields.map((field) => (
                              <td key={field.field_id}>
                                {formatValue(row[field.field_name])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {filterResult.rows.length > 100 && (
                    <div style={{ textAlign: 'center', padding: '8px', color: '#64748b', fontSize: '12px' }}>
                      仅显示前 100 行，保存为快照可查看完整数据
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-state" style={{ height: '100%' }}>
                  <p>请选择数据快照并添加筛选条件</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'stats' && (
          <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '16px', height: 'calc(100vh - 260px)' }}>
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
                      background: selectedSnapshotForStats?.id === s.id ? '#eff6ff' : '#f9fafb',
                      border: selectedSnapshotForStats?.id === s.id ? '2px solid #3b82f6' : '2px solid transparent',
                      marginBottom: '6px'
                    }}
                    onClick={() => handleSelectSnapshotForStats(s)}>
                    <span style={{ fontSize: '13px' }}>{s.name}</span>
                  </div>
                ))}
              </div>

              {selectedSnapshotForStats && snapshotDataForStats && (
                <>
                  <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>分组字段（可选）</h3>
                  <div style={{ marginBottom: '16px' }}>
                    <select
                      value={groupByField || ''}
                      onChange={(e) => setGroupByField(e.target.value || null)}
                      style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}>
                      <option value="">不分组（统计全部）</option>
                      {snapshotDataForStats.fields.map(f => (
                        <option key={f.field_id} value={f.field_id}>{f.field_name}</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ margin: '16px 0 12px 0' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={allowConvertToNumber}
                        onChange={(e) => setAllowConvertToNumber(e.target.checked)}
                      />
                      <span style={{ fontSize: '13px', color: '#374151' }}>允许将文本等字段转为数值</span>
                    </label>
                  </div>
                  
                  <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择要统计的字段</h3>
                  <div style={{ marginBottom: '16px' }}>
                    {(() => {
                      let availableFields = snapshotDataForStats.fields
                      if (!allowConvertToNumber) {
                        availableFields = availableFields.filter(f => f.data_type === 'number')
                      }
                      if (availableFields.length === 0) {
                        return (
                          <div style={{ padding: '12px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
                            {allowConvertToNumber ? '没有可统计的字段' : '没有数值型字段可统计，请勾选"允许将文本等字段转为数值"'}
                          </div>
                        )
                      }
                      return availableFields.map(field => (
                        <div
                          key={field.field_id}
                          style={{
                            padding: '8px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            background: statsFields.includes(field.field_id) ? '#eff6ff' : 'transparent',
                            border: statsFields.includes(field.field_id) ? '1px solid #3b82f6' : '1px solid transparent',
                            marginBottom: '4px'
                          }}
                          onClick={() => toggleStatsField(field.field_id)}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <input
                              type="checkbox"
                              checked={statsFields.includes(field.field_id)}
                              onChange={() => toggleStatsField(field.field_id)}
                              style={{ marginRight: '4px' }}
                            />
                            <span style={{ fontSize: '13px' }}>
                              {field.field_name}
                              {allowConvertToNumber && field.data_type !== 'number' && (
                                <span style={{ color: '#64748b', fontSize: '11px', marginLeft: '4px' }}>
                                  ({field.data_type} → 数值)
                                </span>
                              )}
                            </span>
                          </div>
                        </div>
                      ))
                    })()}
                  </div>

                  <button
                    className="btn btn-primary"
                    onClick={executeStats}
                    disabled={loading || statsFields.length === 0}
                    style={{ width: '100%' }}>
                    {loading ? '统计中...' : '执行统计'}
                  </button>
                </>
              )}
            </div>

            <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
              {statsResult && statsResult.fields && statsResult.rows ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                      统计结果 ({statsResult.rows.length} 组)
                    </h3>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleOpenSaveModalForResult({ fields: statsResult.fields, rows: statsResult.rows }, `统计结果 - ${selectedSnapshotForStats?.name}`)}
                    >
                      保存为新快照
                    </button>
                  </div>
                  <div className="data-table-container" style={{ maxHeight: 'calc(100vh - 320px)' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          {statsResult.fields.map((field) => (
                          <th key={field.field_id} style={field.data_type === 'number' ? { textAlign: 'right' } : {}}>
                            {field.field_name}
                          </th>
                        ))}
                        </tr>
                      </thead>
                      <tbody>
                        {statsResult.rows.map((row, index) => (
                          <tr key={index}>
                            {statsResult.fields.map((field) => (
                              <td key={field.field_id} style={field.data_type === 'number' ? { textAlign: 'right' } : {}}>
                                {formatValue(row[field.field_name])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="empty-state" style={{ height: '100%' }}>
                  <p>请选择数据快照和要统计的字段</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'advanced' && (
          <AdvancedStats snapshots={snapshots} dataflowsMap={dataflowsMap} />
        )}

      </div>

      <Modal
        isOpen={isSaveModalOpen}
        onClose={() => setIsSaveModalOpen(false)}
        title="保存结果"
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
            disabled={saving}
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </Modal>
    </div>
  )
}

export default AnalysisPage
