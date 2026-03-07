"""
工具调用解析器
支持多种AI模型的工具调用格式解析
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolCallParser(ABC):
    """工具调用解析器基类"""
    
    @abstractmethod
    def parse(self, content: str) -> List[ToolCall]:
        """解析工具调用"""
        pass
    
    @abstractmethod
    def detect(self, content: str) -> bool:
        """检测内容是否包含工具调用"""
        pass


class OpenAIToolCallParser(ToolCallParser):
    """OpenAI标准格式解析器（GPT、DeepSeek-V3等）"""
    
    def detect(self, content: str) -> bool:
        return bool(re.search(r'<｜tool▁calls▁begin｜>', content))
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        patterns = [
            r'function<｜tool▁sep｜>(\w+).*?```json\s*(\{.*?\})\s*```',
            r'function<｜tool▁sep｜>(\w+)\s*\n?\s*(\{[^{}]*\})\s*\n?\s*```',
            r'function<｜tool▁sep｜>(\w+)\s*(\{[^{}]*\})\s*```',
            r'function<｜tool▁sep｜>(\w+)\s*\n+\s*(\{.*?\})\s*\n+\s*```',
        ]
        
        seen_tools = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                tool_name = match[0]
                if tool_name in seen_tools:
                    continue
                seen_tools.add(tool_name)
                
                try:
                    args = json.loads(match[1])
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id=f"call_{len(tool_calls)}",
                    name=tool_name,
                    arguments=args
                ))
        
        if not tool_calls:
            pattern = r'<｜tool▁call▁begin｜>function<｜tool▁sep｜>(\w+)\s*\n?\s*(\{.*?\})\s*\n?\s*```<｜tool▁call▁end｜>'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for idx, match in enumerate(matches):
                try:
                    args = json.loads(match[1])
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id=f"call_{idx}",
                    name=match[0],
                    arguments=args
                ))
        
        return tool_calls


class MinimaxToolCallParser(ToolCallParser):
    """Minimax XML格式解析器"""
    
    def detect(self, content: str) -> bool:
        return '<invoke' in content or 'minimax:tool_call' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        invoke_pattern = r'<invoke\s+name="([^"]+)">(.*?)</invoke>'
        invoke_matches = re.findall(invoke_pattern, content, re.DOTALL)
        
        for idx, (tool_name, params_xml) in enumerate(invoke_matches):
            args = {}
            
            param_pattern = r'<parameter\s+name="([^"]+)">(.*?)</parameter>'
            params = re.findall(param_pattern, params_xml, re.DOTALL)
            
            for param_name, param_value in params:
                param_value = param_value.strip()
                try:
                    args[param_name] = json.loads(param_value)
                except:
                    args[param_name] = param_value
            
            tool_calls.append(ToolCall(
                id=f"call_{idx}",
                name=tool_name,
                arguments=args
            ))
        
        return tool_calls


class AnthropicToolCallParser(ToolCallParser):
    """Anthropic Claude格式解析器"""
    
    def detect(self, content: str) -> bool:
        return '<tool_calls>' in content or '<invoke_tool>' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        patterns = [
            r'<tool_calltools>\s*<name>([^<]+)</name>\s*<arguments>([^<]+)</arguments>\s*</tool_calltools>',
            r'<invoke_tool>\s*<name>([^<]+)</name>\s*<parameters>([^<]+)</parameters>\s*</invoke_tool>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for idx, match in enumerate(matches):
                try:
                    args = json.loads(match[1])
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id=f"call_{idx}",
                    name=match[0].strip(),
                    arguments=args
                ))
        
        return tool_calls


class GLMToolCallParser(ToolCallParser):
    """智谱GLM格式解析器"""
    
    def detect(self, content: str) -> bool:
        return '```tool_call' in content or '```tool' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        patterns = [
            r'```tool_call\s*\n?\s*(\w+)\s*\n?\s*(\{.*?\})\s*```',
            r'```tool\s*\n?\s*(\w+)\s*\n?\s*(\{.*?\})\s*```',
        ]
        
        seen_tools = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                tool_name = match[0]
                if tool_name in seen_tools:
                    continue
                seen_tools.add(tool_name)
                
                try:
                    args = json.loads(match[1])
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id=f"call_{len(tool_calls)}",
                    name=tool_name,
                    arguments=args
                ))
        
        return tool_calls


class QwenToolCallParser(ToolCallParser):
    """通义千问格式解析器"""
    
    def detect(self, content: str) -> bool:
        return '✿FUNCTION✿' in content or '✿CALL✿' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        patterns = [
            r'✿FUNCTION✿\s*(\w+)\s*✿ARGS✿\s*(\{.*?\})\s*✿END✿',
            r'✿CALL✿\s*(\w+)\s*\n?\s*(\{.*?\})\s*✿RESULT✿',
        ]
        
        seen_tools = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                tool_name = match[0]
                if tool_name in seen_tools:
                    continue
                seen_tools.add(tool_name)
                
                try:
                    args = json.loads(match[1])
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id=f"call_{len(tool_calls)}",
                    name=tool_name,
                    arguments=args
                ))
        
        return tool_calls


class DeepSeekDSMLParser(ToolCallParser):
    """DeepSeek-R1 DSML格式解析器"""
    
    def detect(self, content: str) -> bool:
        return '<｜DSML｜' in content or '<|DSML|>' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        invoke_pattern = r'<｜DSML｜invoke\s+name="([^"]+)">(.*?)</｜DSML｜invoke>'
        invoke_matches = re.findall(invoke_pattern, content, re.DOTALL)
        
        for idx, (tool_name, params_xml) in enumerate(invoke_matches):
            args = {}
            
            param_pattern = r'<｜DSML｜parameter\s+name="([^"]+)"[^>]*>(.*?)</｜DSML｜parameter>'
            params = re.findall(param_pattern, params_xml, re.DOTALL)
            
            for param_name, param_value in params:
                param_value = param_value.strip()
                try:
                    args[param_name] = json.loads(param_value)
                except:
                    args[param_name] = param_value
            
            tool_calls.append(ToolCall(
                id=f"call_{idx}",
                name=tool_name,
                arguments=args
            ))
        
        return tool_calls


class JSONToolCallParser(ToolCallParser):
    """通用JSON格式解析器（兜底方案）"""
    
    def detect(self, content: str) -> bool:
        return '"tool_calls"' in content or '"function_call"' in content
    
    def parse(self, content: str) -> List[ToolCall]:
        tool_calls = []
        
        try:
            start_idx = content.find('{"tool_calls"')
            if start_idx == -1:
                start_idx = content.find('{ "tool_calls"')
            if start_idx != -1:
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                for idx, tc in enumerate(data.get('tool_calls', [])):
                    func = tc.get('function', {})
                    args_str = func.get('arguments', '{}')
                    try:
                        args = json.loads(args_str) if isinstance(args_str, str) else args_str
                    except:
                        args = {}
                    
                    tool_calls.append(ToolCall(
                        id=tc.get('id', f"call_{idx}"),
                        name=func.get('name', ''),
                        arguments=args
                    ))
                
                if tool_calls:
                    return tool_calls
        except Exception as e:
            pass
        
        try:
            start_idx = content.find('{"function_call"')
            if start_idx != -1:
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                func = data.get('function_call', {})
                args_str = func.get('arguments', '{}')
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except:
                    args = {}
                
                tool_calls.append(ToolCall(
                    id="call_0",
                    name=func.get('name', ''),
                    arguments=args
                ))
        except:
            pass
        
        return tool_calls


class ToolCallParserRegistry:
    """工具调用解析器注册表"""
    
    def __init__(self):
        self.parsers: List[ToolCallParser] = [
            OpenAIToolCallParser(),
            DeepSeekDSMLParser(),
            MinimaxToolCallParser(),
            AnthropicToolCallParser(),
            GLMToolCallParser(),
            QwenToolCallParser(),
            JSONToolCallParser(),
        ]
    
    def parse(self, content: str) -> List[ToolCall]:
        """自动检测并解析工具调用"""
        for parser in self.parsers:
            if parser.detect(content):
                tool_calls = parser.parse(content)
                if tool_calls:
                    return tool_calls
        
        return []
    
    def to_openai_format(self, tool_calls: List[ToolCall]) -> List[Dict]:
        """转换为OpenAI标准格式"""
        return [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments)
                }
            }
            for tc in tool_calls
        ]


parser_registry = ToolCallParserRegistry()


def parse_tool_calls(content: str) -> List[ToolCall]:
    """解析工具调用的便捷函数"""
    return parser_registry.parse(content)


def tool_calls_to_openai_format(tool_calls: List[ToolCall]) -> List[Dict]:
    """转换为OpenAI格式的便捷函数"""
    return parser_registry.to_openai_format(tool_calls)
