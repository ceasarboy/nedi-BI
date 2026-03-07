"""
图表智能推荐API接口
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from src.services.chart_recommendation import ChartRecommendationService
from src.api.auth import get_current_user_optional

router = APIRouter(prefix="/api/chart-recommend", tags=["chart-recommend"])

recommendation_service = ChartRecommendationService()


class AnalyzeRequest(BaseModel):
    data: List[Dict[str, Any]]
    fields: Optional[List[str]] = None


class RecommendRequest(BaseModel):
    data: List[Dict[str, Any]]
    fields: Optional[List[str]] = None


class FeedbackRequest(BaseModel):
    data_features: Dict[str, Any]
    recommended_chart: str
    chosen_chart: str
    accepted: bool


@router.post("/analyze")
async def analyze_data(
    request: AnalyzeRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    分析数据特征
    
    返回数据中各字段的类型、分布等特征信息
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="数据不能为空")
    
    try:
        result = recommendation_service.analyze_and_recommend(request.data, request.fields)
        return {
            "success": True,
            "features": result["features"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/recommend")
async def recommend_charts(
    request: RecommendRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    获取图表推荐
    
    根据数据特征推荐最适合的图表类型
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="数据不能为空")
    
    try:
        result = recommendation_service.analyze_and_recommend(request.data, request.fields)
        return {
            "success": True,
            "features": result["features"],
            "recommendations": result["recommendations"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user = Depends(get_current_user_optional)
):
    """
    提交推荐反馈
    
    记录用户是否采纳推荐，用于优化推荐算法
    """
    try:
        user_id = current_user.id if current_user else None
        
        from src.core.database import SessionLocal
        from src.models.feedback import AIFeedback
        
        db = SessionLocal()
        try:
            feedback = AIFeedback(
                user_id=user_id,
                feedback_type="chart_recommendation",
                context={
                    "data_features": request.data_features,
                    "recommended_chart": request.recommended_chart,
                    "chosen_chart": request.chosen_chart,
                    "accepted": request.accepted
                }
            )
            db.add(feedback)
            db.commit()
        finally:
            db.close()
        
        return {"success": True, "message": "反馈已记录"}
    except Exception as e:
        return {"success": False, "message": f"记录失败: {str(e)}"}


@router.get("/stats")
async def get_recommendation_stats(
    current_user = Depends(get_current_user_optional)
):
    """
    获取推荐统计
    
    返回推荐准确率等统计信息
    """
    try:
        from src.core.database import SessionLocal
        from src.models.feedback import AIFeedback
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            total = db.query(func.count(AIFeedback.id)).filter(
                AIFeedback.feedback_type == "chart_recommendation"
            ).scalar()
            
            accepted = db.query(func.count(AIFeedback.id)).filter(
                AIFeedback.feedback_type == "chart_recommendation",
                AIFeedback.context["accepted"].as_boolean() == True
            ).scalar()
            
            accuracy = (accepted / total * 100) if total > 0 else 0
            
            return {
                "success": True,
                "stats": {
                    "total_recommendations": total,
                    "accepted_count": accepted,
                    "accuracy_rate": round(accuracy, 2)
                }
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "success": True,
            "stats": {
                "total_recommendations": 0,
                "accepted_count": 0,
                "accuracy_rate": 0
            }
        }


@router.get("/chart-types")
async def get_chart_types():
    """
    获取支持的图表类型列表
    """
    try:
        chart_types = recommendation_service.get_chart_types()
        return {
            "success": True,
            "chart_types": chart_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
