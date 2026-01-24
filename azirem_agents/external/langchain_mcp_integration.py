"""
LangChain MCP Integration - Bridge between LangChain and MCP Server
Allows LangChain agents to communicate with Duix Avatar agents via MCP
"""
import asyncio
import sys
import os
from typing import Dict, Any, List, Optional

# Try to import LangChain MCP adapters
LANGCHAIN_MCP_AVAILABLE = False
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_core.tools import BaseTool
    LANGCHAIN_MCP_AVAILABLE = True
except ImportError as e:
    # Fallback: create a simple wrapper that uses the MCP server directly
    logger.debug("LangChain MCP adapters not available", error=str(e))
    pass

from config import config
import structlog

logger = structlog.get_logger()

class LangChainMCPIntegration:
    """Integration layer for LangChain to communicate with agents via MCP"""

    def __init__(self):
        self.enabled = config.mcp_enabled and LANGCHAIN_MCP_AVAILABLE
        self.client = None

        if self.enabled:
            try:
                # Connect to our MCP server (Lisa-Agents)
                # The MCP server runs as stdio, so we need to connect to it
                self.client = self._create_client()
                logger.info("LangChain MCP Integration initialized", enabled=True)
            except Exception as e:
                logger.error("Failed to initialize LangChain MCP client", error=str(e))
                self.enabled = False
        else:
            logger.warning("LangChain MCP Integration disabled",
                         mcp_enabled=config.mcp_enabled,
                         adapters_available=LANGCHAIN_MCP_AVAILABLE)

    def _create_client(self):
        """Create MCP client connection to our agent server"""
        if not LANGCHAIN_MCP_AVAILABLE:
            return None

        try:
            # Connect to the MCP server that exposes our agents
            # The server is at agents/mcp_server.py and runs via stdio
            client = MultiServerMCPClient({
                "lisa-agents": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": [os.path.join(os.path.dirname(__file__), "mcp_server.py")],
                },
            })
            return client
        except Exception as e:
            logger.error("Failed to create MCP client", error=str(e))
            return None

    async def get_agent_tools(self) -> List[BaseTool]:
        """Get LangChain tools that wrap our MCP agent tools"""
        if not self.enabled or not self.client:
            return []

        try:
            tools = await self.client.get_tools()
            logger.info("Retrieved agent tools via LangChain MCP", count=len(tools))
            return tools
        except Exception as e:
            logger.error("Failed to get agent tools", error=str(e))
            return []

    async def chat_with_agent(self, message: str, user_id: Optional[str] = None) -> str:
        """Chat with OrchestratorAgent via LangChain MCP"""
        if not self.enabled or not self.client:
            return "LangChain MCP integration not available"

        try:
            # Get the chat_with_lisa tool
            tools = await self.get_agent_tools()
            chat_tool = next((t for t in tools if t.name == "chat_with_lisa"), None)

            if chat_tool:
                result = await chat_tool.ainvoke({"message": message, "user_id": user_id})
                return result
            else:
                return "chat_with_lisa tool not found"
        except Exception as e:
            logger.error("Failed to chat with agent via LangChain MCP", error=str(e))
            return f"Error: {str(e)}"

    async def get_system_status(self) -> str:
        """Get system status via LangChain MCP"""
        if not self.enabled or not self.client:
            return "LangChain MCP integration not available"

        try:
            tools = await self.get_agent_tools()
            status_tool = next((t for t in tools if t.name == "get_system_status"), None)

            if status_tool:
                result = await status_tool.ainvoke({})
                return result
            else:
                return "get_system_status tool not found"
        except Exception as e:
            logger.error("Failed to get system status via LangChain MCP", error=str(e))
            return f"Error: {str(e)}"

# Fallback: Direct MCP communication if LangChain adapters not available
class DirectMCPWrapper:
    """Direct wrapper for MCP server when LangChain adapters unavailable"""

    def __init__(self):
        self.enabled = config.mcp_enabled
        logger.info("Direct MCP Wrapper initialized", enabled=self.enabled)

    async def chat_with_agent(self, message: str, user_id: Optional[str] = None) -> str:
        """Direct communication with MCP server"""
        if not self.enabled:
            return "MCP not enabled"

        # Import orchestrator directly
        try:
            from orchestrator_agent import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            result = await orchestrator.process_message(
                query=message,
                user_id=user_id,
                generate_audio=False
            )
            if result.get("success"):
                return result.get("response", "No response")
            return f"Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            logger.error("Direct MCP communication failed", error=str(e))
            return f"Error: {str(e)}"

# Export the appropriate integration
if LANGCHAIN_MCP_AVAILABLE:
    LangChainAgentBridge = LangChainMCPIntegration
else:
    LangChainAgentBridge = DirectMCPWrapper
