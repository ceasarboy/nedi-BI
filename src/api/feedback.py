"""
反馈循环API接口
提供用户反馈收集、记忆层管理、效果评估等功能
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import json

from src.core.database import SessionLocal, Base, engine
from src.models.feedback import AIFeedback, FeedbackMemory, FeedbackAnalytics
from src.api.auth import get_current_user_optional
from src.services.memory_service import MemoryService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

Base.metadata.create_all(bind=engine)


class FeedbackCreate(BaseModel):
    session_id: str = Field(..., description="会话ID")
    message_id: str = Field(..., description="消息ID")
    rating: int = Field(..., ge=-1, le=1, description="评分: 1=满意, -1=不满意, 0=中性")
    user_query: str = Field(..., description="用户问题")
    ai_response: str = Field(..., description="AI回复")
    user_correction: Optional[str] = Field(None, description="用户修正内容")
    correction_type: Optional[str] = Field(None, description="修正类型")
    tool_calls: Optional[List[Dict]] = Field(None, description="工具调用记录")
    chart_generated: bool = Field(False, description="是否生成图表")
    context: Optional[Dict] = Field(None, description="上下文信息")


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: int
    message: str


class MemoryCreate(BaseModel):
    query_pattern: str
    correct_response: str
    memory_type: str = "correction"
    entity_mentions: Optional[Dict] = None
    intent_category: Optional[str] = None


class FeedbackStats(BaseModel):
    total_feedbacks: int
    positive_count: int
    negative_count: int
    satisfaction_rate: float
    corrections_count: int
    charts_generated: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    feedback_type = "positive" if feedback.rating > 0 else ("negative" if feedback.rating < 0 else "neutral")
    
    user_id = current_user.id if current_user else None
    
    db_feedback = AIFeedback(
        session_id=feedback.session_id,
        message_id=feedback.message_id,
        user_id=user_id,
        rating=feedback.rating,
        feedback_type=feedback_type,
        user_query=feedback.user_query,
        ai_response=feedback.ai_response,
        user_correction=feedback.user_correction,
        correction_type=feedback.correction_type,
        tool_calls=feedback.tool_calls,
        chart_generated=feedback.chart_generated,
        context=feedback.context
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    memory_service = MemoryService(db)
    
    if feedback.rating > 0:
        memory_service.save_success_case(
            user_id=user_id,
            query=feedback.user_query,
            response=feedback.ai_response,
            tool_calls=feedback.tool_calls,
            chart_generated=feedback.chart_generated
        )
        memory_service.extract_preferences_from_positive_feedback(
            user_id=user_id,
            query=feedback.user_query,
            response=feedback.ai_response
        )
        print(f"[Feedback] 已创建成功案例: {feedback.user_query[:50]}...")
    
    elif feedback.rating < 0:
        if feedback.user_correction:
            memory_service.save_failure_lesson(
                user_id=user_id,
                query=feedback.user_query,
                failed_response=feedback.ai_response,
                user_correction=feedback.user_correction,
                failure_type=feedback.correction_type or "general"
            )
            print(f"[Feedback] 已创建失败教训: {feedback.user_query[:50]}...")
        
        _create_memory_from_correction(db, db_feedback)
    
    _update_daily_analytics(db, feedback)
    
    return FeedbackResponse(
        success=True,
        feedback_id=db_feedback.id,
        message="反馈提交成功，感谢您的评价！"
    )


def _create_memory_from_correction(db: Session, feedback: AIFeedback):
    query_pattern = feedback.user_query[:255] if len(feedback.user_query) > 255 else feedback.user_query
    
    memory = FeedbackMemory(
        feedback_id=feedback.id,
        memory_type="correction",
        query_pattern=query_pattern,
        correct_response=feedback.user_correction,
        intent_category=feedback.correction_type
    )
    
    db.add(memory)
    db.commit()
    print(f"[Feedback] 已创建记忆: {query_pattern[:50]}...")


def _update_daily_analytics(db: Session, feedback: FeedbackCreate):
    today = datetime.utcnow().date()
    
    analytics = db.query(FeedbackAnalytics).filter(
        func.date(FeedbackAnalytics.date) == today
    ).first()
    
    if not analytics:
        analytics = FeedbackAnalytics(
            date=today,
            total_feedbacks=0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            corrections_count=0,
            charts_generated=0,
            charts_positive=0
        )
        db.add(analytics)
    
    analytics.total_feedbacks = (analytics.total_feedbacks or 0) + 1
    
    if feedback.rating > 0:
        analytics.positive_count = (analytics.positive_count or 0) + 1
    elif feedback.rating < 0:
        analytics.negative_count = (analytics.negative_count or 0) + 1
    else:
        analytics.neutral_count = (analytics.neutral_count or 0) + 1
    
    if analytics.total_feedbacks > 0:
        analytics.satisfaction_rate = (analytics.positive_count or 0) / analytics.total_feedbacks
    
    if feedback.user_correction:
        analytics.corrections_count = (analytics.corrections_count or 0) + 1
    
    if feedback.chart_generated:
        analytics.charts_generated = (analytics.charts_generated or 0) + 1
        if feedback.rating > 0:
            analytics.charts_positive = (analytics.charts_positive or 0) + 1
    
    db.commit()


@router.get("/memories", response_model=List[Dict])
async def get_memories(
    limit: int = 20,
    memory_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FeedbackMemory).filter(FeedbackMemory.active == True)
    
    if memory_type:
        query = query.filter(FeedbackMemory.memory_type == memory_type)
    
    memories = query.order_by(
        FeedbackMemory.importance_score.desc(),
        FeedbackMemory.usage_count.desc()
    ).limit(limit).all()
    
    return [m.to_dict() for m in memories]


@router.post("/memories", response_model=Dict)
async def create_memory(
    memory: MemoryCreate,
    db: Session = Depends(get_db)
):
    db_memory = FeedbackMemory(
        memory_type=memory.memory_type,
        query_pattern=memory.query_pattern,
        correct_response=memory.correct_response,
        entity_mentions=memory.entity_mentions,
        intent_category=memory.intent_category
    )
    
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    
    return db_memory.to_dict()


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    result = db.query(
        func.sum(FeedbackAnalytics.total_feedbacks).label("total"),
        func.sum(FeedbackAnalytics.positive_count).label("positive"),
        func.sum(FeedbackAnalytics.negative_count).label("negative"),
        func.sum(FeedbackAnalytics.corrections_count).label("corrections"),
        func.sum(FeedbackAnalytics.charts_generated).label("charts")
    ).filter(FeedbackAnalytics.date >= start_date).first()
    
    total = result.total or 0
    positive = result.positive or 0
    negative = result.negative or 0
    
    satisfaction_rate = positive / total if total > 0 else 0
    
    return FeedbackStats(
        total_feedbacks=total,
        positive_count=positive,
        negative_count=negative,
        satisfaction_rate=round(satisfaction_rate * 100, 1),
        corrections_count=result.corrections or 0,
        charts_generated=result.charts or 0
    )


@router.get("/history")
async def get_feedback_history(
    limit: int = 20,
    rating: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AIFeedback)
    
    if rating is not None:
        query = query.filter(AIFeedback.rating == rating)
    
    feedbacks = query.order_by(AIFeedback.created_at.desc()).limit(limit).all()
    
    return [f.to_dict() for f in feedbacks]


@router.get("/context/{session_id}")
async def get_session_context(
    session_id: str,
    db: Session = Depends(get_db)
):
    memories = db.query(FeedbackMemory).filter(
        FeedbackMemory.active == True
    ).order_by(
        FeedbackMemory.importance_score.desc()
    ).limit(10).all()
    
    context_parts = []
    for m in memories:
        pattern = m.query_pattern[:50] if m.query_pattern else ""
        response = m.correct_response[:100] if m.correct_response else ""
        context_parts.append(f'- 当用户问类似"{pattern}"时，注意：{response}')
    
    return {
        "session_id": session_id,
        "memory_context": "\n".join(context_parts) if context_parts else None,
        "memory_count": len(memories)
    }


@router.post("/optimize")
async def optimize_memories(db: Session = Depends(get_db)):
    memories = db.query(FeedbackMemory).filter(
        FeedbackMemory.active == True
    ).all()
    
    optimized_count = 0
    
    for memory in memories:
        related_feedbacks = db.query(AIFeedback).filter(
            AIFeedback.user_query.contains(memory.query_pattern[:50])
        ).all()
        
        if related_feedbacks:
            positive = sum(1 for f in related_feedbacks if f.rating > 0)
            total = len(related_feedbacks)
            
            memory.usage_count = total
            memory.success_rate = positive / total if total > 0 else 0
            
            memory.importance_score = (memory.usage_count * 0.3 + memory.success_rate * 0.7)
            
            if memory.success_rate < 0.3 and memory.usage_count > 5:
                memory.active = False
            
            optimized_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "optimized_count": optimized_count,
        "message": f"已优化 {optimized_count} 条记忆"
    }


class PreferenceCreate(BaseModel):
    preference_type: str
    preference_key: str
    preference_value: str
    confidence: float = 0.8
    source: str = "manual"


@router.post("/memory/preferences")
async def add_user_preference(
    preference: PreferenceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """添加用户偏好"""
    user_id = current_user.id if current_user else None
    memory_service = MemoryService(db)
    
    pref = memory_service.save_user_preference(
        user_id=user_id,
        preference_type=preference.preference_type,
        preference_key=preference.preference_key,
        preference_value=preference.preference_value,
        source=preference.source
    )
    
    if preference.confidence != 0.8:
        pref.confidence = preference.confidence
        db.commit()
    
    return pref.to_dict()


@router.get("/memory/preferences")
async def get_user_preferences(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """获取用户偏好列表"""
    user_id = current_user.id if current_user else None
    memory_service = MemoryService(db)
    preferences = memory_service.get_user_preferences(user_id, limit)
    return [p.to_dict() for p in preferences]


@router.get("/memory/success-cases")
async def get_success_cases(
    query: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """获取成功案例列表"""
    user_id = current_user.id if current_user else None
    memory_service = MemoryService(db)
    
    if query:
        cases = memory_service.get_success_cases(query, user_id, limit)
    else:
        from src.models.memory import SuccessCase
        cases = db.query(SuccessCase).filter(
            SuccessCase.active == True
        ).order_by(SuccessCase.created_at.desc()).limit(limit).all()
    
    return [c.to_dict() for c in cases]


@router.get("/memory/failure-lessons")
async def get_failure_lessons(
    query: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """获取失败教训列表"""
    user_id = current_user.id if current_user else None
    memory_service = MemoryService(db)
    
    if query:
        lessons = memory_service.get_failure_lessons(query, user_id, limit)
    else:
        from src.models.memory import FailureLesson
        lessons = db.query(FailureLesson).filter(
            FailureLesson.active == True
        ).order_by(FailureLesson.created_at.desc()).limit(limit).all()
    
    return [l.to_dict() for l in lessons]


@router.get("/memory/stats")
async def get_memory_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """获取记忆系统统计信息"""
    from src.models.memory import UserPreference, SuccessCase, FailureLesson
    
    user_id = current_user.id if current_user else None
    
    pref_query = db.query(UserPreference).filter(UserPreference.active == True)
    success_query = db.query(SuccessCase).filter(SuccessCase.active == True)
    failure_query = db.query(FailureLesson).filter(FailureLesson.active == True)
    
    if user_id:
        pref_query = pref_query.filter(UserPreference.user_id == user_id)
        success_query = success_query.filter(SuccessCase.user_id == user_id)
        failure_query = failure_query.filter(FailureLesson.user_id == user_id)
    
    return {
        "preferences_count": pref_query.count(),
        "success_cases_count": success_query.count(),
        "failure_lessons_count": failure_query.count(),
        "user_id": user_id
    }


@router.delete("/memory/preferences/{preference_id}")
async def delete_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """删除用户偏好"""
    from src.models.memory import UserPreference
    
    user_id = current_user.id if current_user else None
    
    preference = db.query(UserPreference).filter(
        UserPreference.id == preference_id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="偏好不存在")
    
    if user_id and preference.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此偏好")
    
    preference.active = False
    db.commit()
    
    return {"success": True, "message": "偏好已删除"}


@router.delete("/memory/success-cases/{case_id}")
async def delete_success_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """删除成功案例"""
    from src.models.memory import SuccessCase
    
    user_id = current_user.id if current_user else None
    
    case = db.query(SuccessCase).filter(SuccessCase.id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    if user_id and case.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此案例")
    
    case.active = False
    db.commit()
    
    return {"success": True, "message": "案例已删除"}


@router.delete("/memory/failure-lessons/{lesson_id}")
async def delete_failure_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """删除失败教训"""
    from src.models.memory import FailureLesson
    
    user_id = current_user.id if current_user else None
    
    lesson = db.query(FailureLesson).filter(FailureLesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="教训不存在")
    
    if user_id and lesson.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此教训")
    
    lesson.active = False
    db.commit()
    
    return {"success": True, "message": "教训已删除"}
