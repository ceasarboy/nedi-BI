# PB-BI MCP集成指南

## 一、MCP概述

MCP (Model Context Protocol) 是一种标准化的工具调用协议，允许AI模型通过统一的接口调用外部工具。

### 1. PB-BI MCP架构
```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (OpenAI兼容)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (FastAPI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  数据工具(7) │  │ 图表工具(19)│  │  分析工具   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│   SQLite │ 明道云API │ 图表文件                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、MCP工具分类

### 1. 数据工具（7个）
| 工具名称 | 功能 | 参数 |
|----------|------|------|
| pbbi_list_dataflows | 列出所有数据流 | 无 |
| pbbi_list_snapshots | 列出所有数据快照 | 无 |
| pbbi_get_snapshot_data | 获取快照数据 | snapshot_id, limit |
| pbbi_get_snapshot_fields | 获取快照字段 | snapshot_id |
| pbbi_query_data | 查询数据 | snapshot_id, fields, filters |
| pbbi_get_field_stats | 获取字段统计 | snapshot_id, field |
| pbbi_search_data | 搜索数据 | snapshot_id, keyword |

### 2. 图表工具（19个）
| 分类 | 工具名称 | 功能 |
|------|----------|------|
| 基础图表 | pbbi_generate_bar_chart | 柱状图 |
| | pbbi_generate_pie_chart | 饼图 |
| | pbbi_generate_line_chart | 折线图 |
| | pbbi_generate_scatter_chart | 散点图 |
| | pbbi_generate_box_plot | 箱线图 |
| | pbbi_generate_histogram | 直方图 |
| 高级图表 | pbbi_generate_heatmap | 热力图 |
| | pbbi_generate_radar_chart | 雷达图 |
| | pbbi_generate_funnel_chart | 漏斗图 |
| | pbbi_generate_gauge_chart | 仪表盘 |
| 3D图表 | pbbi_generate_bar3d_chart | 3D柱状图 |
| | pbbi_generate_scatter3d_chart | 3D散点图 |
| | pbbi_generate_surface3d_chart | 3D曲面图 |
| | pbbi_generate_led_wafer_chart | LED晶圆图 |
| 组合图表 | pbbi_generate_combination_chart | 组合图 |
| | pbbi_generate_multiple_y_axis_chart | 多Y轴图 |
| | pbbi_generate_stacked_bar_chart | 堆叠柱状图 |
| | pbbi_generate_stacked_line_chart | 堆叠折线图 |
| | pbbi_generate_linked_chart | 联动图表 |

---

## 三、MCP工具定义

### 1. 工具装饰器
```python
from mcp.server import Server

server = Server("pbbi-mcp")

@server.tool("pbbi_generate_bar_chart")
async def generate_bar_chart(
    title: str,
    x_field: str,
    y_field: str,
    data: list[dict],
    color: str = "#5470c6",
    show_legend: bool = True
) -> dict:
    """
    生成柱状图
    
    Args:
        title: 图表标题
        x_field: X轴字段名
        y_field: Y轴字段名
        data: 数据列表
        color: 柱子颜色
        show_legend: 是否显示图例
    
    Returns:
        包含图表文件路径的字典
    """
    # 实现图表生成逻辑
    file_path = await create_bar_chart(title, x_field, y_field, data, color)
    return {"file_path": file_path, "url": f"/charts/{file_path}"}
```

### 2. 数据工具示例
```python
@server.tool("pbbi_query_data")
async def query_data(
    snapshot_id: int,
    fields: list[str] = None,
    filters: dict = None,
    limit: int = 100
) -> dict:
    """
    查询数据快照中的数据
    
    Args:
        snapshot_id: 数据快照ID
        fields: 要查询的字段列表，为空则返回所有字段
        filters: 过滤条件，如 {"field": "value"}
        limit: 返回记录数限制
    
    Returns:
        包含字段列表和数据行的字典
    """
    snapshot = await get_snapshot(snapshot_id)
    df = pd.DataFrame(snapshot.rows)
    
    # 应用过滤条件
    if filters:
        for field, value in filters.items():
            df = df[df[field] == value]
    
    # 选择字段
    if fields:
        df = df[fields]
    
    return {
        "fields": list(df.columns),
        "rows": df.head(limit).to_dict('records'),
        "total": len(df)
    }
```

---

## 四、图表生成实现

### 1. 基础图表生成
```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

