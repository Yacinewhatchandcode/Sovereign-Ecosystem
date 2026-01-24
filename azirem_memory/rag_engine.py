#!/usr/bin/env python3
"""
AZIREM RAG Engine
=================
Retrieval-Augmented Generation for querying documentation.
Uses ChromaDB for vector storage and Ollama for generation.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

# Try to import chromadb, fall back to simple search if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not available. Using keyword-based search.")


# ============================================================================
# CONFIGURATION
# ============================================================================

CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200
TOP_K = 5


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Document:
    """A document chunk for RAG."""
    id: str
    content: str
    source: str
    chunk_index: int
    metadata: Dict = field(default_factory=dict)


@dataclass
class SearchResult:
    """A search result with relevance score."""
    document: Document
    score: float
    highlights: List[str] = field(default_factory=list)


@dataclass
class RAGResponse:
    """Response from RAG query."""
    answer: str
    sources: List[str]
    confidence: float
    retrieved_chunks: int


# ============================================================================
# TEXT PROCESSING
# ============================================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, 
               overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence/paragraph boundary
        if end < len(text):
            # Look for sentence end
            for delim in ['\n\n', '\n', '. ', '! ', '? ']:
                last_delim = text[start:end].rfind(delim)
                if last_delim > chunk_size // 2:
                    end = start + last_delim + len(delim)
                    break
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text."""
    # Simple keyword extraction
    text_lower = text.lower()
    
    # Remove common words
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                 'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
                 'by', 'from', 'as', 'into', 'through', 'during', 'before',
                 'after', 'above', 'below', 'between', 'under', 'again', 'and',
                 'but', 'or', 'nor', 'so', 'yet', 'both', 'each', 'few', 'more',
                 'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own',
                 'same', 'than', 'too', 'very', 'just', 'also', 'now', 'here',
                 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'which',
                 'this', 'that', 'these', 'those', 'what', 'who', 'whom', 'it'}
    
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    keywords = [w for w in words if w not in stopwords]
    
    # Get most common
    freq = defaultdict(int)
    for w in keywords:
        freq[w] += 1
    
    sorted_keywords = sorted(freq.items(), key=lambda x: -x[1])
    return [k for k, _ in sorted_keywords[:20]]


# ============================================================================
# SIMPLE SEARCH (No ChromaDB)
# ============================================================================

class SimpleSearchEngine:
    """Simple keyword-based search engine."""
    
    def __init__(self):
        self.documents: List[Document] = []
        self.inverted_index: Dict[str, set] = defaultdict(set)
    
    def add_document(self, doc: Document):
        """Add a document to the index."""
        doc_idx = len(self.documents)
        self.documents.append(doc)
        
        # Build inverted index
        words = set(re.findall(r'\b[a-z]{3,}\b', doc.content.lower()))
        for word in words:
            self.inverted_index[word].add(doc_idx)
    
    def search(self, query: str, top_k: int = TOP_K) -> List[SearchResult]:
        """Search for documents matching query."""
        query_words = set(re.findall(r'\b[a-z]{3,}\b', query.lower()))
        
        if not query_words:
            return []
        
        # Score documents
        scores = defaultdict(float)
        for word in query_words:
            for doc_idx in self.inverted_index.get(word, []):
                scores[doc_idx] += 1.0 / len(query_words)
        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        
        results = []
        for doc_idx, score in ranked:
            doc = self.documents[doc_idx]
            results.append(SearchResult(
                document=doc,
                score=score,
                highlights=self._extract_highlights(doc.content, query_words)
            ))
        
        return results
    
    def _extract_highlights(self, content: str, query_words: set) -> List[str]:
        """Extract highlighted snippets."""
        highlights = []
        sentences = re.split(r'[.!?]\s+', content)
        
        for sentence in sentences[:10]:
            sentence_lower = sentence.lower()
            if any(w in sentence_lower for w in query_words):
                highlights.append(sentence[:200])
                if len(highlights) >= 3:
                    break
        
        return highlights


# ============================================================================
# RAG ENGINE
# ============================================================================

