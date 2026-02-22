import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function BarChart({ data, config = {} }) {
  const { xAxisField, yAxisField, title = '柱状图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const xData = data?.map(item => item[xAxisField]) || []
  const yData = data?.map(item => item[yAxisField]) || []

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
      data: [yAxisField || '数值'],
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
    series: [
      {
        name: yAxisField || '数值',
        type: 'bar',
        data: yData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default BarChart
