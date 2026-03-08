"""
MCP工具执行器 - 执行PB-BI的MCP工具
包含字段验证和错误反馈机制
"""

from typing import Dict, Any, Optional, List
from src.mcp.service import mcp_service
from src.mcp.tools import register_all_tools
from src.mcp.chart_mcp import register_chart_tools
import sqlite3
import json

register_all_tools(mcp_service)
register_chart_tools(mcp_service)

def _get_db_connection():
    """获取数据库连接"""
    from src.core.config import CONFIG_DIR
    db_path = CONFIG_DIR / "pb_bi.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


class FieldValidator:
    """字段验证器 - 在执行工具前验证字段是否存在"""
    
    async def validate_fields(self, snapshot_id: int, fields: List[str]) -> Dict[str, Any]:
        """
        验证字段是否存在于快照中
        
        Args:
            snapshot_id: 数据快照ID
            fields: 需要验证的字段列表
            
        Returns:
            验证结果，包含是否有效、缺失字段、可用字段等
        """
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT fields FROM data_snapshots WHERE id = ?",
                (snapshot_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {
                    "valid": False,
                    "error": f"快照 {snapshot_id} 不存在",
                    "available_fields": []
                }
            
            fields_json = row["fields"]
            if not fields_json:
                return {
                    "valid": False,
                    "error": f"快照 {snapshot_id} 没有字段信息",
                    "available_fields": []
                }
            
            field_list = json.loads(fields_json)
            # 支持多种字段格式：{"name": "xxx"} 或 {"field_name": "xxx"} 或 {"field_id": "xxx"}
            available_fields = []
            for f in field_list:
                if isinstance(f, dict):
                    field_name = f.get("name") or f.get("field_name") or f.get("field_id")
                    if field_name:
                        available_fields.append(field_name)
                else:
                    available_fields.append(str(f))
            
            print(f"[DEBUG] Available fields: {available_fields[:10]}...")
            print(f"[DEBUG] Fields to validate: {fields}")
            
            # 检查每个字段
            missing_fields = []
            for field in fields:
                if field not in available_fields:
                    similar = self._find_similar_field(field, available_fields)
                    missing_fields.append({
                        "field": field,
                        "similar": similar
                    })
            
            if missing_fields:
                return {
                    "valid": False,
                    "error": self._format_field_error(missing_fields, available_fields),
                    "missing_fields": missing_fields,
                    "available_fields": available_fields
                }
            
            return {
                "valid": True,
                "available_fields": available_fields
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"字段验证异常: {str(e)}",
                "available_fields": []
            }
    
    def _find_similar_field(self, field: str, available_fields: List[str]) -> Optional[str]:
        """查找相似的字段名"""
        if not field:
            return None
        
        field_lower = field.lower().replace(" ", "").replace("（", "(").replace("）", ")")
        
        for available in available_fields:
            if not available:
                continue
            available_lower = available.lower().replace(" ", "").replace("（", "(").replace("）", ")")
            if field_lower in available_lower or available_lower in field_lower:
                return available
        
        return None
    
    def _format_field_error(self, missing_fields: List[Dict], available_fields: List[str]) -> str:
        """格式化字段错误信息"""
        errors = []
        for mf in missing_fields:
            field_name = mf['field'] if mf['field'] else '未知字段'
            if mf["similar"]:
                errors.append(f"字段 '{field_name}' 不存在，您是否想使用 '{mf['similar']}'？")
            else:
                errors.append(f"字段 '{field_name}' 不存在")
        
        # 过滤掉None值
        valid_fields = [f for f in available_fields if f is not None]
        return "; ".join(errors) + f"\n可用字段: {', '.join(valid_fields[:10])}{'...' if len(valid_fields) > 10 else ''}"


class MCPToolExecutor:
    def __init__(self):
        self._tools_registered = False
        self._validator = FieldValidator()
        self._register_tools()
    
    def _register_tools(self):
        if not self._tools_registered:
            register_all_tools(mcp_service)
            self._tools_registered = True
    
    def list_available_tools(self) -> list:
        tools = mcp_service.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in tools
        ]
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[DEBUG] Executing tool: {tool_name}, arguments: {arguments}")
        
        # 图表生成工具需要验证字段
        chart_tools = [
            "pbbi_generate_line_chart",
            "pbbi_generate_bar_chart",
            "pbbi_generate_pie_chart",
            "pbbi_generate_scatter_chart",
            "pbbi_generate_heatmap",
            "pbbi_generate_radar_chart",
            "pbbi_generate_histogram"
        ]
        
        if tool_name in chart_tools:
            print(f"[DEBUG] Validating chart tool fields...")
            validation_result = await self._validate_chart_tool(tool_name, arguments)
            print(f"[DEBUG] Validation result: valid={validation_result.get('valid')}, error={validation_result.get('error', 'None')}")
            if not validation_result.get("valid"):
                return {
                    "success": False,
                    "error": validation_result.get("error"),
                    "tool": tool_name,
                    "needs_retry": True,
                    "available_fields": validation_result.get("available_fields", [])
                }
        
        result = mcp_service.execute_tool(tool_name, arguments)
        
        # 检查外层success
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "tool": tool_name,
                "needs_retry": True
            }
        
        # 检查内层data中的success（工具执行结果）
        data = result.get("data", {})
        if isinstance(data, dict) and not data.get("success", True):
            error_msg = data.get("error", "工具执行失败")
            return {
                "success": False,
                "error": error_msg,
                "tool": tool_name,
                "needs_retry": True,
                "available_fields": data.get("available_fields", [])
            }
        
        return {
            "success": True,
            "data": data,
            "tool": tool_name
        }
    
    async def _validate_chart_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """验证图表工具的字段参数"""
        snapshot_id = arguments.get("snapshot_id")
        
        if not snapshot_id:
            return {"valid": True}  # 没有snapshot_id，跳过验证
        
        # 收集需要验证的字段
        fields_to_validate = []
        
        for key in ["x_field", "y_field", "category_field", "value_field"]:
            field = arguments.get(key)
            if field:
                fields_to_validate.append(field)
        
        # 处理多字段情况
        y_fields = arguments.get("y_fields", [])
        if isinstance(y_fields, list):
            fields_to_validate.extend(y_fields)
        
        fields_key = arguments.get("fields", [])
        if isinstance(fields_key, list):
            fields_to_validate.extend(fields_key)
        
        if not fields_to_validate:
            return {"valid": True}  # 没有字段参数，跳过验证
        
        return await self._validator.validate_fields(snapshot_id, fields_to_validate)
    
    async def execute_multiple(self, tool_calls: list) -> list:
        results = []
        for call in tool_calls:
            tool_name = call.get("name") or call.get("function", {}).get("name")
            arguments = call.get("arguments") or call.get("function", {}).get("arguments", {})
            
            if isinstance(arguments, str):
                import json
                try:
                    arguments = json.loads(arguments)
                except:
                    arguments = {}
            
            result = await self.execute(tool_name, arguments)
            results.append(result)
        
        return results
