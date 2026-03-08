"""
LLM客户端 - 调用DeepSeek API
"""

import httpx
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import os

@dataclass
class LLMConfig:
    api_key: str = ""
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "moonshot-v1-8k"
    max_tokens: int = 4096
    temperature: float = 0.7

class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._load_config()
    
    def _load_config(self):
        from src.core.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
        
        try:
            from src.core.database import SessionLocal
            from src.models.settings import SystemSettings
            from src.core.crypto import decrypt_value, is_encrypted
            
            db = SessionLocal()
            try:
                settings = db.query(SystemSettings).first()
                if settings:
                    if settings.ai_api_key:
                        api_key = decrypt_value(settings.ai_api_key) if is_encrypted(settings.ai_api_key) else settings.ai_api_key
                        self.config.api_key = api_key
                    if settings.ai_base_url:
                        self.config.base_url = settings.ai_base_url
                    if settings.ai_model:
                        self.config.model = settings.ai_model
                    try:
                        self.config.temperature = float(settings.ai_temperature)
                    except:
                        pass
                    if settings.ai_max_tokens:
                        self.config.max_tokens = settings.ai_max_tokens
                    return
            finally:
                db.close()
        except Exception as e:
            print(f"Load config from database error: {e}")
        
        self.config.api_key = LLM_API_KEY or self.config.api_key
        self.config.base_url = LLM_BASE_URL or self.config.base_url
        self.config.model = LLM_MODEL or self.config.model
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"LLM API error: {response.status_code} - {error_text.decode()}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
    
    async def chat_sync(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")
            
            return response.json()
    
    def get_tools_definition(self) -> List[Dict]:
        return [
            # Database MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_list_snapshots",
                    "description": "列出SQLite数据库中的所有数据快照。数据快照是保存的数据副本，可以用于离线查询和分析。返回快照ID、名称、表名、行数等信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_flow_id": {"type": "integer", "description": "按数据流ID筛选（可选）"},
                            "page": {"type": "integer", "description": "页码，默认1"},
                            "page_size": {"type": "integer", "description": "每页数量，默认20"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_snapshot_schema",
                    "description": "获取指定快照的表结构，包括字段名、字段类型、示例数据等信息。在查询快照数据前，先调用此工具了解数据结构。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "快照ID"},
                            "table_name": {"type": "string", "description": "快照表名（与snapshot_id二选一）"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_query_snapshot",
                    "description": "查询指定快照的数据，支持字段选择、条件筛选、排序和分页。这是主要的快照数据查询工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "快照ID"},
                            "table_name": {"type": "string", "description": "快照表名（与snapshot_id二选一）"},
                            "fields": {"type": "array", "items": {"type": "string"}, "description": "要查询的字段列表，默认查询所有字段"},
                            "where": {"type": "string", "description": "WHERE条件（SQL语法），如: age > 18 AND city = '北京'"},
                            "order_by": {"type": "string", "description": "排序字段，如: created_at DESC"},
                            "limit": {"type": "integer", "description": "返回行数限制，默认100"},
                            "offset": {"type": "integer", "description": "偏移量，用于分页"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_execute_sql",
                    "description": "在快照数据库上执行SQL查询语句（仅支持SELECT）。可用于复杂查询、聚合分析、多表关联等场景。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "SQL查询语句（仅支持SELECT）"},
                            "limit": {"type": "integer", "description": "返回行数限制，默认1000"}
                        },
                        "required": ["sql"]
                    }
                }
            },
            # MingDao MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_mingdao_connect",
                    "description": "连接明道云API，验证凭证并保存连接配置。需要提供appkey、sign和可选的base_url。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appkey": {"type": "string", "description": "明道云应用的AppKey"},
                            "sign": {"type": "string", "description": "明道云应用的Sign密钥"},
                            "base_url": {"type": "string", "description": "API基础URL，默认为 https://api.mingdao.com"},
                            "connection_name": {"type": "string", "description": "连接名称，用于后续引用，默认为 'default'"}
                        },
                        "required": ["appkey", "sign"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_mingdao_get_fields",
                    "description": "获取明道云工作表的字段列表，包括字段ID、名称、类型等信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "worksheet_id": {"type": "string", "description": "工作表ID"},
                            "connection_name": {"type": "string", "description": "连接名称，默认为 'default'"}
                        },
                        "required": ["worksheet_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_mingdao_get_rows",
                    "description": "获取明道云工作表的数据行，支持字段筛选和分页。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "worksheet_id": {"type": "string", "description": "工作表ID"},
                            "field_ids": {"type": "array", "items": {"type": "string"}, "description": "要获取的字段ID列表"},
                            "page_index": {"type": "integer", "description": "页码，默认1"},
                            "page_size": {"type": "integer", "description": "每页数量，默认100"},
                            "connection_name": {"type": "string", "description": "连接名称，默认为 'default'"}
                        },
                        "required": ["worksheet_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_mingdao_save_snapshot",
                    "description": "从明道云工作表获取数据并保存为本地快照，便于离线分析。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "worksheet_id": {"type": "string", "description": "工作表ID"},
                            "snapshot_name": {"type": "string", "description": "快照名称"},
                            "field_ids": {"type": "array", "items": {"type": "string"}, "description": "要保存的字段ID列表"},
                            "page_size": {"type": "integer", "description": "获取数据数量，默认1000"},
                            "connection_name": {"type": "string", "description": "连接名称，默认为 'default'"}
                        },
                        "required": ["worksheet_id", "snapshot_name"]
                    }
                }
            },
            # LocalFile MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_local_upload_file",
                    "description": "上传文件到服务器，支持CSV、Excel、JSON等格式。返回文件ID和基本信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_name": {"type": "string", "description": "文件名"},
                            "file_content": {"type": "string", "description": "文件内容（Base64编码或文本内容）"},
                            "file_type": {"type": "string", "description": "文件类型：csv, json, txt, excel", "enum": ["csv", "json", "txt", "excel"]},
                            "encoding": {"type": "string", "description": "文件编码，默认utf-8"}
                        },
                        "required": ["file_name", "file_content", "file_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_local_parse_file",
                    "description": "解析已上传的文件，提取数据和字段信息。支持CSV、JSON、Excel格式。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "文件ID（上传时返回的file_id）"},
                            "file_type": {"type": "string", "description": "文件类型：csv, json, excel"},
                            "preview_rows": {"type": "integer", "description": "预览行数，默认10"}
                        },
                        "required": ["file_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_local_list_files",
                    "description": "列出所有已上传的文件。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_type": {"type": "string", "description": "按文件类型筛选：csv, json, excel"}
                        },
                        "required": []
                    }
                }
            },
            # DataFlow MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_list_dataflows",
                    "description": "列出PB-BI系统中配置的所有数据流，支持分页和类型筛选。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "description": "按数据流类型筛选：mingdao, local_file, api"},
                            "page": {"type": "integer", "description": "页码，默认1"},
                            "page_size": {"type": "integer", "description": "每页数量，默认20"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_dataflow",
                    "description": "获取指定数据流的详细信息，包括字段列表。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dataflow_id": {"type": "integer", "description": "数据流ID"}
                        },
                        "required": ["dataflow_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_dataflow_snapshots",
                    "description": "获取指定数据流关联的所有快照。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dataflow_id": {"type": "integer", "description": "数据流ID"}
                        },
                        "required": ["dataflow_id"]
                    }
                }
            },
            # Analysis MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_aggregate_data",
                    "description": "对快照数据进行聚合分析，支持SUM、AVG、COUNT、MAX、MIN等聚合函数。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "快照ID"},
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
                            "group_by": {"type": "array", "items": {"type": "string"}, "description": "分组字段列表"},
                            "where": {"type": "string", "description": "筛选条件"}
                        },
                        "required": ["aggregations"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_statistics",
                    "description": "计算数值字段的统计描述，包括均值、中位数、标准差、最大值、最小值等。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "快照ID"},
                            "field": {"type": "string", "description": "要统计的数值字段"},
                            "where": {"type": "string", "description": "筛选条件"}
                        },
                        "required": ["field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_recommend_chart",
                    "description": "根据数据特征推荐合适的图表类型。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "快照ID"},
                            "fields": {"type": "array", "items": {"type": "string"}, "description": "要分析的字段列表"}
                        },
                        "required": ["fields"]
                    }
                }
            },
            # Dashboard MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_list_dashboards",
                    "description": "列出PB-BI系统中所有已创建的数据看板。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "description": "页码，默认1"},
                            "page_size": {"type": "integer", "description": "每页数量，默认20"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_dashboard",
                    "description": "获取指定看板的详细信息，包括配置信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dashboard_id": {"type": "integer", "description": "看板ID"}
                        },
                        "required": ["dashboard_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_create_dashboard",
                    "description": "创建新的数据看板。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "看板名称"},
                            "chart_type": {"type": "string", "description": "图表类型：line, bar, pie, scatter等"},
                            "config": {"type": "object", "description": "看板配置"},
                            "data_snapshot_id": {"type": "integer", "description": "关联的数据快照ID"}
                        },
                        "required": ["name", "chart_type"]
                    }
                }
            },
            # User MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_current_user",
                    "description": "获取当前登录用户的基本信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_get_user_resources",
                    "description": "获取当前用户可访问的资源统计，包括数据流、快照、看板数量。",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            # Chart MCP Tools
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_bar_chart",
                    "description": "根据数据生成柱状图，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "title": {"type": "string", "description": "图表标题"},
                            "aggregation": {"type": "string", "description": "聚合方式：sum, avg, count"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_pie_chart",
                    "description": "根据数据生成饼图,返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "category_field": {"type": "string", "description": "分类字段名"},
                            "value_field": {"type": "string", "description": "数值字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "category_field", "value_field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_line_chart",
                    "description": "根据数据生成折线图,返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_box_plot",
                    "description": "根据数据生成箱线图,返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "field": {"type": "string", "description": "要绘制箱线图的字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "field"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_scatter_chart",
                    "description": "根据数据生成散点图,返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field"]
                    }
                }
            },
            # 新增图表工具 - 直方图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_histogram",
                    "description": "根据数据生成直方图，用于展示数据分布，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "field": {"type": "string", "description": "数值字段名"},
                            "bins": {"type": "integer", "description": "分组数量（默认10）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "field"]
                    }
                }
            },
            # 新增图表工具 - 热力图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_heatmap",
                    "description": "根据数据生成热力图，用于展示相关性或密度分布，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "value_field": {"type": "string", "description": "数值字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field", "value_field"]
                    }
                }
            },
            # 新增图表工具 - 雷达图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_radar_chart",
                    "description": "根据数据生成雷达图，用于多维度评估对比，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "category_field": {"type": "string", "description": "分类字段名"},
                            "value_field": {"type": "string", "description": "数值字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "category_field", "value_field"]
                    }
                }
            },
            # 新增图表工具 - 漏斗图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_funnel_chart",
                    "description": "根据数据生成漏斗图，用于转化率分析，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "stage_field": {"type": "string", "description": "阶段字段名"},
                            "value_field": {"type": "string", "description": "数值字段名"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "stage_field", "value_field"]
                    }
                }
            },
            # 新增图表工具 - 仪表盘
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_gauge_chart",
                    "description": "根据数据生成仪表盘，用于KPI指标展示，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "value_field": {"type": "string", "description": "数值字段名"},
                            "min_value": {"type": "number", "description": "最小值（默认0）"},
                            "max_value": {"type": "number", "description": "最大值（默认100）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "value_field"]
                    }
                }
            },
            # 新增图表工具 - 组合图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_combo_chart",
                    "description": "根据数据生成组合图（柱状图+折线图），用于多指标对比，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "bar_field": {"type": "string", "description": "柱状图数值字段"},
                            "line_field": {"type": "string", "description": "折线图数值字段"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "bar_field", "line_field"]
                    }
                }
            },
            # 新增图表工具 - 3D柱状图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_bar_3d_chart",
                    "description": "根据数据生成3D柱状图，支持透明效果和颜色映射，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "z_field": {"type": "string", "description": "Z轴字段名（数值类型）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field", "z_field"]
                    }
                }
            },
            # 新增图表工具 - 3D散点图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_scatter_3d_chart",
                    "description": "根据数据生成3D散点图，用于展示三维数据关系，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名（数值类型）"},
                            "y_field": {"type": "string", "description": "Y轴字段名（数值类型）"},
                            "z_field": {"type": "string", "description": "Z轴字段名（数值类型）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field", "z_field"]
                    }
                }
            },
            # 新增图表工具 - 3D曲面图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_surface_3d_chart",
                    "description": "根据数据生成3D曲面图，用于展示三维形貌数据，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "z_field": {"type": "string", "description": "Z轴字段名（数值类型）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field", "z_field"]
                    }
                }
            },
            # 新增图表工具 - LED晶圆图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_led_wafer_chart",
                    "description": "根据数据生成LED晶圆分析图，支持波长到RGB颜色转换，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_field": {"type": "string", "description": "Y轴字段名"},
                            "z_field": {"type": "string", "description": "Z轴字段名（数值类型）"},
                            "wavelength_field": {"type": "string", "description": "波长字段名（纳米）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_field", "z_field"]
                    }
                }
            },
            # 新增图表工具 - 多Y轴图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_multiple_y_axis_chart",
                    "description": "根据数据生成多Y轴图，支持多个数值字段在不同Y轴上展示，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段，至少2个）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_fields"]
                    }
                }
            },
            # 新增图表工具 - 堆叠柱状图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_stacked_bar_chart",
                    "description": "根据数据生成堆叠柱状图，支持多个数值字段堆叠展示，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段，至少2个）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_fields"]
                    }
                }
            },
            # 新增图表工具 - 堆叠折线图
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_stacked_line_chart",
                    "description": "根据数据生成堆叠折线图，支持多个数值字段堆叠展示趋势，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段，至少2个）"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "y_fields"]
                    }
                }
            },
            # 新增图表工具 - 联动图表
            {
                "type": "function",
                "function": {
                    "name": "pbbi_generate_linked_chart",
                    "description": "根据数据生成联动图表，折线图与饼图联动展示，返回图表URL。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                            "x_field": {"type": "string", "description": "X轴字段名"},
                            "name_field": {"type": "string", "description": "名称字段（用于饼图分类）"},
                            "value_field": {"type": "string", "description": "数值字段"},
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["snapshot_id", "x_field", "name_field", "value_field"]
                    }
                }
            }
        ]
