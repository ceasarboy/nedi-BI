import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app


class TestMCPIntegration(unittest.TestCase):
    """MCP API集成测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_health_check(self):
        """IT-001: 测试健康检查"""
        response = self.client.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_list_tools(self):
        """IT-002: 测试列出所有工具"""
        response = self.client.get(f"{self.base_url}/tools")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tools", data)
        self.assertIn("count", data)
        self.assertGreaterEqual(data["count"], 7)

    def test_list_tools_contains_required(self):
        """IT-003: 测试工具列表包含必需工具"""
        response = self.client.get(f"{self.base_url}/tools")
        data = response.json()
        tool_names = [t["name"] for t in data["tools"]]

        required_tools = [
            "pbbi_get_dataflows",
            "pbbi_get_dataflow",
            "pbbi_query_data",
            "pbbi_get_schema",
            "pbbi_get_snapshots",
            "pbbi_get_snapshot_data",
            "pbbi_get_dashboards"
        ]

        for tool in required_tools:
            self.assertIn(tool, tool_names)

    def test_get_tool_info(self):
        """IT-004: 测试获取单个工具信息"""
        response = self.client.get(f"{self.base_url}/tools/pbbi_get_dataflows")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "pbbi_get_dataflows")
        self.assertIn("description", data)
        self.assertIn("parameters", data)

    def test_get_nonexistent_tool(self):
        """IT-005: 测试获取不存在的工具"""
        response = self.client.get(f"{self.base_url}/tools/nonexistent_tool")
        self.assertEqual(response.status_code, 404)

    def test_execute_get_dataflows(self):
        """IT-006: 测试执行获取数据流列表"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_dataflows", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)

    def test_execute_get_schema(self):
        """IT-007: 测试执行获取Schema"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_schema", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)
        inner_data = data["data"]
        if isinstance(inner_data, dict) and "schema" in inner_data:
            self.assertIn("schema", inner_data)

    def test_execute_get_snapshots(self):
        """IT-008: 测试执行获取快照列表"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_snapshots", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)

    def test_execute_get_dashboards(self):
        """IT-009: 测试执行获取看板列表"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_dashboards", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)

    def test_execute_nonexistent_tool(self):
        """IT-010: 测试执行不存在的工具"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "nonexistent_tool", "params": {}}
        )
        self.assertEqual(response.status_code, 400)

    def test_execute_with_pagination(self):
        """IT-011: 测试分页参数"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_dataflows", "params": {"page": 1, "page_size": 5}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        inner_data = data["data"]
        if isinstance(inner_data, dict) and "pagination" in inner_data:
            self.assertEqual(inner_data["pagination"]["page"], 1)
            self.assertEqual(inner_data["pagination"]["page_size"], 5)

    def test_execute_get_specific_table(self):
        """IT-012: 测试获取指定表Schema"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_schema", "params": {"table_name": "users"}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)

    def test_execute_get_invalid_table(self):
        """IT-013: 测试获取不存在的表"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_schema", "params": {"table_name": "invalid_table"}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = data.get("data", {})
        self.assertFalse(inner_data.get("success", True))

    def test_api_response_format(self):
        """IT-014: 测试API响应格式"""
        response = self.client.get(f"{self.base_url}/tools")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data["tools"], list)
        self.assertIsInstance(data["count"], int)

        if data["tools"]:
            tool = data["tools"][0]
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("parameters", tool)


class TestMCPPerformance(unittest.TestCase):
    """MCP性能测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_response_time_list_tools(self):
        """IT-015: 测试列出工具响应时间"""
        import time
        start = time.time()
        response = self.client.get(f"{self.base_url}/tools")
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 1.0, f"响应时间超过1秒: {elapsed}")

    def test_response_time_execute(self):
        """IT-016: 测试执行工具响应时间"""
        import time
        start = time.time()
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_get_schema", "params": {}}
        )
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 2.0, f"响应时间超过2秒: {elapsed}")


class TestMCPAuthentication(unittest.TestCase):
    """MCP认证测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_public_endpoints_accessible(self):
        """IT-017: 测试公共端点可访问"""
        response = self.client.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"{self.base_url}/tools")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
