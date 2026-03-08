# PB-BI MCP 使用指南

## 一、架构概述

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   前端 React    │────▶│  JoyAgent API   │────▶│   PB-BI 后端    │
│  (localhost:3000)│     │ (localhost:8080)│     │ (localhost:8001)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
  用户交互界面            MCP协议转换             业务逻辑处理
```

## 二、服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| PB-BI 前端 | http://localhost:3000 | React前端界面 |
| JoyAgent API | http://localhost:8080 | AI Agent服务 |
| PB-BI 后端 | http://localhost:8001 | FastAPI后端服务 |

## 三、MCP工具调用示例

### 1. 列出可用工具

```bash
curl -X POST http://localhost:8080/v1/tool/list \
  -H "Content-Type: application/json" \
  -d '{"server_url":"http://localhost:8001/mcp"}'
```

### 2. 调用数据查询工具

```bash
curl -X POST http://localhost:8080/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8001/mcp",
    "tool_name": "pbbi_list_snapshots",
    "arguments": {}
  }'
```

### 3. 调用图表生成工具

```bash
curl -X POST http://localhost:8080/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8001/mcp",
    "tool_name": "pbbi_generate_bar_chart",
    "arguments": {
      "snapshot_id": 1,
      "x_field": "category",
      "y_field": "value"
    }
  }'
```

### 4. 调用数据分析工具

```bash
curl -X POST http://localhost:8080/v1/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_url": "http://localhost:8001/mcp",
    "tool_name": "pbbi_query_snapshot",
    "arguments": {
      "snapshot_id": 1,
      "limit": 10
    }
  }'
```

## 四、PowerShell测试命令

```powershell
# 获取MCP工具列表
Invoke-WebRequest -Uri "http://localhost:8001/api/mcp/tools" -UseBasicParsing

# 通过JoyAgent调用MCP
Invoke-WebRequest -Uri "http://localhost:8080/v1/tool/list" -Method POST -ContentType "application/json" -Body '{"server_url":"http://localhost:8001/mcp"}' -UseBasicParsing
```

## 五、JoyAgent配置示例

```yaml
# JoyAgent配置文件
mcp_client_url: "http://localhost:8001"  # PB-BI MCP客户端地址
mcp_server_url: "http://localhost:8001/mcp"  # PB-BI MCP服务端地址
```

## 六、注意事项

1. 确保PB-BI后端服务在8001端口运行
2. JoyAgent服务默认在8080端口
3. 前端服务默认在3000端口
4. 所有服务需要在同一网络环境下运行
