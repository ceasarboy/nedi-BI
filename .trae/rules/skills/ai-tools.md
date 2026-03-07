# PB-BI AI工具调用与交互指南

## 一、AI Agent架构

### 1. 核心组件
```
src/ai/
├── agent.py           # AI Agent主类
├── tools.py           # 工具定义
├── prompts.py         # 提示词模板
└── memory_service.py  # 记忆系统服务
```

### 2. Agent初始化
```python
class AIAgent:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.client = self._init_client(api_key)
        self.model = model
        self.temperature = 0.7
        self.max_tokens = 4096
        self._memory_service = None  # 延迟加载
    
    @property
    def memory_service(self):
        if self._memory_service is None:
            self._memory_service = MemoryService()
        return self._memory_service
```

---

## 二、工具调用流程

### 1. 工具定义格式
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_data",
            "description": "查询数据快照中的数据",
            "parameters": {
                "type": "object",
                "properties": {
                    "snapshot_id": {
                        "type": "integer",
                        "description": "数据快照ID"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要查询的字段列表"
                    }
                },
                "required": ["snapshot_id"]
            }
        }
    }
]
```

### 2. 工具调用处理
```python
async def handle_tool_call(self, tool_name: str, arguments: dict):
    if tool_name == "query_data":
        return await self._query_data(arguments)
    elif tool_name == "generate_chart":
        return await self._generate_chart(arguments)
    # ... 其他工具
```

### 3. 流式响应实现
```python
async def chat_stream(self, messages: list, tools: list = None):
    response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        tools=tools,
        stream=True,
        temperature=self.temperature,
        max_tokens=self.max_tokens
    )
    
    for chunk in response:
        # 发送思考过程事件
        if chunk.choices[0].delta.tool_calls:
            yield {
                "type": "tool_call",
                "tool_name": chunk.choices[0].delta.tool_calls[0].function.name,
                "arguments": chunk.choices[0].delta.tool_calls[0].function.arguments
            }
        elif chunk.choices[0].delta.content:
            yield {
                "type": "content",
                "content": chunk.choices[0].delta.content
            }
```

---

## 三、三层记忆系统

### 1. 记忆层级设计
| 层级 | 类型 | 优先级 | 说明 |
|------|------|--------|------|
| 第一层 | 用户偏好 | 最高 | 存储用户个性化偏好 |
| 第二层 | 成功案例 | 中等 | 存储成功的AI回复案例 |
| 第三层 | 失败教训 | 最低 | 存储失败的AI回复案例 |

### 2. 记忆数据模型
```python
class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    preference_key = Column(String(100), unique=True)
    preference_value = Column(Text)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class SuccessCase(Base):
    __tablename__ = "success_cases"
    
    id = Column(Integer, primary_key=True)
    user_query = Column(Text)
    ai_response = Column(Text)
    keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FailureLesson(Base):
    __tablename__ = "failure_lessons"
    
    id = Column(Integer, primary_key=True)
    user_query = Column(Text)
    wrong_response = Column(Text)
    correct_response = Column(Text)
    lesson = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 3. 记忆注入到系统提示词
```python
def build_system_prompt(self, user_query: str) -> str:
    base_prompt = "你是PB-BI数据分析平台的AI助手..."
    
    # 注入用户偏好
    preferences = self.memory_service.get_relevant_preferences(user_query)
    if preferences:
        base_prompt += "\n\n用户偏好：\n"
        for p in preferences:
            base_prompt += f"- {p.preference_key}: {p.preference_value}\n"
    
    # 注入成功案例
    cases = self.memory_service.get_relevant_success_cases(user_query)
    if cases:
        base_prompt += "\n\n参考案例：\n"
        for case in cases[:3]:  # 最多3个案例
            base_prompt += f"- 问题: {case.user_query}\n"
            base_prompt += f"  回答: {case.ai_response[:200]}...\n"
    
    # 注入失败教训
    lessons = self.memory_service.get_relevant_failure_lessons(user_query)
    if lessons:
        base_prompt += "\n\n避免以下错误：\n"
        for lesson in lessons[:2]:  # 最多2个教训
            base_prompt += f"- {lesson.lesson}\n"
    
    return base_prompt
```

