from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import json

from src.mcp.service import mcp_service
from src.mcp.tools import register_all_tools

register_all_tools(mcp_service)

router = APIRouter(prefix="", tags=["mcp"])

class McpToolRequest(BaseModel):
    server_url: str
    name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None

@router.post("/v1/tool/list")
async def list_mcp_tools(request: McpToolRequest):
    """MCP工具列表接口 - JoyAgent需要调用此接口获取工具列表"""
    tools = mcp_service.list_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in tools
        ]
    }

@router.post("/v1/tool/call")
async def call_mcp_tool(request: McpToolRequest):
    """MCP工具调用接口 - JoyAgent需要调用此接口执行工具"""
    if not request.name:
        raise HTTPException(status_code=400, detail="Tool name is required")
    
    arguments = request.arguments or {}
    result = mcp_service.execute_tool(request.name, arguments)
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Tool execution failed"))
    
    return {"result": result}

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
