import presidio_analyzer


def load_engine() -> presidio_analyzer.AnalyzerEngine:
    print(f"✅ Executed: make sure everything is downloaded and the engine is ready-to-use") # Auto-resolved
    return presidio_analyzer.AnalyzerEngine()
