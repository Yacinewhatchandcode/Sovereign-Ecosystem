"""
🧪 SOVEREIGN EVALUATION - INTEGRATION TEST
==========================================
Demonstrates the complete evaluation workflow:
1. Create a test dataset in Opik
2. Run Sovereign metrics (local Ollama judge)
3. View results in Opik Console
"""

import opik
from opik import track
from azirem_evaluation import ReasoningDepthMetric, HallucinationMetric

# Configure for local stack
opik.configure(url="http://localhost:5173/api")

print("=" * 60)
print("🔬 SOVEREIGN EVALUATION - INTEGRATION TEST")
print("=" * 60)

# ============================================================================
# STEP 1: Create Test Dataset
# ============================================================================

print("\n📊 Creating test dataset...")

client = opik.Opik()

# Create or get dataset
dataset_name = "Sovereign_Test_Dataset"
try:
    dataset = client.get_dataset(dataset_name)
    print(f"✅ Using existing dataset: {dataset_name}")
except:
    dataset = client.create_dataset(name=dataset_name, description="Test dataset for Sovereign Evaluation")
    print(f"✅ Created new dataset: {dataset_name}")
    
    # Add test items
    test_items = [
        {
            "input": "Scan the codebase for security vulnerabilities.",
            "expected_output": "Found 3 potential API keys in .env file. Recommend rotating credentials.",
            "context": ["File: .env", "Content: API_KEY=sk-1234", "PERPLEXITY_API_KEY=pplx-5678"]
        },
        {
            "input": "Classify the following files: scanner.py, config.yaml, test_api.py",
            "expected_output": "scanner.py: agent, config.yaml: config, test_api.py: test",
            "context": ["scanner.py contains class RealScannerAgent", "config.yaml has YAML structure", "test_api.py has pytest fixtures"]
        },
        {
            "input": "What is the purpose of the AZIREM system?",
            "expected_output": "AZIREM is a sovereign discovery ecosystem that inventories, classifies, and orchestrates code across multiple projects using local LLMs.",
            "context": ["AZIREM uses Ollama for local execution", "Multi-agent orchestration", "Self-evolving architecture"]
        }
    ]
    
    dataset.insert(test_items)
    print(f"✅ Added {len(test_items)} test items")

# ============================================================================
# STEP 2: Define Task Function
# ============================================================================

@track(name="sovereign_test_task")
def test_task(item):
    """Simulate agent response for testing."""
    # In real scenario, this would call your agent
    return {
        "output": item["expected_output"],
        "context": item.get("context", [])
    }

# ============================================================================
# STEP 3: Run Evaluation
# ============================================================================

print("\n⚖️ Running Sovereign Evaluation...")

from opik.evaluation import evaluate

metrics = [
    ReasoningDepthMetric(),
    HallucinationMetric()
]

try:
    result = evaluate(
        dataset=dataset,
        task=test_task,
        scoring_metrics=metrics,
        experiment_name="Sovereign_Integration_Test",
        nb_samples=3  # Test with 3 samples
    )
    
    print("\n✅ Evaluation Complete!")
    print(f"📈 Results:")
    print(f"   - Total samples: {len(result.test_results)}")
    
    # Display scores
    for metric_name, score_data in result.aggregate_scores.items():
        print(f"   - {metric_name}: {score_data['value']:.2f}")
    
    print(f"\n🔭 View detailed results in Opik Console:")
    print(f"   http://localhost:5173")
    
except Exception as e:
    print(f"\n❌ Evaluation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Integration test complete!")
print("=" * 60)
