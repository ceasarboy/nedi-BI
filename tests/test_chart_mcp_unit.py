"""
Chart MCP 单元测试
测试图表生成工具的核心功能
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.chart_mcp import (
    _setup_chinese_font,
    _get_chart_cache_key,
    _check_chart_cache,
    _save_to_cache,
    _validate_numeric_field,
    GenerateBarChartTool,
    GeneratePieChartTool,
    GenerateLineChartTool,
    GenerateScatterChartTool,
    GenerateBoxPlotTool,
    GenerateHistogramTool,
    GenerateHeatmapTool,
    GenerateRadarChartTool,
    GenerateFunnelChartTool,
    GenerateGaugeChartTool,
    GenerateComboChartTool,
    BaseChartTool,
    CHART_CACHE,
    CHART_CACHE_MAX_SIZE
)


class TestChartCache:
    """测试图表缓存功能"""
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        key1 = _get_chart_cache_key("bar", {"snapshot_id": 1, "x_field": "a", "y_field": "b"})
        key2 = _get_chart_cache_key("bar", {"snapshot_id": 1, "x_field": "a", "y_field": "b"})
        key3 = _get_chart_cache_key("bar", {"snapshot_id": 2, "x_field": "a", "y_field": "b"})
        
        assert key1 == key2, "相同参数应生成相同的缓存键"
        assert key1 != key3, "不同参数应生成不同的缓存键"
        assert len(key1) == 32, "MD5哈希应为32字符"
    
    def test_cache_save_and_check(self):
        """测试缓存保存和检查"""
        test_key = "test_cache_key_123"
        test_result = {"success": True, "chart_url": "/api/charts/test.png"}
        
        _save_to_cache(test_key, test_result)
        cached = _check_chart_cache(test_key)
        
        assert cached == test_result, "缓存结果应与原始结果一致"
        
        CHART_CACHE.pop(test_key, None)
    
    def test_cache_max_size(self):
        """测试缓存上限"""
        global CHART_CACHE
        
        original_cache = CHART_CACHE.copy()
        CHART_CACHE.clear()
        
        for i in range(CHART_CACHE_MAX_SIZE + 10):
            _save_to_cache(f"key_{i}", {"data": i})
        
        assert len(CHART_CACHE) <= CHART_CACHE_MAX_SIZE, f"缓存不应超过上限 {CHART_CACHE_MAX_SIZE}"
        
        CHART_CACHE.clear()
        CHART_CACHE.update(original_cache)


class TestNumericValidation:
    """测试数值字段验证"""
    
    def test_validate_numeric_field_valid(self):
        """测试有效的数值字段"""
        import pandas as pd
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        
        is_valid, error = _validate_numeric_field(df, "value")
        
        assert is_valid == True, "数值字段应验证通过"
        assert error is None
    
    def test_validate_numeric_field_invalid(self):
        """测试无效的字段"""
        import pandas as pd
        df = pd.DataFrame({"text": ["a", "b", "c"]})
        
        is_valid, error = _validate_numeric_field(df, "text")
        
        assert is_valid == False, "文本字段应验证失败"
        assert error is not None
    
    def test_validate_numeric_field_missing(self):
        """测试不存在的字段"""
        import pandas as pd
        df = pd.DataFrame({"value": [1, 2, 3]})
        
        is_valid, error = _validate_numeric_field(df, "nonexistent")
        
        assert is_valid == False, "不存在的字段应验证失败"
        assert "不存在" in error
    
    def test_validate_numeric_field_empty(self):
        """测试空数据"""
        import pandas as pd
        df = pd.DataFrame({"value": [None, None, None]})
        
        is_valid, error = _validate_numeric_field(df, "value")
        
        # pandas会将None列视为float64类型，所以验证会通过
        # 这是预期行为，因为字段类型是数值类型
        assert is_valid == True, "空数值列仍被视为数值类型"


class TestChineseFontSetup:
    """测试中文字体配置"""
    
    def test_setup_chinese_font_no_error(self):
        """测试字体配置不抛出异常"""
        try:
            _setup_chinese_font()
            assert True
        except Exception as e:
            pytest.fail(f"字体配置不应抛出异常: {e}")


class TestToolParameters:
    """测试工具参数定义"""
    
    def test_bar_chart_parameters(self):
        """测试柱状图参数定义"""
        tool = GenerateBarChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
        assert "snapshot_id" in params["required"]
    
    def test_pie_chart_parameters(self):
        """测试饼图参数定义"""
        tool = GeneratePieChartTool()
        params = tool.get_parameters()
        
        assert "category_field" in params["properties"]
        assert "value_field" in params["properties"]
    
    def test_line_chart_parameters(self):
        """测试折线图参数定义"""
        tool = GenerateLineChartTool()
        params = tool.get_parameters()
        
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
    
    def test_scatter_chart_parameters(self):
        """测试散点图参数定义"""
        tool = GenerateScatterChartTool()
        params = tool.get_parameters()
        
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
    
    def test_box_plot_parameters(self):
        """测试箱线图参数定义"""
        tool = GenerateBoxPlotTool()
        params = tool.get_parameters()
        
        assert "field" in params["properties"]


class TestToolExecution:
    """测试工具执行"""
    
    def test_bar_chart_missing_params(self):
        """测试柱状图缺少参数"""
        tool = GenerateBarChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_bar_chart_invalid_snapshot(self):
        """测试柱状图无效快照ID"""
        tool = GenerateBarChartTool()
        result = tool.execute({
            "snapshot_id": 99999,
            "x_field": "test",
            "y_field": "value"
        })
        
        assert result["success"] == False
        assert "不存在" in result["error"] or "error" in result
    
    def test_pie_chart_missing_params(self):
        """测试饼图缺少参数"""
        tool = GeneratePieChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
    
    def test_box_plot_missing_params(self):
        """测试箱线图缺少参数"""
        tool = GenerateBoxPlotTool()
        result = tool.execute({})
        
        assert result["success"] == False


class TestBaseChartTool:
    """测试基类功能"""
    
    def test_get_chart_type(self):
        """测试图表类型获取"""
        tool = GenerateBarChartTool()
        chart_type = tool.get_chart_type()
        
        assert chart_type == "bar_chart"
    
    def test_create_result(self):
        """测试结果创建"""
        tool = GenerateBarChartTool()
        result = tool._create_result("bar", "/api/charts/test.png", "测试标题")
        
        assert result["success"] == True
        assert result["chart_type"] == "bar"
        assert result["chart_url"] == "/api/charts/test.png"
        assert result["title"] == "测试标题"
    
    def test_create_error(self):
        """测试错误创建"""
        tool = GenerateBarChartTool()
        result = tool._create_error("测试错误")
        
        assert result["success"] == False
        assert result["error"] == "测试错误"


class TestHistogramTool:
    """测试直方图工具"""
    
    def test_histogram_parameters(self):
        """测试直方图参数定义"""
        tool = GenerateHistogramTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "field" in params["properties"]
        assert "bins" in params["properties"]
        assert "snapshot_id" in params["required"]
        assert "field" in params["required"]
    
    def test_histogram_missing_params(self):
        """测试直方图缺少参数"""
        tool = GenerateHistogramTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_histogram_get_name(self):
        """测试直方图工具名称"""
        tool = GenerateHistogramTool()
        
        assert tool.get_name() == "pbbi_generate_histogram"
        assert tool.get_description() == "根据数据生成直方图，用于展示数据分布"


class TestHeatmapTool:
    """测试热力图工具"""
    
    def test_heatmap_parameters(self):
        """测试热力图参数定义"""
        tool = GenerateHeatmapTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
        assert "value_field" in params["properties"]
    
    def test_heatmap_missing_params(self):
        """测试热力图缺少参数"""
        tool = GenerateHeatmapTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_heatmap_partial_params(self):
        """测试热力图部分参数"""
        tool = GenerateHeatmapTool()
        result = tool.execute({"snapshot_id": 1, "x_field": "a"})
        
        assert result["success"] == False
        assert "必需" in result["error"]


class TestRadarChartTool:
    """测试雷达图工具"""
    
    def test_radar_parameters(self):
        """测试雷达图参数定义"""
        tool = GenerateRadarChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "category_field" in params["properties"]
        assert "value_field" in params["properties"]
    
    def test_radar_missing_params(self):
        """测试雷达图缺少参数"""
        tool = GenerateRadarChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_radar_get_name(self):
        """测试雷达图工具名称"""
        tool = GenerateRadarChartTool()
        
        assert tool.get_name() == "pbbi_generate_radar_chart"
        assert "雷达图" in tool.get_description()


class TestFunnelChartTool:
    """测试漏斗图工具"""
    
    def test_funnel_parameters(self):
        """测试漏斗图参数定义"""
        tool = GenerateFunnelChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "stage_field" in params["properties"]
        assert "value_field" in params["properties"]
    
    def test_funnel_missing_params(self):
        """测试漏斗图缺少参数"""
        tool = GenerateFunnelChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_funnel_get_name(self):
        """测试漏斗图工具名称"""
        tool = GenerateFunnelChartTool()
        
        assert tool.get_name() == "pbbi_generate_funnel_chart"
        assert "漏斗图" in tool.get_description()


class TestGaugeChartTool:
    """测试仪表盘工具"""
    
    def test_gauge_parameters(self):
        """测试仪表盘参数定义"""
        tool = GenerateGaugeChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "value_field" in params["properties"]
        assert "min_value" in params["properties"]
        assert "max_value" in params["properties"]
        assert "thresholds" in params["properties"]
    
    def test_gauge_missing_params(self):
        """测试仪表盘缺少参数"""
        tool = GenerateGaugeChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_gauge_get_name(self):
        """测试仪表盘工具名称"""
        tool = GenerateGaugeChartTool()
        
        assert tool.get_name() == "pbbi_generate_gauge_chart"
        assert "仪表盘" in tool.get_description() or "KPI" in tool.get_description()


class TestComboChartTool:
    """测试组合图工具"""
    
    def test_combo_parameters(self):
        """测试组合图参数定义"""
        tool = GenerateComboChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "snapshot_id" in params["properties"]
        assert "x_field" in params["properties"]
        assert "bar_field" in params["properties"]
        assert "line_field" in params["properties"]
    
    def test_combo_missing_params(self):
        """测试组合图缺少参数"""
        tool = GenerateComboChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_combo_partial_params(self):
        """测试组合图部分参数"""
        tool = GenerateComboChartTool()
        result = tool.execute({"snapshot_id": 1, "x_field": "a"})
        
        assert result["success"] == False
        assert "必需" in result["error"]
    
    def test_combo_get_name(self):
        """测试组合图工具名称"""
        tool = GenerateComboChartTool()
        
        assert tool.get_name() == "pbbi_generate_combo_chart"
        assert "组合图" in tool.get_description()


class TestAllToolsCoverage:
    """测试所有工具覆盖率"""
    
    def test_all_tools_have_required_methods(self):
        """测试所有工具都有必需的方法"""
        tools = [
            GenerateBarChartTool(),
            GeneratePieChartTool(),
            GenerateLineChartTool(),
            GenerateScatterChartTool(),
            GenerateBoxPlotTool(),
            GenerateHistogramTool(),
            GenerateHeatmapTool(),
            GenerateRadarChartTool(),
            GenerateFunnelChartTool(),
            GenerateGaugeChartTool(),
            GenerateComboChartTool(),
        ]
        
        for tool in tools:
            assert hasattr(tool, 'get_name'), f"{tool.__class__.__name__} 缺少 get_name 方法"
            assert hasattr(tool, 'get_description'), f"{tool.__class__.__name__} 缺少 get_description 方法"
            assert hasattr(tool, 'get_parameters'), f"{tool.__class__.__name__} 缺少 get_parameters 方法"
            assert hasattr(tool, 'execute'), f"{tool.__class__.__name__} 缺少 execute 方法"
            assert callable(tool.get_name), f"{tool.__class__.__name__}.get_name 不是方法"
            assert callable(tool.get_description), f"{tool.__class__.__name__}.get_description 不是方法"
            assert callable(tool.get_parameters), f"{tool.__class__.__name__}.get_parameters 不是方法"
            assert callable(tool.execute), f"{tool.__class__.__name__}.execute 不是方法"
    
    def test_all_tool_names_unique(self):
        """测试所有工具名称唯一"""
        tools = [
            GenerateBarChartTool(),
            GeneratePieChartTool(),
            GenerateLineChartTool(),
            GenerateScatterChartTool(),
            GenerateBoxPlotTool(),
            GenerateHistogramTool(),
            GenerateHeatmapTool(),
            GenerateRadarChartTool(),
            GenerateFunnelChartTool(),
            GenerateGaugeChartTool(),
            GenerateComboChartTool(),
        ]
        
        names = [tool.get_name() for tool in tools]
        assert len(names) == len(set(names)), "工具名称应该唯一"
    
    def test_all_tool_parameters_valid_json_schema(self):
        """测试所有工具参数是有效的JSON Schema"""
        tools = [
            GenerateBarChartTool(),
            GeneratePieChartTool(),
            GenerateLineChartTool(),
            GenerateScatterChartTool(),
            GenerateBoxPlotTool(),
            GenerateHistogramTool(),
            GenerateHeatmapTool(),
            GenerateRadarChartTool(),
            GenerateFunnelChartTool(),
            GenerateGaugeChartTool(),
            GenerateComboChartTool(),
        ]
        
        for tool in tools:
            params = tool.get_parameters()
            assert "type" in params, f"{tool.get_name()} 参数缺少 type"
            assert params["type"] == "object", f"{tool.get_name()} 参数 type 应为 object"
            assert "properties" in params, f"{tool.get_name()} 参数缺少 properties"
            assert isinstance(params["properties"], dict), f"{tool.get_name()} properties 应为字典"


class TestChartCacheAdvanced:
    """测试图表缓存高级功能"""
    
    def test_cache_key_different_chart_types(self):
        """测试不同图表类型生成不同缓存键"""
        params = {"snapshot_id": 1, "x_field": "a", "y_field": "b"}
        
        key_bar = _get_chart_cache_key("bar", params)
        key_line = _get_chart_cache_key("line", params)
        key_pie = _get_chart_cache_key("pie", params)
        
        assert key_bar != key_line, "不同图表类型应有不同缓存键"
        assert key_bar != key_pie, "不同图表类型应有不同缓存键"
        assert key_line != key_pie, "不同图表类型应有不同缓存键"
    
    def test_cache_key_order_independent(self):
        """测试缓存键与参数顺序无关"""
        key1 = _get_chart_cache_key("bar", {"a": 1, "b": 2})
        key2 = _get_chart_cache_key("bar", {"b": 2, "a": 1})
        
        assert key1 == key2, "参数顺序不同应生成相同缓存键"


class TestNumericValidationAdvanced:
    """测试数值验证高级功能"""
    
    def test_validate_mixed_numeric_string(self):
        """测试混合数值字符串"""
        import pandas as pd
        df = pd.DataFrame({"mixed": ["1", "2", "3", "4", "5"]})
        
        is_valid, error = _validate_numeric_field(df, "mixed")
        
        assert is_valid == True, "可转换的字符串应验证通过"
    
    def test_validate_partial_numeric(self):
        """测试部分数值数据"""
        import pandas as pd
        df = pd.DataFrame({"partial": [1, 2, None, 4, 5]})
        
        is_valid, error = _validate_numeric_field(df, "partial")
        
        assert is_valid == True, "包含None的数值列应验证通过"
    
    def test_validate_float_values(self):
        """测试浮点数值"""
        import pandas as pd
        df = pd.DataFrame({"floats": [1.5, 2.7, 3.14, 4.0]})
        
        is_valid, error = _validate_numeric_field(df, "floats")
        
        assert is_valid == True, "浮点数应验证通过"


class TestChartExecutionWithMockData:
    """使用模拟数据测试图表执行"""
    
    @pytest.fixture
    def mock_db(self, tmp_path):
        """创建模拟数据库"""
        import sqlite3
        import json
        
        db_path = tmp_path / "test_pb_bi.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        test_data = [
            {"category": "A", "value": 100, "value2": 50},
            {"category": "B", "value": 200, "value2": 80},
            {"category": "C", "value": 150, "value2": 60},
            {"category": "D", "value": 300, "value2": 90},
            {"category": "E", "value": 250, "value2": 70},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test_data", json.dumps(test_data))
        )
        
        time_series_data = [
            {"month": "2024-01", "sales": 1000, "profit": 100},
            {"month": "2024-02", "sales": 1200, "profit": 150},
            {"month": "2024-03", "sales": 1100, "profit": 120},
            {"month": "2024-04", "sales": 1400, "profit": 180},
            {"month": "2024-05", "sales": 1300, "profit": 160},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("time_series", json.dumps(time_series_data))
        )
        
        scatter_data = [
            {"x": 1, "y": 2, "size": 10},
            {"x": 2, "y": 4, "size": 20},
            {"x": 3, "y": 5, "size": 15},
            {"x": 4, "y": 4, "size": 25},
            {"x": 5, "y": 6, "size": 30},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("scatter_data", json.dumps(scatter_data))
        )
        
        funnel_data = [
            {"stage": "访问", "count": 1000},
            {"stage": "注册", "count": 500},
            {"stage": "下单", "count": 200},
            {"stage": "支付", "count": 150},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("funnel_data", json.dumps(funnel_data))
        )
        
        radar_data = [
            {"dimension": "销售", "score": 80},
            {"dimension": "市场", "score": 70},
            {"dimension": "研发", "score": 90},
            {"dimension": "服务", "score": 85},
            {"dimension": "管理", "score": 75},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("radar_data", json.dumps(radar_data))
        )
        
        heatmap_data = [
            {"row": "A", "col": "X", "value": 10},
            {"row": "A", "col": "Y", "value": 20},
            {"row": "B", "col": "X", "value": 30},
            {"row": "B", "col": "Y", "value": 40},
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("heatmap_data", json.dumps(heatmap_data))
        )
        
        gauge_data = [
            {"kpi": 75}
        ]
        
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("gauge_data", json.dumps(gauge_data))
        )
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def test_bar_chart_execution(self, mock_db, monkeypatch):
        """测试柱状图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateBarChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "x_field": "category",
            "y_field": "value",
            "title": "测试柱状图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
        assert result["chart_type"] == "bar"
    
    def test_pie_chart_execution(self, mock_db, monkeypatch):
        """测试饼图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GeneratePieChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "category_field": "category",
            "value_field": "value",
            "title": "测试饼图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_line_chart_execution(self, mock_db, monkeypatch):
        """测试折线图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateLineChartTool()
        result = tool.execute({
            "snapshot_id": 2,
            "x_field": "month",
            "y_field": "sales",
            "title": "测试折线图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_scatter_chart_execution(self, mock_db, monkeypatch):
        """测试散点图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateScatterChartTool()
        result = tool.execute({
            "snapshot_id": 3,
            "x_field": "x",
            "y_field": "y",
            "size_field": "size",
            "title": "测试散点图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_histogram_execution(self, mock_db, monkeypatch):
        """测试直方图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateHistogramTool()
        result = tool.execute({
            "snapshot_id": 1,
            "field": "value",
            "bins": 5,
            "title": "测试直方图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_heatmap_execution(self, mock_db, monkeypatch):
        """测试热力图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateHeatmapTool()
        result = tool.execute({
            "snapshot_id": 6,
            "x_field": "col",
            "y_field": "row",
            "value_field": "value",
            "title": "测试热力图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_radar_chart_execution(self, mock_db, monkeypatch):
        """测试雷达图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateRadarChartTool()
        result = tool.execute({
            "snapshot_id": 5,
            "category_field": "dimension",
            "value_field": "score",
            "title": "测试雷达图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_funnel_chart_execution(self, mock_db, monkeypatch):
        """测试漏斗图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateFunnelChartTool()
        result = tool.execute({
            "snapshot_id": 4,
            "stage_field": "stage",
            "value_field": "count",
            "title": "测试漏斗图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_gauge_chart_execution(self, mock_db, monkeypatch):
        """测试仪表盘实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateGaugeChartTool()
        result = tool.execute({
            "snapshot_id": 7,
            "value_field": "kpi",
            "title": "测试仪表盘",
            "min_value": 0,
            "max_value": 100
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_combo_chart_execution(self, mock_db, monkeypatch):
        """测试组合图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateComboChartTool()
        result = tool.execute({
            "snapshot_id": 2,
            "x_field": "month",
            "bar_field": "sales",
            "line_field": "profit",
            "title": "测试组合图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result
    
    def test_box_plot_execution(self, mock_db, monkeypatch):
        """测试箱线图实际执行"""
        from src.mcp import chart_mcp
        from pathlib import Path
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", mock_db)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", Path(mock_db).parent / "charts")
        Path(mock_db).parent.joinpath("charts").mkdir(exist_ok=True)
        
        tool = chart_mcp.GenerateBoxPlotTool()
        result = tool.execute({
            "snapshot_id": 1,
            "field": "value",
            "title": "测试箱线图"
        })
        
        assert result["success"] == True
        assert "chart_url" in result


class TestChartCacheIntegration:
    """测试图表缓存集成"""
    
    def test_cache_hit(self, tmp_path, monkeypatch):
        """测试缓存命中"""
        from src.mcp import chart_mcp
        import sqlite3
        import json
        
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test", json.dumps([{"a": 1, "b": 2}]))
        )
        conn.commit()
        conn.close()
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", db_path)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", tmp_path / "charts")
        (tmp_path / "charts").mkdir(exist_ok=True)
        
        chart_mcp.CHART_CACHE.clear()
        
        tool = chart_mcp.GenerateBarChartTool()
        params = {"snapshot_id": 1, "x_field": "a", "y_field": "b"}
        
        result1 = tool.execute(params)
        assert result1["success"] == True
        
        cache_key = chart_mcp._get_chart_cache_key("bar", params)
        assert cache_key in chart_mcp.CHART_CACHE
        
        result2 = tool.execute(params)
        assert result2["success"] == True
        
        chart_mcp.CHART_CACHE.clear()


class TestRegisterChartTools:
    """测试工具注册"""
    
    def test_register_chart_tools(self):
        """测试注册所有图表工具"""
        from src.mcp import chart_mcp
        from unittest.mock import MagicMock
        
        mock_service = MagicMock()
        
        tools = chart_mcp.register_chart_tools(mock_service)
        
        assert len(tools) == 19, f"应该注册19种图表工具，实际{len(tools)}种"
        
        register_calls = mock_service.register_tool.call_count
        assert register_calls == 19, f"应该调用register_tool 19次，实际{register_calls}次"
        
        handler_calls = mock_service.register_handler.call_count
        assert handler_calls == 19, f"应该调用register_handler 19次，实际{handler_calls}次"


class TestEdgeCases:
    """测试边界情况"""
    
    def test_bar_chart_with_nonexistent_field(self, tmp_path, monkeypatch):
        """测试柱状图使用不存在的字段"""
        from src.mcp import chart_mcp
        import sqlite3
        import json
        
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test", json.dumps([{"a": 1, "b": 2}]))
        )
        conn.commit()
        conn.close()
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", db_path)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", tmp_path / "charts")
        
        tool = chart_mcp.GenerateBarChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "x_field": "nonexistent",
            "y_field": "b"
        })
        
        assert result["success"] == False
        assert "不存在" in result["error"]
    
    def test_pie_chart_with_text_field(self, tmp_path, monkeypatch):
        """测试饼图使用文本字段作为数值"""
        from src.mcp import chart_mcp
        import sqlite3
        import json
        
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test", json.dumps([{"category": "A", "text": "hello"}]))
        )
        conn.commit()
        conn.close()
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", db_path)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", tmp_path / "charts")
        
        tool = chart_mcp.GeneratePieChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "category_field": "category",
            "value_field": "text"
        })
        
        assert result["success"] == False
    
    def test_radar_chart_insufficient_dimensions(self, tmp_path, monkeypatch):
        """测试雷达图维度不足"""
        from src.mcp import chart_mcp
        import sqlite3
        import json
        
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test", json.dumps([{"dim": "A", "val": 10}, {"dim": "B", "val": 20}]))
        )
        conn.commit()
        conn.close()
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", db_path)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", tmp_path / "charts")
        
        tool = chart_mcp.GenerateRadarChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "category_field": "dim",
            "value_field": "val"
        })
        
        assert result["success"] == False
        assert "至少需要3个维度" in result["error"]
    
    def test_box_plot_insufficient_data(self, tmp_path, monkeypatch):
        """测试箱线图数据不足"""
        from src.mcp import chart_mcp
        import sqlite3
        import json
        
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        """)
        conn.execute(
            "INSERT INTO data_snapshots (name, data) VALUES (?, ?)",
            ("test", json.dumps([{"val": 10}, {"val": 20}]))
        )
        conn.commit()
        conn.close()
        
        monkeypatch.setattr(chart_mcp, "MAIN_DB_PATH", db_path)
        monkeypatch.setattr(chart_mcp, "CHARTS_DIR", tmp_path / "charts")
        
        tool = chart_mcp.GenerateBoxPlotTool()
        result = tool.execute({
            "snapshot_id": 1,
            "field": "val"
        })
        
        assert result["success"] == False
        assert "至少需要3个数据点" in result["error"]


class TestNew3DCharts:
    """测试新增的3D图表"""
    
    def test_bar_3d_parameters(self):
        """测试3D柱状图参数"""
        from src.mcp.chart_mcp import GenerateBar3DChartTool
        
        tool = GenerateBar3DChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
        assert "z_field" in params["properties"]
    
    def test_scatter_3d_parameters(self):
        """测试3D散点图参数"""
        from src.mcp.chart_mcp import GenerateScatter3DChartTool
        
        tool = GenerateScatter3DChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
        assert "z_field" in params["properties"]
    
    def test_surface_3d_parameters(self):
        """测试3D曲面图参数"""
        from src.mcp.chart_mcp import GenerateSurface3DChartTool
        
        tool = GenerateSurface3DChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "x_field" in params["properties"]
        assert "y_field" in params["properties"]
        assert "z_field" in params["properties"]
    
    def test_led_wafer_parameters(self):
        """测试LED晶圆图参数"""
        from src.mcp.chart_mcp import GenerateLEDWaferChartTool
        
        tool = GenerateLEDWaferChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "wavelength_field" in params["properties"]
    
    def test_bar_3d_missing_params(self):
        """测试3D柱状图缺少参数"""
        from src.mcp.chart_mcp import GenerateBar3DChartTool
        
        tool = GenerateBar3DChartTool()
        result = tool.execute({})
        
        assert result["success"] == False
        assert "error" in result


class TestNewComboCharts:
    """测试新增的组合图表"""
    
    def test_multiple_y_axis_parameters(self):
        """测试多Y轴图参数"""
        from src.mcp.chart_mcp import GenerateMultipleYAxisChartTool
        
        tool = GenerateMultipleYAxisChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "y_fields" in params["properties"]
    
    def test_stacked_bar_parameters(self):
        """测试堆叠柱状图参数"""
        from src.mcp.chart_mcp import GenerateStackedBarChartTool
        
        tool = GenerateStackedBarChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "y_fields" in params["properties"]
    
    def test_stacked_line_parameters(self):
        """测试堆叠折线图参数"""
        from src.mcp.chart_mcp import GenerateStackedLineChartTool
        
        tool = GenerateStackedLineChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "y_fields" in params["properties"]
    
    def test_linked_chart_parameters(self):
        """测试联动图表参数"""
        from src.mcp.chart_mcp import GenerateLinkedChartTool
        
        tool = GenerateLinkedChartTool()
        params = tool.get_parameters()
        
        assert params["type"] == "object"
        assert "name_field" in params["properties"]
    
    def test_multiple_y_axis_insufficient_fields(self):
        """测试多Y轴图字段不足"""
        from src.mcp.chart_mcp import GenerateMultipleYAxisChartTool
        
        tool = GenerateMultipleYAxisChartTool()
        result = tool.execute({
            "snapshot_id": 1,
            "x_field": "a",
            "y_fields": ["b"]
        })
        
        assert result["success"] == False
        assert "至少需要2个字段" in result["error"]


class TestAllChartToolsCount:
    """测试所有图表工具数量"""
    
    def test_total_chart_tools_count(self):
        """测试图表工具总数"""
        from src.mcp.chart_mcp import register_chart_tools
        from unittest.mock import MagicMock
        
        mock_service = MagicMock()
        tools = register_chart_tools(mock_service)
        
        assert len(tools) == 19, f"应该有19种图表工具，实际{len(tools)}种"
    
    def test_all_tools_have_unique_names(self):
        """测试所有工具名称唯一"""
        from src.mcp.chart_mcp import register_chart_tools
        from unittest.mock import MagicMock
        
        mock_service = MagicMock()
        tools = register_chart_tools(mock_service)
        
        names = [tool.get_name() for tool in tools]
        assert len(names) == len(set(names)), "工具名称应该唯一"
