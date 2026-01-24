# 🎤 Voice Cloning Setup for aSiReM

Your aSiReM speaking engine now supports **F5-TTS voice cloning** using your actual voice!

## 📋 Quick Setup

### Step 1: Prepare Your Voice Sample

Record or provide an MP3 file of your voice. For best results:
- **Duration**: 5-30 seconds
- **Quality**: Clear audio, minimal background noise
- **Content**: Natural speech (not reading a script robotically)
- **Format**: MP3, WAV, or any audio format

### Step 2: Set Up Your Voice Reference

Run the setup script with your audio file:

```bash
cd /Users/yacinebenhamou/aSiReM/sovereign-dashboard
python3 setup_voice.py /path/to/your/voice.mp3 "Exact transcription of what you said"
```

**Example:**
```bash
python3 setup_voice.py ~/Downloads/my_voice.mp3 "Hello, I'm Yacine. This is a sample of my voice for AI cloning."
```

### Step 3: Test Your Voice

1. Navigate to the dashboard: http://localhost:8082/index.html
2. Click the **"aSiReM Speak"** button (gold colored with 🗣️)
3. Listen to aSiReM speaking with YOUR voice!

## 🎯 How It Works

The system uses **F5-TTS** (Diffusion-based Text-to-Speech) for zero-shot voice cloning:

1. **Reference Audio**: Your voice sample (`assets/voice/reference.mp3`)
2. **Transcription**: What you said in the sample (`assets/voice/reference.txt`)
3. **F5-TTS**: Clones your voice characteristics to generate new speech
4. **Output**: aSiReM speaks with your voice!

## 📁 File Structure

```
sovereign-dashboard/
├── assets/
│   └── voice/
│       ├── reference.mp3  # Your voice sample (you provide this)
│       └── reference.txt  # Transcription (auto-loaded by engine)
├── setup_voice.py         # Helper script to set up your voice
└── asirem_speaking_engine.py  # Main speaking engine
```

## 🔧 Advanced Usage

### Programmatic Setup

```python
from asirem_speaking_engine import ASiREMSpeakingEngine

engine = ASiREMSpeakingEngine()
await engine.initialize()

# Set your voice reference
engine.tts.set_reference_audio(
    "/path/to/your/voice.mp3",
    "Transcription of what you said"
)

# Make aSiReM speak with your voice
result = await engine.speak("Hello! I'm speaking with your voice!")
```

### Without Transcription

If you don't provide a transcription, F5-TTS will use a system_value. This works but may reduce quality:

```bash
python3 setup_voice.py ~/Downloads/my_voice.mp3
```

## 🎨 Quality Tips

For the **best voice cloning results**:

1. ✅ **Clear audio**: Record in a quiet environment
2. ✅ **Natural speech**: Speak naturally, not like reading
3. ✅ **Accurate transcription**: Provide the exact words you said
4. ✅ **Good length**: 10-20 seconds is ideal
5. ✅ **Consistent tone**: Use your normal speaking voice

## 🔍 Troubleshooting

### "F5-TTS helper not found"
The system will fall back to system TTS. F5-TTS is available at:
`~/.starconnect/tts_clone_helper.py`

### "Reference voice not found"
Make sure you've run `setup_voice.py` to copy your audio file to the correct location.

### Poor quality output
- Provide the exact transcription of your reference audio
- Use a longer, clearer voice sample
- Ensure minimal background noise

## 🚀 Next Steps

Once your voice is set up:
1. Test the speaking engine in the dashboard
2. Try different topics: "greeting", "what_is_ai", "the_future"
3. Generate lip-synced videos with MuseTalk
4. Create narrative videos with Veo3

---

**Ready to hear aSiReM speak with YOUR voice? Run the setup script now!** 🎉
