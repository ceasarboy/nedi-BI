"""
图表智能推荐系统集成测试
测试API端点和完整流程
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app


client = TestClient(app)


class TestChartRecommendationAPI:
    """图表推荐API集成测试"""
    
    def test_analyze_endpoint_success(self):
        """测试分析端点 - 成功"""
        response = client.post("/api/chart-recommend/analyze", json={
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20},
                {"category": "C", "value": 30}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "features" in data
        assert data["features"]["numerical_count"] == 1
        assert data["features"]["categorical_count"] == 1
    
    def test_analyze_endpoint_with_fields(self):
        """测试分析端点 - 指定字段"""
        response = client.post("/api/chart-recommend/analyze", json={
            "data": [
                {"category": "A", "value1": 10, "value2": 100},
                {"category": "B", "value1": 20, "value2": 200}
            ],
            "fields": ["category", "value1"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]["fields"]) == 2
    
    def test_analyze_endpoint_empty_data(self):
        """测试分析端点 - 空数据"""
        response = client.post("/api/chart-recommend/analyze", json={
            "data": []
        })
        
        assert response.status_code == 400
    
    def test_recommend_endpoint_success(self):
        """测试推荐端点 - 成功"""
        response = client.post("/api/chart-recommend/recommend", json={
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20},
                {"category": "C", "value": 30}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "features" in data
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
    
    def test_recommend_endpoint_single_numerical(self):
        """测试推荐端点 - 单数值字段"""
        response = client.post("/api/chart-recommend/recommend", json={
            "data": [
                {"value": 10}, {"value": 20}, {"value": 30}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"][0]["chart_type"] in ["histogram", "box_plot"]
    
    def test_recommend_endpoint_time_series(self):
        """测试推荐端点 - 时间序列"""
        response = client.post("/api/chart-recommend/recommend", json={
            "data": [
                {"date": "2026-01-01", "value": 10},
                {"date": "2026-01-02", "value": 20},
                {"date": "2026-01-03", "value": 30}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) > 0
    
    def test_recommend_endpoint_two_numerical(self):
        """测试推荐端点 - 双数值"""
        response = client.post("/api/chart-recommend/recommend", json={
            "data": [
                {"x": 1, "y": 10},
                {"x": 2, "y": 20},
                {"x": 3, "y": 30}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"][0]["chart_type"] == "scatter"
    
    def test_chart_types_endpoint(self):
        """测试获取图表类型端点"""
        response = client.get("/api/chart-recommend/chart-types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["chart_types"]) > 0
    
    def test_stats_endpoint(self):
        """测试统计端点"""
        response = client.get("/api/chart-recommend/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data


class TestMemoryManagementAPI:
    """记忆管理API集成测试"""
    
    def test_get_memory_stats(self):
        """测试获取记忆统计"""
        response = client.get("/api/feedback/memory/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "preferences_count" in data
        assert "success_cases_count" in data
        assert "failure_lessons_count" in data
    
    def test_get_preferences(self):
        """测试获取用户偏好列表"""
        response = client.get("/api/feedback/memory/preferences")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_success_cases(self):
        """测试获取成功案例列表"""
        response = client.get("/api/feedback/memory/success-cases")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_failure_lessons(self):
        """测试获取失败教训列表"""
        response = client.get("/api/feedback/memory/failure-lessons")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestEndToEndFlow:
    """端到端流程测试"""
    
    def test_full_recommendation_flow(self):
        """测试完整推荐流程"""
        data = [
            {"category": "产品A", "sales": 1000, "profit": 200},
            {"category": "产品B", "sales": 1500, "profit": 300},
            {"category": "产品C", "sales": 800, "profit": 150},
            {"category": "产品D", "sales": 1200, "profit": 250}
        ]
        
        analyze_response = client.post("/api/chart-recommend/analyze", json={"data": data})
        assert analyze_response.status_code == 200
        features = analyze_response.json()["features"]
        
        recommend_response = client.post("/api/chart-recommend/recommend", json={"data": data})
        assert recommend_response.status_code == 200
        recommendations = recommend_response.json()["recommendations"]
        
        assert len(recommendations) > 0
        assert recommendations[0]["score"] >= 0.5
        assert recommendations[0]["reason"] is not None
    
    def test_recommendation_with_different_data_types(self):
        """测试不同数据类型的推荐"""
        test_cases = [
            {
                "data": [{"value": i} for i in range(100)],
                "expected_first": ["histogram", "box_plot"]
            },
            {
                "data": [{"category": chr(65 + i % 5)} for i in range(50)],
                "expected_first": ["pie", "bar"]
            },
            {
                "data": [{"date": f"2026-01-{i+1:02d}", "value": i * 10} for i in range(30)],
                "expected_first": ["bar", "line", "pie"]
            }
        ]
        
        for case in test_cases:
            response = client.post("/api/chart-recommend/recommend", json={"data": case["data"]})
            assert response.status_code == 200
            chart_type = response.json()["recommendations"][0]["chart_type"]
            assert chart_type in case["expected_first"], f"Expected {case['expected_first']}, got {chart_type}"


class TestPerformance:
    """性能测试"""
    
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time
        
        large_data = [
            {"category": f"cat_{i % 20}", "value": i, "score": i * 0.5}
            for i in range(10000)
        ]
        
        start_time = time.time()
        response = client.post("/api/chart-recommend/recommend", json={"data": large_data})
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0, "推荐响应时间应小于5秒"
    
    def test_analyze_performance(self):
        """测试分析性能"""
        import time
        
        data = [{"field1": i, "field2": f"cat_{i % 100}", "field3": i * 2} for i in range(5000)]
        
        start_time = time.time()
        response = client.post("/api/chart-recommend/analyze", json={"data": data})
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0, "分析响应时间应小于3秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
