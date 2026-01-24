#!/usr/bin/env python3
"""
🔮 EMBEDDING AGENT - Semantic Search & Embeddings
==================================================
Generates and searches vector embeddings for semantic
understanding of code, documentation, and conversations.

Priority 3 Agent for completing Phase 8 tasks.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
from dataclasses import dataclass

# Embedding models
EMBEDDINGS_AVAILABLE = False
EMBEDDING_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    pass

# NumPy for similarity
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: str


class EmbeddingAgent:
    """
    Embedding Agent - semantic search and vector operations.
    
    Provides:
    - Text to vector embedding generation
    - Semantic similarity search
    - Code understanding via embeddings
    - Documentation semantic indexing
    """
    
    SUPPORTED_MODELS = [
        "all-MiniLM-L6-v2",      # Fast, good quality
        "all-mpnet-base-v2",     # Best quality
        "paraphrase-MiniLM-L6-v2"  # Paraphrase focused
    ]
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.callback: Optional[Callable] = None
        
        # In-memory index (for quick access)
        self.index: List[EmbeddingResult] = []
        
        # Initialize model
        self._init_model()
        
    def _init_model(self):
        """Initialize the embedding model."""
        if not EMBEDDINGS_AVAILABLE:
            print("⚠️ sentence-transformers not installed")
            print("   Run: pip install sentence-transformers")
            return
            
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"⚠️ Failed to load model: {e}")
            
    def set_callback(self, callback: Callable):
        """Set event callback."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: Dict):
        """Emit event to listeners."""
        if self.callback:
            await self.callback(event_type, {
                "agent": "embedding",
                "timestamp": datetime.now().isoformat(),
                **data
            })
            
    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        if not self.model:
            return None
            
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️ Embedding failed: {e}")
            return None
            
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        if not self.model:
            return [None] * len(texts)
            
        try:
            embeddings = self.model.encode(texts)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            print(f"⚠️ Batch embedding failed: {e}")
            return [None] * len(texts)
            
    async def index_text(self, id: str, text: str, metadata: Dict = None) -> EmbeddingResult:
        """Index a text for semantic search."""
        embedding = self.embed(text)
        
        if embedding is None:
            await self.emit("index_failed", {"id": id, "reason": "embedding failed"})
            return None
            
        result = EmbeddingResult(
            id=id,
            text=text,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat()
        )
        
        self.index.append(result)
        
        await self.emit("text_indexed", {
            "id": id,
            "text_preview": text[:50],
            "embedding_dim": len(embedding)
        })
        
        return result
        
    async def index_file(self, file_path: str, chunk_size: int = 500) -> List[EmbeddingResult]:
        """Index a file by chunking and embedding."""
        path = Path(file_path)
        
        if not path.exists():
            await self.emit("index_failed", {"path": file_path, "reason": "file not found"})
            return []
            
        try:
            content = path.read_text()
        except Exception as e:
            await self.emit("index_failed", {"path": file_path, "reason": str(e)})
            return []
            
        # Chunk content
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        results = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{path.stem}_{i}"
            result = await self.index_text(
                chunk_id, 
                chunk,
                {"file": str(path), "chunk": i, "total_chunks": len(chunks)}
            )
            if result:
                results.append(result)
                
        await self.emit("file_indexed", {
            "path": file_path,
            "chunks": len(results)
        })
        
        return results
        
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not NUMPY_AVAILABLE:
            # Simple dot product fallback
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = sum(x**2 for x in a) ** 0.5
            norm_b = sum(x**2 for x in b) ** 0.5
            return dot / (norm_a * norm_b) if norm_a and norm_b else 0
            
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search in indexed content."""
        query_embedding = self.embed(query)
        
        if query_embedding is None:
            return []
            
        # Compute similarities
        scored = []
        for item in self.index:
            similarity = self._cosine_similarity(query_embedding, item.embedding)
            scored.append({
                "id": item.id,
                "text": item.text,
                "metadata": item.metadata,
                "similarity": similarity
            })
            
        # Sort by similarity
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        
        await self.emit("search_completed", {
            "query": query[:50],
            "results_count": min(top_k, len(scored))
        })
        
        return scored[:top_k]
        
    async def find_similar(self, text: str, top_k: int = 5) -> List[Dict]:
        """Find similar indexed content."""
        return await self.search(text, top_k)
        
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "agent": "embedding",
            "version": "1.0.0",
            "model": self.model_name,
            "model_loaded": self.model is not None,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "indexed_count": len(self.index)
        }
        
    def clear_index(self):
        """Clear the in-memory index."""
        self.index = []


# CLI for testing
async def demo():
    """Demo the Embedding Agent."""
    print("🔮 Embedding Agent Demo")
    print("=" * 50)
    
    agent = EmbeddingAgent()
    status = agent.get_status()
    
    print(f"\n📊 Status:")
    print(f"   Model: {status['model']}")
    print(f"   Loaded: {'✅' if status['model_loaded'] else '❌'}")
    
    if not status['model_loaded']:
        print("\n⚠️ Install: pip install sentence-transformers")
        return
        
    # Index some content
    print("\n📝 Indexing test content...")
    await agent.index_text("doc1", "AZIREM is a sovereign AI orchestration system")
    await agent.index_text("doc2", "The Scanner agent discovers files on disk")
    await agent.index_text("doc3", "Voice cloning uses XTTS for realistic speech")
    await agent.index_text("doc4", "The dashboard provides real-time telemetry")
    
    print(f"   Indexed: {len(agent.index)} items")
    
    # Search
    print("\n🔍 Searching for 'AI system orchestration'...")
    results = await agent.search("AI system orchestration", top_k=3)
    
    for i, r in enumerate(results):
        print(f"   {i+1}. [{r['similarity']:.3f}] {r['text'][:40]}...")
        
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
