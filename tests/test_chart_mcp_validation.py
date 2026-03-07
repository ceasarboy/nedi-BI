# -*- coding: utf-8 -*-
"""图表MCP综合验证测试脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import time
from pathlib import Path
from unittest.mock import MagicMock

def test_mcp_registration():
    """验证MCP组件注册"""
    print("\n=== 1. MCP组件注册验证 ===")
    from src.mcp.chart_mcp import register_chart_tools
    
    mock_service = MagicMock()
    tools = register_chart_tools(mock_service)
    
    print(f"注册工具总数: {len(tools)}")
    assert len(tools) == 19, f"期望19个工具，实际{len(tools)}个"
    print("✓ MCP组件注册验证通过")
    return True

def test_database_and_snapshots():
    """验证数据库和数据快照"""
    print("\n=== 2. 数据库和数据快照验证 ===")
    
    db_path = Path("config/pb_bi.db")
    if not db_path.exists():
        print("数据库文件不存在，需要通过后端API创建测试数据")
        return False
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM data_snapshots ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    if rows:
        print(f"找到 {len(rows)} 个数据快照:")
        for row in rows:
            print(f"  ID: {row['id']}, 名称: {row['name']}")
        conn.close()
        return True
    else:
        print("无数据快照")
        conn.close()
        return False

def test_chart_tools_parameters():
    """验证所有图表工具参数定义"""
    print("\n=== 3. 图表工具参数验证 ===")
    
    from src.mcp.chart_mcp import (
        GenerateBarChartTool, GeneratePieChartTool, GenerateLineChartTool,
        GenerateScatterChartTool, GenerateBoxPlotTool, GenerateHistogramTool,
        GenerateHeatmapTool, GenerateRadarChartTool, GenerateFunnelChartTool,
        GenerateGaugeChartTool, GenerateComboChartTool,
        GenerateBar3DChartTool, GenerateScatter3DChartTool,
        GenerateSurface3DChartTool, GenerateLEDWaferChartTool,
        GenerateMultipleYAxisChartTool, GenerateStackedBarChartTool,
        GenerateStackedLineChartTool, GenerateLinkedChartTool
    )
    
    tools = [
        ("柱状图", GenerateBarChartTool()),
        ("饼图", GeneratePieChartTool()),
        ("折线图", GenerateLineChartTool()),
        ("散点图", GenerateScatterChartTool()),
        ("箱线图", GenerateBoxPlotTool()),
        ("直方图", GenerateHistogramTool()),
        ("热力图", GenerateHeatmapTool()),
        ("雷达图", GenerateRadarChartTool()),
        ("漏斗图", GenerateFunnelChartTool()),
        ("仪表盘", GenerateGaugeChartTool()),
        ("组合图", GenerateComboChartTool()),
        ("3D柱状图", GenerateBar3DChartTool()),
        ("3D散点图", GenerateScatter3DChartTool()),
        ("3D曲面图", GenerateSurface3DChartTool()),
        ("LED晶圆图", GenerateLEDWaferChartTool()),
        ("多Y轴图", GenerateMultipleYAxisChartTool()),
        ("堆叠柱状图", GenerateStackedBarChartTool()),
        ("堆叠折线图", GenerateStackedLineChartTool()),
        ("联动图表", GenerateLinkedChartTool()),
    ]
    
    passed = 0
    for name, tool in tools:
        params = tool.get_parameters()
        if params.get("type") == "object" and "properties" in params:
            print(f"  ✓ {name}: 参数定义正确")
            passed += 1
        else:
            print(f"  ✗ {name}: 参数定义错误")
    
    print(f"\n参数验证通过: {passed}/{len(tools)}")
    return passed == len(tools)

def test_chart_execution_with_mock():
    """使用模拟数据测试图表执行"""
    print("\n=== 4. 图表执行测试（模拟数据）===")
    
    import tempfile
    import shutil
    
    from src.mcp import chart_mcp
    
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test.db"
    charts_dir = temp_dir / "charts"
    charts_dir.mkdir()
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS data_snapshots (
            id INTEGER PRIMARY KEY,
            name TEXT,
            data TEXT
        )
    """)
    
    test_data = [
        {"category": "A", "value": 100, "value2": 50, "x": 1, "y": 2, "z": 3},
        {"category": "B", "value": 200, "value2": 80, "x": 2, "y": 4, "z": 6},
        {"category": "C", "value": 150, "value2": 60, "x": 3, "y": 5, "z": 9},
        {"category": "D", "value": 300, "value2": 90, "x": 4, "y": 3, "z": 12},
        {"category": "E", "value": 250, "value2": 70, "x": 5, "y": 6, "z": 15},
    ]
    
    conn.execute("INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
                 ("test_data", json.dumps(test_data)))
    
    funnel_data = [
        {"stage": "访问", "count": 1000},
        {"stage": "注册", "count": 500},
        {"stage": "下单", "count": 200},
        {"stage": "支付", "count": 150},
    ]
    conn.execute("INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
                 ("funnel_data", json.dumps(funnel_data)))
    
    radar_data = [
        {"dimension": "销售", "score": 80},
        {"dimension": "市场", "score": 70},
        {"dimension": "研发", "score": 90},
        {"dimension": "服务", "score": 85},
        {"dimension": "管理", "score": 75},
    ]
    conn.execute("INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
                 ("radar_data", json.dumps(radar_data)))
    
    conn.commit()
    conn.close()
    
    original_db = chart_mcp.MAIN_DB_PATH
    original_charts = chart_mcp.CHARTS_DIR
    
    chart_mcp.MAIN_DB_PATH = db_path
    chart_mcp.CHARTS_DIR = charts_dir
    
    results = []
    
    test_cases = [
        ("柱状图", chart_mcp.GenerateBarChartTool(), {"snapshot_id": 1, "x_field": "category", "y_field": "value"}),
        ("饼图", chart_mcp.GeneratePieChartTool(), {"snapshot_id": 1, "category_field": "category", "value_field": "value"}),
        ("折线图", chart_mcp.GenerateLineChartTool(), {"snapshot_id": 1, "x_field": "category", "y_field": "value"}),
        ("散点图", chart_mcp.GenerateScatterChartTool(), {"snapshot_id": 1, "x_field": "x", "y_field": "y"}),
        ("箱线图", chart_mcp.GenerateBoxPlotTool(), {"snapshot_id": 1, "field": "value"}),
        ("直方图", chart_mcp.GenerateHistogramTool(), {"snapshot_id": 1, "field": "value"}),
        ("热力图", chart_mcp.GenerateHeatmapTool(), {"snapshot_id": 1, "x_field": "x", "y_field": "category", "value_field": "value"}),
        ("雷达图", chart_mcp.GenerateRadarChartTool(), {"snapshot_id": 3, "category_field": "dimension", "value_field": "score"}),
        ("漏斗图", chart_mcp.GenerateFunnelChartTool(), {"snapshot_id": 2, "stage_field": "stage", "value_field": "count"}),
        ("仪表盘", chart_mcp.GenerateGaugeChartTool(), {"snapshot_id": 1, "value_field": "value"}),
        ("组合图", chart_mcp.GenerateComboChartTool(), {"snapshot_id": 1, "x_field": "category", "bar_field": "value", "line_field": "value2"}),
        ("3D柱状图", chart_mcp.GenerateBar3DChartTool(), {"snapshot_id": 1, "x_field": "category", "y_field": "category", "z_field": "value"}),
        ("3D散点图", chart_mcp.GenerateScatter3DChartTool(), {"snapshot_id": 1, "x_field": "x", "y_field": "y", "z_field": "z"}),
        ("3D曲面图", chart_mcp.GenerateSurface3DChartTool(), {"snapshot_id": 1, "x_field": "x", "y_field": "y", "z_field": "z"}),
        ("LED晶圆图", chart_mcp.GenerateLEDWaferChartTool(), {"snapshot_id": 1, "x_field": "x", "y_field": "y", "z_field": "value"}),
        ("多Y轴图", chart_mcp.GenerateMultipleYAxisChartTool(), {"snapshot_id": 1, "x_field": "category", "y_fields": ["value", "value2"]}),
        ("堆叠柱状图", chart_mcp.GenerateStackedBarChartTool(), {"snapshot_id": 1, "x_field": "category", "y_fields": ["value", "value2"]}),
        ("堆叠折线图", chart_mcp.GenerateStackedLineChartTool(), {"snapshot_id": 1, "x_field": "category", "y_fields": ["value", "value2"]}),
        ("联动图表", chart_mcp.GenerateLinkedChartTool(), {"snapshot_id": 1, "x_field": "category", "name_field": "category", "value_field": "value"}),
    ]
    
    for name, tool, params in test_cases:
        try:
            result = tool.execute(params)
            if result.get("success"):
                print(f"  ✓ {name}: 执行成功")
                results.append((name, True, None))
            else:
                print(f"  ✗ {name}: {result.get('error', '未知错误')}")
                results.append((name, False, result.get('error')))
        except Exception as e:
            print(f"  ✗ {name}: 异常 - {str(e)}")
            results.append((name, False, str(e)))
    
    chart_mcp.MAIN_DB_PATH = original_db
    chart_mcp.CHARTS_DIR = original_charts
    
    shutil.rmtree(temp_dir)
    
    passed = sum(1 for r in results if r[1])
    print(f"\n执行测试通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def main():
    print("=" * 60)
    print("图表MCP综合验证测试")
    print("=" * 60)
    
    results = []
    
    results.append(("MCP组件注册", test_mcp_registration()))
    results.append(("数据库快照", test_database_and_snapshots()))
    results.append(("工具参数验证", test_chart_tools_parameters()))
    results.append(("图表执行测试", test_chart_execution_with_mock()))
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
    
    total_passed = sum(1 for r in results if r[1])
    print(f"\n总计: {total_passed}/{len(results)} 项通过")
    
    return total_passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
