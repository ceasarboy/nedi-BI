# -*- coding: utf-8 -*-
"""测试图表生成完整流程"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
from pathlib import Path

def test_chart_generation():
    """测试图表生成"""
    from src.mcp import chart_mcp
    
    # 检查数据库
    db_path = Path("config/pb_bi.db")
    if not db_path.exists():
        print("数据库不存在")
        return False
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取第一个快照
    cursor.execute("SELECT id, name FROM data_snapshots LIMIT 1")
    row = cursor.fetchone()
    
    if not row:
        print("没有数据快照")
        conn.close()
        return False
    
    snapshot_id = row["id"]
    snapshot_name = row["name"]
    print(f"使用快照: ID={snapshot_id}, 名称={snapshot_name}")
    
    # 获取快照数据
    cursor.execute("SELECT data FROM data_snapshots WHERE id = ?", (snapshot_id,))
    data_row = cursor.fetchone()
    data = json.loads(data_row["data"])
    
    print(f"数据行数: {len(data)}")
    if data:
        print(f"数据字段: {list(data[0].keys())}")
    
    conn.close()
    
    # 测试生成柱状图
    print("\n测试生成柱状图...")
    tool = chart_mcp.GenerateBarChartTool()
    
    # 直接使用数据中的字段
    fields = list(data[0].keys())
    print(f"可用字段: {fields}")
    
    # 使用第一个字段作为X轴，最后一个数值字段作为Y轴
    x_field = fields[0]  # X（um）
    y_field = fields[2]  # 亮度（nit）
    
    print(f"使用字段: x={x_field}, y={y_field}")
    
    result = tool.execute({
        "snapshot_id": snapshot_id,
        "x_field": x_field,
        "y_field": y_field,
        "title": "测试柱状图"
    })
    
    print(f"结果: {result}")
    
    if result.get("success"):
        chart_url = result.get("chart_url")
        print(f"图表URL: {chart_url}")
        
        # 检查文件是否存在
        chart_filename = chart_url.split("/")[-1]
        chart_path = Path("config/charts") / chart_filename
        if chart_path.exists():
            print(f"图表文件存在: {chart_path}")
            print(f"文件大小: {chart_path.stat().st_size} bytes")
        else:
            print(f"图表文件不存在: {chart_path}")
        
        return True
    else:
        print(f"生成失败: {result.get('error')}")
        return False

if __name__ == "__main__":
    success = test_chart_generation()
    sys.exit(0 if success else 1)
