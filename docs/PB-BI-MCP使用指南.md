# PB-BI MCP 工具使用指南

## 概述

本文档说明如何在JoyAgent中配置和使用PB-BI的MCP工具，实现智能数据分析。

## 系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   JoyAgent UI   │────▶│ JoyAgent 后端   │────▶│   PB-BI 后端    │
│  (localhost:3000)│     │ (localhost:8080)│     │ (localhost:8000)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                              ┌──────────────────────────┤
                              │                          │
                        ┌─────▼─────┐            ┌──────▼──────┐
                        │ MCP 工具  │            │  MCP 客户端  │
                        │ (/api/mcp)│            │ (/v1/tool)   │
                        └───────────┘            └──────────────┘
```

## 当前配置

### 服务地址

| 服务 | 地址 |
|------|------|
| JoyAgent 前端 | http://localhost:3000 |
| JoyAgent 后端 | http://localhost:8080 |
| PB-BI 后端 | http://localhost:8000 |

### 可用MCP工具 (7个)

| 工具名称 | 功能 | 参数 |
|----------|------|------|
| `pbbi_get_dataflows` | 获取数据流列表 | page, page_size |
| `pbbi_get_dataflow` | 获取单个数据流详情 | dataflow_id |
| `pbbi_query_data` | 查询数据 | dataflow_id, filters, pagination |
| `pbbi_get_schema` | 获取数据库Schema | table_name(可选) |
| `pbbi_get_snapshots` | 获取快照列表 | dataflow_id |
| `pbbi_get_snapshot_data` | 获取快照数据 | snapshot_id |
| `pbbi_get_dashboards` | 获取看板列表 | - |

## 使用方法

### 方法1：通过JoyAgent前端

1. 打开浏览器访问：**http://localhost:3000**
2. 在输入框中输入自然语言查询，例如：
   - "列出所有数据流"
   - "查询销售数据"
   - "获取数据库表结构"
   - "显示所有看板"
3. 发送问题

### 方法2：直接调用MCP API

#### 获取工具列表

```bash
curl -X POST http://localhost:8000/v1/tool/list \
  -H "Content-Type: application/json" \
  -d '{"server_url":"http://localhost:8000/mcp"}'
```

#### 执行工具

```bash
# 获取数据流列表
curl -X POST http://localhost:8000/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8000/mcp",
    "name": "pbbi_get_dataflows",
    "arguments": {"page": 1, "page_size": 10}
  }'

# 获取数据流详情
curl -X POST http://localhost:8000/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8000/mcp",
    "name": "pbbi_get_dataflow",
    "arguments": {"dataflow_id": "sales_data"}
  }'

# 查询数据
curl -X POST http://localhost:8000/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8000/mcp",
    "name": "pbbi_query_data",
    "arguments": {
      "dataflow_id": "sales_data",
      "filters": {},
      "pagination": {"page": 1, "page_size": 100}
    }
  }'

# 获取数据库Schema
curl -X POST http://localhost:8000/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8000/mcp",
    "name": "pbbi_get_schema",
    "arguments": {}
  }'

# 获取看板列表
curl -X POST http://localhost:8000/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8000/mcp",
    "name": "pbbi_get_dashboards",
    "arguments": {}
  }'
```

## 故障排除

### 问题1：JoyAgent无法调用MCP工具

**症状**：在JoyAgent中提问后，提示无法调用MCP工具

**排查步骤**：

1. 验证PB-BI服务是否运行：
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/api/mcp/tools" -UseBasicParsing
   ```

2. 验证MCP客户端接口：
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/v1/tool/list" -Method POST -ContentType "application/json" -Body '{"server_url":"http://localhost:8000/mcp"}' -UseBasicParsing
   ```

3. 检查JoyAgent后端日志，查找MCP相关错误

### 问题2：工具返回空结果

**可能原因**：
- 数据库中没有数据
- 数据流ID不正确
- 权限问题

**解决方案**：
1. 先使用 `pbbi_get_dataflows` 获取可用的数据流
2. 使用正确的 `dataflow_id` 进行查询

### 问题3：服务未启动

**需要启动的服务**：

1. PB-BI后端：
   ```powershell
   cd f:\PB-BI
   venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

2. JoyAgent后端：
   ```powershell
   cd f:\PB-BI\joyagent-jdgenie-data_agent\genie-backend
   powershell -ExecutionPolicy Bypass -File start_backend.ps1
   ```

3. JoyAgent前端：
   ```powershell
   cd f:\PB-BI\joyagent-jdgenie-data_agent\ui
   npm run dev
   ```

## 配置说明

### JoyAgent MCP配置

配置文件位置：`f:\PB-BI\joyagent-jdgenie-data_agent\genie-backend\src\main\resources\application.yml`

关键配置项：
```yaml
mcp_client_url: "http://localhost:8000"  # PB-BI MCP客户端地址
mcp_server_url: "http://localhost:8000/mcp"  # PB-BI MCP服务端地址
```

### 修改LLM配置

如需更换LLM API，修改以下配置：

```yaml
llm:
  default:
    base_url: 'https://api.siliconflow.cn'  # LLM API地址
    apikey: 'your-api-key'  # 您的API密钥
    model: 'deepseek-ai/DeepSeek-V3'  # 使用的模型
```

## 示例对话

### 示例1：列出数据流

**用户输入**：
> 列出所有数据流

**期望行为**：
1. JoyAgent调用 `pbbi_get_dataflows` 工具
2. 返回数据流列表
3. 显示给用户

### 示例2：查询数据

**用户输入**：
> 查询销售数据

**期望行为**：
1. JoyAgent调用 `pbbi_get_dataflow` 获取数据流信息
2. 调用 `pbbi_query_data` 查询数据
3. 返回查询结果

### 示例3：获取数据库结构

**用户输入**：
> 数据库有哪些表？

**期望行为**：
1. JoyAgent调用 `pbbi_get_schema` 工具
2. 返回数据库表结构
3. 显示给用户

---

**创建日期**: 2026-03-04
**版本**: 1.0
