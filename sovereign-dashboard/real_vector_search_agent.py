#!/usr/bin/env python3
"""
🔍 VECTOR SEARCH AGENT - Semantic Search with ChromaDB
=======================================================
Vector database integration for semantic code search.
Implements semantic indexing and search capabilities.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not installed. Run: pip install chromadb")


@dataclass
class SearchHit:
    """Search result hit."""
    document: str
    distance: float
    metadata: Dict
    snippet: str


class RealVectorSearchAgent:
    """
    Semantic search agent using ChromaDB vector database.
    Enables semantic code search across codebase.
    """
    
    def __init__(self, broadcast_callback=None, persist_directory: str = None):
        self.broadcast_callback = broadcast_callback
        self.persist_dir = persist_directory or ".chromadb"
        
        if not CHROMA_AVAILABLE:
            raise RuntimeError("ChromaDB not available. Install: pip install chromadb")
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_dir
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            metadata={"description": "Code semantic search"}
        )
        
    async def broadcast(self, event_type: str, data: dict):
        """Broadcast event."""
        if self.broadcast_callback:
            await self.broadcast_callback(event_type, {
                "agent_id": "vector_search",
                "agent_name": "Vector Search Agent",
                "icon": "🔍",
                "timestamp": datetime.now().isoformat(),
                **data
            })
    
    async def semantic_indexing(self, documents: List[Dict]) -> dict:
        """
        Index documents with vector embeddings.
        
        Args:
            documents: List of dicts with 'id', 'text', and 'metadata'
        
        Returns:
            Indexing statistics
        """
        await self.broadcast("activity", {
            "message": f"🔍 Indexing {len(documents)} documents..."
        })
        
        # Prepare data for ChromaDB
        ids = [doc['id'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        # Add to collection (ChromaDB handles embedding automatically)
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        # Persist to disk
        self.client.persist()
        
        result = {
            "indexed": len(documents),
            "collection": self.collection.name,
            "total_docs": self.collection.count()
        }
        
        await self.broadcast("indexing_complete", result)
        
        return result
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchHit]:
        """
        Perform semantic search across indexed documents.
        
        Args:
            query: Search query (natural language)
            limit: Max results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of search hits with relevance scores
        """
        await self.broadcast("activity", {
            "message": f"🔍 Searching: {query[:50]}..."
        })
        
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=filter_metadata  # Optional filtering
        )
        
        # Parse results
        hits = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                hit = SearchHit(
                    document=results['documents'][0][i],
                    distance=results['distances'][0][i],
                    metadata=results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                    snippet=results['documents'][0][i][:200]
                )
                hits.append(hit)
        
        await self.broadcast("search_complete", {
            "query": query,
            "results": len(hits)
        })
        
        return hits
    
    async def index_codebase(self, root_path: str) -> dict:
        """Index entire codebase for semantic search."""
        root = Path(root_path)
        
        # Find all code files
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        code_files = []
        for ext in extensions:
            code_files.extend(root.rglob(f"*{ext}"))
        
        # Prepare documents
        documents = []
        for i, file_path in enumerate(code_files[:1000]):  # Limit to 1000 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create document with metadata
                documents.append({
                    'id': f"file_{i}",
                    'text': content,
                    'metadata': {
                        'path': str(file_path.relative_to(root)),
                        'extension': file_path.suffix,
                        'size': len(content)
                    }
                })
            except Exception as e:
                print(f"⚠️ Skip {file_path}: {e}")
        
        # Index all documents
        result = await self.semantic_indexing(documents)
        
        return result
    
    def get_stats(self) -> dict:
        """Get collection statistics."""
        return {
            "collection": self.collection.name,
            "total_documents": self.collection.count(),
            "persist_directory": self.persist_dir
        }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

async def test_vector_search():
    """Test vector search agent."""
    print("🔍 Testing Vector Search Agent...")
    
    if not CHROMA_AVAILABLE:
        print("❌ ChromaDB not available - skipping test")
        return
    
    agent = RealVectorSearchAgent(persist_directory=".test_chromadb")
    
    # Test 1: Index some documents
    docs = [
        {
            'id': 'doc1',
            'text': 'Python function to process data using pandas',
            'metadata': {'type': 'function', 'lang': 'python'}
        },
        {
            'id': 'doc2',
            'text': 'JavaScript async function for API calls',
            'metadata': {'type': 'function', 'lang': 'javascript'}
        },
        {
            'id': 'doc3',
            'text': 'React component for user authentication',
            'metadata': {'type': 'component', 'lang': 'javascript'}
        }
    ]
    
    result = await agent.semantic_indexing(docs)
    print(f"✅ Indexed {result['indexed']} documents")
    
    # Test 2: Semantic search
    hits = await agent.semantic_search("authentication", limit=5)
    print(f"✅ Found {len(hits)} results for 'authentication'")
    if hits:
        print(f"   Top result: {hits[0].snippet[:60]}... (distance: {hits[0].distance:.3f})")
    
    # Test 3: Stats
    stats = agent.get_stats()
    print(f"✅ Collection stats: {stats['total_documents']} documents")
    
    print("\n✅ Vector Search Agent tests complete!")


if __name__ == "__main__":
    asyncio.run(test_vector_search())
