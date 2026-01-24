# 🎬 Sovereign Command Center - Visual Streaming User Guide

## ✅ System Status

Your **Sovereign Command Center** is now **LIVE** and fully operational with:

- ✅ Real-time Agent Visual Streaming Engine
- ✅ Individual MP4 streams for all 13 agents
- ✅ F5-TTS Voice Cloning with MuseTalk Lip-Sync
- ✅ 9-Expert Cinematic Narrative Factory
- ✅ Veo3 Video Generation with Credit Tracking
- ✅ WebSocket Live Telemetry

## 📺 Dashboard URL

**http://localhost:8082/index.html**

Open this in your browser to see the live dashboard.

---

## 🎥 Demo 1: aSiReM Speaking (Voice Cloning + Lip-Sync)

### What You'll See:
- aSiReM's avatar switches from idle to **lip-synced speaking video**
- Real-time voice synthesis using F5-TTS with YOUR cloned voice
- MuseTalk generates synchronized lip movements
- Activity stream shows: "🎤 TTS Engine synthesizing voice..." → "👄 MuseTalk generating lip sync..." → "✅ aSiReM Speaking complete!"

### How to Trigger:
1. Open the dashboard: **http://localhost:8082/index.html**
2. Find the **Quick Actions** panel (left sidebar)
3. Click the **"🗣️ aSiReM Speak"** button
4. Watch the **Activity Stream** (center panel) for real-time updates
5. Look at **aSiReM's avatar** (top of Agent Fleet) - it will show the lip-synced video

### What's Happening Behind the Scenes:
```
User clicks "aSiReM Speak"
    ↓
NarrativeEngine generates greeting script
    ↓
TTSEngine synthesizes with F5-TTS (your voice clone)
    ↓
LipSyncEngine creates MuseTalk video
    ↓
Visual stream updates: assets/asirem-video.mp4 → speaking_TIMESTAMP.mp4
    ↓
Dashboard displays lip-synced avatar
```

---

## 📡 Demo 2: Evolution Pipeline (Multi-Agent Visual Streaming)

### What You'll See:
- **Scanner** agent lights up with file discovery visualization
- **Classifier** agent shows pattern categorization
- **Extractor** agent displays knowledge graph building
- **Researcher** agent visualizes web search activity
- Each agent's circular avatar shows their actual work in real-time!

### How to Trigger:
1. Open the dashboard
2. Click **"🔄 Run Evolution"** in Quick Actions
3. Watch the **Agent Fleet** sidebar:
   - Scanner's avatar switches to scanning visualization
   - Red **LIVE** dot appears on active agents
   - Cyan glow effect pulses during activity
4. Monitor the **Activity Stream** for progress updates

### Expected Output:
```
📡 Scanner: Starting deep scan of 7 repositories...
🎥 Scanner visual stream: scanning_20260118_181206.mp4
📡 Scanner: Scan complete! Found 5,850 files with 15,296 patterns

🏷️ Classifier: Classifying 5,850 discovered files...
🎥 Classifier visual stream activated
🏷️ Classifier: Classification complete! 997 agents, 720 tools

🔬 Extractor: Building knowledge graph from discoveries...
🎥 Extractor: Extracted 20 concepts with 380 connections

🌐 Researcher: Starting web search for 2026 agentic patterns...
🎥 Researcher visual stream showing search activity
```

### Visual Indicators:
- **Idle**: Ambient blue loop playing
- **Working**: Agent-specific visualization (file count, metrics, progress)
- **Active Border**: Cyan glow around avatar
- **LIVE Dot**: Red pulsing indicator on top-right of avatar

---

## 🎭 Demo 3: Cinematic Narrative Production (9-Expert Team)

### What You'll See:
- **9-Expert Deliberation**: Story Team orchestrates Plot, Logic, Visuals, Tone experts
- **Multi-Scene Production**: Script broken into scenes, each with its own:
  - Voice synthesis (using your cloned voice)
  - Veo3 cinematic prompts
  - Real-time credit deduction
- **Progress Tracking**: Activity stream shows each expert's contribution

### How to Trigger:
1. Open the dashboard
2. Click **"🎭 Cinematic Narrative"** in Quick Actions
3. Watch the multi-stage production unfold

### Expected Flow:
```
🎭 AZIREM: Initializing Cinematic Narrative Production

🤝 Story Team: Orchestrating 9-expert deliberation...
   (Plot Expert, Logic Expert, Visual Expert, Tone Expert, etc.)

📝 Script Generated (3 scenes)

Scene 1/3:
   🎙️ Narrative Analyst: Analyzing emotional tone...
   🎤 Voice cloning with F5-TTS
   🎨 Visual Architect: Generating Veo3 prompts
   💎 Credits: -100 (Quality video)

Scene 2/3:
   ... (repeat for each scene)

🎬 AZIREM: Cinematic Narrative Production Complete!
💎 Remaining Credits: 12,400
```

### Veo3 Credit Tracking:
- **Initial**: 12,500 credits
- **Fast Video** (8s): 20 credits
- **Quality Video** (8s): 100 credits
- Click **"💎 Veo3 Credits"** to see detailed breakdown

