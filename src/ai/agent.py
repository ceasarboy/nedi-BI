"""
PB-BI AI Agent - 核心Agent类
实现与AI对话、工具调用、数据分析功能
"""

import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

from .llm_client import LLMClient, LLMConfig
from .tools import MCPToolExecutor
from .tool_parser import parse_tool_calls, tool_calls_to_openai_format
from src.services.memory_service import MemoryService

SYSTEM_PROMPT = """你是PB-BI智能数据分析助手，帮助用户查询和分析数据。

## 重要：语言要求
- 你必须始终使用简体中文回复用户
- 无论用户使用什么语言提问，你都必须用中文回答
- 所有分析、解释、图表说明都必须用中文
- 不要使用其他语言（如英语、泰语、日语等）

## 服务器信息
- 后端服务地址: http://localhost:8000
- 图表访问地址: http://localhost:8000/api/charts/

## 你的能力
1. 查询数据流列表和详情
2. 执行数据查询
3. 分析数据并生成报告
4. 推荐合适的图表类型
5. 生成可视化图表（柱状图、饼图、折线图、散点图、箱线图）

## 工具使用指南

### 查询数据的步骤：
1. 首先调用 `pbbi_list_snapshots` 获取所有数据快照
2. 根据用户需求，找到对应的快照ID
3. 调用 `pbbi_get_snapshot_schema` 获取快照字段信息
4. 调用 `pbbi_query_snapshot` 查询实际数据

### 生成图表的步骤：
1. 确定要生成的图表类型
2. 调用对应的图表生成工具：
   - 基础图表：
     - `pbbi_generate_bar_chart` - 柱状图（支持聚合、堆叠、水平显示）
     - `pbbi_generate_pie_chart` - 饼图（支持环形图）
     - `pbbi_generate_line_chart` - 折线图（支持面积图）
     - `pbbi_generate_scatter_chart` - 散点图（支持气泡图）
     - `pbbi_generate_box_plot` - 箱线图（支持分组）
     - `pbbi_generate_histogram` - 直方图（数据分布）
   - 高级图表：
     - `pbbi_generate_heatmap` - 热力图（相关性/密度分布）
     - `pbbi_generate_radar_chart` - 雷达图（多维度评估）
     - `pbbi_generate_funnel_chart` - 漏斗图（转化率分析）
     - `pbbi_generate_gauge_chart` - 仪表盘（KPI指标）
   - 3D图表：
     - `pbbi_generate_bar_3d_chart` - 3D柱状图（三维数据展示）
     - `pbbi_generate_scatter_3d_chart` - 3D散点图（三维关系分析）
     - `pbbi_generate_surface_3d_chart` - 3D曲面图（形貌数据）
     - `pbbi_generate_led_wafer_chart` - LED晶圆分析图（波长颜色映射）
   - 组合图表：
     - `pbbi_generate_combo_chart` - 组合图（柱状图+折线图）
     - `pbbi_generate_multiple_y_axis_chart` - 多Y轴图（多指标对比）
     - `pbbi_generate_stacked_bar_chart` - 堆叠柱状图（构成分析）
     - `pbbi_generate_stacked_line_chart` - 堆叠折线图（趋势构成）
     - `pbbi_generate_linked_chart` - 联动图表（折线图+饼图）
3. 工具返回的chart_url需要拼接完整地址
4. **必须使用markdown图片格式展示图表**: `![图表标题](http://localhost:8000/api/charts/xxx.png)`
5. 不要只显示URL文本，必须用图片格式让用户直接看到图表

### 重要提示：
- 快照ID (snapshot_id) 是整数类型
- 生成图表时需要指定正确的字段名
- 图表生成后必须返回完整的可访问URL给用户

## 回复格式
- 使用清晰的中文回复
- 数据用表格或列表展示
- 分析结论要简洁明了
- 生成图表后，显示完整图表URL让用户查看

## 当前日期
{{current_date}}
"""

@dataclass
class ChatMessage:
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

