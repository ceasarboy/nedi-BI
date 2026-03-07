"""
字段勾选功能综合测试
测试目标：验证字段is_enabled字段的完整功能

测试类型：
1. 单元测试 - 测试后端模型和API
2. 集成测试 - 测试前后端交互
3. 功能测试 - 测试完整用户流程
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name, reason):
        self.failed += 1
        self.errors.append(f"{test_name}: {reason}")
        print(f"  ❌ {test_name} - {reason}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"测试结果: {self.passed}/{total} 通过")
        if self.errors:
            print("\n失败详情:")
            for e in self.errors:
                print(f"  - {e}")
        return self.failed == 0

result = TestResult()

def login():
    """登录获取session"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.cookies.get_dict() if response.status_code == 200 else None

def test_01_api_response_format():
    """测试1: API响应格式一致性"""
    print("\n【测试1: API响应格式一致性】")
    cookies = login()
    if not cookies:
        result.add_fail("API响应格式", "登录失败")
        return None
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    data = response.json()
    
    if "success" in data and "data" in data:
        result.add_pass("API响应格式正确")
        return cookies
    else:
        result.add_fail("API响应格式", f"缺少success或data字段: {data.keys()}")
        return cookies

def test_02_field_data_types():
    """测试2: 字段数据类型正确性"""
    print("\n【测试2: 字段数据类型正确性】")
    cookies = login()
    if not cookies:
        result.add_fail("字段数据类型", "登录失败")
        return
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    data = response.json()
    
    if not data.get("data"):
        result.add_fail("字段数据类型", "没有字段数据")
        return
    
    for field in data["data"]:
        if not isinstance(field.get("field_id"), str):
            result.add_fail("字段数据类型", f"field_id应为字符串: {type(field.get('field_id'))}")
            return
        if not isinstance(field.get("field_name"), str):
            result.add_fail("字段数据类型", f"field_name应为字符串")
            return
        if not isinstance(field.get("is_enabled"), str):
            result.add_fail("字段数据类型", f"is_enabled应为字符串: {type(field.get('is_enabled'))}")
            return
        if field.get("is_enabled") not in ["true", "false"]:
            result.add_fail("字段数据类型", f"is_enabled值应为'true'或'false': {field.get('is_enabled')}")
            return
    
    result.add_pass("所有字段数据类型正确")

def test_03_toggle_single_field():
    """测试3: 切换单个字段"""
    print("\n【测试3: 切换单个字段】")
    cookies = login()
    if not cookies:
        result.add_fail("切换单个字段", "登录失败")
        return
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    fields = response.json()["data"]
    
    if not fields:
        result.add_fail("切换单个字段", "没有字段数据")
        return
    
    original_value = fields[0]["is_enabled"]
    new_value = "false" if original_value == "true" else "true"
    fields[0]["is_enabled"] = new_value
    
    save_response = requests.post(
        f"{BASE_URL}/dataflows/1/fields",
        json={"fields": fields},
        cookies=cookies
    )
    
    if save_response.status_code != 200:
        result.add_fail("切换单个字段", f"保存失败: {save_response.status_code}")
        return
    
    verify_response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    verify_fields = verify_response.json()["data"]
    
    if verify_fields[0]["is_enabled"] == new_value:
        result.add_pass(f"字段切换成功: {original_value} -> {new_value}")
    else:
        result.add_fail("切换单个字段", f"期望{new_value}, 实际{verify_fields[0]['is_enabled']}")

def test_04_toggle_multiple_fields():
    """测试4: 批量切换字段"""
    print("\n【测试4: 批量切换字段】")
    cookies = login()
    if not cookies:
        result.add_fail("批量切换字段", "登录失败")
        return
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    fields = response.json()["data"]
    
    if len(fields) < 3:
        result.add_fail("批量切换字段", "字段数量不足3个")
        return
    
    original_values = [f["is_enabled"] for f in fields[:3]]
    new_values = ["false" if v == "true" else "true" for v in original_values]
    
    for i in range(3):
        fields[i]["is_enabled"] = new_values[i]
    
    save_response = requests.post(
        f"{BASE_URL}/dataflows/1/fields",
        json={"fields": fields},
        cookies=cookies
    )
    
    if save_response.status_code != 200:
        result.add_fail("批量切换字段", f"保存失败")
        return
    
    verify_response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    verify_fields = verify_response.json()["data"]
    
    all_match = True
    for i in range(3):
        if verify_fields[i]["is_enabled"] != new_values[i]:
            all_match = False
            break
    
    if all_match:
        result.add_pass("批量切换3个字段成功")
    else:
        result.add_fail("批量切换字段", "部分字段切换失败")

def test_05_persistence():
    """测试5: 数据持久化"""
    print("\n【测试5: 数据持久化】")
    cookies = login()
    if not cookies:
        result.add_fail("数据持久化", "登录失败")
        return
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    fields = response.json()["data"]
    
    if not fields:
        result.add_fail("数据持久化", "没有字段数据")
        return
    
    original_value = fields[0]["is_enabled"]
    new_value = "false" if original_value == "true" else "true"
    fields[0]["is_enabled"] = new_value
    
    requests.post(
        f"{BASE_URL}/dataflows/1/fields",
        json={"fields": fields},
        cookies=cookies
    )
    
    import time
    time.sleep(1)
    
    verify_response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    verify_fields = verify_response.json()["data"]
    
    if verify_fields[0]["is_enabled"] == new_value:
        result.add_pass("数据持久化验证成功")
    else:
        result.add_fail("数据持久化", "数据未正确保存")

def test_06_edge_cases():
    """测试6: 边界情况"""
    print("\n【测试6: 边界情况】")
    cookies = login()
    if not cookies:
        result.add_fail("边界情况", "登录失败")
        return
    
    response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
    fields = response.json()["data"]
    
    if not fields:
        result.add_fail("边界情况", "没有字段数据")
        return
    
    test_field = fields[0].copy()
    test_field["is_enabled"] = "TRUE"
    
    all_fields = fields.copy()
    all_fields[0] = test_field
    
    save_response = requests.post(
        f"{BASE_URL}/dataflows/1/fields",
        json={"fields": all_fields},
        cookies=cookies
    )
    
    if save_response.status_code == 200:
        verify_response = requests.get(f"{BASE_URL}/dataflows/1/fields", cookies=cookies)
        verify_fields = verify_response.json()["data"]
        
        if verify_fields[0]["is_enabled"] in ["true", "false", "TRUE", "FALSE"]:
            result.add_pass("边界情况处理正确")
        else:
            result.add_fail("边界情况", f"意外的is_enabled值: {verify_fields[0]['is_enabled']}")
    else:
        result.add_fail("边界情况", f"保存失败: {save_response.status_code}")

def run_all_tests():
    """运行所有测试"""
    print("="*50)
    print("字段勾选功能综合测试")
    print("="*50)
    
    test_01_api_response_format()
    test_02_field_data_types()
    test_03_toggle_single_field()
    test_04_toggle_multiple_fields()
    test_05_persistence()
    test_06_edge_cases()
    
    return result.summary()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
