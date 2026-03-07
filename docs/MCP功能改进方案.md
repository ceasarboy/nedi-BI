# PB-BI MCP 功能改进方案 v3.2

## 版本信息
- 版本: v3.2
- 日期: 2026-03-05
- 状态: 设计中
- 原则: 调试阶段尽量多给AI工具使用，逐步训练AI少使用工具

---

## 一、MCP工具总览

| 分类 | 工具数量 | 功能 |
|------|---------|------|
| **Database MCP** | 4个 | 访问SQLite数据快照 |
| **MingDao MCP** | 4个 | 明道云API调用 |
| **LocalFile MCP** | 3个 | 本地文件上传处理 |
| **DataFlow MCP** | 3个 | 数据流配置管理 |
| **Snapshot MCP** | 3个 | 数据快照管理 |
| **Analysis MCP** | 8个 | 数据分析功能 |
| **Dashboard MCP** | 5个 | 看板管理功能 |
| **User MCP** | 2个 | 用户信息管理 |

**总计: 32个工具**

---

## 二、Database MCP (访问SQLite数据快照)

### `pbbi_list_snapshots` - 列出所有数据快照
```python
{
    "name": "pbbi_list_snapshots",
    "description": "列出SQLite数据库中所有可用的数据快照",
    "parameters": {
        "type": "object",
        "properties": {
            "data_flow_id": {"type": "integer", "description": "按数据流ID筛选"}
        },
        "required": []
    }
}
```

### `pbbi_get_snapshot_schema` - 获取快照结构
```python
{
    "name": "pbbi_get_snapshot_schema",
    "description": "获取数据快照的字段结构和样本数据",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"}
        },
        "required": ["snapshot_id"]
    }
}
```

### `pbbi_query_snapshot` - 查询快照数据
```python
{
    "name": "pbbi_query_snapshot",
    "description": "查询数据快照中的数据，支持筛选和分页",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "fields": {"type": "array", "items": {"type": "string"}, "description": "要返回的字段列表"},
            "filter": {"type": "string", "description": "筛选条件"},
            "page": {"type": "integer", "description": "页码，默认1"},
            "page_size": {"type": "integer", "description": "每页数量，默认100"}
        },
        "required": ["snapshot_id"]
    }
}
```

### `pbbi_execute_sql` - 执行SQL查询
```python
{
    "name": "pbbi_execute_sql",
    "description": "在SQLite数据库上执行只读SQL查询",
    "parameters": {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "SQL查询语句"}
        },
        "required": ["sql"]
    },
    "security": {
        "read_only": true,
        "blocked_keywords": ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"],
        "max_rows": 1000
    }
}
```

---

## 三、MingDao MCP (明道云API调用)

### `pbbi_mingdao_connect` - 连接明道云
```python
{
    "name": "pbbi_mingdao_connect",
    "description": "测试明道云API连接，验证认证参数是否正确",
    "parameters": {
        "type": "object",
        "properties": {
            "appkey": {"type": "string", "description": "明道云应用Key"},
            "sign": {"type": "string", "description": "明道云签名"},
            "worksheet_id": {"type": "string", "description": "工作表ID"},
            "is_private": {"type": "boolean", "description": "是否私有部署，默认false"},
            "private_api_url": {"type": "string", "description": "私有部署API地址"}
        },
        "required": ["appkey", "sign", "worksheet_id"]
    }
}
```

### `pbbi_mingdao_get_fields` - 获取工作表字段
```python
{
    "name": "pbbi_mingdao_get_fields",
    "description": "获取明道云工作表的字段列表",
    "parameters": {
        "type": "object",
        "properties": {
            "appkey": {"type": "string", "description": "明道云应用Key"},
            "sign": {"type": "string", "description": "明道云签名"},
            "worksheet_id": {"type": "string", "description": "工作表ID"},
            "is_private": {"type": "boolean", "description": "是否私有部署"},
            "private_api_url": {"type": "string", "description": "私有部署API地址"}
        },
        "required": ["appkey", "sign", "worksheet_id"]
    }
}
```

