from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class DataFlow(SQLModel, table=True):
    __tablename__ = "data_flows"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    name: str = Field(default="", index=True)
    type: str = Field(default="mingdao")
    appkey: Optional[str] = Field(default=None)
    sign: Optional[str] = Field(default=None)
    worksheet_id: Optional[str] = Field(default=None)
    is_private: int = Field(default=0)
    private_api_url: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    field_types: List["FieldType"] = Relationship(back_populates="data_flow")


class FieldType(SQLModel, table=True):
    __tablename__ = "field_types"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    data_flow_id: int = Field(default=0, foreign_key="data_flows.id")
    worksheet_id: Optional[str] = Field(default=None)
    field_id: str = Field(default="")
    field_name: str = Field(default="")
    data_type: str = Field(default="string")
    is_enabled: str = Field(default="true")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    data_flow: Optional[DataFlow] = Relationship(back_populates="field_types")


class DataSnapshot(SQLModel, table=True):
    __tablename__ = "data_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    data_flow_id: int = Field(default=0)
    name: str = Field(default="")
    worksheet_id: str = Field(default="")
    fields: str = Field(default="[]")
    data: str = Field(default="[]")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    data_flow: Optional[DataFlow] = Relationship()


class Dashboard(SQLModel, table=True):
    __tablename__ = "dashboards"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    name: str = Field(default="")
    data_snapshot_id: Optional[int] = Field(default=None, foreign_key="data_snapshots.id")
    chart_type: str = Field(default="line")
    config: str = Field(default="{}")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    data_snapshot: Optional[DataSnapshot] = Relationship()
