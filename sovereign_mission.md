# Sovereign Mission Instruction

This file defines the operational boundaries and guidelines for the Nexus Global Mission Engine.

## Agent Boundaries

- **Read-Only First**: Prefer `ls`, `find`, `grep`, `cat` before any modifications
- **Sandboxed Execution**: All bash commands must run inside ByteBot Docker container
- **No Network Writes**: Agents cannot make external network requests without explicit approval
- **File Size Limit**: Skip files larger than 1MB to preserve context window

## Allowed Commands

```bash
# Discovery
find . -type f -name "*.py"
ls -la
tree -L 3

# Analysis
grep -rn "pattern" .
cat filename.py | head -100
wc -l *.py

# Extraction
sed -n '10,20p' filename.py
head -50 README.md
```

## Forbidden Commands

```bash
# NEVER execute these
rm -rf *
sudo *
curl/wget to external hosts
git push (without explicit approval)
```

## Output Format

All agent reports must follow this structure:
1. **Summary**: One-line description of findings
2. **Evidence**: File paths and line numbers
3. **Confidence**: HIGH / MEDIUM / LOW
4. **Next Action**: Recommended follow-up

## 6-Phase Research Pipeline

When conducting autonomous research, follow this progression:

1. **CAPTURE**: Document the initial idea or problem
2. **SEARCH**: Use grep/find to locate relevant code patterns
3. **VALIDATE**: Cross-reference multiple sources
4. **FEASIBILITY**: Assess implementation complexity
5. **ROADMAP**: Create actionable implementation steps
6. **REPORT**: Synthesize findings into structured output
