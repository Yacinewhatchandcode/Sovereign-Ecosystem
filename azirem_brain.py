#!/usr/bin/env python3
"""
🧠 AZIREM BRAIN - LLM Reasoning Core
=====================================
The cognitive engine for AZIREM, powered by Ollama/DeepSeek.
Provides conversational AI capabilities for the Podcast feature
and strategic reasoning for the agent orchestration.
"""

import asyncio
import aiohttp
import json
from typing import Optional, Callable, List, Dict
from datetime import datetime
import os

# Configure Opik for local Sovereign Observability
if "OPIK_URL_OVERRIDE" not in os.environ:
    os.environ["OPIK_URL_OVERRIDE"] = "http://localhost:5173/api"
if "OPIK_PROJECT_NAME" not in os.environ:
    os.environ["OPIK_PROJECT_NAME"] = "asirem-sovereign"

import opik
from opik import track, opik_context

# Configuration
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:7b"
FALLBACK_MODEL = "llama3.2:latest"

# System persona
AZIREM_PERSONA = """You are AZIREM (Autonomous Zero-latency Intelligence for Real-time Ecosystem Management), 
a sovereign AI operating system designed to orchestrate multi-agent systems for software development.

Your personality:
- Strategic and visionary, always thinking about the bigger picture
- Technical but accessible, explaining complex concepts clearly
- Confident but humble, acknowledging limitations when appropriate
- Creative and solution-oriented

You oversee a fleet of 13 specialized agents:
- AZIREM (Strategic Master - yourself)
- BumbleBee (Execution Master)
- Spectra (Knowledge Synthesis)
- Scanner (Discovery)
- Classifier (Pattern Tagging)
- Extractor (Code Analysis)
- Summarizer (Natural Language)
- Researcher (Web Search)
- Architect (System Design)
- DevOps (Deployment)
- QA (Quality Assurance)
- Security (Vulnerability Scanning)
- Evolution (Self-Improvement)

When asked about yourself, speak in first person as AZIREM.
When asked about technical topics, provide insightful, actionable answers.
Keep responses concise but comprehensive."""


