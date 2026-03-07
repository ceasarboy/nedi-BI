import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.service import MCPService, MCPTool
from src.mcp.tools import (
    GetDataFlowsTool,
    GetDataFlowTool,
    QueryDataTool,
    GetSchemaTool,
    GetSnapshotsTool,
    GetSnapshotDataTool,
    GetDashboardsTool,
    register_all_tools
)


class TestMCPTool(unittest.TestCase):
    """MCP服务基础测试"""

    def setUp(self):
        self.service = MCPService()

    def test_register_tool(self):
        """UT-001: 测试工具注册"""
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object", "properties": {}}
        )
        self.service.register_tool(tool)
        retrieved = self.service.get_tool("test_tool")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "test_tool")

    def test_get_nonexistent_tool(self):
        """UT-002: 测试获取不存在的工具"""
        tool = self.service.get_tool("nonexistent")
        self.assertIsNone(tool)

    def test_list_tools(self):
        """UT-003: 测试列出所有工具"""
        tool1 = MCPTool(name="tool1", description="Desc1", parameters={})
        tool2 = MCPTool(name="tool2", description="Desc2", parameters={})
        self.service.register_tool(tool1)
        self.service.register_tool(tool2)
        tools = self.service.list_tools()
        self.assertEqual(len(tools), 2)

    def test_execute_tool_success(self):
        """UT-004: 测试成功执行工具"""
        tool = MCPTool(name="test_tool", description="Test", parameters={})
        self.service.register_tool(tool, lambda params: {"message": "success"})
        result = self.service.execute_tool("test_tool", {})
        self.assertTrue(result.get("success"))

    def test_execute_tool_not_found(self):
        """UT-005: 测试执行不存在的工具"""
        result = self.service.execute_tool("nonexistent", {})
        self.assertFalse(result.get("success"))


class TestDataFlowTools(unittest.TestCase):
    """数据流工具测试"""

    def test_get_dataflows_tool_info(self):
        """UT-011: 测试获取数据流工具信息"""
        tool = GetDataFlowsTool()
        self.assertEqual(tool.get_name(), "pbbi_get_dataflows")
        self.assertIn("数据流", tool.get_description())
        params = tool.get_parameters()
        self.assertIn("properties", params)
        self.assertIn("page", params["properties"])
        self.assertIn("page_size", params["properties"])

    def test_get_dataflow_tool_info(self):
        """UT-012: 测试获取单个数据流工具信息"""
        tool = GetDataFlowTool()
        self.assertEqual(tool.get_name(), "pbbi_get_dataflow")
        self.assertIn("dataflow_id", tool.get_parameters()["required"])

    def test_query_data_tool_info(self):
        """UT-013: 测试数据查询工具信息"""
        tool = QueryDataTool()
        self.assertEqual(tool.get_name(), "pbbi_query_data")
        self.assertIn("dataflow_id", tool.get_parameters()["required"])

    def test_get_dataflows_with_pagination(self):
        """UT-014: 测试分页参数"""
        tool = GetDataFlowsTool()
        result = tool.execute({"page": 1, "page_size": 10})
        self.assertIn("pagination", result)

    def test_get_dataflow_without_id(self):
        """UT-015: 测试缺少dataflow_id"""
        tool = GetDataFlowTool()
        result = tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_get_dataflow_invalid_id(self):
        """UT-016: 测试无效的dataflow_id"""
        tool = GetDataFlowTool()
        result = tool.execute({"dataflow_id": 99999})
        self.assertFalse(result.get("success"))


