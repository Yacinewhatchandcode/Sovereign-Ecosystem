# 🌌 AZIREM SOVEREIGN DISCOVERY ECOSYSTEM

**Version 2.0** | Built: 2026-01-18  
**Rule: inventory → map → freeze → orchestrate → intelligence**

---

## 🚀 Quick Start (72-Hour Checklist)

```bash
# 1. Check system status
python3 azirem_cli.py status

# 2. Run full pipeline (scan → classify → extract → deps → secrets → summarize)
python3 azirem_cli.py pipeline /Users/yacinebenhamou/aSiReM --max-files 10000

# 3. Start Matrix UI + REST API
python3 azirem_cli.py serve --port 8080

# Open browser: http://localhost:8080
```

---

## 📁 Repository Structure

```
azirem/
├── azirem_cli.py              # 🎯 Main CLI entry point
├── AZIREM_CORE.md             # Master documentation (this file)
│
├── azirem_discovery/          # Phase 1: Read-Only Inventory
│   ├── scanner.py             # Basic scanner
│   ├── discovery_cli.py       # Enhanced discovery CLI
│   ├── inventory_frozen.json  # Frozen manifest
│   └── README.md
│
├── azirem_registry/           # Phase 2: Agent Registry
│   ├── registry_manager.py    # Registry builder
│   ├── agents_frozen.json     # Frozen agent manifest
│   └── README.md
│
├── azirem_agents/             # Phase 3: Core Agents (6 types)
│   ├── core_agents.py         # All 6 agent implementations
│   └── README.md
│
├── azirem_orchestration/      # Phase 4: Orchestration
│   ├── master_orchestrator.py # Original orchestrator
│   ├── pipeline_orchestrator.py # Full pipeline
│   ├── api_server.py          # REST API (Flask)
│   └── README.md
│
├── azirem_memory/             # Phase 5: Memory (future)
│   └── README.md
│
├── web-ui/                    # Matrix UI Frontend
│   └── index.html             # Single-page app
│
└── cold_azirem/               # Original codebase (untouched)
    └── ...
```

---

## 🤖 Core Agent Types (6)

| # | Agent Type | Purpose | Output |
|---|------------|---------|--------|
| 1 | **Scanner** | Read-only file discovery | File list with metadata |
| 2 | **Classifier** | Tag files by type | Tags: agent/script/api/config/... |
| 3 | **Extractor** | Extract code signatures | Functions, classes, imports |
| 4 | **Dependency Resolver** | Parse package files | Project dependencies |
| 5 | **Secrets** | Find potential secrets | Line numbers only (NEVER content!) |
| 6 | **Summarizer** | Generate descriptions | NL summaries, embedding-ready |

---

## 🔄 Pipeline Flow

```
                    ┌─────────────┐
                    │   SCAN      │  Read-only discovery
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  CLASSIFY   │  Tag by patterns
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
   │   EXTRACT   │  │    DEPS     │  │   SECRETS   │
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │  SUMMARIZE  │  Generate descriptions
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    MERGE    │  → registry.json
                    └─────────────┘
```

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System status |
| GET | `/api/search?q=...&tag=...` | Search files |
| GET | `/api/file/<path>` | File details |
| GET | `/api/file/<path>/content` | File content (5KB max) |
| GET | `/api/tags` | All tags with counts |
| GET | `/api/projects` | Projects with dependencies |
| GET | `/api/agents` | Registered agents |
| GET | `/api/agents/status` | Live agent status |
| GET | `/api/secrets/summary` | Secrets summary (no values!) |
| GET | `/api/matrix` | Matrix view data |
| GET | `/api/export/csv` | Export as CSV |
| GET | `/api/export/json` | Export as JSON |

---

## 📊 Classification Tags

| Tag | Pattern Examples |
|-----|-----------------|
| `agent` | `*_agent.py`, class with `Agent` |
| `script` | `run*.py`, `demo*.py`, `if __name__` |
| `lib` | `*_utils.py`, `helper*.py` |
| `config` | `.yaml`, `.env`, `requirements.txt` |
| `api` | `*route*.py`, `@app.get`, OpenAPI |
| `frontend` | `.html`, `.jsx`, `.vue`, `.css` |
| `backend` | `server*.py`, `flask`, `express` |
| `docs` | `.md`, `README*`, `LICENSE` |
| `test` | `test_*.py`, `*_test.py` |
| `secret-suspect` | `.pem`, `.key`, `API_KEY=` |
| `db` | `.sql`, `migrations/*`, `model*.py` |

---

## 🔒 Security Rules (MUST DO)

1. **Scanner is READ-ONLY** - Never modifies source files
2. **Secrets agent NEVER stores content** - Only line numbers and types
3. **No raw secrets in registry** - Hash references only
4. **Provenance tracking** - Every entry has `scanner:sha256`, timestamps
5. **Mount read-only** if possible when scanning external drives

---

## 📈 Current State

```
✅ Discovery:     72 files inventoried
✅ Pipeline:      500 files processed  
✅ Agents:        11 registered (3 strategic, 2 execution, 6 specialist)
✅ Projects:      3 dependency trees resolved
✅ Tags:          12 classification types
✅ API:           12 endpoints ready
✅ Matrix UI:     Single-page app ready
```

---

## 🔮 Next Steps (Progressive Enrichment)

### Phase 6: Memory Persistence
- [ ] ChromaDB vector store for embeddings
- [ ] Conversation logs
- [ ] Cross-session state

### Phase 7: MCP Tool Integration
- [ ] GitHub MCP for code operations
- [ ] Supabase MCP for database
- [ ] Custom domain tools

### Phase 8: Intelligence Layer
- [ ] LLM-powered summarization
- [ ] Semantic search (embeddings)
- [ ] Auto-documentation generation

---

## 🎯 Commands Reference

```bash
# Status
python3 azirem_cli.py status

# Discovery scan
python3 azirem_cli.py scan /path --max-files 10000

# Full pipeline
python3 azirem_cli.py pipeline /path --output /tmp/results

# Build agent registry
python3 azirem_cli.py registry

# Start server
python3 azirem_cli.py serve --port 8080

# Test agents
python3 azirem_cli.py agents
```

---

**Status**: ✅ PRODUCTION READY  
**Version**: 2.0.0  
**Last Updated**: 2026-01-18T13:44:00Z
