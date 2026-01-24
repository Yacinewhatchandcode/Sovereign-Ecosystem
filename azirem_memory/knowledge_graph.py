#!/usr/bin/env python3
"""
AZIREM Knowledge Graph Builder
==============================
Builds a knowledge graph from discovered markdown files.
Extracts entities, relationships, and creates topic clusters.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field, asdict


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Entity:
    """A knowledge entity (project, technology, concept)."""
    name: str
    entity_type: str  # project, technology, concept, file, person
    mentions: int = 0
    files: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    context: str = ""


@dataclass 
class Topic:
    """A topic cluster."""
    name: str
    keywords: List[str]
    files: List[str] = field(default_factory=list)
    entity_count: int = 0


@dataclass
class KnowledgeGraph:
    """The complete knowledge graph."""
    created_at: str
    total_documents: int
    entities: Dict[str, Entity]
    topics: Dict[str, Topic]
    relationships: List[Tuple[str, str, str]]  # (entity1, relation, entity2)
    

# ============================================================================
# ENTITY EXTRACTION
# ============================================================================

class EntityExtractor:
    """Extract entities from markdown content."""
    
    # Known projects/technologies
    KNOWN_PROJECTS = {
        "PrimeAI", "AZIREM", "Fortress", "Duix-Avatar", "VoiceCloning",
        "OptimusAI", "LuckLoop", "nobot.news", "Lisa", "PRIMEYE",
        "Cold Azirem", "BumbleBee", "Spectra", "ComfyUI", "AnimateDiff"
    }
    
    KNOWN_TECH = {
        "Ollama", "LangGraph", "CrewAI", "FAISS", "ChromaDB", "Flask",
        "FastAPI", "React", "Next.js", "Vite", "Docker", "AWS", "S3",
        "OpenAI", "Claude", "GPT-4", "Llama", "Whisper", "XTTS",
        "WebSocket", "MCP", "RAG", "PyTorch", "TensorFlow", "F5-TTS"
    }
    
    CONCEPT_PATTERNS = [
        r'\*\*([A-Z][a-zA-Z\s]+)\*\*',  # **Bold Terms**
        r'`([A-Za-z_]+)`',  # `code terms`
        r'#+\s+(.+?)[\n$]',  # # Headers
    ]
    
    def extract_entities(self, content: str, filename: str) -> List[Entity]:
        """Extract entities from content."""
        entities = []
        content_lower = content.lower()
        
        # Find known projects
        for project in self.KNOWN_PROJECTS:
            if project.lower() in content_lower:
                entities.append(Entity(
                    name=project,
                    entity_type="project",
                    mentions=content_lower.count(project.lower()),
                    files=[filename]
                ))
        
        # Find known technologies
        for tech in self.KNOWN_TECH:
            if tech.lower() in content_lower:
                entities.append(Entity(
                    name=tech,
                    entity_type="technology",
                    mentions=content_lower.count(tech.lower()),
                    files=[filename]
                ))
        
        # Extract concepts from headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for header in headers[:10]:
            clean = header.strip('# *`')
            if len(clean) > 3 and len(clean) < 60:
                entities.append(Entity(
                    name=clean,
                    entity_type="concept",
                    mentions=1,
                    files=[filename]
                ))
        
        return entities
    
    def extract_relationships(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Pattern: "X integrates with Y", "X uses Y", etc.
        patterns = [
            (r'(\w+)\s+integrates?\s+with\s+(\w+)', 'integrates_with'),
            (r'(\w+)\s+uses?\s+(\w+)', 'uses'),
            (r'(\w+)\s+depends?\s+on\s+(\w+)', 'depends_on'),
            (r'(\w+)\s+connects?\s+to\s+(\w+)', 'connects_to'),
        ]
        
        for pattern, rel_type in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match[0]) > 2 and len(match[1]) > 2:
                    relationships.append((match[0], rel_type, match[1]))
        
        return relationships


# ============================================================================
# TOPIC CLUSTERING
# ============================================================================

class TopicClusterer:
    """Cluster documents into topics."""
    
    TOPIC_KEYWORDS = {
        "AI Agents": ["agent", "multi-agent", "orchestrat", "autonomous", "agentic"],
        "Voice & Audio": ["voice", "audio", "tts", "speech", "whisper", "cloning"],
        "Video Generation": ["video", "animation", "diffusion", "comfyui", "animate"],
        "Infrastructure": ["docker", "deploy", "aws", "server", "database", "api"],
        "UI/UX": ["ui", "frontend", "react", "dashboard", "interface", "design"],
        "Security": ["security", "auth", "rbac", "gate", "policy", "secret"],
        "Quality Assurance": ["test", "qa", "quality", "bug", "validation"],
        "Documentation": ["readme", "guide", "doc", "spec", "plan"],
        "Machine Learning": ["model", "training", "inference", "gpu", "cuda", "llm"],
        "Search & RAG": ["search", "rag", "retrieval", "embedding", "vector", "faiss"],
    }
    
    def classify_document(self, content: str, filename: str) -> List[str]:
        """Classify a document into topics."""
        content_lower = content.lower()
        topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score >= 2:  # At least 2 keyword matches
                topics.append(topic)
        
        return topics if topics else ["General"]


# ============================================================================
# KNOWLEDGE GRAPH BUILDER
# ============================================================================

class KnowledgeGraphBuilder:
    """Build knowledge graph from markdown files."""
    
    def __init__(self):
        self.extractor = EntityExtractor()
        self.clusterer = TopicClusterer()
        self.entities: Dict[str, Entity] = {}
        self.topics: Dict[str, Topic] = defaultdict(
            lambda: Topic(name="", keywords=[], files=[])
        )
        self.relationships: List[Tuple[str, str, str]] = []
    
    def add_document(self, filepath: str, content: str):
        """Process a single document."""
        filename = Path(filepath).name
        
        # Extract entities
        doc_entities = self.extractor.extract_entities(content, filepath)
        for entity in doc_entities:
            if entity.name in self.entities:
                self.entities[entity.name].mentions += entity.mentions
                if filepath not in self.entities[entity.name].files:
                    self.entities[entity.name].files.append(filepath)
            else:
                self.entities[entity.name] = entity
        
        # Extract relationships
        doc_relationships = self.extractor.extract_relationships(content)
        self.relationships.extend(doc_relationships)
        
        # Classify into topics
        doc_topics = self.clusterer.classify_document(content, filename)
        for topic_name in doc_topics:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(
                    name=topic_name,
                    keywords=self.clusterer.TOPIC_KEYWORDS.get(topic_name, []),
                )
            if filepath not in self.topics[topic_name].files:
                self.topics[topic_name].files.append(filepath)
    
    def build(self, md_files: List[Dict]) -> KnowledgeGraph:
        """Build the complete knowledge graph."""
        print(f"📊 Building knowledge graph from {len(md_files)} documents...")
        
        for file_info in md_files:
            filepath = file_info.get("path", "")
            try:
                content = Path(filepath).read_text(errors='ignore')
                self.add_document(filepath, content)
            except Exception as e:
                continue
        
        # Calculate topic entity counts
        for topic in self.topics.values():
            topic.entity_count = len([
                e for e in self.entities.values()
                if any(f in topic.files for f in e.files)
            ])
        
        # Build graph
        graph = KnowledgeGraph(
            created_at=datetime.now().isoformat(),
            total_documents=len(md_files),
            entities=self.entities,
            topics=dict(self.topics),
            relationships=list(set(self.relationships))[:100],
        )
        
        return graph
    
    def to_dict(self, graph: KnowledgeGraph) -> Dict:
        """Convert graph to serializable dict."""
        return {
            "created_at": graph.created_at,
            "total_documents": graph.total_documents,
            "summary": {
                "total_entities": len(graph.entities),
                "total_topics": len(graph.topics),
                "total_relationships": len(graph.relationships),
            },
            "entities": {
                name: {
                    "name": e.name,
                    "type": e.entity_type,
                    "mentions": e.mentions,
                    "files": e.files[:10],
                }
                for name, e in sorted(
                    graph.entities.items(), 
                    key=lambda x: -x[1].mentions
                )[:50]
            },
            "topics": {
                name: {
                    "name": t.name,
                    "keywords": t.keywords,
                    "file_count": len(t.files),
                    "entity_count": t.entity_count,
                }
                for name, t in graph.topics.items()
            },
            "relationships": graph.relationships[:50],
        }


# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

class SemanticSearch:
    """Simple keyword-based semantic search (no embeddings required)."""
    
    def __init__(self, documents: List[Dict]):
        self.documents = documents
        self.index = self._build_index()
    
    def _build_index(self) -> Dict[str, Set[int]]:
        """Build inverted index."""
        index = defaultdict(set)
        
        for i, doc in enumerate(self.documents):
            # Index path
            path = doc.get("path", "").lower()
            for word in re.findall(r'\w+', path):
                if len(word) > 2:
                    index[word].add(i)
            
            # Index summary
            summary = doc.get("summary", "").lower()
            for word in re.findall(r'\w+', summary):
                if len(word) > 2:
                    index[word].add(i)
        
        return dict(index)
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search documents."""
        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
        
        if not query_words:
            return []
        
        # Score documents
        scores = defaultdict(int)
        for word in query_words:
            for doc_idx in self.index.get(word, []):
                scores[doc_idx] += 1
        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        
        # Return top results
        results = []
        for doc_idx, score in ranked[:limit]:
            doc = self.documents[doc_idx].copy()
            doc["relevance_score"] = score / len(query_words)
            results.append(doc)
        
        return results


