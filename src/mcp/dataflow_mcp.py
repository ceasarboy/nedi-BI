"""
DataFlow MCP - 数据流管理工具
提供数据流的查询和管理能力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from src.mcp.service import MCPTool
from src.core.database import SessionLocal
from src.models.config import DataFlow, FieldType


class ListDataFlowsTool:
    """列出所有数据流"""

    def get_name(self) -> str:
        return "pbbi_list_dataflows"

    def get_description(self) -> str:
        return "列出PB-BI系统中配置的所有数据流，支持分页和类型筛选"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "按数据流类型筛选：mingdao, local_file, api",
                    "enum": ["mingdao", "local_file", "api"]
                },
                "page": {
                    "type": "integer",
                    "description": "页码，默认1"
                },
                "page_size": {
                    "type": "integer",
                    "description": "每页数量，默认20"
                }
            },
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        flow_type = params.get("type")
        page = max(1, params.get("page", 1))
        page_size = max(1, params.get("page_size", 20))
        offset = (page - 1) * page_size

        db = SessionLocal()
        try:
            query = db.query(DataFlow)
            
            if flow_type:
                query = query.filter(DataFlow.type == flow_type)
            
            total = query.count()
            
            dataflows = query.order_by(DataFlow.id.desc()).offset(offset).limit(page_size).all()

            return {
                "success": True,
                "data": {
                    "dataflows": [
                        {
                            "id": df.id,
                            "name": df.name,
                            "type": df.type,
                            "worksheet_id": df.worksheet_id,
                            "created_at": str(df.created_at) if df.created_at else None,
                            "updated_at": str(df.updated_at) if df.updated_at else None
                        }
                        for df in dataflows
                    ],
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": f"查询数据流失败: {str(e)}"}
        finally:
            db.close()


class GetDataFlowTool:
    """获取数据流详情"""

    def get_name(self) -> str:
        return "pbbi_get_dataflow"

    def get_description(self) -> str:
        return "获取指定数据流的详细信息，包括字段列表"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {
                    "type": "integer",
                    "description": "数据流ID"
                }
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dataflow_id = params.get("dataflow_id")

        if not dataflow_id:
            return {"success": False, "error": "dataflow_id是必需的"}

        db = SessionLocal()
        try:
            dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
            
            if not dataflow:
                return {"success": False, "error": f"数据流不存在: id={dataflow_id}"}

            fields = db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).all()

            return {
                "success": True,
                "data": {
                    "id": dataflow.id,
                    "name": dataflow.name,
                    "type": dataflow.type,
                    "worksheet_id": dataflow.worksheet_id,
                    "created_at": str(dataflow.created_at) if dataflow.created_at else None,
                    "updated_at": str(dataflow.updated_at) if dataflow.updated_at else None,
                    "fields": [
                        {
                            "field_id": f.field_id,
                            "field_name": f.field_name,
                            "data_type": f.data_type,
                            "is_enabled": f.is_enabled
                        }
                        for f in fields
                    ],
                    "fields_count": len(fields)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"获取数据流详情失败: {str(e)}"}
        finally:
            db.close()


class DeleteDataFlowTool:
    """删除数据流"""

    def get_name(self) -> str:
        return "pbbi_delete_dataflow"

    def get_description(self) -> str:
        return "删除指定的数据流及其关联的字段配置"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {
                    "type": "integer",
                    "description": "数据流ID"
                }
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dataflow_id = params.get("dataflow_id")

        if not dataflow_id:
            return {"success": False, "error": "dataflow_id是必需的"}

        db = SessionLocal()
        try:
            dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
            
            if not dataflow:
                return {"success": False, "error": f"数据流不存在: id={dataflow_id}"}

            db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).delete()
            
            db.delete(dataflow)
            db.commit()

            return {
                "success": True,
                "data": {
                    "deleted_dataflow_id": dataflow_id,
                    "deleted_dataflow_name": dataflow.name
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"删除数据流失败: {str(e)}"}
        finally:
            db.close()


class UpdateDataFlowTool:
    """更新数据流"""

    def get_name(self) -> str:
        return "pbbi_update_dataflow"

    def get_description(self) -> str:
        return "更新数据流的名称或配置"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {
                    "type": "integer",
                    "description": "数据流ID"
                },
                "name": {
                    "type": "string",
                    "description": "新的数据流名称"
                }
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dataflow_id = params.get("dataflow_id")
        name = params.get("name")

        if not dataflow_id:
            return {"success": False, "error": "dataflow_id是必需的"}

        db = SessionLocal()
        try:
            dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
            
            if not dataflow:
                return {"success": False, "error": f"数据流不存在: id={dataflow_id}"}

            if name:
                dataflow.name = name
            
            dataflow.updated_at = datetime.now()
            db.commit()

            return {
                "success": True,
                "data": {
                    "id": dataflow.id,
                    "name": dataflow.name,
                    "updated_at": str(dataflow.updated_at)
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"更新数据流失败: {str(e)}"}
        finally:
            db.close()


class GetDataFlowSnapshotsTool:
    """获取数据流关联的快照"""

    def get_name(self) -> str:
        return "pbbi_get_dataflow_snapshots"

    def get_description(self) -> str:
        return "获取指定数据流关联的所有快照"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {
                    "type": "integer",
                    "description": "数据流ID"
                }
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dataflow_id = params.get("dataflow_id")

        if not dataflow_id:
            return {"success": False, "error": "dataflow_id是必需的"}

        from src.mcp.database_mcp import _get_snapshot_connection

        conn = _get_snapshot_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, name, table_name, row_count, created_at FROM snapshots WHERE data_flow_id = ? ORDER BY created_at DESC",
                (dataflow_id,)
            )
            rows = cursor.fetchall()

            return {
                "success": True,
                "data": {
                    "dataflow_id": dataflow_id,
                    "snapshots": [
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "table_name": row["table_name"],
                            "row_count": row["row_count"],
                            "created_at": row["created_at"]
                        }
                        for row in rows
                    ],
                    "total": len(rows)
                }
            }
        finally:
            conn.close()


def register_dataflow_tools(mcp_service):
    """注册DataFlow MCP工具"""
    tools = [
        ListDataFlowsTool(),
        GetDataFlowTool(),
        DeleteDataFlowTool(),
        UpdateDataFlowTool(),
        GetDataFlowSnapshotsTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
