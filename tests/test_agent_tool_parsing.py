"""
Agent 工具解析单元测试
测试DeepSeek文本格式工具调用的解析功能
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestToolCallParsing:
    """测试工具调用解析"""
    
    def test_parse_simple_tool_call(self):
        """测试解析简单工具调用"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        
        text = '''<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_list_snapshots
```json
{}
```
<｜tool▁call▁end｜><｜tool▁calls▁end｜>'''
        
        tool_calls = agent._parse_text_tool_calls(text)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["function"]["name"] == "pbbi_list_snapshots"
    
    def test_parse_tool_call_with_params(self):
        """测试解析带参数的工具调用"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        
        text = '''<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_generate_bar_chart
```json
{"snapshot_id": 1, "x_field": "name", "y_field": "value"}
```
<｜tool▁call▁end｜><｜tool▁calls▁end｜>'''
        
        tool_calls = agent._parse_text_tool_calls(text)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["function"]["name"] == "pbbi_generate_bar_chart"
        
        import json
        args = json.loads(tool_calls[0]["function"]["arguments"])
        assert args["snapshot_id"] == 1
        assert args["x_field"] == "name"
        assert args["y_field"] == "value"
    
    def test_parse_multiple_tool_calls(self):
        """测试解析多个工具调用"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        
        text = '''<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_list_snapshots
```json
{}
```
<｜tool▁call▁end｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_get_snapshot_schema
```json
{"snapshot_id": 1}
```
<｜tool▁call▁end｜><｜tool▁calls▁end｜>'''
        
        tool_calls = agent._parse_text_tool_calls(text)
        
        assert len(tool_calls) == 2
        assert tool_calls[0]["function"]["name"] == "pbbi_list_snapshots"
        assert tool_calls[1]["function"]["name"] == "pbbi_get_snapshot_schema"
    
    def test_parse_empty_text(self):
        """测试解析空文本"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        tool_calls = agent._parse_text_tool_calls("")
        
        assert len(tool_calls) == 0
    
    def test_parse_no_tool_calls(self):
        """测试解析无工具调用的文本"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        tool_calls = agent._parse_text_tool_calls("这是一段普通文本，没有工具调用")
        
        assert len(tool_calls) == 0
    
    def test_parse_invalid_json(self):
        """测试解析无效JSON参数"""
        from src.ai.agent import PBBIAgent
        
        agent = PBBIAgent()
        
        text = '''<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>test_tool
```json
{invalid json}
```
<｜tool▁call▁end｜><｜tool▁calls▁end｜>'''
        
        tool_calls = agent._parse_text_tool_calls(text)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["function"]["name"] == "test_tool"
        
        import json
        args = json.loads(tool_calls[0]["function"]["arguments"])
        assert args == {}


class TestFullWidthCharacters:
    """测试全角字符处理"""
    
    def test_fullwidth_vs_halfwidth(self):
        """测试全角和半角字符的区别"""
        fullwidth_pipe = "｜"
        halfwidth_pipe = "|"
        
        assert fullwidth_pipe != halfwidth_pipe
        
        fullwidth_underscore = "▁"
        halfwidth_underscore = "_"
        
        assert fullwidth_underscore != halfwidth_underscore
    
    def test_pattern_matches_fullwidth(self):
        """测试正则表达式匹配全角字符"""
        import re
        
        pattern = r'<｜tool▁calls▁begin｜>'
        
        text_with_fullwidth = "<｜tool▁calls▁begin｜>"
        text_with_halfwidth = "<|tool_calls_begin|>"
        
        match_fullwidth = re.search(pattern, text_with_fullwidth)
        match_halfwidth = re.search(pattern, text_with_halfwidth)
        
        assert match_fullwidth is not None, "应匹配全角字符"
        assert match_halfwidth is None, "不应匹配半角字符"


class TestAgentSystemPrompt:
    """测试Agent系统提示"""
    
    def test_system_prompt_contains_server_info(self):
        """测试系统提示包含服务器信息"""
        from src.ai.agent import SYSTEM_PROMPT
        
        assert "localhost:8000" in SYSTEM_PROMPT
        assert "/api/charts/" in SYSTEM_PROMPT
    
    def test_system_prompt_contains_chart_tools(self):
        """测试系统提示包含图表工具"""
        from src.ai.agent import SYSTEM_PROMPT
        
        assert "pbbi_generate_bar_chart" in SYSTEM_PROMPT
        assert "pbbi_generate_pie_chart" in SYSTEM_PROMPT
        assert "pbbi_generate_line_chart" in SYSTEM_PROMPT
    
    def test_system_prompt_contains_markdown_format(self):
        """测试系统提示包含markdown图片格式说明"""
        from src.ai.agent import SYSTEM_PROMPT
        
        assert "![" in SYSTEM_PROMPT
        assert "markdown图片格式" in SYSTEM_PROMPT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