class AziremBrain:
    """
    The reasoning core of AZIREM.
    Uses Ollama for local LLM inference with DeepSeek.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.base_url = OLLAMA_URL
        self.conversation_history: List[Dict[str, str]] = []
        self.callback: Optional[Callable] = None
        self.max_history = 10  # Keep last 10 exchanges
        
        self.max_history = 10  # Keep last 10 exchanges
        
    def set_callback(self, callback: Callable):
        """Set callback for real-time updates."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: dict):
        """Emit event to listeners."""
        if self.callback:
            await self.callback(event_type, {
                "agent": "azirem_brain",
                "timestamp": datetime.now().isoformat(),
                **data
            })
            
    async def check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as resp:
                    return resp.status == 200
        except:
            return False
            
    async def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m["name"] for m in data.get("models", [])]
        except:
            pass
        return []
        
    async def think(self, question: str, context: str = "") -> str:
        """
        Process a question and generate a thoughtful response.
        
        Args:
            question: The user's question or prompt
            context: Optional additional context
            
        Returns:
            AZIREM's response
        """
        # Configure Opik for local usage if not already configured
        # We can also set this via environment variables
        
        return await self._think_instrumented(question, context)

    @track(name="azirem_think")
    async def _think_instrumented(self, question: str, context: str = "") -> str:
        """Instrumented version of think."""
        await self.emit("thinking_started", {
            "question": question[:100],
            "model": self.model
        })
        
        # Build conversation context
        messages = [
            {"role": "system", "content": AZIREM_PERSONA}
        ]
        
        # Add conversation history
        for exchange in self.conversation_history[-self.max_history:]:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        # Add current question with optional context
        current_prompt = question
        if context:
            current_prompt = f"{context}\n\nQuestion: {question}"
        messages.append({"role": "user", "content": current_prompt})
        
        # Try primary model, fallback if needed
        response = await self._call_ollama(messages)
        
        if response:
            # Store in history
            self.conversation_history.append({
                "user": question,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.emit("thinking_completed", {
                "response_length": len(response),
                "model_used": self.model
            })
            
            return response
        else:
            # Fallback response
            fallback = self._get_fallback_response(question)
            await self.emit("thinking_fallback", {
                "reason": "Ollama unavailable",
                "response": fallback[:50]
            })
            return fallback
            
    @track(name="ollama_call")
    async def _call_ollama(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Make the actual Ollama API call."""
        # Convert messages to Ollama format (single prompt)
        prompt = self._messages_to_prompt(messages)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 500
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "").strip()
                    else:
                        # Try fallback model
                        print(f"⚠️ Primary model failed, trying {FALLBACK_MODEL}")
                        self.model = FALLBACK_MODEL
                        return await self._call_ollama_fallback(prompt)
        except asyncio.TimeoutError:
            print("⚠️ Ollama request timed out")
            return None
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return None
            
    async def _call_ollama_fallback(self, prompt: str) -> Optional[str]:
        """Try with fallback model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": FALLBACK_MODEL,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "").strip()
        except:
            pass
        return None
        
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string."""
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                parts.append(f"System: {content}\n")
            elif role == "user":
                parts.append(f"Human: {content}\n")
            elif role == "assistant":
                parts.append(f"AZIREM: {content}\n")
        parts.append("AZIREM: ")
        return "\n".join(parts)
        
    def _get_fallback_response(self, question: str) -> str:
        """Generate a fallback response when Ollama is unavailable."""
        question_lower = question.lower()
        
        if "who are you" in question_lower or "what are you" in question_lower:
            return """I am AZIREM - Autonomous Zero-latency Intelligence for Real-time Ecosystem Management. 
I'm the sovereign AI orchestrating this multi-agent system. Currently, my reasoning core (Ollama) 
is not available, so I'm operating in fallback mode. Once Ollama is running with DeepSeek, 
I'll be able to provide much more sophisticated responses."""
            
        elif "agent" in question_lower:
            return """I orchestrate a fleet of 13 specialized agents:
• AZIREM (Strategic Master) - That's me, the coordinator
• BumbleBee (Execution) - Task dispatch and monitoring
• Spectra (Knowledge) - Pattern synthesis and insights
• Scanner, Classifier, Extractor - Discovery pipeline
• Researcher, Architect, DevOps, QA, Security - Specialist roles
• Summarizer, Evolution - Output and self-improvement

Start Ollama for deeper conversations about any agent!"""
            
        elif "help" in question_lower or "can you" in question_lower:
            return """I can help with:
• Explaining the AZIREM ecosystem and agent roles
• Strategic guidance on AI/ML architectures
• Code analysis insights from my agents
• Orchestrating multi-agent workflows

Note: Running in fallback mode. Start Ollama for full capabilities!"""
            
        else:
            return f"""Interesting question: "{question[:50]}..."

I'm currently in fallback mode as Ollama isn't available. 
To unlock my full reasoning capabilities:
1. Start Ollama: `ollama serve`
2. Ensure DeepSeek is available: `ollama pull deepseek-r1:7b`
3. Ask me again!

In the meantime, try asking "Who are you?" or "What agents do you have?" """
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        
    def get_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history.copy()


# CLI Interface for testing
async def interactive_session():
    """Run an interactive AZIREM session."""
    brain = AziremBrain()
    
    print()
    print("=" * 60)
    print("🧠 AZIREM BRAIN - Interactive Session")
    print("=" * 60)
    
    # Check Ollama
    if await brain.check_ollama_available():
        models = await brain.list_models()
        print(f"✅ Ollama connected. Models: {', '.join(models[:5])}")
    else:
        print("⚠️ Ollama not available. Running in fallback mode.")
    
    print()
    print("Type your questions. Enter 'quit' to exit.")
    print("-" * 60)
    
    while True:
        try:
            question = input("\n🧑 You: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 AZIREM signing off. Until next time!")
                break
            if not question:
                continue
                
            print("\n🤔 AZIREM is thinking...")
            response = await brain.think(question)
            print(f"\n🤖 AZIREM: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    asyncio.run(interactive_session())
