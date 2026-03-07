# -*- coding: utf-8 -*-
"""测试DeepSeek工具调用解析"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parse_text_tool_calls():
    """测试DeepSeek工具调用解析"""
    from src.ai.agent import PBBIAgent
    
    agent = PBBIAgent()
    
    # 测试用例1: 实际返回格式（无json标记）
    text1 = """<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_query_snapshot 
 
 {"snapshot_id": 1} 
 
 ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>"""
    
    result1 = agent._parse_text_tool_calls(text1)
    print("测试用例1: 实际返回格式（无json标记）")
    print(f"  输入: {repr(text1[:80])}...")
    print(f"  结果: {result1}")
    assert len(result1) == 1, f"期望1个工具调用，实际{len(result1)}个"
    assert result1[0]["function"]["name"] == "pbbi_query_snapshot"
    print("  ✓ 通过\n")
    
    # 测试用例2: 带json标记格式
    text2 = """<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_generate_bar_chart```json
{"snapshot_id": 1, "x_field": "category", "y_field": "value"}
```<｜tool▁call▁end｜><｜tool▁calls▁end｜>"""
    
    result2 = agent._parse_text_tool_calls(text2)
    print("测试用例2: 带json标记格式")
    print(f"  输入: {repr(text2[:80])}...")
    print(f"  结果: {result2}")
    assert len(result2) == 1, f"期望1个工具调用，实际{len(result2)}个"
    assert result2[0]["function"]["name"] == "pbbi_generate_bar_chart"
    print("  ✓ 通过\n")
    
    # 测试用例3: 多个工具调用
    text3 = """<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_query_snapshot 
 
 {"snapshot_id": 1} 
 
 ```<｜tool▁call▁end｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_get_snapshot_schema 
 
 {"snapshot_id": 1} 
 
 ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>"""
    
    result3 = agent._parse_text_tool_calls(text3)
    print("测试用例3: 多个工具调用")
    print(f"  输入: {repr(text3[:80])}...")
    print(f"  结果数量: {len(result3)}")
    assert len(result3) == 2, f"期望2个工具调用，实际{len(result3)}个"
    assert result3[0]["function"]["name"] == "pbbi_query_snapshot"
    assert result3[1]["function"]["name"] == "pbbi_get_snapshot_schema"
    print("  ✓ 通过\n")
    
    # 测试用例4: 3D图表工具
    text4 = """<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_generate_bar_3d_chart 
 
 {"snapshot_id": 1, "x_field": "x", "y_field": "y", "z_field": "value"} 
 
 ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>"""
    
    result4 = agent._parse_text_tool_calls(text4)
    print("测试用例4: 3D图表工具")
    print(f"  输入: {repr(text4[:80])}...")
    print(f"  结果: {result4}")
    assert len(result4) == 1, f"期望1个工具调用，实际{len(result4)}个"
    assert result4[0]["function"]["name"] == "pbbi_generate_bar_3d_chart"
    print("  ✓ 通过\n")
    
    # 测试用例5: LED晶圆图工具
    text5 = """<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>pbbi_generate_led_wafer_chart 
 
 {"snapshot_id": 1, "x_field": "x", "y_field": "y", "z_field": "brightness"} 
 
 ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>"""
    
    result5 = agent._parse_text_tool_calls(text5)
    print("测试用例5: LED晶圆图工具")
    print(f"  输入: {repr(text5[:80])}...")
    print(f"  结果: {result5}")
    assert len(result5) == 1, f"期望1个工具调用，实际{len(result5)}个"
    assert result5[0]["function"]["name"] == "pbbi_generate_led_wafer_chart"
    print("  ✓ 通过\n")
    
    print("=" * 50)
    print("所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_parse_text_tool_calls()
    sys.exit(0 if success else 1)
