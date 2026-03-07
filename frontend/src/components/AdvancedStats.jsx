import { useState, useEffect } from 'react'
import ThemedChart from '../charts/echarts/ThemedChart'
import { analysisAPI } from '../services/api'
import '../styles/AnalysisComponents.css'

function AdvancedStats({ snapshots, dataflowsMap }) {
  const [activeTab, setActiveTab] = useState('statistical')
  const [selectedSnapshot, setSelectedSnapshot] = useState(null)
  const [snapshotData, setSnapshotData] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const [selectedField, setSelectedField] = useState('')
  const [statisticalResult, setStatisticalResult] = useState(null)
  
  const [selectedDistField, setSelectedDistField] = useState('')
  const [selectedDistributions, setSelectedDistributions] = useState(['norm', 'expon', 'gamma', 'lognorm'])
  const [removeEmpty, setRemoveEmpty] = useState(true)
  const [distributionResult, setDistributionResult] = useState(null)
  
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
        itemStyle: { color: 'rgba(59, 130, 246, 0.6)' }
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
        lineStyle: { width: isBestFit ? 3 : 2, color: colors[idx % colors.length] },
        itemStyle: { color: colors[idx % colors.length] }
      })
    })
    
    return {
      title: { text: '分布拟合图', left: 'center', textStyle: { fontSize: 16, fontWeight: 600 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['直方图', ...fitted_curves.map(c => c.distribution)], top: 30 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 100, containLabel: true },
      xAxis: { type: 'value', name: '数值', min: histogram.bin_edges[0], max: histogram.bin_edges[histogram.bin_edges.length - 1] },
      yAxis: { type: 'value', name: '频数' },
      series: series
    }
  }

  const getRegressionChartOption = (chartData, dependentVar, independentVar) => {
    if (!chartData || !chartData.actual || !chartData.predicted) return {}
    
    const sortedActual = [...chartData.actual].sort((a, b) => a[0] - b[0])
    const sortedPredicted = [...chartData.predicted].sort((a, b) => a[0] - b[0])
    
    return {
      title: { text: '回归拟合图', left: 'center', textStyle: { fontSize: 16, fontWeight: 600 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['实际数据点', '拟合曲线'], top: 30 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 100, containLabel: true },
      xAxis: { type: 'value', name: independentVar || '自变量' },
      yAxis: { type: 'value', name: dependentVar || '因变量' },
      series: [
        { name: '实际数据点', type: 'scatter', data: sortedActual, itemStyle: { color: '#3b82f6' } },
        { name: '拟合曲线', type: 'line', smooth: true, data: sortedPredicted, symbol: 'none', lineStyle: { width: 3, color: '#ef4444' } }
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
      const response = await analysisAPI.statisticalAnalysis({ snapshot_id: selectedSnapshot.id, field: selectedField })
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
    setIndependentVars(prev => prev.includes(field) ? prev.filter(f => f !== field) : [...prev, field])
  }

  const getNumericFields = () => {
    if (!snapshotData || !snapshotData.fields) return []
    return snapshotData.fields.filter(f => f.data_type === 'number' || f.data_type === 'numeric')
  }

  return (
    <div className="analysis-container">
      <div className="analysis-sidebar">
        <h3 className="analysis-sidebar-title">选择数据快照</h3>
        <div className="param-group">
          {snapshots.map(s => (
            <div
              key={s.id}
              className={`snapshot-item ${selectedSnapshot?.id === s.id ? 'snapshot-item-active' : 'snapshot-item-default'}`}
              onClick={() => loadSnapshotData(s)}>
              <span className="snapshot-item-name">{s.name}</span>
            </div>
          ))}
        </div>

        {snapshotData && (
          <>
            <hr className="divider" />
            <div className="tab-group">
              {['statistical', 'distribution', 'regression'].map(tab => (
                <div
                  key={tab}
                  className={`tab-item ${activeTab === tab ? 'tab-item-active' : 'tab-item-default'}`}
                  onClick={() => setActiveTab(tab)}>
                  {tab === 'statistical' && '统计描述'}
                  {tab === 'distribution' && '分布拟合'}
                  {tab === 'regression' && '回归分析'}
                </div>
              ))}
            </div>

            {activeTab === 'statistical' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">选择分析字段</h3>
                <select
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                  className="param-select">
                  <option value="">请选择字段</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>
                <button className="btn btn-primary btn-execute" onClick={runStatisticalAnalysis} disabled={!selectedField || loading}>
                  {loading ? '分析中...' : '执行统计分析'}
                </button>
              </div>
            )}

            {activeTab === 'distribution' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">选择分析字段</h3>
                <select
                  value={selectedDistField}
                  onChange={(e) => setSelectedDistField(e.target.value)}
                  className="param-select">
                  <option value="">请选择字段</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>
                
                <h3 className="analysis-sidebar-title">数据设置</h3>
                <label className="checkbox-item">
                  <input type="checkbox" checked={removeEmpty} onChange={(e) => setRemoveEmpty(e.target.checked)} />
                  <span className="checkbox-label">去掉空数据</span>
                </label>
                
                <h3 className="analysis-sidebar-title">选择分布类型</h3>
                <div className="param-group">
                  {distributionOptions.map(dist => (
                    <label key={dist.value} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={selectedDistributions.includes(dist.value)}
                        onChange={() => {
                          setSelectedDistributions(prev => 
                            prev.includes(dist.value) ? prev.filter(d => d !== dist.value) : [...prev, dist.value]
                          )
                        }}
                      />
                      <span className="checkbox-label">{dist.label}</span>
                    </label>
                  ))}
                </div>
                
                <button
                  className="btn btn-primary btn-execute"
                  onClick={runDistributionAnalysis}
                  disabled={!selectedDistField || selectedDistributions.length === 0 || loading}>
                  {loading ? '分析中...' : '执行分布拟合'}
                </button>
              </div>
            )}

            {activeTab === 'regression' && (
              <div className="param-group">
                <h3 className="analysis-sidebar-title">回归类型</h3>
                <select value={regressionType} onChange={(e) => setRegressionType(e.target.value)} className="param-select">
                  {regressionTypes.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>

                {regressionType === 'polynomial' && (
                  <>
                    <h3 className="analysis-sidebar-title">回归设置</h3>
                    <div className="param-group">
                      <label className="param-label">多项式阶数 (Degree)</label>
                      <input
                        type="number"
                        value={polynomialDegree}
                        onChange={(e) => setPolynomialDegree(Math.max(1, parseInt(e.target.value) || 2))}
                        min="1"
                        max="10"
                        className="param-input"
                      />
                    </div>
                  </>
                )}

                <h3 className="analysis-sidebar-title">因变量 (Y)</h3>
                <select value={dependentVar} onChange={(e) => setDependentVar(e.target.value)} className="param-select">
                  <option value="">请选择因变量</option>
                  {getNumericFields().map(f => (
                    <option key={f.field_id} value={f.field_name}>{f.field_name}</option>
                  ))}
                </select>

                <h3 className="analysis-sidebar-title">自变量 (X)</h3>
                <div className="param-group">
                  {getNumericFields().map(f => (
                    <label key={f.field_id} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={independentVars.includes(f.field_name)}
                        onChange={() => toggleIndependentVar(f.field_name)}
                        disabled={f.field_name === dependentVar}
                      />
                      <span className={`checkbox-label ${f.field_name === dependentVar ? 'checkbox-label-disabled' : ''}`}>
                        {f.field_name}
                      </span>
                    </label>
                  ))}
                </div>
                
                <button
                  className="btn btn-primary btn-execute"
                  onClick={runRegressionAnalysis}
                  disabled={!dependentVar || independentVars.length === 0 || loading}>
                  {loading ? '分析中...' : '执行回归分析'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="analysis-main">
        {!selectedSnapshot ? (
          <div className="empty-state">
            <p>请选择数据快照开始高级统计分析</p>
          </div>
        ) : activeTab === 'statistical' && statisticalResult ? (
          <div className="result-section">
            <h3 className="result-title">统计描述分析结果 - {statisticalResult.field}</h3>
            
            <div className="result-grid">
              <div className="result-box result-box-default">
                <h4 className="result-box-title result-box-title-default">基础统计量</h4>
                <table className="result-table">
                  <tbody>
                    <tr><td>样本量</td><td>{statisticalResult.sample_size}</td></tr>
                    <tr><td>均值</td><td>{statisticalResult.basic_stats.mean}</td></tr>
                    <tr><td>中位数</td><td>{statisticalResult.basic_stats.median}</td></tr>
                    <tr><td>标准差</td><td>{statisticalResult.basic_stats.std}</td></tr>
                    <tr><td>方差</td><td>{statisticalResult.basic_stats.variance}</td></tr>
                    <tr><td>最小值</td><td>{statisticalResult.basic_stats.min}</td></tr>
                    <tr><td>最大值</td><td>{statisticalResult.basic_stats.max}</td></tr>
                    <tr><td>极差</td><td>{statisticalResult.basic_stats.range}</td></tr>
                  </tbody>
                </table>
              </div>

              <div className="result-box result-box-default">
                <h4 className="result-box-title result-box-title-default">形状统计量</h4>
                <table className="result-table">
                  <tbody>
                    <tr><td>偏度</td><td>{statisticalResult.shape_stats.skewness}</td></tr>
                    <tr><td>峰度</td><td>{statisticalResult.shape_stats.kurtosis}</td></tr>
                    <tr><td>变异系数</td><td>{statisticalResult.shape_stats.cv || 'N/A'}</td></tr>
                    <tr><td>Q1 (25%)</td><td>{statisticalResult.quantiles.q1}</td></tr>
                    <tr><td>Q3 (75%)</td><td>{statisticalResult.quantiles.q3}</td></tr>
                    <tr><td>IQR</td><td>{statisticalResult.quantiles.iqr}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="result-box result-box-default">
              <h4 className="result-box-title result-box-title-default">95% 置信区间</h4>
              <p className="result-text">
                [{statisticalResult.confidence_interval.lower}, {statisticalResult.confidence_interval.upper}]
              </p>
            </div>

            <div className="result-box result-box-default">
              <h4 className="result-box-title result-box-title-default">正态性检验</h4>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>检验方法</th>
                    <th>统计量</th>
                    <th>P值</th>
                    <th>是否正态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Shapiro-Wilk</td>
                    <td>{statisticalResult.normality_tests.shapiro_wilk.statistic || 'N/A'}</td>
                    <td>{statisticalResult.normality_tests.shapiro_wilk.p_value || 'N/A'}</td>
                    <td>
                      {statisticalResult.normality_tests.shapiro_wilk.is_normal === null ? 'N/A' : 
                       statisticalResult.normality_tests.shapiro_wilk.is_normal ? '✅ 是' : '❌ 否'}
                    </td>
                  </tr>
                  <tr>
                    <td>Kolmogorov-Smirnov</td>
                    <td>{statisticalResult.normality_tests.kolmogorov_smirnov.statistic}</td>
                    <td>{statisticalResult.normality_tests.kolmogorov_smirnov.p_value}</td>
                    <td>{statisticalResult.normality_tests.kolmogorov_smirnov.is_normal ? '✅ 是' : '❌ 否'}</td>
                  </tr>
                  <tr>
                    <td>Jarque-Bera</td>
                    <td>{statisticalResult.normality_tests.jarque_bera.statistic}</td>
                    <td>{statisticalResult.normality_tests.jarque_bera.p_value}</td>
                    <td>{statisticalResult.normality_tests.jarque_bera.is_normal ? '✅ 是' : '❌ 否'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        ) : activeTab === 'distribution' && distributionResult ? (
          <div className="result-section">
            <h3 className="result-title">分布拟合分析结果 - {distributionResult.field}</h3>
            
            {distributionResult.best_fit && (
              <div className="result-box result-box-success">
                <h4 className="result-box-title result-box-title-success">最佳拟合分布</h4>
                <p className="result-text result-text-highlight result-text-success">
                  {distributionResult.best_fit.distribution}
                </p>
                <p className="result-text result-text-success">
                  KS检验 P值: {distributionResult.best_fit.ks_test.p_value} 
                  ({distributionResult.best_fit.ks_test.fit_good ? '拟合良好' : '拟合不佳'})
                </p>
              </div>
            )}

            {distributionResult.chart_data && (
              <div className="chart-container">
                <ThemedChart 
                  option={getDistributionChartOption(distributionResult.chart_data, distributionResult.best_fit?.distribution)}
                  style={{ height: '100%', width: '100%' }}
                />
              </div>
            )}

            <div className="result-box result-box-default">
              <h4 className="result-box-title result-box-title-default">所有分布拟合结果</h4>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>分布</th>
                    <th>KS统计量</th>
                    <th>P值</th>
                    <th>拟合评价</th>
                  </tr>
                </thead>
                <tbody>
                  {distributionResult.all_fits.map((fit, idx) => (
                    <tr key={idx}>
                      <td>{fit.distribution}</td>
                      <td>{fit.ks_test.statistic}</td>
                      <td>{fit.ks_test.p_value}</td>
                      <td>
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
          <div className="result-section">
            <h3 className="result-title">{regressionResult.regression_type}</h3>
            
            {regressionResult.formula && (
              <div className="result-box result-box-info">
                <h4 className="result-box-title result-box-title-info">拟合公式</h4>
                <p className="result-text result-text-highlight result-text-info" style={{ fontFamily: 'monospace' }}>
                  {regressionResult.formula}
                </p>
              </div>
            )}
            
            {regressionResult.chart_data && (
              <div className="chart-container">
                <ThemedChart 
                  option={getRegressionChartOption(regressionResult.chart_data, regressionResult.dependent_var, regressionResult.independent_vars[0])}
                  style={{ height: '100%', width: '100%' }}
                />
              </div>
            )}
            
            <div className="result-box result-box-default">
              <h4 className="result-box-title result-box-title-default">模型信息</h4>
              <p className="result-text"><strong>因变量:</strong> {regressionResult.dependent_var}</p>
              <p className="result-text"><strong>自变量:</strong> {regressionResult.independent_vars.join(', ')}</p>
              <p className="result-text"><strong>样本量:</strong> {regressionResult.sample_size}</p>
              <p className="result-text"><strong>截距:</strong> {regressionResult.intercept}</p>
            </div>

            {regressionResult.coefficients && Object.keys(regressionResult.coefficients).length > 0 && (
              <div className="result-box result-box-default">
                <h4 className="result-box-title result-box-title-default">回归系数</h4>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>变量</th>
                      <th>系数</th>
                      {regressionResult.coefficients[Object.keys(regressionResult.coefficients)[0]]?.std_error !== undefined && (
                        <>
                          <th>标准误</th>
                          <th>t值</th>
                          <th>P值</th>
                          <th>显著性</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(regressionResult.coefficients).map(([variable, coef], idx) => (
                      <tr key={idx}>
                        <td>{variable}</td>
                        <td>{typeof coef === 'object' ? coef.coefficient : coef}</td>
                        {coef.std_error !== undefined && (
                          <>
                            <td>{coef.std_error}</td>
                            <td>{coef.t_value}</td>
                            <td>{coef.p_value}</td>
                            <td>
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

            <div className="result-box result-box-default">
              <h4 className="result-box-title result-box-title-default">模型评估</h4>
              <table className="result-table">
                <tbody>
                  <tr><td>R²</td><td>{regressionResult.model_stats.r_squared}</td></tr>
                  {regressionResult.model_stats.mse !== undefined && (
                    <tr><td>均方误差 (MSE)</td><td>{regressionResult.model_stats.mse}</td></tr>
                  )}
                  {regressionResult.model_stats.adjusted_r_squared !== undefined && (
                    <tr><td>调整R²</td><td>{regressionResult.model_stats.adjusted_r_squared}</td></tr>
                  )}
                  {regressionResult.model_stats.f_statistic !== undefined && (
                    <>
                      <tr><td>F统计量</td><td>{regressionResult.model_stats.f_statistic}</td></tr>
                      <tr><td>F检验P值</td><td>{regressionResult.model_stats.f_pvalue}</td></tr>
                    </>
                  )}
                  {regressionResult.model_stats.aic !== undefined && (
                    <tr><td>AIC</td><td>{regressionResult.model_stats.aic}</td></tr>
                  )}
                  {regressionResult.model_stats.bic !== undefined && (
                    <tr><td>BIC</td><td>{regressionResult.model_stats.bic}</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <p>选择分析参数并执行分析</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdvancedStats
