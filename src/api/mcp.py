from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from src.mcp.service import mcp_service, MCPService
from src.mcp.tools import register_all_tools, GetDataFlowsTool, QueryDataTool
from src.mcp.database_mcp import register_database_tools
from src.mcp.mingdao_mcp import register_mingdao_tools
from src.mcp.localfile_mcp import register_localfile_tools
from src.mcp.dataflow_mcp import register_dataflow_tools
from src.mcp.analysis_mcp import register_analysis_tools
from src.mcp.dashboard_mcp import register_dashboard_tools
from src.mcp.chart_mcp import register_chart_tools

register_all_tools(mcp_service)
register_database_tools(mcp_service)
register_mingdao_tools(mcp_service)
register_localfile_tools(mcp_service)
register_dataflow_tools(mcp_service)
register_analysis_tools(mcp_service)
register_dashboard_tools(mcp_service)
register_chart_tools(mcp_service)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

class ToolExecuteRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = {}

class ToolListResponse(BaseModel):
    tools: List[Dict[str, Any]]
    count: int

@router.get("/tools", response_model=ToolListResponse)
async def list_tools():
    tools = mcp_service.list_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in tools
        ],
        "count": len(tools)
    }

@router.post("/execute")
async def execute_tool(request: ToolExecuteRequest):
    result = mcp_service.execute_tool(request.tool_name, request.params)
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    tool = mcp_service.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tools_count": len(mcp_service.list_tools())
    }
