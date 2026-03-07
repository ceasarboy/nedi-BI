"""
Dashboard MCP - 看板管理工具
提供看板的查询和管理能力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.mcp.service import MCPTool
from src.core.database import SessionLocal
from src.models.config import Dashboard


class ListDashboardsTool:
    """列出所有看板"""

    def get_name(self) -> str:
        return "pbbi_list_dashboards"

    def get_description(self) -> str:
        return "列出PB-BI系统中所有已创建的数据看板"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
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
        page = max(1, params.get("page", 1))
        page_size = max(1, params.get("page_size", 20))
        offset = (page - 1) * page_size

        db = SessionLocal()
        try:
            total = db.query(Dashboard).count()
            
            dashboards = db.query(Dashboard).order_by(Dashboard.id.desc()).offset(offset).limit(page_size).all()

            return {
                "success": True,
                "data": {
                    "dashboards": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "chart_type": d.chart_type,
                            "created_at": str(d.created_at) if d.created_at else None,
                            "updated_at": str(d.updated_at) if d.updated_at else None
                        }
                        for d in dashboards
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
            return {"success": False, "error": f"查询看板失败: {str(e)}"}
        finally:
            db.close()


class GetDashboardTool:
    """获取看板详情"""

    def get_name(self) -> str:
        return "pbbi_get_dashboard"

    def get_description(self) -> str:
        return "获取指定看板的详细信息，包括配置信息"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "integer",
                    "description": "看板ID"
                }
            },
            "required": ["dashboard_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dashboard_id = params.get("dashboard_id")

        if not dashboard_id:
            return {"success": False, "error": "dashboard_id是必需的"}

        db = SessionLocal()
        try:
            dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            
            if not dashboard:
                return {"success": False, "error": f"看板不存在: id={dashboard_id}"}

            config = {}
            if dashboard.config:
                try:
                    config = json.loads(dashboard.config) if isinstance(dashboard.config, str) else dashboard.config
                except:
                    config = {}

            return {
                "success": True,
                "data": {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "chart_type": dashboard.chart_type,
                    "config": config,
                    "data_snapshot_id": dashboard.data_snapshot_id,
                    "created_at": str(dashboard.created_at) if dashboard.created_at else None,
                    "updated_at": str(dashboard.updated_at) if dashboard.updated_at else None
                }
            }
        except Exception as e:
            return {"success": False, "error": f"获取看板详情失败: {str(e)}"}
        finally:
            db.close()


class CreateDashboardTool:
    """创建看板"""

    def get_name(self) -> str:
        return "pbbi_create_dashboard"

    def get_description(self) -> str:
        return "创建新的数据看板"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "看板名称"
                },
                "chart_type": {
                    "type": "string",
                    "description": "图表类型：line, bar, pie, scatter等",
                    "enum": ["line", "bar", "pie", "scatter", "area", "table"]
                },
                "config": {
                    "type": "object",
                    "description": "看板配置"
                },
                "data_snapshot_id": {
                    "type": "integer",
                    "description": "关联的数据快照ID"
                }
            },
            "required": ["name", "chart_type"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        chart_type = params.get("chart_type", "line")
        config = params.get("config", {})
        data_snapshot_id = params.get("data_snapshot_id")

        if not name:
            return {"success": False, "error": "name是必需的"}

        db = SessionLocal()
        try:
            dashboard = Dashboard(
                name=name,
                chart_type=chart_type,
                config=json.dumps(config) if config else "{}",
                data_snapshot_id=data_snapshot_id
            )
            db.add(dashboard)
            db.commit()
            db.refresh(dashboard)

            return {
                "success": True,
                "data": {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "chart_type": dashboard.chart_type,
                    "created_at": str(dashboard.created_at) if dashboard.created_at else None
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"创建看板失败: {str(e)}"}
        finally:
            db.close()


class DeleteDashboardTool:
    """删除看板"""

    def get_name(self) -> str:
        return "pbbi_delete_dashboard"

    def get_description(self) -> str:
        return "删除指定的数据看板"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "integer",
                    "description": "看板ID"
                }
            },
            "required": ["dashboard_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dashboard_id = params.get("dashboard_id")

        if not dashboard_id:
            return {"success": False, "error": "dashboard_id是必需的"}

        db = SessionLocal()
        try:
            dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            
            if not dashboard:
                return {"success": False, "error": f"看板不存在: id={dashboard_id}"}

            deleted_name = dashboard.name
            db.delete(dashboard)
            db.commit()

            return {
                "success": True,
                "data": {
                    "deleted_dashboard_id": dashboard_id,
                    "deleted_dashboard_name": deleted_name
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"删除看板失败: {str(e)}"}
        finally:
            db.close()


class UpdateDashboardTool:
    """更新看板"""

    def get_name(self) -> str:
        return "pbbi_update_dashboard"

    def get_description(self) -> str:
        return "更新看板的名称、图表类型或配置"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": "integer",
                    "description": "看板ID"
                },
                "name": {
                    "type": "string",
                    "description": "新的看板名称"
                },
                "chart_type": {
                    "type": "string",
                    "description": "新的图表类型"
                },
                "config": {
                    "type": "object",
                    "description": "新的看板配置"
                }
            },
            "required": ["dashboard_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dashboard_id = params.get("dashboard_id")
        name = params.get("name")
        chart_type = params.get("chart_type")
        config = params.get("config")

        if not dashboard_id:
            return {"success": False, "error": "dashboard_id是必需的"}

        db = SessionLocal()
        try:
            dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            
            if not dashboard:
                return {"success": False, "error": f"看板不存在: id={dashboard_id}"}

            if name:
                dashboard.name = name
            if chart_type:
                dashboard.chart_type = chart_type
            if config:
                dashboard.config = json.dumps(config)
            
            db.commit()

            return {
                "success": True,
                "data": {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "chart_type": dashboard.chart_type,
                    "updated_at": str(dashboard.updated_at) if dashboard.updated_at else None
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"更新看板失败: {str(e)}"}
        finally:
            db.close()


class GetCurrentuserTool:
    """获取当前用户信息"""

    def get_name(self) -> str:
        return "pbbi_get_current_user"

    def get_description(self) -> str:
        return "获取当前登录用户的基本信息"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "data": {
                "user_id": 1,
                "username": "admin",
                "role": "admin",
                "permissions": ["read", "write", "delete", "admin"]
            }
        }


class GetUserResourcesTool:
    """获取用户资源"""

    def get_name(self) -> str:
        return "pbbi_get_user_resources"

    def get_description(self) -> str:
        return "获取当前用户可访问的资源统计"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            from src.models.config import DataFlow
            from src.mcp.database_mcp import _get_snapshot_connection

            dataflow_count = db.query(DataFlow).count()
            dashboard_count = db.query(Dashboard).count()

            conn = _get_snapshot_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM snapshots")
            snapshot_count = cursor.fetchone()[0]
            conn.close()

            return {
                "success": True,
                "data": {
                    "dataflows": dataflow_count,
                    "snapshots": snapshot_count,
                    "dashboards": dashboard_count
                }
            }
        except Exception as e:
            return {"success": False, "error": f"获取资源统计失败: {str(e)}"}
        finally:
            db.close()


def register_dashboard_tools(mcp_service):
    """注册Dashboard MCP工具"""
    tools = [
        ListDashboardsTool(),
        GetDashboardTool(),
        CreateDashboardTool(),
        DeleteDashboardTool(),
        UpdateDashboardTool(),
        GetCurrentuserTool(),
        GetUserResourcesTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
