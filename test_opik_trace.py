import os
import opik
from opik import track
import asyncio

# Configure Opik for local usage
os.environ["OPIK_URL_OVERRIDE"] = "http://localhost:5173/api"

@track
def nested_call(arg):
    return f"Processed {arg}"

@track(name="test_trace")
def main_trace():
    print("Starting trace test...")
    res = nested_call("Sovereign Data")
    print(f"Result: {res}")
    return res

if __name__ == "__main__":
    try:
        main_trace()
        print("✅ Trace generated! Check http://localhost:5173 to verify.")
    except Exception as e:
        print(f"❌ Trace failed: {e}")
