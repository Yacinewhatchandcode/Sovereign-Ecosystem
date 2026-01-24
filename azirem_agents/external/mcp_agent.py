"""
MCPAgent - Interface for Model Context Protocol (MCP) servers
Integrates deepsearch-local and github servers for enhanced capabilities
"""
import os
from config import config
import structlog

logger = structlog.get_logger()

class MCPAgent:
    """Agent responsible for communicating with MCP servers"""

    def __init__(self):
        self.enabled = config.mcp_enabled
        self.sessions = {}
        self.server_params = {
            "deepsearch": StdioServerParameters(
                command="/Users/yacinebenhamou/.bun/bin/bun",
                args=["run", "/Users/yacinebenhamou/ConverseSpark/server/mcp-server.ts"],
                env={
                    **os.environ,
                    "DATABASE_URL": config.mcp_deepsearch_url,
                    "OPENROUTER_API_KEY": config.mcp_openrouter_key,
                    "PERPLEXITY_API_KEY": config.mcp_perplexity_key,
                }
            ),
            "github": StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": config.mcp_github_token,
                }
            )
        }
        logger.info("MCPAgent initialized", enabled=self.enabled)

    async def _get_session(self, server_name: str) -> Optional[ClientSession]:
        """Get or create a session for the specified server"""
        if not self.enabled:
            return None

        if server_name in self.sessions:
            return self.sessions[server_name]

        if server_name not in self.server_params:
            logger.error("Unknown MCP server", server=server_name)
            return None

        try:
            params = self.server_params[server_name]
            # Use stdio_client context manager but since we want persistent sessions,
            # we'll handle the connection manually or create a new one each time.
            # For simplicity in this implementation, we'll create a new connection per request
            # but ideally we'd keep it open.
            return params
        except Exception as e:
            logger.error("Failed to connect to MCP server", server=server_name, error=str(e))
            return None

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server"""
        if not self.enabled:
            return None

        params = await self._get_session(server_name)
        if not params:
            return None

        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)

                    # Extract data from CallToolResult
                    if hasattr(result, 'content'):
                        # The content is usually a list of text/image objects
                        # For simple tool calls, we just want the text data
                        text_content = [r.text for r in result.content if hasattr(r, 'text')]
                        logger.info("MCP tool called", server=server_name, tool=tool_name, success=True)

                        # Most GitHub tools return JSON strings in the text content
                        if text_content:
                            import json
                            try:
                                return json.loads(text_content[0])
                            except:
                                return text_content[0]

                    return result
        except Exception as e:
            logger.error("MCP tool call failed", server=server_name, tool=tool_name, error=str(e))
            return None

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools on an MCP server"""
        if not self.enabled:
            return []

        params = await self._get_session(server_name)
        if not params:
            return []

        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    return result.tools
        except Exception as e:
            logger.error("Failed to list MCP tools", server=server_name, error=str(e))
            return []

    async def search_deep(self, query: str) -> Any:
        """Helper to use deepsearch-local for complex queries"""
        # Assuming the deepsearch server has a 'search' or similar tool
        return await self.call_tool("deepsearch", "search", {"query": query})

    async def github_action(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Helper to use github MCP tools"""
        return await self.call_tool("github", tool_name, arguments)

    async def get_repo_context(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository details, issues, and pull requests for context"""
        context = {}
        try:
            # 1. Get repository metadata
            repo_info = await self.github_action("get_repository", {"owner": owner, "repo": repo})
            context["info"] = repo_info

            # 2. Get recent issues (top 5)
            issues = await self.github_action("list_issues", {"owner": owner, "repo": repo, "state": "open", "per_page": 5})
            context["issues"] = issues

            # 3. Get recent PRs (top 5)
            prs = await self.github_action("list_pull_requests", {"owner": owner, "repo": repo, "state": "open", "per_page": 5})
            context["pull_requests"] = prs

            logger.info("GitHub context retrieved", owner=owner, repo=repo)
            return context
        except Exception as e:
            logger.error("Failed to fetch GitHub context", error=str(e))
            return {"error": str(e)}