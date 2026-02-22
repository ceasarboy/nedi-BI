import ReactECharts from 'echarts-for-react'
import { getColorList } from '../../utils/colorSchemes'

function FunnelChart({ data, config = {} }) {
  const { nameField, valueField, title = '漏斗图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)

  const funnelData = data?.map(item => ({
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
      formatter: '{a} <br/>{b} : {c}'
    },
    series: [
      {
        name: '漏斗图',
        type: 'funnel',
        left: '10%',
        width: '80%',
        label: {
          show: true,
          position: 'inside'
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 20
          }
        },
        data: funnelData
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default FunnelChart
