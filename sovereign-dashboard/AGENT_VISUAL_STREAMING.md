# Sovereign Command Center - Real-Time Agent Visual Streaming

## 🎬 Visual Streaming Architecture

The **Agent Visual Engine** provides **real-time MP4 streaming** for each agent, showing their actual work in progress.

## Features

### 1. **Individual Agent Streams**
Every agent in the fleet has its own dedicated visual stream:
- **aSiReM**: Speaks with lip-synced MuseTalk output
- **Scanner**: Displays file discovery visualizations  
- **Classifier**: Shows classification progress
- **Extractor**: Visualizes knowledge extraction
- **Researcher**: Displays web search activity
- **All others**: Ambient work visualizations

### 2. **Real-Time Updates**
The dashboard receives `agent_stream_update` WebSocket events containing:
```json
{
  "type": "agent_stream_update",
  "data": {
    "agent_id": "scanner",
    "agent_name": "Scanner",
    "status": "working",
    "stream_url": "/outputs/agent_streams/scanner/scanning_20260118_175900.mp4",
    "message": "Scanning 1247 files"
  }
}
```

### 3. **Dynamic Video Switching**
- **Idle State**: Shows ambient bg-loop.mp4
- **Working State**: Switches to task-specific visualization
- **Active Indicator**: Red pulsing dot appears on avatar
- **Glow Effect**: Avatar border pulses during activity

### 4. **Work Type Visualizations**

#### Speaking (aSiReM)
- Generates lip-synced MP4 using MuseTalk
- Shows synchronized avatar speaking
- Real-time audio-to-visual conversion

#### Scanning (Scanner)
- Overlays file count and current file on video
- Uses ffmpeg to dynamically generate frames
- Updates stream every batch of files

#### Analysis (Classifier, Extractor)
- Shows pattern detection statistics
- Visualizes knowledge graph formation
- Real-time metric overlays

#### Searching (Researcher)
- Displays search queries and results
- Shows web scraping progress
- Highlights discovered patterns

## Implementation

### Backend (`agent_visual_engine.py`)

```python
class AgentVisualStream:
    """Manages real-time visual output for a single agent."""
    
    async def start_work_stream(self, work_type: str, context: dict):
        """Generate and stream real-time work visualization."""
        # Generates MP4 based on work type
        # Emits updates via WebSocket
        
    async def _generate_speaking_visual(self, context: dict, timestamp: str):
        """Generate lip-synced speaking visual using MuseTalk."""
        
    async def _generate_scanning_visual(self, context: dict, timestamp: str):
        """Generate file scanning visualization with ffmpeg overlays."""
```

### Integration (`real_agent_system.py`)

```python
# Initialize visual engine
self.visual_engine = AgentVisualEngine()
self.visual_engine.set_callback(self.broadcast_event)

# During pipeline execution
if self.visual_engine:
    await self.visual_engine.start_agent_work("scanner", "scanning", {
        "files_count": 0,
        "current_file": "Initializing scan..."
    })
```

### Frontend (`index.html`)

```javascript
case 'agent_stream_update':
    updateAgentVideoStream(data.agent_id, data.stream_url, data.status);
    logTerminal(`📹 ${data.agent_name}: ${data.message}`);
    break;

function updateAgentVideoStream(agentId, streamUrl, status) {
    const videoElement = card.querySelector('.agent-video');
    if (videoElement && streamUrl) {
        videoElement.src = streamUrl;
        videoElement.load();
        videoElement.play();
        
        // Add pulsing effect during work
        if (status === 'working' || status === 'streaming') {
            card.classList.add('active');
        }
    }
}
```

## Verification

1. **Open Dashboard**: Navigate to `http://localhost:8082/`
2. **Trigger Evolution**: Click "Run Evolution" in Quick Actions
3. **Watch Agents**: Each agent's avatar will:
   - Light up with a red LIVE indicator
   - Show their actual work visualization
   - Pulse with cyan glow during activity
4. **Monitor Activity**: Real-time activity stream shows stream updates

## Technical Details

### Video Generation
- **Format**: MP4 (H.264)
- **Resolution**: Adaptive (based on source)
- **Frame Rate**: 24-30 fps
- **Audio**: Synchronized for speaking agents

### Performance
- **Lazy Generation**: Videos generated only when needed
- **Caching**: Reuses static loops for idle states
- **Async Processing**: Non-blocking video generation
- **Stream Management**: Automatic cleanup after completion

### Storage
- **Output Directory**: `outputs/agent_streams/{agent_id}/`
- **Naming Convention**: `{work_type}_{timestamp}.mp4`
- **Cleanup**: Old streams purged after 24h

## Future Enhancements

1. **WebRTC Streaming**: Real-time frame-by-frame streaming
2. **Canvas Rendering**: Browser-side visualization generation
3. **3D Avatars**: Three.js integrated character models
4. **Multi-Camera**: Picture-in-picture for complex tasks
5. **Replay System**: DVR-style time travel for agent work

## Logs

The system logs all visual streaming events:

```
📹 Registered visual stream for Scanner (scanner)
📹 All agent visual streams initialized
📹 Scanner: Scanning 1247 files
📹 Classifier: Classifying 1247 files
📹 aSiReM: Speaking scene 1/3
```
