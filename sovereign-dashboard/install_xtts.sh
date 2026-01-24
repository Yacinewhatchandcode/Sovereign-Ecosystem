#!/bin/bash
# 🎤 ONE-CLICK XTTS Voice Cloning Setup
# This script installs XTTS with your voice for true voice cloning

set -e  # Exit on any error

echo "🎤 aSiReM Voice Cloning - XTTS Installation"
echo "=========================================="
echo ""

# Check for Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo "📦 Installing Python 3.11..."
    brew install python@3.11
else
    echo "✅ Python 3.11 found"
fi

# Create virtual environment
VENV_PATH="$HOME/venv-xtts"
if [ -d "$VENV_PATH" ]; then
    echo "⚠️  venv-xtts already exists, removing..."
    rm -rf "$VENV_PATH"
fi

echo "📦 Creating Python 3.11 virtual environment..."
python3.11 -m venv "$VENV_PATH"

echo "📦 Activating environment..."
source "$VENV_PATH/bin/activate"

echo "📦 Installing XTTS and dependencies..."
pip install --upgrade pip
pip install TTS torch torchaudio numpy scipy soundfile

echo ""
echo "✅ XTTS Installed Successfully!"
echo ""

# Test with user's voice
VOICE_FILE="$(pwd)/assets/MyVoice.wav"
TEST_OUTPUT="$(pwd)/generated/test_xtts_clone.wav"

if [ -f "$VOICE_FILE" ]; then
    echo "🎤 Testing voice cloning with YOUR voice..."
    echo "   Voice: $VOICE_FILE"
    echo ""
    
    tts --text "Hello! This is aSiReM, speaking with your cloned voice using XTTS." \
        --model_name "tts_models/multilingual/multi-dataset/xtts_v2" \
        --speaker_wav "$VOICE_FILE" \
        --language en \
        --out_path "$TEST_OUTPUT"
    
    echo ""
    echo "✅ Voice cloning test complete!"
    echo "   Output: $TEST_OUTPUT"
    echo ""
    echo "🔊 Playing cloned voice..."
    afplay "$TEST_OUTPUT"
    
    echo ""
    echo "🎉 SUCCESS! Your voice has been cloned!"
    echo ""
else
    echo "⚠️  Voice file not found at: $VOICE_FILE"
    echo "   Place your voice file there and run this script again"
fi

echo "============================================"
echo "📝 NEXT STEPS:"
echo ""
echo "1. Update asirem_speaking_engine.py to use XTTS:"
echo "   Edit line ~170 to use: $VENV_PATH/bin/python3"
echo ""
echo "2. Or set environment variable:"
echo "   export XTTS_PYTHON=$VENV_PATH/bin/python3"
echo ""
echo "3. Test the speaking engine:"
echo "   python3 test_voice_cloning.py"
echo ""
echo "4. Open dashboard and click 'aSiReM Speak'!"
echo "   http://localhost:8082/index.html"
echo "============================================"
