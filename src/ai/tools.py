"""
MCP工具执行器 - 执行PB-BI的MCP工具
"""

from typing import Dict, Any, Optional
from src.mcp.service import mcp_service
from src.mcp.tools import register_all_tools

register_all_tools(mcp_service)

class MCPToolExecutor:
    def __init__(self):
        self._tools_registered = False
        self._register_tools()
    
    def _register_tools(self):
        if not self._tools_registered:
            register_all_tools(mcp_service)
            self._tools_registered = True
    
    def list_available_tools(self) -> list:
        tools = mcp_service.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in tools
        ]
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = mcp_service.execute_tool(tool_name, arguments)
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "tool": tool_name
            }
        
        return {
            "success": True,
            "data": result.get("data"),
            "tool": tool_name
        }
    
    async def execute_multiple(self, tool_calls: list) -> list:
        results = []
        for call in tool_calls:
            tool_name = call.get("name") or call.get("function", {}).get("name")
            arguments = call.get("arguments") or call.get("function", {}).get("arguments", {})
            
            if isinstance(arguments, str):
                import json
                try:
                    arguments = json.loads(arguments)
                except:
                    arguments = {}
            
            result = await self.execute(tool_name, arguments)
            results.append(result)
        
        return results
