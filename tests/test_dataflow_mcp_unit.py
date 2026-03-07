"""
DataFlow MCP 单元测试
测试所有DataFlow MCP工具的基本功能
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.dataflow_mcp import (
    ListDataFlowsTool,
    GetDataFlowTool,
    DeleteDataFlowTool,
    UpdateDataFlowTool,
    GetDataFlowSnapshotsTool
)


class TestListDataFlowsTool(unittest.TestCase):
    """ListDataFlowsTool单元测试"""

    def setUp(self):
        self.tool = ListDataFlowsTool()

    def test_get_name(self):
        """UT-DF-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_list_dataflows")

    def test_get_description(self):
        """UT-DF-002: 测试工具描述"""
        desc = self.tool.get_description()
        self.assertIn("数据流", desc)

    def test_get_parameters(self):
        """UT-DF-003: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("type", params["properties"])
        self.assertIn("page", params["properties"])
        self.assertIn("page_size", params["properties"])

    def test_execute_empty_params(self):
        """UT-DF-004: 测试空参数执行"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("dataflows", result.get("data", {}))

    def test_execute_with_pagination(self):
        """UT-DF-005: 测试分页参数"""
        result = self.tool.execute({"page": 2, "page_size": 5})
        self.assertTrue(result.get("success"))
        pagination = result.get("data", {}).get("pagination", {})
        self.assertEqual(pagination.get("page"), 2)
        self.assertEqual(pagination.get("page_size"), 5)

    def test_execute_with_type_filter(self):
        """UT-DF-006: 测试类型筛选"""
        result = self.tool.execute({"type": "mingdao"})
        self.assertTrue(result.get("success"))


class TestGetDataFlowTool(unittest.TestCase):
    """GetDataFlowTool单元测试"""

    def setUp(self):
        self.tool = GetDataFlowTool()

    def test_get_name(self):
        """UT-DF-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_dataflow")

    def test_get_parameters(self):
        """UT-DF-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dataflow_id", params["properties"])
        self.assertIn("dataflow_id", params["required"])

    def test_execute_without_dataflow_id(self):
        """UT-DF-013: 测试缺少dataflow_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_dataflow_id(self):
        """UT-DF-014: 测试无效数据流ID"""
        result = self.tool.execute({"dataflow_id": 99999})
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))


class TestDeleteDataFlowTool(unittest.TestCase):
    """DeleteDataFlowTool单元测试"""

    def setUp(self):
        self.tool = DeleteDataFlowTool()

    def test_get_name(self):
        """UT-DF-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_delete_dataflow")

    def test_get_parameters(self):
        """UT-DF-022: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dataflow_id", params["properties"])
        self.assertIn("dataflow_id", params["required"])

    def test_execute_without_dataflow_id(self):
        """UT-DF-023: 测试缺少dataflow_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_dataflow_id(self):
        """UT-DF-024: 测试无效数据流ID"""
        result = self.tool.execute({"dataflow_id": 99999})
        self.assertFalse(result.get("success"))


class TestUpdateDataFlowTool(unittest.TestCase):
    """UpdateDataFlowTool单元测试"""

    def setUp(self):
        self.tool = UpdateDataFlowTool()

    def test_get_name(self):
        """UT-DF-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_update_dataflow")

    def test_get_parameters(self):
        """UT-DF-032: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dataflow_id", params["properties"])
        self.assertIn("dataflow_id", params["required"])

    def test_execute_without_dataflow_id(self):
        """UT-DF-033: 测试缺少dataflow_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_dataflow_id(self):
        """UT-DF-034: 测试无效数据流ID"""
        result = self.tool.execute({"dataflow_id": 99999, "name": "新名称"})
        self.assertFalse(result.get("success"))


class TestGetDataFlowSnapshotsTool(unittest.TestCase):
    """GetDataFlowSnapshotsTool单元测试"""

    def setUp(self):
        self.tool = GetDataFlowSnapshotsTool()

    def test_get_name(self):
        """UT-DF-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_dataflow_snapshots")

    def test_get_parameters(self):
        """UT-DF-042: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dataflow_id", params["properties"])
        self.assertIn("dataflow_id", params["required"])

    def test_execute_without_dataflow_id(self):
        """UT-DF-043: 测试缺少dataflow_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_valid_dataflow_id(self):
        """UT-DF-044: 测试有效数据流ID"""
        result = self.tool.execute({"dataflow_id": 1})
        self.assertTrue(result.get("success"))


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def test_list_negative_page(self):
        """UT-DF-051: 测试负数页码"""
        tool = ListDataFlowsTool()
        result = tool.execute({"page": -1})
        self.assertTrue(result.get("success"))

    def test_list_zero_page_size(self):
        """UT-DF-052: 测试零页面大小"""
        tool = ListDataFlowsTool()
        result = tool.execute({"page_size": 0})
        self.assertTrue(result.get("success"))

    def test_list_large_page_size(self):
        """UT-DF-053: 测试大页面大小"""
        tool = ListDataFlowsTool()
        result = tool.execute({"page_size": 10000})
        self.assertTrue(result.get("success"))


if __name__ == "__main__":
    unittest.main()
