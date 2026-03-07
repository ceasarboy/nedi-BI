"""
AI对话API接口
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio

from src.ai.agent import PBBIAgent
from src.ai.llm_client import LLMConfig
from src.api.auth import get_current_user_optional

router = APIRouter(prefix="/api/ai", tags=["ai"])

agent_instances: Dict[str, PBBIAgent] = {}

def get_agent(session_id: Optional[str] = None, user_id: Optional[int] = None) -> PBBIAgent:
    if session_id and session_id in agent_instances:
        existing_agent = agent_instances[session_id]
        existing_agent.llm_client._load_config()
        existing_agent.set_user_id(user_id)
        return existing_agent
    
    agent = PBBIAgent(session_id=session_id, user_id=user_id)
    
    if session_id:
        agent_instances[session_id] = agent
    
    return agent

def load_session_history(agent: PBBIAgent, session_id: str):
    """从数据库加载会话历史"""
    try:
        from src.core.database import SessionLocal
        from src.models.conversation import ConversationMessage
        
        db = SessionLocal()
        try:
            messages = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session_id
            ).order_by(ConversationMessage.created_at).all()
            
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            if history:
                agent.load_history(history)
        finally:
            db.close()
    except Exception as e:
        print(f"Load history error: {e}")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    clear_history: bool = False

class ConfigRequest(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None

class ConfigResponse(BaseModel):
    api_key: str
    base_url: str
    model: str

@router.post("/chat")
async def chat(request: ChatRequest, current_user = Depends(get_current_user_optional)):
    user_id = current_user.id if current_user else None
    agent = get_agent(request.session_id, user_id)
    
    if request.session_id:
        load_session_history(agent, request.session_id)
    
    if request.clear_history:
        agent.clear_history()
    
    async def generate():
        try:
            async for event in agent.chat(request.message):
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_data}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_event = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {error_event}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/history")
async def get_history():
    agent = get_agent()
    return {"history": agent.get_history()}

@router.post("/clear")
async def clear_history():
    agent = get_agent()
    agent.clear_history()
    return {"success": True, "message": "对话历史已清除"}

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    agent = get_agent()
    config = agent.llm_client.config
    return ConfigResponse(
        api_key=config.api_key[:8] + "..." if config.api_key else "",
        base_url=config.base_url,
        model=config.model
    )

@router.post("/config")
async def set_config(request: ConfigRequest):
    global agent_instance
    
    config = LLMConfig()
    if request.api_key:
        config.api_key = request.api_key
    if request.base_url:
        config.base_url = request.base_url
    if request.model:
        config.model = request.model
    
    agent_instance = PBBIAgent(config)
    
    return {"success": True, "message": "配置已更新"}

@router.get("/tools")
async def list_tools():
    agent = get_agent()
    return {"tools": agent.tool_executor.list_available_tools()}
