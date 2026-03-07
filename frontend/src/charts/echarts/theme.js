import * as echarts from 'echarts'

export const lightTheme = {
  color: [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
  ],
  backgroundColor: 'transparent',
  title: {
    textStyle: {
      color: '#1a1a2e',
      fontWeight: 'bold'
    },
    subtextStyle: {
      color: '#666'
    }
  },
  legend: {
    textStyle: {
      color: '#333'
    }
  },
  xAxis: {
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#666'
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6'
      }
    }
  },
  yAxis: {
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#666'
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6'
      }
    }
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e5e7eb',
    textStyle: {
      color: '#333'
    }
  }
}

export const bloombergDarkTheme = {
  color: [
    '#ff6600', '#00ff00', '#00ffff', '#ff00ff', '#ffff00',
    '#ff3333', '#33ff33', '#3333ff', '#ff9900', '#00ff99'
  ],
  backgroundColor: 'transparent',
  title: {
    textStyle: {
      color: '#ff6600',
      fontWeight: 'bold',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    },
    subtextStyle: {
      color: '#00ff00',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    }
  },
  legend: {
    textStyle: {
      color: '#00ff00',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    }
  },
  xAxis: {
    axisLine: {
      lineStyle: {
        color: '#1a1a1a'
      }
    },
    axisLabel: {
      color: '#00ff00',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    },
    splitLine: {
      lineStyle: {
        color: '#1a1a1a'
      }
    }
  },
  yAxis: {
    axisLine: {
      lineStyle: {
        color: '#1a1a1a'
      }
    },
    axisLabel: {
      color: '#00ff00',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    },
    splitLine: {
      lineStyle: {
        color: '#1a1a1a'
      }
    }
  },
  tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    borderColor: '#ff6600',
    textStyle: {
      color: '#00ff00',
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace'
    }
  }
}

export const getTheme = () => {
  const theme = document.body.getAttribute('data-theme')
  return theme === 'bloomberg-dark' ? bloombergDarkTheme : lightTheme
}

export const getThemeName = () => {
  const theme = document.body.getAttribute('data-theme')
  return theme === 'bloomberg-dark' ? 'bloomberg-dark' : 'light'
}

export const applyThemeToOption = (option, themeName = null) => {
  const theme = themeName === 'bloomberg-dark' ? bloombergDarkTheme : 
                themeName === 'light' ? lightTheme : 
                getTheme()
  
  return {
    ...theme,
    ...option,
    title: {
      ...theme.title,
      ...option.title
    },
    legend: {
      ...theme.legend,
      ...option.legend
    },
    xAxis: option.xAxis ? {
      ...theme.xAxis,
      ...option.xAxis,
      axisLine: {
        ...theme.xAxis?.axisLine,
        ...option.xAxis?.axisLine
      },
      axisLabel: {
        ...theme.xAxis?.axisLabel,
        ...option.xAxis?.axisLabel
      },
      splitLine: {
        ...theme.xAxis?.splitLine,
        ...option.xAxis?.splitLine
      }
    } : theme.xAxis,
    yAxis: option.yAxis ? {
      ...theme.yAxis,
      ...option.yAxis,
      axisLine: {
        ...theme.yAxis?.axisLine,
        ...option.yAxis?.axisLine
      },
      axisLabel: {
        ...theme.yAxis?.axisLabel,
        ...option.yAxis?.axisLabel
      },
      splitLine: {
        ...theme.yAxis?.splitLine,
        ...option.yAxis?.splitLine
      }
    } : theme.yAxis,
    tooltip: {
      ...theme.tooltip,
      ...option.tooltip
    }
  }
}

export const registerThemes = () => {
  echarts.registerTheme('light', lightTheme)
  echarts.registerTheme('bloomberg-dark', bloombergDarkTheme)
}

registerThemes()
