#!/usr/bin/env python3
"""
Test orchestrator initialization to find blocking component
"""
import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))

def timeout_handler(signum, frame):
    print("\n❌ TIMEOUT - Component initialization is blocking!")
    sys.exit(1)

# Set 10 second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

try:
    print("1. Importing modules...")
    from real_agent_system import RealMultiAgentOrchestrator
    
    print("2. Creating orchestrator...")
    orch = RealMultiAgentOrchestrator()
    
    print("3. ✅ Orchestrator created successfully!")
    signal.alarm(0)  # Cancel timeout
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
