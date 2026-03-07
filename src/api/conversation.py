"""
对话会话API接口
支持对话列表、新建对话、关闭对话、加载历史对话等功能
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json
import uuid
import os

from src.core.database import SessionLocal, Base, engine
from src.api.auth import get_current_user_optional
from src.models.conversation import ConversationSession, ConversationMessage

router = APIRouter(prefix="/api/conversation", tags=["conversation"])

ARCHIVE_DIR = "archives"

Base.metadata.create_all(bind=engine)


class CreateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, description="对话标题")


class AddMessageRequest(BaseModel):
    role: str = Field(..., description="角色: user/assistant")
    content: str = Field(..., description="消息内容")
    tool_calls: Optional[List[Dict]] = Field(None, description="工具调用记录")
    tokens: int = Field(0, description="token数量")


class SessionResponse(BaseModel):
    id: int
    session_id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str
    is_active: bool


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    feedback_rating: Optional[int] = None
    created_at: str


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]
    context_info: Dict


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    
    session_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    title = request.title if request and request.title else f"对话 {datetime.now().strftime('%m-%d %H:%M')}"
    
    session = ConversationSession(
        session_id=session_id,
        user_id=user_id,
        title=title,
        is_active=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        session_id=session.session_id,
        title=session.title,
        message_count=0,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        is_active=session.is_active
    )


@router.get("/list", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    
    query = db.query(ConversationSession)
    if user_id:
        query = query.filter(ConversationSession.user_id == user_id)
    
    sessions = query.order_by(desc(ConversationSession.updated_at)).limit(limit).all()
    
    result = []
    for s in sessions:
        msg_count = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == s.session_id
        ).count()
        
        result.append(SessionResponse(
            id=s.id,
            session_id=s.session_id,
            title=s.title,
            message_count=msg_count,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
            is_active=s.is_active
        ))
    
    return result


@router.get("/search")
async def search_conversations(
    q: str = "",
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    if not q or len(q.strip()) < 2:
        return []
    
    user_id = current_user.id if current_user else None
    
    search_term = f"%{q.strip()}%"
    
    message_query = db.query(ConversationMessage).filter(
        ConversationMessage.content.ilike(search_term)
    )
    
    matching_messages = message_query.limit(100).all()
    
    session_ids = list(set([m.session_id for m in matching_messages]))
    
    if not session_ids:
        return []
    
    session_query = db.query(ConversationSession).filter(
        ConversationSession.session_id.in_(session_ids)
    )
    
    if user_id:
        session_query = session_query.filter(ConversationSession.user_id == user_id)
    
    sessions = session_query.order_by(desc(ConversationSession.updated_at)).limit(limit).all()
    
    result = []
    for s in sessions:
        matching_msgs = [m for m in matching_messages if m.session_id == s.session_id]
        highlights = []
        for m in matching_msgs[:3]:
            content = m.content[:200] + "..." if len(m.content) > 200 else m.content
            highlights.append({
                "role": m.role,
                "content": content
            })
        
        result.append({
            "session_id": s.session_id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "match_count": len([m for m in matching_messages if m.session_id == s.session_id]),
            "highlights": highlights
        })
    
    return result


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at).all()
    
    total_tokens = sum(m.tokens or 0 for m in messages)
    context_usage = {
        "total_tokens": total_tokens,
        "limit": session.context_limit,
        "usage_percent": round(total_tokens / session.context_limit * 100, 1) if session.context_limit > 0 else 0,
        "is_near_limit": total_tokens > session.context_limit * 0.8
    }
    
    return SessionDetailResponse(
        session=SessionResponse(
            id=session.id,
            session_id=session.session_id,
            title=session.title,
            message_count=len(messages),
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            is_active=session.is_active
        ),
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                feedback_rating=m.feedback_rating,
                created_at=m.created_at.isoformat()
            ) for m in messages
        ],
        context_info=context_usage
    )


@router.post("/{session_id}/archive")
async def archive_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    session.is_archived = True
    session.is_active = False
    db.commit()
    
    return {"success": True, "message": "对话已归档"}


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).delete()
    
    db.delete(session)
    db.commit()
    
    return {"success": True, "message": "对话已删除"}


@router.post("/{session_id}/messages")
async def add_message(
    session_id: str,
    request: AddMessageRequest,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    message = ConversationMessage(
        session_id=session_id,
        role=request.role,
        content=request.content,
        tool_calls=request.tool_calls,
        tokens=request.tokens
    )
    
    db.add(message)
    
    session.message_count = (session.message_count or 0) + 1
    session.context_tokens = (session.context_tokens or 0) + request.tokens
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    context_warning = None
    if session.context_tokens > session.context_limit * 0.8:
        context_warning = {
            "level": "warning" if session.context_tokens < session.context_limit else "error",
            "message": f"上下文已使用 {round(session.context_tokens / session.context_limit * 100, 1)}%，即将达到限制"
        }
    
    return {
        "success": True,
        "message_id": message.id,
        "context_warning": context_warning
    }


@router.post("/{session_id}/feedback")
async def rate_message(
    session_id: str,
    message_id: int,
    rating: int,
    db: Session = Depends(get_db)
):
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == message_id,
        ConversationMessage.session_id == session_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    message.feedback_rating = rating
    db.commit()
    
    return {"success": True}


@router.get("/active/default")
async def get_default_active_session(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    
    query = db.query(ConversationSession).filter(
        ConversationSession.is_active == True,
        ConversationSession.is_archived == False
    )
    
    if user_id:
        query = query.filter(ConversationSession.user_id == user_id)
    
    session = query.order_by(desc(ConversationSession.updated_at)).first()
    
    if not session:
        return {"has_active_session": False}
    
    return {
        "has_active_session": True,
        "session_id": session.session_id,
        "title": session.title
    }


@router.get("/{session_id}/export")
async def export_session_markdown(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at).all()
    
    lines = [
        f"# {session.title}",
        "",
        f"> 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 会话ID: {session_id}",
        f"> 消息数量: {len(messages)}",
        "",
        "---",
        ""
    ]
    
    for msg in messages:
        timestamp = msg.created_at.strftime('%H:%M:%S') if msg.created_at else ""
        if msg.role == 'user':
            lines.append(f"## 👤 用户 ({timestamp})")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
        else:
            lines.append(f"## 🤖 AI助手 ({timestamp})")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
            
            if msg.feedback_rating:
                rating_emoji = "👍" if msg.feedback_rating > 0 else "👎"
                lines.append(f"> 反馈: {rating_emoji}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    markdown_content = "\n".join(lines)
    
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    
    safe_title = "".join(c for c in session.title if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title:
        safe_title = "conversation"
    
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(ARCHIVE_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "content": markdown_content
    }


@router.get("/{session_id}/download")
async def download_session_markdown(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(ConversationSession).filter(
        ConversationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at).all()
    
    lines = [
        f"# {session.title}",
        "",
        f"> 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 会话ID: {session_id}",
        f"> 消息数量: {len(messages)}",
        "",
        "---",
        ""
    ]
    
    for msg in messages:
        timestamp = msg.created_at.strftime('%H:%M:%S') if msg.created_at else ""
        if msg.role == 'user':
            lines.append(f"## 👤 用户 ({timestamp})")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
        else:
            lines.append(f"## 🤖 AI助手 ({timestamp})")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
            
            if msg.feedback_rating:
                rating_emoji = "👍" if msg.feedback_rating > 0 else "👎"
                lines.append(f"> 反馈: {rating_emoji}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    markdown_content = "\n".join(lines)
    
    safe_title = "".join(c for c in session.title if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title:
        safe_title = "conversation"
    
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    from fastapi.responses import Response
    
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
