#!/usr/bin/env python3
"""
🔌 PLUGIN CONNECTOR
===================
Connects external APIs and services as plugged agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import asyncio
import json

class PluginType(Enum):
    LLM = "llm"
    DATABASE = "database"
    CLOUD = "cloud"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    CODE_ANALYSIS = "code_analysis"
    STORAGE = "storage"
    AUTH = "auth"
    WEBHOOK = "webhook"

class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER = "bearer"
    BASIC = "basic"
    NONE = "none"

@dataclass
class PluginConfig:
    """Configuration for a plugin"""
    name: str
    type: PluginType
    base_url: str
    auth_type: AuthType
    auth_config: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: int = 100  # requests per minute
    timeout: float = 30.0
    retry_count: int = 3

@dataclass
class PluginEndpoint:
    """Single endpoint of a plugin"""
    name: str
    method: str
    path: str
    description: str
    params: List[str] = field(default_factory=list)
    body_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None

@dataclass
class PluggedAgent:
    """An external service wrapped as an agent"""
    name: str
    config: PluginConfig
    endpoints: List[PluginEndpoint]
    created_at: datetime = field(default_factory=datetime.now)
    
    async def call(self, endpoint_name: str, params: Dict = None) -> Dict:
        """Call a plugin endpoint"""
        endpoint = next(
            (e for e in self.endpoints if e.name == endpoint_name),
            None
        )
        if not endpoint:
            return {"error": f"Unknown endpoint: {endpoint_name}"}
        
        # Simulated call - would use aiohttp in production
        return {
            "plugin": self.name,
            "endpoint": endpoint_name,
            "status": "success",
            "params": params
        }

class PluginConnector:
    """
    🔌 Plugin Connector
    
    Connects external APIs as plugged agents in the system.
    """
    
    # Pre-defined plugin configurations
    KNOWN_PLUGINS = {
        # LLM Providers
        "openai": PluginConfig(
            name="OpenAI",
            type=PluginType.LLM,
            base_url="https://api.openai.com/v1",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "OPENAI_API_KEY"}
        ),
        "anthropic": PluginConfig(
            name="Anthropic",
            type=PluginType.LLM,
            base_url="https://api.anthropic.com/v1",
            auth_type=AuthType.API_KEY,
            auth_config={"header": "x-api-key", "env_var": "ANTHROPIC_API_KEY"}
        ),
        "mistral": PluginConfig(
            name="Mistral",
            type=PluginType.LLM,
            base_url="https://api.mistral.ai/v1",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "MISTRAL_API_KEY"}
        ),
        
        # Cloud Providers
        "aws": PluginConfig(
            name="AWS",
            type=PluginType.CLOUD,
            base_url="https://aws.amazon.com",
            auth_type=AuthType.API_KEY,
            auth_config={"env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]}
        ),
        "azure": PluginConfig(
            name="Azure",
            type=PluginType.CLOUD,
            base_url="https://management.azure.com",
            auth_type=AuthType.OAUTH2,
            auth_config={"env_var": "AZURE_CREDENTIALS"}
        ),
        "gcp": PluginConfig(
            name="GCP",
            type=PluginType.CLOUD,
            base_url="https://cloud.google.com",
            auth_type=AuthType.OAUTH2,
            auth_config={"env_var": "GOOGLE_APPLICATION_CREDENTIALS"}
        ),
        
        # Databases
        "supabase": PluginConfig(
            name="Supabase",
            type=PluginType.DATABASE,
            base_url="https://api.supabase.io",
            auth_type=AuthType.API_KEY,
            auth_config={"env_var": "SUPABASE_KEY"}
        ),
        "mongodb": PluginConfig(
            name="MongoDB",
            type=PluginType.DATABASE,
            base_url="mongodb://localhost:27017",
            auth_type=AuthType.BASIC,
            auth_config={"env_vars": ["MONGO_USER", "MONGO_PASSWORD"]}
        ),
        
        # Monitoring
        "datadog": PluginConfig(
            name="Datadog",
            type=PluginType.MONITORING,
            base_url="https://api.datadoghq.com",
            auth_type=AuthType.API_KEY,
            auth_config={"env_var": "DD_API_KEY"}
        ),
        "sentry": PluginConfig(
            name="Sentry",
            type=PluginType.MONITORING,
            base_url="https://sentry.io/api/0",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "SENTRY_DSN"}
        ),
        "opik": PluginConfig(
            name="Opik",
            type=PluginType.MONITORING,
            base_url="http://localhost:5173",
            auth_type=AuthType.NONE,
            auth_config={}
        ),
        
        # Communication
        "slack": PluginConfig(
            name="Slack",
            type=PluginType.COMMUNICATION,
            base_url="https://slack.com/api",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "SLACK_BOT_TOKEN"}
        ),
        "discord": PluginConfig(
            name="Discord",
            type=PluginType.COMMUNICATION,
            base_url="https://discord.com/api/v10",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "DISCORD_BOT_TOKEN"}
        ),
        
        # Code Analysis
        "github": PluginConfig(
            name="GitHub",
            type=PluginType.CODE_ANALYSIS,
            base_url="https://api.github.com",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "GITHUB_TOKEN"}
        ),
        "sonarqube": PluginConfig(
            name="SonarQube",
            type=PluginType.CODE_ANALYSIS,
            base_url="https://sonarcloud.io/api",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "SONAR_TOKEN"}
        ),
        
        # Search
        "perplexity": PluginConfig(
            name="Perplexity",
            type=PluginType.LLM,
            base_url="https://api.perplexity.ai",
            auth_type=AuthType.BEARER,
            auth_config={"env_var": "PERPLEXITY_API_KEY"}
        ),
    }
    
    # Standard endpoints for each plugin type
    STANDARD_ENDPOINTS = {
        PluginType.LLM: [
            PluginEndpoint("chat", "POST", "/chat/completions", "Send chat message"),
            PluginEndpoint("embeddings", "POST", "/embeddings", "Generate embeddings"),
        ],
        PluginType.DATABASE: [
            PluginEndpoint("query", "POST", "/query", "Execute query"),
            PluginEndpoint("insert", "POST", "/insert", "Insert data"),
            PluginEndpoint("update", "PATCH", "/update", "Update data"),
            PluginEndpoint("delete", "DELETE", "/delete", "Delete data"),
        ],
        PluginType.MONITORING: [
            PluginEndpoint("log", "POST", "/logs", "Send log"),
            PluginEndpoint("metric", "POST", "/metrics", "Send metric"),
            PluginEndpoint("trace", "POST", "/traces", "Send trace"),
        ],
        PluginType.COMMUNICATION: [
            PluginEndpoint("send_message", "POST", "/messages", "Send message"),
            PluginEndpoint("get_channels", "GET", "/channels", "List channels"),
        ],
        PluginType.CLOUD: [
            PluginEndpoint("list_resources", "GET", "/resources", "List resources"),
            PluginEndpoint("create_resource", "POST", "/resources", "Create resource"),
            PluginEndpoint("delete_resource", "DELETE", "/resources", "Delete resource"),
        ],
        PluginType.CODE_ANALYSIS: [
            PluginEndpoint("analyze", "POST", "/analyze", "Analyze code"),
            PluginEndpoint("get_issues", "GET", "/issues", "Get issues"),
        ],
    }
    
    def __init__(self):
        self.connected_plugins: Dict[str, PluggedAgent] = {}
        
    def connect(self, plugin_name: str, custom_config: Dict = None) -> PluggedAgent:
        """Connect a plugin by name"""
        
        if plugin_name not in self.KNOWN_PLUGINS:
            raise ValueError(f"Unknown plugin: {plugin_name}")
        
        config = self.KNOWN_PLUGINS[plugin_name]
        
        # Apply custom config overrides
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Get standard endpoints
        endpoints = self.STANDARD_ENDPOINTS.get(config.type, [])
        
        # Create plugged agent
        agent = PluggedAgent(
            name=plugin_name,
            config=config,
            endpoints=endpoints
        )
        
        self.connected_plugins[plugin_name] = agent
        return agent
    
    def connect_custom(
        self,
        name: str,
        config: PluginConfig,
        endpoints: List[PluginEndpoint]
    ) -> PluggedAgent:
        """Connect a custom plugin"""
        agent = PluggedAgent(
            name=name,
            config=config,
            endpoints=endpoints
        )
        self.connected_plugins[name] = agent
        return agent
    
    def connect_all_available(self) -> List[PluggedAgent]:
        """Connect all known plugins"""
        agents = []
        for plugin_name in self.KNOWN_PLUGINS.keys():
            try:
                agent = self.connect(plugin_name)
                agents.append(agent)
            except Exception as e:
                print(f"Failed to connect {plugin_name}: {e}")
        return agents
    
    def get_by_type(self, plugin_type: PluginType) -> List[PluggedAgent]:
        """Get all connected plugins of a type"""
        return [
            agent for agent in self.connected_plugins.values()
            if agent.config.type == plugin_type
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connector statistics"""
        return {
            "total_connected": len(self.connected_plugins),
            "known_plugins": len(self.KNOWN_PLUGINS),
            "by_type": {
                ptype.value: len([
                    a for a in self.connected_plugins.values()
                    if a.config.type == ptype
                ])
                for ptype in PluginType
            }
        }

