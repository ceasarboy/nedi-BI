import ReactECharts from 'echarts-for-react'
import { useEffect, useState, useRef } from 'react'
import { getColorList } from '../../utils/colorSchemes'

function LinkedChart({ data, config = {} }) {
  const { 
    xAxisField, 
    nameField, 
    valueField,
    title = '联动图表-ECharts', 
    colorScheme = 'default'
  } = config
  const [currentIndex, setCurrentIndex] = useState(0)
  const chartRef = useRef(null)
  const colors = getColorList(colorScheme)

  const processData = () => {
    if (!data || data.length === 0) return null

    const uniqueXValues = [...new Set(data.map(item => item[xAxisField]))].sort()
    const uniqueNames = [...new Set(data.map(item => item[nameField]))].sort()

    const source = [
      [nameField, ...uniqueXValues]
    ]

    uniqueNames.forEach(name => {
      const row = [name]
      uniqueXValues.forEach(x => {
        const item = data.find(d => d[xAxisField] === x && d[nameField] === name)
        row.push(parseFloat(item?.[valueField]) || 0)
      })
      source.push(row)
    })

    return { source, uniqueXValues, uniqueNames }
  }

  const processedData = processData()

  const getPieData = (index) => {
    if (!processedData) return []
    const { source, uniqueNames } = processedData
    return uniqueNames.map((name, i) => ({
      name,
      value: source[i + 1][index + 1] || 0
    }))
  }

  const getOption = () => {
    if (!processedData) {
      return {
        title: { text: title, left: 'center' }
      }
    }

    const { source, uniqueXValues } = processedData
    const pieData = getPieData(currentIndex)

    return {
      title: {
        text: title,
        left: 'center',
        top: 10
      },
      legend: {
        top: 50
      },
      tooltip: {
        trigger: 'axis'
      },
      dataset: {
        source
      },
      xAxis: [
        {
          type: 'category',
          name: xAxisField,
          gridIndex: 0
        }
      ],
      yAxis: [
        {
          gridIndex: 0,
          name: valueField
        }
      ],
      grid: [
        {
          top: 100,
          bottom: '55%',
          left: '10%',
          right: '10%'
        }
      ],
      series: [
        ...Array.from({ length: source.length - 1 }, (_, i) => ({
          type: 'line',
          smooth: true,
          seriesLayoutBy: 'row',
          emphasis: {
            focus: 'series'
          },
          encode: {
            x: 0,
            y: i + 1
          },
          xAxisIndex: 0,
          yAxisIndex: 0
        })),
        {
          type: 'pie',
          id: 'pie',
          radius: '30%',
          center: ['50%', '78%'],
          data: pieData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          }
        }
      ],
      graphic: [
        {
          type: 'text',
          left: 'center',
          top: 80,
          style: {
            text: uniqueXValues[currentIndex] || '',
            fontSize: 24,
            fontWeight: 'bold',
            fill: '#333'
          }
        }
      ]
    }
  }

  const onEvents = {
    updateAxisPointer: function (event) {
      if (event.axesInfo && event.axesInfo.length > 0) {
        const xInfo = event.axesInfo.find(info => info.dimension === 0)
        if (xInfo && xInfo.value !== undefined) {
          setCurrentIndex(xInfo.value)
          if (chartRef.current) {
            const echarts = chartRef.current.getEchartsInstance()
            if (echarts) {
              echarts.setOption({
                series: [{
                  id: 'pie',
                  data: getPieData(xInfo.value)
                }],
                graphic: [{
                  type: 'text',
                  left: 'center',
                  top: 80,
                  style: {
                    text: processedData?.uniqueXValues[xInfo.value] || ''
                  }
                }]
              })
            }
          }
        }
      }
    }
  }

  const handleChartReady = (echarts) => {
    chartRef.current = { getEchartsInstance: () => echarts }
  }

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactECharts
        ref={chartRef}
        option={getOption()}
        style={{ height: '100%', width: '100%' }}
        onEvents={onEvents}
        onChartReady={handleChartReady}
      />
    </div>
  )
}

export default LinkedChart