async def create_bar_chart(title: str, x_field: str, y_field: str, 
                           data: list, color: str) -> str:
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = [get_chinese_font()]
    plt.rcParams['axes.unicode_minus'] = False
    
    # 提取数据
    x_values = [d[x_field] for d in data]
    y_values = [d[y_field] for d in data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_values, y_values, color=color)
    ax.set_title(title)
    ax.set_xlabel(x_field)
    ax.set_ylabel(y_field)
    
    # 保存图表
    filename = f"bar_{int(time.time())}.png"
    file_path = CHART_DIR / filename
    plt.savefig(file_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filename
```

### 2. 3D图表生成
```python
async def create_bar3d_chart(title: str, x_field: str, y_field: str, 
                             z_field: str, data: list) -> str:
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 提取数据
    x_values = [d[x_field] for d in data]
    y_values = [d[y_field] for d in data]
    z_values = [d[z_field] for d in data]
    
    # 创建3D柱状图
    ax.bar3d(x_values, y_values, 0, 1, 1, z_values)
    ax.set_title(title)
    ax.set_xlabel(x_field)
    ax.set_ylabel(y_field)
    ax.set_zlabel(z_field)
    
    # 保存图表
    filename = f"bar3d_{int(time.time())}.png"
    plt.savefig(CHART_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filename
```

---

## 五、图表缓存机制

### 1. 缓存实现
```python
from functools import lru_cache
import hashlib

class ChartCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def _get_hash(self, chart_type: str, data: list, config: dict) -> str:
        content = f"{chart_type}_{json.dumps(data, sort_keys=True)}_{json.dumps(config)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, chart_type: str, data: list, config: dict) -> Optional[str]:
        key = self._get_hash(chart_type, data, config)
        return self.cache.get(key)
    
    def set(self, chart_type: str, data: list, config: dict, file_path: str):
        key = self._get_hash(chart_type, data, config)
        if len(self.cache) >= self.max_size:
            # 移除最旧的缓存
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = file_path

chart_cache = ChartCache()
```

### 2. 使用缓存
```python
@server.tool("pbbi_generate_bar_chart")
async def generate_bar_chart(...):
    # 检查缓存
    cached = chart_cache.get("bar", data, {"title": title, "x": x_field, "y": y_field})
    if cached:
        return {"file_path": cached, "url": f"/charts/{cached}", "cached": True}
    
    # 生成新图表
    file_path = await create_bar_chart(...)
    
    # 存入缓存
    chart_cache.set("bar", data, {"title": title, "x": x_field, "y": y_field}, file_path)
    
    return {"file_path": file_path, "url": f"/charts/{file_path}"}
```

---

## 六、中文字体支持

### 1. 字体检测
```python
import matplotlib.font_manager as fm

def get_chinese_font():
    """检测并返回可用的中文字体"""
    font_names = [
        'SimHei',           # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'PingFang SC',      # 苹方
        'Hiragino Sans GB', # 冬青黑体
        'WenQuanYi Micro Hei',  # 文泉驿
        'Noto Sans CJK SC', # 思源黑体
        'DejaVu Sans'       # 备用
    ]
    
    for font_name in font_names:
        try:
            font_path = fm.findfont(font_name)
            if font_path and 'DejaVu' not in font_path:
                return font_name
        except:
            continue
    
    return 'SimHei'  # 默认返回
```

### 2. 字体配置
```python
def setup_chinese_font():
    font = get_chinese_font()
    plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
```

---

## 七、与AI Agent集成

### 1. 工具注册
```python
def get_mcp_tools():
    """获取所有MCP工具定义"""
    return [
        {
            "type": "function",
            "function": {
                "name": "pbbi_query_data",
                "description": "查询数据快照中的数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                        "fields": {"type": "array", "items": {"type": "string"}},
                        "limit": {"type": "integer", "default": 100}
                    },
                    "required": ["snapshot_id"]
                }
            }
        },
        # ... 其他工具定义
    ]
```

### 2. 工具调用处理
```python
async def handle_tool_call(self, tool_name: str, arguments: dict):
    """处理AI工具调用"""
    if tool_name.startswith("pbbi_"):
        # 调用MCP工具
        result = await self.mcp_client.call_tool(tool_name, arguments)
        return result
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
```

---

## 八、错误处理

### 1. 工具调用错误
```python
@server.tool("pbbi_query_data")
async def query_data(snapshot_id: int, ...):
    try:
        # 验证参数
        if snapshot_id <= 0:
            return {"error": "无效的快照ID"}
        
        # 执行查询
        result = await do_query(snapshot_id)
        
        return {"success": True, "data": result}
    
    except SnapshotNotFound:
        return {"error": f"快照 {snapshot_id} 不存在"}
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}
```

### 2. 图表生成错误
```python
async def create_chart_safely(chart_type: str, **kwargs):
    try:
        if chart_type == "bar":
            return await create_bar_chart(**kwargs)
        elif chart_type == "line":
            return await create_line_chart(**kwargs)
        # ...
    except Exception as e:
        # 返回错误图表
        return await create_error_chart(str(e))
```

---

## 九、相关文件

| 文件 | 说明 |
|------|------|
| `src/mcp/server.py` | MCP服务器主文件 |
| `src/mcp/data_tools.py` | 数据工具定义 |
| `src/mcp/chart_tools.py` | 图表工具定义 |
| `src/ai/agent.py` | AI Agent集成 |
| `docs/PB-BI-MCP使用指南.md` | MCP使用文档 |

---

## 十、经验教训

1. **工具命名规范**：使用`pbbi_`前缀统一命名，避免与其他MCP工具冲突
2. **中文字体**：必须检测多种字体，兼容不同操作系统
3. **图表缓存**：避免重复生成相同图表，提升性能
4. **错误处理**：工具调用要有完善的错误处理，返回明确的错误信息
5. **参数验证**：在工具执行前验证参数，避免无效操作
6. **文件命名**：使用时间戳生成唯一文件名，避免冲突
7. **资源清理**：图表生成后及时关闭matplotlib图形，释放内存
