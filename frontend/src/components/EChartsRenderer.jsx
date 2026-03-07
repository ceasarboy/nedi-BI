import { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import 'echarts-gl'
import { getThemeName, applyThemeToOption } from '../charts/echarts/theme'

const EChartsRenderer = ({ 
  config, 
  style = { height: 400 }, 
  onChartClick,
  exportable = true,
  theme: propTheme
}) => {
  const chartRef = useRef(null)
  const chartInstance = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const getActiveTheme = () => {
    return propTheme || getThemeName()
  }

  useEffect(() => {
    if (!config || !chartRef.current) return

    const initChart = async () => {
      try {
        setLoading(true)
        setError(null)

        if (chartInstance.current) {
          chartInstance.current.dispose()
        }

        const themeName = getActiveTheme()
        chartInstance.current = echarts.init(chartRef.current, themeName)

        let option = config.option || config

        if (config.data_url) {
          const response = await fetch(config.data_url)
          const data = await response.json()
          
          if (config.chart_type === 'bar' || config.chart_type === 'line') {
            option.xAxis.data = data.map(item => item[config.x_field])
            option.series[0].data = data.map(item => item[config.y_field])
          } else if (config.chart_type === 'pie') {
            option.series[0].data = data.map(item => ({
              name: item[config.category_field],
              value: item[config.value_field]
            }))
          } else if (config.chart_type === 'scatter') {
            option.series[0].data = data.map(item => [
              item[config.x_field],
              item[config.y_field]
            ])
          } else if (config.chart_type === 'heatmap') {
            const xCategories = [...new Set(data.map(item => item[config.x_field]))]
            const yCategories = [...new Set(data.map(item => item[config.y_field]))]
            option.xAxis.data = xCategories
            option.yAxis.data = yCategories
            option.series[0].data = data.map(item => [
              xCategories.indexOf(item[config.x_field]),
              yCategories.indexOf(item[config.y_field]),
              item[config.value_field]
            ])
          }
        }

        const themedOption = applyThemeToOption(option, themeName)
        chartInstance.current.setOption(themedOption, true)

        if (onChartClick) {
          chartInstance.current.on('click', onChartClick)
        }

        setLoading(false)
      } catch (err) {
        setError(err.message)
        setLoading(false)
      }
    }

    initChart()

    const handleResize = () => {
      chartInstance.current?.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chartInstance.current?.dispose()
    }
  }, [config, propTheme])

  const exportPNG = () => {
    if (!chartInstance.current) return
    
    const themeName = getActiveTheme()
    const url = chartInstance.current.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: themeName === 'bloomberg-dark' ? '#0a0a0a' : '#fff'
    })
    
    const link = document.createElement('a')
    link.download = `chart_${Date.now()}.png`
    link.href = url
    link.click()
  }

  const exportSVG = () => {
    if (!chartInstance.current) return
    
    const themeName = getActiveTheme()
    const url = chartInstance.current.getDataURL({
      type: 'svg',
      backgroundColor: themeName === 'bloomberg-dark' ? '#0a0a0a' : '#fff'
    })
    
    const link = document.createElement('a')
    link.download = `chart_${Date.now()}.svg`
    link.href = url
    link.click()
  }

  if (error) {
    return (
      <div className="echarts-error" style={style}>
        <span>❌ 图表加载失败: {error}</span>
      </div>
    )
  }

  return (
    <div className="echarts-container" style={style}>
      {loading && (
        <div className="echarts-loading">
          <div className="spinner"></div>
          <span>加载图表中...</span>
        </div>
      )}
      
      <div 
        ref={chartRef} 
        style={{ width: '100%', height: '100%' }}
      />
      
      {exportable && !loading && (
        <div className="echarts-toolbar">
          <button onClick={exportPNG} title="导出PNG">
            📷 PNG
          </button>
          <button onClick={exportSVG} title="导出SVG">
            📐 SVG
          </button>
        </div>
      )}
    </div>
  )
}

