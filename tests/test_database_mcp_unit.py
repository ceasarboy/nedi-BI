"""
Database MCP 单元测试
测试所有Database MCP工具的基本功能
"""

import unittest
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.database_mcp import (
    ListSnapshotsTool,
    GetSnapshotSchemaTool,
    QuerySnapshotTool,
    ExecuteSQLTool,
    CreateSnapshotTableTool,
    DeleteSnapshotTool,
    _get_main_db_connection
)


class TestListSnapshotsTool(unittest.TestCase):
    """ListSnapshotsTool单元测试"""

    def setUp(self):
        self.tool = ListSnapshotsTool()

    def test_get_name(self):
        """UT-DB-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_list_snapshots")

    def test_get_description(self):
        """UT-DB-002: 测试工具描述"""
        desc = self.tool.get_description()
        self.assertIn("快照", desc)
        self.assertIn("SQLite", desc)

    def test_get_parameters(self):
        """UT-DB-003: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("properties", params)
        self.assertIn("page", params["properties"])
        self.assertIn("page_size", params["properties"])
        self.assertIn("data_flow_id", params["properties"])

    def test_execute_empty_params(self):
        """UT-DB-004: 测试空参数执行"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("data", result)
        self.assertIn("pagination", result)

    def test_execute_with_pagination(self):
        """UT-DB-005: 测试分页参数"""
        result = self.tool.execute({"page": 2, "page_size": 5})
        self.assertTrue(result.get("success"))
        pagination = result.get("pagination", {})
        self.assertEqual(pagination.get("page"), 2)
        self.assertEqual(pagination.get("page_size"), 5)

    def test_execute_with_dataflow_filter(self):
        """UT-DB-006: 测试数据流筛选"""
        result = self.tool.execute({"data_flow_id": 999})
        self.assertTrue(result.get("success"))


class TestGetSnapshotSchemaTool(unittest.TestCase):
    """GetSnapshotSchemaTool单元测试"""

    def setUp(self):
        self.tool = GetSnapshotSchemaTool()

    def test_get_name(self):
        """UT-DB-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_get_snapshot_schema")

    def test_get_parameters(self):
        """UT-DB-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("snapshot_id", params["properties"])
        self.assertIn("snapshot_id", params["required"])

    def test_execute_without_params(self):
        """UT-DB-013: 测试缺少参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_execute_with_invalid_snapshot_id(self):
        """UT-DB-014: 测试无效快照ID"""
        result = self.tool.execute({"snapshot_id": 99999})
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))


class TestQuerySnapshotTool(unittest.TestCase):
    """QuerySnapshotTool单元测试"""

    def setUp(self):
        self.tool = QuerySnapshotTool()

    def test_get_name(self):
        """UT-DB-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_query_snapshot")

    def test_get_parameters(self):
        """UT-DB-022: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("fields", params["properties"])
        self.assertIn("where", params["properties"])
        self.assertIn("order_by", params["properties"])
        self.assertIn("limit", params["properties"])

    def test_execute_without_params(self):
        """UT-DB-023: 测试缺少参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_execute_with_invalid_snapshot_id(self):
        """UT-DB-024: 测试无效快照ID"""
        result = self.tool.execute({"snapshot_id": 99999})
        self.assertFalse(result.get("success"))


class TestExecuteSQLTool(unittest.TestCase):
    """ExecuteSQLTool单元测试"""

    def setUp(self):
        self.tool = ExecuteSQLTool()

    def test_get_name(self):
        """UT-DB-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_execute_sql")

    def test_get_parameters(self):
        """UT-DB-032: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("sql", params["properties"])
        self.assertIn("limit", params["properties"])
        self.assertIn("sql", params["required"])

    def test_execute_empty_sql(self):
        """UT-DB-033: 测试空SQL"""
        result = self.tool.execute({"sql": ""})
        self.assertFalse(result.get("success"))
        self.assertIn("空", result.get("error", ""))

    def test_execute_non_select_sql(self):
        """UT-DB-034: 测试非SELECT语句"""
        result = self.tool.execute({"sql": "DROP TABLE test"})
        self.assertFalse(result.get("success"))
        self.assertIn("SELECT", result.get("error", ""))

    def test_execute_dangerous_sql(self):
        """UT-DB-035: 测试危险SQL语句"""
        dangerous_sqls = [
            "DELETE FROM test",
            "UPDATE test SET a=1",
            "INSERT INTO test VALUES (1)",
            "DROP TABLE test",
            "ALTER TABLE test ADD COLUMN x"
        ]
        for sql in dangerous_sqls:
            result = self.tool.execute({"sql": sql})
            self.assertFalse(result.get("success"), f"应该拒绝: {sql}")

    def test_execute_invalid_sql(self):
        """UT-DB-036: 测试无效SQL语法"""
        result = self.tool.execute({"sql": "SELECT * FROM nonexistent_table_xyz"})
        self.assertFalse(result.get("success"))

    def test_execute_with_limit(self):
        """UT-DB-037: 测试LIMIT参数"""
        result = self.tool.execute({"sql": "SELECT 1", "limit": 10})
        self.assertTrue(result.get("success"))


class TestCreateSnapshotTableTool(unittest.TestCase):
    """CreateSnapshotTableTool单元测试"""

    def setUp(self):
        self.tool = CreateSnapshotTableTool()

    def test_get_name(self):
        """UT-DB-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_create_snapshot_table")

    def test_get_parameters(self):
        """UT-DB-042: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("name", params["properties"])
        self.assertIn("fields", params["properties"])
        self.assertIn("data", params["properties"])

    def test_execute_without_required_params(self):
        """UT-DB-043: 测试缺少必需参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_execute_with_minimal_params(self):
        """UT-DB-044: 测试最小参数"""
        result = self.tool.execute({
            "name": f"测试快照_{int(time.time())}",
            "fields": [],
            "data": []
        })
        self.assertTrue(result.get("success"))
        self.assertIn("snapshot_id", result.get("data", {}))


