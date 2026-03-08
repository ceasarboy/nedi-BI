"""
Chart MCP - 图表生成工具
提供数据可视化图表生成能力，支持多种图表类型
"""

from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
import json
import sqlite3
import time
import hashlib
from pathlib import Path
import os

from src.mcp.service import MCPTool
from src.core.config import CONFIG_DIR


MAIN_DB_PATH = CONFIG_DIR / "pb_bi.db"
CHARTS_DIR = CONFIG_DIR / "charts"
Path(CHARTS_DIR).mkdir(parents=True, exist_ok=True)

CHART_CACHE = {}
CHART_CACHE_MAX_SIZE = 100

_chinese_font_configured = False


class BaseChartTool(ABC):
    """图表工具基类，提供统一的接口和通用功能"""
    
    @abstractmethod
    def get_name(self) -> str:
        """返回工具名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """返回工具描述"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """返回工具参数定义"""
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行图表生成"""
        pass
    
    def get_chart_type(self) -> str:
        """返回图表类型标识"""
        return self.get_name().replace("pbbi_generate_", "")
    
    def _get_data_from_snapshot(self, snapshot_id: int) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """从快照获取数据"""
        conn = _get_main_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, data FROM data_snapshots WHERE id = ?",
                (snapshot_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None, f"快照不存在: id={snapshot_id}"
            
            data = json.loads(row["data"]) if row["data"] else []
            if not data:
                return None, "快照没有数据"
            return data, None
        finally:
            conn.close()
    
    def _create_result(self, chart_type: str, chart_url: str, title: str, 
                       data: Dict = None, statistics: Dict = None) -> Dict[str, Any]:
        """创建标准返回结果"""
        # 如果是相对路径，转换为完整URL
        if chart_url.startswith("/api/charts/"):
            full_url = f"http://localhost:8001{chart_url}"
        else:
            full_url = chart_url
        
        result = {
            "success": True,
            "chart_type": chart_type,
            "chart_url": full_url,
            "title": title
        }
        if data:
            result["data"] = data
        if statistics:
            result["statistics"] = statistics
        return result
    
    def _create_error(self, error_msg: str) -> Dict[str, Any]:
        """创建错误返回结果"""
        return {"success": False, "error": error_msg}


def _setup_chinese_font():
    """配置matplotlib中文字体"""
    global _chinese_font_configured
    if _chinese_font_configured:
        return
    
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import platform
        
        system = platform.system()
        
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc"
            ]
        elif system == "Darwin":
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/Library/Fonts/Arial Unicode.ttf"
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
        
        font_path = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_path = fp
                break
        
        if font_path:
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
        else:
            plt.rcParams['axes.unicode_minus'] = False
        
        _chinese_font_configured = True
    except Exception as e:
        print(f"配置中文字体失败: {e}")


