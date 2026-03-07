from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import json

class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

    class Config:
        frozen = True

class MCPService:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}

    def register_tool(self, tool: MCPTool, handler: Callable = None):
        self.tools[tool.name] = tool
        if handler:
            self.tool_handlers[tool.name] = handler

    def register_handler(self, name: str, handler: Callable):
        self.tool_handlers[name] = handler

    def get_tool(self, name: str) -> Optional[MCPTool]:
        return self.tools.get(name)

    def list_tools(self) -> List[MCPTool]:
        return list(self.tools.values())

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool {name} not found"}

        handler = self.tool_handlers.get(name)
        if not handler:
            return {"success": False, "error": f"No handler for tool {name}"}

        try:
            result = handler(params)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


mcp_service = MCPService()
