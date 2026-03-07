from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel, model_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete
from typing import List, Optional
import pandas as pd
import io
import json
from datetime import datetime

from src.core.database_async import get_db
from src.models.config_sqlmodel import DataFlow, FieldType, DataSnapshot
from src.services.mingdao import MingDaoService
from src.core.permissions_async import get_current_user, check_resource_access, filter_by_user_permission

router = APIRouter(prefix="/api/async/dataflows", tags=["async-dataflows"])

class DataFlowCreate(BaseModel):
    name: str
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None
    type: str = "mingdao"
    is_private: bool = False
    private_api_url: Optional[str] = None

class DataFlowUpdate(BaseModel):
    name: Optional[str] = None
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None
    is_private: Optional[bool] = None
    private_api_url: Optional[str] = None

class DataFlowResponse(BaseModel):
    id: int
    name: str
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None
    type: str = "mingdao"
    is_private: bool = False
    private_api_url: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def convert_is_private(cls, data):
        if hasattr(data, 'is_private'):
            val = data.is_private
            if isinstance(val, int):
                data.is_private = bool(val)
        return data

    class Config:
        from_attributes = True

class FieldConfig(BaseModel):
    field_id: str
    field_name: str
    data_type: str
    is_enabled: str = "true"

class FieldConfigSave(BaseModel):
    fields: List[FieldConfig]

class PaginationRequest(BaseModel):
    page: int = 1
    page_size: int = 10

@router.get("", response_model=List[DataFlowResponse])
async def get_dataflows(
    page: int = 1,
    page_size: int = 10,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    query = select(DataFlow)
    query = filter_by_user_permission(query, user, DataFlow.user_id)
    query = query.order_by(DataFlow.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    dataflows = result.scalars().all()
    return dataflows

@router.get("/count")
async def get_dataflows_count(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow)
    query = filter_by_user_permission(query, user, DataFlow.user_id)
    result = await db.execute(query)
    count = len(result.scalars().all())
    return {"success": True, "data": {"count": count}}

@router.get("/{dataflow_id}", response_model=DataFlowResponse)
async def get_dataflow(
    dataflow_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()

    if not dataflow:
        raise HTTPException(status_code=404, detail="DataFlow not found")

    check_resource_access(user, dataflow.user_id)
    return dataflow

@router.post("", response_model=DataFlowResponse)
async def create_dataflow(
    dataflow: DataFlowCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    db_dataflow = DataFlow(
        name=dataflow.name,
        appkey=dataflow.appkey,
        sign=dataflow.sign,
        worksheet_id=dataflow.worksheet_id,
        type=dataflow.type,
        user_id=user.id,
        is_private=1 if dataflow.is_private else 0,
        private_api_url=dataflow.private_api_url
    )
    db.add(db_dataflow)
    await db.commit()
    await db.refresh(db_dataflow)
    return db_dataflow

@router.put("/{dataflow_id}", response_model=DataFlowResponse)
async def update_dataflow(
    dataflow_id: int,
    dataflow: DataFlowUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    db_dataflow = result.scalar_one_or_none()

    if not db_dataflow:
        raise HTTPException(status_code=404, detail="DataFlow not found")

    check_resource_access(user, db_dataflow.user_id)

    if dataflow.name is not None:
        db_dataflow.name = dataflow.name
    if dataflow.appkey is not None:
        db_dataflow.appkey = dataflow.appkey
    if dataflow.sign is not None:
        db_dataflow.sign = dataflow.sign
    if dataflow.worksheet_id is not None:
        db_dataflow.worksheet_id = dataflow.worksheet_id
    if dataflow.is_private is not None:
        db_dataflow.is_private = 1 if dataflow.is_private else 0
    if dataflow.private_api_url is not None:
        db_dataflow.private_api_url = dataflow.private_api_url

    db_dataflow.updated_at = datetime.now()
    await db.commit()
    await db.refresh(db_dataflow)
    return db_dataflow

@router.delete("/{dataflow_id}")
async def delete_dataflow(
    dataflow_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()

    if not dataflow:
        raise HTTPException(status_code=404, detail="DataFlow not found")

    check_resource_access(user, dataflow.user_id)

    await db.delete(dataflow)
    await db.commit()
    return {"success": True, "message": "DataFlow deleted"}

@router.post("/{dataflow_id}/fields")
async def save_field_config(
    dataflow_id: int,
    config: FieldConfigSave,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()

    if not dataflow:
        raise HTTPException(status_code=404, detail="DataFlow not found")

    check_resource_access(user, dataflow.user_id)

    await db.execute(delete(FieldType).where(FieldType.data_flow_id == dataflow_id))

    for field in config.fields:
        db_field = FieldType(
            data_flow_id=dataflow_id,
            worksheet_id=dataflow.worksheet_id,
            field_id=field.field_id,
            field_name=field.field_name,
            data_type=field.data_type,
            is_enabled=field.is_enabled
        )
        db.add(db_field)

    await db.commit()
    return {"success": True, "message": "Field config saved"}

@router.get("/{dataflow_id}/fields")
async def get_field_config(
    dataflow_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()

    if not dataflow:
        raise HTTPException(status_code=404, detail="DataFlow not found")

    check_resource_access(user, dataflow.user_id)

    query = select(FieldType).where(FieldType.data_flow_id == dataflow_id)
    result = await db.execute(query)
    fields = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "field_id": f.field_id,
                "field_name": f.field_name,
                "data_type": f.data_type,
                "is_enabled": f.is_enabled
            }
            for f in fields
        ]
    }
