"""Pattern Engine stub — provides analyze_content and AGENTIC_PATTERNS."""

AGENTIC_PATTERNS = {
    "orchestration": ["orchestrat", "coordinate", "delegate", "pipeline"],
    "generation": ["generat", "create", "build", "deploy", "synthesize"],
    "analysis": ["analyz", "scan", "audit", "inspect", "detect"],
    "communication": ["speak", "broadcast", "notify", "report", "message"],
}

def analyze_content(content: str, patterns: dict = None) -> dict:
    """Analyze content for agentic patterns. Returns detected pattern categories."""
    if patterns is None:
        patterns = AGENTIC_PATTERNS
    
    results = {}
    content_lower = content.lower()
    
    for category, keywords in patterns.items():
        matches = [kw for kw in keywords if kw in content_lower]
        if matches:
            results[category] = matches
    
    return {
        "detected_patterns": results,
        "pattern_count": len(results),
        "content_length": len(content),
        "is_agentic": len(results) > 0
    }
