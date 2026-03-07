"""
图表智能推荐系统单元测试
测试数据特征分析器和图表推荐引擎
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from src.services.chart_recommendation import (
    DataFeatureAnalyzer,
    ChartRecommendationEngine,
    ChartRecommendationService,
    FieldType,
    DistributionType,
    FieldFeatures,
    DataFeatures,
    ChartRecommendation
)


class TestDataFeatureAnalyzer:
    """数据特征分析器单元测试"""
    
    @pytest.fixture
    def analyzer(self):
        return DataFeatureAnalyzer()
    
    def test_analyze_empty_data(self, analyzer):
        """测试空数据分析"""
        result = analyzer.analyze([])
        
        assert result.numerical_count == 0
        assert result.categorical_count == 0
        assert result.time_count == 0
        assert result.row_count == 0
        assert len(result.fields) == 0
    
    def test_analyze_single_numerical_field(self, analyzer):
        """测试单数值字段分析"""
        data = [
            {"value": 10},
            {"value": 20},
            {"value": 30},
            {"value": 40},
            {"value": 50}
        ]
        
        result = analyzer.analyze(data)
        
        assert result.numerical_count == 1
        assert result.categorical_count == 0
        assert result.row_count == 5
        assert len(result.fields) == 1
        assert result.fields[0].field_type == FieldType.NUMERICAL
    
    def test_analyze_single_categorical_field(self, analyzer):
        """测试单分类字段分析"""
        data = [
            {"category": "A"},
            {"category": "B"},
            {"category": "A"},
            {"category": "C"},
            {"category": "B"}
        ]
        
        result = analyzer.analyze(data)
        
        assert result.numerical_count == 0
        assert result.categorical_count == 1
        assert result.fields[0].field_type == FieldType.CATEGORICAL
        assert result.fields[0].unique_count == 3
    
    def test_analyze_time_field(self, analyzer):
        """测试时间字段分析"""
        data = [
            {"date": f"2026-01-0{i}"} for i in range(1, 11)
        ]
        
        result = analyzer.analyze(data)
        
        assert result.row_count == 10
        assert len(result.fields) == 1
    
    def test_analyze_mixed_fields(self, analyzer):
        """测试混合字段分析"""
        data = [
            {"category": "A", "value": 10, "date": "2026-01-01"},
            {"category": "B", "value": 20, "date": "2026-01-02"},
            {"category": "A", "value": 30, "date": "2026-01-03"},
        ]
        
        result = analyzer.analyze(data)
        
        assert result.numerical_count == 1
        assert len(result.fields) == 3
    
    def test_analyze_with_selected_fields(self, analyzer):
        """测试选中字段分析"""
        data = [
            {"category": "A", "value1": 10, "value2": 100},
            {"category": "B", "value1": 20, "value2": 200},
        ]
        
        result = analyzer.analyze(data, fields=["category", "value1"])
        
        assert len(result.fields) == 2
        assert result.numerical_count == 1
        assert result.categorical_count == 1
    
    def test_detect_field_type_numerical(self, analyzer):
        """测试数值类型检测"""
        series = __import__('pandas').Series([1, 2, 3, 4, 5])
        field_type = analyzer._detect_field_type(series)
        
        assert field_type == FieldType.NUMERICAL
    
    def test_detect_field_type_categorical(self, analyzer):
        """测试分类类型检测"""
        series = __import__('pandas').Series(["A", "B", "A", "C"])
        field_type = analyzer._detect_field_type(series)
        
        assert field_type == FieldType.CATEGORICAL
    
    def test_analyze_distribution_normal(self, analyzer):
        """测试正态分布检测"""
        np.random.seed(42)
        series = __import__('pandas').Series(np.random.normal(0, 1, 1000))
        distribution = analyzer._analyze_distribution(series)
        
        assert distribution in [DistributionType.NORMAL, DistributionType.UNKNOWN]
    
    def test_analyze_distribution_skewed(self, analyzer):
        """测试偏态分布检测"""
        series = __import__('pandas').Series([1, 2, 3, 100, 200, 300, 1000])
        distribution = analyzer._analyze_distribution(series)
        
        assert distribution in [DistributionType.SKEWED, DistributionType.UNKNOWN]
    
    def test_missing_ratio_calculation(self, analyzer):
        """测试缺失值比例计算"""
        import pandas as pd
        import numpy as np
        
        data = [
            {"value": 10},
            {"value": None},
            {"value": 30},
            {"value": None},
            {"value": 50}
        ]
        
        result = analyzer.analyze(data)
        
        assert result.fields[0].missing_ratio >= 0.0


class TestChartRecommendationEngine:
    """图表推荐引擎单元测试"""
    
    @pytest.fixture
    def engine(self):
        return ChartRecommendationEngine()
    
    def create_features(self, numerical=0, categorical=0, time=0, row_count=10):
        """创建测试用数据特征"""
        fields = []
        
        for i in range(numerical):
            fields.append(FieldFeatures(
                name=f"num_{i}",
                field_type=FieldType.NUMERICAL,
                distribution=DistributionType.UNKNOWN,
                missing_ratio=0.0,
                unique_count=row_count,
                total_count=row_count
            ))
        
        for i in range(categorical):
            fields.append(FieldFeatures(
                name=f"cat_{i}",
                field_type=FieldType.CATEGORICAL,
                distribution=DistributionType.UNIFORM,
                missing_ratio=0.0,
                unique_count=5,
                total_count=row_count
            ))
        
        for i in range(time):
            fields.append(FieldFeatures(
                name=f"time_{i}",
                field_type=FieldType.TIME,
                distribution=DistributionType.UNIFORM,
                missing_ratio=0.0,
                unique_count=row_count,
                total_count=row_count
            ))
        
        return DataFeatures(
            fields=fields,
            numerical_count=numerical,
            categorical_count=categorical,
            time_count=time,
            row_count=row_count,
            correlations=[]
        )
    
    def test_recommend_single_numerical(self, engine):
        """测试单数值字段推荐"""
        features = self.create_features(numerical=1)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type in ["histogram", "box_plot"]
        assert recommendations[0].score > 0
    
    def test_recommend_single_categorical(self, engine):
        """测试单分类字段推荐"""
        features = self.create_features(categorical=1)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type in ["pie", "bar"]
    
    def test_recommend_categorical_numerical(self, engine):
        """测试分类+数值字段推荐"""
        features = self.create_features(numerical=1, categorical=1)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type == "bar"
        assert recommendations[0].score >= 0.95
    
    def test_recommend_time_numerical(self, engine):
        """测试时间+数值字段推荐"""
        features = self.create_features(numerical=1, time=1)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type == "line"
        assert recommendations[0].score >= 0.95
    
    def test_recommend_two_numerical(self, engine):
        """测试双数值字段推荐"""
        features = self.create_features(numerical=2)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type == "scatter"
    
    def test_recommend_three_numerical(self, engine):
        """测试三数值字段推荐"""
        features = self.create_features(numerical=3)
        recommendations = engine.recommend(features)
        
        assert len(recommendations) > 0
        assert recommendations[0].chart_type in ["scatter_3d", "bar_3d", "radar"]
    
    def test_recommend_sorted_by_score(self, engine):
        """测试推荐结果按评分排序"""
        features = self.create_features(numerical=1, categorical=1)
        recommendations = engine.recommend(features)
        
        scores = [r.score for r in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    def test_recommend_with_selected_fields(self, engine):
        """测试选中字段推荐"""
        features = self.create_features(numerical=2, categorical=1)
        recommendations = engine.recommend(features, selected_fields=["num_0", "cat_0"])
        
        assert len(recommendations) > 0
    
    def test_get_chart_types(self, engine):
        """测试获取图表类型列表"""
        chart_types = engine.CHART_TYPES
        
        assert "bar" in chart_types
        assert "pie" in chart_types
        assert "line" in chart_types
        assert len(chart_types) >= 10
    
    def test_check_condition_equality(self, engine):
        """测试条件匹配 - 相等"""
        assert engine._check_condition(1, 1) == True
        assert engine._check_condition(1, 2) == False
    
    def test_check_condition_gte(self, engine):
        """测试条件匹配 - 大于等于"""
        assert engine._check_condition(">=3", 3) == True
        assert engine._check_condition(">=3", 5) == True
        assert engine._check_condition(">=3", 2) == False
    
    def test_check_condition_gt(self, engine):
        """测试条件匹配 - 大于"""
        assert engine._check_condition(">2", 3) == True
        assert engine._check_condition(">2", 2) == False


class TestChartRecommendationService:
    """图表推荐服务单元测试"""
    
    @pytest.fixture
    def service(self):
        return ChartRecommendationService()
    
    def test_analyze_and_recommend(self, service):
        """测试分析并推荐"""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "A", "value": 30},
        ]
        
        result = service.analyze_and_recommend(data)
        
        assert "features" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
    
    def test_analyze_and_recommend_with_fields(self, service):
        """测试选中字段分析推荐"""
        data = [
            {"category": "A", "value1": 10, "value2": 100},
            {"category": "B", "value1": 20, "value2": 200},
        ]
        
        result = service.analyze_and_recommend(data, fields=["category", "value1"])
        
        assert len(result["features"]["fields"]) == 2
    
    def test_get_chart_types(self, service):
        """测试获取图表类型"""
        chart_types = service.get_chart_types()
        
        assert len(chart_types) > 0
        assert any(ct["type"] == "bar" for ct in chart_types)


class TestFieldTypeEnum:
    """字段类型枚举测试"""
    
    def test_field_types(self):
        """测试字段类型枚举值"""
        assert FieldType.NUMERICAL.value == "numerical"
        assert FieldType.CATEGORICAL.value == "categorical"
        assert FieldType.TIME.value == "time"
        assert FieldType.TEXT.value == "text"


class TestDistributionTypeEnum:
    """分布类型枚举测试"""
    
    def test_distribution_types(self):
        """测试分布类型枚举值"""
        assert DistributionType.NORMAL.value == "normal"
        assert DistributionType.SKEWED.value == "skewed"
        assert DistributionType.UNIFORM.value == "uniform"
        assert DistributionType.UNKNOWN.value == "unknown"


class TestDataClasses:
    """数据类测试"""
    
    def test_field_features_dataclass(self):
        """测试字段特征数据类"""
        features = FieldFeatures(
            name="test_field",
            field_type=FieldType.NUMERICAL,
            distribution=DistributionType.NORMAL,
            missing_ratio=0.1,
            unique_count=100,
            total_count=110,
            stats={"mean": 50.0, "std": 10.0}
        )
        
        assert features.name == "test_field"
        assert features.field_type == FieldType.NUMERICAL
        assert features.missing_ratio == 0.1
    
    def test_data_features_dataclass(self):
        """测试数据特征数据类"""
        features = DataFeatures(
            fields=[],
            numerical_count=2,
            categorical_count=1,
            time_count=0,
            row_count=100,
            correlations=[{"field1": "a", "field2": "b", "correlation": 0.8}]
        )
        
        assert features.numerical_count == 2
        assert features.categorical_count == 1
        assert len(features.correlations) == 1
    
    def test_chart_recommendation_dataclass(self):
        """测试图表推荐数据类"""
        rec = ChartRecommendation(
            chart_type="bar",
            chart_name="📊 柱状图",
            score=0.95,
            reason="分类+数值，最适合对比分析",
            suitable_fields=["category", "value"]
        )
        
        assert rec.chart_type == "bar"
        assert rec.score == 0.95
        assert len(rec.suitable_fields) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
