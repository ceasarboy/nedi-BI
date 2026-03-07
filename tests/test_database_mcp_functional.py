"""
Database MCP 功能测试
测试用户场景和完整功能流程
"""

import unittest
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app


def get_unique_id():
    return int(time.time() * 1000000)


class TestUserScenario1_DataImportAndQuery(unittest.TestCase):
    """用户场景1: 导入数据并查询"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        self.snapshot_ids = []

    def tearDown(self):
        for snapshot_id in self.snapshot_ids:
            self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_delete_snapshot",
                    "params": {"snapshot_id": snapshot_id}
                }
            )

    def test_import_and_query_flow(self):
        """FT-DB-001: 完整的数据导入和查询流程"""
        unique_id = get_unique_id()
        
        create_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "销售数据",
                    "table_name": f"sales_data_{unique_id}",
                    "data_flow_id": 1,
                    "worksheet_id": "worksheet_001",
                    "fields": [
                        {"name": "product", "type": "text"},
                        {"name": "region", "type": "text"},
                        {"name": "sales", "type": "integer"},
                        {"name": "date", "type": "text"}
                    ],
                    "data": [
                        {"product": "产品A", "region": "华东", "sales": 1000, "date": "2024-01"},
                        {"product": "产品A", "region": "华北", "sales": 1500, "date": "2024-01"},
                        {"product": "产品B", "region": "华东", "sales": 2000, "date": "2024-01"},
                        {"product": "产品B", "region": "华北", "sales": 1800, "date": "2024-01"},
                        {"product": "产品A", "region": "华东", "sales": 1200, "date": "2024-02"},
                        {"product": "产品B", "region": "华东", "sales": 2200, "date": "2024-02"}
                    ]
                }
            }
        )
        self.assertEqual(create_result.status_code, 200)
        create_data = create_result.json()
        self.assertTrue(create_data.get("success"), f"创建失败: {create_data}")
        
        inner_data = create_data.get("data", {})
        if isinstance(inner_data, dict) and "data" in inner_data:
            snapshot_id = inner_data["data"]["snapshot_id"]
            table_name = inner_data["data"]["table_name"]
        else:
            snapshot_id = inner_data.get("snapshot_id")
            table_name = inner_data.get("table_name")
        
        self.snapshot_ids.append(snapshot_id)

        list_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_list_snapshots",
                "params": {"data_flow_id": 1}
            }
        )
        self.assertEqual(list_result.status_code, 200)
        list_data = list_result.json()
        self.assertTrue(list_data.get("success"))
        
        found = False
        for snapshot in list_data.get("data", {}).get("data", []):
            if snapshot.get("id") == snapshot_id:
                found = True
                self.assertEqual(snapshot.get("row_count"), 6)
                break
        self.assertTrue(found, "创建的快照未在列表中找到")

        query_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_query_snapshot",
                "params": {
                    "snapshot_id": snapshot_id,
                    "fields": ["product", "sales"],
                    "where": "region = '华东'",
                    "order_by": "sales DESC",
                    "limit": 10
                }
            }
        )
        self.assertEqual(query_result.status_code, 200)
        query_data = query_result.json()
        self.assertTrue(query_data.get("success"))
        
        inner_query = query_data.get("data", {})
        if isinstance(inner_query, dict) and "data" in inner_query:
            rows = inner_query.get("data", [])
        else:
            rows = inner_query.get("data", [])
        
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertIn("product", row)
            self.assertIn("sales", row)
            self.assertNotIn("region", row)

        agg_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_execute_sql",
                "params": {
                    "sql": f"""
                        SELECT product, SUM(sales) as total_sales
                        FROM {table_name}
                        GROUP BY product
                        ORDER BY total_sales DESC
                    """
                }
            }
        )
        self.assertEqual(agg_result.status_code, 200)
        agg_data = agg_result.json()
        self.assertTrue(agg_data.get("success"))
        
        inner_agg = agg_data.get("data", {})
        if isinstance(inner_agg, dict) and "data" in inner_agg:
            agg_rows = inner_agg.get("data", [])
        else:
            agg_rows = inner_agg.get("data", [])
        
        self.assertEqual(len(agg_rows), 2)


class TestUserScenario2_SchemaExploration(unittest.TestCase):
    """用户场景2: 探索数据结构"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        self.snapshot_id = None

    def tearDown(self):
        if self.snapshot_id:
            self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_delete_snapshot",
                    "params": {"snapshot_id": self.snapshot_id}
                }
            )

    def test_schema_exploration_flow(self):
        """FT-DB-002: 数据结构探索流程"""
        unique_id = get_unique_id()
        
        create_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "员工数据",
                    "table_name": f"employee_data_{unique_id}",
                    "fields": [
                        {"name": "emp_id", "type": "integer"},
                        {"name": "name", "type": "text"},
                        {"name": "department", "type": "text"},
                        {"name": "salary", "type": "integer"},
                        {"name": "hire_date", "type": "text"}
                    ],
                    "data": [
                        {"emp_id": 1, "name": "张三", "department": "技术部", "salary": 15000, "hire_date": "2020-01-15"},
                        {"emp_id": 2, "name": "李四", "department": "销售部", "salary": 12000, "hire_date": "2021-03-20"},
                        {"emp_id": 3, "name": "王五", "department": "技术部", "salary": 18000, "hire_date": "2019-06-10"}
                    ]
                }
            }
        )
        self.assertEqual(create_result.status_code, 200)
        create_data = create_result.json()
        
        inner_data = create_data.get("data", {})
        if isinstance(inner_data, dict) and "data" in inner_data:
            self.snapshot_id = inner_data["data"]["snapshot_id"]
        else:
            self.snapshot_id = inner_data.get("snapshot_id")

        schema_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_get_snapshot_schema",
                "params": {"snapshot_id": self.snapshot_id}
            }
        )
        self.assertEqual(schema_result.status_code, 200)
        schema_data = schema_result.json()
        self.assertTrue(schema_data.get("success"))
        
        inner_schema = schema_data.get("data", {})
        if isinstance(inner_schema, dict) and "data" in inner_schema:
            schema = inner_schema["data"]
        else:
            schema = inner_schema
        
        self.assertIn("columns", schema)
        columns = schema["columns"]
        column_names = [col["name"] for col in columns]
        
        self.assertIn("emp_id", column_names)
        self.assertIn("name", column_names)
        self.assertIn("department", column_names)
        self.assertIn("salary", column_names)
        
        self.assertIn("sample_data", schema)
        sample_data = schema["sample_data"]
        self.assertGreater(len(sample_data), 0)