### `pbbi_mingdao_get_rows` - 获取工作表数据
```python
{
    "name": "pbbi_mingdao_get_rows",
    "description": "从明道云工作表获取数据行",
    "parameters": {
        "type": "object",
        "properties": {
            "appkey": {"type": "string", "description": "明道云应用Key"},
            "sign": {"type": "string", "description": "明道云签名"},
            "worksheet_id": {"type": "string", "description": "工作表ID"},
            "field_ids": {"type": "array", "items": {"type": "string"}, "description": "要获取的字段ID列表"},
            "page_index": {"type": "integer", "description": "页码，默认1"},
            "page_size": {"type": "integer", "description": "每页数量，默认100"},
            "is_private": {"type": "boolean", "description": "是否私有部署"},
            "private_api_url": {"type": "string", "description": "私有部署API地址"}
        },
        "required": ["appkey", "sign", "worksheet_id"]
    }
}
```

### `pbbi_mingdao_save_snapshot` - 保存到快照
```python
{
    "name": "pbbi_mingdao_save_snapshot",
    "description": "将明道云数据保存为本地快照，便于后续分析",
    "parameters": {
        "type": "object",
        "properties": {
            "appkey": {"type": "string", "description": "明道云应用Key"},
            "sign": {"type": "string", "description": "明道云签名"},
            "worksheet_id": {"type": "string", "description": "工作表ID"},
            "snapshot_name": {"type": "string", "description": "快照名称"},
            "is_private": {"type": "boolean", "description": "是否私有部署"},
            "private_api_url": {"type": "string", "description": "私有部署API地址"}
        },
        "required": ["appkey", "sign", "worksheet_id", "snapshot_name"]
    }
}
```

---

## 四、LocalFile MCP (本地文件上传)

### `pbbi_local_upload_file` - 上传本地文件
```python
{
    "name": "pbbi_local_upload_file",
    "description": "上传本地文件（CSV/Excel）并创建数据快照",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "文件路径"},
            "file_type": {"type": "string", "description": "文件类型: csv, xlsx, xls"},
            "snapshot_name": {"type": "string", "description": "快照名称"},
            "sheet_name": {"type": "string", "description": "Excel工作表名"},
            "delimiter": {"type": "string", "description": "CSV分隔符，默认逗号"},
            "encoding": {"type": "string", "description": "文件编码，默认utf-8"}
        },
        "required": ["file_path", "file_type", "snapshot_name"]
    }
}
```

### `pbbi_local_parse_file` - 解析文件预览
```python
{
    "name": "pbbi_local_parse_file",
    "description": "解析本地文件并预览数据结构，不保存快照",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "文件路径"},
            "file_type": {"type": "string", "description": "文件类型: csv, xlsx, xls"},
            "preview_rows": {"type": "integer", "description": "预览行数，默认5"}
        },
        "required": ["file_path", "file_type"]
    }
}
```

### `pbbi_local_create_dataflow` - 创建本地数据流
```python
{
    "name": "pbbi_local_create_dataflow",
    "description": "创建本地类型的数据流配置",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "数据流名称"},
            "description": {"type": "string", "description": "数据流描述"}
        },
        "required": ["name"]
    }
}
```

---

## 五、DataFlow MCP (数据流配置管理)

