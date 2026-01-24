"""
Base Agent class for Cold Azirem Multi-Agent System
Adapted from OptimusAI BaseAgent with enhanced capabilities
"""

import asyncio
import logging
import httpx
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Foundation class for all Cold Azirem agents.
    
    Features:
    - Async Ollama LLM integration
    - Rolling context window for memory
    - Tool calling framework
    - Self-reflection capabilities
    - Event-driven communication
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        model: str,
        fallback_model: str,
        tools: Optional[Dict[str, Callable]] = None,
        max_context_messages: int = 10,
        temperature: float = 0.7,
        top_p: float = 0.9,
        ollama_base_url: str = "http://localhost:11434",
    ):
        """
        Initialize agent.
        
        Args:
            name: Agent identifier (e.g., "ArchitectureDev")
            role: Agent role description
            model: Primary Ollama model name
            fallback_model: Fallback model if primary fails
            tools: Dictionary of tool name -> callable function
            max_context_messages: Maximum messages in context window
            temperature: LLM temperature (0.0-1.0)
            top_p: LLM top_p sampling (0.0-1.0)
            ollama_base_url: Ollama API base URL
        """
        self.name = name
        self.role = role
        self.model = model
        self.fallback_model = fallback_model
        self.max_context_messages = max_context_messages
        self.temperature = temperature
        self.top_p = top_p
        
        # Context window (rolling memory)
        self.context: List[Dict[str, str]] = []
        
        # Tools registry
        self.tools = tools or {}
        
        # HTTP client for Ollama
        self.client = httpx.AsyncClient(
            base_url=ollama_base_url,
            timeout=120.0
        )
        
        # Event callbacks for inter-agent communication
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tool_calls": 0,
            "avg_response_time": 0.0,
        }
        
        logger.info(f"✅ Initialized {self.name} with model {self.model}")
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for agent events (for inter-agent communication)"""
        self.callbacks.append(callback)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all registered callbacks"""
        event = {
            "source": self.name,
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    async def think(self, user_message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Process a message and generate a response using the LLM.
        
        Args:
            user_message: The user's message/task
            context: Optional additional context messages
            
        Returns:
            The agent's response
        """
        start_time = datetime.now()
        
        # Emit think start event
        await self._emit_event("think_start", {"message": user_message})
        
        # Add user message to context
        self.context.append({"role": "user", "content": user_message})
        
        # Trim context if needed (rolling window)
        if len(self.context) > self.max_context_messages:
            self.context = self.context[-self.max_context_messages:]
        
        # Build messages for Ollama
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ]
        
        # Add additional context if provided
        if context:
            messages.extend(context)
        
        # Add agent's context
        messages.extend(self.context)
        
        try:
            # Call Ollama API
            response = await self._call_ollama(messages, self.model)
            
            if response is None:
                # Try fallback model
                logger.warning(f"{self.name}: Primary model failed, trying fallback {self.fallback_model}")
                response = await self._call_ollama(messages, self.fallback_model)
            
            if response is None:
                raise Exception("Both primary and fallback models failed")
            
            assistant_message = response["message"]["content"]
            
            # Add to context
            self.context.append({"role": "assistant", "content": assistant_message})
            
            # Update metrics
            self.metrics["total_requests"] += 1
            self.metrics["successful_requests"] += 1
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (self.metrics["successful_requests"] - 1) + response_time)
                / self.metrics["successful_requests"]
            )
            
            # Emit think end event
            await self._emit_event("think_end", {
                "response": assistant_message,
                "response_time": response_time
            })
            
            logger.debug(f"{self.name} response: {assistant_message[:100]}...")
            return assistant_message
            
        except Exception as e:
            self.metrics["total_requests"] += 1
            self.metrics["failed_requests"] += 1
            logger.error(f"{self.name} LLM error: {e}")
            await self._emit_event("error", {"error": str(e)})
            raise
    
    async def _call_ollama(self, messages: List[Dict], model: str) -> Optional[Dict]:
        """Call Ollama API with error handling"""
        try:
            response = await self.client.post(
                "/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ollama API error with model {model}: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent (override in subclasses)"""
        return f"""You are {self.name}, an AI agent specialized in {self.role}.

You are part of the Cold Azirem Multi-Agent Ecosystem. Your role is to:
- {self.role}
- Communicate clearly and concisely
- Use available tools when needed
- Collaborate with other agents
- Report results accurately

When you need to use a tool, respond with a JSON object:
{{"tool": "tool_name", "args": {{"arg1": "value1"}}}}

Available tools: {', '.join(self.tools.keys()) if self.tools else 'None'}

Current time: {datetime.now().isoformat()}
"""
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a registered tool.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}")
        
        tool_func = self.tools[tool_name]
        
        try:
            logger.info(f"{self.name} executing tool: {tool_name} with args: {args}")
            
            # Emit tool start event
            await self._emit_event("tool_start", {"tool": tool_name, "args": args})
            
            # Execute tool (handle both sync and async)
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)
            
            # Update metrics
            self.metrics["tool_calls"] += 1
            
            logger.info(f"{self.name} tool {tool_name} completed successfully")
            
            # Emit tool end event
            await self._emit_event("tool_end", {"tool": tool_name, "result": result})
            
            return result
            
        except Exception as e:
            logger.error(f"{self.name} tool {tool_name} failed: {e}")
            await self._emit_event("tool_error", {"tool": tool_name, "error": str(e)})
            raise
    
    async def process(self, task: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Process a task with potential tool usage.
        
        Args:
            task: The task to process
            max_iterations: Maximum number of think-tool loops
            
        Returns:
            Processing result with response and tool calls
        """
        tool_calls = []
        response = ""
        
        await self._emit_event("process_start", {"task": task})
        
        for iteration in range(max_iterations):
            logger.debug(f"{self.name} iteration {iteration + 1}/{max_iterations}")
            
            # Think
            response = await self.think(task)
            
            # Check if response contains tool call
            if self._is_tool_call(response):
                tool_call = self._parse_tool_call(response)
                
                if tool_call:
                    tool_name = tool_call["tool"]
                    tool_args = tool_call.get("args", {})
                    
                    # Execute tool
                    try:
                        tool_result = await self.execute_tool(tool_name, tool_args)
                        tool_calls.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "result": tool_result,
                            "success": True
                        })
                        
                        # Add tool result to context for next iteration
                        task = f"Tool '{tool_name}' returned: {tool_result}\n\nContinue with the task."
                        
                    except Exception as e:
                        tool_calls.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "error": str(e),
                            "success": False
                        })
                        task = f"Tool '{tool_name}' failed with error: {e}\n\nTry a different approach."
                else:
                    # No valid tool call, return response
                    break
            else:
                # No tool call, task complete
                break
        
        result = {
            "agent": self.name,
            "response": response,
            "tool_calls": tool_calls,
            "success": True,
            "iterations": iteration + 1,
            "metrics": self.metrics.copy()
        }
        
        await self._emit_event("process_complete", result)
        return result
    
    def _is_tool_call(self, response: str) -> bool:
        """Check if response contains a tool call"""
        response = response.strip()
        if "{" in response and "}" in response:
            try:
                # Try to find JSON block
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_str = response[start:end]
                
                data = json.loads(json_str)
                return "tool" in data
            except:
                pass
        return False
    
    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Parse tool call from response"""
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                response = response[start:end]
            
            tool_call = json.loads(response)
            
            if "tool" in tool_call:
                return tool_call
            return None
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse tool call: {response}")
            return None
    
    def reset_context(self):
        """Clear conversation context"""
        self.context = []
        logger.info(f"{self.name} context reset")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return self.metrics.copy()
    
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()
