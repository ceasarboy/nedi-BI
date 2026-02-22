import ReactECharts from 'echarts-for-react'
import { getSingleColor } from '../../utils/colorSchemes'

function GaugeChart({ data, config = {} }) {
  const { valueField, title = '仪表盘-ECharts', max = 100, colorScheme = 'default' } = config
  const color = getSingleColor(colorScheme)

  const value = data?.[0]?.[valueField] || 0

  const option = {
    color: [color],
    title: {
      text: title,
      left: 'center'
    },
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: max,
        splitNumber: 5,
        itemStyle: {
          color: color
        },
        progress: {
          show: true,
          width: 18
        },
        pointer: {
          show: false
        },
        axisLine: {
          lineStyle: {
            width: 18
          }
        },
        axisTick: {
          distance: -28,
          splitNumber: 5,
          lineStyle: {
            width: 2,
            color: '#999'
          }
        },
        splitLine: {
          distance: -35,
          length: 14,
          lineStyle: {
            width: 3,
            color: '#999'
          }
        },
        axisLabel: {
          distance: -20,
          color: '#999',
          fontSize: 12
        },
        anchor: {
          show: false
        },
        title: {
          show: false
        },
        detail: {
          valueAnimation: true,
          width: '60%',
          lineHeight: 40,
          borderRadius: 8,
          offsetCenter: [0, '-15%'],
          fontSize: 32,
          fontWeight: 'bolder',
          formatter: '{value}',
          color: 'inherit'
        },
        data: [
          {
            value: value
          }
        ]
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default GaugeChart
