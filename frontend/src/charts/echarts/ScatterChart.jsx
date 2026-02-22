import ReactECharts from 'echarts-for-react'
import { getColorList, getSingleColor } from '../../utils/colorSchemes'

function ScatterChart({ data, config = {} }) {
  const { xAxisField, yAxisField, title = '散点图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)
  const singleColor = getSingleColor(colorScheme)

  const scatterData = data?.map(item => [item[xAxisField], item[yAxisField]]) || []

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    grid: {
      left: '3%',
      right: '7%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: xAxisField || 'X轴'
    },
    yAxis: {
      type: 'value',
      name: yAxisField || 'Y轴'
    },
    series: [
      {
        name: '散点',
        type: 'scatter',
        data: scatterData,
        symbolSize: 15,
        itemStyle: {
          color: singleColor
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default ScatterChart
