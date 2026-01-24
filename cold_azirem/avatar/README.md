# aSiReM Avatar System

## Overview
Real-time, interactive avatar powered by the Cold Azirem Multi-Agent Ecosystem.
Designed for Apple Silicon (M4 Pro, 36GB RAM).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    aSiReM AVATAR LAYER                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CAPTURE    │  │   PROCESS    │  │   RENDER     │      │
│  │              │  │              │  │              │      │
│  │  • Webcam    │──│  • FACSvatar │──│  • WebGL     │      │
│  │  • Audio     │  │  • MuseTalk  │  │  • Canvas    │      │
│  │              │  │  • XTTS v2   │  │  • Three.js  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           │                                 │
│                    ┌──────┴──────┐                         │
│                    │  SPECTRA    │                         │
│                    │  (Design)   │                         │
│                    └─────────────┘                         │
│                           │                                 │
│  ┌──────────────┐  ┌──────┴──────┐  ┌──────────────┐      │
│  │   AZIREM     │──│ ORCHESTRATOR │──│  BUMBLEBEE   │      │
│  │   (Code)     │  │              │  │  (Research)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Motion Capture (FACSvatar)
- Real-time facial action unit tracking
- Webcam-based gesture recognition
- Emotion classification

### 2. Lip Synchronization (MuseTalk)
- Audio-driven mouth animation
- 30 FPS on Apple Silicon (MPS)
- Integration with XTTS v2 output

### 3. Voice Engine (XTTS v2 - Existing)
- French/Arabic voice cloning
- Real-time TTS from agent responses
- Integration with Ollama LLM output

### 4. Portrait Animation (LivePortrait)
- Single image to animated avatar
- Expression transfer
- High-fidelity 2D animation

### 5. Rendering Layer
- WebGL/Three.js for browser
- Electron for desktop
- Real-time compositing

## Hardware Requirements
- Apple Silicon M1+ (M4 Pro optimal)
- 16GB+ RAM (36GB optimal)
- Webcam for motion capture
- Microphone for voice input

## Installation

```bash
# Clone avatar dependencies
cd /Users/yacinebenhamou/aSiReM/cold_azirem/avatar

# FACSvatar (Motion Tracking)
git clone https://github.com/NumesSanguis/FACSvatar.git

# MuseTalk (Lip Sync)
git clone https://github.com/TMElyralab/MuseTalk.git

# LivePortrait (Animation)
git clone https://github.com/KlingTeam/LivePortrait.git

# Install Python dependencies (Apple Silicon optimized)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Quick Start

```python
from cold_azirem.avatar import AvatarEngine

# Initialize with SPECTRA design
engine = AvatarEngine(
    motion_tracker="facsvatar",
    lip_sync="musetalk",
    voice_engine="xtts_v2",
    renderer="webgl"
)

# Connect to agent orchestrator
engine.connect_to_orchestrator(orchestrator)

# Start real-time avatar
engine.start_realtime_session()
```
