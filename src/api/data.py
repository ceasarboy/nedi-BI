from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import pandas as pd
import io
from datetime import datetime

from src.core.database import get_db
from src.models.config import DataFlow, FieldType, DataSnapshot
from src.services.mingdao import MingDaoService
from src.core.permissions import get_current_user, check_resource_access, filter_by_user_permission

router = APIRouter(prefix="/api/data", tags=["data"])

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
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
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
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    saved_fields = db.query(FieldType).filter(
        FieldType.data_flow_id == dataflow_id,
        FieldType.is_enabled == "true"
    ).all()
    
    response_fields = []
    for field in saved_fields:
        response_fields.append({
            "field_id": field.field_id,
            "field_name": field.field_name,
            "data_type": field.data_type
        })
    
    return {"success": True, "data": response_fields}

@router.post("/query")
async def query_data(
    request: DataQueryRequest,
    fastapi_request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == request.dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    is_private_bool = bool(dataflow.is_private)
    base_url = dataflow.private_api_url if is_private_bool else "https://api.mingdao.com"
    service = MingDaoService(dataflow.appkey, dataflow.sign, base_url)
    
    enabled_fields = db.query(FieldType).filter(
        FieldType.data_flow_id == request.dataflow_id,
        FieldType.is_enabled == "true"
    ).all()
    
    field_ids = [f.field_id for f in enabled_fields] if enabled_fields else None
    
    try:
        result = service.get_rows(dataflow.worksheet_id, field_ids, request.page_size)
        
        rows = result.get("data", {}).get("data", [])
        
        field_map = {f.field_id: f for f in enabled_fields}
        
        formatted_rows = []
        for row in rows:
            formatted_row = {}
            
            row_data = row.get("data", row)
            
            for field_id, field_value in row_data.items():
                if field_id in field_map:
                    field_name = field_map[field_id].field_name
                    formatted_row[field_name] = field_value
            
            if not formatted_row and "data" in row:
                for field_id, field_value in row["data"].items():
                    if field_id in field_map:
                        field_name = field_map[field_id].field_name
                        formatted_row[field_name] = field_value
            
            formatted_rows.append(formatted_row)
        
        return {
            "success": True,
            "data": {
                "fields": [{"field_id": f.field_id, "field_name": f.field_name, "data_type": f.data_type} for f in enabled_fields],
                "rows": formatted_rows
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询数据失败: {str(e)}")

@router.get("/snapshots")
async def get_all_snapshots(
    page: int = 1,
    page_size: int = 10,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    query = db.query(DataSnapshot)
    query = filter_by_user_permission(query, user, DataSnapshot.user_id)
    snapshots = query.order_by(DataSnapshot.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "data_flow_id": s.data_flow_id,
                "name": s.name,
                "worksheet_id": s.worksheet_id,
                "created_at": s.created_at.isoformat() if s.created_at else ""
            }
            for s in snapshots
        ]
    }

@router.get("/snapshots/count")
async def get_snapshots_count(
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(DataSnapshot)
    query = filter_by_user_permission(query, user, DataSnapshot.user_id)
    count = query.count()
    return {"success": True, "data": {"count": count}}

@router.get("/{dataflow_id}/snapshots")
async def get_snapshots(
    dataflow_id: int,
    page: int = 1,
    page_size: int = 10,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    offset = (page - 1) * page_size
    snapshots = db.query(DataSnapshot).filter(
        DataSnapshot.data_flow_id == dataflow_id
    ).order_by(DataSnapshot.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "worksheet_id": s.worksheet_id,
                "created_at": s.created_at.isoformat() if s.created_at else ""
            }
            for s in snapshots
        ]
    }

@router.post("/snapshots")
async def create_snapshot(
    snapshot: DataSnapshotCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    worksheet_id = None
    if snapshot.dataflow_id > 0:
        dataflow = db.query(DataFlow).filter(DataFlow.id == snapshot.dataflow_id).first()
        if not dataflow:
            raise HTTPException(status_code=404, detail="数据流不存在")
        check_resource_access(user, dataflow.user_id, "数据流")
        worksheet_id = dataflow.worksheet_id
    else:
        worksheet_id = f"aggregate_{int(datetime.now().timestamp())}"
    
    db_snapshot = DataSnapshot(
        user_id=user.id,
        data_flow_id=snapshot.dataflow_id,
        name=snapshot.name,
        worksheet_id=worksheet_id,
        fields=snapshot.fields,
        data=snapshot.data
    )
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    
    return {
        "success": True,
        "message": "快照保存成功",
        "data": {
            "id": db_snapshot.id,
            "name": db_snapshot.name
        }
    }

@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(
    snapshot_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    snapshot = db.query(DataSnapshot).filter(DataSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="快照不存在")
    check_resource_access(user, snapshot.user_id, "快照")
    
    try:
        fields = json.loads(snapshot.fields)
        data = json.loads(snapshot.data)
        
        if snapshot.data_flow_id > 0:
            saved_fields = db.query(FieldType).filter(
                FieldType.data_flow_id == snapshot.data_flow_id
            ).all()
            saved_fields_dict = {f.field_id: f for f in saved_fields}
            
            for field in fields:
                field_id = field.get("field_id")
                if field_id and field_id in saved_fields_dict:
                    field["data_type"] = saved_fields_dict[field_id].data_type
                    field["is_enabled"] = saved_fields_dict[field_id].is_enabled
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="数据解析失败")
    
    return {
        "success": True,
        "data": {
            "fields": fields,
            "rows": data
        }
    }

@router.delete("/snapshots/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    snapshot = db.query(DataSnapshot).filter(DataSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="快照不存在")
    check_resource_access(user, snapshot.user_id, "快照")
    
    db.delete(snapshot)
    db.commit()
    
    return {"success": True, "message": "快照删除成功"}

@router.post("/import/local")
async def import_local_file(
    file: UploadFile = File(...),
    dataflow_id: int = Form(...),
    name: Optional[str] = Form(None),
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
        if not dataflow:
            raise HTTPException(status_code=404, detail="数据流不存在")
        check_resource_access(user, dataflow.user_id, "数据流")
        
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        df = None
        if file_extension == 'csv':
            df = pd.read_csv(io.BytesIO(contents))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持CSV和Excel")
        
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        fields = []
        for col in df.columns:
            fields.append({
                "field_id": str(col),
                "field_name": str(col),
                "data_type": "string"
            })
        
        rows = df.to_dict('records')
        
        def clean_nan(obj):
            if isinstance(obj, float) and pd.isna(obj):
                return None
            elif isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            return obj
        
        rows = [clean_nan(row) for row in rows]
        
        snapshot_name = name if name else file.filename
        worksheet_id = f"local_{dataflow_id}_{int(datetime.now().timestamp())}"
        
        db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).delete()
        
        for field in fields:
            field_type = FieldType(
                data_flow_id=dataflow_id,
                worksheet_id=worksheet_id,
                field_id=field["field_id"],
                field_name=field["field_name"],
                data_type=field["data_type"],
                is_enabled="true"
            )
            db.add(field_type)
        
        db_snapshot = DataSnapshot(
            user_id=user.id,
            data_flow_id=dataflow_id,
            name=snapshot_name,
            worksheet_id=worksheet_id,
            fields=json.dumps(fields),
            data=json.dumps(rows)
        )
        db.add(db_snapshot)
        db.commit()
        db.refresh(db_snapshot)
        
        return {
            "success": True,
            "message": "导入成功",
            "data": {
                "id": db_snapshot.id,
                "name": db_snapshot.name,
                "fields": fields,
                "rows": rows[:100]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
