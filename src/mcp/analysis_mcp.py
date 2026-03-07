"""
Analysis MCP - 数据分析工具
提供数据聚合、筛选、统计等分析能力
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sqlite3

from src.mcp.service import MCPTool
from src.core.config import CONFIG_DIR


MAIN_DB_PATH = CONFIG_DIR / "pb_bi.db"


def _get_main_db_connection():
    """获取主数据库连接（pb_bi.db）"""
    conn = sqlite3.connect(str(MAIN_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


class AggregateDataTool:
    """数据聚合"""

    def get_name(self) -> str:
        return "pbbi_aggregate_data"

    def get_description(self) -> str:
        return "对快照数据进行聚合分析，支持SUM、AVG、COUNT、MAX、MIN等聚合函数"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                },
                "aggregations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string", "description": "字段名"},
                            "function": {"type": "string", "description": "聚合函数：SUM, AVG, COUNT, MAX, MIN"},
                            "alias": {"type": "string", "description": "结果别名"}
                        }
                    },
                    "description": "聚合配置列表"
                },
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "分组字段列表"
                },
                "where": {
                    "type": "string",
                    "description": "筛选条件"
                }
            },
            "required": ["aggregations"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        aggregations = params.get("aggregations", [])
        group_by = params.get("group_by", [])
        where = params.get("where", "")

        if not aggregations:
            return {"success": False, "error": "aggregations是必需的"}

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

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

            if where:
                try:
                    data = [d for d in data if self._evaluate_where(d, where)]
                except:
                    pass

            results = []
            if group_by:
                groups = {}
                for row_data in data:
                    key = tuple(row_data.get(f, "") for f in group_by)
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(row_data)
                
                for key, group_data in groups.items():
                    result = dict(zip(group_by, key))
                    for agg in aggregations:
                        field = agg.get("field")
                        func = agg.get("function", "COUNT").upper()
                        alias = agg.get("alias", f"{func}_{field}")
                        
                        values = [d.get(field) for d in group_data if d.get(field) is not None]
                        result[alias] = self._aggregate(values, func)
                    results.append(result)
            else:
                result = {}
                for agg in aggregations:
                    field = agg.get("field")
                    func = agg.get("function", "COUNT").upper()
                    alias = agg.get("alias", f"{func}_{field}")
                    
                    values = [d.get(field) for d in data if d.get(field) is not None]
                    result[alias] = self._aggregate(values, func)
                results.append(result)

            return {
                "success": True,
                "data": results,
                "snapshot_name": name,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": f"聚合分析失败: {str(e)}"}
        finally:
            conn.close()

    def _aggregate(self, values: list, func: str) -> Any:
        if not values:
            return 0 if func == "COUNT" else None
        
        if func == "COUNT":
            return len(values)
        elif func == "SUM":
            return sum(float(v) for v in values if isinstance(v, (int, float)))
        elif func == "AVG":
            nums = [float(v) for v in values if isinstance(v, (int, float))]
            return sum(nums) / len(nums) if nums else None
        elif func == "MAX":
            return max(values)
        elif func == "MIN":
            return min(values)
        return None

    def _evaluate_where(self, row: dict, where: str) -> bool:
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


class FilterDataTool:
    """数据筛选"""

    def get_name(self) -> str:
        return "pbbi_filter_data"

    def get_description(self) -> str:
        return "对快照数据进行高级筛选，支持多条件组合"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                },
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operator": {"type": "string", "description": "=, !=, >, <, >=, <=, LIKE, IN"},
                            "value": {"type": "string"},
                            "logic": {"type": "string", "description": "AND, OR"}
                        }
                    },
                    "description": "筛选条件列表"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "返回字段列表"
                },
                "order_by": {
                    "type": "string",
                    "description": "排序字段"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回行数限制"
                }
            },
            "required": ["snapshot_id", "conditions"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        conditions = params.get("conditions", [])
        fields = params.get("fields", [])
        order_by = params.get("order_by", "")
        limit = params.get("limit", 100)

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

        if not conditions:
            return {"success": False, "error": "conditions是必需的"}

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

            filtered_data = []
            for row_data in data:
                if self._evaluate_conditions(row_data, conditions):
                    if fields:
                        filtered_row = {f: row_data.get(f) for f in fields}
                    else:
                        filtered_row = row_data
                    filtered_data.append(filtered_row)

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
            filtered_data = filtered_data[:limit]

            return {
                "success": True,
                "data": filtered_data,
                "snapshot_name": name,
                "count": len(filtered_data),
                "total": total
            }
        except Exception as e:
            return {"success": False, "error": f"数据筛选失败: {str(e)}"}
        finally:
            conn.close()

    def _evaluate_conditions(self, row: dict, conditions: list) -> bool:
        if not conditions:
            return True
        
        result = True
        for i, cond in enumerate(conditions):
            field = cond.get("field")
            operator = cond.get("operator", "=").upper()
            value = cond.get("value", "")
            logic = cond.get("logic", "AND").upper() if i > 0 else "AND"
            
            row_value = row.get(field)
            cond_result = False
            
            if row_value is not None:
                if operator == "=":
                    cond_result = str(row_value) == value or row_value == value
                elif operator == "!=":
                    cond_result = str(row_value) != value and row_value != value
                elif operator == ">":
                    try:
                        cond_result = float(row_value) > float(value)
                    except:
                        pass
                elif operator == "<":
                    try:
                        cond_result = float(row_value) < float(value)
                    except:
                        pass
                elif operator == ">=":
                    try:
                        cond_result = float(row_value) >= float(value)
                    except:
                        pass
                elif operator == "<=":
                    try:
                        cond_result = float(row_value) <= float(value)
                    except:
                        pass
                elif operator == "LIKE":
                    cond_result = value.lower() in str(row_value).lower()
            
            if i == 0:
                result = cond_result
            else:
                if logic == "AND":
                    result = result and cond_result
                else:
                    result = result or cond_result
        
        return result


class StatisticsTool:
    """统计描述"""

    def get_name(self) -> str:
        return "pbbi_statistics"

    def get_description(self) -> str:
        return "计算数值字段的统计描述，包括均值、中位数、标准差、最大值、最小值等"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                },
                "field": {
                    "type": "string",
                    "description": "要统计的数值字段"
                },
                "where": {
                    "type": "string",
                    "description": "筛选条件"
                }
            },
            "required": ["snapshot_id", "field"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        field = params.get("field")
        where = params.get("where", "")

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

        if not field:
            return {"success": False, "error": "field是必需的"}

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
            data = json.loads(row["data"]) if row["data"] else []

            values = []
            for row_data in data:
                if where:
                    try:
                        if not self._evaluate_where(row_data, where):
                            continue
                    except:
                        continue
                
                val = row_data.get(field)
                if val is not None and isinstance(val, (int, float)):
                    values.append(float(val))

            if not values:
                return {
                    "success": True,
                    "data": {
                        "field": field,
                        "count": 0,
                        "sum": None,
                        "avg": None,
                        "min": None,
                        "max": None,
                        "median": None
                    }
                }

            sorted_values = sorted(values)
            n = len(sorted_values)
            if n % 2 == 0:
                median = (sorted_values[n//2-1] + sorted_values[n//2]) / 2
            else:
                median = sorted_values[n//2]

            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            std_dev = variance ** 0.5

            return {
                "success": True,
                "data": {
                    "field": field,
                    "count": n,
                    "sum": sum(values),
                    "avg": mean,
                    "min": min(values),
                    "max": max(values),
                    "median": median,
                    "std_dev": std_dev
                },
                "snapshot_name": name
            }
        except Exception as e:
            return {"success": False, "error": f"统计计算失败: {str(e)}"}
        finally:
            conn.close()

    def _evaluate_where(self, row: dict, where: str) -> bool:
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
                        elif op == ">":
                            return float(row_value) > float(value)
                        elif op == "<":
                            return float(row_value) < float(value)
                        elif op == ">=":
                            return float(row_value) >= float(value)
                        elif op == "<=":
                            return float(row_value) <= float(value)
                    except:
                        return str(row_value) == value
        return True


class PivotTableTool:
    """透视表"""

    def get_name(self) -> str:
        return "pbbi_pivot_table"

    def get_description(self) -> str:
        return "创建数据透视表，支持行分组、列分组和值聚合"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {
                    "type": "integer",
                    "description": "快照ID"
                },
                "row_field": {
                    "type": "string",
                    "description": "行分组字段"
                },
                "column_field": {
                    "type": "string",
                    "description": "列分组字段（可选）"
                },
                "value_field": {
                    "type": "string",
                    "description": "值字段"
                },
                "agg_function": {
                    "type": "string",
                    "description": "聚合函数：SUM, COUNT, AVG",
                    "enum": ["SUM", "COUNT", "AVG"]
                },
                "where": {
                    "type": "string",
                    "description": "筛选条件"
                }
            },
            "required": ["snapshot_id", "row_field", "value_field"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        row_field = params.get("row_field")
        column_field = params.get("column_field")
        value_field = params.get("value_field")
        agg_function = params.get("agg_function", "SUM").upper()
        where = params.get("where", "")

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

        if not row_field or not value_field:
            return {"success": False, "error": "row_field和value_field是必需的"}

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
            data = json.loads(row["data"]) if row["data"] else []

            if where:
                try:
                    data = [d for d in data if self._evaluate_where(d, where)]
                except:
                    pass

            if column_field:
                pivot_data = {}
                for row_data in data:
                    row_key = row_data.get(row_field, "")
                    col_key = row_data.get(column_field, "")
                    if row_key not in pivot_data:
                        pivot_data[row_key] = {}
                    if col_key not in pivot_data[row_key]:
                        pivot_data[row_key][col_key] = []
                    val = row_data.get(value_field)
                    if val is not None:
                        pivot_data[row_key][col_key].append(float(val) if isinstance(val, (int, float)) else val)

                results = []
                for row_key, cols in pivot_data.items():
                    result = {row_field: row_key}
                    for col_key, values in cols.items():
                        result[col_key] = self._aggregate(values, agg_function)
                    results.append(result)
            else:
                groups = {}
                for row_data in data:
                    key = row_data.get(row_field, "")
                    if key not in groups:
                        groups[key] = []
                    val = row_data.get(value_field)
                    if val is not None:
                        groups[key].append(float(val) if isinstance(val, (int, float)) else val)

                results = []
                for key, values in groups.items():
                    results.append({
                        row_field: key,
                        value_field: self._aggregate(values, agg_function)
                    })

            return {
                "success": True,
                "data": results,
                "snapshot_name": name,
                "pivot_config": {
                    "row_field": row_field,
                    "column_field": column_field,
                    "value_field": value_field,
                    "agg_function": agg_function
                }
            }
        except Exception as e:
            return {"success": False, "error": f"透视表创建失败: {str(e)}"}
        finally:
            conn.close()

    def _aggregate(self, values: list, func: str) -> Any:
        if not values:
            return 0 if func == "COUNT" else None
        
        nums = [v for v in values if isinstance(v, (int, float))]
        
        if func == "COUNT":
            return len(values)
        elif func == "SUM":
            return sum(nums) if nums else None
        elif func == "AVG":
            return sum(nums) / len(nums) if nums else None
        return None

    def _evaluate_where(self, row: dict, where: str) -> bool:
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
                        elif op == ">":
                            return float(row_value) > float(value)
                        elif op == "<":
                            return float(row_value) < float(value)
                        elif op == ">=":
                            return float(row_value) >= float(value)
                        elif op == "<=":
                            return float(row_value) <= float(value)
                    except:
                        return str(row_value) == value
        return True


class RecommendChartTool:
    """推荐图表类型"""

    def get_name(self) -> str:
        return "pbbi_recommend_chart"

    def get_description(self) -> str:
        return "根据数据特征推荐合适的图表类型"

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
                    "description": "要分析的字段列表"
                }
            },
            "required": ["snapshot_id", "fields"]
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        fields = params.get("fields", [])

        if not snapshot_id:
            return {"success": False, "error": "snapshot_id是必需的"}

        if not fields:
            return {"success": False, "error": "fields是必需的"}

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

            field_types = {}
            for field in fields:
                for row_data in data:
                    val = row_data.get(field)
                    if val is not None:
                        if isinstance(val, int):
                            field_types[field] = "integer"
                        elif isinstance(val, float):
                            field_types[field] = "real"
                        else:
                            field_types[field] = "text"
                        break
                if field not in field_types:
                    field_types[field] = "text"

            total_rows = len(data)

            recommendations = []
            
            numeric_fields = [f for f, t in field_types.items() if t in ("integer", "real")]
            text_fields = [f for f, t in field_types.items() if t == "text"]

            if len(numeric_fields) >= 1 and len(text_fields) >= 1:
                recommendations.append({
                    "chart_type": "bar",
                    "reason": "适合展示分类数据的数值比较",
                    "x_field": text_fields[0],
                    "y_field": numeric_fields[0]
                })

            if len(numeric_fields) >= 2:
                recommendations.append({
                    "chart_type": "scatter",
                    "reason": "适合展示两个数值变量的关系",
                    "x_field": numeric_fields[0],
                    "y_field": numeric_fields[1]
                })

            if len(text_fields) >= 1:
                recommendations.append({
                    "chart_type": "pie",
                    "reason": "适合展示分类占比",
                    "category_field": text_fields[0]
                })

            if len(numeric_fields) >= 1:
                recommendations.append({
                    "chart_type": "histogram",
                    "reason": "适合展示数值分布",
                    "value_field": numeric_fields[0]
                })

            return {
                "success": True,
                "data": {
                    "field_types": field_types,
                    "total_rows": total_rows,
                    "recommendations": recommendations
                },
                "snapshot_name": name
            }
        except Exception as e:
            return {"success": False, "error": f"图表推荐失败: {str(e)}"}
        finally:
            conn.close()


def register_analysis_tools(mcp_service):
    """注册Analysis MCP工具"""
    tools = [
        AggregateDataTool(),
        FilterDataTool(),
        StatisticsTool(),
        PivotTableTool(),
        RecommendChartTool(),
    ]

    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)

    return tools
