"""
MingDao MCP 单元测试
测试所有MingDao MCP工具的基本功能
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.mingdao_mcp import (
    MingDaoConnectTool,
    MingDaoGetFieldsTool,
    MingDaoGetRowsTool,
    MingDaoSaveSnapshotTool,
    MingDaoListConnectionsTool,
    _mingdao_connections
)


class TestMingDaoConnectTool(unittest.TestCase):
    """MingDaoConnectTool单元测试"""

    def setUp(self):
        self.tool = MingDaoConnectTool()
        _mingdao_connections.clear()

    def test_get_name(self):
        """UT-MD-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_mingdao_connect")

    def test_get_description(self):
        """UT-MD-002: 测试工具描述"""
        desc = self.tool.get_description()
        self.assertIn("明道云", desc)
        self.assertIn("API", desc)

    def test_get_parameters(self):
        """UT-MD-003: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("appkey", params["properties"])
        self.assertIn("sign", params["properties"])
        self.assertIn("appkey", params["required"])
        self.assertIn("sign", params["required"])

    def test_execute_without_appkey(self):
        """UT-MD-004: 测试缺少appkey"""
        result = self.tool.execute({"sign": "test_sign"})
        self.assertFalse(result.get("success"))
        self.assertIn("appkey", result.get("error", ""))

    def test_execute_without_sign(self):
        """UT-MD-005: 测试缺少sign"""
        result = self.tool.execute({"appkey": "test_appkey"})
        self.assertFalse(result.get("success"))
        self.assertIn("sign", result.get("error", ""))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_execute_with_valid_credentials(self, mock_service_class):
        """UT-MD-006: 测试有效凭证"""
        mock_service = MagicMock()
        mock_service.test_connection.return_value = True
        mock_service_class.return_value = mock_service

        result = self.tool.execute({
            "appkey": "test_appkey",
            "sign": "test_sign"
        })

        self.assertTrue(result.get("success"))
        self.assertIn("connection_name", result.get("data", {}))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_execute_with_invalid_credentials(self, mock_service_class):
        """UT-MD-007: 测试无效凭证"""
        mock_service = MagicMock()
        mock_service.test_connection.return_value = False
        mock_service_class.return_value = mock_service

        result = self.tool.execute({
            "appkey": "invalid_appkey",
            "sign": "invalid_sign"
        })

        self.assertFalse(result.get("success"))


class TestMingDaoGetFieldsTool(unittest.TestCase):
    """MingDaoGetFieldsTool单元测试"""

    def setUp(self):
        self.tool = MingDaoGetFieldsTool()
        _mingdao_connections.clear()

    def test_get_name(self):
        """UT-MD-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_mingdao_get_fields")

    def test_get_parameters(self):
        """UT-MD-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("worksheet_id", params["properties"])
        self.assertIn("worksheet_id", params["required"])

    def test_execute_without_worksheet_id(self):
        """UT-MD-013: 测试缺少worksheet_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("worksheet_id", result.get("error", ""))

    def test_execute_without_connection(self):
        """UT-MD-014: 测试未建立连接"""
        result = self.tool.execute({"worksheet_id": "test_worksheet"})
        self.assertFalse(result.get("success"))
        self.assertIn("连接", result.get("error", ""))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_execute_with_inline_credentials(self, mock_service_class):
        """UT-MD-015: 测试使用内联凭证"""
        mock_service = MagicMock()
        mock_service.get_fields.return_value = {
            "success": True,
            "data": {"data": [{"fieldId": "f1", "name": "字段1", "type": "text"}]}
        }
        mock_service_class.return_value = mock_service

        result = self.tool.execute({
            "worksheet_id": "test_worksheet",
            "appkey": "test_appkey",
            "sign": "test_sign"
        })

        self.assertTrue(result.get("success"))
        self.assertIn("fields", result.get("data", {}))


