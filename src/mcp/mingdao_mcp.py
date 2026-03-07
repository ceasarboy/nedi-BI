"""
MingDao MCP - 明道云API操作工具
提供与明道云API的交互能力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.mcp.service import MCPTool
from src.services.mingdao import MingDaoService


_mingdao_connections: Dict[str, Dict[str, Any]] = {}


class MingDaoConnectTool:
    """连接明道云API"""

    def get_name(self) -> str:
        return "pbbi_mingdao_connect"

    def get_description(self) -> str:
        return "连接明道云API，验证凭证并保存连接配置。需要提供appkey、sign和可选的base_url。"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "appkey": {
                    "type": "string",
                    "description": "明道云应用的AppKey"
                },
                "sign": {
                    "type": "string",
                    "description": "明道云应用的Sign密钥"
                },
                "base_url": {
                    "type": "string",
                    "description": "API基础URL，默认为 https://api.mingdao.com，私有部署时需要修改"
                },
                "connection_name": {
                    "type": "string",
                    "description": "连接名称，用于后续引用，默认为 'default'"
                }
            },
            "required": ["appkey", "sign"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        appkey = params.get("appkey")
        sign = params.get("sign")
        base_url = params.get("base_url", "https://api.mingdao.com")
        connection_name = params.get("connection_name", "default")

        if not appkey or not sign:
            return {"success": False, "error": "appkey和sign是必需的"}

        service = MingDaoService(appkey, sign, base_url)
        
        try:
            is_connected = service.test_connection()
            if not is_connected:
                return {"success": False, "error": "连接验证失败，请检查appkey和sign是否正确"}

            _mingdao_connections[connection_name] = {
                "appkey": appkey,
                "sign": sign,
                "base_url": base_url,
                "connected_at": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": {
                    "connection_name": connection_name,
                    "base_url": base_url,
                    "connected": True,
                    "message": "明道云API连接成功"
                }
            }
        except Exception as e:
            return {"success": False, "error": f"连接失败: {str(e)}"}


class MingDaoGetFieldsTool:
    """获取工作表字段"""

    def get_name(self) -> str:
        return "pbbi_mingdao_get_fields"

    def get_description(self) -> str:
        return "获取明道云工作表的字段列表，包括字段ID、名称、类型等信息"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "worksheet_id": {
                    "type": "string",
                    "description": "工作表ID"
                },
                "connection_name": {
                    "type": "string",
                    "description": "连接名称，默认为 'default'"
                },
                "appkey": {
                    "type": "string",
                    "description": "AppKey（可选，如果未建立连接则使用此参数）"
                },
                "sign": {
                    "type": "string",
                    "description": "Sign密钥（可选，如果未建立连接则使用此参数）"
                },
                "base_url": {
                    "type": "string",
                    "description": "API基础URL（可选）"
                }
            },
            "required": ["worksheet_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        worksheet_id = params.get("worksheet_id")
        connection_name = params.get("connection_name", "default")

        if not worksheet_id:
            return {"success": False, "error": "worksheet_id是必需的"}

        conn = _mingdao_connections.get(connection_name)
        
        if conn:
            service = MingDaoService(conn["appkey"], conn["sign"], conn["base_url"])
        elif params.get("appkey") and params.get("sign"):
            service = MingDaoService(
                params["appkey"],
                params["sign"],
                params.get("base_url", "https://api.mingdao.com")
            )
        else:
            return {"success": False, "error": "请先使用pbbi_mingdao_connect建立连接，或提供appkey和sign参数"}

        try:
            result = service.get_fields(worksheet_id)
            
            if result.get("success"):
                fields = result.get("data", {}).get("data", [])
                return {
                    "success": True,
                    "data": {
                        "worksheet_id": worksheet_id,
                        "fields": [
                            {
                                "field_id": f.get("fieldId") or f.get("field_id"),
                                "field_name": f.get("name") or f.get("fieldName"),
                                "type": f.get("type"),
                                "required": f.get("required", False)
                            }
                            for f in fields
                        ],
                        "total": len(fields)
                    }
                }
            else:
                return {"success": False, "error": result.get("error_msg", "获取字段失败")}
        except Exception as e:
            return {"success": False, "error": f"获取字段失败: {str(e)}"}


class MingDaoGetRowsTool:
    """获取工作表数据"""

    def get_name(self) -> str:
        return "pbbi_mingdao_get_rows"

    def get_description(self) -> str:
        return "获取明道云工作表的数据行，支持字段筛选和分页"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "worksheet_id": {
                    "type": "string",
                    "description": "工作表ID"
                },
                "field_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要获取的字段ID列表，不填则获取所有字段"
                },
                "page_index": {
                    "type": "integer",
                    "description": "页码，默认1"
                },
                "page_size": {
                    "type": "integer",
                    "description": "每页数量，默认100"
                },
                "connection_name": {
                    "type": "string",
                    "description": "连接名称，默认为 'default'"
                },
                "appkey": {
                    "type": "string",
                    "description": "AppKey（可选）"
                },
                "sign": {
                    "type": "string",
                    "description": "Sign密钥（可选）"
                },
                "base_url": {
                    "type": "string",
                    "description": "API基础URL（可选）"
                }
            },
            "required": ["worksheet_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        worksheet_id = params.get("worksheet_id")
        field_ids = params.get("field_ids")
        page_index = params.get("page_index", 1)
        page_size = params.get("page_size", 100)
        connection_name = params.get("connection_name", "default")

        if not worksheet_id:
            return {"success": False, "error": "worksheet_id是必需的"}

        conn = _mingdao_connections.get(connection_name)
        
        if conn:
            service = MingDaoService(conn["appkey"], conn["sign"], conn["base_url"])
        elif params.get("appkey") and params.get("sign"):
            service = MingDaoService(
                params["appkey"],
                params["sign"],
                params.get("base_url", "https://api.mingdao.com")
            )
        else:
            return {"success": False, "error": "请先使用pbbi_mingdao_connect建立连接，或提供appkey和sign参数"}

        try:
            rows = service.get_data(
                worksheet_id,
                field_ids=field_ids,
                page_index=page_index,
                page_size=page_size
            )

            return {
                "success": True,
                "data": {
                    "worksheet_id": worksheet_id,
                    "rows": rows,
                    "count": len(rows),
                    "pagination": {
                        "page_index": page_index,
                        "page_size": page_size
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": f"获取数据失败: {str(e)}"}


class MingDaoSaveSnapshotTool:
    """保存数据到快照"""

    def get_name(self) -> str:
        return "pbbi_mingdao_save_snapshot"

    def get_description(self) -> str:
        return "从明道云工作表获取数据并保存为本地快照，便于离线分析"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "worksheet_id": {
                    "type": "string",
                    "description": "工作表ID"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "快照名称"
                },
                "field_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要保存的字段ID列表，不填则保存所有字段"
                },
                "page_size": {
                    "type": "integer",
                    "description": "获取数据数量，默认1000"
                },
                "connection_name": {
                    "type": "string",
                    "description": "连接名称，默认为 'default'"
                },
                "appkey": {
                    "type": "string",
                    "description": "AppKey（可选）"
                },
                "sign": {
                    "type": "string",
                    "description": "Sign密钥（可选）"
                },
                "base_url": {
                    "type": "string",
                    "description": "API基础URL（可选）"
                }
            },
            "required": ["worksheet_id", "snapshot_name"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        worksheet_id = params.get("worksheet_id")
        snapshot_name = params.get("snapshot_name")
        field_ids = params.get("field_ids")
        page_size = params.get("page_size", 1000)
        connection_name = params.get("connection_name", "default")

        if not worksheet_id or not snapshot_name:
            return {"success": False, "error": "worksheet_id和snapshot_name是必需的"}

        conn = _mingdao_connections.get(connection_name)
        
        if conn:
            service = MingDaoService(conn["appkey"], conn["sign"], conn["base_url"])
        elif params.get("appkey") and params.get("sign"):
            service = MingDaoService(
                params["appkey"],
                params["sign"],
                params.get("base_url", "https://api.mingdao.com")
            )
        else:
            return {"success": False, "error": "请先使用pbbi_mingdao_connect建立连接，或提供appkey和sign参数"}

        try:
            fields_result = service.get_fields(worksheet_id)
            if not fields_result.get("success"):
                return {"success": False, "error": "获取字段失败"}
            
            fields = fields_result.get("data", {}).get("data", [])

            rows = service.get_data(
                worksheet_id,
                field_ids=field_ids,
                page_size=page_size
            )

            if not rows:
                return {"success": False, "error": "获取的数据为空"}

            from src.mcp.database_mcp import CreateSnapshotTableTool
            import time
            
            table_name = f"mingdao_{worksheet_id}_{int(time.time())}"
            
            create_params = {
                "name": snapshot_name,
                "table_name": table_name,
                "fields": [
                    {
                        "name": f.get("name") or f.get("fieldName"),
                        "field_id": f.get("fieldId") or f.get("field_id"),
                        "type": f.get("type")
                    }
                    for f in fields
                    if not field_ids or (f.get("fieldId") or f.get("field_id")) in field_ids
                ],
                "data": rows
            }

            create_tool = CreateSnapshotTableTool()
            create_result = create_tool.execute(create_params)

            if create_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "snapshot_name": snapshot_name,
                        "table_name": table_name,
                        "row_count": len(rows),
                        "worksheet_id": worksheet_id,
                        "snapshot_id": create_result.get("data", {}).get("snapshot_id")
                    }
                }
            else:
                return {"success": False, "error": f"创建快照失败: {create_result.get('error')}"}

        except Exception as e:
            return {"success": False, "error": f"保存快照失败: {str(e)}"}


class MingDaoListConnectionsTool:
    """列出所有明道云连接"""

    def get_name(self) -> str:
        return "pbbi_mingdao_list_connections"

    def get_description(self) -> str:
        return "列出当前所有已建立的明道云API连接"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        connections = []
        for name, conn in _mingdao_connections.items():
            connections.append({
                "name": name,
                "base_url": conn.get("base_url"),
                "connected_at": conn.get("connected_at")
            })

        return {
            "success": True,
            "data": {
                "connections": connections,
                "total": len(connections)
            }
        }


def register_mingdao_tools(mcp_service):
    """注册MingDao MCP工具"""
    tools = [
        MingDaoConnectTool(),
        MingDaoGetFieldsTool(),
        MingDaoGetRowsTool(),
        MingDaoSaveSnapshotTool(),
        MingDaoListConnectionsTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
