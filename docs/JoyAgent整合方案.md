# JoyAgent-JDGenie 与 PB-BI 整合方案

## 一、项目概述

### 1.1 JoyAgent-JDGenie 核心能力

| 能力 | 说明 |
|------|------|
| JoyDataAgent | 首个开源的包含数据治理DGP协议、智能问数和智能诊断分析的智能体 |
| 多智能体框架 | 支持react模式、plan and executor模式 |
| MCP工具接入 | 可插拔的工具系统，支持自定义MCP服务 |
| 开箱即用 | 端到端完整产品，无需大量二次开发 |

### 1.2 整合价值

```
当前PB-BI能力          +      JoyAgent能力          =   整合后能力
--------------------------------------------------------------------------------
数据源配置                     智能问数                 =   自然语言查询数据
字段类型设置                   SQL生成与执行           =   自动SQL转换
数据快照保存                   智能诊断分析             =   自动数据分析
图表可视化                     报告生成                 =   AI驱动的洞察
```

## 二、整合架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         用户界面 (PB-BI Frontend)                       │
│              http://localhost:3000 (现有)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PB-BI Backend (FastAPI)                             │
│                    http://localhost:8001                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 数据流API   │  │ 快照API    │  │ 向量API    │  │ 图表推荐API │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
            │                         │
            │ MCP工具                  │ 数据源
            ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   JoyAgent-JDGenie (DataAgent)                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     MCP Server (PB-BI Tools)                    │  │
│  │  - get_dataflow_list    - 获取数据流列表                         │  │
│  │  - query_data           - 查询数据                              │  │
│  │  - get_snapshot         - 获取快照                              │  │
│  │  - get_schema           - 获取数据库Schema                      │  │
│  │  - analyze_data         - 数据诊断分析                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    LLM (DeepSeek/OpenAI)                       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流说明

1. **自然语言查询**: 用户在PB-BI界面输入自然语言问题
2. **MCP转发**: JoyAgent通过MCP调用PB-BI的工具
3. **数据返回**: PB-BI执行查询，返回结果
4. **智能分析**: JoyAgent分析数据，生成洞察
5. **图表推荐**: 调用PB-BI的图表推荐API
6. **可视化展示**: 在PB-BI界面展示结果

## 三、实施计划

### 3.1 阶段一：基础集成 (1-2天)

| 任务 | 说明 | 预估时间 |
|------|------|----------|
| 1.1 | 部署JoyAgent-JDGenie | 2h |
| 1.2 | 开发PB-BI MCP工具类 | 4h |
| 1.3 | 实现数据流查询工具 | 4h |
| 1.4 | 实现快照获取工具 | 2h |

### 3.2 阶段二：智能问数 (2-3天)

| 任务 | 说明 | 预估时间 |
|------|------|----------|
| 2.1 | 对接PB-BI数据库Schema | 4h |
| 2.2 | 实现SQL生成与转换 | 4h |
| 2.3 | 集成SQL执行结果返回 | 4h |
| 2.4 | 集成图表推荐API | 2h |

### 3.3 阶段三：高级分析 (2-3天)

| 任务 | 说明 | 预估时间 |
|------|------|----------|
| 3.1 | 数据诊断分析工具 | 4h |
| 3.2 | 趋势分析工具 | 4h |
| 3.3 | 异常检测工具 | 4h |
| 3.4 | 报告生成集成 | 2h |

## 四、技术实现

### 4.1 MCP工具定义

```python
# pb_bi_mcp_tools.py

class GetDataFlowsTool(BaseTool):
    """获取数据流列表"""
    def get_name(self):
        return "pbbi_get_dataflows"

    def get_description(self):
        return "获取PB-BI系统中配置的所有数据流"

    def to_params(self):
        return '{"type":"object","properties":{},"required":[]}'


class QueryDataTool(BaseTool):
    """查询数据"""
    def get_name(self):
        return "pbbi_query_data"

    def get_description(self):
        return "执行SQL查询并返回结果"

    def to_params(self):
        return '''{
            "type": "object",
            "properties": {
                "dataflow_id": {"type": "integer", "description": "数据流ID"},
                "sql": {"type": "string", "description": "SQL查询语句"}
            },
            "required": ["dataflow_id"]
        }'''

    def execute(self, input):
        # 实现查询逻辑
        pass


class AnalyzeDataTool(BaseTool):
    """数据分析诊断"""
    def get_name(self):
        return "pbbi_analyze"

    def get_description(self):
        return "对数据进行智能分析，包括趋势、异常、相关性等"

    def to_params(self):
        return '''{
            "type": "object",
            "properties": {
                "data": {"type": "array", "description": "分析数据"},
                "analysis_type": {"type": "string", "description": "分析类型: trend/anomaly/correlation"}
            },
            "required": ["data"]
        }'''
```

### 4.2 配置文件

```yaml
# application.yml (JoyAgent配置)

mcp_server_url: "http://localhost:8001/mcp"
```

### 4.3 API对接

```python
# PB-BI 新增API端点
@router.get("/mcp/tools")
async def get_mcp_tools():
    """返回MCP工具列表"""
    return {
        "tools": [
            {"name": "pbbi_get_dataflows", "description": "获取数据流列表"},
            {"name": "pbbi_query_data", "description": "查询数据"},
            {"name": "pbbi_analyze", "description": "数据分析"}
        ]
    }

@router.post("/mcp/execute")
async def execute_mcp_tool(tool_name: str, params: dict):
    """执行MCP工具"""
    if tool_name == "pbbi_query_data":
        return await query_data(params)
    elif tool_name == "pbbi_analyze":
        return await analyze_data(params)
    # ...
```

## 五、整合后的能力提升

### 5.1 自然语言查询

| 用户输入 | AI理解 | 执行 | 结果 |
|----------|--------|------|------|
| "显示本月销售额趋势" | 转化为SQL | 查询快照 | 折线图 |
| "北京和上海对比" | 分组查询 | 数据聚合 | 柱状图 |
| "有哪些异常数据" | 异常检测 | 智能分析 | 诊断报告 |

### 5.2 智能诊断

- **趋势分析**: 自动识别增长/下降趋势
- **异常检测**: 发现异常数据点
- **相关性分析**: 识别变量间关系
- **预测分析**: 基于历史数据预测

## 六、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 部署复杂性 | 可能遇到环境问题 | 使用Docker一键部署 |
| LLM成本 | API调用费用 | 使用本地DeepSeek模型 |
| 数据安全 | 敏感数据外泄 | 本地部署，数据不外传 |
| 性能问题 | 查询速度慢 | 异步处理，缓存优化 |

## 七、下一步行动

1. **技术评审**: 确认整合方案可行性
2. **环境准备**: 准备部署环境
3. **小规模试点**: 先实现基础MCP工具
4. **迭代优化**: 根据使用反馈持续改进

---

**创建日期**: 2026-02-23
**版本**: 1.0
**状态**: 待审批