class TestMingDaoGetRowsTool(unittest.TestCase):
    """MingDaoGetRowsTool单元测试"""

    def setUp(self):
        self.tool = MingDaoGetRowsTool()
        _mingdao_connections.clear()

    def test_get_name(self):
        """UT-MD-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_mingdao_get_rows")

    def test_get_parameters(self):
        """UT-MD-022: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("worksheet_id", params["properties"])
        self.assertIn("field_ids", params["properties"])
        self.assertIn("page_index", params["properties"])
        self.assertIn("page_size", params["properties"])

    def test_execute_without_worksheet_id(self):
        """UT-MD-023: 测试缺少worksheet_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_execute_with_pagination(self, mock_service_class):
        """UT-MD-024: 测试分页参数"""
        mock_service = MagicMock()
        mock_service.get_data.return_value = [
            {"rowid": "1", "name": "测试数据"}
        ]
        mock_service_class.return_value = mock_service

        result = self.tool.execute({
            "worksheet_id": "test_worksheet",
            "appkey": "test_appkey",
            "sign": "test_sign",
            "page_index": 2,
            "page_size": 50
        })

        self.assertTrue(result.get("success"))
        mock_service.get_data.assert_called_with(
            "test_worksheet",
            field_ids=None,
            page_index=2,
            page_size=50
        )


class TestMingDaoSaveSnapshotTool(unittest.TestCase):
    """MingDaoSaveSnapshotTool单元测试"""

    def setUp(self):
        self.tool = MingDaoSaveSnapshotTool()
        _mingdao_connections.clear()

    def test_get_name(self):
        """UT-MD-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_mingdao_save_snapshot")

    def test_get_parameters(self):
        """UT-MD-032: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("worksheet_id", params["required"])
        self.assertIn("snapshot_name", params["required"])

    def test_execute_without_required_params(self):
        """UT-MD-033: 测试缺少必需参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    @patch('src.mcp.mingdao_mcp.MingDaoService')
    def test_execute_with_empty_data(self, mock_service_class):
        """UT-MD-034: 测试空数据"""
        mock_service = MagicMock()
        mock_service.get_fields.return_value = {
            "success": True,
            "data": {"data": [{"fieldId": "f1", "name": "字段1"}]}
        }
        mock_service.get_data.return_value = []
        mock_service_class.return_value = mock_service

        result = self.tool.execute({
            "worksheet_id": "test_worksheet",
            "snapshot_name": "测试快照",
            "appkey": "test_appkey",
            "sign": "test_sign"
        })

        self.assertFalse(result.get("success"))
        self.assertIn("空", result.get("error", ""))


class TestMingDaoListConnectionsTool(unittest.TestCase):
    """MingDaoListConnectionsTool单元测试"""

    def setUp(self):
        self.tool = MingDaoListConnectionsTool()
        _mingdao_connections.clear()

    def test_get_name(self):
        """UT-MD-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_mingdao_list_connections")

    def test_execute_empty(self):
        """UT-MD-042: 测试空连接列表"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("data", {}).get("total"), 0)

    def test_execute_with_connections(self):
        """UT-MD-043: 测试有连接"""
        _mingdao_connections["test_conn"] = {
            "appkey": "test",
            "sign": "test",
            "base_url": "https://api.mingdao.com",
            "connected_at": "2024-01-01T00:00:00"
        }

        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("data", {}).get("total"), 1)


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def setUp(self):
        _mingdao_connections.clear()

    def test_connection_with_custom_name(self):
        """UT-MD-051: 测试自定义连接名称"""
        tool = MingDaoConnectTool()
        
        with patch('src.mcp.mingdao_mcp.MingDaoService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.test_connection.return_value = True
            mock_service_class.return_value = mock_service

            result = tool.execute({
                "appkey": "test_appkey",
                "sign": "test_sign",
                "connection_name": "custom_connection"
            })

            self.assertTrue(result.get("success"))
            self.assertEqual(result.get("data", {}).get("connection_name"), "custom_connection")

    def test_connection_override(self):
        """UT-MD-052: 测试连接覆盖"""
        tool = MingDaoConnectTool()
        
        with patch('src.mcp.mingdao_mcp.MingDaoService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.test_connection.return_value = True
            mock_service_class.return_value = mock_service

            tool.execute({
                "appkey": "appkey1",
                "sign": "sign1"
            })

            tool.execute({
                "appkey": "appkey2",
                "sign": "sign2"
            })

            self.assertEqual(_mingdao_connections["default"]["appkey"], "appkey2")


if __name__ == "__main__":
    unittest.main()
