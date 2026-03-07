"""
用户偏好模型 - User Preference Model
存储用户个性化偏好，优先级最高
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from datetime import datetime
from src.core.database import Base


class UserPreference(Base):
    """用户偏好表 - 存储用户个性化设置和行为偏好"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, index=True, comment="用户ID")
    
    preference_type = Column(String(32), comment="偏好类型: style/format/priority/frequency")
    preference_key = Column(String(64), comment="偏好键: concise/detailed/chart_first/data_first")
    preference_value = Column(Text, comment="偏好值")
    
    source = Column(String(32), default="auto", comment="来源: auto(自动提取)/manual(手动设置)")
    confidence = Column(Float, default=0.5, comment="置信度: 0-1")
    
    usage_count = Column(Integer, default=0, comment="使用次数")
    last_used_at = Column(DateTime, comment="最后使用时间")
    
    active = Column(Boolean, default=True, comment="是否激活")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preference_type": self.preference_type,
            "preference_key": self.preference_key,
            "preference_value": self.preference_value,
            "source": self.source,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "active": self.active
        }


class SuccessCase(Base):
    """成功案例表 - 存储正面反馈的成功模式"""
    __tablename__ = "success_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, index=True, nullable=True, comment="用户ID")
    
    query_pattern = Column(String(255), index=True, comment="问题模式/关键词")
    query_intent = Column(String(64), comment="意图分类: data_analysis/chart_generation/data_query")
    
    original_query = Column(Text, comment="原始问题")
    successful_response = Column(Text, comment="成功的AI回复")
    
    tool_calls = Column(JSON, comment="工具调用链")
    tool_sequence = Column(JSON, comment="工具调用顺序")
    
    chart_generated = Column(Boolean, default=False, comment="是否生成图表")
    chart_types = Column(JSON, comment="图表类型列表")
    
    satisfaction_score = Column(Float, default=1.0, comment="满意度评分")
    
    keywords = Column(JSON, comment="关键词列表")
    entities = Column(JSON, comment="实体提及")
    
    similarity_count = Column(Integer, default=0, comment="相似问题匹配次数")
    reuse_count = Column(Integer, default=0, comment="被参考次数")
    
    importance_score = Column(Float, default=1.0, comment="重要性评分")
    
    active = Column(Boolean, default=True, comment="是否激活")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "query_pattern": self.query_pattern,
            "query_intent": self.query_intent,
            "tool_sequence": self.tool_sequence,
            "satisfaction_score": self.satisfaction_score,
            "reuse_count": self.reuse_count,
            "importance_score": self.importance_score,
            "active": self.active
        }


class FailureLesson(Base):
    """失败教训表 - 存储负面反馈的教训"""
    __tablename__ = "failure_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, index=True, nullable=True, comment="用户ID")
    
    query_pattern = Column(String(255), index=True, comment="问题模式/关键词")
    
    original_query = Column(Text, comment="原始问题")
    failed_response = Column(Text, comment="失败的AI回复")
    failure_reason = Column(Text, comment="失败原因")
    
    user_correction = Column(Text, comment="用户修正内容")
    correct_approach = Column(Text, comment="正确做法")
    
    failure_type = Column(String(32), comment="失败类型: wrong_tool/wrong_field/missing_step/bad_format")
    
    keywords = Column(JSON, comment="关键词列表")
    
    occurrence_count = Column(Integer, default=1, comment="发生次数")
    
    importance_score = Column(Float, default=0.5, comment="重要性评分")
    
    active = Column(Boolean, default=True, comment="是否激活")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "query_pattern": self.query_pattern,
            "failure_reason": self.failure_reason,
            "correct_approach": self.correct_approach,
            "failure_type": self.failure_type,
            "occurrence_count": self.occurrence_count,
            "importance_score": self.importance_score,
            "active": self.active
        }
