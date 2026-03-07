"""
LocalFile MCP 单元测试
测试所有LocalFile MCP工具的基本功能
"""

import unittest
import sys
import os
import json
import tempfile
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.localfile_mcp import (
    UploadFileTool,
    ParseFileTool,
    CreateDataFlowFromFilesTool,
    ListUploadedFilesTool,
    DeleteUploadedFileTool,
    UPLOAD_DIR
)


class TestUploadFileTool(unittest.TestCase):
    """UploadFileTool单元测试"""

    def setUp(self):
        self.tool = UploadFileTool()
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def test_get_name(self):
        """UT-LF-001: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_local_upload_file")

    def test_get_description(self):
        """UT-LF-002: 测试工具描述"""
        desc = self.tool.get_description()
        self.assertIn("上传", desc)
        self.assertIn("文件", desc)

    def test_get_parameters(self):
        """UT-LF-003: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("file_name", params["properties"])
        self.assertIn("file_content", params["properties"])
        self.assertIn("file_type", params["properties"])
        self.assertIn("file_name", params["required"])
        self.assertIn("file_content", params["required"])

    def test_execute_without_file_name(self):
        """UT-LF-004: 测试缺少file_name"""
        result = self.tool.execute({
            "file_content": "test",
            "file_type": "csv"
        })
        self.assertFalse(result.get("success"))
        self.assertIn("file_name", result.get("error", ""))

    def test_execute_without_file_content(self):
        """UT-LF-005: 测试缺少file_content"""
        result = self.tool.execute({
            "file_name": "test.csv",
            "file_type": "csv"
        })
        self.assertFalse(result.get("success"))
        self.assertIn("file_content", result.get("error", ""))

    def test_execute_csv_text_content(self):
        """UT-LF-006: 测试CSV文本内容上传"""
        csv_content = "name,age,city\n张三,25,北京\n李四,30,上海"
        result = self.tool.execute({
            "file_name": "test.csv",
            "file_content": csv_content,
            "file_type": "csv"
        })
        self.assertTrue(result.get("success"), f"上传失败: {result}")
        self.assertIn("file_id", result.get("data", {}))
        
        if result.get("success"):
            file_id = result["data"]["file_id"]
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_execute_csv_base64_content(self):
        """UT-LF-007: 测试CSV Base64内容上传"""
        csv_content = "name,age\n张三,25"
        encoded = base64.b64encode(csv_content.encode("utf-8")).decode("ascii")
        
        result = self.tool.execute({
            "file_name": "test_b64.csv",
            "file_content": encoded,
            "file_type": "csv"
        })
        self.assertTrue(result.get("success"), f"上传失败: {result}")
        
        if result.get("success"):
            file_id = result["data"]["file_id"]
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_execute_json_content(self):
        """UT-LF-008: 测试JSON内容上传"""
        json_content = json.dumps([{"name": "张三", "age": 25}])
        result = self.tool.execute({
            "file_name": "test.json",
            "file_content": json_content,
            "file_type": "json"
        })
        self.assertTrue(result.get("success"), f"上传失败: {result}")
        
        if result.get("success"):
            file_id = result["data"]["file_id"]
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()


