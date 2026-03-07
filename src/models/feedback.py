"""
反馈循环系统 - Feedback Loop System
参考Metabot设计，实现AI助手的螺旋式进化
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base


class AIFeedback(Base):
    """AI反馈数据表"""
    __tablename__ = "ai_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    
    session_id = Column(String(64), index=True, comment="会话ID")
    message_id = Column(String(64), index=True, comment="消息ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    
    rating = Column(Integer, comment="评分: 1=满意, -1=不满意, 0=中性")
    feedback_type = Column(String(32), comment="反馈类型: positive/negative/neutral")
    
    user_query = Column(Text, comment="用户原始问题")
    ai_response = Column(Text, comment="AI回复内容")
    
    user_correction = Column(Text, nullable=True, comment="用户修正内容")
    correction_type = Column(String(32), nullable=True, comment="修正类型: fact/style/other")
    
    tool_calls = Column(JSON, nullable=True, comment="工具调用记录")
    chart_generated = Column(Boolean, default=False, comment="是否生成图表")
    
    context = Column(JSON, nullable=True, comment="上下文信息")
    
    processed = Column(Boolean, default=False, comment="是否已处理")
    processed_at = Column(DateTime, nullable=True, comment="处理时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "feedback_type": self.feedback_type,
            "user_query": self.user_query[:200] if self.user_query else None,
            "user_correction": self.user_correction,
            "correction_type": self.correction_type,
            "processed": self.processed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FeedbackMemory(Base):
    """反馈记忆层 - 结构化存储用户修正"""
    __tablename__ = "feedback_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    
    feedback_id = Column(Integer, ForeignKey("ai_feedback.id"), comment="关联反馈ID")
    
    memory_type = Column(String(32), comment="记忆类型: correction/pattern/preference")
    
    query_pattern = Column(String(255), comment="问题模式")
    correct_response = Column(Text, comment="正确回复模式")
    
    entity_mentions = Column(JSON, nullable=True, comment="实体提及")
    intent_category = Column(String(64), nullable=True, comment="意图分类")
    
    importance_score = Column(Float, default=1.0, comment="重要性评分")
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(Float, default=0.0, comment="成功率")
    
    active = Column(Boolean, default=True, comment="是否激活")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "memory_type": self.memory_type,
            "query_pattern": self.query_pattern,
            "importance_score": self.importance_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "active": self.active
        }


class FeedbackAnalytics(Base):
    """反馈分析统计表"""
    __tablename__ = "feedback_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    date = Column(DateTime, index=True, comment="统计日期")
    
    total_feedbacks = Column(Integer, default=0, comment="总反馈数")
    positive_count = Column(Integer, default=0, comment="正面反馈数")
    negative_count = Column(Integer, default=0, comment="负面反馈数")
    neutral_count = Column(Integer, default=0, comment="中性反馈数")
    
    satisfaction_rate = Column(Float, default=0.0, comment="满意度")
    
    corrections_count = Column(Integer, default=0, comment="修正次数")
    corrections_applied = Column(Integer, default=0, comment="已应用修正数")
    
    avg_response_time = Column(Float, nullable=True, comment="平均响应时间")
    
    tool_calls_success = Column(Integer, default=0, comment="工具调用成功数")
    tool_calls_failed = Column(Integer, default=0, comment="工具调用失败数")
    
    charts_generated = Column(Integer, default=0, comment="生成图表数")
    charts_positive = Column(Integer, default=0, comment="图表正面反馈数")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "date": self.date.isoformat() if self.date else None,
            "total_feedbacks": self.total_feedbacks,
            "satisfaction_rate": round(self.satisfaction_rate * 100, 1),
            "corrections_count": self.corrections_count,
            "charts_generated": self.charts_generated
        }