export const generateChartOption = (chartType, data, config) => {
  const baseOption = {
    title: {
      text: config.title || '',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: chartType === 'pie' ? 'item' : 'axis',
      confine: true
    },
    toolbox: {
      feature: {
        saveAsImage: { title: '保存图片' },
        dataZoom: { title: { zoom: '区域缩放', back: '区域还原' } },
        restore: { title: '还原' }
      },
      right: 20
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }

  switch (chartType) {
    case 'bar':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: data.map(item => item[config.x_field]),
          axisLabel: { rotate: config.rotate || 0 }
        },
        yAxis: {
          type: 'value',
          name: config.y_field
        },
        series: [{
          type: 'bar',
          data: data.map(item => item[config.y_field]),
          itemStyle: {
            color: config.color || '#3b82f6'
          },
          label: {
            show: config.show_labels || false,
            position: 'top'
          }
        }]
      }

    case 'line':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: data.map(item => item[config.x_field]),
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          name: config.y_field
        },
        series: [{
          type: 'line',
          data: data.map(item => item[config.y_field]),
          smooth: config.smooth || false,
          itemStyle: {
            color: config.color || '#3b82f6'
          },
          areaStyle: config.area ? { opacity: 0.3 } : null
        }]
      }

    case 'pie':
      return {
        ...baseOption,
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'middle'
        },
        series: [{
          type: 'pie',
          radius: config.radius || ['40%', '70%'],
          center: ['60%', '50%'],
          data: data.map(item => ({
            name: item[config.category_field],
            value: item[config.value_field]
          })),
          label: {
            show: true,
            formatter: '{b}: {d}%'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          }
        }]
      }

    case 'scatter':
      return {
        ...baseOption,
        xAxis: {
          type: 'value',
          name: config.x_field,
          scale: true
        },
        yAxis: {
          type: 'value',
          name: config.y_field,
          scale: true
        },
        series: [{
          type: 'scatter',
          data: data.map(item => [item[config.x_field], item[config.y_field]]),
          symbolSize: config.symbol_size || 10,
          itemStyle: {
            color: config.color || '#3b82f6'
          }
        }]
      }

    case 'histogram':
      const values = data.map(item => item[config.value_field])
      const min = Math.min(...values)
      const max = Math.max(...values)
      const binCount = config.bins || 10
      const binWidth = (max - min) / binCount
      
      const bins = Array(binCount).fill(0)
      values.forEach(v => {
        const binIndex = Math.min(Math.floor((v - min) / binWidth), binCount - 1)
        bins[binIndex]++
      })
      
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: bins.map((_, i) => (min + i * binWidth).toFixed(1))
        },
        yAxis: {
          type: 'value',
          name: '频次'
        },
        series: [{
          type: 'bar',
          data: bins,
          itemStyle: {
            color: config.color || '#3b82f6'
          }
        }]
      }

    case 'heatmap':
      const xCategories = [...new Set(data.map(item => item[config.x_field]))]
      const yCategories = [...new Set(data.map(item => item[config.y_field]))]
      
      return {
        ...baseOption,
        tooltip: {
          position: 'top',
          formatter: (params) => {
            return `${xCategories[params.data[0]]}, ${yCategories[params.data[1]]}: ${params.data[2]}`
          }
        },
        grid: {
          top: 60,
          bottom: 60
        },
        xAxis: {
          type: 'category',
          data: xCategories,
          splitArea: { show: true }
        },
        yAxis: {
          type: 'category',
          data: yCategories,
          splitArea: { show: true }
        },
        visualMap: {
          min: Math.min(...data.map(item => item[config.value_field])),
          max: Math.max(...data.map(item => item[config.value_field])),
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 0
        },
        series: [{
          type: 'heatmap',
          data: data.map(item => [
            xCategories.indexOf(item[config.x_field]),
            yCategories.indexOf(item[config.y_field]),
            item[config.value_field]
          ]),
          label: {
            show: config.show_labels || false
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }

    case 'radar':
      const indicators = config.fields.map(field => ({
        name: field,
        max: Math.max(...data.map(item => item[field]))
      }))
      
      return {
        ...baseOption,
        radar: {
          indicator: indicators,
          shape: config.shape || 'polygon'
        },
        series: [{
          type: 'radar',
          data: data.map((item, index) => ({
            name: item[config.name_field] || `数据${index + 1}`,
            value: config.fields.map(field => item[field])
          }))
        }]
      }

    case 'boxplot':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: config.categories || ['数据']
        },
        yAxis: {
          type: 'value',
          name: config.y_field
        },
        series: [{
          type: 'boxplot',
          data: [data]
        }]
      }

    case 'scatter_3d':
      return {
        ...baseOption,
        tooltip: {},
        visualMap: {
          show: true,
          dimension: 2,
          min: Math.min(...data.map(item => item[config.z_field])),
          max: Math.max(...data.map(item => item[config.z_field])),
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
                    '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          }
        },
        xAxis3D: { type: 'value', name: config.x_field },
        yAxis3D: { type: 'value', name: config.y_field },
        zAxis3D: { type: 'value', name: config.z_field },
        grid3D: {
          viewControl: {
            autoRotate: config.auto_rotate || false
          }
        },
        series: [{
          type: 'scatter3D',
          data: data.map(item => [
            item[config.x_field],
            item[config.y_field],
            item[config.z_field]
          ]),
          symbolSize: config.symbol_size || 10
        }]
      }

    case 'bar_3d':
      const xCat3d = [...new Set(data.map(item => item[config.x_field]))]
      const yCat3d = [...new Set(data.map(item => item[config.y_field]))]
      
      return {
        ...baseOption,
        visualMap: {
          show: true,
          min: Math.min(...data.map(item => item[config.value_field])),
          max: Math.max(...data.map(item => item[config.value_field])),
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
                    '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          }
        },
        xAxis3D: { type: 'category', data: xCat3d },
        yAxis3D: { type: 'category', data: yCat3d },
        zAxis3D: { type: 'value' },
        grid3D: {
          viewControl: {
            autoRotate: config.auto_rotate || false
          }
        },
        series: [{
          type: 'bar3D',
          data: data.map(item => [
            xCat3d.indexOf(item[config.x_field]),
            yCat3d.indexOf(item[config.y_field]),
            item[config.value_field]
          ]),
          shading: 'lambert',
          label: {
            show: config.show_labels || false
          }
        }]
      }

    case 'surface_3d':
      return {
        ...baseOption,
        visualMap: {
          show: true,
          dimension: 2,
          min: -1,
          max: 1,
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
                    '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          }
        },
        xAxis3D: { type: 'value' },
        yAxis3D: { type: 'value' },
        zAxis3D: { type: 'value' },
        grid3D: {
          viewControl: {
            autoRotate: config.auto_rotate || true
          }
        },
        series: [{
          type: 'surface',
          wireframe: {
            show: config.show_wireframe || false
          },
          shading: 'color',
          equation: config.equation || {
            x: { step: 0.05 },
            y: { step: 0.05 },
            z: (x, y) => Math.sin(x) * Math.cos(y)
          }
        }]
      }

    default:
      return baseOption
  }
}

export default EChartsRenderer