class TestUserScenario3_DataFiltering(unittest.TestCase):
    """用户场景3: 数据筛选和分析"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        self.snapshot_id = None
        self.table_name = None

    def tearDown(self):
        if self.snapshot_id:
            self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_delete_snapshot",
                    "params": {"snapshot_id": self.snapshot_id}
                }
            )

    def test_filtering_and_analysis_flow(self):
        """FT-DB-003: 数据筛选和分析流程"""
        unique_id = get_unique_id()
        
        create_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "订单数据",
                    "table_name": f"order_data_{unique_id}",
                    "fields": [
                        {"name": "order_id"},
                        {"name": "customer"},
                        {"name": "amount"},
                        {"name": "status"},
                        {"name": "create_time"}
                    ],
                    "data": [
                        {"order_id": "ORD001", "customer": "客户A", "amount": 500, "status": "completed", "create_time": "2024-01-01"},
                        {"order_id": "ORD002", "customer": "客户B", "amount": 800, "status": "pending", "create_time": "2024-01-02"},
                        {"order_id": "ORD003", "customer": "客户A", "amount": 1200, "status": "completed", "create_time": "2024-01-03"},
                        {"order_id": "ORD004", "customer": "客户C", "amount": 300, "status": "cancelled", "create_time": "2024-01-04"},
                        {"order_id": "ORD005", "customer": "客户B", "amount": 600, "status": "completed", "create_time": "2024-01-05"}
                    ]
                }
            }
        )
        self.assertEqual(create_result.status_code, 200)
        create_data = create_result.json()
        
        inner_data = create_data.get("data", {})
        if isinstance(inner_data, dict) and "data" in inner_data:
            self.snapshot_id = inner_data["data"]["snapshot_id"]
            self.table_name = inner_data["data"]["table_name"]
        else:
            self.snapshot_id = inner_data.get("snapshot_id")
            self.table_name = inner_data.get("table_name")

        filter_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_query_snapshot",
                "params": {
                    "snapshot_id": self.snapshot_id,
                    "where": "status = 'completed'",
                    "order_by": "amount DESC"
                }
            }
        )
        self.assertEqual(filter_result.status_code, 200)
        filter_data = filter_result.json()
        self.assertTrue(filter_data.get("success"))
        
        inner_filter = filter_data.get("data", {})
        if isinstance(inner_filter, dict) and "data" in inner_filter:
            rows = inner_filter.get("data", [])
        else:
            rows = inner_filter.get("data", [])
        
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row.get("status"), "completed")

        stats_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_execute_sql",
                "params": {
                    "sql": f"""
                        SELECT status, COUNT(*) as count, SUM(amount) as total_amount
                        FROM {self.table_name}
                        GROUP BY status
                    """
                }
            }
        )
        self.assertEqual(stats_result.status_code, 200)
        stats_data = stats_result.json()
        self.assertTrue(stats_data.get("success"))
        
        inner_stats = stats_data.get("data", {})
        if isinstance(inner_stats, dict) and "data" in inner_stats:
            stats_rows = inner_stats.get("data", [])
        else:
            stats_rows = inner_stats.get("data", [])
        
        status_stats = {row["status"]: row for row in stats_rows}
        self.assertEqual(status_stats["completed"]["count"], 3)
        self.assertEqual(status_stats["pending"]["count"], 1)
        self.assertEqual(status_stats["cancelled"]["count"], 1)


class TestUserScenario4_MultipleSnapshots(unittest.TestCase):
    """用户场景4: 管理多个快照"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        self.snapshot_ids = []

    def tearDown(self):
        for snapshot_id in self.snapshot_ids:
            self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_delete_snapshot",
                    "params": {"snapshot_id": snapshot_id}
                }
            )

    def test_multiple_snapshots_management(self):
        """FT-DB-004: 多快照管理流程"""
        unique_id = get_unique_id()
        
        for i in range(3):
            result = self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_create_snapshot_table",
                    "params": {
                        "name": f"测试快照{i+1}",
                        "table_name": f"multi_test_{unique_id}_{i+1}",
                        "data_flow_id": i + 1,
                        "fields": [{"name": "value"}],
                        "data": [{"value": i * 100}]
                    }
                }
            )
            self.assertEqual(result.status_code, 200)
            data = result.json()
            
            inner_data = data.get("data", {})
            if isinstance(inner_data, dict) and "data" in inner_data:
                snapshot_id = inner_data["data"]["snapshot_id"]
            else:
                snapshot_id = inner_data.get("snapshot_id")
            
            self.snapshot_ids.append(snapshot_id)

        list_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_list_snapshots",
                "params": {}
            }
        )
        self.assertEqual(list_result.status_code, 200)
        list_data = list_result.json()
        
        inner_list = list_data.get("data", {})
        if isinstance(inner_list, dict) and "data" in inner_list:
            snapshots = inner_list.get("data", [])
        else:
            snapshots = inner_list.get("data", [])
        
        listed_ids = [s["id"] for s in snapshots]
        for sid in self.snapshot_ids:
            self.assertIn(sid, listed_ids)

        filter_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_list_snapshots",
                "params": {"data_flow_id": 1}
            }
        )
        self.assertEqual(filter_result.status_code, 200)
        filter_data = filter_result.json()
        
        inner_filter = filter_data.get("data", {})
        if isinstance(inner_filter, dict) and "data" in inner_filter:
            filtered = inner_filter.get("data", [])
        else:
            filtered = inner_filter.get("data", [])
        
        for snapshot in filtered:
            self.assertEqual(snapshot.get("data_flow_id"), 1)


