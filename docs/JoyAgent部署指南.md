# JoyAgent-JDGenie 部署指南

## 方式一：Docker 部署（推荐）

### 1. 下载代码

```bash
git clone https://github.com/jd-opensource/joyagent-jdgenie.git
cd joyagent-jdgenie
```

### 2. 配置环境变量

编辑 `genie-backend/src/main/resources/application.yml`：

```yaml
base_url: "https://api.deepseek.com"  # 或其他LLM API
apikey: "your-api-key"
model: "deepseek-chat"
max_tokens: 8192
model_name: "deepseek-chat"
```

编辑 `genie-tool/.env_template`：

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
DEFAULT_MODEL=deepseek/deepseek-chat
```

### 3. 构建Docker镜像

```bash
docker build -t joyagent:latest .
```

### 4. 启动容器

```bash
docker run -d -p 3000:3000 -p 8080:8080 -p 1601:1601 --name joyagent joyagent:latest
```

### 5. 访问

- 前端：http://localhost:3000
- 后端：http://localhost:8080
- 工具服务：http://localhost:1601

---

## 方式二：手动部署

### 环境要求

- JDK 17+
- Python 3.11+
- Node.js 18+

### 1. 下载代码

```bash
git clone https://github.com/jd-opensource/joyagent-jdgenie.git
cd joyagent-jdgenie
```

### 2. 配置后端

```bash
cd genie-backend
# 编辑 application.yml 配置LLM
mvn clean package -DskipTests
```

### 3. 配置前端

```bash
cd ui
npm install
npm run build
```

### 4. 配置工具服务

```bash
cd genie-tool
pip install -r requirements.txt
# 编辑 .env 配置API密钥
```

### 5. 启动服务

```bash
# 后端
java -jar target/genie-backend.jar

# 前端
npm run dev

# 工具服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 1601
```

---

## PB-BI MCP工具接入

部署完成后，需要在JoyAgent中配置MCP工具：

### 1. 配置MCP服务地址

在JoyAgent的配置文件中添加：

```yaml
mcp_server_url: "http://localhost:8000/mcp"
```

### 2. 可用的MCP工具

| 工具名称 | 功能 |
|----------|------|
| pbbi_get_dataflows | 获取数据流列表 |
| pbbi_get_dataflow | 获取数据流详情 |
| pbbi_query_data | 查询数据 |
| pbbi_get_schema | 获取数据库Schema |
| pbbi_get_snapshots | 获取快照列表 |
| pbbi_get_snapshot_data | 获取快照数据 |
| pbbi_get_dashboards | 获取看板列表 |

### 3. 测试MCP工具

```bash
# 获取工具列表
curl http://localhost:8000/api/mcp/tools

# 执行工具
curl -X POST http://localhost:8000/api/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "pbbi_get_dataflows", "params": {}}'
```

---

## 注意事项

1. **LLM API密钥**：需要准备DeepSeek或OpenAI的API密钥
2. **网络访问**：确保服务器可以访问LLM API
3. **端口冲突**：确保3000、8080、1601端口未被占用
4. **数据持久化**：Docker模式下数据不会持久化，重启后会丢失

---

**创建日期**: 2026-02-23
