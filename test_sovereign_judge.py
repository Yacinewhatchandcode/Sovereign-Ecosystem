"""
🧪 SOVEREIGN EVALUATION - SIMPLE TEST
=====================================
Tests the Sovereign Judge metrics without requiring Opik authentication.
"""

from azirem_evaluation import ReasoningDepthMetric, HallucinationMetric
from azirem_agents.ollama_executor import OllamaClient

print("=" * 60)
print("🔬 SOVEREIGN EVALUATION - SIMPLE TEST")
print("=" * 60)

# Check Ollama availability
client = OllamaClient()
if not client.is_available():
    print("\n❌ Ollama is not running. Start it with: ollama serve")
    exit(1)

print(f"\n✅ Ollama is running")
print(f"📦 Available models: {', '.join(client.list_models()[:3])}")

# ============================================================================
# TEST 1: Reasoning Depth Metric
# ============================================================================

print("\n" + "-" * 60)
print("🧠 TEST 1: Reasoning Depth Metric")
print("-" * 60)

reasoning_metric = ReasoningDepthMetric()

test_cases = [
    {
        "input": "Scan the codebase for security vulnerabilities.",
        "output": "<think>First, I need to identify files that might contain secrets. Common locations are .env files, config files, and hardcoded credentials in source code.</think> I found 3 potential API keys in the .env file. Recommend rotating these credentials immediately."
    },
    {
        "input": "What is 2+2?",
        "output": "4"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n  Case {i}:")
    print(f"  Input: {test['input'][:50]}...")
    print(f"  Output: {test['output'][:80]}...")
    
    result = reasoning_metric.score(test['input'], test['output'])
    print(f"  ✅ Score: {result.value:.2f}")
    print(f"  💭 Reason: {result.reason}")

# ============================================================================
# TEST 2: Hallucination Metric
# ============================================================================

print("\n" + "-" * 60)
print("🔍 TEST 2: Hallucination Check Metric")
print("-" * 60)

hallucination_metric = HallucinationMetric()

test_cases = [
    {
        "input": "What files did you find?",
        "output": "I found scanner.py, config.yaml, and test_api.py",
        "context": ["scanner.py", "config.yaml", "test_api.py", "README.md"]
    },
    {
        "input": "What files did you find?",
        "output": "I found unicorn.py and dragon.ts",
        "context": ["scanner.py", "config.yaml", "test_api.py"]
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n  Case {i}:")
    print(f"  Input: {test['input']}")
    print(f"  Output: {test['output']}")
    print(f"  Context: {test['context']}")
    
    result = hallucination_metric.score(
        test['input'], 
        test['output'],
        context=test['context']
    )
    print(f"  ✅ Score: {result.value:.2f} (1.0 = grounded, 0.0 = hallucination)")
    print(f"  💭 Reason: {result.reason}")

print("\n" + "=" * 60)
print("✅ Sovereign Judge is operational!")
print("=" * 60)
print("\n📊 Summary:")
print("  - Local Ollama judge: llama3.1:8b")
print("  - Metrics tested: Reasoning Depth, Hallucination Check")
print("  - All evaluations run locally (sovereign)")
print("\n🔭 Next: Integrate with Opik for experiment tracking")
