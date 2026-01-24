# 🎙️ AZIREM PODCAST VIDEO API DOCUMENTATION

## Overview

The AZIREM Podcast system provides real-time video generation featuring conversations between:
- **You** (User avatar with cloned voice from `MyVoice.wav`)
- **AZIREM** (AI avatar with anime/Sony character)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PODCAST VIDEO SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   REST API   │───▶│   WebSocket  │───▶│  Video Gen   │  │
│  │  Endpoints   │    │   Streaming  │    │   Pipeline   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ AZIREM Brain │    │ Activity Log │    │  TTS Engine  │  │
│  │  (DeepSeek)  │    │  (Real-time) │    │  (XTTS/F5)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                         │          │
│         ▼                                         ▼          │
│  ┌──────────────┐                        ┌──────────────┐  │
│  │   Response   │                        │   Lip-Sync   │  │
│  │  Generation  │                        │    Engine    │  │
│  └──────────────┘                        └──────────────┘  │
│                                                   │          │
│                                                   ▼          │
│                                          ┌──────────────┐  │
│                                          │  MP4 Output  │  │
│                                          │  (Streaming) │  │
│                                          └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Text-Only Podcast (Q&A)

**Endpoint:** `POST /api/podcast/ask`

**Description:** Ask AZIREM a question and get a text response (optionally with voice).

**Request:**
```json
{
  "question": "What are your main capabilities?",
  "use_voice": false
}
```

**Response:**
```json
{
  "question": "What are your main capabilities?",
  "response": "I manage a fleet of 13 specialized agents...",
  "agent": "azirem",
  "audio_path": "/path/to/audio.wav",  // if use_voice=true
  "video_path": "/path/to/video.mp4"   // if use_voice=true
}
```

**Example:**
```bash
curl -X POST http://localhost:8082/api/podcast/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about your agents", "use_voice": true}'
```

---

### 2. Video Podcast Generation (Dual Avatar)

**Endpoint:** `POST /api/podcast/video`

**Description:** Generate a complete podcast video with both user and AZIREM avatars.

**Request:**
```json
{
  "conversation": [
    {
      "speaker": "user",
      "text": "Hello AZIREM!"
    },
    {
      "speaker": "ai",
      "text": "Hello! I'm AZIREM, your AI orchestrator."
    },
    {
      "speaker": "user",
      "text": "Tell me about your agent fleet."
    },
    {
      "speaker": "ai",
      "text": "I manage 13 specialized agents, each with unique capabilities..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "video_path": "/path/to/podcast_20260119_004500.mp4",
  "segments": 4,
  "message": "Podcast video generated successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8082/api/podcast/video \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"speaker": "user", "text": "Hi AZIREM!"},
      {"speaker": "ai", "text": "Hello! How can I help?"}
    ]
  }'
```

---

### 3. Video Streaming

**Endpoint:** `GET /api/podcast/stream?path={video_path}`

**Description:** Stream a generated podcast video.

**Parameters:**
- `path` (query): Full path to the video file

**Response:** MP4 video stream with proper headers

**Example:**
```bash
# Stream the video
curl "http://localhost:8082/api/podcast/stream?path=/path/to/podcast.mp4" \
  --output podcast.mp4

# Or open in browser
open "http://localhost:8082/api/podcast/stream?path=/path/to/podcast.mp4"
```

---

### 4. WebSocket Real-Time Podcast

**Endpoint:** `ws://localhost:8082/ws/stream`

**Description:** Real-time podcast interaction via WebSocket.

**Send Message:**
```json
{
  "type": "podcast_ask",
  "data": {
    "question": "What makes you unique?",
    "use_voice": true
  }
}
```

**Receive Messages:**

1. **Activity Update:**
```json
{
  "type": "activity",
  "data": {
    "agent_id": "azirem",
    "agent_name": "AZIREM",
    "icon": "🎙️",
    "message": "Podcast Question: What makes you unique?..."
  }
}
```

2. **Response:**
```json
{
  "type": "podcast_response",
  "data": {
    "question": "What makes you unique?",
    "response": "Unlike traditional AI systems...",
    "agent_id": "azirem"
  }
}
```

3. **Audio/Video Ready:**
```json
{
  "type": "podcast_audio",
  "data": {
    "audio_path": "/path/to/audio.wav",
    "video_path": "/path/to/video.mp4"
  }
}
```

4. **Video Generation Complete:**
```json
{
  "type": "podcast_video_ready",
  "data": {
    "video_path": "/path/to/podcast_20260119.mp4",
    "segments": 6
  }
}
```

---

## Video Generation Pipeline

### Step-by-Step Process

1. **User Input** → Question or conversation script
2. **Brain Processing** → AZIREM thinks using DeepSeek LLM
3. **TTS Generation** → Voice synthesis for both speakers:
   - User: Voice cloning from `MyVoice.wav` (XTTS/F5-TTS)
   - AZIREM: AI voice (XTTS/system TTS)
4. **Lip-Sync** → Generate talking head videos:
   - User avatar: `WhatsApp Image 2025-10-27 at 15.20.55.jpeg`
   - AZIREM avatar: `Gemini_Generated_Image_rxyzqarxyzqarxyz.png`
5. **Video Assembly** → Combine segments into final MP4
6. **Streaming** → Serve via HTTP or WebSocket

---

## Character Assets

### User Avatar
- **Image:** `/sovereign-dashboard/assets/character/WhatsApp Image 2025-10-27 at 15.20.55.jpeg`
- **Voice Sample:** `/sovereign-dashboard/assets/MyVoice.wav`
- **Voice Engine:** XTTS voice cloning

