"""
Bedrock AgentCore Integration
Integrates with AWS Bedrock AgentCore for agent status monitoring, tool calling, and session management.
"""
import asyncio
import json
import os
import time
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BEDROCK_MODEL_ID = os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


class BedrockAgentCore:
    """Bedrock AgentCore integration for agent monitoring"""
    
    def __init__(self, region: str = AWS_REGION, model_id: str = AWS_BEDROCK_MODEL_ID):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for Bedrock AgentCore")
        
        self.region = region
        self.model_id = model_id
        self._bedrock_runtime = None
        self._bedrock_agent = None  # AgentCore client (if available)
        self.agent_sessions: Dict[str, Dict[str, Any]] = {}
    
    def _get_bedrock_runtime_client(self):
        """Get or create Bedrock runtime client"""
        if self._bedrock_runtime is None:
            self._bedrock_runtime = boto3.client('bedrock-runtime', region_name=self.region)
        return self._bedrock_runtime
    
    async def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent status from AgentCore"""
        # Note: This is a system_value implementation
        # Actual AgentCore API may differ based on AWS service availability
        
        bedrock = self._get_bedrock_runtime_client()
        if not bedrock:
            return {
                "status": "unavailable",
                "error": "Bedrock client not available"
            }
        
        try:
            # System_value for actual AgentCore status check
            # In production, this would call AgentCore APIs
            return {
                "status": "active",
                "model": self.model_id,
                "region": self.region,
                "agent_id": agent_id,
                "timestamp": time.time(),
                "sessions": len(self.agent_sessions)
            }
        except Exception as e:
            logger.error("Failed to get agent status", error=str(e))
            return {"status": "error", "error": str(e)}
    
    async def create_session(self, agent_id: str, session_config: Optional[Dict[str, Any]] = None) -> str:
        """Create a new agent session"""
        session_id = f"session_{int(time.time())}_{agent_id}"
        
        self.agent_sessions[session_id] = {
            'agent_id': agent_id,
            'created_at': time.time(),
            'config': session_config or {},
            'status': 'active',
            'messages': []
        }
        
        logger.info("Agent session created", session_id=session_id, agent_id=agent_id)
        return session_id
    
    async def invoke_agent(self, session_id: str, message: str, 
                          tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Invoke agent with message and optional tools"""
        bedrock = self._get_bedrock_runtime_client()
        if not bedrock:
            return {"error": "Bedrock client not available"}
        
        if session_id not in self.agent_sessions:
            return {"error": "Session not found"}
        
        session = self.agent_sessions[session_id]
        
        try:
            # Build messages
            messages = session.get('messages', [])
            messages.append({"role": "user", "content": message})
            
            # Build request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": messages
            }
            
            # Add tools if provided
            if tools:
                body["tools"] = tools
            
            # Invoke model
            response = bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Update session
            messages.append({"role": "assistant", "content": response_text})
            session['messages'] = messages
            session['last_activity'] = time.time()
            
            return {
                "response": response_text,
                "session_id": session_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error("Failed to invoke agent", error=str(e))
            return {"error": str(e)}
    
    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session message history"""
        if session_id not in self.agent_sessions:
            return []
        
        return self.agent_sessions[session_id].get('messages', [])
    
    async def end_session(self, session_id: str):
        """End an agent session"""
        if session_id in self.agent_sessions:
            self.agent_sessions[session_id]['status'] = 'ended'
            self.agent_sessions[session_id]['ended_at'] = time.time()
            logger.info("Agent session ended", session_id=session_id)
    
    async def get_quality_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get quality evaluation metrics for agents"""
        # Filter sessions by agent_id if provided
        sessions = self.agent_sessions.values()
        if agent_id:
            sessions = [s for s in sessions if s.get('agent_id') == agent_id]
        
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.get('status') == 'active'])
        
        # Calculate average messages per session
        total_messages = sum(len(s.get('messages', [])) for s in sessions)
        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "avg_messages_per_session": avg_messages,
            "timestamp": time.time()
        }
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all active agents"""
        agent_ids = set(s.get('agent_id') for s in self.agent_sessions.values())
        
        agents = []
        for agent_id in agent_ids:
            sessions = [s for s in self.agent_sessions.values() 
                       if s.get('agent_id') == agent_id]
            agents.append({
                "agent_id": agent_id,
                "active_sessions": len([s for s in sessions if s.get('status') == 'active']),
                "total_sessions": len(sessions)
            })
        
        return agents
