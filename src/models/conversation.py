"""
对话会话模型 - Conversation Session Model
支持多会话管理和上下文记忆
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base


class ConversationSession(Base):
    """对话会话表"""
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    session_id = Column(String(64), unique=True, index=True, comment="会话唯一标识")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    
    title = Column(String(255), nullable=True, comment="会话标题")
    summary = Column(Text, nullable=True, comment="会话摘要")
    
    messages = Column(JSON, default=list, comment="对话消息列表")
    message_count = Column(Integer, default=0, comment="消息数量")
    
    is_active = Column(Boolean, default=True, comment="是否活跃")
    is_archived = Column(Boolean, default=False, comment="是否已归档")
    
    context_tokens = Column(Integer, default=0, comment="上下文token数")
    context_limit = Column(Integer, default=4000, comment="上下文限制")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title or f"对话 {self.id}",
            "summary": self.summary,
            "message_count": self.message_count,
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "context_tokens": self.context_tokens,
            "context_limit": self.context_limit,
            "context_warning": self.context_tokens > self.context_limit * 0.8,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ConversationMessage(Base):
    """对话消息表（用于持久化存储）"""
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    session_id = Column(String(64), index=True, comment="会话ID")
    role = Column(String(32), comment="角色: user/assistant/system")
    content = Column(Text, comment="消息内容")
    
    tool_calls = Column(JSON, nullable=True, comment="工具调用记录")
    feedback_rating = Column(Integer, nullable=True, comment="反馈评分")
    
    tokens = Column(Integer, default=0, comment="token数量")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "feedback_rating": self.feedback_rating,
            "tokens": self.tokens,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
