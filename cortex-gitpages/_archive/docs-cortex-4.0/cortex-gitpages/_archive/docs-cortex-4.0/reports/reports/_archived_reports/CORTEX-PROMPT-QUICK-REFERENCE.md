# CORTEX Prompt - Quick Reference Guide

**File:** `.github/prompts/CORTEX.prompt.md`  
**Purpose:** Master Orchestrator + Intent Router system prompt for working with real repositories  
**Version:** 1.0  
**Date:** January 15, 2026

---

## What This Prompt Does

This system prompt enables CORTEX agents to:

1. **Understand Intent Deeply** - Parse what users really want (not just what they say)
2. **Analyze Real Repositories** - Use LENS protocol to gather holistic context
3. **Route Intelligently** - Decide where to execute (planning, code, TDD, etc.)
4. **Enforce Governance** - All output complies with CORTEX rules
5. **Require Approval** - Present for user confirmation BEFORE execution
6. **Generate Governance-Compliant Code** - Type hints, docstrings, tests, documentation

---

## Quick Navigation

| Section | Purpose | When to Use |
|---------|---------|------------|
| **Core Identity** | Understand the agent's role | Setup/orientation |
| **Master Orchestrator Pattern** | 4-stage execution pattern | Architecture understanding |
| **LENS Protocol** | Multi-source intelligence gathering | Deep context building |
| **Repository Analysis Workflow** | Step-by-step process | Working with real repos |
| **Governance Integration** | Governance rule enforcement | Compliance checking |
| **Real Repository Workflow** | Full example flow | Practical execution |
| **Decision Trees** | Intent routing decisions | Routing logic |
| **Error Handling** | Fallbacks and error recovery | Robustness |

---

## Key Concepts

### LENS Protocol (5-Step Intelligence Gathering)

```
L - Language Understanding   → Parse natural language intent
E - Examination (AST)        → Analyze code structure
N - Navigation (Git)         → Understand history & context
S - Synthesis (Comments)     → Extract developer intent
S - Synthesis (Relationships)→ Map impact & dependencies
```

### 4-Stage Master Orchestrator Process

```
STAGE 1: INTENT COMPREHENSION
→ Build complete understanding of what user wants

STAGE 2: INTENT ROUTING
→ Decide where to execute (planning, TDD, query, etc.)

STAGE 3: KNOWLEDGE INTEGRATION
→ Merge governance + company context

STAGE 4: APPROVAL GATE
→ Present for user confirmation before executing
```

### Governance Tiers

```
TIER 0: Immutable core rules (28 rules)
        - Apply to ALL operations
        - No exceptions allowed
        - Examples: CORE-008 (tests first), CORE-011 (type hints)

TIER 1: Domain-specific rules
        - interaction-rules.yaml (comprehension)
        - planning-rules.yaml (planning)
        - tdd-rules.yaml (code)
```

---

## How to Use This Prompt

### For LLM Agents (GPT, Claude, etc.)

**To use as a system prompt:**

1. Copy the full content of `.github/prompts/CORTEX.prompt.md`
2. Use as system message in your LLM API call
3. Add user repository path in user message
4. Agent will automatically follow the 4-stage pattern

**Example:**
```python
import anthropic

client = anthropic.Anthropic()

# Load CORTEX prompt
with open(".github/prompts/CORTEX.prompt.md") as f:
    cortex_prompt = f.read()

# User request
user_request = """
Repository: /Users/alice/projects/myapp
Task: Add rate limiting to login endpoint
"""

# Call agent
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    system=cortex_prompt,
    messages=[{
        "role": "user",
        "content": user_request
    }]
)

print(response.content[0].text)
```

### For Human Developers

**To understand how to work with Master Orchestrator:**

1. Read **Core Identity** section (understand the role)
2. Read **LENS Protocol** section (learn intelligence gathering)
3. Review **Real Repository Workflow** example (practical execution)
4. Use **Decision Trees** when routing decisions needed
5. Reference **Governance Integration** for compliance checking

---

## Real-World Examples

### Example 1: Adding Feature to Real Repo

```
USER PROVIDES:
  Repository: /Users/bob/projects/api
  Request: "Add email verification to registration"

MASTER ORCHESTRATOR FOLLOWS:
  1. Scan repository structure
  2. Run LENS protocol on registration code
  3. Generate holistic context document
  4. Identify challenges (security, testing, etc.)
  5. Suggest mitigations and recommendations
  6. Ask clarifying questions
  7. Wait for user approval
  
USER CONFIRMS:
  "Yes, async email, 24-hour expiry, block unverified users"
  
MASTER ORCHESTRATOR EXECUTES:
  1. Generate tests (RED → GREEN)
  2. Generate code (governance-compliant)
  3. Generate documentation
  4. Show git diff
  5. Output: Ready to merge
```

### Example 2: Fixing Bug in Real Repo

```
USER PROVIDES:
  Repository: /Users/carol/projects/webapp
  Request: "Users can't reset passwords - timeout error"

MASTER ORCHESTRATOR FOLLOWS:
  1. Parse intent: FIX, severity: HIGH
  2. Analyze password reset code (AST)
  3. Check git history (why does this fail?)
  4. Look for error handling gaps
  5. Identify root cause
  6. Propose fix with minimal disruption
  7. Present challenges (backward compat? fallback?)
  8. Ask for confirmation
  
USER CONFIRMS:
  "Add automatic retry, log errors for monitoring"
  
MASTER ORCHESTRATOR EXECUTES:
  1. Generate retry logic with backoff
  2. Add error logging
  3. Generate tests for failure scenarios
  4. Update documentation
  5. Show git diff
```

