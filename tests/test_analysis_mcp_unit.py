"""
Analysis MCP 单元测试
测试所有Analysis MCP工具的基本功能
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.analysis_mcp import (
    AggregateDataTool,
    FilterDataTool,
    StatisticsTool,
    PivotTableTool,
    RecommendChartTool
)
from src.mcp.database_mcp import CreateSnapshotTableTool, DeleteSnapshotTool


class TestAggregateDataTool(unittest.TestCase):
    """AggregateDataTool单元测试"""

    def setUp(self):
        self.tool = AggregateDataTool()
        self.create_tool = CreateSnapshotTableTool()
        self.delete_tool = DeleteSnapshotTool()
        self.snapshot_ids = []

    def tearDown(self):
        for snapshot_id in self.snapshot_ids:
            self.delete_tool.execute({"snapshot_id": snapshot_id})

    def test_get_name(self):
        """UT-AN-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_aggregate_data")

    def test_get_parameters(self):
        """UT-AN-002: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("aggregations", params["properties"])
        self.assertIn("aggregations", params["required"])

    def test_execute_without_aggregations(self):
        """UT-AN-003: 测试缺少aggregations"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_function(self):
        """UT-AN-004: 测试无效聚合函数"""
        result = self.tool.execute({
            "table_name": "test_table",
            "aggregations": [{"field": "value", "function": "INVALID"}]
        })
        self.assertFalse(result.get("success"))

    def test_execute_with_valid_data(self):
        """UT-AN-005: 测试有效数据聚合"""
        create_result = self.create_tool.execute({
            "name": "聚合测试",
            "table_name": f"agg_test_{int(time.time())}",
            "fields": [{"name": "category"}, {"name": "value"}],
            "data": [
                {"category": "A", "value": 100},
                {"category": "B", "value": 200},
                {"category": "A", "value": 150}
            ]
        })
        self.assertTrue(create_result.get("success"))
        snapshot_id = create_result["data"]["snapshot_id"]
        self.snapshot_ids.append(snapshot_id)

        result = self.tool.execute({
            "snapshot_id": snapshot_id,
            "aggregations": [
                {"field": "value", "function": "SUM", "alias": "total"},
                {"field": "value", "function": "AVG", "alias": "average"}
            ],
            "group_by": ["category"]
        })
        self.assertTrue(result.get("success"))


class TestFilterDataTool(unittest.TestCase):
    """FilterDataTool单元测试"""

    def setUp(self):
        self.tool = FilterDataTool()

    def test_get_name(self):
        """UT-AN-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_filter_data")

    def test_get_parameters(self):
        """UT-AN-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("conditions", params["properties"])
        self.assertIn("conditions", params["required"])

    def test_execute_without_conditions(self):
        """UT-AN-013: 测试缺少conditions"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_operator(self):
        """UT-AN-014: 测试无效操作符"""
        result = self.tool.execute({
            "table_name": "test_table",
            "conditions": [{"field": "value", "operator": "INVALID", "value": "1"}]
        })
        self.assertFalse(result.get("success"))


class TestStatisticsTool(unittest.TestCase):
    """StatisticsTool单元测试"""

    def setUp(self):
        self.tool = StatisticsTool()

    def test_get_name(self):
        """UT-AN-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_statistics")

    def test_get_parameters(self):
        """UT-AN-022: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("field", params["properties"])
        self.assertIn("field", params["required"])

    def test_execute_without_field(self):
        """UT-AN-023: 测试缺少field"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))


class TestPivotTableTool(unittest.TestCase):
    """PivotTableTool单元测试"""

    def setUp(self):
        self.tool = PivotTableTool()

    def test_get_name(self):
        """UT-AN-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_pivot_table")

    def test_get_parameters(self):
        """UT-AN-032: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("row_field", params["properties"])
        self.assertIn("value_field", params["properties"])
        self.assertIn("row_field", params["required"])
        self.assertIn("value_field", params["required"])

    def test_execute_without_required_params(self):
        """UT-AN-033: 测试缺少必需参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))


class TestRecommendChartTool(unittest.TestCase):
    """RecommendChartTool单元测试"""

    def setUp(self):
        self.tool = RecommendChartTool()

    def test_get_name(self):
        """UT-AN-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_recommend_chart")

    def test_get_parameters(self):
        """UT-AN-042: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("fields", params["properties"])
        self.assertIn("fields", params["required"])

    def test_execute_without_fields(self):
        """UT-AN-043: 测试缺少fields"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def test_aggregate_empty_data(self):
        """UT-AN-051: 测试空数据聚合"""
        tool = AggregateDataTool()
        result = tool.execute({
            "table_name": "nonexistent_table",
            "aggregations": [{"field": "value", "function": "SUM"}]
        })
        self.assertFalse(result.get("success"))

    def test_filter_empty_conditions(self):
        """UT-AN-052: 测试空条件筛选"""
        tool = FilterDataTool()
        result = tool.execute({
            "table_name": "test_table",
            "conditions": []
        })
        self.assertFalse(result.get("success"))

    def test_statistics_nonexistent_table(self):
        """UT-AN-053: 测试不存在表的统计"""
        tool = StatisticsTool()
        result = tool.execute({
            "table_name": "nonexistent_table",
            "field": "value"
        })
        self.assertFalse(result.get("success"))


if __name__ == "__main__":
    unittest.main()
