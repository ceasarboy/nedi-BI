"""
ECharts图表配置生成API
返回图表配置数据供前端渲染
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from src.core.database import SessionLocal
from src.models.config import DataSnapshot

router = APIRouter(prefix="/api/echarts", tags=["echarts"])


class ChartConfigRequest(BaseModel):
    snapshot_id: int
    chart_type: str
    config: Dict[str, Any]


def get_snapshot_data(snapshot_id: int) -> List[Dict]:
    """获取快照数据"""
    db = SessionLocal()
    try:
        snapshot = db.query(DataSnapshot).filter(DataSnapshot.id == snapshot_id).first()
        if not snapshot:
            return []
        
        import json
        data = json.loads(snapshot.data) if isinstance(snapshot.data, str) else snapshot.data
        return data
    finally:
        db.close()


def generate_bar_config(data: List[Dict], config: Dict) -> Dict:
    """生成柱状图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field") or config.get("x_axis_field")
    y_field = config.get("y_field") or config.get("y_axis_field")
    title = config.get("title", "柱状图")
    aggregation = config.get("aggregation", "sum")
    
    if not x_field or not y_field:
        return {"error": "缺少x_field或y_field"}
    
    if x_field not in df.columns:
        return {"error": f"字段 '{x_field}' 不存在"}
    
    df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
    df = df.dropna(subset=[y_field])
    
    if aggregation == "sum":
        grouped = df.groupby(x_field)[y_field].sum()
    elif aggregation == "avg":
        grouped = df.groupby(x_field)[y_field].mean()
    else:
        grouped = df.groupby(x_field)[y_field].count()
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in grouped.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": y_field},
        "series": [{
            "name": y_field,
            "type": "bar",
            "data": grouped.values.tolist(),
            "itemStyle": {"color": "#3b82f6"}
        }]
    }


def generate_line_config(data: List[Dict], config: Dict) -> Dict:
    """生成折线图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field") or config.get("x_axis_field")
    y_field = config.get("y_field") or config.get("y_axis_field")
    title = config.get("title", "折线图")
    
    if not x_field or not y_field:
        return {"error": "缺少x_field或y_field"}
    
    if x_field not in df.columns or y_field not in df.columns:
        return {"error": f"字段不存在"}
    
    df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
    df = df.dropna(subset=[y_field])
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in df[x_field].tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": y_field},
        "series": [{
            "name": y_field,
            "type": "line",
            "data": df[y_field].tolist(),
            "smooth": True,
            "itemStyle": {"color": "#3b82f6"}
        }]
    }


def generate_pie_config(data: List[Dict], config: Dict) -> Dict:
    """生成饼图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    name_field = config.get("name_field") or config.get("x_axis_field")
    value_field = config.get("value_field") or config.get("y_axis_field")
    title = config.get("title", "饼图")
    
    if not name_field or not value_field:
        return {"error": "缺少name_field或value_field"}
    
    df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
    df = df.dropna(subset=[value_field])
    
    grouped = df.groupby(name_field)[value_field].sum()
    
    pie_data = [{"name": str(k), "value": v} for k, v in grouped.items()]
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left"},
        "series": [{
            "name": value_field,
            "type": "pie",
            "radius": "50%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }


def generate_scatter_config(data: List[Dict], config: Dict) -> Dict:
    """生成散点图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field") or config.get("x_axis_field")
    y_field = config.get("y_field") or config.get("y_axis_field")
    title = config.get("title", "散点图")
    
    if not x_field or not y_field:
        return {"error": "缺少x_field或y_field"}
    
    df[x_field] = pd.to_numeric(df[x_field], errors='coerce')
    df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
    df = df.dropna(subset=[x_field, y_field])
    
    scatter_data = [[row[x_field], row[y_field]] for _, row in df.iterrows()]
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{c}"},
        "xAxis": {"type": "value", "name": x_field},
        "yAxis": {"type": "value", "name": y_field},
        "series": [{
            "name": "数据点",
            "type": "scatter",
            "data": scatter_data,
            "symbolSize": 10,
            "itemStyle": {"color": "#3b82f6"}
        }]
    }


def generate_histogram_config(data: List[Dict], config: Dict) -> Dict:
    """生成直方图配置"""
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(data)
    field = config.get("field")
    bins = config.get("bins", 10)
    title = config.get("title", "直方图")
    
    if not field:
        return {"error": "缺少field参数"}
    
    df[field] = pd.to_numeric(df[field], errors='coerce')
    values = df[field].dropna().tolist()
    
    if not values:
        return {"error": "没有有效数据"}
    
    counts, edges = np.histogram(values, bins=bins)
    
    bar_data = []
    for i, count in enumerate(counts):
        bar_data.append({
            "name": f"{edges[i]:.1f}-{edges[i+1]:.1f}",
            "value": count
        })
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "category",
            "data": [d["name"] for d in bar_data],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "频数"},
        "series": [{
            "name": "频数",
            "type": "bar",
            "data": [d["value"] for d in bar_data],
            "itemStyle": {"color": "#3b82f6"}
        }]
    }


def generate_radar_config(data: List[Dict], config: Dict) -> Dict:
    """生成雷达图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    fields = config.get("fields", [])
    name_field = config.get("name_field")
    title = config.get("title", "雷达图")
    
    if not fields or not name_field:
        return {"error": "缺少fields或name_field参数"}
    
    for f in fields:
        df[f] = pd.to_numeric(df[f], errors='coerce')
    
    df = df.dropna(subset=fields)
    
    indicator = [{"name": f, "max": df[f].max() * 1.2 if df[f].max() > 0 else 100} for f in fields]
    
    series_data = []
    for _, row in df.iterrows():
        series_data.append({
            "name": str(row[name_field]),
            "value": [row[f] for f in fields]
        })
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {},
        "legend": {"bottom": 10},
        "radar": {"indicator": indicator},
        "series": [{
            "type": "radar",
            "data": series_data
        }]
    }


def generate_bar_3d_config(data: List[Dict], config: Dict) -> Dict:
    """生成3D柱状图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field")
    y_field = config.get("y_field")
    z_field = config.get("z_field")
    title = config.get("title", "3D柱状图")
    
    if not x_field or not y_field or not z_field:
        return {"error": "缺少x_field、y_field或z_field参数"}
    
    df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
    df = df.dropna(subset=[z_field])
    
    x_categories = df[x_field].unique().tolist()
    y_categories = df[y_field].unique().tolist()
    
    grid_data = []
    for _, row in df.iterrows():
        x_idx = x_categories.index(row[x_field])
        y_idx = y_categories.index(row[y_field])
        grid_data.append([x_idx, y_idx, row[z_field]])
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {},
        "visualMap": {
            "show": True,
            "min": min(d[2] for d in grid_data) if grid_data else 0,
            "max": max(d[2] for d in grid_data) if grid_data else 100,
            "inRange": {"color": ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']}
        },
        "xAxis3D": {"type": "category", "data": [str(x) for x in x_categories]},
        "yAxis3D": {"type": "category", "data": [str(y) for y in y_categories]},
        "zAxis3D": {"type": "value"},
        "grid3D": {
            "boxWidth": 100,
            "boxHeight": 60,
            "viewControl": {"autoRotate": True}
        },
        "series": [{
            "type": "bar3D",
            "data": grid_data,
            "shading": "lambert",
            "label": {"show": False}
        }]
    }


def generate_scatter_3d_config(data: List[Dict], config: Dict) -> Dict:
    """生成3D散点图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field")
    y_field = config.get("y_field")
    z_field = config.get("z_field")
    title = config.get("title", "3D散点图")
    
    if not x_field or not y_field or not z_field:
        return {"error": "缺少x_field、y_field或z_field参数"}
    
    df[x_field] = pd.to_numeric(df[x_field], errors='coerce')
    df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
    df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
    df = df.dropna(subset=[x_field, y_field, z_field])
    
    scatter_data = [[row[x_field], row[y_field], row[z_field]] for _, row in df.iterrows()]
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {},
        "xAxis3D": {"type": "value", "name": x_field},
        "yAxis3D": {"type": "value", "name": y_field},
        "zAxis3D": {"type": "value", "name": z_field},
        "grid3D": {
            "viewControl": {"autoRotate": True}
        },
        "series": [{
            "type": "scatter3D",
            "data": scatter_data,
            "symbolSize": 12,
            "itemStyle": {"color": "#3b82f6"}
        }]
    }


