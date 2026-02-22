import { useState, useEffect } from 'react'
import { dataAPI, dashboardAPI } from '../services/api'
import LineChart from '../charts/echarts/LineChart'
import BarChart from '../charts/echarts/BarChart'
import PieChart from '../charts/echarts/PieChart'
import ScatterChart from '../charts/echarts/ScatterChart'
import RadarChart from '../charts/echarts/RadarChart'
import FunnelChart from '../charts/echarts/FunnelChart'
import GaugeChart from '../charts/echarts/GaugeChart'
import HeatMap from '../charts/echarts/HeatMap'
import Bar3DChart from '../charts/echarts/Bar3DChart'
import Scatter3DChart from '../charts/echarts/Scatter3DChart'
import Surface3DChart from '../charts/echarts/Surface3DChart'
import StackedLineChart from '../charts/echarts/StackedLineChart'
import StackedBarChart from '../charts/echarts/StackedBarChart'
import MultipleYAxisChart from '../charts/echarts/MultipleYAxisChart'
import LinkedChart from '../charts/echarts/LinkedChart'
import LEDWaferChart from '../charts/echarts/LEDWaferChart'
import ChartSettings from '../components/ChartSettings'

const CHART_TYPES = [
  { id: 'line', name: '折线图-ECharts', icon: '📈', category: 'ECharts' },
  { id: 'bar', name: '柱状图-ECharts', icon: '📊', category: 'ECharts' },
  { id: 'pie', name: '饼图-ECharts', icon: '🥧', category: 'ECharts' },
  { id: 'scatter', name: '散点图-ECharts', icon: '⚪', category: 'ECharts' },
  { id: 'radar', name: '雷达图-ECharts', icon: '🎯', category: 'ECharts' },
  { id: 'funnel', name: '漏斗图-ECharts', icon: '🔻', category: 'ECharts' },
  { id: 'gauge', name: '仪表盘-ECharts', icon: '⏱️', category: 'ECharts' },
  { id: 'heatmap', name: '热力图-ECharts', icon: '🔥', category: 'ECharts' },
  { id: 'bar3d', name: '3D柱状图-ECharts', icon: '🏗️', category: 'ECharts' },
  { id: 'scatter3d', name: '3D散点图-ECharts', icon: '🔵', category: 'ECharts' },
  { id: 'surface3d', name: '3D形貌图-ECharts', icon: '🏔️', category: 'ECharts' },
  { id: 'stacked_line', name: '堆叠折线图-ECharts', icon: '📉', category: 'ECharts' },
  { id: 'stacked_bar', name: '堆叠柱状图-ECharts', icon: '📊', category: 'ECharts' },
  { id: 'multiple_y', name: '多Y轴图-ECharts', icon: '📐', category: 'ECharts' },
  { id: 'linked', name: '联动图表-ECharts', icon: '🔗', category: 'ECharts' },
  { id: 'led_wafer', name: 'LED晶圆图-ECharts', icon: '💡', category: 'ECharts' }
]

const CHART_COMPONENTS = {
  line: LineChart,
  bar: BarChart,
  pie: PieChart,
  scatter: ScatterChart,
  radar: RadarChart,
  funnel: FunnelChart,
  gauge: GaugeChart,
  heatmap: HeatMap,
  bar3d: Bar3DChart,
  scatter3d: Scatter3DChart,
  surface3d: Surface3DChart,
  stacked_line: StackedLineChart,
  stacked_bar: StackedBarChart,
  multiple_y: MultipleYAxisChart,
  linked: LinkedChart,
  led_wafer: LEDWaferChart
}