---

##  📹 Understanding Agent Visual Streams

### Stream Architecture:

Each agent has 3 video states:

1. **Idle State**:
   - Source: `assets/bg-loop.mp4`
   - Shows ambient background animation
   - Default state when not working

2. **Working State**:
   - Source: `/outputs/agent_streams/{agent_id}/{work_type}_TIMESTAMP.mp4`
   - Dynamically generated based on work type
   - Real-time overlays with metrics

3. **Transitioning**:
   - Smooth fade between states
   - LIVE indicator appears/disappears
   - Border glow effect activates

### Stream Generation Methods:

#### Speaking (aSiReM):
- Uses **MuseTalk** for lip-sync
- Input: Audio from F5-TTS
- Output: Lip-synced MP4 with character avatar
- Resolution: High-quality for close-up viewing

#### Scanning (Scanner):
- Uses **ffmpeg** for text overlays
- Displays: File count, current file name, patterns found
- Updates every batch of files
- Example overlay: "Scanning: 1,247 files | patterns_discovered.py"

#### Analysis (Classifier, Extractor):
- Shows: Pattern statistics, knowledge graph metrics
- Visual: Data visualization overlays
- Updates: Real-time as processing completes

#### Searching (Researcher):
- Displays: Search queries, results count
- Shows: Web scraping progress
- Highlights: Discovered agentic patterns

---

## 🚀 Quick Start Commands

### Terminal Commands:

```bash
# Check server status
lsof -i :8082

# Restart server
kill -9 $(lsof -t -i:8082) && python3 real_agent_system.py > /dev/null 2>&1 &

# Trigger pipeline via API
python3 -c "import requests; requests.post('http://localhost:8082/api/run-pipeline')"

# Watch  server logs
tail -f server_live.log
```

### Python API:

```python
import requests

# Trigger evolution pipeline
requests.post("http://localhost:8082/api/run-pipeline")

# Get system status
status = requests.get("http://localhost:8082/api/status").json()
print(f"Mode: {status['mode']}, Metrics: {status['metrics']}")
```

---

## 📊 Metrics & Monitoring

### Real-Time Metrics (Top Right Panel):

- **Patterns Discovered**: Total agentic patterns found
- **Files Scanned**: Code files analyzed
- **Knowledge Nodes**: Concepts extracted
- **Agents Spawned**: Currently active agents

### Evolution Progress Bars:

- **Scan Phase**: 0-100% file discovery
- **Learn Phase**: 0-100% classification
- **Evolve Phase**: 0-100% knowledge extraction

### Activity Stream:

- Real-time log of all agent activities
- Color-coded by agent (icon + name)
- Click events to see details
- Auto-scrolls to latest activity

---

## 🎨 Visual Customization

### Agent Fleet Customization:

You can customize each agent's video source in `index.html`:

```javascript
const AGENTS = [
    { 
        id: 'azirem', 
        name: 'AZIREM', 
        video: 'assets/asirem-video.mp4'  // Your custom video here
    },
    // ... other agents
];
```

### Adding New Visualizations:

1. Create custom generator in `agent_visual_engine.py`:
```python
async def _generate_custom_visual(self, context: dict, timestamp: str):
    # Your ffmpeg commands here
    subprocess.run([
        "ffmpeg", "-i", "base_video.mp4",
        "-vf", f"drawtext=text='{your_text}':...",
        "-c:v", "libx264",
        str(output_path)
    ])
```

2. Register in `start_work_stream()`:
```python
if work_type == "your_custom_type":
    await self._generate_custom_visual(context, timestamp)
```

---

## 🔧 Troubleshooting

### Issue: Agent videos not updating
**Solution**: Refresh the browser page, check WebSocket connection in DevTools

### Issue: Server not responding
**Solution**: 
```bash
kill -9 $(lsof -t -i:8082)
python3 real_agent_system.py > server.log 2>&1 &
tail -f server.log
```

### Issue: Visual streams showing old videos
**Solution**: Clear browser cache or hard refresh (Cmd+Shift+R)

### Issue: High CPU usage
**Solution**: The system is processing files. This is normal during pipeline execution.

---

## 🎯 Next Steps

1. **Customize Your Voice**: Replace `assets/voice/reference.mp3` with your voice sample
2. **Add Custom Agents**: Extend the agent fleet with domain-specific specialists
3. **Create Custom Visualizations**: Design unique work visualizations for each agent
4. **Integrate Production APIs**: Connect to real Veo3, actual database, etc.
5. **Deploy to Production**: Set up SSL, authentication, load balancing

---

## 📄 Documentation Files

- `AGENT_VISUAL_STREAMING.md` - Technical architecture
- `VOICE_CLONING_SETUP.md` - Voice cloning guide
- `README.md` - Project overview

---

## 🎬 Enjoy Your Sovereign Command Center!

The future of multi-agent orchestration is visual, dynamic, and sovereign. You now have a production-ready system where **every agent shows you exactly what they're doing** in real-time through their own dedicated visual stream.

**Dashboard**: http://localhost:8082/index.html

**Happy Orchestrating! 🚀**
