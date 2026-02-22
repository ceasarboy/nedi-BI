import { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { analysisAPI } from '../services/api'

function AdvancedStats({ snapshots, dataflowsMap }) {
  const [activeTab, setActiveTab] = useState('statistical')
  const [selectedSnapshot, setSelectedSnapshot] = useState(null)
  const [snapshotData, setSnapshotData] = useState(null)
  const [loading, setLoading] = useState(false)
  
  // 统计分析状态
  const [selectedField, setSelectedField] = useState('')
  const [statisticalResult, setStatisticalResult] = useState(null)
  
  // 分布拟合状态
  const [selectedDistField, setSelectedDistField] = useState('')
  const [selectedDistributions, setSelectedDistributions] = useState(['norm', 'expon', 'gamma', 'lognorm'])
  const [removeEmpty, setRemoveEmpty] = useState(true)
  const [distributionResult, setDistributionResult] = useState(null)
  
  // 回归分析状态
  const [dependentVar, setDependentVar] = useState('')
  const [independentVars, setIndependentVars] = useState([])
  const [regressionType, setRegressionType] = useState('linear')
  const [polynomialDegree, setPolynomialDegree] = useState(2)
  const [regressionResult, setRegressionResult] = useState(null)

  const getDistributionChartOption = (chartData, bestFitName) => {
    if (!chartData || !chartData.histogram) return {}
    
    const { histogram, fitted_curves } = chartData
    
    const series = [
      {
        name: '直方图',
        type: 'bar',
        data: histogram.counts.map((count, idx) => [
          (histogram.bin_edges[idx] + histogram.bin_edges[idx + 1]) / 2,
          count
        ]),
        barWidth: (histogram.bin_edges[1] - histogram.bin_edges[0]) * 0.95,
        itemStyle: {
          color: 'rgba(59, 130, 246, 0.6)'
        }
      }
    ]
    
    const colors = ['#ef4444', '#6b7280', '#8b5cf6', '#059669']
    fitted_curves.forEach((curve, idx) => {
      const isBestFit = curve.distribution === bestFitName
      series.push({
        name: curve.distribution,
        type: 'line',
        smooth: true,
        data: curve.x.map((x, i) => [x, curve.y[i]]),
        symbol: 'none',
        lineStyle: {
          width: isBestFit ? 3 : 2,
          color: colors[idx % colors.length]
        },
        itemStyle: {
          color: colors[idx % colors.length]
        }
      })
    })
    
    return {
      title: {
        text: '分布拟合图',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['直方图', ...fitted_curves.map(c => c.distribution)],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 100,
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '数值',
        min: histogram.bin_edges[0],
        max: histogram.bin_edges[histogram.bin_edges.length - 1]
      },
      yAxis: {
        type: 'value',
        name: '频数'
      },
      series: series
    }
  }

  const getRegressionChartOption = (chartData, dependentVar, independentVar) => {
    if (!chartData || !chartData.actual || !chartData.predicted) return {}
    
    const sortedActual = [...chartData.actual].sort((a, b) => a[0] - b[0])
    const sortedPredicted = [...chartData.predicted].sort((a, b) => a[0] - b[0])
    
    return {
      title: {
        text: '回归拟合图',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['实际数据点', '拟合曲线'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 100,
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: independentVar || '自变量'
      },
      yAxis: {
        type: 'value',
        name: dependentVar || '因变量'
      },
      series: [
        {
          name: '实际数据点',
          type: 'scatter',
          data: sortedActual,
          itemStyle: {
            color: '#3b82f6'
          }
        },
        {
          name: '拟合曲线',
          type: 'line',
          smooth: true,
          data: sortedPredicted,
          symbol: 'none',
          lineStyle: {
            width: 3,
            color: '#ef4444'
          }
        }
      ]
    }
  }

  const distributionOptions = [
    { value: 'norm', label: '正态分布' },
    { value: 'expon', label: '指数分布' },
    { value: 'gamma', label: '伽马分布' },
    { value: 'lognorm', label: '对数正态分布' },
    { value: 'poisson', label: '泊松分布' }
  ]

  const regressionTypes = [
    { value: 'linear', label: '线性回归' },
    { value: 'ridge', label: '岭回归' },
    { value: 'lasso', label: 'Lasso回归' },
    { value: 'polynomial', label: '多项式回归' }
  ]

  const loadSnapshotData = async (snapshot) => {
    setSelectedSnapshot(snapshot)
    setLoading(true)
    try {
      const response = await analysisAPI.getSnapshot(snapshot.id)
      setSnapshotData(response.data.data)
    } catch (error) {
      console.error('加载快照数据失败', error)
    } finally {
      setLoading(false)
    }
  }

  const runStatisticalAnalysis = async () => {
    if (!selectedSnapshot || !selectedField) return
    setLoading(true)
    try {
      const response = await analysisAPI.statisticalAnalysis({
        snapshot_id: selectedSnapshot.id,
        field: selectedField
      })
      setStatisticalResult(response.data)
    } catch (error) {
      console.error('统计分析失败', error)
      alert('统计分析失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runDistributionAnalysis = async () => {
    if (!selectedSnapshot || !selectedDistField) return
    setLoading(true)
    try {
      const response = await analysisAPI.distributionAnalysis({
        snapshot_id: selectedSnapshot.id,
        field: selectedDistField,
        distributions: selectedDistributions,
        remove_empty: removeEmpty
      })
      setDistributionResult(response.data)
    } catch (error) {
      console.error('分布拟合分析失败', error)
      alert('分布拟合分析失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runRegressionAnalysis = async () => {
    if (!selectedSnapshot || !dependentVar || independentVars.length === 0) return
    setLoading(true)
    try {
      const requestData = {
        snapshot_id: selectedSnapshot.id,
        dependent_var: dependentVar,
        independent_vars: independentVars,
        regression_type: regressionType
      }
      
      if (regressionType === 'polynomial') {
        requestData.polynomial_degree = polynomialDegree
      }
      
      const response = await analysisAPI.regressionAnalysis(requestData)
      setRegressionResult(response.data)
    } catch (error) {
      console.error('回归分析失败', error)
      alert('回归分析失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const toggleIndependentVar = (field) => {
    setIndependentVars(prev => 
      prev.includes(field) 
        ? prev.filter(f => f !== field)
        : [...prev, field]
    )
  }

  const getNumericFields = () => {
    if (!snapshotData || !snapshotData.fields) return []
    return snapshotData.fields.filter(f => f.data_type === 'number' || f.data_type === 'numeric')
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '16px', height: 'calc(100vh - 260px)' }}>
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
                background: selectedSnapshot?.id === s.id ? '#eff6ff' : '#f9fafb',
                border: selectedSnapshot?.id === s.id ? '2px solid #3b82f6' : '2px solid transparent',
                marginBottom: '6px'
              }}
              onClick={() => loadSnapshotData(s)}>
              <span style={{ fontSize: '13px' }}>{s.name}</span>
            </div>
          ))}
        </div>

        {snapshotData && (
          <>
            <div style={{ marginBottom: '16px', borderBottom: '1px solid #e5e7eb', paddingBottom: '16px' }}>
              <div style={{ display: 'flex', gap: '4px', marginBottom: '12px', flexWrap: 'wrap' }}>
                {['statistical', 'distribution', 'regression'].map(tab => (
                  <div
                    key={tab}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: activeTab === tab ? '#3b82f6' : '#f3f4f6',
                      color: activeTab === tab ? '#fff' : '#374151',
                      fontSize: '12px',
                      fontWeight: activeTab === tab ? 600 : 400
                    }}
                    onClick={() => setActiveTab(tab)}>
                    {tab === 'statistical' && '统计描述'}
                    {tab === 'distribution' && '分布拟合'}
                    {tab === 'regression' && '回归分析'}
                  </div>
                ))}
              </div>
            </div>

            {activeTab === 'statistical' && (
              <div>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择分析字段</h3>
                <select
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px', marginBottom: '12px' }}>
                  <option value="">请选择字段</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>
                <button
                  className="btn btn-primary"
                  onClick={runStatisticalAnalysis}
                  disabled={!selectedField || loading}
                  style={{ width: '100%' }}>
                  {loading ? '分析中...' : '执行统计分析'}
                </button>
              </div>
            )}

            {activeTab === 'distribution' && (
              <div>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择分析字段</h3>
                <select
                  value={selectedDistField}
                  onChange={(e) => setSelectedDistField(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px', marginBottom: '12px' }}>
                  <option value="">请选择字段</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>
                
                <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>数据设置</h3>
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={removeEmpty}
                      onChange={(e) => setRemoveEmpty(e.target.checked)}
                    />
                    <span style={{ fontSize: '13px' }}>去掉空数据</span>
                  </label>
                </div>
                
                <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>选择分布类型</h3>
                <div style={{ marginBottom: '12px' }}>
                  {distributionOptions.map(dist => (
                    <label key={dist.value} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={selectedDistributions.includes(dist.value)}
                        onChange={() => {
                          setSelectedDistributions(prev => 
                            prev.includes(dist.value)
                              ? prev.filter(d => d !== dist.value)
                              : [...prev, dist.value]
                          )
                        }}
                      />
                      <span style={{ fontSize: '13px' }}>{dist.label}</span>
                    </label>
                  ))}
                </div>
                
                <button
                  className="btn btn-primary"
                  onClick={runDistributionAnalysis}
                  disabled={!selectedDistField || selectedDistributions.length === 0 || loading}
                  style={{ width: '100%' }}>
                  {loading ? '分析中...' : '执行分布拟合'}
                </button>
              </div>
            )}

            {activeTab === 'regression' && (
              <div>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>回归类型</h3>
                <select
                  value={regressionType}
                  onChange={(e) => setRegressionType(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px', marginBottom: '12px' }}>
                  {regressionTypes.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>

                {regressionType === 'polynomial' && (
                  <>
                    <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>回归设置</h3>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', marginBottom: '4px', fontSize: '13px', color: '#374151' }}>多项式阶数 (Degree)</label>
                      <input
                        type="number"
                        value={polynomialDegree}
                        onChange={(e) => setPolynomialDegree(Math.max(1, parseInt(e.target.value) || 2))}
                        min="1"
                        max="10"
                        style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>
                  </>
                )}

                <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>因变量 (Y)</h3>
                <select
                  value={dependentVar}
                  onChange={(e) => setDependentVar(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px', marginBottom: '12px' }}>
                  <option value="">请选择因变量</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>

                <h3 style={{ margin: '16px 0 12px 0', fontSize: '14px', fontWeight: 600, color: '#374151' }}>自变量 (X)</h3>
                <div style={{ marginBottom: '12px' }}>
                  {getNumericFields().map(f => (
                    <label key={f.field_id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={independentVars.includes(f.field_name)}
                        onChange={() => toggleIndependentVar(f.field_name)}
                        disabled={f.field_name === dependentVar}
                      />
                      <span style={{ fontSize: '13px', color: f.field_name === dependentVar ? '#9ca3af' : '#374151' }}>
                        {f.field_name}
                      </span>
                    </label>
                  ))}
                </div>
                
                <button
                  className="btn btn-primary"
                  onClick={runRegressionAnalysis}
                  disabled={!dependentVar || independentVars.length === 0 || loading}
                  style={{ width: '100%' }}>
                  {loading ? '分析中...' : '执行回归分析'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* 右侧结果展示区域 */}
      <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '16px', overflowY: 'auto' }}>
        {!selectedSnapshot ? (
          <div className="empty-state" style={{ height: '100%' }}>
            <p>请选择数据快照开始高级统计分析</p>
          </div>
        ) : activeTab === 'statistical' && statisticalResult ? (
          <div>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
              统计描述分析结果 - {statisticalResult.field}
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>基础统计量</h4>
                <table style={{ width: '100%', fontSize: '13px' }}>
                  <tbody>
                    <tr><td>样本量</td><td style={{ textAlign: 'right', fontWeight: 600 }}>{statisticalResult.sample_size}</td></tr>
                    <tr><td>均值</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.mean}</td></tr>
                    <tr><td>中位数</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.median}</td></tr>
                    <tr><td>标准差</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.std}</td></tr>
                    <tr><td>方差</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.variance}</td></tr>
                    <tr><td>最小值</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.min}</td></tr>
                    <tr><td>最大值</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.max}</td></tr>
                    <tr><td>极差</td><td style={{ textAlign: 'right' }}>{statisticalResult.basic_stats.range}</td></tr>
                  </tbody>
                </table>
              </div>

              <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>形状统计量</h4>
                <table style={{ width: '100%', fontSize: '13px' }}>
                  <tbody>
                    <tr><td>偏度</td><td style={{ textAlign: 'right' }}>{statisticalResult.shape_stats.skewness}</td></tr>
                    <tr><td>峰度</td><td style={{ textAlign: 'right' }}>{statisticalResult.shape_stats.kurtosis}</td></tr>
                    <tr><td>变异系数</td><td style={{ textAlign: 'right' }}>{statisticalResult.shape_stats.cv || 'N/A'}</td></tr>
                    <tr><td>Q1 (25%)</td><td style={{ textAlign: 'right' }}>{statisticalResult.quantiles.q1}</td></tr>
                    <tr><td>Q3 (75%)</td><td style={{ textAlign: 'right' }}>{statisticalResult.quantiles.q3}</td></tr>
                    <tr><td>IQR</td><td style={{ textAlign: 'right' }}>{statisticalResult.quantiles.iqr}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>95% 置信区间</h4>
              <p style={{ margin: 0, fontSize: '13px' }}>
                [{statisticalResult.confidence_interval.lower}, {statisticalResult.confidence_interval.upper}]
              </p>
            </div>

            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>正态性检验</h4>
              <table style={{ width: '100%', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <th style={{ textAlign: 'left', padding: '8px 0' }}>检验方法</th>
                    <th style={{ textAlign: 'right', padding: '8px 0' }}>统计量</th>
                    <th style={{ textAlign: 'right', padding: '8px 0' }}>P值</th>
                    <th style={{ textAlign: 'center', padding: '8px 0' }}>是否正态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Shapiro-Wilk</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.shapiro_wilk.statistic || 'N/A'}</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.shapiro_wilk.p_value || 'N/A'}</td>
                    <td style={{ textAlign: 'center' }}>
                      {statisticalResult.normality_tests.shapiro_wilk.is_normal === null ? 'N/A' : 
                       statisticalResult.normality_tests.shapiro_wilk.is_normal ? '✅ 是' : '❌ 否'}
                    </td>
                  </tr>
                  <tr>
                    <td>Kolmogorov-Smirnov</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.kolmogorov_smirnov.statistic}</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.kolmogorov_smirnov.p_value}</td>
                    <td style={{ textAlign: 'center' }}>
                      {statisticalResult.normality_tests.kolmogorov_smirnov.is_normal ? '✅ 是' : '❌ 否'}
                    </td>
                  </tr>
                  <tr>
                    <td>Jarque-Bera</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.jarque_bera.statistic}</td>
                    <td style={{ textAlign: 'right' }}>{statisticalResult.normality_tests.jarque_bera.p_value}</td>
                    <td style={{ textAlign: 'center' }}>
                      {statisticalResult.normality_tests.jarque_bera.is_normal ? '✅ 是' : '❌ 否'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        ) : activeTab === 'distribution' && distributionResult ? (
          <div>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
              分布拟合分析结果 - {distributionResult.field}
            </h3>
            
            {distributionResult.best_fit && (
              <div style={{ background: '#dcfce7', border: '1px solid #86efac', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#166534' }}>最佳拟合分布</h4>
                <p style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#166534' }}>
                  {distributionResult.best_fit.distribution}
                </p>
                <p style={{ margin: '8px 0 0 0', fontSize: '13px', color: '#166534' }}>
                  KS检验 P值: {distributionResult.best_fit.ks_test.p_value} 
                  ({distributionResult.best_fit.ks_test.fit_good ? '拟合良好' : '拟合不佳'})
                </p>
              </div>
            )}

            {/* 分布拟合图 */}
            {distributionResult.chart_data && (
              <div style={{ marginBottom: '20px', height: '400px' }}>
                <ReactECharts 
                  option={getDistributionChartOption(
                    distributionResult.chart_data, 
                    distributionResult.best_fit?.distribution
                  )}
                  style={{ height: '100%', width: '100%' }}
                />
              </div>
            )}

            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>所有分布拟合结果</h4>
              <table style={{ width: '100%', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <th style={{ textAlign: 'left', padding: '8px 0' }}>分布</th>
                    <th style={{ textAlign: 'right', padding: '8px 0' }}>KS统计量</th>
                    <th style={{ textAlign: 'right', padding: '8px 0' }}>P值</th>
                    <th style={{ textAlign: 'center', padding: '8px 0' }}>拟合评价</th>
                  </tr>
                </thead>
                <tbody>
                  {distributionResult.all_fits.map((fit, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px 0' }}>{fit.distribution}</td>
                      <td style={{ textAlign: 'right' }}>{fit.ks_test.statistic}</td>
                      <td style={{ textAlign: 'right' }}>{fit.ks_test.p_value}</td>
                      <td style={{ textAlign: 'center' }}>
                        {fit.ks_test.fit_good ? 
                          <span style={{ color: '#22c55e' }}>✅ 良好</span> : 
                          <span style={{ color: '#ef4444' }}>❌ 不佳</span>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : activeTab === 'regression' && regressionResult ? (
          <div>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#374151' }}>
              {regressionResult.regression_type}
            </h3>
            
            {regressionResult.formula && (
              <div style={{ background: '#dbeafe', border: '1px solid #93c5fd', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1e40af' }}>拟合公式</h4>
                <p style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#1e40af', fontFamily: 'monospace' }}>
                  {regressionResult.formula}
                </p>
              </div>
            )}
            
            {/* 回归拟合图 */}
            {regressionResult.chart_data && (
              <div style={{ marginBottom: '20px', height: '400px' }}>
                <ReactECharts 
                  option={getRegressionChartOption(
                    regressionResult.chart_data, 
                    regressionResult.dependent_var,
                    regressionResult.independent_vars[0]
                  )}
                  style={{ height: '100%', width: '100%' }}
                />
              </div>
            )}
            
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>模型信息</h4>
              <p style={{ margin: '4px 0', fontSize: '13px' }}><strong>因变量:</strong> {regressionResult.dependent_var}</p>
              <p style={{ margin: '4px 0', fontSize: '13px' }}><strong>自变量:</strong> {regressionResult.independent_vars.join(', ')}</p>
              <p style={{ margin: '4px 0', fontSize: '13px' }}><strong>样本量:</strong> {regressionResult.sample_size}</p>
              <p style={{ margin: '4px 0', fontSize: '13px' }}><strong>截距:</strong> {regressionResult.intercept}</p>
            </div>

            {regressionResult.coefficients && Object.keys(regressionResult.coefficients).length > 0 && (
              <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>回归系数</h4>
                <table style={{ width: '100%', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <th style={{ textAlign: 'left', padding: '8px 0' }}>变量</th>
                      <th style={{ textAlign: 'right', padding: '8px 0' }}>系数</th>
                      {regressionResult.coefficients[Object.keys(regressionResult.coefficients)[0]]?.std_error !== undefined && (
                        <>
                          <th style={{ textAlign: 'right', padding: '8px 0' }}>标准误</th>
                          <th style={{ textAlign: 'right', padding: '8px 0' }}>t值</th>
                          <th style={{ textAlign: 'right', padding: '8px 0' }}>P值</th>
                          <th style={{ textAlign: 'center', padding: '8px 0' }}>显著性</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(regressionResult.coefficients).map(([variable, coef], idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '8px 0' }}>{variable}</td>
                        <td style={{ textAlign: 'right' }}>
                          {typeof coef === 'object' ? coef.coefficient : coef}
                        </td>
                        {coef.std_error !== undefined && (
                          <>
                            <td style={{ textAlign: 'right' }}>{coef.std_error}</td>
                            <td style={{ textAlign: 'right' }}>{coef.t_value}</td>
                            <td style={{ textAlign: 'right' }}>{coef.p_value}</td>
                            <td style={{ textAlign: 'center' }}>
                              {coef.significant ? 
                                <span style={{ color: '#22c55e' }}>✅ 显著</span> : 
                                <span style={{ color: '#9ca3af' }}>不显著</span>
                              }
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#374151' }}>模型评估</h4>
              <table style={{ width: '100%', fontSize: '13px' }}>
                <tbody>
                  <tr>
                    <td>R²</td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>{regressionResult.model_stats.r_squared}</td>
                  </tr>
                  {regressionResult.model_stats.mse !== undefined && (
                    <tr>
                      <td>均方误差 (MSE)</td>
                      <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.mse}</td>
                    </tr>
                  )}
                  {regressionResult.model_stats.adjusted_r_squared !== undefined && (
                    <tr>
                      <td>调整R²</td>
                      <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.adjusted_r_squared}</td>
                    </tr>
                  )}
                  {regressionResult.model_stats.f_statistic !== undefined && (
                    <>
                      <tr>
                        <td>F统计量</td>
                        <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.f_statistic}</td>
                      </tr>
                      <tr>
                        <td>F检验P值</td>
                        <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.f_pvalue}</td>
                      </tr>
                    </>
                  )}
                  {regressionResult.model_stats.aic !== undefined && (
                    <tr>
                      <td>AIC</td>
                      <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.aic}</td>
                    </tr>
                  )}
                  {regressionResult.model_stats.bic !== undefined && (
                    <tr>
                      <td>BIC</td>
                      <td style={{ textAlign: 'right' }}>{regressionResult.model_stats.bic}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="empty-state" style={{ height: '100%' }}>
            <p>选择分析参数并执行分析</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdvancedStats
