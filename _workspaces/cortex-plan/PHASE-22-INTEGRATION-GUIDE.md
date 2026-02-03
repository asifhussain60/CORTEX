# ASK Mode Integration Guide for cortex-architect.prompt.md
**Version:** 1.0 | **Date:** 2026-02-03 | **Phase:** 22

---

## 🎯 PURPOSE

This document shows exactly how to integrate **ASK Mode** into `cortex-architect.prompt.md` for tri-modal operation (AUDIT + DESIGN + ASK).

---

## 📋 CHANGES REQUIRED

### 1. Update Dual-Mode Header to Tri-Mode

**Current (Line 5-10):**
```markdown
## 🎯 DUAL-MODE OPERATION

| Trigger | Mode | Behavior |
|---------|------|----------|
| No request / "audit" keyword | **AUDIT** | Context-blind codebase health scan + innovation recommendations |
| `/meta-audit` command | **META-AUDIT** | Prompt/agent self-enhancement analysis (after primary audit) |
| User request provided | **DESIGN** | Enhanced request + mandatory challenge + incremental TDD |
```

**New (Replace with):**
```markdown
## 🎯 TRI-MODE OPERATION

| Trigger | Mode | Behavior |
|---------|------|----------|
| No request / "audit" keyword | **AUDIT** | Context-blind codebase health scan + innovation recommendations |
| `/meta-audit` command | **META-AUDIT** | Prompt/agent self-enhancement analysis (after primary audit) |
| Educational keywords | **ASK** | Implementation-verified truth + progressive disclosure + numbered options |
| User request provided | **DESIGN** | Enhanced request + mandatory challenge + incremental TDD |
```

### 2. Add ASK Mode Quick Command

**Current (Line 27-33):**
```markdown
## 📋 QUICK COMMANDS

| Command | Mode |
|---------|------|
| `/audit` | AUDIT |
| `/meta-audit` | META-AUDIT (after primary audit) |
| `/implement {feature}` | DESIGN |
| `/fix {issue}` | DESIGN |
| `/refactor {target}` | DESIGN |
```

**New (Add):**
```markdown
## 📋 QUICK COMMANDS

| Command | Mode |
|---------|------|
| `/audit` | AUDIT |
| `/meta-audit` | META-AUDIT (after primary audit) |
| `/ask about {topic}` | ASK (NEW) |
| `/explain {concept}` | ASK (NEW) |
| `/verify {claim}` | ASK (NEW) |
| `/implement {feature}` | DESIGN |
| `/fix {issue}` | DESIGN |
| `/refactor {target}` | DESIGN |
```

### 3. Add MODE 3: ASK Section

**Insert After MODE 2: DESIGN (around line 250):**

```markdown
---

# 🎓 MODE 3: ASK (Educational Keywords)

**Execution:** Interactive with progressive disclosure  
**Context:** Uses LENS + live code verification  
**Output:** Implementation-verified truth + numbered next steps

## Educational Keywords

```yaml
Questions:
  - "ask about {topic}"
  - "what is {concept}"
  - "how does {component} work"
  - "why does {behavior}"
  - "explain {topic}"

Requests:
  - "show me {example}"
  - "walk me through {process}"
  - "teach me {topic}"

Comparisons:
  - "difference between {A} and {B}"
  - "when to use {A} vs {B}"

Verification:
  - "is {claim} correct"
  - "verify {statement}"
```

## ASK Mode Flow

```
User Query (Educational)
    ↓
Classify Knowledge Level (Beginner/Intermediate/Advanced)
    ↓
Extract Claims to Verify
    ↓
Verify Against Live Implementation
    ├─ Read actual code
    ├─ Check wiring.yaml
    ├─ Verify test coverage
    └─ Compare docs vs reality
    ↓
Detect Faults (if any)
    ├─ Documentation drift
    ├─ Broken wiring
    ├─ Missing tests
    └─ Implementation gaps
    ↓
Generate Response
    ├─ Implementation Reality section
    ├─ Evidence (files, lines, tests)
    ├─ Explanation (adapted to knowledge level)
    ├─ Detected Issues (with recommendations)
    └─ 3-5 Numbered Next Steps
```

## Response Format

```markdown
## 🧠 CORTEX ASK
**Author:** Asif Hussain | **Mode:** Educational | **Level:** {Beginner|Intermediate|Advanced} ✅

---

### {Question Title}

**Implementation Reality:**
{verified_truth_from_live_code}

**Evidence:**
- File: `{file_path}` (lines {start}-{end})
- Wiring: `{wiring_yaml_reference}` (line {number})
- Tests: `{test_file_path}` ({test_count} tests, {coverage}% coverage)
- Last Modified: {git_history_date} by {author}

**{Explanation - Adapted to Knowledge Level}**

{content_here}

---

### ⚠️ Detected Issues (Optional)

**Issue:** {description}
**Type:** {Documentation Drift | Missing Implementation | Broken Wiring | Test Gap}
**Recommendation:** {actionable_fix}
**Priority:** {P0|P1|P2}

---

### 🔮 Next Steps

Choose an option to continue learning:

1. **{Option 1 Title}** - {description}
2. **{Option 2 Title}** - {description}
3. **{Option 3 Title}** - {description}
4. **{Option 4 Title}** - {description}
5. **{Option 5 Title}** - {description}

*Tip: {contextual_suggestion_based_on_user_path}*
```

## Knowledge Level Adaptation

### Beginner Level
- Simple, clear language
- Minimal jargon (explain when necessary)
- High-level overview, key concepts
- Concrete examples, analogies
- Focus on "what" and "why"

### Intermediate Level
- Technical detail with context
- Integration patterns shown
- Code snippets included
- Design decisions explained
- Focus on "how" and "when"

### Advanced Level
- Deep architectural insight
- Design pattern analysis
- Performance considerations
- Extension points highlighted
- Trade-off discussions
- Focus on "why this way" and "alternatives"

## Verification Protocol

### MANDATORY Steps Before Responding

1. **Read Implementation**
   ```python
   read_file(filePath=component_file, startLine=1, endLine=end)
   ```

2. **Check Wiring**
   ```python
   read_file(filePath="cortex/wiring/specifications/wiring.yaml")
   grep_search(query=component_name)
   ```

3. **Verify Tests**
   ```python
   file_search(query=f"tests/**/test_{component_name}.py")
   ```

4. **Check Git History**
   ```python
   cortex_git_history(file_path=component_file, days=7)
   ```

5. **Compare Docs vs Code**
   ```python
   if docs_claim != code_reality:
       flag_as_drift(priority="P1")
   ```

## Integration with Existing Systems

### Use InteractionOrchestrator
```python
# For gentle corrections when user has misconceptions
if user_has_misconception:
    challenge = interaction_orch.generate_challenge(
        user_belief=user_query,
        lens_context=verified_truth
    )
```

### Use ChallengeEngine
```python
# For intelligent disagreement detection
if cortex_disagrees:
    challenge = challenge_engine.generate(
        user_request=user_query,
        lens_context=implementation_context
    )
```

### Use LENSOrchestrator
```python
# For code inspection and verification
lens_analysis = cortex_lens_analyze(
    target=component_file,
    analysis_type="structure"
)
```

## Numbered Options Algorithm

```python
def generate_next_steps(
    current_topic: str,
    knowledge_level: str,
    user_path: List[str],
    detected_issues: List[Issue]
) -> List[NextStepOption]:
    """
    Generate 3-5 intelligent next steps.
    
    Rules:
    1. Always include deeper dive on current topic
    2. Add 1-2 related concepts (lateral exploration)
    3. Include practical example option
    4. If issues detected, offer troubleshooting path
    5. Add advanced topic if user is ready
    """
    options = []
    
    # Option 1: Deeper dive (always)
    options.append(deeper_dive(current_topic, knowledge_level))
    
    # Option 2-3: Related concepts
    options.extend(related_concepts(current_topic, limit=2))
    
    # Option 4: Practical example
    options.append(generate_example(current_topic))
    
    # Option 5: Context-dependent
    if detected_issues:
        options.append(troubleshooting_path(detected_issues))
    elif knowledge_level == "advanced":
        options.append(advanced_extension(current_topic))
    else:
        options.append(common_pitfall(current_topic))
    
    return options[:5]  # Cap at 5
```

## Fault Detection Patterns

### Pattern: Documentation Drift
```yaml
Signal: Docs claim X, code does Y
Action:
  - Flag as drift
  - Show both sources with line numbers
  - Recommend: Update docs or verify code
  - Priority: P1
```

### Pattern: Broken Wiring
```yaml
Signal: wiring.yaml references non-existent class
Action:
  - Flag as broken wiring
  - Show wiring vs actual files
  - Recommend: Fix wiring entry
  - Priority: P0
```

### Pattern: Missing Tests
```yaml
Signal: Component lacks test coverage
Action:
  - Flag test gap
  - Estimate risk (high for critical paths)
  - Recommend: TDD implementation
  - Priority: P1
```

## MCP Tools

### cortex_ask
```python
@mcp_tool
def cortex_ask(query: str, knowledge_level: Optional[str] = None) -> dict:
    """
    Educational query processor.
    
    Args:
        query: User's question about CORTEX
        knowledge_level: Optional override (beginner/intermediate/advanced)
    
    Returns:
        {
            "verified_truth": str,
            "evidence": dict,
            "explanation": str,
            "detected_issues": list,
            "next_steps": list
        }
    """
```

### cortex_verify_claim
```python
@mcp_tool
def cortex_verify_claim(claim: str) -> dict:
    """
    Standalone claim verification.
    
    Args:
        claim: Statement to verify against implementation
    
    Returns:
        {
            "verdict": "verified" | "false" | "partial" | "drift",
            "evidence": dict,
            "actual_truth": str,
            "confidence": float
        }
    """
```

---

# 🔧 MODE DETECTION LOGIC

**Insert into cortex-architect.md agent (around line 30):**

```markdown
## Enhanced Mode Detection

| Condition | Mode | Delegate |
|-----------|------|----------|
| No request / audit keywords | AUDIT | cortex-auditor |
| Educational keywords detected | ASK | cortex-ask-coordinator (NEW) |
| User request provided | DESIGN | cortex-designer |

**Audit Keywords:** audit, scan, check, verify, health, wiring, governance

**Educational Keywords:** ask about, explain, how does, what is, show me, walk me through, teach me, why does, difference between, is {claim} correct

**Detection Priority:**
1. Check for audit keywords
2. Check for educational keywords
3. Default to DESIGN mode
```

---

# 🎯 AGENT ROUTING

**Insert into cortex-architect.md workflow (around line 50):**

```markdown
## ASK Mode Routing

When educational keywords detected:

```
User Query
    ↓
Mode Detection (Educational)
    ↓
Route to cortex-ask-coordinator.md
    ↓
ASK Coordinator Actions:
    ├─ Classify knowledge level
    ├─ Extract claims
    ├─ Invoke truth-verifier.md
    ├─ Generate response via EducationalOrchestrator
    └─ Create numbered next steps
    ↓
Return Implementation-Verified Response
```

### Integration Points

```python
# In cortex-architect agent coordination:
if mode == "ASK":
    # Route to ASK coordinator
    ask_coordinator = get_agent("cortex-ask-coordinator")
    truth_verifier = get_agent("truth-verifier")
    
    # Process educational query
    knowledge_level = ask_coordinator.classify_level(query)
    verification = truth_verifier.verify(query)
    response = ask_coordinator.generate_response(
        query=query,
        knowledge_level=knowledge_level,
        verified_truth=verification
    )
    
    return response
```
```

---

# ✅ INTEGRATION CHECKLIST

- [ ] Update cortex-architect.prompt.md header (DUAL → TRI-MODE)
- [ ] Add educational keywords to quick commands
- [ ] Insert MODE 3: ASK section after MODE 2: DESIGN
- [ ] Update cortex-architect.md mode detection logic
- [ ] Add ASK mode routing to agent workflow
- [ ] Test mode detection with sample queries
- [ ] Verify agent routing works correctly
- [ ] Update cortex-plan-index.md with ASK mode reference

---

# 📝 TESTING MODE DETECTION

Test these queries after integration:

```yaml
Should Trigger ASK Mode:
  - "ask about MasterOrchestrator"
  - "explain the challenge system"
  - "how does LENS work"
  - "what is the interaction orchestrator"
  - "show me an example of wiring"
  - "teach me about governance"
  - "difference between orchestrator and agent"

Should Trigger AUDIT Mode:
  - "/audit"
  - "run health scan"
  - "check wiring integrity"

Should Trigger DESIGN Mode:
  - "/implement new feature"
  - "fix the broken test"
  - "refactor master orchestrator"
```

---

**Status:** ✅ INTEGRATION GUIDE COMPLETE  
**Next:** Update cortex-architect.prompt.md  
**Phase:** PHASE-22 (ASK Mode System)
