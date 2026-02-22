import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import 'echarts-gl'

function wavelengthToRGB(wavelength) {
  let R = 0, G = 0, B = 0

  if (wavelength < 380 || wavelength > 780) {
    return '#808080'
  }

  if (wavelength >= 380 && wavelength < 410) {
    R = 0.6 - 0.41 * ((410 - wavelength) / 30)
    G = 0
    B = 0.39 + 0.6 * ((410 - wavelength) / 30)
  } else if (wavelength >= 410 && wavelength < 440) {
    R = 0.19 - 0.19 * ((440 - wavelength) / 30)
    G = 0
    B = 1
  } else if (wavelength >= 440 && wavelength < 490) {
    R = 0
    G = 1 - ((490 - wavelength) / 50)
    B = 1
  } else if (wavelength >= 490 && wavelength < 510) {
    R = 0
    G = 1
    B = ((510 - wavelength) / 20)
  } else if (wavelength >= 510 && wavelength < 580) {
    R = 1 - ((580 - wavelength) / 70)
    G = 1
    B = 0
  } else if (wavelength >= 580 && wavelength < 640) {
    R = 1
    G = ((640 - wavelength) / 60)
    B = 0
  } else if (wavelength >= 640 && wavelength < 700) {
    R = 1
    G = 0
    B = 0
  } else if (wavelength >= 700 && wavelength <= 780) {
    R = 0.35 - 0.65 * ((780 - wavelength) / 80)
    G = 0
    B = 0
  }

  R = Math.max(0, Math.min(1, R))
  G = Math.max(0, Math.min(1, G))
  B = Math.max(0, Math.min(1, B))

  const toHex = (n) => {
    const hex = Math.round(n * 255).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(R)}${toHex(G)}${toHex(B)}`
}

function LEDWaferChart({ data, config = {} }) {
  const { 
    xAxisField, 
    yAxisField, 
    zAxisField,
    wavelengthField,
    title = 'LED晶圆分析图-ECharts'
  } = config
  const [chartData, setChartData] = useState([])
  const [xCategories, setXCategories] = useState([])
  const [yCategories, setYCategories] = useState([])

  useEffect(() => {
    console.log('LEDWaferChart 接收到的数据:', data)
    console.log('LEDWaferChart 配置:', config)
    
    if (data && data.length > 0) {
      const uniqueX = [...new Set(data.map(item => item[xAxisField]))].sort()
      const uniqueY = [...new Set(data.map(item => item[yAxisField]))].sort()
      
      setXCategories(uniqueX)
      setYCategories(uniqueY)
      
      const processed = data.map((item) => {
        const xIndex = uniqueX.indexOf(item[xAxisField])
        const yIndex = uniqueY.indexOf(item[yAxisField])
        const z = parseFloat(item[zAxisField]) || 0
        const wavelength = parseFloat(item[wavelengthField]) || 550
        const color = wavelengthToRGB(wavelength)
        
        return {
          value: [xIndex, yIndex, z],
          wavelength: wavelength,
          itemStyle: {
            color: color
          }
        }
      })
      
      console.log('处理后的LED晶圆数据:', processed)
      console.log('X轴类别:', uniqueX)
      console.log('Y轴类别:', uniqueY)
      setChartData(processed)
    }
  }, [data, xAxisField, yAxisField, zAxisField, wavelengthField])

  const option = {
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      formatter: function (params) {
        const xVal = xCategories[params.value[0]]
        const yVal = yCategories[params.value[1]]
        const zVal = params.value[2].toFixed(2)
        const color = params.data?.itemStyle?.color || ''
        const wavelength = params.data?.wavelength || 0
        return `${xAxisField}: ${xVal}<br/>${yAxisField}: ${yVal}<br/>${zAxisField}: ${zVal}<br/>波长: ${wavelength.toFixed(1)} nm<br/>颜色: ${color}`
      }
    },
    xAxis3D: {
      type: 'category',
      data: xCategories,
      name: xAxisField
    },
    yAxis3D: {
      type: 'category',
      data: yCategories,
      name: yAxisField
    },
    zAxis3D: {
      type: 'value',
      name: zAxisField
    },
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 300,
        alpha: 20,
        beta: 40
      },
      boxWidth: 200,
      boxDepth: 200,
      light: {
        main: {
          intensity: 1.5,
          shadow: false
        },
        ambient: {
          intensity: 0.6
        }
      }
    },
    series: [
      {
        type: 'bar3D',
        data: chartData,
        shading: 'color',
        label: {
          show: false
        },
        itemStyle: {
          opacity: 0.8,
          borderWidth: 1,
          borderColor: 'rgba(255,255,255,0.8)'
        },
        emphasis: {
          label: {
            show: false
          },
          itemStyle: {
            opacity: 1
          }
        }
      }
    ]
  }

  console.log('ECharts option:', option)

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
      {chartData.length === 0 && data && data.length > 0 && (
        <div style={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)',
          background: '#fef3c7',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #fcd34d',
          zIndex: 100
        }}>
          <div style={{ fontWeight: 600, marginBottom: '8px' }}>调试信息</div>
          <div>数据行数: {data.length}</div>
          <div>配置字段: X={xAxisField}, Y={yAxisField}, Z={zAxisField}, Wavelength={wavelengthField}</div>
        </div>
      )}
    </div>
  )
}

export default LEDWaferChart