class TestUserScenario5_CrossTableQuery(unittest.TestCase):
    """用户场景5: 跨表查询"""

    def setUp(self):
        self.client = TestClient(app)
        self.base_url = "/api/mcp"
        self.snapshot_ids = []
        self.table_names = []

    def tearDown(self):
        for snapshot_id in self.snapshot_ids:
            self.client.post(
                f"{self.base_url}/execute",
                json={
                    "tool_name": "pbbi_delete_snapshot",
                    "params": {"snapshot_id": snapshot_id}
                }
            )

    def test_cross_table_query(self):
        """FT-DB-005: 跨表SQL查询"""
        unique_id = get_unique_id()
        
        dept_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "部门表",
                    "table_name": f"departments_{unique_id}",
                    "fields": [
                        {"name": "dept_id"},
                        {"name": "dept_name"}
                    ],
                    "data": [
                        {"dept_id": 1, "dept_name": "技术部"},
                        {"dept_id": 2, "dept_name": "销售部"},
                        {"dept_id": 3, "dept_name": "财务部"}
                    ]
                }
            }
        )
        self.assertEqual(dept_result.status_code, 200)
        dept_data = dept_result.json()
        
        inner_dept = dept_data.get("data", {})
        if isinstance(inner_dept, dict) and "data" in inner_dept:
            self.snapshot_ids.append(inner_dept["data"]["snapshot_id"])
            self.table_names.append(inner_dept["data"]["table_name"])
        else:
            self.snapshot_ids.append(inner_dept.get("snapshot_id"))
            self.table_names.append(inner_dept.get("table_name"))

        emp_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_create_snapshot_table",
                "params": {
                    "name": "员工表",
                    "table_name": f"employees_{unique_id}",
                    "fields": [
                        {"name": "emp_name"},
                        {"name": "dept_id"},
                        {"name": "salary"}
                    ],
                    "data": [
                        {"emp_name": "张三", "dept_id": 1, "salary": 15000},
                        {"emp_name": "李四", "dept_id": 2, "salary": 12000},
                        {"emp_name": "王五", "dept_id": 1, "salary": 18000}
                    ]
                }
            }
        )
        self.assertEqual(emp_result.status_code, 200)
        emp_data = emp_result.json()
        
        inner_emp = emp_data.get("data", {})
        if isinstance(inner_emp, dict) and "data" in inner_emp:
            self.snapshot_ids.append(inner_emp["data"]["snapshot_id"])
            self.table_names.append(inner_emp["data"]["table_name"])
        else:
            self.snapshot_ids.append(inner_emp.get("snapshot_id"))
            self.table_names.append(inner_emp.get("table_name"))

        join_result = self.client.post(
            f"{self.base_url}/execute",
            json={
                "tool_name": "pbbi_execute_sql",
                "params": {
                    "sql": f"""
                        SELECT e.emp_name, d.dept_name, e.salary
                        FROM {self.table_names[1]} e
                        JOIN {self.table_names[0]} d ON e.dept_id = d.dept_id
                        ORDER BY e.salary DESC
                    """
                }
            }
        )
        self.assertEqual(join_result.status_code, 200)
        join_data = join_result.json()
        self.assertTrue(join_data.get("success"))
        
        inner_join = join_data.get("data", {})
        if isinstance(inner_join, dict) and "data" in inner_join:
            rows = inner_join.get("data", [])
        else:
            rows = inner_join.get("data", [])
        
        self.assertEqual(len(rows), 3)
        
        for row in rows:
            self.assertIn("emp_name", row)
            self.assertIn("dept_name", row)
            self.assertIn("salary", row)


if __name__ == "__main__":
    unittest.main()
