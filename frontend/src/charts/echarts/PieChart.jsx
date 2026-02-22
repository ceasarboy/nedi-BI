import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function PieChart({ data, config = {} }) {
  const { nameField, valueField, title = '饼图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const pieData = data?.map(item => ({
    name: item[nameField] || '未知',
    value: item[valueField] || 0
  })) || []

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: nameField || '数据',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default PieChart
