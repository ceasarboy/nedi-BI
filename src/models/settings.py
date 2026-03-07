"""
系统设置模型
支持UI风格、AI配置、第三方平台模型选择
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from datetime import datetime
from src.core.database import Base


class SystemSettings(Base):
    """系统设置表"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, nullable=True, comment="用户ID，NULL表示全局设置")
    
    ui_style = Column(String(32), default="modern", comment="UI风格: modern/classic/minimal")
    ui_primary_color = Column(String(16), default="#3b82f6", comment="主色调")
    ui_font_size = Column(String(8), default="medium", comment="字体大小: small/medium/large")
    ui_dark_mode = Column(Boolean, default=False, comment="暗黑模式")
    
    ai_provider = Column(String(32), default="deepseek", comment="AI提供商: deepseek/openai/siliconflow/zhipu")
    ai_api_key = Column(Text, nullable=True, comment="API密钥(加密存储)")
    ai_base_url = Column(String(255), nullable=True, comment="API基础URL")
    ai_model = Column(String(128), default="deepseek-chat", comment="模型名称")
    ai_temperature = Column(String(8), default="0.7", comment="温度参数")
    ai_max_tokens = Column(Integer, default=4096, comment="最大token数")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ui_style": self.ui_style,
            "ui_primary_color": self.ui_primary_color,
            "ui_font_size": self.ui_font_size,
            "ui_dark_mode": self.ui_dark_mode,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "ai_temperature": self.ai_temperature,
            "ai_max_tokens": self.ai_max_tokens,
            "has_api_key": bool(self.ai_api_key),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AIProvider(Base):
    """AI提供商配置表"""
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(32), unique=True, comment="提供商名称")
    display_name = Column(String(64), comment="显示名称")
    base_url = Column(String(255), comment="API基础URL")
    models = Column(JSON, comment="支持的模型列表")
    default_model = Column(String(64), comment="默认模型")
    icon = Column(String(64), comment="图标")
    description = Column(Text, comment="描述")
    
    active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "base_url": self.base_url,
            "models": self.models,
            "default_model": self.default_model,
            "icon": self.icon,
            "description": self.description
        }
