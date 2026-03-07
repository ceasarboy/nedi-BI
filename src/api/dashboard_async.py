from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from pydantic import BaseModel
from src.core.database_async import get_db
from src.models.config_sqlmodel import Dashboard
from src.core.permissions_async import get_current_user, check_resource_access, filter_by_user_permission
import json
from datetime import datetime

router = APIRouter(prefix="/api/async/dashboards", tags=["async-dashboards"])

class DashboardCreate(BaseModel):
    name: str
    data_snapshot_id: Optional[int] = None
    chart_type: str = "line"
    config: dict

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    data_snapshot_id: Optional[int] = None
    chart_type: Optional[str] = None
    config: Optional[dict] = None

@router.get("")
async def get_dashboards(
    page: int = 1,
    page_size: int = 100,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    query = select(Dashboard)
    query = filter_by_user_permission(query, user, Dashboard.user_id)
    query = query.order_by(Dashboard.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    dashboards = result.scalars().all()
    
    result_list = []
    for dashboard in dashboards:
        result_list.append({
            "id": dashboard.id,
            "name": dashboard.name,
            "data_snapshot_id": dashboard.data_snapshot_id,
            "chart_type": dashboard.chart_type,
            "config": json.loads(dashboard.config),
            "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
            "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
        })
    return result_list

@router.get("/count")
async def get_dashboards_count(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(Dashboard)
    query = filter_by_user_permission(query, user, Dashboard.user_id)
    result = await db.execute(query)
    dashboards = result.scalars().all()
    count = len(dashboards)
    return {"success": True, "data": {"count": count}}

@router.get("/{dashboard_id}")
async def get_dashboard(
    dashboard_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(Dashboard).where(Dashboard.id == dashboard_id)
    result = await db.execute(query)
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="看板不存在")
    
    check_resource_access(user, dashboard.user_id, "看板")
    
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "data_snapshot_id": dashboard.data_snapshot_id,
        "chart_type": dashboard.chart_type,
        "config": json.loads(dashboard.config),
        "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
        "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
    }

@router.post("")
async def create_dashboard(
    dashboard: DashboardCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    db_dashboard = Dashboard(
        user_id=user.id,
        name=dashboard.name,
        data_snapshot_id=dashboard.data_snapshot_id,
        chart_type=dashboard.chart_type,
        config=json.dumps(dashboard.config)
    )
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)
    
    return {
        "id": db_dashboard.id,
        "name": db_dashboard.name,
        "data_snapshot_id": db_dashboard.data_snapshot_id,
        "chart_type": db_dashboard.chart_type,
        "config": json.loads(db_dashboard.config),
        "created_at": db_dashboard.created_at.isoformat() if db_dashboard.created_at else None
    }

@router.put("/{dashboard_id}")
async def update_dashboard(
    dashboard_id: int,
    dashboard: DashboardUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(Dashboard).where(Dashboard.id == dashboard_id)
    result = await db.execute(query)
    db_dashboard = result.scalar_one_or_none()
    
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="看板不存在")
    
    check_resource_access(user, db_dashboard.user_id, "看板")
    
    if dashboard.name is not None:
        db_dashboard.name = dashboard.name
    if dashboard.data_snapshot_id is not None:
        db_dashboard.data_snapshot_id = dashboard.data_snapshot_id
    if dashboard.chart_type is not None:
        db_dashboard.chart_type = dashboard.chart_type
    if dashboard.config is not None:
        db_dashboard.config = json.dumps(dashboard.config)
    
    db_dashboard.updated_at = datetime.now()
    await db.commit()
    await db.refresh(db_dashboard)
    
    return {
        "id": db_dashboard.id,
        "name": db_dashboard.name,
        "data_snapshot_id": db_dashboard.data_snapshot_id,
        "chart_type": db_dashboard.chart_type,
        "config": json.loads(db_dashboard.config),
        "updated_at": db_dashboard.updated_at.isoformat() if db_dashboard.updated_at else None
    }

@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: int,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    query = select(Dashboard).where(Dashboard.id == dashboard_id)
    result = await db.execute(query)
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="看板不存在")
    
    check_resource_access(user, dashboard.user_id, "看板")
    
    await db.delete(dashboard)
    await db.commit()
    
    return {"success": True, "message": "看板已删除"}
