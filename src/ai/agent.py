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
- 后端服务地址: http://localhost:8001
- 图表访问地址: http://localhost:8001/api/charts/

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
4. **必须使用markdown图片格式展示图表**: `![图表标题](http://localhost:8001/api/charts/xxx.png)`
5. 不要只显示URL文本，必须用图片格式让用户直接看到图表

### 重要提示：
- 快照ID (snapshot_id) 是整数类型
- 生成图表时需要指定正确的字段名
- 图表生成后必须返回完整的可访问URL给用户

## 回复格式要求（必须遵守）
- 使用清晰的中文回复
- 数据用表格或列表展示
- 分析结论要简洁明了
- 生成图表后，显示完整图表URL让用户查看
- **绝对禁止**在回复中包含`<tool_call>`、`<arg_key>`、`<arg_value>`等标签
- 工具调用应该通过API的function calling机制完成，而不是在文本中输出
- 如果工具调用失败，直接告诉用户错误信息，不要输出工具调用的XML格式

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
        print(f"[DEBUG] _parse_text_tool_calls called with text length: {len(text)}")
        print(f"[DEBUG] _parse_text_tool_calls text preview: {repr(text[:200])}")
        tool_calls = parse_tool_calls(text)
        print(f"[DEBUG] parse_tool_calls returned {len(tool_calls)} tool calls")
        result = tool_calls_to_openai_format(tool_calls)
        print(f"[DEBUG] tool_calls_to_openai_format returned {len(result)} items")
        return result
    
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
    
    def _filter_tool_call_tags(self, content: str) -> str:
        """过滤掉工具调用标签，返回给用户友好的内容"""
        import re
        
        # 定义需要过滤的模式
        patterns_to_filter = [
            # XML格式的工具调用
            (r'<tool_call>.*?</tool_call>', ''),
            (r'<arg_key>.*?</arg_key>', ''),
            (r'<arg_value>.*?</arg_value>', ''),
            # 其他工具调用格式
            (r'<｜tool▁calls▁begin｜>.*?<｜tool▁calls▁end｜>', '', re.DOTALL),
            (r'<｜tool▁call▁begin｜>.*?<｜tool▁call▁end｜>', '', re.DOTALL),
            (r'```tool_call.*?```', '', re.DOTALL),
            (r'```tool.*?```', '', re.DOTALL),
            (r'✿FUNCTION✿.*?✿END✿', '', re.DOTALL),
            (r'✿CALL✿.*?✿RESULT✿', '', re.DOTALL),
            # Python函数调用格式
            (r'pbbi_\w+\s*\([^)]*\)', ''),
            # 纯文本参数格式
            (r'pbbi_\w+\s*\n(?:\s*\w+\s*=.*\n?)+', ''),
        ]
        
        result = content
        for pattern in patterns_to_filter:
            if len(pattern) == 3:
                result = re.sub(pattern[0], pattern[1], result, flags=pattern[2])
            else:
                result = re.sub(pattern[0], pattern[1], result)
        
        # 清理多余的空行
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
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
        
        # 检测GLM-5的工具调用格式：pbbi_xxx(
        import re
        if re.search(r'pbbi_\w+\s*\(', content):
            return True
        
        # 检测GLM-5的纯文本格式：pbbi_xxx\nparam=value
        if re.search(r'pbbi_\w+\s*\n\s*\w+\s*=', content):
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
                # 过滤掉工具调用标签，不让用户看到
                filtered_content = self._filter_tool_call_tags(content)
                if filtered_content:
                    print(f"[DEBUG] Content chunk: {repr(content[:50])}...")
                    full_response += content
                    yield {
                        "type": "content",
                        "content": filtered_content
                    }
                else:
                    print(f"[DEBUG] Tool call content filtered: {repr(content[:50])}...")
                    full_response += content
            
            if "tool_calls" in delta:
                print(f"[DEBUG] API tool_calls in delta: {delta['tool_calls']}")
                for tc in delta["tool_calls"]:
                    print(f"[DEBUG] Processing tool call: index={tc.get('index')}, id={tc.get('id')}, function={tc.get('function', {})}")
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
            
            # 打印完整的工具调用参数
            for i, tc in enumerate(tool_calls_buffer):
                print(f"[DEBUG] Tool call {i}: name={tc['function']['name']}, arguments={repr(tc['function']['arguments'])}")
            
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
                args_str = tc["function"]["arguments"]
                print(f"[DEBUG] Parsing arguments for {tool_name}: {repr(args_str)}")
                try:
                    args = json.loads(args_str)
                    print(f"[DEBUG] Parsed args: {args}")
                except Exception as e:
                    print(f"[DEBUG] Failed to parse arguments: {e}")
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
                
                # 检查是否需要重试（字段验证失败等情况）
                if result.get("needs_retry"):
                    yield {
                        "type": "thinking",
                        "stage": "error_correction",
                        "message": f"检测到错误，正在自动修正..."
                    }
                    
                    # 将错误信息反馈给LLM
                    error_message = f"工具执行失败: {result.get('error')}\n请根据可用字段修正参数后重试。"
                    if result.get("available_fields"):
                        error_message += f"\n可用字段: {', '.join(result['available_fields'][:10])}"
                    
                    # 构建重试消息
                    retry_messages = messages.copy()
                    retry_messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tc]
                    })
                    retry_messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                    
                    # 让LLM重新生成正确的工具调用
                    retry_success = False
                    async for chunk in self.llm_client.chat(retry_messages, tools, stream=True):
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        
                        if "tool_calls" in delta:
                            for retry_tc in delta["tool_calls"]:
                                if retry_tc.get("function", {}).get("name"):
                                    retry_tool_name = retry_tc["function"]["name"]
                                    try:
                                        retry_args = json.loads(retry_tc["function"].get("arguments", "{}"))
                                    except:
                                        retry_args = {}
                                    
                                    # 执行修正后的工具调用
                                    retry_result = await self.tool_executor.execute(retry_tool_name, retry_args)
                                    
                                    if retry_result.get("success"):
                                        retry_success = True
                                        result = retry_result
                                        
                                        yield {
                                            "type": "thinking",
                                            "stage": "correction_success",
                                            "message": "自动修正成功！"
                                        }
                                        
                                        # 更新消息
                                        tc["function"]["arguments"] = json.dumps(retry_args, ensure_ascii=False)
                    
                    if not retry_success:
                        yield {
                            "type": "thinking",
                            "stage": "correction_failed",
                            "message": "自动修正失败，将显示错误信息"
                        }
                
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
            
            print(f"[DEBUG] Parsed text tool calls: {len(text_tool_calls)} from response length {len(full_response)}")
            if text_tool_calls:
                for tc in text_tool_calls:
                    print(f"[DEBUG] Tool: {tc['function']['name']}, args: {tc['function']['arguments'][:100] if tc['function'].get('arguments') else 'empty'}")
            
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
    
    async def _continue_conversation(self, messages: List[Dict], depth: int = 0) -> AsyncGenerator[Dict[str, Any], None]:
        # 限制递归深度，防止无限循环
        if depth > 3:
            yield {
                "type": "thinking",
                "stage": "max_depth_reached",
                "message": "已达到最大对话深度，结束对话"
            }
            return
        
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
        
        # 检查是否有文本工具调用
        text_tool_calls = self._parse_text_tool_calls(full_response)
        
        print(f"[DEBUG] _continue_conversation: Parsed {len(text_tool_calls)} text tool calls from response length {len(full_response)}")
        print(f"[DEBUG] _continue_conversation: full_response = {repr(full_response[:500])}")
        
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
                
                # 检查是否需要重试（字段验证失败等情况）
                if result.get("needs_retry"):
                    yield {
                        "type": "thinking",
                        "stage": "error_correction",
                        "message": f"⚠️ 工具执行失败: {result.get('error', '未知错误')}，正在尝试自动修正..."
                    }
                    
                    # 构建详细的错误反馈信息
                    error_feedback = f"""工具调用失败，需要修正参数：

**错误信息**: {result.get('error', '未知错误')}

**原始调用**:
- 工具: {tool_name}
- 参数: {json.dumps(args, ensure_ascii=False)}

**修正要求**:
1. 检查字段名是否正确
2. 参考可用字段列表选择正确的字段名
3. 重新生成工具调用

**可用字段**:
{chr(10).join([f"- {field}" for field in result.get('available_fields', [])[:15]])}
{('...' if len(result.get('available_fields', [])) > 15 else '')}

请使用正确的字段名重新生成工具调用。"""
                    
                    # 构建重试消息
                    retry_messages = messages.copy()
                    retry_messages.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    retry_messages.append({
                        "role": "user",
                        "content": error_feedback
                    })
                    
                    yield {
                        "type": "thinking",
                        "stage": "retrying",
                        "message": "正在请求AI重新生成正确的工具调用..."
                    }
                    
                    # 让LLM重新生成正确的工具调用
                    retry_full_response = ""
                    retry_success = False
                    
                    async for chunk in self.llm_client.chat(retry_messages, stream=True):
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            retry_full_response += content
                            # 实时显示AI的思考过程
                            if len(content) > 10:  # 只显示有意义的内容
                                yield {
                                    "type": "thinking",
                                    "stage": "ai_thinking",
                                    "message": content[:100] + ("..." if len(content) > 100 else "")
                                }
                    
                    # 解析重试响应中的工具调用
                    if retry_full_response:
                        retry_tool_calls = self._parse_text_tool_calls(retry_full_response)
                        
                        if retry_tool_calls:
                            yield {
                                "type": "thinking",
                                "stage": "retry_tool_detected",
                                "message": f"检测到 {len(retry_tool_calls)} 个修正后的工具调用"
                            }
                            
                            for retry_tc in retry_tool_calls:
                                retry_tool_name = retry_tc["function"]["name"]
                                try:
                                    retry_args = json.loads(retry_tc["function"]["arguments"])
                                except:
                                    retry_args = {}
                                
                                yield {
                                    "type": "tool_call_start",
                                    "tool": retry_tool_name,
                                    "display_name": self._get_tool_display_name(retry_tool_name),
                                    "arguments": retry_args,
                                    "step": 1,
                                    "total": 1,
                                    "is_retry": True
                                }
                                
                                # 执行修正后的工具调用
                                retry_result = await self.tool_executor.execute(retry_tool_name, retry_args)
                                
                                if retry_result.get("success"):
                                    retry_success = True
                                    result = retry_result
                                    
                                    yield {
                                        "type": "thinking",
                                        "stage": "correction_success",
                                        "message": "✅ 自动修正成功！图表已生成。"
                                    }
                                    
                                    yield {
                                        "type": "tool_result",
                                        "tool": retry_tool_name,
                                        "result": retry_result,
                                        "summary": self._get_result_summary(retry_result),
                                        "is_retry": True
                                    }
                                else:
                                    yield {
                                        "type": "thinking",
                                        "stage": "correction_failed",
                                        "message": f"❌ 自动修正仍然失败: {retry_result.get('error', '未知错误')}"
                                    }
                                    
                                    yield {
                                        "type": "tool_result",
                                        "tool": retry_tool_name,
                                        "result": retry_result,
                                        "summary": f"修正失败: {retry_result.get('error', '未知错误')}",
                                        "is_retry": True
                                    }
                        else:
                            yield {
                                "type": "thinking",
                                "stage": "no_retry_tool",
                                "message": "AI没有生成修正后的工具调用"
                            }
                    
                    if not retry_success:
                        yield {
                            "type": "thinking",
                            "stage": "correction_failed",
                            "message": "❌ 自动修正失败，请检查字段名是否正确"
                        }
                
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
            
            # 继续对话
            yield {
                "type": "thinking",
                "stage": "generating_response",
                "message": "正在整理结果..."
            }
            
            async for chunk in self._continue_conversation(messages, depth + 1):
                yield chunk
        else:
            if len(messages) >= 2:
                last_user = None
                for msg in reversed(messages):
                    if msg["role"] == "user":
                        last_user = msg["content"]
                        break
                
                if last_user:
                    self.conversation_history.append({"role": "user", "content": last_user})
                self.conversation_history.append({"role": "assistant", "content": full_response})
        
        # 发送结束标记
        yield {"type": "done"}
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()
