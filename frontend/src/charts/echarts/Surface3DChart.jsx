import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import 'echarts-gl'
import { getColorList, getSingleColor } from '../../utils/colorSchemes'

function Surface3DChart({ data, config = {} }) {
  const { 
    xAxisField, 
    yAxisField, 
    zAxisField, 
    title = '3D形貌图-ECharts', 
    colorScheme = 'default',
    xStart = 0,
    xInterval = 1,
    yStart = 0,
    yInterval = 1,
    zStart = 0,
    zInterval = 10
  } = config
  const [chartData, setChartData] = useState([])
  const [xCategories, setXCategories] = useState([])
  const [yCategories, setYCategories] = useState([])
  const colors = getColorList(colorScheme)

  useEffect(() => {
    console.log('Surface3DChart 接收到的数据:', data)
    console.log('Surface3DChart 配置:', config)
    
    if (data && data.length > 0) {
      const uniqueX = [...new Set(data.map(item => item[xAxisField]))].sort()
      const uniqueY = [...new Set(data.map(item => item[yAxisField]))].sort()
      
      setXCategories(uniqueX)
      setYCategories(uniqueY)
      
      const dataMap = {}
      data.forEach(item => {
        const key = `${item[xAxisField]}-${item[yAxisField]}`
        dataMap[key] = parseFloat(item[zAxisField]) || 0
      })
      
      const processed = []
      uniqueX.forEach((xVal, xIndex) => {
        uniqueY.forEach((yVal, yIndex) => {
          const key = `${xVal}-${yVal}`
          const z = dataMap[key] ?? 0
          processed.push([xIndex, yIndex, z])
        })
      })
      
      console.log('处理后的3D表面数据:', processed)
      console.log('X轴类别:', uniqueX)
      console.log('Y轴类别:', uniqueY)
      setChartData(processed)
    } else {
      console.log('没有数据，生成测试数据')
      const testData = []
      for (let i = 0; i <= 30; i++) {
        for (let j = 0; j <= 30; j++) {
          const x = i
          const y = j
          const z = Math.sin(i / 5) * Math.cos(j / 5) * 10 + 20
          testData.push([x, y, z])
        }
      }
      setChartData(testData)
    }
  }, [data, xAxisField, yAxisField, zAxisField, xStart, xInterval, yStart, yInterval, zStart, zInterval])

  const getVisualMapColors = (scheme) => {
    switch(scheme) {
      case 'blue':
        return ['#e0f2fe', '#0ea5e9', '#0369a1']
      case 'green':
        return ['#dcfce7', '#22c55e', '#15803d']
      case 'purple':
        return ['#f3e8ff', '#a855f7', '#7c3aed']
      case 'orange':
        return ['#ffedd5', '#f97316', '#c2410c']
      case 'red':
        return ['#fee2e2', '#ef4444', '#b91c1c']
      case 'cyan':
        return ['#cffafe', '#06b6d4', '#0891b2']
      case 'pink':
        return ['#fce7f3', '#ec4899', '#be185d']
      case 'yellow':
        return ['#fef9c3', '#eab308', '#a16207']
      case 'warm':
        return ['#fef3c7', '#f59e0b', '#b45309']
      case 'cool':
        return ['#e0f2fe', '#3b82f6', '#1e40af']
      case 'vintage':
        return ['#fef3c7', '#d97706', '#92400e']
      case 'rainbow':
        return ['#fee2e2', '#a855f7', '#3b82f6']
      default:
        return ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    }
  }

  const formatNumber = (num) => {
    return Number(num).toFixed(2)
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
    visualMap: {
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
    },
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
      name: zAxisField,
      min: zStart,
      interval: zInterval,
      axisLabel: {
        formatter: function (value) {
          return formatNumber(value)
        }
      }
    },
    grid3D: {
      viewControl: {
        projection: 'perspective',
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 300,
        alpha: 20,
        beta: 40
      },
      boxWidth: 200,
      boxDepth: 200,
      boxHeight: 150,
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
        type: 'surface',
        data: chartData,
        shading: 'color',
        wireframe: {
          show: false
        }
      }
    ]
  }

  console.log('ECharts option:', option)

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      {chartData.length === 0 && (
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
          <div>数据行数: {data?.length || 0}</div>
          <div>配置字段: x={xAxisField}, y={yAxisField}, z={zAxisField}</div>
          <div>图表数据行数: {chartData.length}</div>
        </div>
      )}
    </div>
  )
}

export default Surface3DChart
