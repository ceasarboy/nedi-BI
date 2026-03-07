"""
三层记忆系统测试用例
测试用户偏好、成功案例、失败教训的存储和检索功能
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.memory import UserPreference, SuccessCase, FailureLesson, Base
from src.services.memory_service import MemoryService


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def memory_service(db_session):
    """创建MemoryService实例"""
    return MemoryService(db_session)


class TestUserPreference:
    """用户偏好层测试"""
    
    def test_save_user_preference(self, memory_service):
        """测试保存用户偏好"""
        pref = memory_service.save_user_preference(
            user_id=1,
            preference_type="style",
            preference_key="response_length",
            preference_value="concise",
            source="auto"
        )
        
        assert pref.id is not None
        assert pref.user_id == 1
        assert pref.preference_key == "response_length"
        assert pref.preference_value == "concise"
        assert pref.confidence == 0.5
    
    def test_update_existing_preference(self, memory_service):
        """测试更新已存在的偏好"""
        memory_service.save_user_preference(
            user_id=1,
            preference_type="style",
            preference_key="response_length",
            preference_value="concise",
            source="auto"
        )
        
        updated_pref = memory_service.save_user_preference(
            user_id=1,
            preference_type="style",
            preference_key="response_length",
            preference_value="detailed",
            source="manual"
        )
        
        assert updated_pref.confidence > 0.5
        assert updated_pref.preference_value == "detailed"
    
    def test_get_user_preferences(self, memory_service):
        """测试获取用户偏好列表"""
        memory_service.save_user_preference(1, "style", "key1", "value1")
        memory_service.save_user_preference(1, "style", "key2", "value2")
        memory_service.save_user_preference(1, "style", "key3", "value3")
        
        prefs = memory_service.get_user_preferences(1, limit=5)
        
        assert len(prefs) == 3
    
    def test_extract_preferences_from_positive_feedback(self, memory_service):
        """测试从正面反馈提取偏好"""
        query = "帮我分析这组数据"
        response = "根据数据分析，结果如下：\n\n图表已生成：\n![柱状图](chart.png)"
        
        extracted = memory_service.extract_preferences_from_positive_feedback(
            user_id=1,
            query=query,
            response=response
        )
        
        assert len(extracted) > 0
        prefs = memory_service.get_user_preferences(1)
        assert any(p.preference_key == "chart_preference" for p in prefs)


class TestSuccessCase:
    """成功案例层测试"""
    
    def test_save_success_case(self, memory_service):
        """测试保存成功案例"""
        case = memory_service.save_success_case(
            user_id=1,
            query="查询影像评分数据",
            response="查询成功，共找到100条记录",
            tool_calls=[{"name": "pbbi_list_snapshots"}, {"name": "pbbi_query_snapshot"}],
            chart_generated=True
        )
        
        assert case.id is not None
        assert case.query_intent == "data_query"
        assert case.chart_generated == True
        assert len(case.tool_sequence) == 2
    
    def test_get_success_cases_by_intent(self, memory_service):
        """测试按意图获取成功案例"""
        memory_service.save_success_case(
            user_id=1,
            query="生成柱状图",
            response="图表已生成",
            tool_calls=[{"name": "pbbi_generate_bar_chart"}],
            chart_generated=True
        )
        
        memory_service.save_success_case(
            user_id=1,
            query="查询数据",
            response="查询成功",
            tool_calls=[{"name": "pbbi_query_snapshot"}],
            chart_generated=False
        )
        
        cases = memory_service.get_success_cases(
            query="帮我生成一个柱状图",
            user_id=1,
            limit=2
        )
        
        assert len(cases) > 0
    
    def test_reuse_count_increment(self, memory_service):
        """测试成功案例复用次数增加"""
        memory_service.save_success_case(
            user_id=1,
            query="查询数据",
            response="查询成功",
            tool_calls=[],
            chart_generated=False
        )
        
        initial_count = memory_service.get_success_cases("查询数据", 1)[0].reuse_count or 0
        
        memory_service.get_success_cases("查询数据", 1)
        
        updated_count = memory_service.get_success_cases("查询数据", 1)[0].reuse_count
        assert updated_count > initial_count


class TestFailureLesson:
    """失败教训层测试"""
    
    def test_save_failure_lesson(self, memory_service):
        """测试保存失败教训"""
        lesson = memory_service.save_failure_lesson(
            user_id=1,
            query="查询影像数据",
            failed_response="查询失败，字段不存在",
            user_correction="应该先查询快照结构，确认字段名后再查询",
            failure_type="wrong_field"
        )
        
        assert lesson.id is not None
        assert lesson.failure_reason is not None
        assert lesson.correct_approach is not None
    
    def test_get_failure_lessons(self, memory_service):
        """测试获取失败教训"""
        memory_service.save_failure_lesson(
            user_id=1,
            query="查询影像数据",
            failed_response="失败响应",
            user_correction="正确做法",
            failure_type="general"
        )
        
        lessons = memory_service.get_failure_lessons(
            query="查询影像数据",
            user_id=1,
            limit=2
        )
        
        assert len(lessons) > 0
    
    def test_failure_reason_extraction(self, memory_service):
        """测试失败原因提取"""
        lesson = memory_service.save_failure_lesson(
            user_id=1,
            query="查询数据",
            failed_response="使用了错误的字段名",
            user_correction="字段名应该是score而不是scroe",
            failure_type="wrong_field"
        )
        
        assert "字段" in lesson.failure_reason


class TestMemoryContext:
    """记忆上下文测试"""
    
    def test_build_memory_context_empty(self, memory_service):
        """测试空记忆上下文"""
        context = memory_service.build_memory_context(
            user_id=1,
            query="测试查询"
        )
        
        assert context == ""
    
    def test_build_memory_context_with_preferences(self, memory_service):
        """测试带偏好的记忆上下文"""
        memory_service.save_user_preference(1, "style", "response_length", "concise")
        
        context = memory_service.build_memory_context(
            user_id=1,
            query="测试查询"
        )
        
        assert "用户偏好" in context
        assert "response_length" in context
    
    def test_build_memory_context_full(self, memory_service):
        """测试完整记忆上下文"""
        memory_service.save_user_preference(1, "style", "response_length", "concise")
        
        memory_service.save_success_case(
            user_id=1,
            query="查询数据",
            response="成功响应",
            tool_calls=[{"name": "pbbi_query_snapshot"}],
            chart_generated=False
        )
        
        memory_service.save_failure_lesson(
            user_id=1,
            query="错误查询",
            failed_response="失败响应",
            user_correction="正确做法",
            failure_type="general"
        )
        
        context = memory_service.build_memory_context(
            user_id=1,
            query="查询数据"
        )
        
        assert "用户偏好" in context
        assert "成功案例" in context or "避免" in context


class TestIntentClassification:
    """意图分类测试"""
    
    def test_classify_chart_intent(self, memory_service):
        """测试图表生成意图"""
        intent = memory_service._classify_intent("帮我生成一个柱状图")
        assert intent == "chart_generation"
    
    def test_classify_analysis_intent(self, memory_service):
        """测试数据分析意图"""
        intent = memory_service._classify_intent("分析这组数据的趋势")
        assert intent == "data_analysis"
    
    def test_classify_query_intent(self, memory_service):
        """测试数据查询意图"""
        intent = memory_service._classify_intent("查询所有影像评分数据")
        assert intent == "data_query"
    
    def test_classify_schema_intent(self, memory_service):
        """测试结构查询意图"""
        intent = memory_service._classify_intent("查看快照的字段结构")
        assert intent == "schema_query"


class TestKeywordExtraction:
    """关键词提取测试"""
    
    def test_extract_keywords(self, memory_service):
        """测试关键词提取"""
        keywords = memory_service._extract_keywords("查询影像评分数据并生成柱状图")
        
        assert len(keywords) > 0
    
    def test_extract_keywords_empty(self, memory_service):
        """测试空文本关键词提取"""
        keywords = memory_service._extract_keywords("")
        
        assert len(keywords) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
