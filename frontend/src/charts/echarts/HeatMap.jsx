import ReactECharts from 'echarts-for-react'
import { getColorList, getSingleColor } from '../../utils/colorSchemes'

function HeatMap({ data, config = {} }) {
  const { xAxisField, yAxisField, valueField, title = '热力图-ECharts', colorScheme = 'default' } = config
  const colors = getColorList(colorScheme)
  const singleColor = getSingleColor(colorScheme)

  const xCategories = [...new Set(data?.map(item => item[xAxisField]))] || []
  const yCategories = [...new Set(data?.map(item => item[yAxisField]))] || []
  
  const heatData = data?.map(item => [
    xCategories.indexOf(item[xAxisField]),
    yCategories.indexOf(item[yAxisField]),
    item[valueField] || 0
  ]) || []

  const getVisualMapColors = (scheme) => {
    switch(scheme) {
      case 'blue':
        return ['#e0f2fe', '#0ea5e9', '#0369a1']
      case 'green':
        return ['#dcfce7', '#22c55e', '#15803d']
      case 'purple':
        return ['#f3e8ff', '#a855f7', '#7c3aed']
      case 'orange':
        return ['#ffedd5', '#f97316', '#c2410c']
      case 'red':
        return ['#fee2e2', '#ef4444', '#b91c1c']
      case 'cyan':
        return ['#cffafe', '#06b6d4', '#0891b2']
      case 'pink':
        return ['#fce7f3', '#ec4899', '#be185d']
      case 'yellow':
        return ['#fef9c3', '#eab308', '#a16207']
      case 'warm':
        return ['#fef3c7', '#f59e0b', '#b45309']
      case 'cool':
        return ['#e0f2fe', '#3b82f6', '#1e40af']
      case 'vintage':
        return ['#fef3c7', '#d97706', '#92400e']
      case 'rainbow':
        return ['#fee2e2', '#a855f7', '#3b82f6']
      default:
        return ['#f0f9eb', '#5470c6', '#2a335b']
    }
  }

  const option = {
    color: colors,
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      position: 'top',
      formatter: function (params) {
        return `${xCategories[params.data[0]]} - ${yCategories[params.data[1]]}: ${params.data[2]}`
      }
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: xCategories,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: yCategories,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: Math.max(...heatData.map(d => d[2])) || 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      inRange: {
        color: getVisualMapColors(colorScheme)
      }
    },
    series: [
      {
        name: '热力图',
        type: 'heatmap',
        data: heatData,
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
}

export default HeatMap
