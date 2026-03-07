# PB-BI 图表系统使用指南

## 一、支持的图表类型

### 1. 基础图表（6种）
| 图表类型 | 组件 | MCP工具 | 适用场景 |
|----------|------|---------|----------|
| 柱状图 | BarChart.jsx | pbbi_generate_bar_chart | 分类对比 |
| 饼图 | PieChart.jsx | pbbi_generate_pie_chart | 占比分析 |
| 折线图 | LineChart.jsx | pbbi_generate_line_chart | 趋势分析 |
| 散点图 | ScatterChart.jsx | pbbi_generate_scatter_chart | 相关性分析 |
| 雷达图 | RadarChart.jsx | pbbi_generate_radar_chart | 多维对比 |
| 箱线图 | - | pbbi_generate_box_plot | 分布分析 |

### 2. 高级图表（4种）
| 图表类型 | 组件 | MCP工具 | 适用场景 |
|----------|------|---------|----------|
| 热力图 | HeatMap.jsx | pbbi_generate_heatmap | 密度分析 |
| 漏斗图 | FunnelChart.jsx | pbbi_generate_funnel_chart | 转化分析 |
| 仪表盘 | GaugeChart.jsx | pbbi_generate_gauge_chart | 指标展示 |
| 直方图 | - | pbbi_generate_histogram | 频率分布 |

### 3. 3D图表（4种）
| 图表类型 | 组件 | MCP工具 | 适用场景 |
|----------|------|---------|----------|
| 3D柱状图 | Bar3DChart.jsx | pbbi_generate_bar3d_chart | 立体对比 |
| 3D散点图 | Scatter3DChart.jsx | pbbi_generate_scatter3d_chart | 立体分布 |
| 3D曲面图 | Surface3DChart.jsx | pbbi_generate_surface3d_chart | 立体形貌 |
| LED晶圆图 | LEDWaferChart.jsx | pbbi_generate_led_wafer_chart | 晶圆分析 |

### 4. 组合图表（5种）
| 图表类型 | 组件 | MCP工具 | 适用场景 |
|----------|------|---------|----------|
| 堆叠柱状图 | StackedBarChart.jsx | pbbi_generate_stacked_bar_chart | 构成分析 |
| 堆叠折线图 | StackedLineChart.jsx | pbbi_generate_stacked_line_chart | 趋势构成 |
| 多Y轴图 | MultipleYAxisChart.jsx | pbbi_generate_multiple_y_axis_chart | 多指标对比 |
| 联动图表 | LinkedChart.jsx | pbbi_generate_linked_chart | 折线图+饼图 |
| 组合图 | - | pbbi_generate_combination_chart | 多类型组合 |

---

## 二、图表组件架构

### 1. 前端组件结构
```
frontend/src/charts/echarts/
├── theme.js           # 主题配置（浅色/Bloomberg暗黑）
├── ThemedChart.jsx    # 主题包装组件
├── BarChart.jsx       # 柱状图
├── LineChart.jsx      # 折线图
├── PieChart.jsx       # 饼图
├── ScatterChart.jsx   # 散点图
├── RadarChart.jsx     # 雷达图
├── HeatMap.jsx        # 热力图
├── FunnelChart.jsx    # 漏斗图
├── GaugeChart.jsx     # 仪表盘
├── Bar3DChart.jsx     # 3D柱状图
├── Scatter3DChart.jsx # 3D散点图
├── Surface3DChart.jsx # 3D曲面图
├── LEDWaferChart.jsx  # LED晶圆图
├── StackedBarChart.jsx    # 堆叠柱状图
├── StackedLineChart.jsx   # 堆叠折线图
├── MultipleYAxisChart.jsx # 多Y轴图
└── LinkedChart.jsx    # 联动图表
```

### 2. ThemedChart包装组件
```jsx
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
```

---

## 三、主题系统

### 1. Bloomberg暗黑主题
```javascript
const bloombergDarkTheme = {
  backgroundColor: '#0a0a0a',
  title: { textStyle: { color: '#ff6600' } },
  legend: { textStyle: { color: '#00ff00' } },
  xAxis: { axisLine: { lineStyle: { color: '#333' } } },
  yAxis: { axisLine: { lineStyle: { color: '#333' } } },
  // ...
}
```