class TestParseFileTool(unittest.TestCase):
    """ParseFileTool单元测试"""

    def setUp(self):
        self.tool = ParseFileTool()
        self.upload_tool = UploadFileTool()
        self.uploaded_files = []

    def tearDown(self):
        for file_id in self.uploaded_files:
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_get_name(self):
        """UT-LF-011: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_local_parse_file")

    def test_get_parameters(self):
        """UT-LF-012: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("file_id", params["properties"])
        self.assertIn("file_id", params["required"])

    def test_execute_without_file_id(self):
        """UT-LF-013: 测试缺少file_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("file_id", result.get("error", ""))

    def test_execute_nonexistent_file(self):
        """UT-LF-014: 测试不存在的文件"""
        result = self.tool.execute({"file_id": "nonexistent_file.csv"})
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))

    def test_parse_csv_file(self):
        """UT-LF-015: 测试解析CSV文件"""
        csv_content = "name,age,city\n张三,25,北京\n李四,30,上海\n王五,28,广州"
        upload_result = self.upload_tool.execute({
            "file_name": "parse_test.csv",
            "file_content": csv_content,
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        
        file_id = upload_result["data"]["file_id"]
        self.uploaded_files.append(file_id)

        parse_result = self.tool.execute({
            "file_id": file_id,
            "file_type": "csv"
        })
        self.assertTrue(parse_result.get("success"), f"解析失败: {parse_result}")
        
        data = parse_result.get("data", {})
        self.assertEqual(data.get("total_rows"), 3)
        self.assertEqual(data.get("total_columns"), 3)
        self.assertIn("fields", data)
        self.assertIn("preview_data", data)

    def test_parse_json_file(self):
        """UT-LF-016: 测试解析JSON文件"""
        json_content = json.dumps([
            {"name": "张三", "age": 25},
            {"name": "李四", "age": 30}
        ])
        upload_result = self.upload_tool.execute({
            "file_name": "parse_test.json",
            "file_content": json_content,
            "file_type": "json"
        })
        self.assertTrue(upload_result.get("success"))
        
        file_id = upload_result["data"]["file_id"]
        self.uploaded_files.append(file_id)

        parse_result = self.tool.execute({
            "file_id": file_id,
            "file_type": "json"
        })
        self.assertTrue(parse_result.get("success"), f"解析失败: {parse_result}")
        
        data = parse_result.get("data", {})
        self.assertEqual(data.get("total_rows"), 2)

    def test_parse_with_preview_limit(self):
        """UT-LF-017: 测试预览行数限制"""
        csv_content = "name\n" + "\n".join([f"用户{i}" for i in range(20)])
        upload_result = self.upload_tool.execute({
            "file_name": "preview_test.csv",
            "file_content": csv_content,
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        
        file_id = upload_result["data"]["file_id"]
        self.uploaded_files.append(file_id)

        parse_result = self.tool.execute({
            "file_id": file_id,
            "preview_rows": 5
        })
        self.assertTrue(parse_result.get("success"))
        
        data = parse_result.get("data", {})
        self.assertEqual(len(data.get("preview_data", [])), 5)


class TestListUploadedFilesTool(unittest.TestCase):
    """ListUploadedFilesTool单元测试"""

    def setUp(self):
        self.tool = ListUploadedFilesTool()
        self.upload_tool = UploadFileTool()
        self.uploaded_files = []

    def tearDown(self):
        for file_id in self.uploaded_files:
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_get_name(self):
        """UT-LF-021: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_local_list_files")

    def test_execute_empty(self):
        """UT-LF-022: 测试空文件列表"""
        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        self.assertIn("files", result.get("data", {}))

    def test_execute_with_files(self):
        """UT-LF-023: 测试有文件"""
        upload_result = self.upload_tool.execute({
            "file_name": "list_test.csv",
            "file_content": "name,age\n张三,25",
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        self.uploaded_files.append(upload_result["data"]["file_id"])

        result = self.tool.execute({})
        self.assertTrue(result.get("success"))
        data = result.get("data", {})
        self.assertGreaterEqual(data.get("total"), 1)

    def test_execute_with_type_filter(self):
        """UT-LF-024: 测试按类型筛选"""
        csv_result = self.upload_tool.execute({
            "file_name": "filter_test.csv",
            "file_content": "name,age\n张三,25",
            "file_type": "csv"
        })
        self.assertTrue(csv_result.get("success"))
        self.uploaded_files.append(csv_result["data"]["file_id"])

        json_result = self.upload_tool.execute({
            "file_name": "filter_test.json",
            "file_content": json.dumps([{"name": "张三"}]),
            "file_type": "json"
        })
        self.assertTrue(json_result.get("success"))
        self.uploaded_files.append(json_result["data"]["file_id"])

        result = self.tool.execute({"file_type": "csv"})
        self.assertTrue(result.get("success"))
        data = result.get("data", {})
        for f in data.get("files", []):
            self.assertEqual(f.get("file_type"), "csv")


class TestDeleteUploadedFileTool(unittest.TestCase):
    """DeleteUploadedFileTool单元测试"""

    def setUp(self):
        self.tool = DeleteUploadedFileTool()
        self.upload_tool = UploadFileTool()

    def test_get_name(self):
        """UT-LF-031: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_local_delete_file")

    def test_execute_without_file_id(self):
        """UT-LF-032: 测试缺少file_id"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))
        self.assertIn("file_id", result.get("error", ""))

    def test_execute_nonexistent_file(self):
        """UT-LF-033: 测试删除不存在的文件"""
        result = self.tool.execute({"file_id": "nonexistent_file.csv"})
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))

    def test_execute_delete_success(self):
        """UT-LF-034: 测试成功删除"""
        upload_result = self.upload_tool.execute({
            "file_name": "delete_test.csv",
            "file_content": "name,age\n张三,25",
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        file_id = upload_result["data"]["file_id"]

        delete_result = self.tool.execute({"file_id": file_id})
        self.assertTrue(delete_result.get("success"))

        list_result = ListUploadedFilesTool().execute({})
        file_ids = [f["file_id"] for f in list_result.get("data", {}).get("files", [])]
        self.assertNotIn(file_id, file_ids)


class TestCreateDataFlowFromFilesTool(unittest.TestCase):
    """CreateDataFlowFromFilesTool单元测试"""

    def setUp(self):
        self.tool = CreateDataFlowFromFilesTool()
        self.upload_tool = UploadFileTool()
        self.uploaded_files = []

    def tearDown(self):
        for file_id in self.uploaded_files:
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_get_name(self):
        """UT-LF-041: 测试工具名称"""
        self.assertEqual(self.tool.get_name(), "pbbi_local_create_dataflow")

    def test_get_parameters(self):
        """UT-LF-042: 测试参数定义"""
        params = self.tool.get_parameters()
        self.assertIn("dataflow_name", params["required"])
        self.assertIn("file_id", params["required"])

    def test_execute_without_required_params(self):
        """UT-LF-043: 测试缺少必需参数"""
        result = self.tool.execute({})
        self.assertFalse(result.get("success"))

    def test_execute_nonexistent_file(self):
        """UT-LF-044: 测试不存在的文件"""
        result = self.tool.execute({
            "dataflow_name": "测试数据流",
            "file_id": "nonexistent.csv"
        })
        self.assertFalse(result.get("success"))
        self.assertIn("不存在", result.get("error", ""))


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def setUp(self):
        self.upload_tool = UploadFileTool()
        self.parse_tool = ParseFileTool()
        self.uploaded_files = []

    def tearDown(self):
        for file_id in self.uploaded_files:
            file_path = UPLOAD_DIR / file_id
            if file_path.exists():
                file_path.unlink()

    def test_empty_csv_file(self):
        """UT-LF-051: 测试空CSV文件"""
        upload_result = self.upload_tool.execute({
            "file_name": "empty.csv",
            "file_content": "",
            "file_type": "csv"
        })
        self.assertFalse(upload_result.get("success"))

    def test_csv_with_special_characters(self):
        """UT-LF-052: 测试特殊字符文件名"""
        upload_result = self.upload_tool.execute({
            "file_name": "测试文件-特殊@字符.csv",
            "file_content": "name,age\n张三,25",
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        self.uploaded_files.append(upload_result["data"]["file_id"])

    def test_large_preview_rows(self):
        """UT-LF-053: 测试大预览行数"""
        csv_content = "name\n" + "\n".join([f"用户{i}" for i in range(5)])
        upload_result = self.upload_tool.execute({
            "file_name": "large_preview.csv",
            "file_content": csv_content,
            "file_type": "csv"
        })
        self.assertTrue(upload_result.get("success"))
        self.uploaded_files.append(upload_result["data"]["file_id"])

        parse_result = self.parse_tool.execute({
            "file_id": upload_result["data"]["file_id"],
            "preview_rows": 1000
        })
        self.assertTrue(parse_result.get("success"))
        self.assertEqual(len(parse_result.get("data", {}).get("preview_data", [])), 5)


if __name__ == "__main__":
    unittest.main()
