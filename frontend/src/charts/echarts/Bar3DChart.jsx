import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import 'echarts-gl'
import { getSingleColor, getColorList } from '../../utils/colorSchemes'

function Bar3DChart({ data, config = {} }) {
  const { 
    xAxisField, 
    yAxisField, 
    zAxisField, 
    title = '3D柱状图-ECharts', 
    colorScheme = 'default',
    transparent = true,
    useVisualMap = true,
    opacity = 0.7
  } = config
  const [chartData, setChartData] = useState([])
  const [xCategories, setXCategories] = useState([])
  const [yCategories, setYCategories] = useState([])
  const colors = getColorList(colorScheme)

  useEffect(() => {
    console.log('Bar3DChart 接收到的数据:', data)
    console.log('Bar3DChart 配置:', config)
    
    if (data && data.length > 0) {
      const uniqueX = [...new Set(data.map(item => item[xAxisField]))].sort()
      const uniqueY = [...new Set(data.map(item => item[yAxisField]))].sort()
      
      setXCategories(uniqueX)
      setYCategories(uniqueY)
      
      const processed = data.map((item) => {
        const xIndex = uniqueX.indexOf(item[xAxisField])
        const yIndex = uniqueY.indexOf(item[yAxisField])
        const z = parseFloat(item[zAxisField]) || 0
        return [xIndex, yIndex, z]
      })
      
      console.log('处理后的3D数据:', processed)
      console.log('X轴类别:', uniqueX)
      console.log('Y轴类别:', uniqueY)
      setChartData(processed)
    }
  }, [data, xAxisField, yAxisField, zAxisField])

  const getVisualMapColors = (scheme) => {
    switch(scheme) {
      case 'blue':
        return ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8']
      case 'green':
        return ['#006837', '#1a9850', '#66bd63', '#a6d96a', '#d9ef8b']
      case 'purple':
        return ['#40004b', '#762a83', '#9970ab', '#c2a5cf', '#e7d4e8']
      case 'orange':
        return ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090']
      case 'red':
        return ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7']
      case 'cyan':
        return ['#003c30', '#01665e', '#35978f', '#80cdc1', '#c7eae5']
      case 'pink':
        return ['#8e0152', '#c51b7d', '#de77ae', '#f1b6da', '#fde0ef']
      case 'yellow':
        return ['#543005', '#8c510a', '#bf812d', '#dfc27d', '#f6e8c3']
      case 'warm':
        return ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7']
      case 'cool':
        return ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0']
      case 'vintage':
        return ['#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#c7eae5']
      case 'rainbow':
        return ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#fef0d9', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
      default:
        return ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    }
  }

  const getOpacityValue = () => {
    if (!transparent) return 1
    return opacity
  }

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      formatter: function (params) {
        const xVal = xCategories[params.value[0]]
        const yVal = yCategories[params.value[1]]
        const zVal = params.value[2].toFixed(2)
        return `${xAxisField}: ${xVal}<br/>${yAxisField}: ${yVal}<br/>${zAxisField}: ${zVal}`
      }
    },
    visualMap: useVisualMap ? {
      show: true,
      min: chartData.length > 0 ? Math.min(...chartData.map(d => d[2])) : 0,
      max: chartData.length > 0 ? Math.max(...chartData.map(d => d[2])) : 100,
      inRange: {
        color: getVisualMapColors(colorScheme)
      },
      calculable: true,
      realtime: false,
      splitNumber: 5,
      left: 'left',
      bottom: '5%'
    } : undefined,
    xAxis3D: {
      type: 'category',
      data: xCategories,
      name: xAxisField
    },
    yAxis3D: {
      type: 'category',
      data: yCategories,
      name: yAxisField
    },
    zAxis3D: {
      type: 'value',
      name: zAxisField
    },
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 300,
        alpha: 20,
        beta: 40
      },
      boxWidth: 200,
      boxDepth: 200,
      light: {
        main: {
          intensity: 1.5,
          shadow: false
        },
        ambient: {
          intensity: 0.6
        }
      }
    },
    series: [
      {
        type: 'bar3D',
        data: chartData,
        shading: 'color',
        label: {
          show: false
        },
        itemStyle: {
          opacity: getOpacityValue(),
          borderWidth: 1,
          borderColor: 'rgba(255,255,255,0.8)'
        },
        emphasis: {
          label: {
            show: false
          },
          itemStyle: {
            opacity: 0.9
          }
        }
      }
    ]
  }

  console.log('ECharts option:', option)

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      {chartData.length === 0 && data && data.length > 0 && (
        <div style={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)',
          background: '#fef3c7',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #fcd34d',
          zIndex: 100
        }}>
          <div style={{ fontWeight: 600, marginBottom: '8px' }}>调试信息</div>
          <div>数据行数: {data.length}</div>
          <div>配置字段: X={xAxisField}, Y={yAxisField}, Z={zAxisField}</div>
        </div>
      )}
    </div>
  )
}

export default Bar3DChart
