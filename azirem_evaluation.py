"""
⚖️ AZIREM SOVEREIGN EVALUATION
==============================
Automated LLM-as-a-Judge system using local Ollama models.
Maintains sovereignty by evaluating agent performance locally.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import BaseMetric
from opik.evaluation.metrics.score_result import ScoreResult
from azirem_agents.ollama_executor import OllamaClient

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign_judge")

# ============================================================================
# JUDGE CONFIGURATION
# ============================================================================

JUDGE_MODEL = "llama3.1:8b"  # Local sovereign judge
JUDGE_TEMPERATURE = 0.1      # Low temp for consistent scoring

# ============================================================================
# METRICS
# ============================================================================

class SovereignMetric(BaseMetric):
    """Base class for Sovereign metrics using Ollama."""
    
    def __init__(self, name: str, client: Optional[OllamaClient] = None):
        super().__init__(name=name)
        self.client = client or OllamaClient()
        
    def _evaluate(self, prompt: str) -> ScoreResult:
        """Helper to run the evaluation prompt."""
        if not self.client.is_available():
            return ScoreResult(name=self.name, value=0.0, reason="Ollama not available")
            
        response = self.client.generate(
            prompt=prompt,
            model=JUDGE_MODEL,
            temperature=JUDGE_TEMPERATURE
        )
        
        if not response.success:
            return ScoreResult(name=self.name, value=0.0, reason=f"Judge failed: {response.error}")
            
        try:
            # Expecting JSON or simple number
            content = response.content.strip()
            # Try to find JSON in markdown block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[0].strip()
                
            data = json.loads(content)
            return ScoreResult(
                name=self.name,
                value=float(data.get("score", 0)),
                reason=data.get("reason", "No reason provided")
            )
        except Exception as e:
            logger.error(f"Failed to parse judge response: {content} | Error: {e}")
            return ScoreResult(name=self.name, value=0.0, reason="Parse error")


class ReasoningDepthMetric(SovereignMetric):
    """
    Evaluates the depth and coherence of the agent's reasoning.
    Checks for <think> blocks and step-by-step logic.
    """
    
    def __init__(self):
        super().__init__(name="Reasoning Depth")
        
    def score(self, input: str, output: str, **kwargs) -> ScoreResult:
        prompt = f"""
        You are an expert evaluator of AI reasoning.
        Analyze the following agent response for reasoning depth.
        
        User Input:
        "{input}"
        
        Agent Response:
        "{output}"
        
        Criteria:
        1. Does the response show evidence of internal thought (e.g., <think> tags)?
        2. Is the logic step-by-step and sound?
        3. Did the agent consider edge cases?
        
        Output valid JSON only:
        {{
            "score": <float 0.0 to 1.0>,
            "reason": "<explanation>"
        }}
        """
        return self._evaluate(prompt)


class HallucinationMetric(SovereignMetric):
    """
    Checks if the output is grounded in the provided context.
    """
    
    def __init__(self):
        super().__init__(name="Hallucination Check")
        
    def score(self, input: str, output: str, context: Optional[List[str]] = None, **kwargs) -> ScoreResult:
        context_str = "\n".join(context) if context else "No context provided."
        
        prompt = f"""
        You are a strict fact-checking judge.
        Determine if the agent's response is hallucinated or grounded in the context.
        
        Context:
        {context_str}
        
        Agent Response:
        "{output}"
        
        Criteria:
        1. Are all facts in the response supported by the context?
        2. Did the agent invent file names or data not present in the context?
        
        Output valid JSON only:
        {{
            "score": <float 0.0 to 1.0, where 1.0 is grounded and 0.0 is hallucination>,
            "reason": "<explanation>"
        }}
        """
        return self._evaluate(prompt)


class ToolEfficiencyMetric(SovereignMetric):
    """
    Evaluates if the agent selected the right tool for the job.
    """
    
    def __init__(self):
        super().__init__(name="Tool Efficiency")
        
    def score(self, input: str, tool_name: str, tool_args: Dict, **kwargs) -> ScoreResult:
        prompt = f"""
        Evaluate the efficiency of the tool selection.
        
        User Goal:
        "{input}"
        
        Tool Selected: {tool_name}
        Arguments: {json.dumps(tool_args)}
        
        Criteria:
        1. Was this the correct tool for the goal?
        2. Were the arguments precise?
        
        Output valid JSON only:
        {{
            "score": <float 0.0 to 1.0>,
            "reason": "<explanation>"
        }}
        """
        return self._evaluate(prompt)


# ============================================================================
# EVALUATION RUNNER
# ============================================================================

def run_dataset_evaluation(dataset_name: str = "Sovereign_Benchmark_v1"):
    """
    Runs evaluation on an Opik dataset using Sovereign Metrics.
    """
    print(f"🚀 Starting Sovereign Evaluation on dataset: {dataset_name}")
    
    # Define metrics
    metrics = [
        ReasoningDepthMetric(),
        HallucinationMetric(),
        # ToolEfficiencyMetric() # Requires specific trace structure
    ]
    
    try:
        # Run Opik assessment
        results = assess(
            dataset_name=dataset_name,
            metrics=metrics,
            nb_samples=10, # Limit for local execution speed
            experiment_name=f"Sovereign_Eval_{datetime.now().strftime('%Y%m%d_%H%M')}"
        )
        print("✅ Evaluation Complete!")
        return results
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

if __name__ == "__main__":
    # Test run
    test_input = "Scan the codebase for security keys."
    test_output = "I have scanned the codebase. Found 3 potential API keys in .env. <think> I should verify if they are active. </think>"
    
    print("🧪 Testing Sovereign Metrics...")
    
    metric = ReasoningDepthMetric()
    result = metric.score(test_input, test_output)
    print(f"Reasoning Score: {result.value} | Reason: {result.reason}")
