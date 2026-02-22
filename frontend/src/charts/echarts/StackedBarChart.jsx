import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function StackedBarChart({ data, config = {} }) {
  const { xAxisField, yAxisFields = [], title = '堆叠柱状图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const xData = data?.map(item => item[xAxisField]) || []

  const series = yAxisFields.map((field, index) => ({
    name: field,
    type: 'bar',
    stack: 'total',
    data: data?.map(item => parseFloat(item[field]) || 0) || [],
    itemStyle: {
      borderRadius: index === yAxisFields.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]
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
        type: 'shadow'
      }
    },
    legend: {
      data: yAxisFields,
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: series
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default StackedBarChart