def _get_main_db_connection():
    """获取主数据库连接（pb_bi.db）"""
    conn = sqlite3.connect(str(MAIN_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _get_chart_cache_key(chart_type: str, params: dict) -> str:
    """生成图表缓存键"""
    key_data = f"{chart_type}_{json.dumps(params, sort_keys=True, ensure_ascii=False)}"
    return hashlib.md5(key_data.encode()).hexdigest()


def _check_chart_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """检查图表缓存"""
    if cache_key in CHART_CACHE:
        return CHART_CACHE[cache_key]
    return None


def _save_to_cache(cache_key: str, result: Dict[str, Any]):
    """保存图表到缓存"""
    if len(CHART_CACHE) >= CHART_CACHE_MAX_SIZE:
        oldest_key = next(iter(CHART_CACHE))
        del CHART_CACHE[oldest_key]
    CHART_CACHE[cache_key] = result


def _validate_numeric_field(df, field_name: str) -> Tuple[bool, Optional[str]]:
    """验证字段是否为数值类型"""
    import pandas as pd
    
    if field_name not in df.columns:
        return False, f"字段 '{field_name}' 不存在"
    
    series = df[field_name]
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return False, f"字段 '{field_name}' 没有有效数据"
        return True, None
    
    try:
        pd.to_numeric(series, errors='raise')
        return True, None
    except:
        return False, f"字段 '{field_name}' 不是数值类型，无法用于此图表"


def _clean_old_charts(days: int = 7):
    """清理旧图表文件"""
    try:
        current_time = time.time()
        for chart_file in CHARTS_DIR.glob("chart_*.png"):
            file_age = current_time - chart_file.stat().st_mtime
            if file_age > days * 24 * 3600:
                chart_file.unlink()
    except Exception as e:
        print(f"清理旧图表失败: {e}")


# ============== 基础图表工具 ==============

class GenerateBarChartTool(BaseChartTool):
    """生成柱状图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_bar_chart"
    
    def get_description(self) -> str:
        return "根据数据生成柱状图，支持聚合、分组、堆叠等功能"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_field": {"type": "string", "description": "Y轴字段名（数值类型）"},
                "title": {"type": "string", "description": "图表标题"},
                "aggregation": {"type": "string", "description": "聚合方式：sum, avg, count", "enum": ["sum", "avg", "count"]},
                "stacked": {"type": "boolean", "description": "是否堆叠显示"},
                "horizontal": {"type": "boolean", "description": "是否水平显示"}
            },
            "required": ["snapshot_id", "x_field", "y_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field") or params.get("x_axis_field")
        y_field = params.get("y_field") or params.get("y_axis_field")
        title = params.get("title", "柱状图")
        aggregation = params.get("aggregation", "sum")
        stacked = params.get("stacked", False)
        horizontal = params.get("horizontal", False)
        
        if not snapshot_id or not x_field or not y_field:
            return self._create_error("snapshot_id, x_field (或 x_axis_field), y_field (或 y_axis_field) 是必需的")
        
        cache_key = _get_chart_cache_key("bar", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            
            is_numeric, error = _validate_numeric_field(df, y_field)
            if not is_numeric:
                return self._create_error(f"Y轴字段验证失败: {error}")
            
            df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
            df = df.dropna(subset=[y_field])
            
            _setup_chinese_font()
            
            if aggregation == "sum":
                grouped = df.groupby(x_field)[y_field].sum().reset_index()
            elif aggregation == "avg":
                grouped = df.groupby(x_field)[y_field].mean().reset_index()
            else:
                grouped = df.groupby(x_field)[y_field].count().reset_index()
            
            x_labels = grouped[x_field].tolist()
            y_values = grouped[y_field].tolist()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if horizontal:
                ax.barh(range(len(x_labels)), y_values, color='steelblue')
                ax.set_yticks(range(len(x_labels)))
                ax.set_yticklabels([str(x) for x in x_labels])
                ax.set_xlabel(y_field)
                ax.set_ylabel(x_field)
            else:
                ax.bar(range(len(x_labels)), y_values, color='steelblue', edgecolor='white')
                ax.set_xticks(range(len(x_labels)))
                ax.set_xticklabels([str(x) for x in x_labels], rotation=45, ha='right')
                ax.set_xlabel(x_field)
                ax.set_ylabel(y_field)
            
            ax.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_bar_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("bar", f"/api/charts/{chart_filename}", title, 
                                        {"x_labels": x_labels[:10], "y_values": y_values[:10]})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GeneratePieChartTool(BaseChartTool):
    """生成饼图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_pie_chart"
    
    def get_description(self) -> str:
        return "根据数据生成饼图，支持环形图、嵌套饼图"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "category_field": {"type": "string", "description": "分类字段名"},
                "value_field": {"type": "string", "description": "数值字段名"},
                "title": {"type": "string", "description": "图表标题"},
                "donut": {"type": "boolean", "description": "是否环形图"},
                "show_percentage": {"type": "boolean", "description": "是否显示百分比"}
            },
            "required": ["snapshot_id", "category_field", "value_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        category_field = params.get("category_field") or params.get("name_field") or params.get("x_axis_field")
        value_field = params.get("value_field") or params.get("y_axis_field")
        title = params.get("title", "饼图")
        donut = params.get("donut", False)
        
        if not snapshot_id or not category_field or not value_field:
            return self._create_error("snapshot_id, category_field (或 name_field), value_field (或 y_axis_field) 是必需的")
        
        cache_key = _get_chart_cache_key("pie", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            if category_field not in df.columns:
                return self._create_error(f"分类字段 '{category_field}' 不存在")
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            df = df.dropna(subset=[value_field])
            
            grouped = df.groupby(category_field)[value_field].sum()
            labels = grouped.index.tolist()
            values = grouped.values.tolist()
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if donut:
                wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                                   startangle=90, wedgeprops=dict(width=0.5))
            else:
                wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            
            ax.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_pie_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("pie", f"/api/charts/{chart_filename}", title,
                                        {"labels": labels[:10], "values": values[:10]})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateLineChartTool(BaseChartTool):
    """生成折线图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_line_chart"
    
    def get_description(self) -> str:
        return "根据数据生成折线图，支持多系列、面积图"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_field": {"type": "string", "description": "Y轴字段名（数值类型）"},
                "title": {"type": "string", "description": "图表标题"},
                "show_area": {"type": "boolean", "description": "是否显示面积"},
                "show_markers": {"type": "boolean", "description": "是否显示数据点标记"}
            },
            "required": ["snapshot_id", "x_field", "y_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field") or params.get("x_axis_field")
        y_field = params.get("y_field") or params.get("y_axis_field")
        title = params.get("title", "折线图")
        show_area = params.get("show_area", False)
        show_markers = params.get("show_markers", True)
        
        if not snapshot_id or not x_field or not y_field:
            return self._create_error("snapshot_id, x_field (或 x_axis_field), y_field (或 y_axis_field) 是必需的")
        
        cache_key = _get_chart_cache_key("line", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            
            is_numeric, error = _validate_numeric_field(df, y_field)
            if not is_numeric:
                return self._create_error(f"Y轴字段验证失败: {error}")
            
            df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
            df = df.dropna(subset=[y_field])
            
            x_data = df[x_field].tolist()
            y_data = df[y_field].tolist()
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if show_area:
                ax.fill_between(range(len(x_data)), y_data, alpha=0.3, color='steelblue')
            
            marker = 'o' if show_markers else None
            ax.plot(range(len(x_data)), y_data, marker=marker, color='steelblue', linewidth=2)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_title(title)
            ax.set_xticks(range(len(x_data)))
            ax.set_xticklabels([str(x) for x in x_data], rotation=45, ha='right')
            plt.tight_layout()
            
            chart_filename = f"chart_line_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("line", f"/api/charts/{chart_filename}", title,
                                        {"x_data": x_data[:10], "y_data": y_data[:10]})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateScatterChartTool(BaseChartTool):
    """生成散点图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_scatter_chart"
    
    def get_description(self) -> str:
        return "根据数据生成散点图，支持气泡图、颜色映射"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名（数值类型）"},
                "y_field": {"type": "string", "description": "Y轴字段名（数值类型）"},
                "size_field": {"type": "string", "description": "气泡大小字段（可选）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "x_field", "y_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field") or params.get("x_axis_field")
        y_field = params.get("y_field") or params.get("y_axis_field")
        size_field = params.get("size_field")
        title = params.get("title", "散点图")
        
        if not snapshot_id or not x_field or not y_field:
            return self._create_error("snapshot_id, x_field (或 x_axis_field), y_field (或 y_axis_field) 是必需的")
        
        cache_key = _get_chart_cache_key("scatter", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            is_numeric_x, error_x = _validate_numeric_field(df, x_field)
            if not is_numeric_x:
                return self._create_error(f"X轴字段验证失败: {error_x}")
            
            is_numeric_y, error_y = _validate_numeric_field(df, y_field)
            if not is_numeric_y:
                return self._create_error(f"Y轴字段验证失败: {error_y}")
            
            df[x_field] = pd.to_numeric(df[x_field], errors='coerce')
            df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
            df = df.dropna(subset=[x_field, y_field])
            
            x_data = df[x_field].tolist()
            y_data = df[y_field].tolist()
            
            sizes = None
            if size_field and size_field in df.columns:
                sizes = pd.to_numeric(df[size_field], errors='coerce').fillna(50).tolist()
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if sizes:
                ax.scatter(x_data, y_data, s=sizes, alpha=0.6, c='steelblue')
            else:
                ax.scatter(x_data, y_data, alpha=0.6, s=50, c='steelblue')
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_scatter_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("scatter", f"/api/charts/{chart_filename}", title,
                                        {"data_count": len(x_data)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateBoxPlotTool(BaseChartTool):
    """生成箱线图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_box_plot"
    
    def get_description(self) -> str:
        return "根据数据生成箱线图，支持分组箱线图"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "field": {"type": "string", "description": "数值字段名"},
                "group_field": {"type": "string", "description": "分组字段（可选）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        field = params.get("field")
        group_field = params.get("group_field")
        title = params.get("title", "箱线图")
        
        if not snapshot_id or not field:
            return self._create_error("snapshot_id, field是必需的")
        
        cache_key = _get_chart_cache_key("box", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, field)
            if not is_numeric:
                return self._create_error(f"字段验证失败: {error}")
            
            df[field] = pd.to_numeric(df[field], errors='coerce')
            df = df.dropna(subset=[field])
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if group_field and group_field in df.columns:
                groups = df.groupby(group_field)[field].apply(list).to_dict()
                labels = list(groups.keys())
                data_list = list(groups.values())
                bp = ax.boxplot(data_list, labels=labels, vert=True, patch_artist=True)
            else:
                values = df[field].tolist()
                if len(values) < 3:
                    return self._create_error("数据点太少，至少需要3个数据点")
                bp = ax.boxplot(values, vert=True, patch_artist=True)
                labels = [field]
                ax.set_xticklabels(labels)
            
            for box in bp['boxes']:
                box.set_facecolor('lightsteelblue')
            
            ax.set_ylabel(field)
            ax.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_box_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            stats = {
                "count": len(df[field].dropna()),
                "mean": float(df[field].mean()),
                "std": float(df[field].std())
            }
            
            result = self._create_result("box", f"/api/charts/{chart_filename}", title, statistics=stats)
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateHistogramTool(BaseChartTool):
    """生成直方图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_histogram"
    
    def get_description(self) -> str:
        return "根据数据生成直方图，用于展示数据分布"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "field": {"type": "string", "description": "数值字段名"},
                "bins": {"type": "integer", "description": "分组数量（默认10）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        field = params.get("field")
        bins = params.get("bins", 10)
        title = params.get("title", "直方图")
        
        if not snapshot_id or not field:
            return self._create_error("snapshot_id, field是必需的")
        
        cache_key = _get_chart_cache_key("histogram", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, field)
            if not is_numeric:
                return self._create_error(f"字段验证失败: {error}")
            
            df[field] = pd.to_numeric(df[field], errors='coerce')
            values = df[field].dropna().tolist()
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(values, bins=bins, color='steelblue', edgecolor='white', alpha=0.7)
            ax.set_xlabel(field)
            ax.set_ylabel("频数")
            ax.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_histogram_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("histogram", f"/api/charts/{chart_filename}", title,
                                        {"bins": bins, "count": len(values)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateHeatmapTool(BaseChartTool):
    """生成热力图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_heatmap"
    
    def get_description(self) -> str:
        return "根据数据生成热力图，用于展示相关性或密度分布"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_field = params.get("y_field")
        value_field = params.get("value_field")
        title = params.get("title", "热力图")
        
        if not snapshot_id or not x_field or not y_field or not value_field:
            return self._create_error("snapshot_id, x_field, y_field, value_field是必需的")
        
        if x_field == y_field:
            return self._create_error("x_field和y_field不能是同一个字段")
        
        cache_key = _get_chart_cache_key("heatmap", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            df = df.dropna(subset=[value_field])
            
            pivot = df.pivot_table(values=value_field, index=y_field, columns=x_field, aggfunc='mean')
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(12, 8))
            im = ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
            
            ax.set_xticks(range(len(pivot.columns)))
            ax.set_yticks(range(len(pivot.index)))
            ax.set_xticklabels([str(c) for c in pivot.columns], rotation=45, ha='right')
            ax.set_yticklabels([str(i) for i in pivot.index])
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_title(title)
            
            plt.colorbar(im, ax=ax)
            plt.tight_layout()
            
            chart_filename = f"chart_heatmap_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("heatmap", f"/api/charts/{chart_filename}", title,
                                        {"rows": len(pivot.index), "cols": len(pivot.columns)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateRadarChartTool(BaseChartTool):
    """生成雷达图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_radar_chart"
    
    def get_description(self) -> str:
        return "根据数据生成雷达图，用于多维度评估对比"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "category_field": {"type": "string", "description": "维度字段名"},
                "value_field": {"type": "string", "description": "数值字段名"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "category_field", "value_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        category_field = params.get("category_field")
        value_field = params.get("value_field")
        title = params.get("title", "雷达图")
        
        if not snapshot_id or not category_field or not value_field:
            return self._create_error("snapshot_id, category_field, value_field是必需的")
        
        cache_key = _get_chart_cache_key("radar", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            df = df.dropna(subset=[value_field])
            
            categories = df[category_field].tolist()
            values = df[value_field].tolist()
            
            if len(categories) < 3:
                return self._create_error("雷达图至少需要3个维度")
            
            _setup_chinese_font()
            
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values_plot = values + [values[0]]
            angles += angles[:1]
            categories_plot = categories + [categories[0]]
            
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            ax.plot(angles, values_plot, 'o-', linewidth=2, color='steelblue')
            ax.fill(angles, values_plot, alpha=0.25, color='steelblue')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_title(title)
            
            chart_filename = f"chart_radar_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("radar", f"/api/charts/{chart_filename}", title,
                                        {"categories": categories, "values": values})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateFunnelChartTool(BaseChartTool):
    """生成漏斗图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_funnel_chart"
    
    def get_description(self) -> str:
        return "根据数据生成漏斗图，用于转化率分析"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "stage_field": {"type": "string", "description": "阶段字段名"},
                "value_field": {"type": "string", "description": "数值字段名"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "stage_field", "value_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        stage_field = params.get("stage_field")
        value_field = params.get("value_field")
        title = params.get("title", "漏斗图")
        
        if not snapshot_id or not stage_field or not value_field:
            return self._create_error("snapshot_id, stage_field, value_field是必需的")
        
        cache_key = _get_chart_cache_key("funnel", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            import numpy as np
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            df = df.dropna(subset=[value_field])
            df = df.sort_values(value_field, ascending=False)
            
            stages = df[stage_field].tolist()
            values = df[value_field].tolist()
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_xlim(0, max(values) * 1.2)
            ax.set_ylim(0, len(stages) * 1.5)
            
            max_val = max(values)
            colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(stages)))
            
            for i, (stage, val) in enumerate(zip(stages, values)):
                width = val / max_val * max_val
                left = (max_val - width) / 2
                rect = mpatches.FancyBboxPatch(
                    (left, len(stages) * 1.5 - i * 1.5 - 1),
                    width, 0.8,
                    boxstyle="round,pad=0.05",
                    facecolor=colors[i],
                    edgecolor='white',
                    linewidth=2
                )
                ax.add_patch(rect)
                ax.text(max_val * 0.6, len(stages) * 1.5 - i * 1.5 - 0.6, 
                       f"{stage}: {val}", fontsize=12, va='center')
            
            ax.axis('off')
            ax.set_title(title)
            
            chart_filename = f"chart_funnel_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("funnel", f"/api/charts/{chart_filename}", title,
                                        {"stages": stages, "values": values})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateGaugeChartTool(BaseChartTool):
    """生成仪表盘"""
    
    def get_name(self) -> str:
        return "pbbi_generate_gauge_chart"
    
    def get_description(self) -> str:
        return "根据数据生成仪表盘，用于KPI指标展示"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "value_field": {"type": "string", "description": "数值字段名"},
                "title": {"type": "string", "description": "图表标题"},
                "min_value": {"type": "number", "description": "最小值（默认0）"},
                "max_value": {"type": "number", "description": "最大值（默认100）"},
                "thresholds": {"type": "array", "description": "阈值区间，如[0.3, 0.7]表示30%和70%为分界点"}
            },
            "required": ["snapshot_id", "value_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        value_field = params.get("value_field")
        title = params.get("title", "仪表盘")
        min_value = params.get("min_value", 0)
        max_value = params.get("max_value", 100)
        thresholds = params.get("thresholds", [0.3, 0.7])
        
        if not snapshot_id or not value_field:
            return self._create_error("snapshot_id, value_field是必需的")
        
        cache_key = _get_chart_cache_key("gauge", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            value = df[value_field].iloc[0] if len(df) > 0 else 0
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))
            
            theta = np.linspace(0.75 * np.pi, 0.25 * np.pi, 100)
            
            ax.fill_between(theta, 0, 1, alpha=0.3, color='gray')
            
            value_ratio = (value - min_value) / (max_value - min_value)
            value_ratio = max(0, min(1, value_ratio))
            
            value_theta = np.linspace(0.75 * np.pi, 0.75 * np.pi - value_ratio * 0.5 * np.pi, 50)
            ax.fill_between(value_theta, 0, 1, alpha=0.8, color='steelblue')
            
            ax.set_ylim(0, 1.5)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.spines['polar'].set_visible(False)
            
            ax.text(0.5 * np.pi, 0.3, f'{value:.1f}', fontsize=24, ha='center', va='center', 
                   fontweight='bold', transform=ax.transData)
            ax.text(0.5 * np.pi, 0.1, title, fontsize=14, ha='center', va='center',
                   transform=ax.transData)
            
            chart_filename = f"chart_gauge_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("gauge", f"/api/charts/{chart_filename}", title,
                                        {"value": value, "min": min_value, "max": max_value})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateComboChartTool(BaseChartTool):
    """生成组合图（柱状图+折线图）"""
    
    def get_name(self) -> str:
        return "pbbi_generate_combo_chart"
    
    def get_description(self) -> str:
        return "根据数据生成组合图，柱状图和折线图组合展示"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        bar_field = params.get("bar_field")
        line_field = params.get("line_field")
        title = params.get("title", "组合图")
        
        if not snapshot_id or not x_field or not bar_field or not line_field:
            return self._create_error("snapshot_id, x_field, bar_field, line_field是必需的")
        
        cache_key = _get_chart_cache_key("combo", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            is_numeric_bar, error_bar = _validate_numeric_field(df, bar_field)
            if not is_numeric_bar:
                return self._create_error(f"柱状图字段验证失败: {error_bar}")
            
            is_numeric_line, error_line = _validate_numeric_field(df, line_field)
            if not is_numeric_line:
                return self._create_error(f"折线图字段验证失败: {error_line}")
            
            df[bar_field] = pd.to_numeric(df[bar_field], errors='coerce')
            df[line_field] = pd.to_numeric(df[line_field], errors='coerce')
            df = df.dropna(subset=[bar_field, line_field])
            
            x_data = df[x_field].tolist()
            bar_data = df[bar_field].tolist()
            line_data = df[line_field].tolist()
            
            _setup_chinese_font()
            
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            ax1.bar(range(len(x_data)), bar_data, color='steelblue', alpha=0.7, label=bar_field)
            ax1.set_xlabel(x_field)
            ax1.set_ylabel(bar_field, color='steelblue')
            ax1.tick_params(axis='y', labelcolor='steelblue')
            
            ax2 = ax1.twinx()
            ax2.plot(range(len(x_data)), line_data, color='red', marker='o', linewidth=2, label=line_field)
            ax2.set_ylabel(line_field, color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            
            ax1.set_xticks(range(len(x_data)))
            ax1.set_xticklabels([str(x) for x in x_data], rotation=45, ha='right')
            
            fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.9))
            ax1.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_combo_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("combo", f"/api/charts/{chart_filename}", title,
                                        {"x_data": x_data[:10], "bar_data": bar_data[:10], "line_data": line_data[:10]})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateBar3DChartTool(BaseChartTool):
    """生成3D柱状图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_bar_3d_chart"
    
    def get_description(self) -> str:
        return "根据数据生成3D柱状图，支持透明效果和颜色映射"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_field": {"type": "string", "description": "Y轴字段名"},
                "z_field": {"type": "string", "description": "Z轴字段名（数值类型）"},
                "title": {"type": "string", "description": "图表标题"},
                "opacity": {"type": "number", "description": "透明度（0-1，默认0.7）"}
            },
            "required": ["snapshot_id", "x_field", "y_field", "z_field"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_field = params.get("y_field")
        z_field = params.get("z_field")
        title = params.get("title", "3D柱状图")
        opacity = params.get("opacity", 0.7)
        
        if not snapshot_id or not x_field or not y_field or not z_field:
            return self._create_error("snapshot_id, x_field, y_field, z_field是必需的")
        
        cache_key = _get_chart_cache_key("bar_3d", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            if y_field not in df.columns:
                return self._create_error(f"Y轴字段 '{y_field}' 不存在")
            
            is_numeric, error = _validate_numeric_field(df, z_field)
            if not is_numeric:
                return self._create_error(f"Z轴字段验证失败: {error}")
            
            df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
            df = df.dropna(subset=[z_field])
            
            x_categories = sorted(df[x_field].unique().tolist())
            y_categories = sorted(df[y_field].unique().tolist())
            
            x_map = {v: i for i, v in enumerate(x_categories)}
            y_map = {v: i for i, v in enumerate(y_categories)}
            
            _setup_chinese_font()
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            xpos = [x_map[row[x_field]] for _, row in df.iterrows()]
            ypos = [y_map[row[y_field]] for _, row in df.iterrows()]
            zpos = [0] * len(df)
            dx = dy = 0.8
            dz = df[z_field].tolist()
            
            colors = plt.cm.viridis(np.array(dz) / max(dz) if max(dz) > 0 else np.zeros(len(dz)))
            
            ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, alpha=opacity)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_zlabel(z_field)
            ax.set_title(title)
            
            ax.set_xticks(range(len(x_categories)))
            ax.set_xticklabels([str(x) for x in x_categories], rotation=45)
            ax.set_yticks(range(len(y_categories)))
            ax.set_yticklabels([str(y) for y in y_categories])
            
            chart_filename = f"chart_bar_3d_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("bar_3d", f"/api/charts/{chart_filename}", title,
                                        {"x_categories": x_categories, "y_categories": y_categories, "data_points": len(df)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateScatter3DChartTool(BaseChartTool):
    """生成3D散点图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_scatter_3d_chart"
    
    def get_description(self) -> str:
        return "根据数据生成3D散点图，用于展示三维数据关系"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_field = params.get("y_field")
        z_field = params.get("z_field")
        title = params.get("title", "3D散点图")
        
        if not snapshot_id or not x_field or not y_field or not z_field:
            return self._create_error("snapshot_id, x_field, y_field, z_field是必需的")
        
        cache_key = _get_chart_cache_key("scatter_3d", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            df = pd.DataFrame(data)
            
            for field in [x_field, y_field, z_field]:
                is_numeric, error = _validate_numeric_field(df, field)
                if not is_numeric:
                    return self._create_error(f"字段 '{field}' 验证失败: {error}")
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            df = df.dropna(subset=[x_field, y_field, z_field])
            
            _setup_chinese_font()
            
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            x_data = df[x_field].tolist()
            y_data = df[y_field].tolist()
            z_data = df[z_field].tolist()
            
            colors = plt.cm.plasma(np.linspace(0, 1, len(x_data)))
            
            ax.scatter(x_data, y_data, z_data, c=colors, s=50, alpha=0.8)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_zlabel(z_field)
            ax.set_title(title)
            
            chart_filename = f"chart_scatter_3d_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("scatter_3d", f"/api/charts/{chart_filename}", title,
                                        {"data_count": len(x_data)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateSurface3DChartTool(BaseChartTool):
    """生成3D曲面图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_surface_3d_chart"
    
    def get_description(self) -> str:
        return "根据数据生成3D曲面图，用于展示三维形貌数据"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_field = params.get("y_field")
        z_field = params.get("z_field")
        title = params.get("title", "3D曲面图")
        
        if not snapshot_id or not x_field or not y_field or not z_field:
            return self._create_error("snapshot_id, x_field, y_field, z_field是必需的")
        
        cache_key = _get_chart_cache_key("surface_3d", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            from scipy.interpolate import griddata
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, z_field)
            if not is_numeric:
                return self._create_error(f"Z轴字段验证失败: {error}")
            
            df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
            df = df.dropna(subset=[z_field])
            
            x_vals = df[x_field].astype(float).values if df[x_field].dtype in ['int64', 'float64'] else pd.factorize(df[x_field])[0]
            y_vals = df[y_field].astype(float).values if df[y_field].dtype in ['int64', 'float64'] else pd.factorize(df[y_field])[0]
            z_vals = df[z_field].values
            
            xi = np.linspace(min(x_vals), max(x_vals), 50)
            yi = np.linspace(min(y_vals), max(y_vals), 50)
            Xi, Yi = np.meshgrid(xi, yi)
            Zi = griddata((x_vals, y_vals), z_vals, (Xi, Yi), method='cubic')
            
            _setup_chinese_font()
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            surf = ax.plot_surface(Xi, Yi, Zi, cmap='viridis', alpha=0.8, antialiased=True)
            
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_zlabel(z_field)
            ax.set_title(title)
            
            chart_filename = f"chart_surface_3d_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("surface_3d", f"/api/charts/{chart_filename}", title,
                                        {"grid_size": "50x50"})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateLEDWaferChartTool(BaseChartTool):
    """生成LED晶圆分析图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_led_wafer_chart"
    
    def get_description(self) -> str:
        return "根据数据生成LED晶圆分析图，支持波长到RGB颜色转换"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def _wavelength_to_rgb(self, wavelength):
        """波长转RGB颜色"""
        if wavelength < 380 or wavelength > 780:
            return '#808080'
        
        if 380 <= wavelength < 440:
            r = -(wavelength - 440) / (440 - 380)
            g = 0.0
            b = 1.0
        elif 440 <= wavelength < 490:
            r = 0.0
            g = (wavelength - 440) / (490 - 440)
            b = 1.0
        elif 490 <= wavelength < 510:
            r = 0.0
            g = 1.0
            b = -(wavelength - 510) / (510 - 490)
        elif 510 <= wavelength < 580:
            r = (wavelength - 510) / (580 - 510)
            g = 1.0
            b = 0.0
        elif 580 <= wavelength < 645:
            r = 1.0
            g = -(wavelength - 645) / (645 - 580)
            b = 0.0
        else:
            r = 1.0
            g = 0.0
            b = 0.0
        
        r = max(0, min(1, r))
        g = max(0, min(1, g))
        b = max(0, min(1, b))
        
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_field = params.get("y_field")
        z_field = params.get("z_field")
        wavelength_field = params.get("wavelength_field")
        title = params.get("title", "LED晶圆分析图")
        
        if not snapshot_id or not x_field or not y_field or not z_field:
            return self._create_error("snapshot_id, x_field, y_field, z_field是必需的")
        
        cache_key = _get_chart_cache_key("led_wafer", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, z_field)
            if not is_numeric:
                return self._create_error(f"Z轴字段验证失败: {error}")
            
            df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
            df = df.dropna(subset=[z_field])
            
            x_categories = sorted(df[x_field].unique().tolist())
            y_categories = sorted(df[y_field].unique().tolist())
            
            x_map = {v: i for i, v in enumerate(x_categories)}
            y_map = {v: i for i, v in enumerate(y_categories)}
            
            _setup_chinese_font()
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            for _, row in df.iterrows():
                x_pos = x_map[row[x_field]]
                y_pos = y_map[row[y_field]]
                z_val = row[z_field]
                
                if wavelength_field and wavelength_field in df.columns:
                    wavelength = float(row.get(wavelength_field, 550))
                    color = self._wavelength_to_rgb(wavelength)
                else:
                    color = '#4a90d9'
                
                ax.bar3d(x_pos, y_pos, 0, 0.8, 0.8, z_val, color=color, alpha=0.8)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_zlabel(z_field)
            ax.set_title(title)
            
            ax.set_xticks(range(len(x_categories)))
            ax.set_xticklabels([str(x) for x in x_categories], rotation=45)
            ax.set_yticks(range(len(y_categories)))
            ax.set_yticklabels([str(y) for y in y_categories])
            
            chart_filename = f"chart_led_wafer_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("led_wafer", f"/api/charts/{chart_filename}", title,
                                        {"x_categories": len(x_categories), "y_categories": len(y_categories)})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateMultipleYAxisChartTool(BaseChartTool):
    """生成多Y轴图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_multiple_y_axis_chart"
    
    def get_description(self) -> str:
        return "根据数据生成多Y轴图，支持多个数值字段在不同Y轴上展示"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "x_field", "y_fields"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_fields = params.get("y_fields", [])
        title = params.get("title", "多Y轴图")
        
        if not snapshot_id or not x_field or not y_fields:
            return self._create_error("snapshot_id, x_field, y_fields是必需的")
        
        if len(y_fields) < 2:
            return self._create_error("y_fields至少需要2个字段")
        
        cache_key = _get_chart_cache_key("multiple_y_axis", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            
            for field in y_fields:
                is_numeric, error = _validate_numeric_field(df, field)
                if not is_numeric:
                    return self._create_error(f"字段 '{field}' 验证失败: {error}")
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            df = df.dropna(subset=y_fields)
            
            _setup_chinese_font()
            
            fig, ax1 = plt.subplots(figsize=(12, 6))
            
            colors = ['#4a90d9', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
            
            x_data = df[x_field].tolist()
            
            ax1.set_xlabel(x_field)
            ax1.set_ylabel(y_fields[0], color=colors[0])
            ax1.plot(x_data, df[y_fields[0]], color=colors[0], marker='o', label=y_fields[0])
            ax1.tick_params(axis='y', labelcolor=colors[0])
            ax1.set_xticklabels([str(x) for x in x_data], rotation=45, ha='right')
            
            axes = [ax1]
            for i, field in enumerate(y_fields[1:], 1):
                ax_new = ax1.twinx()
                ax_new.spines['right'].set_position(('outward', 60 * (i - 1)))
                ax_new.set_ylabel(field, color=colors[i % len(colors)])
                ax_new.plot(x_data, df[field], color=colors[i % len(colors)], marker='s', linestyle='--', label=field)
                ax_new.tick_params(axis='y', labelcolor=colors[i % len(colors)])
                axes.append(ax_new)
            
            lines = []
            labels = []
            for ax in axes:
                line, label = ax.get_legend_handles_labels()
                lines.extend(line)
                labels.extend(label)
            
            ax1.legend(lines, labels, loc='upper left')
            ax1.set_title(title)
            plt.tight_layout()
            
            chart_filename = f"chart_multiple_y_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("multiple_y_axis", f"/api/charts/{chart_filename}", title,
                                        {"y_fields": y_fields})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateStackedBarChartTool(BaseChartTool):
    """生成堆叠柱状图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_stacked_bar_chart"
    
    def get_description(self) -> str:
        return "根据数据生成堆叠柱状图，支持多个数值字段堆叠展示"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "x_field", "y_fields"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_fields = params.get("y_fields", [])
        title = params.get("title", "堆叠柱状图")
        
        if not snapshot_id or not x_field or not y_fields:
            return self._create_error("snapshot_id, x_field, y_fields是必需的")
        
        if len(y_fields) < 2:
            return self._create_error("y_fields至少需要2个字段")
        
        cache_key = _get_chart_cache_key("stacked_bar", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            
            for field in y_fields:
                is_numeric, error = _validate_numeric_field(df, field)
                if not is_numeric:
                    return self._create_error(f"字段 '{field}' 验证失败: {error}")
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            df = df.dropna(subset=y_fields)
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x_data = df[x_field].tolist()
            x_pos = np.arange(len(x_data))
            width = 0.6
            
            colors = ['#4a90d9', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
            
            bottom = np.zeros(len(x_data))
            for i, field in enumerate(y_fields):
                values = df[field].tolist()
                ax.bar(x_pos, values, width, bottom=bottom, label=field, color=colors[i % len(colors)])
                bottom += np.array(values)
            
            ax.set_xlabel(x_field)
            ax.set_ylabel("值")
            ax.set_title(title)
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(x) for x in x_data], rotation=45, ha='right')
            ax.legend(loc='upper right')
            
            plt.tight_layout()
            
            chart_filename = f"chart_stacked_bar_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("stacked_bar", f"/api/charts/{chart_filename}", title,
                                        {"y_fields": y_fields})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateStackedLineChartTool(BaseChartTool):
    """生成堆叠折线图"""
    
    def get_name(self) -> str:
        return "pbbi_generate_stacked_line_chart"
    
    def get_description(self) -> str:
        return "根据数据生成堆叠折线图，支持多个数值字段堆叠展示趋势"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot_id": {"type": "integer", "description": "数据快照ID"},
                "x_field": {"type": "string", "description": "X轴字段名"},
                "y_fields": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段列表（多个数值字段）"},
                "title": {"type": "string", "description": "图表标题"}
            },
            "required": ["snapshot_id", "x_field", "y_fields"]
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        y_fields = params.get("y_fields", [])
        title = params.get("title", "堆叠折线图")
        
        if not snapshot_id or not x_field or not y_fields:
            return self._create_error("snapshot_id, x_field, y_fields是必需的")
        
        if len(y_fields) < 2:
            return self._create_error("y_fields至少需要2个字段")
        
        cache_key = _get_chart_cache_key("stacked_line", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            df = pd.DataFrame(data)
            
            if x_field not in df.columns:
                return self._create_error(f"X轴字段 '{x_field}' 不存在")
            
            for field in y_fields:
                is_numeric, error = _validate_numeric_field(df, field)
                if not is_numeric:
                    return self._create_error(f"字段 '{field}' 验证失败: {error}")
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            df = df.dropna(subset=y_fields)
            
            _setup_chinese_font()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x_data = list(range(len(df)))
            x_labels = df[x_field].tolist()
            
            colors = ['#4a90d9', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
            
            stacked_data = np.zeros((len(y_fields), len(df)))
            for i, field in enumerate(y_fields):
                stacked_data[i] = df[field].values
            
            cumulative = np.zeros(len(df))
            for i, field in enumerate(y_fields):
                ax.fill_between(x_data, cumulative, cumulative + stacked_data[i], 
                               alpha=0.5, label=field, color=colors[i % len(colors)])
                ax.plot(x_data, cumulative + stacked_data[i], color=colors[i % len(colors)], linewidth=2)
                cumulative += stacked_data[i]
            
            ax.set_xlabel(x_field)
            ax.set_ylabel("值")
            ax.set_title(title)
            ax.set_xticks(x_data)
            ax.set_xticklabels([str(x) for x in x_labels], rotation=45, ha='right')
            ax.legend(loc='upper left')
            
            plt.tight_layout()
            
            chart_filename = f"chart_stacked_line_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("stacked_line", f"/api/charts/{chart_filename}", title,
                                        {"y_fields": y_fields})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


class GenerateLinkedChartTool(BaseChartTool):
    """生成联动图表（折线图+饼图）"""
    
    def get_name(self) -> str:
        return "pbbi_generate_linked_chart"
    
    def get_description(self) -> str:
        return "根据数据生成联动图表，折线图与饼图联动展示"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
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
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("snapshot_id")
        x_field = params.get("x_field")
        name_field = params.get("name_field")
        value_field = params.get("value_field")
        title = params.get("title", "联动图表")
        
        if not snapshot_id or not x_field or not name_field or not value_field:
            return self._create_error("snapshot_id, x_field, name_field, value_field是必需的")
        
        cache_key = _get_chart_cache_key("linked", params)
        cached = _check_chart_cache(cache_key)
        if cached:
            return cached
        
        data, error = self._get_data_from_snapshot(snapshot_id)
        if error:
            return self._create_error(error)
        
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.gridspec import GridSpec
            
            df = pd.DataFrame(data)
            
            is_numeric, error = _validate_numeric_field(df, value_field)
            if not is_numeric:
                return self._create_error(f"数值字段验证失败: {error}")
            
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
            df = df.dropna(subset=[value_field])
            
            _setup_chinese_font()
            
            fig = plt.figure(figsize=(12, 10))
            gs = GridSpec(2, 1, height_ratios=[1.5, 1])
            
            ax1 = fig.add_subplot(gs[0])
            ax2 = fig.add_subplot(gs[1])
            
            x_categories = sorted(df[x_field].unique().tolist())
            names = sorted(df[name_field].unique().tolist())
            
            colors = plt.cm.Set2(np.linspace(0, 1, len(names)))
            color_map = {name: colors[i] for i, name in enumerate(names)}
            
            for name in names:
                subset = df[df[name_field] == name]
                x_vals = [x_categories.index(x) if x in x_categories else 0 for x in subset[x_field]]
                y_vals = subset[value_field].tolist()
                ax1.plot(x_vals, y_vals, marker='o', label=name, color=color_map[name])
            
            ax1.set_xlabel(x_field)
            ax1.set_ylabel(value_field)
            ax1.set_title(f"{title} - 趋势图")
            ax1.set_xticks(range(len(x_categories)))
            ax1.set_xticklabels([str(x) for x in x_categories], rotation=45, ha='right')
            ax1.legend(loc='upper left')
            
            last_x_data = df[df[x_field] == x_categories[-1]] if x_categories else df
            pie_data = last_x_data.groupby(name_field)[value_field].sum()
            pie_labels = pie_data.index.tolist()
            pie_values = pie_data.values.tolist()
            pie_colors = [color_map[label] for label in pie_labels]
            
            ax2.pie(pie_values, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%', startangle=90)
            ax2.set_title(f"{title} - 分布图 ({x_categories[-1] if x_categories else '总计'})")
            
            plt.tight_layout()
            
            chart_filename = f"chart_linked_{int(time.time())}.png"
            chart_path = CHARTS_DIR / chart_filename
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            result = self._create_result("linked", f"/api/charts/{chart_filename}", title,
                                        {"x_categories": x_categories, "names": names})
            _save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            return self._create_error(f"生成图表失败: {str(e)}")


def register_chart_tools(mcp_service):
    """注册所有图表MCP工具"""
    _clean_old_charts()
    
    tools = [
        # 基础图表
        GenerateBarChartTool(),
        GeneratePieChartTool(),
        GenerateLineChartTool(),
        GenerateScatterChartTool(),
        GenerateBoxPlotTool(),
        GenerateHistogramTool(),
        
        # 高级图表
        GenerateHeatmapTool(),
        GenerateRadarChartTool(),
        GenerateFunnelChartTool(),
        GenerateGaugeChartTool(),
        
        # 3D图表
        GenerateBar3DChartTool(),
        GenerateScatter3DChartTool(),
        GenerateSurface3DChartTool(),
        GenerateLEDWaferChartTool(),
        
        # 组合图表
        GenerateComboChartTool(),
        GenerateMultipleYAxisChartTool(),
        GenerateStackedBarChartTool(),
        GenerateStackedLineChartTool(),
        GenerateLinkedChartTool(),
    ]
    
    for tool in tools:
        mcp_service.register_tool(MCPTool(
            name=tool.get_name(),
            description=tool.get_description(),
            parameters=tool.get_parameters()
        ))
        mcp_service.register_handler(tool.get_name(), tool.execute)
    
    return tools
