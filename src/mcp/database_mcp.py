"""
Database MCP - 数据快照数据库操作工具
提供对SQLite数据快照的查询能力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sqlite3
import time
from pathlib import Path

from src.mcp.service import MCPTool
from src.core.config import CONFIG_DIR


MAIN_DB_PATH = CONFIG_DIR / "pb_bi.db"


def _get_main_db_connection():
    """获取主数据库连接（pb_bi.db）"""
    conn = sqlite3.connect(str(MAIN_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


class ListSnapshotsTool:
    """列出所有数据快照"""

    def get_name(self) -> str:
        return "pbbi_list_snapshots"

    def get_description(self) -> str:
        return "列出SQLite数据库中的所有数据快照，返回快照ID、名称、表名、行数等信息"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_flow_id": {
                    "type": "integer",
                    "description": "按数据流ID筛选（可选）"
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
        data_flow_id = params.get("data_flow_id")
        page = max(1, params.get("page", 1))
        page_size = max(1, params.get("page_size", 20))
        offset = (page - 1) * page_size

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            if data_flow_id:
                count_query = "SELECT COUNT(*) FROM data_snapshots WHERE data_flow_id = ?"
                cursor.execute(count_query, (data_flow_id,))
                total = cursor.fetchone()[0]

                query = """
                    SELECT id, name, data_flow_id, worksheet_id, fields, data, created_at
                    FROM data_snapshots 
                    WHERE data_flow_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (data_flow_id, page_size, offset))
            else:
                count_query = "SELECT COUNT(*) FROM data_snapshots"
                cursor.execute(count_query)
                total = cursor.fetchone()[0]

                query = """
                    SELECT id, name, data_flow_id, worksheet_id, fields, data, created_at
                    FROM data_snapshots 
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (page_size, offset))

            rows = cursor.fetchall()

            snapshots = []
            for row in rows:
                data_json = row["data"]
                row_count = 0
                if data_json:
                    try:
                        data_list = json.loads(data_json)
                        row_count = len(data_list) if isinstance(data_list, list) else 0
                    except:
                        pass
                
                snapshots.append({
                    "id": row["id"],
                    "name": row["name"],
                    "data_flow_id": row["data_flow_id"],
                    "worksheet_id": row["worksheet_id"],
                    "row_count": row_count,
                    "created_at": row["created_at"]
                })

            return {
                "success": True,
                "data": snapshots,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        finally:
            conn.close()


class GetSnapshotSchemaTool:
    """获取快照表结构"""

    def get_name(self) -> str:
        return "pbbi_get_snapshot_schema"

    def get_description(self) -> str:
        return "获取指定快照的表结构，包括字段名、字段类型等信息。可以通过snapshot_id或table_name查询"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID（与table_name二选一）"
                },
                "table_name": {
                    "type": "string",
                    "description": "快照表名/名称（与snapshot_id二选一）"
                }
            },
            "required": []
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        table_name = params.get("table_name") or params.get("name")

        if not snapshot_id and not table_name:
            return {
                "success": False,
                "error": "必须提供snapshot_id或table_name"
            }

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            if snapshot_id:
                cursor.execute(
                    "SELECT id, name, fields, data FROM data_snapshots WHERE id = ?",
                    (snapshot_id,)
                )
            else:
                cursor.execute(
                    "SELECT id, name, fields, data FROM data_snapshots WHERE name = ?",
                    (table_name,)
                )

            row = cursor.fetchone()
            if not row:
                error_msg = f"快照不存在: snapshot_id={snapshot_id}" if snapshot_id else f"快照不存在: table_name={table_name}"
                return {
                    "success": False,
                    "error": error_msg
                }

            snapshot_id = row["id"]
            name = row["name"]
            fields = json.loads(row["fields"]) if row["fields"] else []
            data = json.loads(row["data"]) if row["data"] else []

            columns = []
            if fields:
                for field in fields:
                    field_name = field.get("name") or field.get("field_name", "unknown")
                    field_type = field.get("type") or field.get("data_type", "text")
                    columns.append({
                        "name": field_name,
                        "type": field_type,
                        "nullable": True,
                        "primary_key": False
                    })

            sample_data = data[:3] if data else []

            return {
                "success": True,
                "data": {
                    "snapshot_id": snapshot_id,
                    "snapshot_name": name,
                    "columns": columns,
                    "fields": fields,
                    "sample_data": sample_data,
                    "row_count": len(data)
                }
            }
        finally:
            conn.close()


class QuerySnapshotTool:
    """查询快照数据"""

    def get_name(self) -> str:
        return "pbbi_query_snapshot"

    def get_description(self) -> str:
        return "查询指定快照的数据，支持字段选择、条件筛选、排序和分页"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要查询的字段列表，默认查询所有字段"
                },
                "where": {
                    "type": "string",
                    "description": "简单条件过滤，如: age > 18"
                },
                "order_by": {
                    "type": "string",
                    "description": "排序字段，如: created_at DESC"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回行数限制，默认100"
                },
                "offset": {
                    "type": "integer",
                    "description": "偏移量，用于分页"
                }
            },
            "required": ["snapshot_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        fields = params.get("fields", [])
        where = params.get("where", "")
        order_by = params.get("order_by", "")
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)

        if not snapshot_id:
            return {
                "success": False,
                "error": "必须提供snapshot_id"
            }

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT name, fields, data FROM data_snapshots WHERE id = ?",
                (snapshot_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"快照不存在: id={snapshot_id}"}

            name = row["name"]
            all_fields = json.loads(row["fields"]) if row["fields"] else []
            data = json.loads(row["data"]) if row["data"] else []

            if fields:
                field_names = fields
            else:
                field_names = [f.get("name") or f.get("field_name", "unknown") for f in all_fields]

            filtered_data = []
            for row_data in data:
                if where:
                    try:
                        if not self._evaluate_where(row_data, where):
                            continue
                    except:
                        continue
                
                row_dict = {}
                for fn in field_names:
                    if fn in row_data:
                        row_dict[fn] = row_data[fn]
                    else:
                        for key in row_data.keys():
                            if fn in key or key in fn:
                                row_dict[fn] = row_data[key]
                                break
                
                if row_dict:
                    filtered_data.append(row_dict)

            if order_by:
                try:
                    reverse = "DESC" in order_by.upper()
                    order_field = order_by.split()[0].strip()
                    filtered_data.sort(
                        key=lambda x: x.get(order_field, ""),
                        reverse=reverse
                    )
                except:
                    pass

            total = len(filtered_data)
            paginated_data = filtered_data[offset:offset + limit]

            return {
                "success": True,
                "data": paginated_data,
                "count": len(paginated_data),
                "total": total,
                "snapshot_name": name,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total
                }
            }
        finally:
            conn.close()

    def _evaluate_where(self, row: dict, where: str) -> bool:
        """简单条件评估"""
        where_upper = where.upper()
        
        if " AND " in where_upper:
            parts = where.split(" AND ")
            return all(self._evaluate_where(row, p.strip()) for p in parts)
        
        if " OR " in where_upper:
            parts = where.split(" OR ")
            return any(self._evaluate_where(row, p.strip()) for p in parts)
        
        operators = [">=", "<=", "!=", ">", "<", "="]
        for op in operators:
            if op in where:
                parts = where.split(op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    row_value = row.get(field)
                    if row_value is None:
                        return False
                    
                    try:
                        if op == "=":
                            return str(row_value) == value or row_value == value
                        elif op == "!=":
                            return str(row_value) != value and row_value != value
                        elif op == ">":
                            return float(row_value) > float(value)
                        elif op == "<":
                            return float(row_value) < float(value)
                        elif op == ">=":
                            return float(row_value) >= float(value)
                        elif op == "<=":
                            return float(row_value) <= float(value)
                    except (ValueError, TypeError):
                        return str(row_value) == value
        return True


class ExecuteSQLTool:
    """执行SQL查询"""

    def get_name(self) -> str:
        return "pbbi_execute_sql"

    def get_description(self) -> str:
        return "在主数据库上执行SQL查询语句（仅支持SELECT语句）"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "SQL查询语句（仅支持SELECT）"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回行数限制，默认1000"
                }
            },
            "required": ["sql"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        sql = params.get("sql", "").strip()
        limit = params.get("limit", 1000)

        if not sql:
            return {"success": False, "error": "SQL语句不能为空"}

        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            return {"success": False, "error": "仅支持SELECT查询语句"}

        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return {"success": False, "error": f"禁止使用{keyword}语句"}

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            if "LIMIT" not in sql_upper:
                sql += f" LIMIT {limit}"

            cursor.execute(sql)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            return {
                "success": True,
                "data": [dict(zip(columns, row)) for row in rows],
                "count": len(rows),
                "columns": columns,
                "sql": sql
            }
        except sqlite3.Error as e:
            return {"success": False, "error": f"SQL执行错误: {str(e)}"}
        finally:
            conn.close()


class CreateSnapshotTableTool:
    """创建快照（内部使用）"""

    def get_name(self) -> str:
        return "pbbi_create_snapshot_table"

    def get_description(self) -> str:
        return "创建新的数据快照（内部工具）"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "快照名称"
                },
                "data_flow_id": {
                    "type": "integer",
                    "description": "关联的数据流ID"
                },
                "worksheet_id": {
                    "type": "string",
                    "description": "工作表ID"
                },
                "fields": {
                    "type": "array",
                    "description": "字段定义列表"
                },
                "data": {
                    "type": "array",
                    "description": "数据行列表"
                }
            },
            "required": ["name", "fields", "data"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        data_flow_id = params.get("data_flow_id", 0)
        worksheet_id = params.get("worksheet_id", f"local_{int(time.time() * 1000)}")
        fields = params.get("fields", [])
        data = params.get("data", [])

        if not name:
            return {"success": False, "error": "name是必需的"}

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_snapshots (name, data_flow_id, worksheet_id, fields, data)
                VALUES (?, ?, ?, ?, ?)
            """, (name, data_flow_id, worksheet_id, json.dumps(fields, ensure_ascii=False), json.dumps(data, ensure_ascii=False)))

            snapshot_id = cursor.lastrowid
            conn.commit()

            return {
                "success": True,
                "data": {
                    "snapshot_id": snapshot_id,
                    "name": name,
                    "row_count": len(data)
                }
            }
        except sqlite3.Error as e:
            conn.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        finally:
            conn.close()


class DeleteSnapshotTool:
    """删除快照"""

    def get_name(self) -> str:
        return "pbbi_delete_snapshot"

    def get_description(self) -> str:
        return "删除指定的数据快照"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                }
            },
            "required": ["snapshot_id"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

        conn = _get_main_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT name FROM data_snapshots WHERE id = ?",
                (snapshot_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"快照不存在: id={snapshot_id}"}

            name = row["name"]

            cursor.execute("DELETE FROM data_snapshots WHERE id = ?", (snapshot_id,))

            conn.commit()

            return {
                "success": True,
                "data": {
                    "deleted_snapshot_id": snapshot_id,
                    "deleted_name": name
                }
            }
        except sqlite3.Error as e:
            conn.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        finally:
            conn.close()


def register_database_tools(mcp_service):
    """注册Database MCP工具"""
    tools = [
        ListSnapshotsTool(),
        GetSnapshotSchemaTool(),
        QuerySnapshotTool(),
        ExecuteSQLTool(),
        CreateSnapshotTableTool(),
        DeleteSnapshotTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
