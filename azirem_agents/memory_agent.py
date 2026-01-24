#!/usr/bin/env python3
"""
🧠 MEMORY AGENT - Persistent Memory & Vector Store
===================================================
Provides ChromaDB vector storage, conversation persistence,
and cross-session state for the AZIREM ecosystem.

Priority 1 Agent for completing Phase 6 tasks.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

# ChromaDB (optional)
CHROMADB_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    pass

# Sentence transformers for embeddings (optional)
EMBEDDINGS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    pass


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ConversationLogger:
    """Persists conversation history to disk."""
    
    def __init__(self, storage_dir: str = "/tmp/azirem_memory"):
        self.storage_dir = Path(storage_dir) / "conversations"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def log_exchange(self, session_id: str, user_input: str, agent_response: str, metadata: Dict = None):
        """Log a conversation exchange."""
        log_file = self.storage_dir / f"{session_id}.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_response,
            "metadata": metadata or {}
        }
        
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_history(self, session_id: str, last_n: int = 10) -> List[Dict]:
        """Get conversation history for a session."""
        log_file = self.storage_dir / f"{session_id}.jsonl"
        
        if not log_file.exists():
            return []
            
        entries = []
        with open(log_file) as f:
            for line in f:
                entries.append(json.loads(line))
                
        return entries[-last_n:]
        
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return [f.stem for f in self.storage_dir.glob("*.jsonl")]


class StateManager:
    """Cross-session state persistence."""
    
    def __init__(self, storage_dir: str = "/tmp/azirem_memory"):
        self.storage_dir = Path(storage_dir) / "state"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.storage_dir / "global_state.json"
        self._state = self._load()
        
    def _load(self) -> Dict:
        """Load state from disk."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"created": datetime.now().isoformat()}
        
    def _save(self):
        """Save state to disk."""
        self._state["updated"] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self._state, indent=2))
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self._state.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set a state value."""
        self._state[key] = value
        self._save()
        
    def update(self, updates: Dict):
        """Update multiple values."""
        self._state.update(updates)
        self._save()
        
    def get_all(self) -> Dict:
        """Get entire state."""
        return self._state.copy()


class ChromaDBSubagent:
    """Vector store operations using ChromaDB."""
    
    def __init__(self, persist_dir: str = "/tmp/azirem_memory/chroma"):
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        self.embedder = None
        
        if CHROMADB_AVAILABLE:
            self._init_chromadb()
        if EMBEDDINGS_AVAILABLE:
            self._init_embedder()
            
    def _init_chromadb(self):
        """Initialize ChromaDB client."""
        try:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir
            ))
            self.collection = self.client.get_or_create_collection(
                name="azirem_memory",
                metadata={"description": "AZIREM knowledge base"}
            )
        except Exception as e:
            print(f"⚠️ ChromaDB init failed: {e}")
            
    def _init_embedder(self):
        """Initialize sentence transformer for embeddings."""
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"⚠️ Embedder init failed: {e}")
            
    def add(self, id: str, content: str, metadata: Dict = None) -> bool:
        """Add content to vector store."""
        if not self.collection:
            return False
            
        try:
            # Generate embedding if we have embedder
            embedding = None
            if self.embedder:
                embedding = self.embedder.encode(content).tolist()
                
            self.collection.add(
                ids=[id],
                documents=[content],
                metadatas=[metadata or {}],
                embeddings=[embedding] if embedding else None
            )
            return True
        except Exception as e:
            print(f"⚠️ Add to ChromaDB failed: {e}")
            return False
            
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar content."""
        if not self.collection:
            return []
            
        try:
            # Generate query embedding
            query_embedding = None
            if self.embedder:
                query_embedding = self.embedder.encode(query).tolist()
                
            results = self.collection.query(
                query_embeddings=[query_embedding] if query_embedding else None,
                query_texts=[query] if not query_embedding else None,
                n_results=n_results
            )
            
            # Format results
            formatted = []
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                formatted.append({
                    "id": results["ids"][0][i] if results.get("ids") else None,
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
            return formatted
            
        except Exception as e:
            print(f"⚠️ ChromaDB search failed: {e}")
            return []
            
    def count(self) -> int:
        """Get total entries in store."""
        if not self.collection:
            return 0
        return self.collection.count()


class MemoryAgent:
    """
    Main Memory Agent - orchestrates all memory operations.
    
    Provides:
    - ChromaDB vector store for semantic search
    - Conversation logging for persistence
    - Cross-session state management
    """
    
    def __init__(self, storage_dir: str = "/tmp/azirem_memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize subagents
        self.conversations = ConversationLogger(str(self.storage_dir))
        self.state = StateManager(str(self.storage_dir))
        self.vectors = ChromaDBSubagent(str(self.storage_dir / "chroma"))
        
        # Callback for events
        self.callback: Optional[Callable] = None
        
    def set_callback(self, callback: Callable):
        """Set event callback."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: Dict):
        """Emit event to listeners."""
        if self.callback:
            await self.callback(event_type, {
                "agent": "memory",
                "timestamp": datetime.now().isoformat(),
                **data
            })
            
    async def remember(self, content: str, metadata: Dict = None) -> str:
        """Store content in memory."""
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Add to vector store
        self.vectors.add(memory_id, content, metadata)
        
        await self.emit("memory_stored", {
            "id": memory_id,
            "content_preview": content[:100]
        })
        
        return memory_id
        
    async def recall(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search memory for relevant content."""
        results = self.vectors.search(query, n_results)
        
        await self.emit("memory_recalled", {
            "query": query,
            "results_count": len(results)
        })
        
        return results
        
    async def log_conversation(self, session_id: str, user: str, agent: str, metadata: Dict = None):
        """Log a conversation exchange."""
        self.conversations.log_exchange(session_id, user, agent, metadata)
        
        # Also add to vector store for semantic search
        content = f"User: {user}\nAgent: {agent}"
        await self.remember(content, {
            "type": "conversation",
            "session_id": session_id,
            **(metadata or {})
        })
        
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "agent": "memory",
            "version": "1.0.0",
            "chromadb_available": CHROMADB_AVAILABLE,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "vector_count": self.vectors.count(),
            "sessions_count": len(self.conversations.list_sessions()),
            "storage_dir": str(self.storage_dir)
        }


# CLI for testing
async def demo():
    """Demo the Memory Agent."""
    print("🧠 Memory Agent Demo")
    print("=" * 50)
    
    agent = MemoryAgent()
    status = agent.get_status()
    
    print(f"\n📊 Status:")
    print(f"   ChromaDB: {'✅' if status['chromadb_available'] else '❌'}")
    print(f"   Embeddings: {'✅' if status['embeddings_available'] else '❌'}")
    print(f"   Vectors: {status['vector_count']}")
    print(f"   Sessions: {status['sessions_count']}")
    
    # Test memory storage
    print("\n📝 Storing test memory...")
    mem_id = await agent.remember(
        "AZIREM is a sovereign AI system with 13 agents",
        {"type": "fact", "source": "demo"}
    )
    print(f"   Stored: {mem_id}")
    
    # Test recall
    print("\n🔍 Recalling memories...")
    results = await agent.recall("What is AZIREM?")
    for r in results:
        print(f"   - {r['content'][:50]}...")
        
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