def generate_surface_3d_config(data: List[Dict], config: Dict) -> Dict:
    """生成3D曲面图配置"""
    import pandas as pd
    
    df = pd.DataFrame(data)
    x_field = config.get("x_field")
    y_field = config.get("y_field")
    z_field = config.get("z_field")
    title = config.get("title", "3D曲面图")
    
    if not x_field or not y_field or not z_field:
        return {"error": "缺少x_field、y_field或z_field参数"}
    
    df[x_field] = pd.to_numeric(df[x_field], errors='coerce')
    df[y_field] = pd.to_numeric(df[y_field], errors='coerce')
    df[z_field] = pd.to_numeric(df[z_field], errors='coerce')
    df = df.dropna(subset=[x_field, y_field, z_field])
    
    x_unique = sorted(df[x_field].unique())
    y_unique = sorted(df[y_field].unique())
    
    surface_data = []
    for i, x_val in enumerate(x_unique):
        for j, y_val in enumerate(y_unique):
            z_val = df[(df[x_field] == x_val) & (df[y_field] == y_val)][z_field]
            z = z_val.iloc[0] if len(z_val) > 0 else 0
            surface_data.append([i, j, z])
    
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {},
        "visualMap": {
            "show": True,
            "min": min(d[2] for d in surface_data) if surface_data else 0,
            "max": max(d[2] for d in surface_data) if surface_data else 100,
            "inRange": {"color": ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']}
        },
        "xAxis3D": {"type": "value", "name": x_field},
        "yAxis3D": {"type": "value", "name": y_field},
        "zAxis3D": {"type": "value", "name": z_field},
        "grid3D": {
            "viewControl": {"autoRotate": True}
        },
        "series": [{
            "type": "surface",
            "data": surface_data,
            "shading": "lambert"
        }]
    }


CHART_GENERATORS = {
    "bar": generate_bar_config,
    "line": generate_line_config,
    "pie": generate_pie_config,
    "scatter": generate_scatter_config,
    "histogram": generate_histogram_config,
    "radar": generate_radar_config,
    "bar3d": generate_bar_3d_config,
    "scatter3d": generate_scatter_3d_config,
    "surface3d": generate_surface_3d_config
}


@router.post("/config")
async def generate_chart_config(request: ChartConfigRequest):
    """生成ECharts图表配置"""
    data = get_snapshot_data(request.snapshot_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="快照不存在或没有数据")
    
    generator = CHART_GENERATORS.get(request.chart_type)
    
    if not generator:
        raise HTTPException(status_code=400, detail=f"不支持的图表类型: {request.chart_type}")
    
    config = generator(data, request.config)
    
    if "error" in config:
        raise HTTPException(status_code=400, detail=config["error"])
    
    return {
        "success": True,
        "chart_type": request.chart_type,
        "config": config
    }