class RAGEngine:
    """RAG engine for document retrieval and generation."""
    
    def __init__(self, persist_dir: str = "/tmp/azirem_rag"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize search engine
        if CHROMA_AVAILABLE:
            self.client = chromadb.Client(Settings(
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name="azirem_docs",
                metadata={"description": "AZIREM documentation"}
            )
            self.search_engine = None
        else:
            self.client = None
            self.collection = None
            self.search_engine = SimpleSearchEngine()
        
        self.documents: Dict[str, Document] = {}
    
    def index_file(self, filepath: str) -> int:
        """Index a file into the RAG store."""
        path = Path(filepath)
        if not path.exists():
            return 0
        
        try:
            content = path.read_text(errors='ignore')
        except:
            return 0
        
        # Chunk the content
        chunks = chunk_text(content)
        
        indexed = 0
        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{filepath}_{i}".encode()).hexdigest()
            
            doc = Document(
                id=doc_id,
                content=chunk,
                source=filepath,
                chunk_index=i,
                metadata={
                    "filename": path.name,
                    "extension": path.suffix,
                    "keywords": extract_keywords(chunk)[:10],
                }
            )
            
            self.documents[doc_id] = doc
            
            if CHROMA_AVAILABLE:
                self.collection.add(
                    ids=[doc_id],
                    documents=[chunk],
                    metadatas=[{
                        "source": filepath,
                        "chunk_index": i,
                        "filename": path.name,
                    }]
                )
            else:
                self.search_engine.add_document(doc)
            
            indexed += 1
        
        return indexed
    
    def index_directory(self, directory: str, extensions: List[str] = None) -> int:
        """Index all files in a directory."""
        if extensions is None:
            extensions = ['.md', '.py', '.txt', '.rst']
        
        path = Path(directory)
        total = 0
        
        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                # Skip large files and common exclusions
                if file.stat().st_size > 500_000:
                    continue
                if any(p in str(file) for p in ['node_modules', '.git', '__pycache__', '.venv']):
                    continue
                
                total += self.index_file(str(file))
        
        return total
    
    def search(self, query: str, top_k: int = TOP_K) -> List[SearchResult]:
        """Search for relevant documents."""
        if CHROMA_AVAILABLE:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            search_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                if doc_id in self.documents:
                    doc = self.documents[doc_id]
                else:
                    doc = Document(
                        id=doc_id,
                        content=results['documents'][0][i],
                        source=results['metadatas'][0][i].get('source', ''),
                        chunk_index=results['metadatas'][0][i].get('chunk_index', 0)
                    )
                
                score = 1.0 - (results['distances'][0][i] if results['distances'] else 0)
                search_results.append(SearchResult(
                    document=doc,
                    score=score,
                    highlights=[]
                ))
            
            return search_results
        else:
            return self.search_engine.search(query, top_k)
    
    def query(self, question: str, 
              ollama_client=None,
              model: str = "llama3.1:8b") -> RAGResponse:
        """Query the RAG system with a question."""
        
        # Retrieve relevant documents
        results = self.search(question, top_k=TOP_K)
        
        if not results:
            return RAGResponse(
                answer="No relevant documents found.",
                sources=[],
                confidence=0.0,
                retrieved_chunks=0
            )
        
        # Build context from retrieved docs
        context_parts = []
        sources = set()
        for r in results:
            context_parts.append(f"[Source: {r.document.source}]\n{r.document.content}")
            sources.add(r.document.source)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate answer with LLM if available
        if ollama_client:
            prompt = f"""Based on the following context, answer the question.
If the context doesn't contain enough information, say so.
Cite sources when possible.

Context:
{context}

Question: {question}

Answer:"""
            
            response = ollama_client.generate(
                prompt=prompt,
                model=model,
                system="You are a helpful assistant that answers questions based on provided context. Be concise but thorough."
            )
            
            if response.success:
                return RAGResponse(
                    answer=response.content,
                    sources=list(sources),
                    confidence=sum(r.score for r in results) / len(results),
                    retrieved_chunks=len(results)
                )
        
        # Fallback: return context summary
        return RAGResponse(
            answer=f"Found {len(results)} relevant documents:\n" + 
                   "\n".join(f"- {Path(s).name}" for s in list(sources)[:5]),
            sources=list(sources),
            confidence=sum(r.score for r in results) / len(results),
            retrieved_chunks=len(results)
        )
    
    def get_stats(self) -> Dict:
        """Get RAG engine stats."""
        return {
            "total_documents": len(self.documents),
            "chroma_available": CHROMA_AVAILABLE,
            "persist_dir": str(self.persist_dir),
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    print("=" * 60)
    print("🔍 AZIREM RAG ENGINE")
    print("=" * 60)
    
    # Initialize engine
    engine = RAGEngine()
    print(f"\nChromaDB available: {CHROMA_AVAILABLE}")
    
    # Index markdown files from inventory
    md_inv_path = Path("/tmp/azirem_md_inventory.json")
    if md_inv_path.exists():
        with open(md_inv_path) as f:
            md_inv = json.load(f)
        
        files = md_inv.get("files", [])[:500]  # Limit for demo
        print(f"\nIndexing {len(files)} markdown files...")
        
        total = 0
        for file_info in files:
            indexed = engine.index_file(file_info.get("path", ""))
            total += indexed
        
        print(f"✅ Indexed {total} chunks from {len(files)} files")
    else:
        print("⚠️ MD inventory not found. Run pipeline first.")
    
    # Demo search
    print("\n" + "-" * 60)
    print("🧪 DEMO SEARCH")
    print("-" * 60)
    
    queries = [
        "How to set up voice cloning?",
        "What is the agent architecture?",
        "How to deploy to production?",
    ]
    
    for query in queries:
        print(f"\n🔹 Query: {query}")
        results = engine.search(query, top_k=3)
        
        for r in results:
            print(f"   [{r.score:.2f}] {Path(r.document.source).name}")
            if r.highlights:
                print(f"         → {r.highlights[0][:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ RAG engine ready!")
    print(f"   Documents: {engine.get_stats()['total_documents']}")


if __name__ == "__main__":
    main()
