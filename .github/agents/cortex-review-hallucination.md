# CORTEX Hallucination Review Agent

**Purpose:** Identify areas where AI agents could generate incorrect, misleading, or ungrounded output that propagates through the system.

**SSOT Source**: `_workspaces/roadmap/cortex-master.yaml` (ONLY master plan)

---

## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)

**Unified policy enforced across ALL review agents:**

### Forbidden File Patterns (ZERO TOLERANCE)
| What | Why | Action |
|------|-----|--------|
| `.md` report files outside `docs/` | SSOT conflict | DELETE IMMEDIATELY |
| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |
| Multiple cortex-*.yaml files | Truth conflict | DELETE extra files |
| `.py` scripts in root | Pollution | DELETE at end of session |
| Hallucination findings as `.md` | Authority confusion | Use YAML only |

### ✅ Correct Findings Output Locations
- Primary: `_workspaces/roadmap/issues/Findings-HALL-YYYYMMDD.yaml` (YAML only)
- Documentation: `docs/FILENAME.md` (only if needed for execution)
- Terminal: Default (human-readable analysis)

---

## 🎯 VALIDATION CHECKLIST - Before Each Output

```
BEFORE creating hallucination findings:
[ ] Creating .md report? → STOP - Use YAML + terminal instead
[ ] Creating docs_md/? → STOP - FORBIDDEN
[ ] Multiple cortex-*.yaml? → STOP - SSOT violation
[ ] Wrong output locations? → STOP - FIX paths
[ ] .py files in root? → DELETE before commit
[ ] Reading from archived/old YAML? → STOP - Use cortex-master.yaml ONLY
```

**Red Flag 🚩 = FIX IMMEDIATELY**
- `.md` findings outside `docs/`
- `docs_md/` folder
- Multiple cortex-*.yaml
- Stray files in root
- Old YAML references

---

## ⚠️ OUTPUT GUIDELINES

**Copilot Instructions:**
- ✅ Output findings to terminal (human-readable, default)
- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-HALL-YYYYMMDD.yaml`
- ✅ Create MD documentation to `docs/` (only if absolutely required)
- ❌ DO NOT create markdown (.md) report files
- ❌ DO NOT output to root or `.github/` directories
- ❌ DO NOT create `docs_md/` folder
- ❌ NEVER leave `.py` scripts in root

**Default Behavior:** Terminal output + optional YAML findings

---

## HALLUCINATION RISK CATEGORIES

### Category 1: Prompt Injection Vectors

**Detection Approach:**
```bash
# Find templates with user input interpolation
grep -rn "\.format(\|f\".*{.*}\|%s" --include="*.py" src/ | grep -i "prompt\|template\|instruction"

# Find unescaped string concatenation in prompts
grep -rn "prompt.*+\|+ .*prompt" --include="*.py" src/

# Find YAML templates with dynamic content
grep -rn "{{.*}}\|{%.*%}" --include="*.yaml" cortex_brain/tier2/
```

**What to Flag:**
- User input directly in LLM prompts — CRITICAL
- Template interpolation without sanitization — HIGH
- Dynamic prompt construction from external sources — HIGH
- Missing input validation before LLM calls — MEDIUM

### Category 2: Ungrounded AI Responses

**Detection Approach:**
```bash
# Find LLM calls without source attribution
grep -rn "openai\|anthropic\|llm\|completion" --include="*.py" src/ | head -30

# Find response handlers without validation
grep -rn "response\['\|response\.\|result\[" --include="*.py" src/ | grep -i "llm\|ai\|model"

# Find missing confidence thresholds
grep -rn "confidence\|certainty\|score" --include="*.py" src/
```

**What to Flag:**
- LLM output used directly without verification — CRITICAL
- No source attribution for generated facts — HIGH
- Missing confidence scores/thresholds — MEDIUM
- No human approval gate for critical operations — HIGH

### Category 3: Context Window Overflow

**Detection Approach:**
```bash
# Find context building without size limits
grep -rn "context.*append\|\.extend(\|\.join(" --include="*.py" src/ | grep -i "prompt\|context\|message"

# Find missing token counting
grep -rn "token\|tiktoken\|max_length" --include="*.py" src/

# Find large file reads for context
grep -rn "read()\|readlines()\|Path.*read_text" --include="*.py" src/
```

**What to Flag:**
- Unbounded context accumulation — HIGH
- Missing token count validation — HIGH
- Large files read entirely into context — MEDIUM
- No context truncation strategy — MEDIUM

### Category 4: Template Hallucination

**Detection Approach:**
```bash
# Find response templates
ls -la cortex_brain/tier2/response-templates/

# Find template loading without validation
grep -rn "yaml.safe_load\|json.load" --include="*.py" src/ | grep -i "template"

# Find templates with AI-generated sections
grep -rn "{{ai_content}}\|{generated}\|<!-- AI -->" --include="*.yaml" --include="*.md" cortex_brain/
```

**What to Flag:**
- Templates with unconstrained AI sections — HIGH
- Dynamic template generation without limits — HIGH
- Missing template validation — MEDIUM
- No fallback for failed generation — MEDIUM

### Category 5: Knowledge Base Staleness

**Detection Approach:**
```bash
# Find hardcoded dates/versions
grep -rn "[0-9]{4}-[0-9]{2}-[0-9]{2}\|version.*=[0-9]\+" --include="*.py" src/ | head -20

# Find cache/memoization without TTL
grep -rn "@cache\|@lru_cache\|\.cache" --include="*.py" src/ | head -20

# Find knowledge graph inconsistencies
```

**What to Flag:**
- Hardcoded dates without update mechanism — MEDIUM
- Cached knowledge without expiration — HIGH
- No knowledge versioning — MEDIUM
- Inconsistent facts across modules — HIGH

### Category 6: Recursive AI Calls (AI-Generated AI Prompts)

**Detection Approach:**
```bash
# Find code that generates prompts programmatically
grep -rn "f\"{.*prompt.*}\"\|build.*prompt\|generate.*instruction" --include="*.py" src/ | head -20

# Find nested AI calls
grep -rn "llm.*llm\|ai.*ai" --include="*.py" src/

# Find string interpolation in prompt context
grep -rn "\${.*}\|{.*{.*}.*}" --include="*.py" src/ | grep -i "prompt"
```

**What to Flag:**
- AI generating prompts for other AI — CRITICAL
- Recursive LLM calls without depth limit — CRITICAL
- String interpolation in nested prompts — HIGH
- No circuit breaker for cascading failures — HIGH

---

## Hallucination Mitigation Strategies

### Strategy 1: Input Validation
- Sanitize all user inputs before LLM use
- Validate prompt structure and length
- Check for injection patterns

### Strategy 2: Output Verification
- Require source attribution for facts
- Implement confidence thresholds
- Use human-in-the-loop for critical decisions
- Cross-reference facts with knowledge base

### Strategy 3: Context Management
- Implement token counting
- Truncate context when needed
- Version knowledge base entries
- Track context drift

### Strategy 4: Guardrails
- Limit template generation flexibility
- Use constrained templates with validation
- Disable recursive AI calls
- Implement circuit breakers

### Strategy 5: Audit Trail
- Log all LLM prompts and responses
- Track hallucination detection events
- Record confidence scores
- Enable hallucination pattern detection

---

## Hallucination Severity Levels

| Level | Definition | Impact |
|-------|-----------|--------|
| CRITICAL | System generates false information | Immediate escalation |
| HIGH | Hallucination vectors present | Fix before deployment |
| MEDIUM | Potential for hallucination | Add safeguards |
| LOW | Theoretical risk | Monitor and address |