### AZIREM Avatar
- **Image:** `/sovereign-dashboard/assets/character/Gemini_Generated_Image_rxyzqarxyzqarxyz.png`
- **Voice:** AI-generated (XTTS or system TTS)
- **Character Type:** Anime/Sony style

---

## Output Formats

### Video Specifications
- **Format:** MP4 (H.264)
- **Resolution:** 1280x720 (HD)
- **Audio:** AAC, 192kbps
- **Frame Rate:** 30fps
- **Layout:** Side-by-side or picture-in-picture

### File Structure
```
outputs/podcasts/
├── audio_You_20260119_004501234567.wav
├── audio_AZIREM_20260119_004502345678.wav
├── video_You_20260119_004503456789.mp4
├── video_AZIREM_20260119_004504567890.mp4
└── podcast_20260119_004500.mp4  ← Final combined video
```

---

## Testing

### Run API Tests
```bash
# Test basic podcast Q&A
python3 test_podcast_api.py

# Test video generation
python3 test_podcast_video_api.py
```

### Manual Testing

1. **Simple Q&A:**
```bash
curl -X POST http://localhost:8082/api/podcast/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who are you?"}'
```

2. **Generate Video:**
```bash
curl -X POST http://localhost:8082/api/podcast/video \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"speaker": "user", "text": "Hello!"},
      {"speaker": "ai", "text": "Hi there!"}
    ]
  }'
```

3. **Stream Video:**
```bash
# Get video path from previous response, then:
curl "http://localhost:8082/api/podcast/stream?path=/path/to/video.mp4" \
  --output my_podcast.mp4
```

---

## Integration Examples

### Python
```python
import aiohttp
import asyncio

async def generate_podcast():
    async with aiohttp.ClientSession() as session:
        # Generate video
        async with session.post(
            "http://localhost:8082/api/podcast/video",
            json={
                "conversation": [
                    {"speaker": "user", "text": "Hi AZIREM!"},
                    {"speaker": "ai", "text": "Hello!"}
                ]
            }
        ) as resp:
            data = await resp.json()
            video_path = data["video_path"]
            print(f"Video ready: {video_path}")
            
            # Stream it
            stream_url = f"http://localhost:8082/api/podcast/stream?path={video_path}"
            print(f"Stream at: {stream_url}")

asyncio.run(generate_podcast())
```

### JavaScript (Browser)
```javascript
// Generate podcast video
async function generatePodcast() {
  const response = await fetch('http://localhost:8082/api/podcast/video', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      conversation: [
        {speaker: 'user', text: 'Hello AZIREM!'},
        {speaker: 'ai', text: 'Hello! How can I help?'}
      ]
    })
  });
  
  const data = await response.json();
  const videoUrl = `http://localhost:8082/api/podcast/stream?path=${data.video_path}`;
  
  // Display in video player
  document.getElementById('podcast-player').src = videoUrl;
}
```

### WebSocket (Real-time)
```javascript
const ws = new WebSocket('ws://localhost:8082/ws/stream');

ws.onopen = () => {
  // Ask a question
  ws.send(JSON.stringify({
    type: 'podcast_ask',
    data: {
      question: 'Tell me about your agents',
      use_voice: true
    }
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.type === 'podcast_response') {
    console.log('AZIREM:', msg.data.response);
  }
  
  if (msg.type === 'podcast_video_ready') {
    const videoUrl = `http://localhost:8082/api/podcast/stream?path=${msg.data.video_path}`;
    document.getElementById('player').src = videoUrl;
  }
};
```

---

## Performance

### Typical Generation Times

| Segments | Audio Gen | Video Gen | Total Time |
|----------|-----------|-----------|------------|
| 2        | ~5s       | ~15s      | ~20s       |
| 4        | ~10s      | ~30s      | ~40s       |
| 6        | ~15s      | ~45s      | ~60s       |
| 10       | ~25s      | ~75s      | ~100s      |

*Times vary based on text length and hardware*

---

## Troubleshooting

### Common Issues

1. **TTS Not Available:**
   - Check if Google dependencies are installed
   - Fallback to system `say` command on macOS

2. **Lip-Sync Fails:**
   - Falls back to static image with waveform
   - Check ffmpeg installation

3. **Video Generation Timeout:**
   - Increase timeout in client
   - Reduce conversation length
   - Check server logs

### Debug Commands
```bash
# Check server status
curl http://localhost:8082/api/status

# View server logs
tail -f sovereign-dashboard/server_live.log

# Test TTS directly
python3 -c "from asirem_speaking_engine import ASiREMSpeakingEngine; import asyncio; asyncio.run(ASiREMSpeakingEngine().speak('test'))"
```

---

## Future Enhancements

- [ ] Real-time streaming during generation
- [ ] Multiple avatar styles
- [ ] Background music and effects
- [ ] Automatic subtitle generation
- [ ] Export to YouTube/social media formats
- [ ] Live podcast recording mode
- [ ] Multi-speaker support (3+ characters)

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/podcast/ask` | POST | Text Q&A with optional voice |
| `/api/podcast/video` | POST | Generate dual-avatar video |
| `/api/podcast/stream` | GET | Stream generated video |
| `/ws/stream` | WebSocket | Real-time podcast interaction |

---

**Server:** `http://localhost:8082`  
**WebSocket:** `ws://localhost:8082/ws/stream`  
**Documentation:** This file  
**Tests:** `test_podcast_api.py`, `test_podcast_video_api.py`
