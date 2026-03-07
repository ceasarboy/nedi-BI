"""
AI Agent集成测试
测试AI Agent与MCP工具的集成功能
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.ai.agent import PBBIAgent
from src.ai.llm_client import LLMConfig


class TestPBBIAgentIntegration:
    """AI Agent集成测试"""
    
    @pytest.fixture
    def agent(self):
        config = LLMConfig(
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model"
        )
        return PBBIAgent(config)
    
    def test_agent_initialization(self, agent):
        assert agent.llm_client is not None
        assert agent.tool_executor is not None
        assert agent.conversation_history == []
    
    def test_system_prompt_contains_date(self, agent):
        prompt = agent._get_system_prompt()
        assert "PB-BI智能数据分析助手" in prompt
        assert "202" in prompt
    
    def test_build_messages(self, agent):
        messages = agent._build_messages("测试消息")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "测试消息"
    
    def test_build_messages_with_history(self, agent):
        agent.conversation_history = [
            {"role": "user", "content": "历史消息1"},
            {"role": "assistant", "content": "历史回复1"}
        ]
        messages = agent._build_messages("新消息")
        assert len(messages) == 4
        assert messages[1]["content"] == "历史消息1"
        assert messages[2]["content"] == "历史回复1"
    
    def test_clear_history(self, agent):
        agent.conversation_history = [
            {"role": "user", "content": "测试"}
        ]
        agent.clear_history()
        assert agent.conversation_history == []
    
    def test_get_history(self, agent):
        agent.conversation_history = [
            {"role": "user", "content": "测试"}
        ]
        history = agent.get_history()
        assert len(history) == 1
        assert history[0]["content"] == "测试"


class TestMCPToolExecutor:
    """MCP工具执行器测试"""
    
    @pytest.fixture
    def executor(self):
        from src.ai.tools import MCPToolExecutor
        return MCPToolExecutor()
    
    def test_list_available_tools(self, executor):
        tools = executor.list_available_tools()
        assert len(tools) > 0
        
        tool_names = [t["name"] for t in tools]
        assert "pbbi_get_dataflows" in tool_names
        assert "pbbi_get_dataflow" in tool_names
        assert "pbbi_get_snapshots" in tool_names
    
    def test_execute_list_dataflows(self, executor):
        result = asyncio.run(executor.execute("pbbi_get_dataflows", {}))
        assert result["success"] is True
        assert "data" in result
    
    def test_execute_list_snapshots(self, executor):
        result = asyncio.run(executor.execute("pbbi_get_snapshots", {}))
        assert result["success"] is True
        assert "data" in result
    
    def test_execute_get_dataflow_invalid(self, executor):
        result = asyncio.run(executor.execute("pbbi_get_dataflow", {"dataflow_id": 99999}))
        assert result["success"] is True
        assert result.get("data") is None or result.get("data", {}).get("error") is not None
    
    def test_execute_unknown_tool(self, executor):
        result = asyncio.run(executor.execute("unknown_tool", {}))
        assert result["success"] is False
        assert "error" in result


class TestLLMClient:
    """LLM客户端测试"""
    
    def test_client_initialization(self):
        config = LLMConfig(
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model"
        )
        from src.ai.llm_client import LLMClient
        client = LLMClient(config)
        assert client.config is not None
        assert client.config.base_url is not None
    
    def test_get_tools_definition(self):
        config = LLMConfig(
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model"
        )
        from src.ai.llm_client import LLMClient
        client = LLMClient(config)
        tools = client.get_tools_definition()
        assert len(tools) > 0
        
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]


class TestAIAPIEndpoints:
    """AI API端点测试"""
    
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from src.main import app
        return TestClient(app)
    
    def test_get_tools_endpoint(self, client):
        response = client.get("/api/ai/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0
    
    def test_get_config_endpoint(self, client):
        response = client.get("/api/ai/config")
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert "base_url" in data
        assert "model" in data
    
    def test_get_history_endpoint(self, client):
        response = client.get("/api/ai/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
    
    def test_clear_history_endpoint(self, client):
        response = client.post("/api/ai/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestToolCategories:
    """工具分类测试"""
    
    @pytest.fixture
    def executor(self):
        from src.ai.tools import MCPToolExecutor
        return MCPToolExecutor()
    
    def test_database_tools_exist(self, executor):
        tools = executor.list_available_tools()
        tool_names = [t["name"] for t in tools]
        
        database_tools = [
            "pbbi_get_snapshots",
            "pbbi_get_snapshot_data",
            "pbbi_get_schema"
        ]
        for tool in database_tools:
            assert tool in tool_names, f"Database tool {tool} not found"
    
    def test_dataflow_tools_exist(self, executor):
        tools = executor.list_available_tools()
        tool_names = [t["name"] for t in tools]
        
        dataflow_tools = [
            "pbbi_get_dataflows",
            "pbbi_get_dataflow",
            "pbbi_query_data"
        ]
        for tool in dataflow_tools:
            assert tool in tool_names, f"Dataflow tool {tool} not found"
    
    def test_dashboard_tools_exist(self, executor):
        tools = executor.list_available_tools()
        tool_names = [t["name"] for t in tools]
        
        dashboard_tools = [
            "pbbi_get_dashboards"
        ]
        for tool in dashboard_tools:
            assert tool in tool_names, f"Dashboard tool {tool} not found"


class TestToolParameterValidation:
    """工具参数验证测试"""
    
    @pytest.fixture
    def executor(self):
        from src.ai.tools import MCPToolExecutor
        return MCPToolExecutor()
    
    def test_get_dataflow_with_valid_id(self, executor):
        result = asyncio.run(executor.execute("pbbi_get_dataflow", {"dataflow_id": 1}))
        assert result["success"] is True
    
    def test_get_snapshot_data_with_valid_id(self, executor):
        result = asyncio.run(executor.execute("pbbi_get_snapshot_data", {"snapshot_id": 1}))
        assert result["success"] is True
    
    def test_query_data_with_valid_dataflow_id(self, executor):
        result = asyncio.run(executor.execute("pbbi_query_data", {"dataflow_id": 1}))
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
