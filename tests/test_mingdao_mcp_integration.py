"""
MingDao MCP 集成测试
测试MingDao MCP与API的集成
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app
from src.mcp.mingdao_mcp import _mingdao_connections


class TestMingDaoMCPAPIIntegration(unittest.TestCase):
    """MingDao MCP API集成测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        _mingdao_connections.clear()

    def tearDown(self):
        _mingdao_connections.clear()

    def test_tool_registration(self):
        """IT-MD-001: 测试工具注册"""
        response = self.client.get(f"{self.base_url}/tools")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        tool_names = [t["name"] for t in data.get("tools", [])]

        expected_tools = [
            "pbbi_mingdao_connect",
            "pbbi_mingdao_get_fields",
            "pbbi_mingdao_get_rows",
            "pbbi_mingdao_save_snapshot",
            "pbbi_mingdao_list_connections"
        ]

        for tool in expected_tools:
            self.assertIn(tool, tool_names)

    def test_list_connections_empty(self):
        """IT-MD-002: 测试空连接列表"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_mingdao_list_connections", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        inner_data = data.get("data", {})
        if isinstance(inner_data, dict) and "data" in inner_data:
            self.assertEqual(inner_data.get("total"), 0)
        else:
            self.assertEqual(inner_data.get("total"), 0)

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_connect_via_api(self, mock_service_class):
        """IT-MD-003: 通过API连接明道云"""
        mock_service = MagicMock()
        mock_service.test_connection.return_value = True
        mock_service_class.return_value = mock_service

        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_connect",
                "params": {
                    "appkey": "test_appkey",
                    "sign": "test_sign"
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        inner_data = data.get("data", {})
        if isinstance(inner_data, dict) and "data" in inner_data:
            self.assertTrue(inner_data.get("connected"))
        else:
            self.assertTrue(inner_data.get("connected"))

    def test_get_fields_without_connection(self):
        """IT-MD-004: 未连接时获取字段"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_get_fields",
                "params": {"worksheet_id": "test_worksheet"}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))

    def test_get_rows_without_connection(self):
        """IT-MD-005: 未连接时获取数据"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_get_rows",
                "params": {"worksheet_id": "test_worksheet"}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_get_fields_with_inline_credentials(self, mock_service_class):
        """IT-MD-006: 使用内联凭证获取字段"""
        mock_service = MagicMock()
        mock_service.get_fields.return_value = {
            "success": True,
            "data": {"data": [{"fieldId": "f1", "name": "字段1", "type": "text"}]}
        }
        mock_service_class.return_value = mock_service

        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_get_fields",
                "params": {
                    "worksheet_id": "test_worksheet",
                    "appkey": "test_appkey",
                    "sign": "test_sign"
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_get_rows_with_inline_credentials(self, mock_service_class):
        """IT-MD-007: 使用内联凭证获取数据"""
        mock_service = MagicMock()
        mock_service.get_data.return_value = [
            {"rowid": "1", "name": "测试数据"}
        ]
        mock_service_class.return_value = mock_service

        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_get_rows",
                "params": {
                    "worksheet_id": "test_worksheet",
                    "appkey": "test_appkey",
                    "sign": "test_sign"
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

    def test_connect_missing_credentials(self):
        """IT-MD-008: 缺少凭证"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_connect",
                "params": {}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_connect_invalid_credentials(self, mock_service_class):
        """IT-MD-009: 无效凭证"""
        mock_service = MagicMock()
        mock_service.test_connection.return_value = False
        mock_service_class.return_value = mock_service

        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_mingdao_connect",
                "params": {
                    "appkey": "invalid_appkey",
                    "sign": "invalid_sign"
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))


class TestMingDaoMCPPerformance(unittest.TestCase):
    """MingDao MCP性能测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_list_connections_response_time(self):
        """IT-MD-010: 列出连接响应时间"""
        import time
        start = time.time()
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_mingdao_list_connections", "params": {}}
        )
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 1.0, f"响应时间超过1秒: {elapsed}")


class TestMingDaoMCPErrorHandling(unittest.TestCase):
    """MingDao MCP错误处理测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_invalid_tool_name(self):
        """IT-MD-011: 无效工具名称"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_mingdao_invalid", "params": {}}
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_tool_name(self):
        """IT-MD-012: 缺少工具名称"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"params": {}}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
