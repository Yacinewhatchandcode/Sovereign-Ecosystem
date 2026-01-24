# AZIREM Memory Zone

This zone contains the memory and knowledge systems for agents.

## Purpose

- **Store** agent conversations and learnings
- **Index** knowledge for retrieval (RAG)
- **Persist** cross-session state

## Structure

```
memory/
├── vector_store/           # ChromaDB/FAISS indexes
├── conversation_logs/      # Session histories
├── knowledge_base/         # Extracted knowledge items
└── memory_manager.py       # Memory access layer
```

## Rule

**Memory is append-only.** Never delete or overwrite existing memories.
