from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.mcp.service import MCPTool

class BaseTool:
    def get_name(self) -> str:
        raise NotImplementedError

    def get_description(self) -> str:
        raise NotImplementedError

    def get_parameters(self) -> Dict[str, Any]:
        raise NotImplementedError

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class GetDataFlowsTool(BaseTool):
    """获取数据流列表工具"""

    def get_name(self) -> str:
        return "pbbi_get_dataflows"

    def get_description(self) -> str:
        return "获取PB-BI系统中配置的所有数据流列表，包括数据流ID、名称、类型等信息"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "description": "页码，默认1"},
                "page_size": {"type": "integer", "description": "每页数量，默认10"}
            },
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import DataFlow

        db = SessionLocal()
        try:
            page = params.get("page", 1)
            page_size = params.get("page_size", 10)
            offset = (page - 1) * page_size

            dataflows = db.query(DataFlow).offset(offset).limit(page_size).all()

            return {
                "success": True,
                "data": [
                    {
                        "id": df.id,
                        "name": df.name,
                        "type": df.type,
                        "worksheet_id": df.worksheet_id,
                        "is_private": df.is_private,
                        "created_at": df.created_at.isoformat() if df.created_at else None
                    }
                    for df in dataflows
                ],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": db.query(DataFlow).count()
                }
            }
        finally:
            db.close()


class GetDataFlowTool(BaseTool):
    """获取单个数据流详情"""

    def get_name(self) -> str:
        return "pbbi_get_dataflow"

    def get_description(self) -> str:
        return "根据数据流ID获取详细信息，包括配置、字段等"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {"type": "integer", "description": "数据流ID"}
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import DataFlow, FieldType

        db = SessionLocal()
        try:
            dataflow_id = params.get("dataflow_id")
            if not dataflow_id:
                return {"success": False, "error": "dataflow_id is required"}

            dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
            if not dataflow:
                return {"success": False, "error": "DataFlow not found"}

            fields = db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).all()

            return {
                "success": True,
                "data": {
                    "id": dataflow.id,
                    "name": dataflow.name,
                    "type": dataflow.type,
                    "appkey": dataflow.appkey,
                    "worksheet_id": dataflow.worksheet_id,
                    "is_private": dataflow.is_private,
                    "private_api_url": dataflow.private_api_url,
                    "created_at": dataflow.created_at.isoformat() if dataflow.created_at else None,
                    "updated_at": dataflow.updated_at.isoformat() if dataflow.updated_at else None,
                    "fields": [
                        {
                            "field_id": f.field_id,
                            "field_name": f.field_name,
                            "data_type": f.data_type,
                            "is_enabled": f.is_enabled
                        }
                        for f in fields
                    ]
                }
            }
        finally:
            db.close()


class QueryDataTool(BaseTool):
    """数据查询工具"""

    def get_name(self) -> str:
        return "pbbi_query_data"

    def get_description(self) -> str:
        return "根据数据流ID查询数据，支持筛选和分页"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {"type": "integer", "description": "数据流ID"},
                "field_ids": {"type": "array", "items": {"type": "string"}, "description": "要查询的字段ID列表"},
                "page_index": {"type": "integer", "description": "页码，默认1"},
                "page_size": {"type": "integer", "description": "每页数量，默认100"}
            },
            "required": ["dataflow_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import DataFlow, FieldType
        from src.services.mingdao import MingDaoService

        db = SessionLocal()
        try:
            dataflow_id = params.get("dataflow_id")
            if not dataflow_id:
                return {"success": False, "error": "dataflow_id is required"}

            dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
            if not dataflow:
                return {"success": False, "error": "DataFlow not found"}

            enabled_fields = db.query(FieldType).filter(
                FieldType.data_flow_id == dataflow_id,
                FieldType.is_enabled == "true"
            ).all()

            enabled_field_ids = {f.field_id for f in enabled_fields}

            is_private = bool(dataflow.is_private)
            base_url = dataflow.private_api_url if is_private else "https://api.mingdao.com"
            service = MingDaoService(dataflow.appkey, dataflow.sign, base_url)

            page_index = params.get("page_index", 1)
            page_size = params.get("page_size", 100)

            all_data = service.get_data(
                dataflow.worksheet_id,
                page_index=page_index,
                page_size=page_size
            )

            field_ids = params.get("field_ids")
            if field_ids:
                all_data = [
                    {k: v for k, v in row.items() if k in field_ids}
                    for row in all_data
                ]

            return {
                "success": True,
                "data": all_data,
                "count": len(all_data),
                "pagination": {
                    "page": page_index,
                    "page_size": page_size
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()


class GetSchemaTool(BaseTool):
    """获取数据库Schema工具"""

    def get_name(self) -> str:
        return "pbbi_get_schema"

    def get_description(self) -> str:
        return "获取PB-BI系统的数据库表结构信息，包括所有表和字段"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "表名，不传则返回所有表"}
            },
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        import sqlite3

        db_path = "config/pb_bi.db"
        table_name = params.get("table_name")

        tables = ["users", "data_flows", "field_types", "data_snapshots", "dashboards"]

        if table_name:
            if table_name not in tables:
                return {"success": False, "error": f"Table {table_name} not found"}
            tables = [table_name]

        schema = {}
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            sample_rows = cursor.fetchall()

            schema[table] = {
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "nullable": not col[3],
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ],
                "sample_data": [dict(zip([c[1] for c in columns], row)) for row in sample_rows]
            }

        conn.close()

        return {
            "success": True,
            "schema": schema
        }


