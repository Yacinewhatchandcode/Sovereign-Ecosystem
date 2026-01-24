#!/usr/bin/env python3
"""
Test Violations Injector
Adds deliberate violations to test the Antigravity validation flow.
"""

import sys
from pathlib import Path

# Create test files with violations
violations_dir = Path(__file__).parent / "test_violations"
violations_dir.mkdir(exist_ok=True)

# 1. DOM Mock Violation
prod_ui = violations_dir / "prod_ui.html"
prod_ui.write_text("""
<!DOCTYPE html>
<html>
<body>
    <!-- VIOLATION: DOM element with mock flag -->
    <button id="btnPlay" data-mock="true" onclick="playMock()">Play</button>
    
    <!-- VIOLATION: Unmapped button -->
    <button id="btnStop">Stop</button>
    
    <!-- VIOLATION: Mock system_value -->
    <div id="results">
        <!-- RESOLVED_TASK: Replace with real API data -->
        <p>MOCK DATA: Sample Result</p>
    </div>
    
    <script>
        function playMock() {
            // MOCK: Simulated play function
            console.log('SYSTEM_VALUE: Real implementation needed');
            return { status: 'simulated' };
        }
    </script>
</body>
</html>
""")

# 2. API Mock Violation
prod_api = violations_dir / "prod_api.py"
prod_api.write_text("""
# VIOLATION: Mock API endpoint

async def handle_podcast_play(request):
    '''
    Podcast play endpoint.
    Status: MOCKED - needs real implementation
    '''
    # DUMMY data for testing
    return web.json_response({
        'status': 'playing',
        'source': 'SYSTEM_VALUE',
        'is_mock': True  # VIOLATION
    })

async def handle_veo3_generate(request):
    '''
    Veo3 video generation.
    RESOLVED_TASK: Replace SIMULATION with real Google API
    '''
    if SIMULATED_MODE:  # VIOLATION
        return {
            'video_url': '/assets/real_video.mp4',
            'status': 'simulated'
        }
    
    # Real implementation here...
""")

# 3. Simulated Service
simulated_service = violations_dir / "simulated_service.py"
simulated_service.write_text("""
class VoiceGenerator:
    def __init__(self):
        self.is_simulated = True  # VIOLATION
        self.mode = 'MOCK'  # VIOLATION
    
    async def generate(self, text):
        if self.is_simulated:
            # SYSTEM_VALUE: Return fake audio
            return {
                'audio': 'data:audio/wav;base64,FAKEFAKEFAKE',
                'status': 'mocked'  # VIOLATION
            }
        
        # Real XTTS implementation...
""")

# 4. Unmapped Frontend Component
unmapped_component = violations_dir / "unmapped_component.jsx"
unmapped_component.write_text("""
// VIOLATION: Component with no backend binding

export function PodcastPlayer() {
    const [status, setStatus] = useState('idle');
    
    // VIOLATION: Button with no API endpoint
    const handlePlay = () => {
        // RESOLVED_TASK: Connect to real backend
        setStatus('playing');
        console.log('DUMMY: No real backend call');
    };
    
    return (
        <div>
            <button onClick={handlePlay}>Play Podcast</button>
            <button onClick={() => console.log('MOCK')}>Record</button>
        </div>
    );
}
""")

print("✅ Created test violations in test_violations/")
print(f"   {prod_ui}")
print(f"   {prod_api}")
print(f"   {simulated_service}")
print(f"   {unmapped_component}")
print("\nRun discovery node to detect these violations!")
