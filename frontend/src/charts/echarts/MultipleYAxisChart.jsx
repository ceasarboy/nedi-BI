import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function MultipleYAxisChart({ data, config = {} }) {
  const { xAxisField, yAxisFields = [], title = '多Y轴图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const xData = data?.map(item => item[xAxisField]) || []

  const series = yAxisFields.map((field, index) => ({
    name: field,
    type: index === 0 ? 'line' : (index === 1 ? 'bar' : 'line'),
    yAxisIndex: index,
    data: data?.map(item => parseFloat(item[field]) || 0) || []
  }))

  const yAxis = yAxisFields.map((field, index) => ({
    type: 'value',
    name: field,
    position: index % 2 === 0 ? 'left' : 'right',
    offset: index > 1 ? (index - 1) * 60 : 0,
    axisLine: {
      show: true,
      lineStyle: {
        color: colors[index % colors.length]
      }
    },
    axisLabel: {
      formatter: '{value}'
    }
  }))

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: yAxisFields,
      bottom: 10
    },
    grid: {
      right: '20%'
    },
    xAxis: [
      {
        type: 'category',
        axisTick: {
          alignWithLabel: true
        },
        data: xData
      }
    ],
    yAxis: yAxis,
    series: series
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default MultipleYAxisChart
