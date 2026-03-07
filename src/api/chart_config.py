"""
图表配置API接口
返回ECharts配置JSON，支持前端渲染
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from src.api.auth import get_current_user_optional

router = APIRouter(prefix="/api/chart", tags=["chart"])


class ChartConfigRequest(BaseModel):
    chart_type: str
    snapshot_id: Optional[int] = None
    data: Optional[List[Dict[str, Any]]] = None
    x_field: Optional[str] = None
    y_field: Optional[str] = None
    category_field: Optional[str] = None
    value_field: Optional[str] = None
    title: Optional[str] = None
    color: Optional[str] = None
    smooth: Optional[bool] = False
    area: Optional[bool] = False
    show_labels: Optional[bool] = False
    radius: Optional[List[str]] = None
    symbol_size: Optional[int] = 10
    bins: Optional[int] = 10
    fields: Optional[List[str]] = None
    name_field: Optional[str] = None
    z_field: Optional[str] = None
    auto_rotate: Optional[bool] = False
    rotate: Optional[int] = 0


def generate_echarts_option(chart_type: str, data: List[Dict], config: ChartConfigRequest) -> Dict:
    """生成ECharts配置"""
    
    base_option = {
        "title": {
            "text": config.title or "",
            "left": "center",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item" if chart_type == "pie" else "axis",
            "confine": True
        },
        "toolbox": {
            "feature": {
                "saveAsImage": {"title": "保存图片"},
                "dataZoom": {"title": {"zoom": "区域缩放", "back": "区域还原"}},
                "restore": {"title": "还原"}
            },
            "right": 20
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        }
    }
    
    if chart_type == "bar":
        return {
            **base_option,
            "xAxis": {
                "type": "category",
                "data": [item.get(config.x_field, "") for item in data],
                "axisLabel": {"rotate": config.rotate or 0}
            },
            "yAxis": {
                "type": "value",
                "name": config.y_field
            },
            "series": [{
                "type": "bar",
                "data": [item.get(config.y_field, 0) for item in data],
                "itemStyle": {
                    "color": config.color or "#3b82f6"
                },
                "label": {
                    "show": config.show_labels or False,
                    "position": "top"
                }
            }]
        }
    
    elif chart_type == "line":
        return {
            **base_option,
            "xAxis": {
                "type": "category",
                "data": [item.get(config.x_field, "") for item in data],
                "boundaryGap": False
            },
            "yAxis": {
                "type": "value",
                "name": config.y_field
            },
            "series": [{
                "type": "line",
                "data": [item.get(config.y_field, 0) for item in data],
                "smooth": config.smooth or False,
                "itemStyle": {
                    "color": config.color or "#3b82f6"
                },
                "areaStyle": {"opacity": 0.3} if config.area else None
            }]
        }
    
    elif chart_type == "pie":
        return {
            **base_option,
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "top": "middle"
            },
            "series": [{
                "type": "pie",
                "radius": config.radius or ["40%", "70%"],
                "center": ["60%", "50%"],
                "data": [
                    {"name": item.get(config.category_field, ""), "value": item.get(config.value_field, 0)}
                    for item in data
                ],
                "label": {
                    "show": True,
                    "formatter": "{b}: {d}%"
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 16,
                        "fontWeight": "bold"
                    }
                }
            }]
        }
    
    elif chart_type == "scatter":
        return {
            **base_option,
            "xAxis": {
                "type": "value",
                "name": config.x_field,
                "scale": True
            },
            "yAxis": {
                "type": "value",
                "name": config.y_field,
                "scale": True
            },
            "series": [{
                "type": "scatter",
                "data": [[item.get(config.x_field, 0), item.get(config.y_field, 0)] for item in data],
                "symbolSize": config.symbol_size or 10,
                "itemStyle": {
                    "color": config.color or "#3b82f6"
                }
            }]
        }
    
    elif chart_type == "heatmap":
        x_categories = list(set(item.get(config.x_field, "") for item in data))
        y_categories = list(set(item.get(config.y_field, "") for item in data))
        
        return {
            **base_option,
            "tooltip": {
                "position": "top"
            },
            "grid": {
                "top": 60,
                "bottom": 60
            },
            "xAxis": {
                "type": "category",
                "data": x_categories,
                "splitArea": {"show": True}
            },
            "yAxis": {
                "type": "category",
                "data": y_categories,
                "splitArea": {"show": True}
            },
            "visualMap": {
                "min": min(item.get(config.value_field, 0) for item in data),
                "max": max(item.get(config.value_field, 0) for item in data),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": 0
            },
            "series": [{
                "type": "heatmap",
                "data": [
                    [
                        x_categories.index(item.get(config.x_field, "")),
                        y_categories.index(item.get(config.y_field, "")),
                        item.get(config.value_field, 0)
                    ]
                    for item in data
                ],
                "label": {
                    "show": config.show_labels or False
                }
            }]
        }
    
    elif chart_type == "radar":
        if not config.fields:
            config.fields = list(data[0].keys())[:5] if data else []
        
        indicators = [
            {
                "name": field,
                "max": max(item.get(field, 0) for item in data) if data else 100
            }
            for field in config.fields
        ]
        
        return {
            **base_option,
            "radar": {
                "indicator": indicators,
                "shape": "polygon"
            },
            "series": [{
                "type": "radar",
                "data": [
                    {
                        "name": item.get(config.name_field, f"数据{i+1}"),
                        "value": [item.get(field, 0) for field in config.fields]
                    }
                    for i, item in enumerate(data)
                ]
            }]
        }
    
    elif chart_type == "histogram":
        values = [item.get(config.value_field, 0) for item in data]
        if not values:
            return base_option
        
        min_val = min(values)
        max_val = max(values)
        bin_count = config.bins or 10
        bin_width = (max_val - min_val) / bin_count if max_val > min_val else 1
        
        bins = [0] * bin_count
        for v in values:
            bin_index = min(int((v - min_val) / bin_width), bin_count - 1) if bin_width > 0 else 0
            bins[bin_index] += 1
        
        return {
            **base_option,
            "xAxis": {
                "type": "category",
                "data": [f"{(min_val + i * bin_width):.1f}" for i in range(bin_count)]
            },
            "yAxis": {
                "type": "value",
                "name": "频次"
            },
            "series": [{
                "type": "bar",
                "data": bins,
                "itemStyle": {
                    "color": config.color or "#3b82f6"
                }
            }]
        }
    
    elif chart_type == "scatter_3d":
        return {
            **base_option,
            "tooltip": {},
            "visualMap": {
                "show": True,
                "dimension": 2,
                "min": min(item.get(config.z_field, 0) for item in data) if data else 0,
                "max": max(item.get(config.z_field, 0) for item in data) if data else 100,
                "inRange": {
                    "color": ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                             "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"]
                }
            },
            "xAxis3D": {"type": "value", "name": config.x_field},
            "yAxis3D": {"type": "value", "name": config.y_field},
            "zAxis3D": {"type": "value", "name": config.z_field},
            "grid3D": {
                "viewControl": {
                    "autoRotate": config.auto_rotate or False
                }
            },
            "series": [{
                "type": "scatter3D",
                "data": [
                    [item.get(config.x_field, 0), item.get(config.y_field, 0), item.get(config.z_field, 0)]
                    for item in data
                ],
                "symbolSize": config.symbol_size or 10
            }]
        }
    
    elif chart_type == "bar_3d":
        x_categories = list(set(item.get(config.x_field, "") for item in data))
        y_categories = list(set(item.get(config.y_field, "") for item in data))
        
        return {
            **base_option,
            "visualMap": {
                "show": True,
                "min": min(item.get(config.value_field, 0) for item in data) if data else 0,
                "max": max(item.get(config.value_field, 0) for item in data) if data else 100,
                "inRange": {
                    "color": ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                             "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"]
                }
            },
            "xAxis3D": {"type": "category", "data": x_categories},
            "yAxis3D": {"type": "category", "data": y_categories},
            "zAxis3D": {"type": "value"},
            "grid3D": {
                "viewControl": {
                    "autoRotate": config.auto_rotate or False
                }
            },
            "series": [{
                "type": "bar3D",
                "data": [
                    [
                        x_categories.index(item.get(config.x_field, "")),
                        y_categories.index(item.get(config.y_field, "")),
                        item.get(config.value_field, 0)
                    ]
                    for item in data
                ],
                "shading": "lambert",
                "label": {
                    "show": config.show_labels or False
                }
            }]
        }
    
    else:
        return base_option


@router.post("/config")
async def get_chart_config(
    request: ChartConfigRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    获取图表配置
    
    根据图表类型和数据生成ECharts配置JSON
    """
    data = request.data or []
    
    if request.snapshot_id and not data:
        from src.core.database import SessionLocal
        from src.models.dataflow import DataSnapshot
        
        db = SessionLocal()
        try:
            snapshot = db.query(DataSnapshot).filter(DataSnapshot.id == request.snapshot_id).first()
            if snapshot and snapshot.data:
                data = json.loads(snapshot.data) if isinstance(snapshot.data, str) else snapshot.data
        finally:
            db.close()
    
    if not data:
        raise HTTPException(status_code=400, detail="数据不能为空")
    
    try:
        option = generate_echarts_option(request.chart_type, data, request)
        
        return {
            "success": True,
            "config": {
                "chart_type": request.chart_type,
                "option": option,
                "data": data[:100]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成配置失败: {str(e)}")


@router.get("/types")
async def get_chart_types():
    """获取支持的图表类型列表"""
    return {
        "success": True,
        "types": [
            {"type": "bar", "name": "柱状图", "icon": "📊"},
            {"type": "line", "name": "折线图", "icon": "📈"},
            {"type": "pie", "name": "饼图", "icon": "🥧"},
            {"type": "scatter", "name": "散点图", "icon": "⚬"},
            {"type": "heatmap", "name": "热力图", "icon": "🌡️"},
            {"type": "radar", "name": "雷达图", "icon": "🎯"},
            {"type": "histogram", "name": "直方图", "icon": "📊"},
            {"type": "scatter_3d", "name": "3D散点图", "icon": "🌐"},
            {"type": "bar_3d", "name": "3D柱状图", "icon": "📊"}
        ]
    }
