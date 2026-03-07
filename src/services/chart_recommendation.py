"""
图表智能推荐服务
根据数据特征自动推荐最适合的图表类型
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime


class FieldType(Enum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TIME = "time"
    TEXT = "text"


class DistributionType(Enum):
    NORMAL = "normal"
    SKEWED = "skewed"
    UNIFORM = "uniform"
    BIMODAL = "bimodal"
    UNKNOWN = "unknown"


@dataclass
class FieldFeatures:
    name: str
    field_type: FieldType
    distribution: DistributionType
    missing_ratio: float
    unique_count: int
    total_count: int
    stats: Optional[Dict[str, float]] = None


@dataclass
class DataFeatures:
    fields: List[FieldFeatures]
    numerical_count: int
    categorical_count: int
    time_count: int
    row_count: int
    correlations: List[Dict[str, Any]]


@dataclass
class ChartRecommendation:
    chart_type: str
    chart_name: str
    score: float
    reason: str
    suitable_fields: List[str]


class DataFeatureAnalyzer:
    """数据特征分析器"""
    
    def analyze(self, data: List[Dict], fields: List[str] = None) -> DataFeatures:
        """
        分析数据特征
        
        Args:
            data: 数据列表
            fields: 要分析的字段列表，如果为None则分析所有字段
            
        Returns:
            DataFeatures: 数据特征分析结果
        """
        if not data:
            return DataFeatures(
                fields=[],
                numerical_count=0,
                categorical_count=0,
                time_count=0,
                row_count=0,
                correlations=[]
            )
        
        df = pd.DataFrame(data)
        
        if fields:
            df = df[[f for f in fields if f in df.columns]]
        
        field_features = []
        numerical_fields = []
        categorical_fields = []
        time_fields = []
        
        for col in df.columns:
            features = self._analyze_field(df[col], col)
            field_features.append(features)
            
            if features.field_type == FieldType.NUMERICAL:
                numerical_fields.append(col)
            elif features.field_type == FieldType.CATEGORICAL:
                categorical_fields.append(col)
            elif features.field_type == FieldType.TIME:
                time_fields.append(col)
        
        correlations = self._analyze_correlations(df, numerical_fields)
        
        return DataFeatures(
            fields=field_features,
            numerical_count=len(numerical_fields),
            categorical_count=len(categorical_fields),
            time_count=len(time_fields),
            row_count=len(df),
            correlations=correlations
        )
    
    def _analyze_field(self, series: pd.Series, name: str) -> FieldFeatures:
        """分析单个字段"""
        series = series.dropna()
        total_count = len(series)
        unique_count = series.nunique()
        missing_ratio = 1 - (total_count / len(series)) if len(series) > 0 else 0
        
        field_type = self._detect_field_type(series)
        distribution = DistributionType.UNKNOWN
        stats = None
        
        if field_type == FieldType.NUMERICAL:
            distribution = self._analyze_distribution(series)
            stats = {
                "mean": float(series.mean()) if not series.empty else 0,
                "std": float(series.std()) if not series.empty else 0,
                "min": float(series.min()) if not series.empty else 0,
                "max": float(series.max()) if not series.empty else 0,
                "median": float(series.median()) if not series.empty else 0
            }
        elif field_type == FieldType.CATEGORICAL:
            if unique_count <= 10:
                distribution = DistributionType.UNIFORM
            else:
                distribution = DistributionType.SKEWED
        
        return FieldFeatures(
            name=name,
            field_type=field_type,
            distribution=distribution,
            missing_ratio=missing_ratio,
            unique_count=unique_count,
            total_count=total_count,
            stats=stats
        )
    
    def _detect_field_type(self, series: pd.Series) -> FieldType:
        """检测字段类型"""
        if series.empty:
            return FieldType.TEXT
        
        dtype = str(series.dtype)
        
        if 'datetime' in dtype or 'date' in dtype.lower():
            return FieldType.TIME
        
        if dtype in ['int64', 'int32', 'float64', 'float32', 'int', 'float']:
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.05 and series.nunique() < 20:
                return FieldType.CATEGORICAL
            return FieldType.NUMERICAL
        
        if dtype == 'object':
            try:
                pd.to_datetime(series, errors='raise')
                return FieldType.TIME
            except:
                pass
            
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.5 or series.nunique() < 20:
                return FieldType.CATEGORICAL
            
            avg_len = series.astype(str).str.len().mean()
            if avg_len > 50:
                return FieldType.TEXT
        
        return FieldType.CATEGORICAL
    
    def _analyze_distribution(self, series: pd.Series) -> DistributionType:
        """分析数值分布"""
        if len(series) < 10:
            return DistributionType.UNKNOWN
        
        try:
            series = series.dropna()
            mean = series.mean()
            std = series.std()
            median = series.median()
            
            if std == 0:
                return DistributionType.UNIFORM
            
            skewness = abs(series.skew())
            
            if skewness < 0.5:
                return DistributionType.NORMAL
            elif skewness > 1:
                return DistributionType.SKEWED
            else:
                return DistributionType.UNKNOWN
        except:
            return DistributionType.UNKNOWN
    
    def _analyze_correlations(self, df: pd.DataFrame, numerical_fields: List[str]) -> List[Dict]:
        """分析数值字段间的相关性"""
        correlations = []
        
        if len(numerical_fields) < 2:
            return correlations
        
        for i, f1 in enumerate(numerical_fields):
            for f2 in numerical_fields[i+1:]:
                try:
                    corr = df[f1].corr(df[f2])
                    if not pd.isna(corr):
                        correlations.append({
                            "field1": f1,
                            "field2": f2,
                            "correlation": abs(corr),
                            "strength": "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.3 else "weak"
                        })
                except:
                    pass
        
        return sorted(correlations, key=lambda x: x["correlation"], reverse=True)


class ChartRecommendationEngine:
    """图表推荐引擎"""
    
    CHART_TYPES = {
        "bar": {"name": "柱状图", "icon": "📊"},
        "pie": {"name": "饼图", "icon": "🥧"},
        "line": {"name": "折线图", "icon": "📈"},
        "scatter": {"name": "散点图", "icon": "⚬"},
        "histogram": {"name": "直方图", "icon": "📊"},
        "box_plot": {"name": "箱线图", "icon": "📦"},
        "heatmap": {"name": "热力图", "icon": "🌡️"},
        "radar": {"name": "雷达图", "icon": "🎯"},
        "funnel": {"name": "漏斗图", "icon": "🔻"},
        "gauge": {"name": "仪表盘", "icon": "⏱️"},
        "scatter_3d": {"name": "3D散点图", "icon": "🌐"},
        "bar_3d": {"name": "3D柱状图", "icon": "📊"},
        "surface_3d": {"name": "3D曲面图", "icon": "🏔️"},
        "combo": {"name": "组合图", "icon": "📊"},
        "stacked_bar": {"name": "堆叠柱状图", "icon": "📊"},
        "stacked_line": {"name": "堆叠折线图", "icon": "📈"},
    }
    
    RECOMMENDATION_RULES = [
        {
            "condition": {"numerical": 1, "categorical": 0, "time": 0},
            "recommendations": [
                {"chart": "histogram", "score": 0.95, "reason": "单数值字段，最适合展示数据分布"},
                {"chart": "box_plot", "score": 0.75, "reason": "单数值字段，适合展示统计特征"},
            ]
        },
        {
            "condition": {"numerical": 0, "categorical": 1, "time": 0},
            "recommendations": [
                {"chart": "pie", "score": 0.90, "reason": "单分类字段，最适合展示类别占比"},
                {"chart": "bar", "score": 0.85, "reason": "单分类字段，适合展示各类别频次"},
            ]
        },
        {
            "condition": {"numerical": 1, "categorical": 1, "time": 0},
            "recommendations": [
                {"chart": "bar", "score": 0.95, "reason": "分类+数值，最适合对比分析"},
                {"chart": "pie", "score": 0.70, "reason": "分类+数值，适合展示占比"},
                {"chart": "radar", "score": 0.60, "reason": "分类+数值，适合多维度对比"},
            ]
        },
        {
            "condition": {"numerical": 1, "categorical": 0, "time": 1},
            "recommendations": [
                {"chart": "line", "score": 0.95, "reason": "时间+数值，最适合趋势分析"},
                {"chart": "bar", "score": 0.75, "reason": "时间+数值，适合时间对比"},
            ]
        },
        {
            "condition": {"numerical": 2, "categorical": 0, "time": 0},
            "recommendations": [
                {"chart": "scatter", "score": 0.95, "reason": "双数值字段，最适合相关性分析"},
                {"chart": "heatmap", "score": 0.70, "reason": "双数值字段，适合密度分析"},
            ]
        },
        {
            "condition": {"numerical": 1, "categorical": 1, "time": 1},
            "recommendations": [
                {"chart": "line", "score": 0.95, "reason": "时间+分类+数值，最适合趋势对比"},
                {"chart": "stacked_bar", "score": 0.80, "reason": "时间+分类+数值，适合构成分析"},
            ]
        },
        {
            "condition": {"numerical": 3, "categorical": 0, "time": 0},
            "recommendations": [
                {"chart": "scatter_3d", "score": 0.90, "reason": "三维数值数据，适合立体展示"},
                {"chart": "bar_3d", "score": 0.75, "reason": "三维数值数据，适合三维对比"},
                {"chart": "surface_3d", "score": 0.70, "reason": "三维数值数据，适合曲面展示"},
            ]
        },
        {
            "condition": {"numerical": ">=3", "categorical": 0, "time": 0},
            "recommendations": [
                {"chart": "radar", "score": 0.90, "reason": "多数值字段，适合多维对比"},
                {"chart": "heatmap", "score": 0.75, "reason": "多数值字段，适合相关性矩阵"},
            ]
        },
        {
            "condition": {"numerical": ">=2", "categorical": 1, "time": 0},
            "recommendations": [
                {"chart": "radar", "score": 0.90, "reason": "分类+多数值，适合多维对比"},
                {"chart": "stacked_bar", "score": 0.80, "reason": "分类+多数值，适合构成分析"},
            ]
        },
    ]
    
    def recommend(self, features: DataFeatures, selected_fields: List[str] = None) -> List[ChartRecommendation]:
        """
        根据数据特征推荐图表
        
        Args:
            features: 数据特征
            selected_fields: 用户选择的字段
            
        Returns:
            List[ChartRecommendation]: 推荐结果列表，按评分降序排列
        """
        recommendations = []
        
        if selected_fields:
            selected_features = self._filter_features(features, selected_fields)
        else:
            selected_features = features
        
        matched_rules = self._match_rules(selected_features)
        
        for rule in matched_rules:
            for rec in rule.get("recommendations", []):
                chart_type = rec["chart"]
                if chart_type in self.CHART_TYPES:
                    chart_info = self.CHART_TYPES[chart_type]
                    recommendations.append(ChartRecommendation(
                        chart_type=chart_type,
                        chart_name=f"{chart_info['icon']} {chart_info['name']}",
                        score=rec["score"],
                        reason=rec["reason"],
                        suitable_fields=self._get_suitable_fields(selected_features, chart_type)
                    ))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.chart_type not in seen:
                seen.add(rec.chart_type)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]
    
    def _filter_features(self, features: DataFeatures, selected_fields: List[str]) -> DataFeatures:
        """过滤特征，只保留选中字段"""
        filtered_fields = [f for f in features.fields if f.name in selected_fields]
        
        return DataFeatures(
            fields=filtered_fields,
            numerical_count=sum(1 for f in filtered_fields if f.field_type == FieldType.NUMERICAL),
            categorical_count=sum(1 for f in filtered_fields if f.field_type == FieldType.CATEGORICAL),
            time_count=sum(1 for f in filtered_fields if f.field_type == FieldType.TIME),
            row_count=features.row_count,
            correlations=features.correlations
        )
    
    def _match_rules(self, features: DataFeatures) -> List[Dict]:
        """匹配推荐规则"""
        matched = []
        
        for rule in self.RECOMMENDATION_RULES:
            condition = rule["condition"]
            
            num_cond = condition.get("numerical", 0)
            cat_cond = condition.get("categorical", 0)
            time_cond = condition.get("time", 0)
            
            num_match = self._check_condition(num_cond, features.numerical_count)
            cat_match = self._check_condition(cat_cond, features.categorical_count)
            time_match = self._check_condition(time_cond, features.time_count)
            
            if num_match and cat_match and time_match:
                matched.append(rule)
        
        return matched
    
    def _check_condition(self, condition, actual_value) -> bool:
        """检查条件是否匹配"""
        if isinstance(condition, str):
            if condition.startswith(">="):
                return actual_value >= int(condition[2:])
            elif condition.startswith(">"):
                return actual_value > int(condition[1:])
            elif condition.startswith("<="):
                return actual_value <= int(condition[2:])
            elif condition.startswith("<"):
                return actual_value < int(condition[1:])
        return actual_value == condition
    
    def _get_suitable_fields(self, features: DataFeatures, chart_type: str) -> List[str]:
        """获取适合该图表的字段"""
        numerical = [f.name for f in features.fields if f.field_type == FieldType.NUMERICAL]
        categorical = [f.name for f in features.fields if f.field_type == FieldType.CATEGORICAL]
        time = [f.name for f in features.fields if f.field_type == FieldType.TIME]
        
        if chart_type in ["histogram", "box_plot"]:
            return numerical[:1]
        elif chart_type in ["pie"]:
            return categorical[:1] if categorical else numerical[:1]
        elif chart_type in ["bar", "stacked_bar"]:
            return (categorical[:1] + numerical[:1]) if categorical else numerical[:1]
        elif chart_type in ["line", "stacked_line"]:
            return (time[:1] + numerical[:1]) if time else numerical[:1]
        elif chart_type in ["scatter"]:
            return numerical[:2]
        elif chart_type in ["scatter_3d", "bar_3d", "surface_3d"]:
            return numerical[:3]
        elif chart_type in ["radar"]:
            return (categorical[:1] + numerical[:5]) if categorical else numerical[:5]
        elif chart_type in ["heatmap"]:
            return numerical[:5]
        
        return [f.name for f in features.fields[:3]]


class ChartRecommendationService:
    """图表推荐服务"""
    
    def __init__(self):
        self.analyzer = DataFeatureAnalyzer()
        self.engine = ChartRecommendationEngine()
    
    def analyze_and_recommend(self, data: List[Dict], fields: List[str] = None) -> Dict[str, Any]:
        """
        分析数据并推荐图表
        
        Args:
            data: 数据列表
            fields: 选中的字段
            
        Returns:
            包含特征分析和推荐结果的字典
        """
        features = self.analyzer.analyze(data, fields)
        recommendations = self.engine.recommend(features, fields)
        
        return {
            "features": {
                "numerical_count": features.numerical_count,
                "categorical_count": features.categorical_count,
                "time_count": features.time_count,
                "row_count": features.row_count,
                "fields": [
                    {
                        "name": f.name,
                        "type": f.field_type.value,
                        "distribution": f.distribution.value,
                        "missing_ratio": round(f.missing_ratio, 3),
                        "unique_count": f.unique_count,
                        "stats": f.stats
                    }
                    for f in features.fields
                ],
                "correlations": features.correlations[:5]
            },
            "recommendations": [
                {
                    "chart_type": r.chart_type,
                    "chart_name": r.chart_name,
                    "score": round(r.score, 2),
                    "reason": r.reason,
                    "suitable_fields": r.suitable_fields
                }
                for r in recommendations
            ]
        }
    
    def get_chart_types(self) -> List[Dict[str, str]]:
        """获取所有支持的图表类型"""
        return [
            {"type": k, "name": v["name"], "icon": v["icon"]}
            for k, v in self.engine.CHART_TYPES.items()
        ]
