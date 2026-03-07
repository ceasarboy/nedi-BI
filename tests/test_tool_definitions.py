# -*- coding: utf-8 -*-
"""验证工具定义"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tool_definitions():
    """验证工具定义"""
    from src.ai.llm_client import LLMClient
    
    client = LLMClient()
    tools = client.get_tools_definition()
    
    print(f"工具定义总数: {len(tools)}")
    
    # 统计图表工具（包含generate且包含chart或plot或histogram或heatmap）
    chart_tools = [t for t in tools if "generate" in t["function"]["name"] and 
                   any(x in t["function"]["name"] for x in ["chart", "plot", "histogram", "heatmap"])]
    print(f"图表工具数量: {len(chart_tools)}")
    
    print("\n图表工具列表:")
    for t in chart_tools:
        print(f"  - {t['function']['name']}")
    
    # 验证数量
    assert len(chart_tools) == 19, f"期望19个图表工具，实际{len(chart_tools)}个"
    
    print("\n✓ 工具定义验证通过！")
    return True

if __name__ == "__main__":
    success = test_tool_definitions()
    sys.exit(0 if success else 1)
