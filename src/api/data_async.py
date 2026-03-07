from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
import json
import pandas as pd
import io
from datetime import datetime

from src.core.database_async import get_db
from src.models.config_sqlmodel import DataFlow, FieldType, DataSnapshot
from src.services.mingdao import MingDaoService
from src.core.permissions_async import get_current_user, check_resource_access, filter_by_user_permission

router = APIRouter(prefix="/api/async/data", tags=["async-data"])

class FieldInfo(BaseModel):
    id: str
    name: str
    type: Optional[str] = None

class DataQueryRequest(BaseModel):
    dataflow_id: int
    field_ids: Optional[List[str]] = None
    page_index: int = 1
    page_size: int = 100

class DataSnapshotCreate(BaseModel):
    dataflow_id: int
    name: str
    fields: str
    data: str

class DataSnapshotResponse(BaseModel):
    id: int
    data_flow_id: int
    name: str
    worksheet_id: str
    created_at: str

    class Config:
        from_attributes = True

@router.get("/{dataflow_id}/fields")
async def get_fields(
    dataflow_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    is_private_bool = bool(dataflow.is_private)
    base_url = dataflow.private_api_url if is_private_bool else "https://api.mingdao.com"
    service = MingDaoService(dataflow.appkey, dataflow.sign, base_url)
    try:
        result = service.get_fields(dataflow.worksheet_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取字段失败: {str(e)}")

@router.get("/{dataflow_id}/enabled-fields")
async def get_enabled_fields(
    dataflow_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    query = select(FieldType).where(
        FieldType.data_flow_id == dataflow_id,
        FieldType.is_enabled == "true"
    )
    result = await db.execute(query)
    saved_fields = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "field_id": f.field_id,
                "field_name": f.field_name,
                "data_type": f.data_type
            }
            for f in saved_fields
        ]
    }

@router.post("/query")
async def query_data(
    query_req: DataQueryRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == query_req.dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    is_private_bool = bool(dataflow.is_private)
    base_url = dataflow.private_api_url if is_private_bool else "https://api.mingdao.com"
    service = MingDaoService(dataflow.appkey, dataflow.sign, base_url)
    
    try:
        all_data = service.get_data(
            dataflow.worksheet_id,
            page_index=query_req.page_index,
            page_size=query_req.page_size
        )
        
        if query_req.field_ids:
            query = select(FieldType).where(
                FieldType.data_flow_id == query_req.dataflow_id,
                FieldType.is_enabled == "true"
            )
            result = await db.execute(query)
            saved_fields = result.scalars().all()
            
            enabled_field_ids = {f.field_id for f in saved_fields}
            filtered_data = []
            for row in all_data:
                filtered_row = {
                    k: v for k, v in row.items()
                    if k in enabled_field_ids
                }
                if query_req.field_ids:
                    filtered_row = {
                        k: v for k, v in filtered_row.items()
                        if k in query_req.field_ids
                    }
                if filtered_row:
                    filtered_data.append(filtered_row)
            all_data = filtered_data
        
        return {"success": True, "data": all_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询数据失败: {str(e)}")

@router.post("/snapshot")
async def create_snapshot(
    snapshot: DataSnapshotCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == snapshot.dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    db_snapshot = DataSnapshot(
        user_id=user.id,
        data_flow_id=snapshot.dataflow_id,
        name=snapshot.name,
        worksheet_id=dataflow.worksheet_id,
        fields=snapshot.fields,
        data=snapshot.data
    )
    db.add(db_snapshot)
    await db.commit()
    await db.refresh(db_snapshot)
    
    return {
        "success": True,
        "data": {
            "id": db_snapshot.id,
            "name": db_snapshot.name,
            "created_at": db_snapshot.created_at.isoformat() if db_snapshot.created_at else ""
        }
    }

@router.get("/snapshots")
async def get_snapshots(
    dataflow_id: Optional[int] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataSnapshot)
    if dataflow_id:
        query = query.where(DataSnapshot.data_flow_id == dataflow_id)
    query = filter_by_user_permission(query, user, DataSnapshot.user_id)
    query = query.order_by(DataSnapshot.created_at.desc())
    
    result = await db.execute(query)
    snapshots = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "data_flow_id": s.data_flow_id,
                "name": s.name,
                "worksheet_id": s.worksheet_id,
                "fields": s.fields,
                "data": s.data,
                "created_at": s.created_at.isoformat() if s.created_at else ""
            }
            for s in snapshots
        ]
    }

@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(
    snapshot_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataSnapshot).where(DataSnapshot.id == snapshot_id)
    result = await db.execute(query)
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="快照不存在")
    check_resource_access(user, snapshot.user_id, "快照")
    
    return {
        "success": True,
        "data": {
            "id": snapshot.id,
            "data_flow_id": snapshot.data_flow_id,
            "name": snapshot.name,
            "worksheet_id": snapshot.worksheet_id,
            "fields": snapshot.fields,
            "data": snapshot.data,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else ""
        }
    }

@router.delete("/snapshots/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataSnapshot).where(DataSnapshot.id == snapshot_id)
    result = await db.execute(query)
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="快照不存在")
    check_resource_access(user, snapshot.user_id, "快照")
    
    await db.delete(snapshot)
    await db.commit()
    
    return {"success": True, "message": "快照已删除"}

@router.post("/import")
async def import_file(
    dataflow_id: int,
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(DataFlow).where(DataFlow.id == dataflow_id)
    result = await db.execute(query)
    dataflow = result.scalar_one_or_none()
    
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    content = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        data_json = df.to_json(orient='records', force_ascii=False)
        fields_json = json.dumps([
            {"field_id": str(col), "field_name": col, "data_type": str(dtype)}
            for col, dtype in df.dtypes.items()
        ])
        
        return {
            "success": True,
            "data": {
                "fields": json.loads(fields_json),
                "data": json.loads(data_json),
                "row_count": len(df)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入文件失败: {str(e)}")
