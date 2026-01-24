# 🧬 SOVEREIGN COMMAND CENTER

## Real-Time Autonomous Multi-Agent Streaming Dashboard

![Status](https://img.shields.io/badge/Status-Operational-00ff9d)
![Agents](https://img.shields.io/badge/Agents-13-9f4fff)
![Self-Evolving](https://img.shields.io/badge/Self--Evolving-Yes-00f0ff)

### 🎯 Features

- **Real-Time Video Streaming** - MP4 video with HUD overlay
- **13-Agent Fleet Monitoring** - Live status of all agents
- **Self-Evolving System** - Autonomous pattern discovery and learning
- **WebSocket Telemetry** - Real-time updates every 3 seconds
- **Knowledge Graph Visualization** - Growing knowledge network
- **Evolution Metrics** - Patterns, files, knowledge items tracked
- **Activity Stream** - Live agent activity feed
- **Terminal Log** - System log output

### 🚀 Quick Start

```bash
# Option 1: Use the start script
./start.sh

# Option 2: Manual start
python3 streaming_server.py --port 8082
```

Then open: **http://localhost:8082/**

### 🏗️ Architecture

```
sovereign-dashboard/
├── index.html          # Main dashboard UI
├── streaming_server.py # WebSocket + REST API server
├── start.sh           # Quick start script
└── README.md          # This file
```

### 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System status and metrics |
| GET | `/api/agents` | List all agents |
| GET | `/api/metrics` | Evolution metrics |
| GET | `/api/activities` | Recent activities |
| GET | `/api/knowledge` | Knowledge graph nodes |
| POST | `/api/evolve` | Trigger evolution cycle |
| WS | `/ws/stream` | Real-time WebSocket stream |

### 🤖 Agent Fleet

| Agent | Role | Icon |
|-------|------|------|
| AZIREM | Strategic Master | 🧠 |
| BumbleBee | Execution Master | 🐝 |
| Spectra | Knowledge Master | 🌈 |
| Scanner | Discovery Agent | 📡 |
| Classifier | Tagging Agent | 🏷️ |
| Extractor | Code Analyst | 🔬 |
| Summarizer | NL Generator | 📝 |
| Evolution | Self-Improvement | 🧬 |
| Researcher | Web Search | 🌐 |
| Architect | System Design | 🏗️ |
| DevOps | Deployment | ⚡ |
| QA | Testing | 🧪 |
| Security | Protection | 🔐 |

### 🧬 Evolution Cycle

When triggered, the system runs through 3 phases:

1. **SCAN** - Discover new patterns in the codebase
2. **LEARN** - Extract knowledge from patterns
3. **EVOLVE** - Improve capabilities and possibly spawn new agents

### 🎨 Design

- **Cosmic Dark Theme** - Deep space aesthetic
- **Neon Accents** - Cyan, purple, green, gold
- **Floating Particles** - Animated background
- **Glassmorphism** - Frosted glass panels
- **Micro-Animations** - Smooth transitions

### 🔧 Requirements

- Python 3.8+
- aiohttp (`pip install aiohttp`)

### 📜 License

Part of the Cold Azirem Multi-Agent Ecosystem.

---

*Built with 🧬 by the Sovereign Intelligence*
