import { useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { analysisAPI } from '../services/api'

function MonteCarloPage() {
  const [activeTab, setActiveTab] = useState('classic')
  const [selectedCase, setSelectedCase] = useState('pi')
  const [piParams, setPiParams] = useState({ simulation_count: 10000 })
  const [integralParams, setIntegralParams] = useState({ x_min: 0, x_max: 1, function: 'x**2', simulation_count: 10000 })
  const [queueParams, setQueueParams] = useState({ num_people: 20, arrival_min: 0, arrival_max: 10, service_min: 1, service_max: 3, simulation_count: 1000 })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const runPiSimulation = async () => {
    setLoading(true)
    try {
      const response = await analysisAPI.monteCarloPi(piParams)
      setResult({ type: 'pi', data: response.data })
    } catch (error) {
      console.error('计算圆周率失败', error)
      alert('计算圆周率失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runIntegralSimulation = async () => {
    setLoading(true)
    try {
      const response = await analysisAPI.monteCarloIntegral(integralParams)
      setResult({ type: 'integral', data: response.data })
    } catch (error) {
      console.error('计算定积分失败', error)
      alert('计算定积分失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runQueueSimulation = async () => {
    setLoading(true)
    try {
      const response = await analysisAPI.monteCarloQueue(queueParams)
      setResult({ type: 'queue', data: response.data })
    } catch (error) {
      console.error('模拟排队问题失败', error)
      alert('模拟排队问题失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const getPiChartOption = (chartData) => {
    if (!chartData) return {}
    
    return {
      title: {
        text: '圆周率计算 - 蒙特卡洛模拟',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'item'
      },
      xAxis: {
        type: 'value',
        min: -1,
        max: 1,
        scale: true
      },
      yAxis: {
        type: 'value',
        min: -1,
        max: 1,
        scale: true
      },
      series: [
        {
          name: '圆内点',
          type: 'scatter',
          data: chartData.points_inside,
          symbolSize: 4,
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: '圆外点',
          type: 'scatter',
          data: chartData.points_outside,
          symbolSize: 4,
          itemStyle: { color: '#ef4444' }
        }
      ]
    }
  }

  const getIntegralChartOption = (chartData) => {
    if (!chartData) return {}
    
    return {
      title: {
        text: '定积分计算 - 蒙特卡洛模拟',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'item'
      },
      xAxis: {
        type: 'value',
        min: chartData.x_min - 0.1,
        max: chartData.x_max + 0.1
      },
      yAxis: {
        type: 'value',
        min: chartData.y_min - 0.1,
        max: chartData.y_max + 0.1
      },
      series: [
        {
          name: '曲线下点',
          type: 'scatter',
          data: chartData.points_below,
          symbolSize: 4,
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: '曲线上点',
          type: 'scatter',
          data: chartData.points_above,
          symbolSize: 4,
          itemStyle: { color: '#ef4444' }
        },
        {
          name: '函数曲线',
          type: 'line',
          data: chartData.function_curve,
          symbol: 'none',
          lineStyle: { color: '#1f2937', width: 3 }
        }
      ]
    }
  }

  const getQueueChartOption = (chartData) => {
    if (!chartData || !chartData.waiting_time_histogram) return {}
    
    const hist = chartData.waiting_time_histogram
    const binEdges = hist.bin_edges
    const binCenters = []
    for (let i = 0; i < binEdges.length - 1; i++) {
      binCenters.push((binEdges[i] + binEdges[i + 1]) / 2)
    }
    
    return {
      title: {
        text: '排队问题 - 等待时间分布',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      xAxis: {
        type: 'category',
        data: binCenters.map(x => x.toFixed(2)),
        axisLabel: { interval: 0, rotate: 45 }
      },
      yAxis: {
        type: 'value',
        name: '频数'
      },
      series: [
        {
          name: '等待时间',
          type: 'bar',
          data: hist.counts,
          itemStyle: { color: '#3b82f6' }
        }
      ]
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">蒙特卡洛分析</h1>
      
      <div style={{ marginBottom: '16px', display: 'flex', gap: '8px' }}>
        {['classic', 'custom'].map(tab => (
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
            {tab === 'classic' ? '经典案例' : '自定义模拟'}
          </div>
        ))}
      </div>
      
      {activeTab === 'classic' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '16px', height: 'calc(100vh - 320px)' }}>
          {/* 左侧选择区域 */}
          <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择案例</h3>
            <div style={{ marginBottom: '16px' }}>
              {[
                { value: 'pi', label: '计算圆周率 π' },
                { value: 'integral', label: '定积分计算' },
                { value: 'queue', label: '排队问题' }
              ].map(c => (
                <div
                  key={c.value}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    background: selectedCase === c.value ? '#eff6ff' : '#f9fafb',
                    border: selectedCase === c.value ? '2px solid #3b82f6' : '2px solid transparent',
                    marginBottom: '6px'
                  }}
                  onClick={() => setSelectedCase(c.value)}>
                  <span style={{ fontSize: '13px' }}>{c.label}</span>
                </div>
              ))}
            </div>

            {selectedCase === 'pi' && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>参数设置</h3>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>模拟点数</label>
                  <input
                    type="number"
                    min="100"
                    max="1000000"
                    value={piParams.simulation_count}
                    onChange={(e) => setPiParams({ ...piParams, simulation_count: parseInt(e.target.value) || 10000 })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                  />
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 10000</p>
                </div>
              </div>
            )}

            {selectedCase === 'integral' && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>参数设置</h3>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>积分区间</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={integralParams.x_min}
                      onChange={(e) => setIntegralParams({ ...integralParams, x_min: parseFloat(e.target.value) || 0 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={integralParams.x_max}
                      onChange={(e) => setIntegralParams({ ...integralParams, x_max: parseFloat(e.target.value) || 1 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                  </div>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>积分函数</label>
                  <input
                    type="text"
                    value={integralParams.function}
                    onChange={(e) => setIntegralParams({ ...integralParams, function: e.target.value })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    placeholder="例如: x**2, np.sin(x), np.exp(x)"
                  />
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: x**2</p>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>模拟点数</label>
                  <input
                    type="number"
                    min="100"
                    max="1000000"
                    value={integralParams.simulation_count}
                    onChange={(e) => setIntegralParams({ ...integralParams, simulation_count: parseInt(e.target.value) || 10000 })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                  />
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 10000</p>
                </div>
              </div>
            )}

            {selectedCase === 'queue' && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>参数设置</h3>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>人数</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={queueParams.num_people}
                    onChange={(e) => setQueueParams({ ...queueParams, num_people: parseInt(e.target.value) || 20 })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                  />
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 20</p>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>到达时间分布（分钟）</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.arrival_min}
                      onChange={(e) => setQueueParams({ ...queueParams, arrival_min: parseFloat(e.target.value) || 0 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.arrival_max}
                      onChange={(e) => setQueueParams({ ...queueParams, arrival_max: parseFloat(e.target.value) || 10 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                  </div>
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 0-10</p>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>服务时间分布（分钟）</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.service_min}
                      onChange={(e) => setQueueParams({ ...queueParams, service_min: parseFloat(e.target.value) || 1 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.service_max}
                      onChange={(e) => setQueueParams({ ...queueParams, service_max: parseFloat(e.target.value) || 3 })}
                      style={{ flex: 1, padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                    />
                  </div>
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 1-3</p>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#6b7280' }}>模拟次数</label>
                  <input
                    type="number"
                    min="10"
                    max="10000"
                    value={queueParams.simulation_count}
                    onChange={(e) => setQueueParams({ ...queueParams, simulation_count: parseInt(e.target.value) || 1000 })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                  />
                  <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#6b7280' }}>默认: 1000</p>
                </div>
              </div>
            )}

            <button
              className="btn btn-primary"
              onClick={
                selectedCase === 'pi' ? runPiSimulation :
                selectedCase === 'integral' ? runIntegralSimulation :
                runQueueSimulation
              }
              disabled={loading}
              style={{ width: '100%' }}>
              {loading ? '模拟中...' : '执行模拟'}
            </button>
          </div>

          {/* 右侧结果展示区域 */}
          <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
            {!result ? (
              <div className="empty-state" style={{ height: '100%' }}>
                <p>选择案例并执行模拟</p>
              </div>
            ) : result.type === 'pi' ? (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
                  圆周率计算结果
                </h3>

                <div style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1e40af' }}>模拟统计</h4>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    模拟点数: <strong>{result.data.simulation_count}</strong>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    圆内点: <strong>{result.data.inside_count}</strong>, 圆外点: <strong>{result.data.outside_count}</strong>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    估计的 π 值: <strong style={{ fontSize: '18px', color: '#1e40af' }}>{result.data.pi_estimate}</strong>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    误差: <strong>{result.data.error}</strong>
                  </p>
                </div>

                {result.data.chart_data && (
                  <div style={{ height: '500px' }}>
                    <ReactECharts 
                      option={getPiChartOption(result.data.chart_data)}
                      style={{ height: '100%', width: '100%' }}
                    />
                  </div>
                )}
              </div>
            ) : result.type === 'integral' ? (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
                  定积分计算结果
                </h3>

                <div style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1e40af' }}>模拟统计</h4>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    模拟点数: <strong>{result.data.simulation_count}</strong>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    曲线下点: <strong>{result.data.below_count}</strong>, 曲线上点: <strong>{result.data.above_count}</strong>
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '13px' }}>
                    估计的积分值: <strong style={{ fontSize: '18px', color: '#1e40af' }}>{result.data.integral_estimate}</strong>
                  </p>
                  {result.data.real_integral !== null && (
                    <>
                      <p style={{ margin: '4px 0', fontSize: '13px' }}>
                        真实积分值: <strong>{result.data.real_integral}</strong>
                      </p>
                      <p style={{ margin: '4px 0', fontSize: '13px' }}>
                        误差: <strong>{result.data.error}</strong>
                      </p>
                    </>
                  )}
                </div>

                {result.data.chart_data && (
                  <div style={{ height: '500px' }}>
                    <ReactECharts 
                      option={getIntegralChartOption(result.data.chart_data)}
                      style={{ height: '100%', width: '100%' }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
                  排队问题模拟结果
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '12px', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#1e40af' }}>等待时间</h4>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>均值: {result.data.waiting_time.mean}</p>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>标准差: {result.data.waiting_time.std}</p>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>中位数: {result.data.waiting_time.median}</p>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>范围: {result.data.waiting_time.min} - {result.data.waiting_time.max}</p>
                  </div>
                  <div style={{ background: '#dcfce7', border: '1px solid #86efac', padding: '12px', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#166534' }}>服务时间</h4>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>均值: {result.data.service_time.mean}</p>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>标准差: {result.data.service_time.std}</p>
                  </div>
                  <div style={{ background: '#fef3c7', border: '1px solid #fcd34d', padding: '12px', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#92400e' }}>空闲时间</h4>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>均值: {result.data.empty_time.mean}</p>
                    <p style={{ margin: '2px 0', fontSize: '12px' }}>标准差: {result.data.empty_time.std}</p>
                  </div>
                </div>

                <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#374151' }}>模拟统计</h4>
                  <p style={{ margin: '0', fontSize: '13px' }}>
                    模拟次数: <strong>{result.data.simulation_count}</strong>
                  </p>
                </div>

                {result.data.chart_data && (
                  <div style={{ height: '400px' }}>
                    <ReactECharts 
                      option={getQueueChartOption(result.data.chart_data)}
                      style={{ height: '100%', width: '100%' }}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="empty-state" style={{ height: 'calc(100vh - 320px)' }}>
          <p>自定义模拟功能开发中...</p>
        </div>
      )}
    </div>
  )
}

export default MonteCarloPage
