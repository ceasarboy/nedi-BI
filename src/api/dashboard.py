from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.models.config import Dashboard
import json

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])

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
async def get_dashboards(page: int = 1, page_size: int = 100, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    dashboards = db.query(Dashboard).order_by(Dashboard.created_at.desc()).offset(offset).limit(page_size).all()
    
    result = []
    for dashboard in dashboards:
        result.append({
            "id": dashboard.id,
            "name": dashboard.name,
            "data_snapshot_id": dashboard.data_snapshot_id,
            "chart_type": dashboard.chart_type,
            "config": json.loads(dashboard.config),
            "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
            "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
        })
    return result

@router.get("/count")
async def get_dashboards_count(db: Session = Depends(get_db)):
    count = db.query(Dashboard).count()
    return {"success": True, "data": {"count": count}}

@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return {
        "success": True,
        "data": {
            "id": dashboard.id,
            "name": dashboard.name,
            "data_snapshot_id": dashboard.data_snapshot_id,
            "chart_type": dashboard.chart_type,
            "config": json.loads(dashboard.config),
            "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
            "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
        }
    }

@router.post("")
async def create_dashboard(dashboard: DashboardCreate, db: Session = Depends(get_db)):
    db_dashboard = Dashboard(
        name=dashboard.name,
        data_snapshot_id=dashboard.data_snapshot_id,
        chart_type=dashboard.chart_type,
        config=json.dumps(dashboard.config)
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    return {
        "success": True,
        "data": {
            "id": db_dashboard.id,
            "name": db_dashboard.name,
            "data_snapshot_id": db_dashboard.data_snapshot_id,
            "chart_type": db_dashboard.chart_type,
            "config": json.loads(db_dashboard.config),
            "created_at": db_dashboard.created_at.isoformat() if db_dashboard.created_at else None,
            "updated_at": db_dashboard.updated_at.isoformat() if db_dashboard.updated_at else None
        }
    }

@router.put("/{dashboard_id}")
async def update_dashboard(dashboard_id: int, dashboard: DashboardUpdate, db: Session = Depends(get_db)):
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.name is not None:
        db_dashboard.name = dashboard.name
    if dashboard.data_snapshot_id is not None:
        db_dashboard.data_snapshot_id = dashboard.data_snapshot_id
    if dashboard.chart_type is not None:
        db_dashboard.chart_type = dashboard.chart_type
    if dashboard.config is not None:
        db_dashboard.config = json.dumps(dashboard.config)
    
    db.commit()
    db.refresh(db_dashboard)
    
    return {
        "success": True,
        "data": {
            "id": db_dashboard.id,
            "name": db_dashboard.name,
            "data_snapshot_id": db_dashboard.data_snapshot_id,
            "chart_type": db_dashboard.chart_type,
            "config": json.loads(db_dashboard.config),
            "created_at": db_dashboard.created_at.isoformat() if db_dashboard.created_at else None,
            "updated_at": db_dashboard.updated_at.isoformat() if db_dashboard.updated_at else None
        }
    }

@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db.delete(db_dashboard)
    db.commit()
    
    return {"success": True, "message": "Dashboard deleted successfully"}
