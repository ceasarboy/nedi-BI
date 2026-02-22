import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function StackedLineChart({ data, config = {} }) {
  const { xAxisField, yAxisFields = [], title = '堆叠折线图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const xData = data?.map(item => item[xAxisField]) || []

  const series = yAxisFields.map(field => ({
    name: field,
    type: 'line',
    stack: 'total',
    data: data?.map(item => parseFloat(item[field]) || 0) || [],
    smooth: true,
    areaStyle: {}
  }))

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
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
      boundaryGap: false,
      data: xData
    },
    yAxis: {
      type: 'value'
    },
    series: series
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default StackedLineChart
