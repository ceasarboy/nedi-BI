import { useState } from 'react'
import ThemedChart from '../charts/echarts/ThemedChart'
import { analysisAPI } from '../services/api'
import '../styles/AnalysisComponents.css'

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
      title: { text: '圆周率计算 - 蒙特卡洛模拟', left: 'center', textStyle: { fontSize: 16, fontWeight: 600 } },
      tooltip: { trigger: 'item' },
      xAxis: { type: 'value', min: -1, max: 1, scale: true },
      yAxis: { type: 'value', min: -1, max: 1, scale: true },
      series: [
        { name: '圆内点', type: 'scatter', data: chartData.points_inside, symbolSize: 4, itemStyle: { color: '#3b82f6' } },
        { name: '圆外点', type: 'scatter', data: chartData.points_outside, symbolSize: 4, itemStyle: { color: '#ef4444' } }
      ]
    }
  }

  const getIntegralChartOption = (chartData) => {
    if (!chartData) return {}
    
    return {
      title: { text: '定积分计算 - 蒙特卡洛模拟', left: 'center', textStyle: { fontSize: 16, fontWeight: 600 } },
      tooltip: { trigger: 'item' },
      xAxis: { type: 'value', min: chartData.x_min - 0.1, max: chartData.x_max + 0.1 },
      yAxis: { type: 'value', min: chartData.y_min - 0.1, max: chartData.y_max + 0.1 },
      series: [
        { name: '曲线下点', type: 'scatter', data: chartData.points_below, symbolSize: 4, itemStyle: { color: '#3b82f6' } },
        { name: '曲线上点', type: 'scatter', data: chartData.points_above, symbolSize: 4, itemStyle: { color: '#ef4444' } },
        { name: '函数曲线', type: 'line', data: chartData.function_curve, symbol: 'none', lineStyle: { color: '#1f2937', width: 3 } }
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
      title: { text: '排队问题 - 等待时间分布', left: 'center', textStyle: { fontSize: 16, fontWeight: 600 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: binCenters.map(x => x.toFixed(2)), axisLabel: { interval: 0, rotate: 45 } },
      yAxis: { type: 'value', name: '频数' },
      series: [{ name: '等待时间', type: 'bar', data: hist.counts, itemStyle: { color: '#3b82f6' } }]
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">蒙特卡洛分析</h1>
      
      <div className="tab-group" style={{ marginBottom: '16px' }}>
        {['classic', 'custom'].map(tab => (
          <div
            key={tab}
            className={`tab-item ${activeTab === tab ? 'tab-item-active' : 'tab-item-default'}`}
            onClick={() => setActiveTab(tab)}>
            {tab === 'classic' ? '经典案例' : '自定义模拟'}
          </div>
        ))}
      </div>
      
      {activeTab === 'classic' ? (
        <div className="analysis-container">
          <div className="analysis-sidebar">
            <h3 className="analysis-sidebar-title">选择案例</h3>
            <div className="param-group">
              {[
                { value: 'pi', label: '计算圆周率 π' },
                { value: 'integral', label: '定积分计算' },
                { value: 'queue', label: '排队问题' }
              ].map(c => (
                <div
                  key={c.value}
                  className={`snapshot-item ${selectedCase === c.value ? 'snapshot-item-active' : 'snapshot-item-default'}`}
                  onClick={() => setSelectedCase(c.value)}>
                  <span className="snapshot-item-name">{c.label}</span>
                </div>
              ))}
            </div>

            {selectedCase === 'pi' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">参数设置</h3>
                <div className="param-group">
                  <label className="param-label">模拟点数</label>
                  <input
                    type="number"
                    min="100"
                    max="1000000"
                    value={piParams.simulation_count}
                    onChange={(e) => setPiParams({ ...piParams, simulation_count: parseInt(e.target.value) || 10000 })}
                    className="param-input"
                  />
                  <p className="param-hint">默认: 10000</p>
                </div>
              </div>
            )}

            {selectedCase === 'integral' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">参数设置</h3>
                <div className="param-group">
                  <label className="param-label">积分区间</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={integralParams.x_min}
                      onChange={(e) => setIntegralParams({ ...integralParams, x_min: parseFloat(e.target.value) || 0 })}
                      className="param-input"
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={integralParams.x_max}
                      onChange={(e) => setIntegralParams({ ...integralParams, x_max: parseFloat(e.target.value) || 1 })}
                      className="param-input"
                    />
                  </div>
                </div>
                <div className="param-group">
                  <label className="param-label">积分函数</label>
                  <input
                    type="text"
                    value={integralParams.function}
                    onChange={(e) => setIntegralParams({ ...integralParams, function: e.target.value })}
                    className="param-input"
                    placeholder="例如: x**2, np.sin(x), np.exp(x)"
                  />
                  <p className="param-hint">默认: x**2</p>
                </div>
                <div className="param-group">
                  <label className="param-label">模拟点数</label>
                  <input
                    type="number"
                    min="100"
                    max="1000000"
                    value={integralParams.simulation_count}
                    onChange={(e) => setIntegralParams({ ...integralParams, simulation_count: parseInt(e.target.value) || 10000 })}
                    className="param-input"
                  />
                  <p className="param-hint">默认: 10000</p>
                </div>
              </div>
            )}

            {selectedCase === 'queue' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">参数设置</h3>
                <div className="param-group">
                  <label className="param-label">人数</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={queueParams.num_people}
                    onChange={(e) => setQueueParams({ ...queueParams, num_people: parseInt(e.target.value) || 20 })}
                    className="param-input"
                  />
                  <p className="param-hint">默认: 20</p>
                </div>
                <div className="param-group">
                  <label className="param-label">到达时间分布（分钟）</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.arrival_min}
                      onChange={(e) => setQueueParams({ ...queueParams, arrival_min: parseFloat(e.target.value) || 0 })}
                      className="param-input"
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.arrival_max}
                      onChange={(e) => setQueueParams({ ...queueParams, arrival_max: parseFloat(e.target.value) || 10 })}
                      className="param-input"
                    />
                  </div>
                  <p className="param-hint">默认: 0-10</p>
                </div>
                <div className="param-group">
                  <label className="param-label">服务时间分布（分钟）</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.service_min}
                      onChange={(e) => setQueueParams({ ...queueParams, service_min: parseFloat(e.target.value) || 1 })}
                      className="param-input"
                    />
                    <span style={{ alignSelf: 'center' }}>到</span>
                    <input
                      type="number"
                      step="0.1"
                      value={queueParams.service_max}
                      onChange={(e) => setQueueParams({ ...queueParams, service_max: parseFloat(e.target.value) || 3 })}
                      className="param-input"
                    />
                  </div>
                  <p className="param-hint">默认: 1-3</p>
                </div>
                <div className="param-group">
                  <label className="param-label">模拟次数</label>
                  <input
                    type="number"
                    min="10"
                    max="10000"
                    value={queueParams.simulation_count}
                    onChange={(e) => setQueueParams({ ...queueParams, simulation_count: parseInt(e.target.value) || 1000 })}
                    className="param-input"
                  />
                  <p className="param-hint">默认: 1000</p>
                </div>
              </div>
            )}

            <button
              className="btn btn-primary btn-execute"
              onClick={
                selectedCase === 'pi' ? runPiSimulation :
                selectedCase === 'integral' ? runIntegralSimulation :
                runQueueSimulation
              }
              disabled={loading}>
              {loading ? '模拟中...' : '执行模拟'}
            </button>
          </div>

          <div className="analysis-main">
            {!result ? (
              <div className="empty-state">
                <p>选择案例并执行模拟</p>
              </div>
            ) : result.type === 'pi' ? (
              <div className="result-section">
                <h3 className="result-title">圆周率计算结果</h3>

                <div className="result-box result-box-info">
                  <h4 className="result-box-title result-box-title-info">模拟统计</h4>
                  <p className="result-text">模拟点数: <strong>{result.data.simulation_count}</strong></p>
                  <p className="result-text">圆内点: <strong>{result.data.inside_count}</strong>, 圆外点: <strong>{result.data.outside_count}</strong></p>
                  <p className="result-text">估计的 π 值: <strong className="result-text-highlight result-text-info">{result.data.pi_estimate}</strong></p>
                  <p className="result-text">误差: <strong>{result.data.error}</strong></p>
                </div>

                {result.data.chart_data && (
                  <div className="chart-container chart-container-lg">
                    <ThemedChart 
                      option={getPiChartOption(result.data.chart_data)}
                      style={{ height: '100%', width: '100%' }}
                    />
                  </div>
                )}
              </div>
            ) : result.type === 'integral' ? (
              <div className="result-section">
                <h3 className="result-title">定积分计算结果</h3>

                <div className="result-box result-box-info">
                  <h4 className="result-box-title result-box-title-info">模拟统计</h4>
                  <p className="result-text">模拟点数: <strong>{result.data.simulation_count}</strong></p>
                  <p className="result-text">曲线下点: <strong>{result.data.below_count}</strong>, 曲线上点: <strong>{result.data.above_count}</strong></p>
                  <p className="result-text">估计的积分值: <strong className="result-text-highlight result-text-info">{result.data.integral_estimate}</strong></p>
                  {result.data.real_integral !== null && (
                    <>
                      <p className="result-text">真实积分值: <strong>{result.data.real_integral}</strong></p>
                      <p className="result-text">误差: <strong>{result.data.error}</strong></p>
                    </>
                  )}
                </div>

                {result.data.chart_data && (
                  <div className="chart-container chart-container-lg">
                    <ThemedChart 
                      option={getIntegralChartOption(result.data.chart_data)}
                      style={{ height: '100%', width: '100%' }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="result-section">
                <h3 className="result-title">排队问题模拟结果</h3>

                <div className="result-grid-3">
                  <div className="result-box result-box-info">
                    <h4 className="result-box-title result-box-title-info">等待时间</h4>
                    <p className="result-text">均值: {result.data.waiting_time.mean}</p>
                    <p className="result-text">标准差: {result.data.waiting_time.std}</p>
                    <p className="result-text">中位数: {result.data.waiting_time.median}</p>
                    <p className="result-text">范围: {result.data.waiting_time.min} - {result.data.waiting_time.max}</p>
                  </div>
                  <div className="result-box result-box-success">
                    <h4 className="result-box-title result-box-title-success">服务时间</h4>
                    <p className="result-text">均值: {result.data.service_time.mean}</p>
                    <p className="result-text">标准差: {result.data.service_time.std}</p>
                  </div>
                  <div className="result-box result-box-warning">
                    <h4 className="result-box-title result-box-title-warning">空闲时间</h4>
                    <p className="result-text">均值: {result.data.empty_time.mean}</p>
                    <p className="result-text">标准差: {result.data.empty_time.std}</p>
                  </div>
                </div>

                <div className="result-box result-box-default">
                  <h4 className="result-box-title result-box-title-default">模拟统计</h4>
                  <p className="result-text">模拟次数: <strong>{result.data.simulation_count}</strong></p>
                </div>

                {result.data.chart_data && (
                  <div className="chart-container">
                    <ThemedChart 
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
