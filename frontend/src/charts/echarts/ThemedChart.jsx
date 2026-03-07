import ReactECharts from 'echarts-for-react'
import { getThemeName, applyThemeToOption } from './theme'

function ThemedChart({ option, style, opts, onEvents, ...props }) {
  const themeName = getThemeName()
  
  const themedOption = applyThemeToOption(option, themeName)
  
  return (
    <ReactECharts
      option={themedOption}
      style={style}
      opts={opts}
      onEvents={onEvents}
      theme={themeName}
      {...props}
    />
  )
}

export default ThemedChart
