"""
Dashboard MCP 单元测试
测试所有Dashboard MCP工具的基本功能
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.dashboard_mcp import (
    ListDashboardsTool,
    GetDashboardTool,
    CreateDashboardTool,
    DeleteDashboardTool,
    UpdateDashboardTool,
    GetCurrentuserTool,
    GetUserResourcesTool
)


class TestListDashboardsTool(unittest.TestCase):
    """ListDashboardsTool单元测试"""

    def setUp(self):
        self.tool = ListDashboardsTool()

    def test_get_name(self):
        """UT-DB-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_list_dashboards")

    def test_get_description(self):
        """UT-DB-002: 测试工具描述"""
        desc = self.tool.get_description()
        self.assertIn("看板", desc)

    def test_get_parameters(self):
        """UT-DB-003: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("page", params["properties"])
        self.assertIn("page_size", params["properties"])

    def test_execute_with_pagination(self):
        """UT-DB-004: 测试分页参数"""
        result = self.tool.execute({"page": 2, "page_size": 5})
        self.assertTrue(result.get("success"))
        pagination = result.get("data", {}).get("pagination", {})
        self.assertEqual(pagination.get("page"), 2)
        self.assertEqual(pagination.get("page_size"), 5)


class TestGetDashboardTool(unittest.TestCase):
    """GetDashboardTool单元测试"""

    def setUp(self):
        self.tool = GetDashboardTool()

    def test_get_name(self):
        """UT-DB-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_dashboard")

    def test_get_parameters(self):
        """UT-DB-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dashboard_id", params["properties"])
        self.assertIn("dashboard_id", params["required"])

    def test_execute_without_dashboard_id(self):
        """UT-DB-013: 测试缺少dashboard_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_dashboard_id(self):
        """UT-DB-014: 测试无效看板ID"""
        result = self.tool.execute({"dashboard_id": 99999})
        self.assertFalse(result.get("success"))


class TestCreateDashboardTool(unittest.TestCase):
    """CreateDashboardTool单元测试"""

    def setUp(self):
        self.tool = CreateDashboardTool()

    def test_get_name(self):
        """UT-DB-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_create_dashboard")

    def test_get_parameters(self):
        """UT-DB-022: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("name", params["properties"])
        self.assertIn("name", params["required"])
        self.assertIn("chart_type", params["required"])

    def test_execute_without_name(self):
        """UT-DB-023: 测试缺少name"""
        result = self.tool.execute({"chart_type": "line"})
        self.assertFalse(result.get("success"))


class TestDeleteDashboardTool(unittest.TestCase):
    """DeleteDashboardTool单元测试"""

    def setUp(self):
        self.tool = DeleteDashboardTool()

    def test_get_name(self):
        """UT-DB-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_delete_dashboard")

    def test_get_parameters(self):
        """UT-DB-032: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dashboard_id", params["properties"])
        self.assertIn("dashboard_id", params["required"])

    def test_execute_without_dashboard_id(self):
        """UT-DB-033: 测试缺少dashboard_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_with_invalid_dashboard_id(self):
        """UT-DB-034: 测试无效看板ID"""
        result = self.tool.execute({"dashboard_id": 99999})
        self.assertFalse(result.get("success"))


class TestUpdateDashboardTool(unittest.TestCase):
    """UpdateDashboardTool单元测试"""

    def setUp(self):
        self.tool = UpdateDashboardTool()

    def test_get_name(self):
        """UT-DB-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_update_dashboard")

    def test_get_parameters(self):
        """UT-DB-042: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dashboard_id", params["properties"])
        self.assertIn("dashboard_id", params["required"])

    def test_execute_without_dashboard_id(self):
        """UT-DB-043: 测试缺少dashboard_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))


class TestGetCurrentuserTool(unittest.TestCase):
    """GetCurrentuserTool单元测试"""

    def setUp(self):
        self.tool = GetCurrentuserTool()

    def test_get_name(self):
        """UT-DB-051: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_current_user")

    def test_execute(self):
        """UT-DB-052: 测试执行"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("user_id", result.get("data", {}))


class TestGetUserResourcesTool(unittest.TestCase):
    """GetUserResourcesTool单元测试"""

    def setUp(self):
        self.tool = GetUserResourcesTool()

    def test_get_name(self):
        """UT-DB-061: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_user_resources")

    def test_execute(self):
        """UT-DB-062: 测试执行"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("dataflows", result.get("data", {}))
        self.assertIn("snapshots", result.get("data", {}))
        self.assertIn("dashboards", result.get("data", {}))


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def test_list_negative_page(self):
        """UT-DB-071: 测试负数页码"""
        tool = ListDashboardsTool()
        result = tool.execute({"page": -1})
        self.assertTrue(result.get("success"))

    def test_list_zero_page_size(self):
        """UT-DB-072: 测试零页面大小"""
        tool = ListDashboardsTool()
        result = tool.execute({"page_size": 0})
        self.assertTrue(result.get("success"))

    def test_create_and_delete_dashboard(self):
        """UT-DB-073: 测试创建和删除看板"""
        create_tool = CreateDashboardTool()
        result = create_tool.execute({
            "name": "测试看板",
            "chart_type": "bar"
        })
        self.assertTrue(result.get("success"))
        
        if result.get("success"):
            dashboard_id = result["data"]["id"]
            delete_tool = DeleteDashboardTool()
            delete_result = delete_tool.execute({"dashboard_id": dashboard_id})
            self.assertTrue(delete_result.get("success"))


if __name__ == "__main__":
    unittest.main()
