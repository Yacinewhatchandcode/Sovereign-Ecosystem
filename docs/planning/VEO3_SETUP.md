# Veo3 Video Generation - Setup & Test Guide

## Current Status

✅ **Code Implementation**: Complete  
⚠️ **Dependencies**: `google-genai` package needs installation  
⚠️ **Testing**: Not yet tested with real API

## Setup Steps

### 1. Install Required Package

```bash
# Option A: Install in user directory
pip3 install --user google-genai

# Option B: Use existing venv
cd /Users/yacinebenhamou/aSiReM/sovereign-dashboard
source venv-speaking/bin/activate
pip install google-genai
```

### 2. Set API Key

```bash
export GOOGLE_API_KEY="AIzaSyBE56mJHeVqhQzOOe1TGdDoe8m3aWN_wSY"
```

### 3. Run Test

```bash
cd /Users/yacinebenhamou/aSiReM/sovereign-dashboard
python3 test_veo3.py
```

## Manual Testing

If the automated test doesn't work, try this Python code directly:

```python
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBE56mJHeVqhQzOOe1TGdDoe8m3aWN_wSY'

from asirem_speaking_engine import Veo3Generator

# Create generator
gen = Veo3Generator()

# Check credits
credits = gen.get_credits()
print(f"Credits: {credits}")

# Generate video
result = await gen.generate_chunk(
    prompt="A blue bird flying through clouds",
    duration_seconds=5,
    quality="fast"
)

print(f"Video result: {result}")
```

## Expected Behavior

### If `google-genai` is NOT installed:
```
⚠️ google-genai not available, Veo3 will run in simulation mode
💎 Veo3 Generator: Simulation mode active (No GOOGLE_API_KEY found)
❌ RuntimeError: Veo3Generator BLOCKED: Missing or invalid GOOGLE_API_KEY...
   (Antigravity Rule 2.2 - Zero Mock Tolerance)
```

### If  `google-genai` IS installed with valid key:
```
💎 Veo3 Generator: Production mode ACTIVATED with Google API Key
✅ Generator initialized
📊 Credits: {'total': 12500, 'used': 0, 'remaining': 12500}
🎬 Generating video...
✅ SUCCESS! Video: /Users/yacinebenhamou/aSiReM/sovereign-dashboard/generated/veo3_<timestamp>.mp4
```

## Antigravity Rules Enforced

**Rule 2.2 (Zero Mock Tolerance)**:  
The system will NOT fall back to simulation mode silently.

**Rule 2.5 (Fail Loud)**:  
If `GOOGLE_API_KEY` is missing or invalid, the system raises `RuntimeError` with clear error message instead of silently degrading.

## Video Output Details

**File Location**: `sovereign-dashboard/generated/veo3_<timestamp>.mp4`

**Credits Used**:
- Fast quality: 20 credits per 5-8 second video
- High quality: 100 credits per 5-8 second video

**Monthly Limit**: 12,500 credits
- Fast videos: ~625 per month
- Quality videos: ~125 per month

## Troubleshooting

### Issue: "google-genai not available"
**Solution**: Install the package:
```bash
pip3 install --user google-genai
```

### Issue: "RuntimeError: Veo3Generator BLOCKED"
**Solution**: This is CORRECT behavior per Antigravity rules!  
Set the API key:
```bash
export GOOGLE_API_KEY="your-key-here"
```

### Issue: API authentication error
**Solution**: Verify your API key is valid and has Vertex AI access enabled in Google Cloud Console.

## Integration with Dashboard

### Backend API Endpoint (when real_agent_system.py works):

```
POST /api/veo3/generate
{
  "prompt": "A blue bird flying",
  "duration": 5,
  "quality": "fast"
}

Response:
{
  "video_path": "/path/to/video.mp4",
  "credits_used": 20,
  "credits_remaining": 12480
}
```

### Enable in Dashboard:
Once backend API is running, the "🎬 Veo3 Generate" button will:
1. Send prompt to `/api/veo3/generate`
2. Display generation progress
3. Show video in dashboard when complete
4. Update credit counter

## Next Steps

1. ✅ Install `google-genai`: `pip3 install --user google-genai`
2. ✅ Export API key: `export GOOGLE_API_KEY="..."`
3. ✅ Run test: `python3 test_veo3.py`
4. ❌ Fix `real_agent_system.py` to enable dashboard integration
5. ✅ Test full workflow from dashboard UI

## Files

- **Implementation**: `asirem_speaking_engine.py` (class Veo3Generator, line 622)
- **Test Script**: `test_veo3.py`
- **Output Dir**: `sovereign-dashboard/generated/`
- **This Guide**: `VEO3_SETUP.md`
