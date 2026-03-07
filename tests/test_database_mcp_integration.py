"""
Database MCP 集成测试
测试Database MCP与API的集成
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app


class TestDatabaseMCPAPIIntegration(unittest.TestCase):
    """Database MCP API集成测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_list_snapshots_via_api(self):
        """IT-DB-001: 通过API列出快照"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_list_snapshots", "params": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("data", data)

    def test_list_snapshots_with_pagination(self):
        """IT-DB-002: 通过API分页列出快照"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_list_snapshots",
                "params": {"page": 1, "page_size": 10}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        inner_data = data.get("data", {})
        if isinstance(inner_data, dict):
            self.assertIn("pagination", inner_data)

    def test_get_snapshot_schema_invalid_id(self):
        """IT-DB-003: 获取不存在快照的Schema"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_get_snapshot_schema",
                "params": {"snapshot_id": 99999}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = data.get("data", {})
        self.assertFalse(inner_data.get("success", True))

    def test_query_snapshot_invalid_id(self):
        """IT-DB-004: 查询不存在的快照"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_query_snapshot",
                "params": {"snapshot_id": 99999}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = data.get("data", {})
        self.assertFalse(inner_data.get("success", True))

    def test_execute_sql_empty(self):
        """IT-DB-005: 执行空SQL"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_execute_sql",
                "params": {"sql": ""}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        inner_data = data.get("data", {})
        self.assertFalse(inner_data.get("success", True))

    def test_execute_sql_dangerous(self):
        """IT-DB-006: 执行危险SQL"""
        dangerous_sqls = [
            "DELETE FROM test",
            "DROP TABLE test",
            "UPDATE test SET x=1"
        ]
        for sql in dangerous_sqls:
            response = self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_execute_sql",
                    "params": {"sql": sql}
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            inner_data = data.get("data", {})
            self.assertFalse(inner_data.get("success", True), f"应该拒绝: {sql}")

    def test_create_and_delete_snapshot(self):
        """IT-DB-007: 创建和删除快照完整流程"""
        create_response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "API集成测试快照",
                    "table_name": "api_test_snapshot",
                    "fields": [
                        {"name": "name", "type": "text"},
                        {"name": "value", "type": "integer"}
                    ],
                    "data": [
                        {"name": "测试1", "value": 100},
                        {"name": "测试2", "value": 200}
                    ]
                }
            }
        )
        self.assertEqual(create_response.status_code, 200)
        create_data = create_response.json()
        self.assertTrue(create_data.get("success"), f"创建失败: {create_data}")
        
        inner_data = create_data.get("data", {})
        if isinstance(inner_data, dict):
            snapshot_id = inner_data.get("data", {}).get("snapshot_id")
        else:
            snapshot_id = inner_data.get("snapshot_id")
        
        self.assertIsNotNone(snapshot_id)

        query_response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_query_snapshot",
                "params": {"snapshot_id": snapshot_id}
            }
        )
        self.assertEqual(query_response.status_code, 200)
        query_data = query_response.json()
        self.assertTrue(query_data.get("success"))

        delete_response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_delete_snapshot",
                "params": {"snapshot_id": snapshot_id}
            }
        )
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertTrue(delete_data.get("success"))

    def test_tool_registration(self):
        """IT-DB-008: 测试工具注册"""
        response = self.client.get(f"{self.base_url}/tools")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        tool_names = [t["name"] for t in data.get("tools", [])]

        expected_tools = [
            "pbbi_list_snapshots",
            "pbbi_get_snapshot_schema",
            "pbbi_query_snapshot",
            "pbbi_execute_sql",
            "pbbi_create_snapshot_table",
            "pbbi_delete_snapshot"
        ]

        for tool in expected_tools:
            self.assertIn(tool, tool_names, f"工具 {tool} 未注册")

    def test_sql_query_with_aggregation(self):
        """IT-DB-009: 测试聚合SQL查询"""
        create_response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "聚合测试快照",
                    "table_name": "agg_test_table",
                    "fields": [
                        {"name": "category"},
                        {"name": "amount"}
                    ],
                    "data": [
                        {"category": "A", "amount": 100},
                        {"category": "B", "amount": 200},
                        {"category": "A", "amount": 150},
                        {"category": "B", "amount": 250}
                    ]
                }
            }
        )
        self.assertEqual(create_response.status_code, 200)
        create_data = create_response.json()
        
        inner_data = create_data.get("data", {})
        if isinstance(inner_data, dict):
            table_name = inner_data.get("data", {}).get("table_name")
            snapshot_id = inner_data.get("data", {}).get("snapshot_id")
        else:
            table_name = inner_data.get("table_name")
            snapshot_id = inner_data.get("snapshot_id")

        sql_response = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_execute_sql",
                "params": {
                    "sql": f"SELECT category, SUM(amount) as total FROM {table_name} GROUP BY category ORDER BY category"
                }
            }
        )
        self.assertEqual(sql_response.status_code, 200)
        sql_data = sql_response.json()
        self.assertTrue(sql_data.get("success"))

        self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_delete_snapshot",
                "params": {"snapshot_id": snapshot_id}
            }
        )


class TestDatabaseMCPPerformance(unittest.TestCase):
    """Database MCP性能测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_list_snapshots_response_time(self):
        """IT-DB-010: 列出快照响应时间"""
        import time
        start = time.time()
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_list_snapshots", "params": {}}
        )
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 1.0, f"响应时间超过1秒: {elapsed}")

    def test_execute_sql_response_time(self):
        """IT-DB-011: SQL执行响应时间"""
        import time
        start = time.time()
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_execute_sql", "params": {"sql": "SELECT 1"}}
        )
        elapsed = time.time() - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 1.0, f"响应时间超过1秒: {elapsed}")


class TestDatabaseMCPErrorHandling(unittest.TestCase):
    """Database MCP错误处理测试"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"

    def test_invalid_tool_name(self):
        """IT-DB-012: 无效工具名称"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_invalid_tool", "params": {}}
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_tool_name(self):
        """IT-DB-013: 缺少工具名称"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"params": {}}
        )
        self.assertEqual(response.status_code, 422)

    def test_malformed_params(self):
        """IT-DB-014: 格式错误的参数"""
        response = self.client.post(
            f"{self.base_url}/execute",
            json={"tool_name": "pbbi_list_snapshots", "params": "invalid"}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