---

## Testing This Prompt

### Test 1: Simple Query

```
Input: "What does our user authentication look like?"
Expected: LENS protocol runs, returns analysis of auth module
```

### Test 2: Intent Understanding

```
Input: "I need to refactor the database layer for performance"
Expected: 
- Parses intent: REFACTOR
- Asks: What specific bottleneck?
- Asks: Performance metric? (latency, throughput?)
- Asks: Backward compatibility requirements?
```

### Test 3: Repository Analysis

```
Input: Repository path + "What's the impact of adding rate limiting?"
Expected:
- Scans repository
- Runs LENS on relevant files
- Identifies affected endpoints
- Lists tests that need updates
- Proposes implementation approach
```

### Test 4: Governance Compliance

```
Input: "Generate a function to parse user input"
Expected:
- Generated code has type hints ✓
- Generated code has docstrings ✓
- Generated code has error handling ✓
- References CORE rules in explanation ✓
```

---

## Integration Points

### With CORTEX Infrastructure

**These tools are referenced in the prompt:**

| Tool | Location | Purpose |
|------|----------|---------|
| ASTIntelligenceEngine | `src/core/intelligence/ast_intelligence.py` | Parse code structure |
| GitHistoryAnalyzer | `src/core/intelligence/git_history_analyzer.py` | Analyze git history |
| CommentAnalyzer | `src/core/intelligence/comment_analyzer.py` | Extract comments/docstrings |
| RelationshipTraversalEngine | `src/core/intelligence/relationship_traversal.py` | Map dependencies |
| MasterOrchestrator | `src/orchestrators/core/master_orchestrator.py` | Route operations |
| Governance Rules | `cortex_brain/tier0/governance/*.yaml` | Enforce rules |

### With LLM Providers

**Compatible with:**
- ✅ OpenAI (GPT-4)
- ✅ Anthropic (Claude)
- ✅ Google (Gemini)
- ✅ Open source (Llama, Mistral)

---

## Common Workflows

### Workflow 1: Adding a New Feature

```
1. User: "Add feature X to repository Y"
2. Agent: Runs LENS, identifies where feature fits
3. Agent: Presents architecture & test plan
4. User: "Yes, proceed"
5. Agent: Generates code, tests, docs (all governance-compliant)
6. Output: Ready to merge
```

### Workflow 2: Fixing a Bug

```
1. User: "Urgent: Feature X is broken"
2. Agent: Analyzes root cause
3. Agent: Proposes minimal fix + tests
4. User: "Approved"
5. Agent: Generates fix, tests, documentation
6. Output: Ready to deploy
```

### Workflow 3: Code Review & Governance

```
1. User: "Is this code governance-compliant?"
2. Agent: Checks against CORTEX rules
3. Agent: Reports violations & suggestions
4. Agent: Optionally generates compliant version
5. Output: Compliance report + fixes
```

---

## Advanced Features

### Feature 1: Confidence Scoring

Agent assigns confidence score (0-1.0) to understanding.

- 0.95+: "I'm very confident"
- 0.80-0.95: "I'm fairly confident, but..."
- 0.70-0.80: "I need clarification on..."
- <0.70: "I don't understand yet, please clarify:"

### Feature 2: Challenge-Based Routing

Agent identifies challenges and routes based on severity:

- CRITICAL: Block execution, redesign required
- HIGH: Warn, require mitigation
- MEDIUM: Inform, allow with mitigations
- LOW: Document, proceed normally

### Feature 3: Audit Trail

Every decision is logged:
- What intent was understood?
- Why was this routing chosen?
- Which governance rules applied?
- What challenges were identified?
- What mitigations were recommended?

---

## Troubleshooting

### Problem: Agent Doesn't Understand Intent

**Solution:** Provide more context
```
Good: "Add rate limiting to prevent brute force attacks on login"
Bad: "Add rate limiting"

Good: "Fix performance issue where queries take >2 seconds"
Bad: "Fix performance"
```

### Problem: Agent Routes to Wrong Path

**Solution:** Clarify constraints
```
Good: "Must maintain backward compatibility with v1 API"
Bad: "Make it better"

Good: "Timeline: must ship this week"
Bad: "When can you do it?"
```

### Problem: Agent Doesn't Follow Governance

**Solution:** Ensure governance files are present
```
Required files:
✓ cortex_brain/tier0/governance/core-rules.yaml
✓ cortex_brain/tier0/governance/interaction-rules.yaml
✓ cortex_brain/tier0/governance/tdd-rules.yaml
```

---

## Summary

**CORTEX.prompt.md is your system prompt for:**

✅ Understanding user intent deeply  
✅ Analyzing real repositories using LENS protocol  
✅ Routing operations intelligently  
✅ Enforcing governance rules  
✅ Generating governance-compliant code  
✅ Requiring user approval before execution  

**Use it by:**

1. Loading it as system prompt in your LLM
2. Providing repository path + user request
3. Agent follows 4-stage Master Orchestrator process
4. Agent presents comprehension for approval
5. Agent generates deliverables (code, tests, docs)
6. All output is governance-compliant and audit-logged

---

**Next Steps:**

1. ✅ Review `.github/prompts/CORTEX.prompt.md`
2. ✅ Test with a real repository
3. ✅ Integrate with your LLM provider
4. ✅ Start using Master Orchestrator pattern

Questions? Check the full `CORTEX.prompt.md` file for detailed examples and workflows.
