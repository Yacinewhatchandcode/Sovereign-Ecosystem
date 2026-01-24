#!/usr/bin/env python3
"""
🧬 PATTERN ENGINE - Unified Pattern Recognition
==============================================
Shared pattern definitions for scanners, classifiers, and visual operators.
"""

import re

# File extensions we care about
LANGUAGE_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'React JSX',
    '.tsx': 'React TSX',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.md': 'Markdown',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Zsh',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.rb': 'Ruby',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C Header',
    '.hpp': 'C++ Header',
    '.sql': 'SQL',
    '.graphql': 'GraphQL',
    '.proto': 'Protocol Buffers',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
}

# Patterns to look for in code
AGENTIC_PATTERNS = {
    'langchain': r'(from langchain|import langchain|LangChain)',
    'langgraph': r'(from langgraph|import langgraph|StateGraph)',
    'crewai': r'(from crewai|import crewai|CrewAI|Agent\()',
    'autogen': r'(from autogen|import autogen|AutoGen)',
    'ollama': r'(ollama|Ollama|OLLAMA)',
    'openai': r'(openai|OpenAI|gpt-|GPT)',
    'anthropic': r'(anthropic|Anthropic|claude|Claude)',
    'mcp': r'(MCP|Model.*Context.*Protocol|mcp_)',
    'rag': r'(RAG|retrieval.*augment|ChromaDB|Chroma|VectorStore)',
    'agent': r'(class.*Agent|def.*agent|Agent\(|BaseAgent)',
    'tool': r'(@tool|BaseTool|Tool\(|ToolSpec)',
    'workflow': r'(workflow|Workflow|DAG|Pipeline)',
    'async': r'(async def|await |asyncio)',
    'websocket': r'(WebSocket|websocket|ws://|wss://)',
    'streaming': r'(stream|Stream|SSE|Server.Sent)',
    'embedding': r'(embed|Embedding|vector|Vector)',
    'memory': r'(ConversationMemory|BufferMemory|ChatMemory)',
    'chain': r'(LLMChain|SequentialChain|Chain\()',
    'prompt': r'(PromptTemplate|ChatPrompt|SystemMessage)',
    'evolution': r'(evolv|self.improv|autonom|self.heal)',
}

def analyze_content(content: str):
    """Analyze string content for agentic patterns."""
    found_patterns = []
    for pattern_name, pattern_regex in AGENTIC_PATTERNS.items():
        if re.search(pattern_regex, content, re.IGNORECASE):
            found_patterns.append(pattern_name)
    
    # Extract structural elements
    functions = re.findall(r'(?:def|function|const|let|var)\s+(\w+)', content)[:15]
    classes = re.findall(r'class\s+(\w+)', content)[:10]
    imports = re.findall(r'(?:import|from|require)\s+[\'"]?([\w.]+)', content)[:15]
    
    return {
        "patterns": found_patterns,
        "functions": list(set(functions)),
        "classes": list(set(classes)),
        "imports": list(set(imports)),
        "score": len(found_patterns) * 10
    }