class TestSchemaTool(unittest.TestCase):
    """Schema工具测试"""

    def test_get_schema_tool_info(self):
        """UT-021: 测试Schema工具信息"""
        tool = GetSchemaTool()
        self.assertEqual(tool.get_name(), "pbbi_get_schema")
        self.assertIn("获取", tool.get_description())

    def test_get_all_schema(self):
        """UT-022: 测试获取所有表结构"""
        tool = GetSchemaTool()
        result = tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("schema", result)
        schema = result["schema"]
        self.assertIn("users", schema)
        self.assertIn("data_flows", schema)
        self.assertIn("field_types", schema)
        self.assertIn("data_snapshots", schema)
        self.assertIn("dashboards", schema)

    def test_get_specific_table_schema(self):
        """UT-023: 测试获取指定表结构"""
        tool = GetSchemaTool()
        result = tool.execute({"table_name": "users"})
        self.assertTrue(result.get("success"))
        self.assertIn("schema", result)
        self.assertIn("users", result["schema"])

    def test_get_nonexistent_table_schema(self):
        """UT-024: 测试获取不存在的表"""
        tool = GetSchemaTool()
        result = tool.execute({"table_name": "nonexistent_table"})
        self.assertFalse(result.get("success"))


class TestSnapshotTools(unittest.TestCase):
    """快照工具测试"""

    def test_get_snapshots_tool_info(self):
        """UT-031: 测试获取快照列表工具信息"""
        tool = GetSnapshotsTool()
        self.assertEqual(tool.get_name(), "pbbi_get_snapshots")

    def test_get_snapshots_empty(self):
        """UT-032: 测试获取快照列表"""
        tool = GetSnapshotsTool()
        result = tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("data", result)

    def test_get_snapshots_with_filter(self):
        """UT-033: 测试按数据流ID筛选"""
        tool = GetSnapshotsTool()
        result = tool.execute({"dataflow_id": 1})
        self.assertTrue(result.get("success"))

    def test_get_snapshot_data_without_id(self):
        """UT-034: 测试缺少snapshot_id"""
        tool = GetSnapshotDataTool()
        result = tool.execute({})
        self.assertFalse(result.get("success"))

    def test_get_snapshot_data_invalid_id(self):
        """UT-035: 测试无效的snapshot_id"""
        tool = GetSnapshotDataTool()
        result = tool.execute({"snapshot_id": 99999})
        self.assertFalse(result.get("success"))


class TestDashboardTools(unittest.TestCase):
    """看板工具测试"""

    def test_get_dashboards_tool_info(self):
        """UT-041: 测试获取看板工具信息"""
        tool = GetDashboardsTool()
        self.assertEqual(tool.get_name(), "pbbi_get_dashboards")

    def test_get_dashboards(self):
        """UT-042: 测试获取看板列表"""
        tool = GetDashboardsTool()
        result = tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("data", result)


class TestToolRegistration(unittest.TestCase):
    """工具注册测试"""

    def test_register_all_tools(self):
        """UT-051: 测试注册所有工具"""
        service = MCPService()
        tools = register_all_tools(service)

        self.assertEqual(len(tools), 7)

        tool_names = [t.get_name() for t in tools]
        self.assertIn("pbbi_get_dataflows", tool_names)
        self.assertIn("pbbi_get_dataflow", tool_names)
        self.assertIn("pbbi_query_data", tool_names)
        self.assertIn("pbbi_get_schema", tool_names)
        self.assertIn("pbbi_get_snapshots", tool_names)
        self.assertIn("pbbi_get_snapshot_data", tool_names)
        self.assertIn("pbbi_get_dashboards", tool_names)


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def test_empty_params(self):
        """UT-061: 测试空参数"""
        tool = GetDataFlowsTool()
        result = tool.execute({})
        self.assertTrue(result.get("success"))

    def test_negative_page(self):
        """UT-062: 测试负数页码"""
        tool = GetDataFlowsTool()
        result = tool.execute({"page": -1})
        self.assertTrue(result.get("success"))

    def test_large_page_size(self):
        """UT-063: 测试大页面大小"""
        tool = GetDataFlowsTool()
        result = tool.execute({"page_size": 10000})
        self.assertTrue(result.get("success"))

    def test_zero_page_size(self):
        """UT-064: 测试零页面大小"""
        tool = GetDataFlowsTool()
        result = tool.execute({"page_size": 0})
        self.assertTrue(result.get("success"))


if __name__ == "__main__":
    unittest.main()
