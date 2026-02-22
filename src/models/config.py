from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base

class DataFlow(Base):
    __tablename__ = "data_flows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="mingdao")  # 'mingdao' or 'local'
    appkey = Column(String, nullable=True)
    sign = Column(String, nullable=True)
    worksheet_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    field_types = relationship("FieldType", back_populates="data_flow", cascade="all, delete-orphan")

class FieldType(Base):
    __tablename__ = "field_types"

    id = Column(Integer, primary_key=True, index=True)
    data_flow_id = Column(Integer, ForeignKey("data_flows.id"), nullable=False)
    worksheet_id = Column(String, nullable=True)
    field_id = Column(String, nullable=False)
    field_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_enabled = Column(Text, nullable=False, default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    data_flow = relationship("DataFlow", back_populates="field_types")

class DataSnapshot(Base):
    __tablename__ = "data_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_flow_id = Column(Integer, ForeignKey("data_flows.id"), nullable=False)
    name = Column(String, nullable=False)
    worksheet_id = Column(String, nullable=False)
    fields = Column(Text, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    data_flow = relationship("DataFlow")

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    data_snapshot_id = Column(Integer, ForeignKey("data_snapshots.id"), nullable=True)
    chart_type = Column(String, nullable=False, default="line")
    config = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    data_snapshot = relationship("DataSnapshot")
