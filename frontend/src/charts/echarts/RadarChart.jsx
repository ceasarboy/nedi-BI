import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function RadarChart({ data, config = {} }) {
  const { fields = [], title = '雷达图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const indicators = fields.map(field => ({ name: field, max: 100 }))
  
  const radarData = data?.map((item, index) => ({
    name: `数据${index + 1}`,
    value: fields.map(field => item[field] || 0)
  })) || []

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {},
    legend: {
      data: radarData.map(item => item.name),
      bottom: 10
    },
    radar: {
      indicator: indicators
    },
    series: [
      {
        name: '雷达图',
        type: 'radar',
        data: radarData,
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default RadarChart