class PBBIAgent:
    def __init__(self, config: Optional[LLMConfig] = None, session_id: Optional[str] = None, user_id: Optional[int] = None):
        self.llm_client = LLMClient(config)
        self.tool_executor = MCPToolExecutor()
        self.conversation_history: List[Dict[str, str]] = []
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(self)}"
        self.user_id = user_id
        self._memory_service = None
    
    @property
    def memory_service(self):
        """延迟加载MemoryService，避免不必要的数据库连接"""
        if self._memory_service is None:
            self._memory_service = MemoryService()
        return self._memory_service
    
    def set_session_id(self, session_id: str):
        """设置会话ID"""
        self.session_id = session_id
    
    def set_user_id(self, user_id: Optional[int]):
        """设置用户ID"""
        self.user_id = user_id
    
    def load_history(self, messages: List[Dict[str, str]]):
        """加载历史消息"""
        self.conversation_history = messages.copy()
    
    def _get_memory_context(self, query: str) -> Optional[str]:
        """从三层记忆系统获取上下文，按优先级注入"""
        try:
            memory_context = self.memory_service.build_memory_context(
                user_id=self.user_id,
                query=query
            )
            return memory_context if memory_context else None
        except Exception as e:
            print(f"[DEBUG] Memory context error: {e}")
            return None
    
    def _get_system_prompt(self, query: str = "") -> str:
        base_prompt = SYSTEM_PROMPT.replace("{{current_date}}", datetime.now().strftime("%Y-%m-%d"))
        
        memory_context = self._get_memory_context(query)
        if memory_context:
            base_prompt = f"{base_prompt}\n\n## 记忆上下文\n{memory_context}"
        
        return base_prompt
    
    def _build_messages(self, user_input: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self._get_system_prompt(user_input)}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def _parse_text_tool_calls(self, text: str) -> List[Dict]:
        """解析文本格式工具调用 - 使用通用解析器"""
        tool_calls = parse_tool_calls(text)
        return tool_calls_to_openai_format(tool_calls)
    
    def _analyze_user_intent(self, query: str) -> str:
        """分析用户意图"""
        query_lower = query.lower()
        
        if any(kw in query for kw in ["图表", "柱状图", "折线图", "饼图", "直方图", "散点图"]):
            return "图表生成"
        elif any(kw in query for kw in ["分析", "统计", "趋势", "分布"]):
            return "数据分析"
        elif any(kw in query for kw in ["查询", "列出", "显示", "查看", "获取"]):
            return "数据查询"
        elif any(kw in query for kw in ["快照", "数据集", "表结构", "字段"]):
            return "结构查询"
        elif any(kw in query for kw in ["帮助", "怎么", "如何", "什么"]):
            return "帮助咨询"
        else:
            return "一般对话"
    
    def _get_tool_display_name(self, tool_name: str) -> str:
        """获取工具的显示名称"""
        tool_names = {
            "pbbi_list_snapshots": "获取快照列表",
            "pbbi_get_snapshot_schema": "获取快照结构",
            "pbbi_query_snapshot": "查询快照数据",
            "pbbi_generate_bar_chart": "生成柱状图",
            "pbbi_generate_line_chart": "生成折线图",
            "pbbi_generate_pie_chart": "生成饼图",
            "pbbi_generate_histogram": "生成直方图",
            "pbbi_generate_scatter_plot": "生成散点图",
            "pbbi_generate_heatmap": "生成热力图",
            "pbbi_generate_box_plot": "生成箱线图",
            "pbbi_generate_radar_chart": "生成雷达图",
            "pbbi_generate_3d_scatter": "生成3D散点图",
            "pbbi_generate_3d_bar": "生成3D柱状图",
            "pbbi_generate_3d_surface": "生成3D曲面图",
            "pbbi_analyze_distribution": "分析数据分布",
            "pbbi_correlation_analysis": "相关性分析",
            "pbbi_monte_carlo_simulation": "蒙特卡洛模拟",
        }
        return tool_names.get(tool_name, tool_name)
    
    def _get_result_summary(self, result: Dict) -> str:
        """获取结果摘要"""
        if not result:
            return "执行完成"
        
        if result.get("success"):
            if "row_count" in result:
                return f"返回 {result['row_count']} 条数据"
            elif "chart_url" in result:
                return "图表已生成"
            elif "snapshots" in result:
                return f"找到 {len(result['snapshots'])} 个快照"
            elif "fields" in result:
                return f"包含 {len(result['fields'])} 个字段"
            else:
                return "执行成功"
        else:
            return result.get("error", "执行失败")[:50]
    
    def _is_tool_call_content(self, content: str) -> bool:
        """检测内容是否是工具调用格式，需要过滤掉不显示给用户"""
        tool_call_patterns = [
            '<｜tool▁calls▁begin｜>',
            '<｜tool▁call▁begin｜>',
            '<｜tool▁sep｜>',
            '<｜tool▁call▁end｜>',
            '<｜tool▁calls▁end｜>',
            '<｜DSML｜',
            '<|DSML|>',
            '```tool_call',
            '```tool',
            '✿FUNCTION✿',
            '✿CALL✿',
            '<tool_calls>',
            '<invoke_tool>',
        ]
        
        for pattern in tool_call_patterns:
            if pattern in content:
                return True
        
        return False
    
    def close(self):
        """清理资源"""
        if self._memory_service:
            self._memory_service.close()
            self._memory_service = None
    
    async def chat(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        messages = self._build_messages(user_input)
        tools = self.llm_client.get_tools_definition()
        
        yield {
            "type": "thinking_start",
            "message": "正在分析您的问题..."
        }
        
        user_intent = self._analyze_user_intent(user_input)
        yield {
            "type": "thinking",
            "stage": "intent_analysis",
            "message": f"识别意图: {user_intent}"
        }
        
        full_response = ""
        tool_calls_buffer = []
        current_tool_call = None
        
        yield {
            "type": "thinking",
            "stage": "llm_call",
            "message": "正在生成回复..."
        }
        
        async for chunk in self.llm_client.chat(messages, tools, stream=True):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            
            content = delta.get("content")
            if content:
                if self._is_tool_call_content(content):
                    print(f"[DEBUG] Tool call content detected, filtering: {repr(content[:50])}...")
                    full_response += content
                else:
                    print(f"[DEBUG] Content chunk: {repr(content[:50])}...")
                    full_response += content
                    yield {
                        "type": "content",
                        "content": content
                    }
            
            if "tool_calls" in delta:
                for tc in delta["tool_calls"]:
                    idx = tc.get("index", 0)
                    
                    if idx >= len(tool_calls_buffer):
                        tool_calls_buffer.append({
                            "id": tc.get("id", ""),
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        })
                    
                    if tc.get("id"):
                        tool_calls_buffer[idx]["id"] = tc["id"]
                    
                    if "function" in tc:
                        if tc["function"].get("name"):
                            tool_calls_buffer[idx]["function"]["name"] = tc["function"]["name"]
                        if tc["function"].get("arguments"):
                            tool_calls_buffer[idx]["function"]["arguments"] += tc["function"]["arguments"]
        
        if tool_calls_buffer:
            tool_names = [tc["function"]["name"] for tc in tool_calls_buffer]
            yield {
                "type": "thinking",
                "stage": "tool_planning",
                "message": f"计划执行 {len(tool_names)} 个工具: {', '.join(tool_names)}"
            }
            
            yield {
                "type": "tool_calls",
                "tools": tool_names
            }
            
            messages.append({
                "role": "assistant",
                "content": full_response or None,
                "tool_calls": tool_calls_buffer
            })
            
            for i, tc in enumerate(tool_calls_buffer):
                tool_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except:
                    args = {}
                
                tool_display_name = self._get_tool_display_name(tool_name)
                yield {
                    "type": "tool_call_start",
                    "tool": tool_name,
                    "display_name": tool_display_name,
                    "arguments": args,
                    "step": i + 1,
                    "total": len(tool_calls_buffer)
                }
                
                yield {
                    "type": "thinking",
                    "stage": "tool_executing",
                    "message": f"正在执行: {tool_display_name}..."
                }
                
                result = await self.tool_executor.execute(tool_name, args)
                
                result_summary = self._get_result_summary(result)
                yield {
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": result,
                    "summary": result_summary
                }
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            yield {
                "type": "thinking",
                "stage": "generating_response",
                "message": "正在整理结果..."
            }
            
            async for chunk in self._continue_conversation(messages):
                yield chunk
        else:
            text_tool_calls = self._parse_text_tool_calls(full_response)
            
            if text_tool_calls:
                tool_names = [tc["function"]["name"] for tc in text_tool_calls]
                
                yield {
                    "type": "thinking",
                    "stage": "tool_planning",
                    "message": f"计划执行 {len(tool_names)} 个工具: {', '.join([self._get_tool_display_name(n) for n in tool_names])}"
                }
                
                yield {
                    "type": "tool_calls",
                    "tools": tool_names
                }
                
                messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
                for i, tc in enumerate(text_tool_calls):
                    tool_name = tc["function"]["name"]
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except:
                        args = {}
                    
                    tool_display_name = self._get_tool_display_name(tool_name)
                    yield {
                        "type": "tool_call_start",
                        "tool": tool_name,
                        "display_name": tool_display_name,
                        "arguments": args,
                        "step": i + 1,
                        "total": len(text_tool_calls)
                    }
                    
                    yield {
                        "type": "thinking",
                        "stage": "tool_executing",
                        "message": f"正在执行: {tool_display_name}..."
                    }
                    
                    result = await self.tool_executor.execute(tool_name, args)
                    
                    result_summary = self._get_result_summary(result)
                    yield {
                        "type": "tool_result",
                        "tool": tool_name,
                        "result": result,
                        "summary": result_summary
                    }
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                yield {
                    "type": "thinking",
                    "stage": "generating_response",
                    "message": "正在整理结果..."
                }
                
                async for chunk in self._continue_conversation(messages):
                    yield chunk
            else:
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": full_response})
    
    async def _continue_conversation(self, messages: List[Dict]) -> AsyncGenerator[Dict[str, Any], None]:
        full_response = ""
        
        async for chunk in self.llm_client.chat(messages, stream=True):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            
            content = delta.get("content")
            if content:
                full_response += content
                yield {
                    "type": "content",
                    "content": content
                }
        
        if len(messages) >= 2:
            last_user = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user = msg["content"]
                    break
            
            if last_user:
                self.conversation_history.append({"role": "user", "content": last_user})
            self.conversation_history.append({"role": "assistant", "content": full_response})
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()
