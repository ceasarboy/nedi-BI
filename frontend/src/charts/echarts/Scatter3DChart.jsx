import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import 'echarts-gl'
import { getColorList, getSingleColor } from '../../utils/colorSchemes'

function Scatter3DChart({ data, config = {} }) {
  const { xAxisField, yAxisField, zAxisField, title = '3D散点图-ECharts', colorScheme = 'default' } = config
  const [chartData, setChartData] = useState([])
  const colors = getColorList(colorScheme)
  const singleColor = getSingleColor(colorScheme)

  useEffect(() => {
    console.log('Scatter3DChart 接收到的数据:', data)
    console.log('Scatter3DChart 配置:', config)
    
    if (data && data.length > 0) {
      const processed = data.map((item) => {
        const x = parseFloat(item[xAxisField] || 0)
        const y = parseFloat(item[yAxisField] || 0)
        const z = parseFloat(item[zAxisField] || 0)
        return [x, y, z]
      })
      console.log('处理后的3D散点数据:', processed)
      setChartData(processed)
    }
  }, [data, xAxisField, yAxisField, zAxisField])

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      formatter: function (params) {
        return `${xAxisField || 'X'}: ${params.value[0]}<br/>${yAxisField || 'Y'}: ${params.value[1]}<br/>${zAxisField || 'Z'}: ${params.value[2]}`
      }
    },
    xAxis3D: {
      type: 'value',
      name: xAxisField || 'X轴'
    },
    yAxis3D: {
      type: 'value',
      name: yAxisField || 'Y轴'
    },
    zAxis3D: {
      type: 'value',
      name: zAxisField || 'Z轴'
    },
    grid3D: {
      viewControl: {
        projection: 'orthographic',
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 200
      },
      boxWidth: 200,
      boxDepth: 200,
      boxHeight: 200,
      light: {
        main: {
          intensity: 1.2
        },
        ambient: {
          intensity: 0.3
        }
      }
    },
    series: [
      {
        type: 'scatter3D',
        data: chartData,
        symbolSize: 15,
        itemStyle: {
          opacity: 0.8,
          color: singleColor
        }
      }
    ]
  }

  console.log('ECharts option:', option)

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
    </div>
  )
}

export default Scatter3DChart
