#!/bin/bash
# aSiReM Avatar System - Dependency Installer
# Optimized for Apple Silicon (M4 Pro)

set -e

echo "🎭 aSiReM Avatar System Installer"
echo "=================================="
echo ""

AVATAR_DIR="/Users/yacinebenhamou/aSiReM/cold_azirem/avatar"
cd "$AVATAR_DIR"

# Create directories
mkdir -p deps models cache

echo "📦 Step 1: Installing PyTorch with Apple Silicon (MPS) support..."
pip install --upgrade pip
pip install torch torchvision torchaudio

echo ""
echo "📦 Step 2: Cloning FACSvatar (Motion Tracking)..."
if [ ! -d "deps/FACSvatar" ]; then
    git clone https://github.com/NumesSanguis/FACSvatar.git deps/FACSvatar
else
    echo "  → FACSvatar already cloned"
fi

echo ""
echo "📦 Step 3: Cloning MuseTalk (Lip Sync)..."
if [ ! -d "deps/MuseTalk" ]; then
    git clone https://github.com/TMElyralab/MuseTalk.git deps/MuseTalk
else
    echo "  → MuseTalk already cloned"
fi

echo ""
echo "📦 Step 4: Cloning LivePortrait (Portrait Animation)..."
if [ ! -d "deps/LivePortrait" ]; then
    git clone https://github.com/KlingTeam/LivePortrait.git deps/LivePortrait
else
    echo "  → LivePortrait already cloned"
fi

echo ""
echo "📦 Step 5: Installing common dependencies..."
pip install opencv-python numpy pillow mediapipe

echo ""
echo "📦 Step 6: Installing audio processing..."
pip install librosa soundfile pyaudio

echo ""
echo "📦 Step 7: Installing web rendering dependencies..."
pip install flask flask-socketio

echo ""
echo "✅ Avatar System dependencies installed!"
echo ""
echo "Next steps:"
echo "  1. Download MuseTalk models: cd deps/MuseTalk && python download_models.py"
echo "  2. Download LivePortrait models: cd deps/LivePortrait && python download_models.py"
echo "  3. Run demo: python -m cold_azirem.avatar.demo"