### `pbbi_list_dataflows` - 列出数据流配置
```python
{
    "name": "pbbi_list_dataflows",
    "description": "列出所有数据流配置信息",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

### `pbbi_get_dataflow` - 获取数据流详情
```python
{
    "name": "pbbi_get_dataflow",
    "description": "获取数据流的详细配置信息",
    "parameters": {
        "type": "object",
        "properties": {
            "dataflow_id": {"type": "integer", "description": "数据流ID"}
        },
        "required": ["dataflow_id"]
    }
}
```

### `pbbi_delete_dataflow` - 删除数据流
```python
{
    "name": "pbbi_delete_dataflow",
    "description": "删除指定的数据流配置",
    "parameters": {
        "type": "object",
        "properties": {
            "dataflow_id": {"type": "integer", "description": "数据流ID"}
        },
        "required": ["dataflow_id"]
    }
}
```

---

## 六、Snapshot MCP (数据快照管理)

### `pbbi_create_snapshot` - 创建快照
```python
{
    "name": "pbbi_create_snapshot",
    "description": "从数据流创建数据快照",
    "parameters": {
        "type": "object",
        "properties": {
            "dataflow_id": {"type": "integer", "description": "数据流ID"},
            "name": {"type": "string", "description": "快照名称"}
        },
        "required": ["dataflow_id", "name"]
    }
}
```

### `pbbi_delete_snapshot` - 删除快照
```python
{
    "name": "pbbi_delete_snapshot",
    "description": "删除指定的数据快照",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"}
        },
        "required": ["snapshot_id"]
    }
}
```

### `pbbi_get_snapshot_detail` - 获取快照详情
```python
{
    "name": "pbbi_get_snapshot_detail",
    "description": "获取数据快照的完整数据",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"}
        },
        "required": ["snapshot_id"]
    }
}
```

---

## 七、Analysis MCP (数据分析功能)

### `pbbi_aggregate_data` - 数据聚合
```python
{
    "name": "pbbi_aggregate_data",
    "description": "对多个数据快照进行聚合操作（UNION/JOIN）",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_ids": {"type": "array", "items": {"type": "integer"}, "description": "快照ID列表"},
            "operation": {"type": "string", "description": "聚合操作: union_all, union, join, left_join, right_join, full_join"},
            "join_keys": {"type": "array", "items": {"type": "string"}, "description": "JOIN键字段"},
            "result_name": {"type": "string", "description": "结果快照名称"}
        },
        "required": ["snapshot_ids", "operation", "result_name"]
    }
}
```

### `pbbi_filter_data` - 数据筛选
```python
{
    "name": "pbbi_filter_data",
    "description": "根据条件筛选数据快照中的数据",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "operator": {"type": "string", "description": "eq, ne, gt, lt, gte, lte, contains, starts_with, ends_with"},
                        "value": {"type": "string"}
                    }
                },
                "description": "筛选条件列表"
            },
            "result_name": {"type": "string", "description": "结果快照名称"}
        },
        "required": ["snapshot_id", "filters", "result_name"]
    }
}
```

### `pbbi_statistics` - 数据统计
```python
{
    "name": "pbbi_statistics",
    "description": "对数据进行统计分析（计数、求和、平均、最大、最小）",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "group_by": {"type": "string", "description": "分组字段"},
            "agg_field": {"type": "string", "description": "聚合字段"},
            "agg_func": {"type": "string", "description": "聚合函数: count, sum, avg, min, max"},
            "result_name": {"type": "string", "description": "结果快照名称"}
        },
        "required": ["snapshot_id", "agg_func", "result_name"]
    }
}
```

### `pbbi_statistical_analysis` - 统计描述分析
```python
{
    "name": "pbbi_statistical_analysis",
    "description": "对数据进行统计描述分析（均值、方差、偏度、峰度等）",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "fields": {"type": "array", "items": {"type": "string"}, "description": "要分析的字段列表"}
        },
        "required": ["snapshot_id", "fields"]
    }
}
```

### `pbbi_regression_analysis` - 回归分析
```python
{
    "name": "pbbi_regression_analysis",
    "description": "对数据进行回归分析（线性、岭、Lasso、多项式）",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "x_fields": {"type": "array", "items": {"type": "string"}, "description": "自变量字段"},
            "y_field": {"type": "string", "description": "因变量字段"},
            "method": {"type": "string", "description": "回归方法: linear, ridge, lasso, polynomial"}
        },
        "required": ["snapshot_id", "x_fields", "y_field"]
    }
}
```

### `pbbi_correlation_analysis` - 相关性分析
```python
{
    "name": "pbbi_correlation_analysis",
    "description": "计算字段之间的相关系数矩阵",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "fields": {"type": "array", "items": {"type": "string"}, "description": "要分析的字段列表"},
            "method": {"type": "string", "description": "相关系数类型: pearson, spearman, kendall"}
        },
        "required": ["snapshot_id", "fields"]
    }
}
```

### `pbbi_distribution_fit` - 分布拟合分析
```python
{
    "name": "pbbi_distribution_fit",
    "description": "对数据进行概率分布拟合（正态、指数、伽马等）",
    "parameters": {
        "type": "object",
        "properties": {
            "snapshot_id": {"type": "integer", "description": "快照ID"},
            "field": {"type": "string", "description": "要分析的字段"},
            "distributions": {"type": "array", "items": {"type": "string"}, "description": "分布类型: norm, expon, gamma, lognorm, beta"}
        },
        "required": ["snapshot_id", "field"]
    }
}
```

### `pbbi_montecarlo_simulation` - 蒙特卡洛模拟
```python
{
    "name": "pbbi_montecarlo_simulation",
    "description": "执行蒙特卡洛模拟分析",
    "parameters": {
        "type": "object",
        "properties": {
            "simulation_type": {"type": "string", "description": "模拟类型: pi, integral, queue, custom"},
            "params": {"type": "object", "description": "模拟参数"},
            "iterations": {"type": "integer", "description": "迭代次数，默认10000"}
        },
        "required": ["simulation_type"]
    }
}
```

---

## 八、Dashboard MCP (看板管理功能)

### `pbbi_list_dashboards` - 列出看板列表
```python
{
    "name": "pbbi_list_dashboards",
    "description": "列出所有数据看板",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

### `pbbi_get_dashboard` - 获取看板详情
```python
{
    "name": "pbbi_get_dashboard",
    "description": "获取看板的详细配置信息",
    "parameters": {
        "type": "object",
        "properties": {
            "dashboard_id": {"type": "integer", "description": "看板ID"}
        },
        "required": ["dashboard_id"]
    }
}
```

### `pbbi_create_dashboard` - 创建看板
```python
{
    "name": "pbbi_create_dashboard",
    "description": "创建新的数据看板",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "看板名称"},
            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
            "chart_type": {"type": "string", "description": "图表类型: line, bar, pie, scatter, radar, funnel, gauge, heatmap, line3d, scatter3d, surface3d, stack_line, stack_bar, multi_yaxis,联动图, led_wafer"},
            "config": {"type": "object", "description": "图表配置"}
        },
        "required": ["name", "snapshot_id", "chart_type"]
    }
}
```

### `pbbi_update_dashboard` - 更新看板
```python
{
    "name": "pbbi_update_dashboard",
    "description": "更新看板配置",
    "parameters": {
        "type": "object",
        "properties": {
            "dashboard_id": {"type": "integer", "description": "看板ID"},
            "name": {"type": "string", "description": "看板名称"},
            "chart_type": {"type": "string", "description": "图表类型"},
            "config": {"type": "object", "description": "图表配置"}
        },
        "required": ["dashboard_id"]
    }
}
```

### `pbbi_delete_dashboard` - 删除看板
```python
{
    "name": "pbbi_delete_dashboard",
    "description": "删除指定的数据看板",
    "parameters": {
        "type": "object",
        "properties": {
            "dashboard_id": {"type": "integer", "description": "看板ID"}
        },
        "required": ["dashboard_id"]
    }
}
```

---

## 九、User MCP (用户信息管理)

### `pbbi_get_current_user` - 获取当前用户
```python
{
    "name": "pbbi_get_current_user",
    "description": "获取当前登录用户的信息",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

### `pbbi_get_user_resources` - 获取用户资源统计
```python
{
    "name": "pbbi_get_user_resources",
    "description": "获取当前用户的资源统计（数据流、快照、看板数量）",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

---

## 十、Agent使用流程示例

### 10.1 查看数据概览
```
用户: "我有哪些数据？"
    │
    ▼
Agent: 调用 pbbi_list_snapshots
    │
    ▼
返回: "您有4个数据快照：晶圆测试数据、贴合生产数据、成绩..."
```

### 10.2 数据分析
```
用户: "分析晶圆测试数据的分布情况"
    │
    ▼
Agent: 调用 pbbi_get_snapshot_schema (了解字段)
    │
    ▼
Agent: 调用 pbbi_statistical_analysis (统计分析)
    │
    ▼
Agent: 调用 pbbi_distribution_fit (分布拟合)
    │
    ▼
返回: 分析报告
```

### 10.3 创建可视化
```
用户: "为晶圆测试数据创建一个柱状图"
    │
    ▼
Agent: 调用 pbbi_list_snapshots (找到快照ID)
    │
    ▼
Agent: 调用 pbbi_create_dashboard (创建看板)
    │
    ▼
返回: "已创建看板，可以在可视化页面查看"
```

### 10.4 从明道云获取数据
```
用户: "从明道云获取设备数据"
    │
    ▼
Agent: 询问 appkey, sign, worksheet_id
    │
    ▼
用户: 提供参数
    │
    ▼
Agent: 调用 pbbi_mingdao_connect (测试连接)
    │
    ▼
Agent: 调用 pbbi_mingdao_save_snapshot (保存快照)
    │
    ▼
返回: "已获取数据并保存为快照"
```

---

## 十一、实施计划

### Phase 1: Database MCP (0.5天)
- [ ] 实现 pbbi_list_snapshots
- [ ] 实现 pbbi_get_snapshot_schema
- [ ] 实现 pbbi_query_snapshot
- [ ] 实现 pbbi_execute_sql

### Phase 2: MingDao MCP (0.5天)
- [ ] 实现 pbbi_mingdao_connect
- [ ] 实现 pbbi_mingdao_get_fields
- [ ] 实现 pbbi_mingdao_get_rows
- [ ] 实现 pbbi_mingdao_save_snapshot

### Phase 3: LocalFile MCP (0.5天)
- [ ] 实现 pbbi_local_upload_file
- [ ] 实现 pbbi_local_parse_file
- [ ] 实现 pbbi_local_create_dataflow

### Phase 4: DataFlow & Snapshot MCP (0.5天)
- [ ] 实现 pbbi_list_dataflows
- [ ] 实现 pbbi_get_dataflow
- [ ] 实现 pbbi_delete_dataflow
- [ ] 实现 pbbi_create_snapshot
- [ ] 实现 pbbi_delete_snapshot
- [ ] 实现 pbbi_get_snapshot_detail

### Phase 5: Analysis MCP (1天)
- [ ] 实现 pbbi_aggregate_data
- [ ] 实现 pbbi_filter_data
- [ ] 实现 pbbi_statistics
- [ ] 实现 pbbi_statistical_analysis
- [ ] 实现 pbbi_regression_analysis
- [ ] 实现 pbbi_correlation_analysis
- [ ] 实现 pbbi_distribution_fit
- [ ] 实现 pbbi_montecarlo_simulation

### Phase 6: Dashboard & User MCP (0.5天)
- [ ] 实现 pbbi_list_dashboards
- [ ] 实现 pbbi_get_dashboard
- [ ] 实现 pbbi_create_dashboard
- [ ] 实现 pbbi_update_dashboard
- [ ] 实现 pbbi_delete_dashboard
- [ ] 实现 pbbi_get_current_user
- [ ] 实现 pbbi_get_user_resources

### Phase 7: Agent集成 (1天)
- [ ] 更新Agent使用新工具
- [ ] 实现参数询问流程
- [ ] 测试验证

**总计: 4.5天**

---

**创建日期**: 2026-03-05
**版本**: 3.2
