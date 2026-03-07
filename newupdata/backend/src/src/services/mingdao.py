import requests
from typing import Dict, List, Optional

class MingDaoService:
    def __init__(self, appkey: str, sign: str, base_url: str = "https://api.mingdao.com"):
        self.appkey = appkey
        self.sign = sign
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "HAP-Appkey": appkey,
            "HAP-Sign": sign
        }

    def get_fields(self, worksheet_id: str) -> Dict:
        try:
            url = f"{self.base_url}/v3/app/worksheets/{worksheet_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            result = response.json()
            
            success = result.get("error_code") == 1 or result.get("success") == True
            fields = []
            
            if success:
                data = result.get("data", {})
                if isinstance(data, dict):
                    fields = data.get("fields", [])
                elif isinstance(data, list):
                    fields = data
            
            return {
                "success": success,
                "data": {
                    "data": fields
                },
                "error_msg": result.get("error_msg", ""),
                "raw_response": result
            }
        except Exception as e:
            return {
                "success": False,
                "data": {
                    "data": []
                },
                "error_msg": str(e)
            }

    def get_rows(self, worksheet_id: str, field_ids: Optional[List[str]] = None, page_size: int = 100) -> Dict:
        url = f"{self.base_url}/v3/app/worksheets/{worksheet_id}/rows/list"
        payload = {
            "pageIndex": 1,
            "pageSize": page_size
        }
        if field_ids:
            payload["fields"] = field_ids
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return {
            "success": result.get("error_code") == 1,
            "data": {
                "data": result.get("data", {}).get("rows", [])
            }
        }

    def test_connection(self) -> bool:
        try:
            url = f"{self.base_url}/v3/app"
            response = requests.get(url, headers=self.headers, timeout=10)
            result = response.json()
            return result.get("error_code") == 1 or result.get("success") == True
        except Exception:
            return False