function VisualPage() {
  const [viewMode, setViewMode] = useState('dashboard')
  const [dashboardDisplayMode, setDashboardDisplayMode] = useState('switch')
  const [selectedDashboardForView, setSelectedDashboardForView] = useState(null)
  
  const [dashboards, setDashboards] = useState([])
  const [selectedDashboardId, setSelectedDashboardId] = useState(null)
  const [selectedDashboard, setSelectedDashboard] = useState(null)
  
  const [snapshots, setSnapshots] = useState([])
  const [selectedSnapshot, setSelectedSnapshot] = useState(null)
  const [snapshotData, setSnapshotData] = useState(null)
  const [dataRows, setDataRows] = useState([])
  const [availableFields, setAvailableFields] = useState([])
  
  const [title, setTitle] = useState('新图表')
  const [chartType, setChartType] = useState('line')
  const [chartConfig, setChartConfig] = useState({})
  
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    loadDashboards()
    loadSnapshots()
  }, [])

  const loadDashboards = async () => {
    try {
      const response = await dashboardAPI.getAll(1, 100)
      console.log('加载看板列表:', response.data)
      setDashboards(response.data)
      if (response.data.length > 0) {
        setSelectedDashboardForView(response.data[0])
      }
    } catch (error) {
      console.error('加载看板失败', error)
    }
  }

  const loadSnapshots = async () => {
    try {
      const response = await dataAPI.getAllSnapshots(1, 1000)
      setSnapshots(response.data.data)
    } catch (error) {
      console.error('加载快照失败', error)
    }
  }

  const loadSnapshotDataById = async (snapshotId) => {
    try {
      console.log('开始加载快照数据, snapshotId:', snapshotId)
      const snapshot = snapshots.find(s => s.id === snapshotId)
      if (snapshot) {
        setSelectedSnapshot(snapshot)
      }
      
      const response = await dataAPI.getSnapshot(snapshotId)
      console.log('API返回数据:', response)
      const data = response.data.data
      console.log('快照数据:', data)
      setSnapshotData(data)
      
      let fields = []
      let rows = []
      if (data.fields) {
        fields = typeof data.fields === 'string' ? JSON.parse(data.fields) : data.fields
      }
      if (data.rows) {
        rows = typeof data.rows === 'string' ? JSON.parse(data.rows) : data.rows
      }
      console.log('解析后的字段:', fields)
      console.log('解析后的行数:', rows.length)
      
      setDataRows(rows)
      
      if (fields.length > 0) {
        const fieldNames = fields.map(f => f.field_name || f.name)
        console.log('字段名:', fieldNames)
        setAvailableFields(fieldNames)
        
        setChartConfig({
          title: title,
          xAxisField: fieldNames[0],
          yAxisField: fieldNames.length > 1 ? fieldNames[1] : fieldNames[0],
          yAxisFields: fieldNames.slice(1, 4),
          nameField: fieldNames[0],
          valueField: fieldNames.length > 1 ? fieldNames[1] : fieldNames[0],
          zAxisField: fieldNames.length > 1 ? fieldNames[1] : fieldNames[0],
          fields: fieldNames.slice(0, 5),
          max: 100
        })
      }
    } catch (error) {
      console.error('加载快照数据失败', error)
    }
  }

  const handleSelectSnapshot = async (snapshot) => {
    setSelectedSnapshot(snapshot)
    await loadSnapshotDataById(snapshot.id)
  }

  const handleSaveDashboard = async () => {
    setLoading(true)
    try {
      const saveData = {
        name: title,
        data_snapshot_id: selectedSnapshot?.id,
        chart_type: chartType,
        config: {
          chartType,
          chartConfig
        }
      }

      console.log('保存看板:', saveData)

      if (selectedDashboardId) {
        await dashboardAPI.update(selectedDashboardId, saveData)
        setMessage({ type: 'success', text: '看板保存成功' })
      } else {
        await dashboardAPI.create(saveData)
        setMessage({ type: 'success', text: '看板创建成功' })
      }
      
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
      await loadDashboards()
      setViewMode('dashboard')
    } catch (error) {
      console.error('保存看板失败', error)
      setMessage({ type: 'error', text: '保存看板失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateDashboard = () => {
    setSelectedDashboardId(null)
    setSelectedDashboard(null)
    setTitle('新图表')
    setSelectedSnapshot(null)
    setSnapshotData(null)
    setDataRows([])
    setAvailableFields([])
    setChartType('line')
    setChartConfig({})
    setViewMode('edit')
  }

  const handleEditDashboard = (dashboard) => {
    console.log('编辑看板:', dashboard)
    setSelectedDashboardId(dashboard.id)
    setSelectedDashboard(dashboard)
    setTitle(dashboard.name)
    
    const config = dashboard.config
    if (config) {
      setChartType(config.chartType || dashboard.chart_type || 'line')
      setChartConfig(config.chartConfig || {})
    }
    
    if (dashboard.data_snapshot_id) {
      const snapshot = snapshots.find(s => s.id === dashboard.data_snapshot_id)
      if (snapshot) {
        setSelectedSnapshot(snapshot)
        loadSnapshotDataById(dashboard.data_snapshot_id)
      }
    }
    
    setViewMode('edit')
  }

  const handleDeleteDashboard = async (dashboard) => {
    if (!window.confirm(`确定要删除看板"${dashboard.name}"吗？`)) return
    try {
      await dashboardAPI.delete(dashboard.id)
      setMessage({ type: 'success', text: '看板删除成功' })
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
      await loadDashboards()
      if (selectedDashboardForView?.id === dashboard.id) {
        setSelectedDashboardForView(null)
      }
    } catch (error) {
      console.error('删除看板失败', error)
      setMessage({ type: 'error', text: '删除看板失败' })
    }
  }

  const renderChart = (type, data, config) => {
    const ChartComponent = CHART_COMPONENTS[type]
    if (!ChartComponent) {
      return <div className="empty-state">不支持的图表类型</div>
    }
    return <ChartComponent data={data} config={config} />
  }

  if (viewMode === 'dashboard') {
    return (
      <div className="page-container" style={{ padding: '16px', height: 'calc(100vh - 100px)' }}>
        {message.text && (
          <div className={`message message-${message.type}`} style={{ marginBottom: '12px' }}>
            {message.text}
          </div>
        )}

        <div>
          <h1 className="page-title">数据看板</h1>
          
          <div style={{ marginBottom: '20px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', color: '#64748b' }}>显示方式：</span>
              <button
                className={`btn ${dashboardDisplayMode === 'switch' ? 'btn-primary' : 'btn-default'}`}
                onClick={() => setDashboardDisplayMode('switch')}
                style={{ padding: '6px 12px', fontSize: '13px' }}>
                切换
              </button>
              <button
                className={`btn ${dashboardDisplayMode === 'tile' ? 'btn-primary' : 'btn-default'}`}
                onClick={() => setDashboardDisplayMode('tile')}
                style={{ padding: '6px 12px', fontSize: '13px' }}>
                平铺
              </button>
            </div>
            <button className="btn btn-primary" onClick={handleCreateDashboard}>
              + 新增图表
            </button>
          </div>

          {dashboardDisplayMode === 'switch' ? (
            <div>
              {dashboards.length === 0 ? (
                <div className="empty-state">
                  <p>暂无看板，点击"新增图表"创建</p>
                </div>
              ) : (
                <div>
                  <div style={{ marginBottom: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {dashboards.map(db => (
                      <button
                        key={db.id}
                        className={`btn ${selectedDashboardForView?.id === db.id ? 'btn-primary' : 'btn-default'}`}
                        onClick={() => setSelectedDashboardForView(db)}>
                        {db.name}
                      </button>
                    ))}
                  </div>
                  {selectedDashboardForView && (
                    <DashboardView 
                      dashboard={selectedDashboardForView} 
                      onEdit={handleEditDashboard}
                      onDelete={handleDeleteDashboard}
                      renderChart={renderChart}
                    />
                  )}
                </div>
              )}
            </div>
          ) : (
            <div>
              {dashboards.length === 0 ? (
                <div className="empty-state">
                  <p>暂无看板，点击"新增图表"创建</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {dashboards.map(db => (
                    <DashboardCard 
                      key={db.id} 
                      dashboard={db} 
                      onEdit={handleEditDashboard}
                      onDelete={handleDeleteDashboard}
                      renderChart={renderChart}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="page-container" style={{ padding: '16px', height: 'calc(100vh - 100px)' }}>
      {message.text && (
        <div className={`message message-${message.type}`} style={{ marginBottom: '12px' }}>
          {message.text}
        </div>
      )}

      <div>
        <h1 className="page-title">{title}</h1>
        
        <div style={{ marginBottom: '20px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-default" onClick={() => setViewMode('dashboard')}>
            ← 返回看板
          </button>
          <button className="btn btn-default" onClick={handleCreateDashboard}>
            + 新增图表
          </button>
          <button className="btn btn-primary" onClick={handleSaveDashboard} disabled={loading}>
            {loading ? '保存中...' : '保存'}
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 280px', gap: '16px', height: 'calc(100vh - 220px)' }}>
          <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>看板列表</h3>
              <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
                {dashboards.map(db => (
                  <div
                    key={db.id}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: selectedDashboardId === db.id ? '#eff6ff' : 'transparent',
                      border: selectedDashboardId === db.id ? '1px solid #3b82f6' : '1px solid transparent',
                      marginBottom: '4px'
                    }}
                    onClick={() => handleEditDashboard(db)}>
                    <span style={{ fontSize: '13px' }}>{db.name}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>数据快照</h3>
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {snapshots.map(s => (
                  <div
                    key={s.id}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: selectedSnapshot?.id === s.id ? '#eff6ff' : 'transparent',
                      border: selectedSnapshot?.id === s.id ? '1px solid #3b82f6' : '1px solid transparent',
                      marginBottom: '4px'
                    }}
                    onClick={() => handleSelectSnapshot(s)}>
                    <span style={{ fontSize: '13px' }}>{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px' }}>
            {dataRows.length > 0 ? (
              renderChart(chartType, dataRows, chartConfig)
            ) : (
              <div className="empty-state" style={{ height: '100%' }}>
                <p>请选择数据快照</p>
              </div>
            )}
          </div>

          <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '0', overflowY: 'auto' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
              {CHART_TYPES.map(type => (
                <div
                  key={type.id}
                  style={{
                    flex: '0 0 calc(50% - 2px)',
                    padding: '10px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    background: chartType === type.id ? '#eff6ff' : '#f9fafb',
                    border: chartType === type.id ? '2px solid #3b82f6' : '2px solid transparent',
                    textAlign: 'center',
                    boxSizing: 'border-box'
                  }}
                  onClick={() => setChartType(type.id)}>
                  <div style={{ fontSize: '20px', marginBottom: '2px' }}>{type.icon}</div>
                  <div style={{ fontSize: '11px' }}>{type.name}</div>
                </div>
              ))}
            </div>
            
            <ChartSettings
              chartType={chartType}
              config={chartConfig}
              fields={availableFields}
              onConfigChange={setChartConfig}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function DashboardView({ dashboard, onEdit, onDelete, renderChart }) {
  const [snapshotData, setSnapshotData] = useState(null)
  const [dataRows, setDataRows] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadData()
  }, [dashboard])

  const loadData = async () => {
    console.log('DashboardView loadData 开始')
    console.log('dashboard:', dashboard)
    if (!dashboard.data_snapshot_id) {
      console.log('没有 data_snapshot_id')
      setLoading(false)
      return
    }
    try {
      setLoading(true)
      const { dataAPI } = await import('../services/api')
      console.log('请求API, data_snapshot_id:', dashboard.data_snapshot_id)
      const response = await dataAPI.getSnapshot(dashboard.data_snapshot_id)
      console.log('API响应:', response)
      setSnapshotData(response.data.data)
      
      let rows = []
      if (response.data.data?.rows) {
        rows = typeof response.data.data.rows === 'string' ? JSON.parse(response.data.data.rows) : response.data.data.rows
      }
      setDataRows(rows)
    } catch (error) {
      console.error('加载数据失败', error)
    } finally {
      setLoading(false)
    }
  }

  const chartType = dashboard.config?.chartType || dashboard.chart_type || 'line'
  const chartConfig = dashboard.config?.chartConfig || {}

  return (
    <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', height: '1000px' }}>
      <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{dashboard.name}</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-default btn-sm" onClick={() => onEdit(dashboard)}>
            ✏️ 修改
          </button>
          <button className="btn btn-danger btn-sm" onClick={() => onDelete(dashboard)}>
            🗑️ 删除
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="empty-state" style={{ height: '930px' }}>
          <p>加载中...</p>
        </div>
      ) : dataRows.length > 0 ? (
        renderChart(chartType, dataRows, chartConfig)
      ) : (
        <DataDebugPanel 
          dashboard={dashboard} 
          snapshotData={snapshotData} 
        />
      )}
    </div>
  )
}

function DashboardCard({ dashboard, onEdit, onDelete, renderChart }) {
  const [snapshotData, setSnapshotData] = useState(null)
  const [dataRows, setDataRows] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadData()
  }, [dashboard])

  const loadData = async () => {
    console.log('DashboardCard loadData 开始')
    console.log('dashboard:', dashboard)
    if (!dashboard.data_snapshot_id) {
      console.log('没有 data_snapshot_id')
      setLoading(false)
      return
    }
    try {
      setLoading(true)
      const { dataAPI } = await import('../services/api')
      console.log('请求API, data_snapshot_id:', dashboard.data_snapshot_id)
      const response = await dataAPI.getSnapshot(dashboard.data_snapshot_id)
      console.log('API响应:', response)
      setSnapshotData(response.data.data)
      
      let rows = []
      if (response.data.data?.rows) {
        rows = typeof response.data.data.rows === 'string' ? JSON.parse(response.data.data.rows) : response.data.data.rows
      }
      setDataRows(rows)
    } catch (error) {
      console.error('加载数据失败', error)
    } finally {
      setLoading(false)
    }
  }

  const chartType = dashboard.config?.chartType || dashboard.chart_type || 'line'
  const chartConfig = dashboard.config?.chartConfig || {}

  return (
    <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', height: '800px' }}>
      <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{dashboard.name}</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-default btn-sm" onClick={() => onEdit(dashboard)}>
            ✏️ 修改
          </button>
          <button className="btn btn-danger btn-sm" onClick={() => onDelete(dashboard)}>
            🗑️ 删除
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="empty-state" style={{ height: '740px' }}>
          <p>加载中...</p>
        </div>
      ) : dataRows.length > 0 ? (
        renderChart(chartType, dataRows, chartConfig)
      ) : (
        <DataDebugPanel 
          dashboard={dashboard} 
          snapshotData={snapshotData} 
          compact={true}
        />
      )}
    </div>
  )
}

function DataDebugPanel({ dashboard, snapshotData, compact = false }) {
  const config = dashboard?.config
  const height = compact ? '740px' : '930px'
  
  let fields = []
  let rows = []
  
  if (snapshotData) {
    if (snapshotData.fields) {
      fields = typeof snapshotData.fields === 'string' ? JSON.parse(snapshotData.fields) : snapshotData.fields
    }
    if (snapshotData.rows) {
      rows = typeof snapshotData.rows === 'string' ? JSON.parse(snapshotData.rows) : snapshotData.rows
    }
  }

  return (
    <div style={{ 
      height, 
      overflow: 'auto', 
      fontSize: '12px', 
      background: '#f9fafb', 
      padding: '12px',
      borderRadius: '6px'
    }}>
      <div style={{ marginBottom: '12px' }}>
        <div style={{ fontWeight: 600, marginBottom: '4px', color: '#ef4444' }}>⚠️ 图表无法显示 - 数据调试面板</div>
      </div>
      
      <div style={{ marginBottom: '12px' }}>
        <div style={{ fontWeight: 600, marginBottom: '4px', color: '#3b82f6' }}>📋 看板配置</div>
        <pre style={{ 
          margin: 0, 
          background: '#fff', 
          padding: '8px', 
          borderRadius: '4px',
          border: '1px solid #e5e7eb',
          overflow: 'auto'
        }}>
          {JSON.stringify(config, null, 2)}
        </pre>
      </div>
      
      <div style={{ marginBottom: '12px' }}>
        <div style={{ fontWeight: 600, marginBottom: '4px', color: '#10b981' }}>📊 数据快照信息</div>
        <div style={{ background: '#fff', padding: '8px', borderRadius: '4px', border: '1px solid #e5e7eb' }}>
          <div>snapshotData 是否存在: {snapshotData ? '是' : '否'}</div>
          <div>字段数: {fields.length}</div>
          <div>数据行数: {rows.length}</div>
        </div>
      </div>
      
      {fields.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontWeight: 600, marginBottom: '4px', color: '#8b5cf6' }}>📝 字段列表</div>
          <pre style={{ 
            margin: 0, 
            background: '#fff', 
            padding: '8px', 
            borderRadius: '4px',
            border: '1px solid #e5e7eb',
            overflow: 'auto',
            maxHeight: '100px'
          }}>
            {JSON.stringify(fields.map(f => f.field_name || f.name), null, 2)}
          </pre>
        </div>
      )}
      
      {rows.length > 0 && (
        <div>
          <div style={{ fontWeight: 600, marginBottom: '4px', color: '#f59e0b' }}>📈 数据样本（前3行）</div>
          <pre style={{ 
            margin: 0, 
            background: '#fff', 
            padding: '8px', 
            borderRadius: '4px',
            border: '1px solid #e5e7eb',
            overflow: 'auto',
            maxHeight: '150px'
          }}>
            {JSON.stringify(rows.slice(0, 3), null, 2)}
          </pre>
        </div>
      )}
      
      {rows.length === 0 && snapshotData && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontWeight: 600, marginBottom: '4px', color: '#ef4444' }}>❌ snapshotData 原始数据</div>
          <pre style={{ 
            margin: 0, 
            background: '#fff', 
            padding: '8px', 
            borderRadius: '4px',
            border: '1px solid #e5e7eb',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {JSON.stringify(snapshotData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default VisualPage