# MCP Server integration (using existing MCP servers in the system)
MCP_INTEGRATIONS = {
    "github-mcp-server": {
        "plugin": "github",
        "capabilities": [
            "create_pull_request", "list_issues", "get_file_contents",
            "search_code", "create_branch", "merge_pull_request"
        ]
    },
    "perplexity-ask": {
        "plugin": "perplexity",
        "capabilities": [
            "perplexity_ask", "perplexity_reason", "perplexity_research"
        ]
    },
    "supabase-mcp-server": {
        "plugin": "supabase",
        "capabilities": [
            "execute_sql", "list_tables", "apply_migration",
            "deploy_edge_function", "list_projects"
        ]
    }
}

# Export
__all__ = [
    "PluginConnector",
    "PluggedAgent",
    "PluginConfig",
    "PluginEndpoint",
    "PluginType",
    "AuthType",
    "MCP_INTEGRATIONS"
]

if __name__ == "__main__":
    print("🔌 PLUGIN CONNECTOR")
    print("=" * 60)
    
    connector = PluginConnector()
    
    # Connect all available plugins
    agents = connector.connect_all_available()
    
    print(f"\n✅ Connected {len(agents)} plugins:\n")
    
    for agent in agents:
        print(f"   📦 {agent.name}")
        print(f"      Type: {agent.config.type.value}")
        print(f"      Auth: {agent.config.auth_type.value}")
        print(f"      Endpoints: {len(agent.endpoints)}")
    
    print("\n📊 Stats:", connector.get_stats())
    
    print("\n🔗 MCP Integrations Available:")
    for mcp_name, info in MCP_INTEGRATIONS.items():
        print(f"   • {mcp_name} -> {info['plugin']}")
        print(f"     Capabilities: {', '.join(info['capabilities'][:3])}...")
