from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
import json
from datetime import datetime

from src.core.database import get_db
from src.models.config import DataFlow, FieldType, DataSnapshot
from src.services.mingdao import MingDaoService
from src.core.permissions import get_current_user, check_resource_access, filter_by_user_permission

router = APIRouter(prefix="/api/dataflows", tags=["dataflows"])

class DataFlowCreate(BaseModel):
    name: str
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None
    type: str = "mingdao"

class DataFlowUpdate(BaseModel):
    name: Optional[str] = None
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None

class DataFlowResponse(BaseModel):
    id: int
    name: str
    appkey: Optional[str] = None
    sign: Optional[str] = None
    worksheet_id: Optional[str] = None
    type: str = "mingdao"

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
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    query = db.query(DataFlow)
    query = filter_by_user_permission(query, user, DataFlow.user_id)
    dataflows = query.order_by(DataFlow.created_at.desc()).offset(offset).limit(page_size).all()
    return dataflows

@router.get("/count")
async def get_dataflows_count(
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(DataFlow)
    query = filter_by_user_permission(query, user, DataFlow.user_id)
    count = query.count()
    return {"success": True, "data": {"count": count}}

@router.get("/{dataflow_id}", response_model=DataFlowResponse)
async def get_dataflow(
    dataflow_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    return dataflow

@router.post("", response_model=DataFlowResponse)
async def create_dataflow(
    dataflow: DataFlowCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    db_dataflow = DataFlow(
        user_id=user.id,
        name=dataflow.name,
        type=dataflow.type,
        appkey=dataflow.appkey,
        sign=dataflow.sign,
        worksheet_id=dataflow.worksheet_id
    )
    db.add(db_dataflow)
    db.commit()
    db.refresh(db_dataflow)
    return db_dataflow

@router.put("/{dataflow_id}", response_model=DataFlowResponse)
async def update_dataflow(
    dataflow_id: int,
    dataflow_update: DataFlowUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    update_data = dataflow_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dataflow, key, value)
    
    db.commit()
    db.refresh(dataflow)
    return dataflow

@router.delete("/{dataflow_id}")
async def delete_dataflow(
    dataflow_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    db.delete(dataflow)
    db.commit()
    return {"success": True, "message": "删除成功"}

@router.post("/{dataflow_id}/test")
async def test_dataflow_connection(
    dataflow_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    service = MingDaoService(dataflow.appkey, dataflow.sign)
    success = service.test_connection()
    
    if success:
        return {"success": True, "message": "连接成功"}
    else:
        raise HTTPException(status_code=400, detail="连接失败，请检查配置")

@router.get("/{dataflow_id}/fields")
async def get_dataflow_fields(
    dataflow_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    saved_fields = db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).all()
    saved_fields_dict = {f.field_id: f for f in saved_fields}
    
    if dataflow.type == "local":
        response_fields = []
        for field in saved_fields:
            response_fields.append({
                "field_id": field.field_id,
                "field_name": field.field_name,
                "data_type": field.data_type,
                "is_enabled": field.is_enabled
            })
        return {"success": True, "data": response_fields}
    else:
        service = MingDaoService(dataflow.appkey, dataflow.sign)
        result = service.get_fields(dataflow.worksheet_id)
        
        if not result["success"]:
            error_msg = result.get("error_msg", "获取字段失败")
            raise HTTPException(status_code=400, detail=f"获取字段失败: {error_msg}")
        
        fields_from_api = result["data"]["data"]
        
        response_fields = []
        for field in fields_from_api:
            field_id = field.get("fieldId", "") or field.get("id", "")
            field_name = field.get("name", "")
            data_type = field.get("type", "text")
            
            is_enabled = "true"
            if field_id in saved_fields_dict:
                is_enabled = saved_fields_dict[field_id].is_enabled
                data_type = saved_fields_dict[field_id].data_type
            
            response_fields.append({
                "field_id": field_id,
                "field_name": field_name,
                "data_type": data_type,
                "is_enabled": is_enabled
            })
        
        return {"success": True, "data": response_fields}

@router.post("/{dataflow_id}/fields")
async def save_dataflow_fields(
    dataflow_id: int,
    field_config: FieldConfigSave,
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    dataflow = db.query(DataFlow).filter(DataFlow.id == dataflow_id).first()
    if not dataflow:
        raise HTTPException(status_code=404, detail="数据流不存在")
    check_resource_access(user, dataflow.user_id, "数据流")
    
    db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).delete()
    
    for field in field_config.fields:
        field_type = FieldType(
            data_flow_id=dataflow_id,
            worksheet_id=dataflow.worksheet_id,
            field_id=field.field_id,
            field_name=field.field_name,
            data_type=field.data_type,
            is_enabled=field.is_enabled
        )
        db.add(field_type)
    
    db.commit()
    return {"success": True, "message": "字段配置保存成功"}


@router.post("/{dataflow_id}/import-fields")
async def import_fields_from_file(
    dataflow_id: int,
    file: UploadFile = File(...),
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
                "data_type": "string",
                "is_enabled": "true"
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
        
        worksheet_id = f"local_{dataflow_id}_{int(datetime.now().timestamp())}"
        
        db.query(FieldType).filter(FieldType.data_flow_id == dataflow_id).delete()
        
        for field in fields:
            field_type = FieldType(
                data_flow_id=dataflow_id,
                worksheet_id=worksheet_id,
                field_id=field["field_id"],
                field_name=field["field_name"],
                data_type=field["data_type"],
                is_enabled=field["is_enabled"]
            )
            db.add(field_type)
        
        db.query(DataSnapshot).filter(DataSnapshot.data_flow_id == dataflow_id).delete()
        
        snapshot_name = file.filename.replace(f'.{file_extension}', '')
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
        
        return {
            "success": True,
            "data": fields
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"导入字段失败: {str(e)}")