### 2. 主题切换
```javascript
function getThemeName() {
  const theme = document.documentElement.getAttribute('data-theme')
  return theme === 'bloomberg' ? 'bloomberg-dark' : 'light'
}
```

---

## 四、MCP图表工具

### 1. 工具调用格式
```python
@server.tool("pbbi_generate_bar_chart")
async def generate_bar_chart(
    title: str,
    x_field: str,
    y_field: str,
    data: list[dict],
    color: str = "#5470c6"
) -> dict:
    # 生成matplotlib图表并保存
    # 返回文件路径
```

### 2. 图表缓存
```python
class ChartCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get_key(self, chart_type: str, data_hash: str) -> str:
        return f"{chart_type}_{data_hash}"
    
    def get(self, key: str) -> Optional[str]:
        return self.cache.get(key)
    
    def set(self, key: str, file_path: str):
        if len(self.cache) >= self.max_size:
            self.cache.popitem()
        self.cache[key] = file_path
```

---

## 五、图表导出

### 1. 前端导出
```javascript
const exportPNG = () => {
  const url = chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: theme === 'bloomberg-dark' ? '#0a0a0a' : '#fff'
  })
  const link = document.createElement('a')
  link.download = `chart_${Date.now()}.png`
  link.href = url
  link.click()
}
```

### 2. 后端导出API
```python
@router.get("/chart-export/{filename}/png")
async def export_png(filename: str):
    file_path = CHART_DIR / filename
    return FileResponse(file_path, media_type="image/png")
```

---

## 六、中文字体支持

### 1. 字体检测
```python
def get_chinese_font():
    font_names = [
        'SimHei', 'Microsoft YaHei', 'PingFang SC',
        'Hiragino Sans GB', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC'
    ]
    for font in font_names:
        try:
            fm.findfont(font)
            return font
        except:
            continue
    return None
```

### 2. 字体配置
```python
plt.rcParams['font.sans-serif'] = [get_chinese_font()]
plt.rcParams['axes.unicode_minus'] = False
```

---

## 七、图表推荐系统

### 1. 数据特征分析
```python
class DataFeatureAnalyzer:
    def analyze(self, data: pd.DataFrame) -> DataFeatures:
        return DataFeatures(
            row_count=len(data),
            column_count=len(data.columns),
            numeric_columns=self._get_numeric_columns(data),
            categorical_columns=self._get_categorical_columns(data),
            time_columns=self._get_time_columns(data),
            distribution=self._analyze_distribution(data),
            correlation=self._analyze_correlation(data)
        )
```

### 2. 推荐规则
```python
recommendation_rules = [
    RecommendationRule(
        name="trend_analysis",
        condition=lambda f: f.has_time_column and f.row_count > 10,
        chart_types=["line", "area"],
        score=0.9
    ),
    RecommendationRule(
        name="comparison",
        condition=lambda f: f.categorical_count <= 10 and f.has_numeric,
        chart_types=["bar", "column"],
        score=0.85
    ),
    # ...
]
```

---

## 八、常见问题

### 1. 图表不显示
**检查项**：
- 数据是否正确加载
- 字段配置是否正确
- 图表类型是否支持该数据格式

### 2. 中文乱码
**解决方案**：
- 确保系统安装中文字体
- 检查matplotlib字体配置
- 使用字体检测函数自动选择

### 3. 3D图表性能问题
**解决方案**：
- 减少数据点数量
- 使用采样或聚合
- 关闭自动旋转

### 4. 主题不生效
**检查项**：
- `data-theme`属性是否正确设置
- ThemedChart组件是否正确使用
- CSS变量是否正确加载

---

## 九、相关文件

| 文件 | 说明 |
|------|------|
| `frontend/src/charts/echarts/*.jsx` | 前端图表组件 |
| `src/mcp/chart_tools.py` | MCP图表工具 |
| `src/services/chart_recommendation.py` | 图表推荐服务 |
| `src/api/chart_config.py` | 图表配置API |

---

## 十、经验教训

1. **主题一致性**：所有图表组件都应使用ThemedChart包装，确保主题一致
2. **中文字体**：需要检测多种字体，兼容不同操作系统
3. **图表缓存**：避免重复生成相同图表，提升性能
4. **数据格式**：不同图表对数据格式要求不同，需要预处理
5. **交互功能**：ECharts支持丰富的交互，应充分利用
