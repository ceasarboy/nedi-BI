# PB-BI 多种AI接口使用指南

## 一、支持的AI提供商

| 提供商 | API地址 | 特点 |
|--------|---------|------|
| DeepSeek | https://api.deepseek.com | 国产大模型，性价比高 |
| OpenAI | https://api.openai.com | GPT系列模型 |
| 硅基流动 | https://api.siliconflow.cn | 多模型聚合平台 |
| 智谱AI | https://open.bigmodel.cn | GLM系列模型 |

---

## 二、配置方式

### 1. 进入设置页面
导航到 `/settings`，选择"AI设置"标签页

### 2. 选择AI提供商
从下拉列表中选择一个AI提供商

### 3. 配置API密钥
- 输入对应提供商的API Key
- API Key会被加密存储

### 4. 选择模型
- 系统会自动获取该提供商可用的模型列表
- 选择要使用的模型

### 5. 高级参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| Temperature | 生成随机性 | 0.7 |
| Max Tokens | 最大输出长度 | 4096 |

---

## 三、API调用实现

### 1. 后端服务层
```python
# src/ai/agent.py
class AIAgent:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.client = self._init_client(api_key)
        self.model = model
    
    def _init_client(self, api_key: str):
        if self.provider == "deepseek":
            from openai import OpenAI
            return OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        elif self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        # ... 其他提供商
```

### 2. 流式响应实现
```python
async def chat_stream(self, messages: list):
    response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        stream=True,
        temperature=self.temperature,
        max_tokens=self.max_tokens
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

---

## 四、模型价格参考

| 提供商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| DeepSeek | deepseek-chat | ¥1/百万token | ¥2/百万token |
| OpenAI | gpt-4o | $2.5/百万token | $10/百万token |
| 硅基流动 | Qwen/Qwen2.5-72B | ¥0.6/百万token | ¥0.6/百万token |
| 智谱AI | glm-4 | ¥100/百万token | ¥100/百万token |

---

## 五、动态模型获取

### 硅基流动模型列表API
```python
async def get_siliconflow_models(api_key: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.siliconflow.cn/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return response.json()
```

---

## 六、API密钥加密存储

### 加密实现
```python
from cryptography.fernet import Fernet

class APIKeyEncryption:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt(self, api_key: str) -> str:
        return self.fernet.encrypt(api_key.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.fernet.decrypt(encrypted.encode()).decode()
```

---

## 七、常见问题

### 1. API调用失败
**检查项**：
- API Key是否正确
- 网络是否可访问API地址
- 模型名称是否正确
- 余额是否充足

### 2. 流式响应中断
**可能原因**：
- 网络不稳定
- Token超限
- 服务器超时

### 3. 模型列表获取失败
**检查项**：
- API Key是否有权限
- API地址是否正确

---

## 八、相关文件

| 文件 | 说明 |
|------|------|
| `src/api/settings.py` | AI设置API |
| `src/ai/agent.py` | AI Agent实现 |
| `frontend/src/pages/SettingsPage.jsx` | 设置页面 |

---

## 九、经验教训

1. **API Key安全**：必须加密存储，不能明文保存
2. **模型名称**：不同提供商的模型命名规则不同，需要精确匹配
3. **流式响应**：使用SSE实现，注意超时处理
4. **错误处理**：API调用可能失败，要有完善的错误提示
5. **价格透明**：在设置页面显示模型价格，帮助用户决策