# ============================================================================
# CLI
# ============================================================================

def main():
    print("=" * 60)
    print("🧠 AZIREM KNOWLEDGE GRAPH BUILDER")
    print("=" * 60)
    
    # Load MD inventory
    md_inv_path = Path("/tmp/azirem_md_inventory.json")
    if not md_inv_path.exists():
        print("❌ MD inventory not found. Run the pipeline first.")
        return
    
    with open(md_inv_path) as f:
        md_inv = json.load(f)
    
    md_files = md_inv.get("files", [])
    print(f"📄 Found {len(md_files)} markdown files")
    
    # Build knowledge graph
    builder = KnowledgeGraphBuilder()
    graph = builder.build(md_files)
    graph_dict = builder.to_dict(graph)
    
    # Save graph
    output_path = Path("/tmp/azirem_knowledge_graph.json")
    with open(output_path, 'w') as f:
        json.dump(graph_dict, f, indent=2)
    
    print(f"\n✅ Knowledge graph saved: {output_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 KNOWLEDGE GRAPH SUMMARY")
    print("=" * 60)
    
    print(f"\nEntities: {graph_dict['summary']['total_entities']}")
    print(f"Topics: {graph_dict['summary']['total_topics']}")
    print(f"Relationships: {graph_dict['summary']['total_relationships']}")
    
    print("\n🏷️ TOP ENTITIES (by mentions):")
    for name, entity in list(graph_dict['entities'].items())[:15]:
        print(f"   {entity['type'][:7]:8} | {entity['mentions']:3}x | {name}")
    
    print("\n📁 TOPIC CLUSTERS:")
    for name, topic in graph_dict['topics'].items():
        print(f"   {name}: {topic['file_count']} files, {topic['entity_count']} entities")
    
    # Demo semantic search
    print("\n" + "=" * 60)
    print("🔍 DEMO SEARCH")
    print("=" * 60)
    
    search = SemanticSearch(md_files)
    
    queries = ["voice cloning pipeline", "multi-agent orchestration", "video generation"]
    for query in queries:
        results = search.search(query, limit=3)
        print(f"\nQuery: \"{query}\"")
        for r in results:
            print(f"   [{r['relevance_score']:.1f}] {r['name']}")


if __name__ == "__main__":
    main()
