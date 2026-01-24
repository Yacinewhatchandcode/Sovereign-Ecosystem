# 📊 UI Pages & API Endpoint Mapping

## Complete Analysis of Frontend API Usage

### Main Dashboard (index.html)

#### 1. **Main Dashboard View** (Default Page)
**API Endpoints Used: 3**
- `GET /api/agents/config` - Load agent list on startup
- `GET /api/status` - System status check
- `WS /ws/stream` - WebSocket for real-time updates

#### 2. **Quick Actions Panel** (Left Sidebar)
**API Endpoints Used: 8**
- `POST /api/speak` - "aSiReM Speak" button
- `POST /api/veo3/generate` - "Veo3 Generate" button  
- `GET /api/veo3/credits` - "Veo3 Credits" button
- `POST /api/podcast/ask` - "AZIREM Podcast" button
- `WS start_integrated_scan` - "Integrated Scan" button
- `WS get_bytebot_vnc` - ByteBot VNC initialization
- `POST /api/run-pipeline` - "Trigger scan cycle" button
- `POST /api/web-search` - "Web Search" button

#### 3. **Evolution Panel** (Right Side)
**API Endpoints Used: 4**
- `POST /api/run-pipeline` - Run Evolution button
- `POST /api/evolution` - Evolution trigger
- `GET /api/discoveries` - Get discovered patterns
- `GET /api/patterns` - Get pattern statistics

#### 4. **Agent Viewer Modal** (Click on any agent)
**API Endpoints Used: 2**
- `WS start_live_capture` - Start screen capture
- `WS stop_live_capture` - Stop screen capture

#### 5. **AZIREM Podcast Modal**
**API Endpoints Used: 2**
- `POST /api/podcast/ask` - Send question
- `WS podcast_ask` - WebSocket alternative

#### 6. **Sovereign API Workbench** (Bottom Panel)
**API Endpoints Used: 31** (All available endpoints)

**Core System:**
- `POST /api/mesh/query` - Sovereign mesh query
- `GET /api/status` - System status
- `POST /api/run-pipeline` - Full pipeline
- `POST /api/evolution` - Evolution trigger
- `POST /api/web-search` - Web search
- `GET /api/discoveries` - Discoveries list
- `GET /api/patterns` - Pattern stats

**Memory & Embedding:**
- `POST /api/memory/store` - Store in memory
- `GET /api/memory/search` - Search memory
- `POST /api/embedding/index` - Index content
- `GET /api/embedding/search` - Semantic search

**Documentation:**
- `POST /api/docgen/readme` - Generate README
- `POST /api/docgen/api` - Generate API docs

**MCP Integration:**
- `POST /api/mcp/github` - GitHub MCP
- `POST /api/mcp/perplexity` - Perplexity MCP

**Extended Agents:**
- `GET /api/agents/extended` - Extended agents status

**Video Generation:**
- `GET /api/veo3/credits` - Veo3 credits
- `POST /api/veo3/generate` - Generate video

**Agent Communication:**
- `GET /api/agents/all` - All agents
- `GET /api/agents/communications` - Agent chat history
- `POST /api/agents/message` - Send inter-agent message
- `GET /api/agents/capabilities` - Capability matrix
- `GET /api/agents/config` - Agent configuration

**Feature Scanner:**
- `POST /api/features/scan` - Trigger scan
- `GET /api/features/all` - All features
- `GET /api/features/summary` - Feature summary

**Podcast:**
- `POST /api/podcast/ask` - Podcast interaction

---

## Summary by Page/Section

| Page/Section | API Endpoints | WebSocket Messages |
|--------------|---------------|-------------------|
| Main Dashboard | 3 | 1 (connection) |
| Quick Actions Panel | 5 | 3 |
| Evolution Panel | 4 | 0 |
| Agent Viewer Modal | 0 | 2 |
| AZIREM Podcast Modal | 1 | 1 |
| API Workbench | 31 | 0 |
| **TOTAL UNIQUE** | **31** | **7** |

---

## WebSocket Messages Used

1. `start_integrated_scan` - Trigger ByteBot scan
2. `get_bytebot_vnc` - Get VNC stream URL
3. `podcast_ask` - Podcast question
4. `run_pipeline` - Run full pipeline
5. `web_search` - Web search
6. `start_live_capture` - Start screen capture
7. `stop_live_capture` - Stop screen capture

---

## API Endpoint Categories

### ✅ Implemented in Minimal Backend (5)
- `GET /api/agents/config`
- `GET /api/veo3/credits`
- `POST /api/veo3/generate`
- `POST /api/speak`
- `WS /ws/stream`

### ⚠️ Not Yet in Minimal Backend (26)
- All Memory/Embedding endpoints (4)
- All Documentation endpoints (2)
- All MCP endpoints (2)
- All Agent Communication endpoints (5)
- All Feature Scanner endpoints (3)
- All Core System endpoints (7)
- Extended agents endpoint (1)
- Podcast endpoint (1)
- Discoveries/Patterns endpoints (2)

---

## Recommendations

### Priority 1: Add Missing Quick Action Endpoints
These are visible buttons that users will click:
1. `POST /api/podcast/ask`
2. `POST /api/run-pipeline`
3. `POST /api/web-search`
4. `POST /api/evolution`

### Priority 2: Add Evolution Panel Endpoints
1. `GET /api/discoveries`
2. `GET /api/patterns`

### Priority 3: Add Agent Communication
1. `GET /api/agents/all`
2. `GET /api/agents/communications`
3. `GET /api/agents/capabilities`

### Priority 4: Add Feature Scanner
1. `POST /api/features/scan`
2. `GET /api/features/all`
3. `GET /api/features/summary`

---

## Current Implementation Status

**Minimal Backend Coverage: 16%** (5 out of 31 endpoints)

**To reach 100% functionality:**
- Need to add 26 more endpoints
- Or update UI to only show working features
- Or extend minimal_backend.py with missing endpoints