class TestDeleteSnapshotTool(unittest.TestCase):
    """DeleteSnapshotTool单元测试"""

    def setUp(self):
        self.tool = DeleteSnapshotTool()

    def test_get_name(self):
        """UT-DB-051: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_delete_snapshot")

    def test_get_parameters(self):
        """UT-DB-052: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("snapshot_id", params["properties"])
        self.assertIn("snapshot_id", params["required"])

    def test_execute_without_snapshot_id(self):
        """UT-DB-053: 测试缺少快照ID"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_execute_with_invalid_snapshot_id(self):
        """UT-DB-054: 测试无效快照ID"""
        result = self.tool.execute({"snapshot_id": 99999})
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))


class TestDatabaseMCPIntegration(unittest.TestCase):
    """Database MCP内部集成测试"""

    def setUp(self):
        self.create_tool = CreateSnapshotTableTool()
        self.list_tool = ListSnapshotsTool()
        self.query_tool = QuerySnapshotTool()
        self.schema_tool = GetSnapshotSchemaTool()
        self.delete_tool = DeleteSnapshotTool()
        self.sql_tool = ExecuteSQLTool()

    def test_full_lifecycle(self):
        """UT-DB-061: 测试完整生命周期（创建-查询-删除）"""
        create_result = self.create_tool.execute({
            "name": f"生命周期测试_{int(time.time())}",
            "data_flow_id": 1,
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "age", "type": "integer"}
            ],
            "data": [
                {"name": "张三", "age": 25},
                {"name": "李四", "age": 30}
            ]
        })
        self.assertTrue(create_result.get("success"), f"创建失败: {create_result}")
        snapshot_id = create_result["data"]["snapshot_id"]

        list_result = self.list_tool.execute({})
        self.assertTrue(list_result.get("success"))
        snapshot_ids = [s["id"] for s in list_result["data"]]
        self.assertIn(snapshot_id, snapshot_ids)

        query_result = self.query_tool.execute({
            "snapshot_id": snapshot_id,
            "limit": 10
        })
        self.assertTrue(query_result.get("success"))
        self.assertEqual(query_result.get("total"), 2)

        schema_result = self.schema_tool.execute({
            "snapshot_id": snapshot_id
        })
        self.assertTrue(schema_result.get("success"))
        self.assertIn("columns", schema_result["data"])

        delete_result = self.delete_tool.execute({
            "snapshot_id": snapshot_id
        })
        self.assertTrue(delete_result.get("success"))

        list_result2 = self.list_tool.execute({})
        snapshot_ids2 = [s["id"] for s in list_result2["data"]]
        self.assertNotIn(snapshot_id, snapshot_ids2)


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def setUp(self):
        self.tool = ListSnapshotsTool()

    def test_negative_page(self):
        """UT-DB-071: 测试负数页码"""
        result = self.tool.execute({"page": -1})
        self.assertTrue(result.get("success"))

    def test_zero_page_size(self):
        """UT-DB-072: 测试零页面大小"""
        result = self.tool.execute({"page_size": 0})
        self.assertTrue(result.get("success"))

    def test_large_page_size(self):
        """UT-DB-073: 测试大页面大小"""
        result = self.tool.execute({"page_size": 10000})
        self.assertTrue(result.get("success"))


if __name__ == "__main__":
    unittest.main()