class GetSnapshotsTool(BaseTool):
    """获取数据快照列表"""

    def get_name(self) -> str:
        return "pbbi_get_snapshots"

    def get_description(self) -> str:
        return "获取数据快照列表，可按数据流ID筛选"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dataflow_id": {"type": "integer", "description": "数据流ID筛选"}
            },
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import DataSnapshot

        db = SessionLocal()
        try:
            dataflow_id = params.get("dataflow_id")

            query = db.query(DataSnapshot)
            if dataflow_id:
                query = query.filter(DataSnapshot.data_flow_id == dataflow_id)

            snapshots = query.order_by(DataSnapshot.created_at.desc()).limit(50).all()

            return {
                "success": True,
                "data": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "data_flow_id": s.data_flow_id,
                        "worksheet_id": s.worksheet_id,
                        "row_count": len(json.loads(s.data)) if s.data else 0,
                        "created_at": s.created_at.isoformat() if s.created_at else None
                    }
                    for s in snapshots
                ]
            }
        finally:
            db.close()


class GetSnapshotDataTool(BaseTool):
    """获取快照详细数据"""

    def get_name(self) -> str:
        return "pbbi_get_snapshot_data"

    def get_description(self) -> str:
        return "根据快照ID获取详细的快照数据"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "快照ID"}
            },
            "required": ["snapshot_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import DataSnapshot

        db = SessionLocal()
        try:
            snapshot_id = params.get("snapshot_id")
            if not snapshot_id:
                return {"success": False, "error": "snapshot_id is required"}

            snapshot = db.query(DataSnapshot).filter(DataSnapshot.id == snapshot_id).first()
            if not snapshot:
                return {"success": False, "error": "Snapshot not found"}

            return {
                "success": True,
                "data": {
                    "id": snapshot.id,
                    "name": snapshot.name,
                    "data_flow_id": snapshot.data_flow_id,
                    "worksheet_id": snapshot.worksheet_id,
                    "fields": json.loads(snapshot.fields) if snapshot.fields else [],
                    "data": json.loads(snapshot.data) if snapshot.data else [],
                    "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None
                }
            }
        finally:
            db.close()


class GetDashboardsTool(BaseTool):
    """获取看板列表"""

    def get_name(self) -> str:
        return "pbbi_get_dashboards"

    def get_description(self) -> str:
        return "获取数据看板列表"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from src.core.database import SessionLocal
        from src.models.config import Dashboard

        db = SessionLocal()
        try:
            dashboards = db.query(Dashboard).order_by(Dashboard.created_at.desc()).limit(50).all()

            return {
                "success": True,
                "data": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "chart_type": d.chart_type,
                        "data_snapshot_id": d.data_snapshot_id,
                        "created_at": d.created_at.isoformat() if d.created_at else None
                    }
                    for d in dashboards
                ]
            }
        finally:
            db.close()


def register_all_tools(mcp_service):
    """注册所有PB-BI工具"""
    tools = [
        GetDataFlowsTool(),
        GetDataFlowTool(),
        QueryDataTool(),
        GetSchemaTool(),
        GetSnapshotsTool(),
        GetSnapshotDataTool(),
        GetDashboardsTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
