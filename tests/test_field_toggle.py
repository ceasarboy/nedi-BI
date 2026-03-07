"""
字段勾选功能测试脚本
测试目标：验证字段is_enabled字段的保存和获取是否正常
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def login():
    """登录获取session"""
    # 使用JSON格式登录
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"},
        allow_redirects=False
    )
    print(f"登录状态: {response.status_code}")
    if response.status_code != 200:
        print(f"登录响应: {response.text}")
    return response.cookies.get_dict()

def test_field_toggle():
    """测试字段勾选功能"""
    cookies = login()
    
    # 1. 获取数据流列表
    print("\n=== 1. 获取数据流列表 ===")
    response = requests.get(f"{BASE_URL}/dataflows?page=1&page_size=10", cookies=cookies)
    dataflows = response.json()
    print(f"响应数据: {dataflows}")
    
    # 处理可能的分页格式
    if isinstance(dataflows, dict) and 'items' in dataflows:
        dataflows = dataflows['items']
    
    print(f"数据流数量: {len(dataflows) if dataflows else 0}")
    
    if not dataflows:
        print("没有数据流，跳过测试")
        return
    
    dataflow_id = dataflows[0]['id']
    print(f"使用数据流ID: {dataflow_id}")
    
    # 2. 获取字段配置
    print("\n=== 2. 获取字段配置 ===")
    response = requests.get(f"{BASE_URL}/dataflows/{dataflow_id}/fields", cookies=cookies)
    fields = response.json()
    print(f"字段数据类型: {type(fields)}")
    print(f"字段数据: {fields}")
    
    # 处理可能的格式
    if isinstance(fields, dict):
        if 'items' in fields:
            fields = fields['items']
        elif 'data' in fields:
            fields = fields['data']
        else:
            print(f"字段响应格式: {fields.keys()}")
    
    print(f"字段数量: {len(fields) if isinstance(fields, list) else 'N/A'}")
    
    if not fields or not isinstance(fields, list):
        print("没有字段数据，跳过测试")
        return
    
    print(f"第一个字段: {fields[0]}")
    print(f"is_enabled类型: {type(fields[0].get('is_enabled'))}")
    print(f"is_enabled值: {fields[0].get('is_enabled')}")
    
    # 3. 修改字段is_enabled
    print("\n=== 3. 修改字段is_enabled ===")
    original_enabled = fields[0].get('is_enabled')
    new_enabled = 'false' if original_enabled == 'true' else 'true'
    
    fields[0]['is_enabled'] = new_enabled
    print(f"原值: {original_enabled}, 新值: {new_enabled}")
    
    # 4. 保存字段配置
    print("\n=== 4. 保存字段配置 ===")
    response = requests.post(
        f"{BASE_URL}/dataflows/{dataflow_id}/fields",
        json={"fields": fields},
        cookies=cookies
    )
    print(f"保存状态: {response.status_code}")
    print(f"保存响应: {response.json()}")
    
    # 5. 重新获取字段配置
    print("\n=== 5. 重新获取字段配置 ===")
    response = requests.get(f"{BASE_URL}/dataflows/{dataflow_id}/fields", cookies=cookies)
    new_fields_raw = response.json()
    print(f"原始响应: {new_fields_raw}")
    
    # 处理响应格式
    if isinstance(new_fields_raw, dict):
        if 'data' in new_fields_raw:
            new_fields = new_fields_raw['data']
        elif 'items' in new_fields_raw:
            new_fields = new_fields_raw['items']
        else:
            new_fields = []
    else:
        new_fields = new_fields_raw
    
    print(f"字段数量: {len(new_fields) if isinstance(new_fields, list) else 'N/A'}")
    
    if new_fields and isinstance(new_fields, list):
        print(f"第一个字段is_enabled: {new_fields[0].get('is_enabled')}")
        
        # 6. 验证修改是否成功
        print("\n=== 6. 验证修改是否成功 ===")
        if new_fields[0].get('is_enabled') == new_enabled:
            print("✅ 测试通过：字段is_enabled修改成功")
        else:
            print(f"❌ 测试失败：期望 {new_enabled}, 实际 {new_fields[0].get('is_enabled')}")
    else:
        print("❌ 测试失败：重新获取字段返回空数组或格式错误")

if __name__ == "__main__":
    test_field_toggle()
