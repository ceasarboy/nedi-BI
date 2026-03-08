# AI调试技能清单

## 目录
1. [分层调试法](#1-分层调试法)
2. [日志驱动调试](#2-日志驱动调试)
3. [模型适配技巧](#3-模型适配技巧)
4. [错误恢复机制](#4-错误恢复机制)
5. [前端联调技巧](#5-前端联调技巧)
6. [常见问题速查](#6-常见问题速查)
7. [最佳实践](#7-最佳实践)

---

## 1. 分层调试法

### 1.1 调试层次结构
```
前端界面 → API网关 → AI Agent → LLM客户端 → 外部API
```

### 1.2 各层调试方法

#### 第一层：API直接测试
**目的**: 验证MCP工具是否正常工作
**方法**:
```python
import requests

session = requests.Session()
# 登录
session.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})

# 直接调用MCP工具
response = session.post(
    f"{BASE_URL}/api/mcp/execute",
    json={
        "tool_name": "pbbi_generate_line_chart",
        "params": {
            "snapshot_id": 7,
            "x_field": "交易日",
            "y_field": "收盘价",
            "title": "测试图表"
        }
    }
)
result = response.json()
print(f"结果: {result}")
```

**关键检查点**:
- [ ] 工具是否执行成功
- [ ] 返回数据格式是否正确
- [ ] 图表URL是否可访问

#### 第二层：AI对话测试
**目的**: 验证AI Agent是否能正确调用工具
**方法**:
```python
# 测试AI对话流程
response = session.post(
    f"{BASE_URL}/api/ai/chat",
    json={"message": "生成ID为7的快照折线图"},
    stream=True
)

for line in response.iter_lines():
    if line:
        decoded = line.decode('utf-8')
        if decoded.startswith('data: '):
            data = decoded[6:]
            if data != '[DONE]':
                event = json.loads(data)
                print(f"事件类型: {event.get('type')}, 内容: {event}")
```

**关键检查点**:
- [ ] AI是否识别意图
- [ ] 是否正确生成工具调用
- [ ] 流式响应是否完整

#### 第三层：前端集成测试
**目的**: 验证前端是否能正确显示结果
**方法**:
1. 打开浏览器开发者工具
2. 检查Network标签页的SSE请求
3. 查看Console是否有JavaScript错误
4. 验证DOM是否正确更新

---

## 2. 日志驱动调试

### 2.1 日志级别设置
```python
# 在关键位置添加DEBUG日志
print(f"[DEBUG] 进入函数: {function_name}")
print(f"[DEBUG] 参数: {args}")
print(f"[DEBUG] 中间结果: {intermediate_result}")
print(f"[DEBUG] 离开函数: {function_name}, 结果: {result}")
```

### 2.2 关键日志点

#### AI Agent层
```python
# agent.py
print(f"[DEBUG] 用户输入: {user_input}")
print(f"[DEBUG] 识别意图: {user_intent}")
print(f"[DEBUG] 计划工具: {tool_names}")
print(f"[DEBUG] 工具参数: {arguments}")
print(f"[DEBUG] 执行结果: {result}")
```

#### 工具执行层
```python
# tools.py
print(f"[DEBUG] 执行工具: {tool_name}")
print(f"[DEBUG] 参数: {arguments}")
print(f"[DEBUG] 字段验证: {validation_result}")
print(f"[DEBUG] 执行结果: {result}")
```

#### 工具解析层
```python
# tool_parser.py
print(f"[DEBUG] 检测到的解析器: {parser.__class__.__name__}")
print(f"[DEBUG] 解析结果: {len(tool_calls)} 个工具调用")
```

### 2.3 日志分析技巧
1. **按时间排序**: 确保日志按时间顺序查看
2. **过滤关键字**: 使用 `grep "[DEBUG]"` 过滤关键日志
3. **对比正常/异常**: 对比成功和失败请求的日志差异

---

## 3. 模型适配技巧

### 3.1 多模型支持架构
```python
class ToolCallParserRegistry:
    def __init__(self):
        self.parsers = [
            KimiToolCallParser(),      # Kimi特殊格式
            OpenAIToolCallParser(),     # OpenAI标准格式
            DeepSeekDSMLParser(),       # DeepSeek格式
            GLM5PythonCallParser(),     # GLM-5 Python格式
            # ... 其他解析器
        ]
```

### 3.2 添加新模型支持步骤

1. **分析模型输出格式**
   ```python
   # 记录原始输出
   print(f"[DEBUG] 原始输出: {repr(content)}")
   ```

2. **实现解析器类**
   ```python
   class NewModelParser(ToolCallParser):
       def detect(self, content: str) -> bool:
           return "特殊标记" in content
       
       def parse(self, content: str) -> List[ToolCall]:
           # 实现解析逻辑
           pass
   ```

3. **注册到解析器列表**
   ```python
   self.parsers = [
       NewModelParser(),  # 放在前面优先检测
       # ... 其他解析器
   ]
   ```

4. **测试验证**
   ```python
   # 测试新解析器
   parser = NewModelParser()
   assert parser.detect(test_content) == True
   tool_calls = parser.parse(test_content)
   assert len(tool_calls) > 0
   ```

### 3.3 常见模型格式对比

| 模型 | 格式示例 | 特点 |
|------|---------|------|
| Kimi | `<\|tool_call_begin\|>functions.tool_name:id<\|...\|>` | 特殊分隔符 |
| DeepSeek | `<｜tool▁calls▁begin｜>function<｜tool▁sep｜>tool_name` | Unicode分隔符 |
| GLM-5 | `tool_name(param1=value1, param2=value2)` | Python风格 |
| OpenAI | 标准JSON格式 | API原生支持 |

---

## 4. 错误恢复机制

### 4.1 字段验证错误恢复

#### 问题场景
AI生成错误的字段名（如"日期"而不是"交易日"）

#### 解决方案
```python
async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    # 1. 验证字段
    validation_result = await self._validate_chart_tool(tool_name, arguments)
    
    if not validation_result.get("valid"):
        # 2. 返回错误和可用字段
        return {
            "success": False,
            "error": validation_result.get("error"),
            "needs_retry": True,  # 标记需要重试
            "available_fields": validation_result.get("available_fields", [])
        }
    
    # 3. 执行工具
    result = await self._execute_tool(tool_name, arguments)
    return result
```

#### 重试流程
```python
if result.get("needs_retry"):
    # 1. 构建错误反馈
    error_feedback = f"""
    工具调用失败，需要修正参数：
    **错误信息**: {result.get('error')}
    **可用字段**: {', '.join(result.get('available_fields', []))}
    请使用正确的字段名重新生成工具调用。
    """
    
    # 2. 发送给AI重试
    retry_messages = messages.copy()
    retry_messages.append({"role": "user", "content": error_feedback})
    
    async for chunk in self.llm_client.chat(retry_messages, stream=True):
        # 3. 执行修正后的工具调用
        ...
```

### 4.2 递归深度控制

#### 问题场景
AI反复调用工具，导致无限循环

#### 解决方案
```python
async def _continue_conversation(self, messages: List[Dict], depth: int = 0):
    # 限制递归深度
    if depth > 3:
        yield {
            "type": "thinking",
            "stage": "max_depth_reached",
            "message": "已达到最大对话深度，结束对话"
        }
        return
    
    # 处理逻辑...
    
    # 递归调用时增加深度
    async for chunk in self._continue_conversation(messages, depth + 1):
        yield chunk
```

---

## 5. 前端联调技巧

### 5.1 SSE流式响应调试

#### 检查事件流
```javascript
// 在前端添加调试代码
eventSource.onmessage = (event) => {
  console.log('收到事件:', event.data);
  const data = JSON.parse(event.data);
  console.log('事件类型:', data.type, '内容:', data);
};
```

#### 常见问题
1. **事件不触发**: 检查 `Content-Type: text/event-stream`
2. **数据解析错误**: 确保每个事件以 `\n\n` 结尾
3. **连接断开**: 检查超时设置和心跳机制

### 5.2 状态管理调试

#### React状态检查
```javascript
// 添加状态日志
useEffect(() => {
  console.log('当前状态:', {
    loading,
    messages,
    thinkingProcess,
    fullContent
  });
}, [loading, messages, thinkingProcess, fullContent]);
```

### 5.3 图表显示问题

#### 问题：图表URL正确但图片不显示
**解决方案**:
```javascript
// 检查URL格式
const chartUrl = result?.chart_url || result?.data?.chart_url;

// 确保URL完整
if (!chartUrl.startsWith('http')) {
  chartUrl = `${BASE_URL}${chartUrl}`;
}

// 使用Markdown格式
const chartMarkdown = `\n\n![${chartTitle}](${chartUrl})\n`;
```

---

## 6. 常见问题速查

### Q1: AI不调用工具
**可能原因**:
- 系统提示中没有正确描述工具
- 工具描述不清晰
- 模型不支持function calling

**解决方案**:
```python
# 检查工具定义
tools = self.llm_client.get_tools_definition()
print(f"[DEBUG] 可用工具: {json.dumps(tools, ensure_ascii=False)}")

# 更新系统提示
system_prompt += """
## 工具使用说明
当需要查询数据或生成图表时，必须使用工具调用功能。
不要直接在回复中描述工具调用。
"""
```

### Q2: 工具参数错误
**可能原因**:
- 字段名拼写错误
- 参数类型不匹配
- 缺少必需参数

**解决方案**:
```python
# 添加参数验证
if not arguments.get('snapshot_id'):
    return {"success": False, "error": "缺少必需参数: snapshot_id"}

# 类型转换
try:
    snapshot_id = int(arguments.get('snapshot_id'))
except:
    return {"success": False, "error": "snapshot_id必须是整数"}
```

### Q3: 流式响应中断
**可能原因**:
- 网络超时
- 服务器错误
- 前端处理异常

**解决方案**:
```python
# 添加错误处理
try:
    async for chunk in self.llm_client.chat(messages, stream=True):
        yield chunk
except Exception as e:
    yield {"type": "error", "message": str(e)}
    
# 确保发送结束标记
finally:
    yield {"type": "done"}
```

### Q4: 图表生成成功但不显示
**可能原因**:
- URL路径错误
- 前端未正确处理tool_result事件
- 数据格式不匹配

**解决方案**:
```javascript
// 检查事件处理
if (event.type === 'tool_result') {
  const result = event.result;
  // 支持多种数据格式
  const chartUrl = result?.chart_url || result?.data?.chart_url;
  const success = result?.success || result?.data?.success;
  
  if (success && chartUrl) {
    // 显示图表
  }
}
```

---

## 7. 最佳实践

### 7.1 开发流程
1. **API先行**: 先测试MCP工具API
2. **分层验证**: 后端 → AI Agent → 前端
3. **日志全覆盖**: 关键路径添加DEBUG日志
4. **错误处理**: 每个环节都要有错误恢复机制

### 7.2 代码规范
1. **类型注解**: 使用Python类型提示
2. **文档字符串**: 每个函数都要有docstring
3. **错误信息**: 提供清晰的错误信息
4. **常量定义**: 工具名、字段名使用常量

### 7.3 测试策略
1. **单元测试**: 测试每个解析器
2. **集成测试**: 测试完整对话流程
3. **回归测试**: 模型切换后重新测试
4. **性能测试**: 大数据量下的响应时间

### 7.4 部署 checklist
- [ ] 环境变量配置正确
- [ ] 数据库迁移完成
- [ ] 静态资源可访问
- [ ] 日志级别设置为INFO
- [ ] 错误监控启用

---

## 附录：调试工具脚本

### A.1 快速测试脚本
```bash
# 测试API连通性
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 测试MCP工具
curl -X POST http://localhost:8001/api/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"pbbi_list_snapshots","params":{}}'
```

### A.2 日志监控
```bash
# 实时监控后端日志
tail -f backend.log | grep "\[DEBUG\]"

# 过滤错误日志
tail -f backend.log | grep -i "error\|exception"
```

### A.3 性能测试
```python
import time

start = time.time()
# 执行操作
result = execute_operation()
elapsed = time.time() - start
print(f"耗时: {elapsed:.2f}秒")
```

---

**文档版本**: 1.0
**最后更新**: 2026-03-08
**维护者**: AI Assistant