### 4. 反馈自动提取记忆
```python
def process_feedback(self, feedback: Feedback):
    if feedback.rating > 0:
        # 点赞：创建成功案例 + 提取偏好
        self.memory_service.save_success_case(
            user_query=feedback.conversation.messages[-2].content,
            ai_response=feedback.conversation.messages[-1].content,
            keywords=extract_keywords(feedback.conversation.messages[-2].content)
        )
        self.memory_service.extract_preferences_from_positive_feedback(feedback)
    
    elif feedback.rating < 0 and feedback.user_correction:
        # 点踩且有修正：创建失败教训
        self.memory_service.save_failure_lesson(
            user_query=feedback.conversation.messages[-2].content,
            wrong_response=feedback.conversation.messages[-1].content,
            correct_response=feedback.user_correction,
            lesson=generate_lesson(feedback)
        )
```

---

## 四、意图分类

### 1. 意图类型
| 意图 | 说明 | 关键词 |
|------|------|--------|
| data_query | 数据查询 | 查看、显示、查询、列出 |
| schema_query | 结构查询 | 有哪些字段、字段列表 |
| analysis | 数据分析 | 分析、统计、计算 |
| visualization | 可视化 | 图表、画图、折线图、柱状图 |
| comparison | 对比分析 | 对比、比较、差异 |
| trend | 趋势分析 | 趋势、变化、增长 |

### 2. 分类优先级
```python
INTENT_PRIORITY = [
    ("schema_query", ["有哪些字段", "字段列表", "字段信息"]),  # 最高优先级
    ("visualization", ["图表", "画图", "折线图", "柱状图", "饼图"]),
    ("analysis", ["分析", "统计", "计算"]),
    ("comparison", ["对比", "比较", "差异"]),
    ("trend", ["趋势", "变化", "增长"]),
    ("data_query", ["查看", "显示", "查询", "列出"])  # 最低优先级
]

def classify_intent(query: str) -> str:
    query_lower = query.lower()
    for intent, keywords in INTENT_PRIORITY:
        if any(kw in query_lower for kw in keywords):
            return intent
    return "data_query"
```

---

## 五、思考过程展示

### 1. 事件类型定义
```python
class ThinkingEvent:
    THOUGHT = "thought"       # AI思考内容
    TOOL_CALL = "tool_call"   # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    CONTENT = "content"       # 回复内容
    DONE = "done"            # 完成
```

### 2. 前端展示组件
```jsx
function ThinkingPanel({ events }) {
  return (
    <div className="thinking-panel">
      {events.map((event, index) => (
        <div key={index} className={`thinking-event ${event.type}`}>
          {event.type === 'tool_call' && (
            <div className="tool-call">
              <span className="tool-icon">🔧</span>
              <span>调用工具: {event.tool_name}</span>
            </div>
          )}
          {event.type === 'tool_result' && (
            <div className="tool-result">
              <span className="result-icon">✓</span>
              <span>工具执行完成</span>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

---

## 六、工具调用内容过滤

### 问题：AI返回原始工具调用格式
```
晶圆亮度分布热力图...<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function...
```

### 解决方案
```python
def _is_tool_call_content(self, content: str) -> bool:
    """检测是否为工具调用格式内容"""
    tool_call_patterns = [
        '<｜tool▁calls▁begin｜>',
        '<｜tool▁call▁begin｜>',
        '<｜tool▁sep｜>',
        '<｜DSML｜',
        '<|tool_calls_begin|>',
        '<|tool_call_begin|>'
    ]
    return any(pattern in content for pattern in tool_call_patterns)

async def chat_stream(self, messages: list):
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            # 过滤工具调用格式内容
            if not self._is_tool_call_content(content):
                yield {"type": "content", "content": content}
```

---

## 七、相关文件

| 文件 | 说明 |
|------|------|
| `src/ai/agent.py` | AI Agent主类 |
| `src/ai/tools.py` | 工具定义 |
| `src/ai/prompts.py` | 提示词模板 |
| `src/services/memory_service.py` | 记忆系统服务 |
| `src/api/ai.py` | AI对话API |
| `src/api/feedback.py` | 反馈API |
| `frontend/src/pages/AIPage.jsx` | AI对话页面 |

---

## 八、经验教训

1. **工具调用过滤**：AI模型可能返回原始工具调用格式，需要过滤
2. **记忆注入顺序**：按优先级注入，避免系统提示词过长
3. **意图分类优先级**：更具体的意图应该有更高的优先级
4. **延迟加载模式**：MemoryService使用延迟加载避免不必要的数据库连接
5. **流式响应**：使用SSE实现，注意超时处理
