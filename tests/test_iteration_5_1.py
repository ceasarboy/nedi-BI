"""
迭代5.1功能测试用例
测试图表配置API、记忆管理增强功能
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app


client = TestClient(app)


class TestChartConfigAPI:
    """图表配置API测试"""
    
    def test_get_chart_types(self):
        """测试获取图表类型列表"""
        response = client.get("/api/chart/types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["types"]) >= 8
    
    def test_bar_chart_config(self):
        """测试柱状图配置生成"""
        response = client.post("/api/chart/config", json={
            "chart_type": "bar",
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20},
                {"category": "C", "value": 30}
            ],
            "x_field": "category",
            "y_field": "value",
            "title": "测试柱状图"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "config" in data
        assert data["config"]["chart_type"] == "bar"
        assert "option" in data["config"]
    
    def test_line_chart_config(self):
        """测试折线图配置生成"""
        response = client.post("/api/chart/config", json={
            "chart_type": "line",
            "data": [
                {"date": "2026-01-01", "value": 100},
                {"date": "2026-01-02", "value": 150}
            ],
            "x_field": "date",
            "y_field": "value",
            "title": "测试折线图",
            "smooth": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_pie_chart_config(self):
        """测试饼图配置生成"""
        response = client.post("/api/chart/config", json={
            "chart_type": "pie",
            "data": [
                {"name": "产品A", "value": 30},
                {"name": "产品B", "value": 50}
            ],
            "category_field": "name",
            "value_field": "value",
            "title": "测试饼图"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_scatter_chart_config(self):
        """测试散点图配置生成"""
        response = client.post("/api/chart/config", json={
            "chart_type": "scatter",
            "data": [
                {"x": 1, "y": 10},
                {"x": 2, "y": 20}
            ],
            "x_field": "x",
            "y_field": "y",
            "title": "测试散点图"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_heatmap_chart_config(self):
        """测试热力图配置生成"""
        response = client.post("/api/chart/config", json={
            "chart_type": "heatmap",
            "data": [
                {"x": "A", "y": "1", "value": 10},
                {"x": "B", "y": "2", "value": 20}
            ],
            "x_field": "x",
            "y_field": "y",
            "value_field": "value",
            "title": "测试热力图"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_empty_data_error(self):
        """测试空数据错误"""
        response = client.post("/api/chart/config", json={
            "chart_type": "bar",
            "data": []
        })
        
        assert response.status_code == 400


class TestMemoryPreferenceAPI:
    """记忆管理偏好API测试"""
    
    def test_add_preference(self):
        """测试添加用户偏好"""
        response = client.post("/api/feedback/memory/preferences", json={
            "preference_type": "style",
            "preference_key": "test_key",
            "preference_value": "test_value",
            "confidence": 0.9,
            "source": "manual"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["preference_key"] == "test_key"
        assert data["preference_value"] == "test_value"
    
    def test_get_preferences(self):
        """测试获取用户偏好列表"""
        response = client.get("/api/feedback/memory/preferences")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_memory_stats(self):
        """测试获取记忆统计"""
        response = client.get("/api/feedback/memory/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "preferences_count" in data
        assert "success_cases_count" in data
        assert "failure_lessons_count" in data


class TestChartRecommendationIntegration:
    """图表推荐集成测试"""
    
    def test_recommend_with_data(self):
        """测试带数据的推荐"""
        response = client.post("/api/chart-recommend/recommend", json={
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
    
    def test_analyze_data(self):
        """测试数据分析"""
        response = client.post("/api/chart-recommend/analyze", json={
            "data": [
                {"name": "Alice", "age": 25, "score": 85},
                {"name": "Bob", "age": 30, "score": 90}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "features" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
