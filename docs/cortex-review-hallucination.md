# CORTEX Hallucination Review Agent

**Purpose:** Identify areas where AI agents could generate incorrect, misleading, or ungrounded output that propagates through the system.

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
- Missing template schema validation — MEDIUM
- Templates allowing arbitrary code execution — CRITICAL
- No output format verification — HIGH

### Category 5: Code Generation Risks

**Detection Approach:**
```bash
# Find eval/exec usage
grep -rn "eval(\|exec(" --include="*.py" src/

# Find dynamic code execution
grep -rn "subprocess\|os.system\|Popen" --include="*.py" src/

# Find code generation patterns
grep -rn "generate.*code\|code.*generation\|ast.parse" --include="*.py" src/
```

**What to Flag:**
- `eval()` or `exec()` with AI output — CRITICAL
- Running AI-generated commands — CRITICAL
- No sandboxing for generated code — HIGH
- Missing syntax validation — MEDIUM

---

## AUDIT LOG QUERIES FOR HALLUCINATION DETECTION

```sql
-- Find operations that might involve AI generation
SELECT operation, component, COUNT(*) as count
FROM audit_log
WHERE message LIKE '%generat%' 
   OR message LIKE '%LLM%'
   OR message LIKE '%AI%'
   OR message LIKE '%completion%'
GROUP BY operation, component
ORDER BY count DESC;

-- Find human approval operations (or lack thereof)
SELECT ac_id, operation, timestamp
FROM audit_log
WHERE operation LIKE '%APPROV%'
   OR operation LIKE '%REVIEW%'
   OR operation LIKE '%CONFIRM%'
ORDER BY timestamp DESC
LIMIT 50;

-- Find rapid successive operations (potential automation without review)
SELECT a1.ac_id, a1.timestamp as start, a2.timestamp as complete,
       (julianday(a2.timestamp) - julianday(a1.timestamp)) * 24 * 60 as minutes
FROM audit_log a1
JOIN audit_log a2 ON a1.ac_id = a2.ac_id
WHERE a1.operation = 'AC_START' 
  AND a2.operation = 'AC_COMPLETE'
  AND minutes < 1  -- Less than 1 minute: suspiciously fast
ORDER BY minutes ASC
LIMIT 20;

-- Find failed validations (potential hallucination catches)
SELECT ac_id, message, timestamp
FROM audit_log
WHERE message LIKE '%invalid%'
   OR message LIKE '%validation failed%'
   OR message LIKE '%schema%'
ORDER BY timestamp DESC
LIMIT 50;
```

---

## HALLUCINATION PREVENTION CHECKLIST

### For Every LLM Integration Point:

- [ ] **Input Sanitization**: User input cleaned before prompt inclusion?
- [ ] **Prompt Injection Defense**: System prompts separated from user content?
- [ ] **Output Validation**: AI response validated against schema?
- [ ] **Confidence Threshold**: Low-confidence responses flagged?
- [ ] **Source Attribution**: Generated facts traced to sources?
- [ ] **Human Gate**: Critical operations require human approval?
- [ ] **Audit Trail**: AI operations logged with context?
- [ ] **Token Limits**: Context window overflow prevented?
- [ ] **Code Safety**: Generated code sandboxed before execution?
- [ ] **Rollback Capability**: AI-generated changes reversible?

### Verification Queries:

```python
# Check if LENS has grounding requirements
grep -rn "source\|citation\|reference" src/core/intelligence/lens/

# Check if orchestrators have approval gates
grep -rn "approval\|confirm\|human_review" src/orchestrators/

# Check if templates have output validation
grep -rn "validate\|schema\|verify" src/core/templates/
```

---

## FINDING TEMPLATE

```yaml
finding:
  id: "HALLUC-XXX"
  agent: "cortex-review-hallucination"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "prompt_injection|ungrounded|context_overflow|template|code_generation"
  
  title: "[Specific hallucination risk description]"
  
  location:
    file: "src/path/to/file.py"
    lines: "123-145"
    function: "function_name"
  
  evidence:
    detection_method: "code_analysis|audit_query|prompt_review|manual_inspection"
    command_or_query: |
      [The exact command or query used]
    output: |
      [The actual output proving this finding]
  
  attack_vector: |
    How an attacker or bad data could exploit this:
    1. Input: [malicious input]
    2. System processes without validation
    3. AI generates [problematic output]
    4. Output is [used in harmful way]
  
  hallucination_scenario: |
    How incorrect AI output could propagate:
    1. AI generates [incorrect information]
    2. System accepts as truth
    3. Information propagates to [where]
    4. User/system acts on false information
    5. Consequence: [what happens]
  
  current_mitigation: "None|Partial|Adequate"
  mitigation_details: |
    What safeguards currently exist (if any).
  
  impact:
    data_integrity_risk: "AI-generated data persisted as fact"
    user_trust_risk: "Users may act on incorrect information"
    security_risk: "Prompt injection could escalate privileges"
    blast_radius: "Single response|Stored data|Propagated knowledge"
  
  remediation:
    effort: "1h|4h|1d|1w"
    approach: |
      1. Add input sanitization at [location]
      2. Implement output validation against [schema]
      3. Add human approval gate for [operation]
      4. Add audit logging for AI operations
    validation_required: true
    validation_description: "Test with known adversarial inputs"
  
  related_rules:
    - "CORE-019"  # TDD-Master routing (hallucination prevention)
    - "CORE-024"  # Observability (audit trail)
  
  llm_integration_point: "LENS|IntentRouter|CodeGenerator|TemplateEngine|Other"
```

---

## KNOWN HALLUCINATION PATTERNS FROM HISTORY

### Pattern 1: Unvalidated Code Generation

**From CORTEX 5.0:**
- AI generated code snippets without syntax validation
- Broken imports propagated to user
- **CHECK:** Is AST validation mandatory for generated code?

### Pattern 2: Intent Misclassification

**From CORTEX 4.0/5.0:**
- Keyword-based intent matching (not LLM)
- Wrong orchestrator invoked
- **CHECK:** Is LLMIntentClassifier with confidence threshold primary?

### Pattern 3: Context Accumulation Overflow

**From CORTEX 5.5:**
- LENS accumulated unlimited context
- Token limit exceeded → truncated responses
- **CHECK:** Is context windowing implemented?

### Pattern 4: Template Interpolation Without Escape

**From CORTEX 4.0:**
- User input in YAML templates
- YAML injection possible
- **CHECK:** Are template inputs sanitized?

---

## HUMAN-IN-THE-LOOP GATES

### Required Gates:

| Operation | Gate Requirement | Implementation |
|-----------|------------------|----------------|
| Code deployment | Human approval | PR review + CI gate |
| Schema changes | Human approval | Migration review |
| Knowledge ingestion | Human validation | Business domain approval |
| AC completion | Test evidence | Automated + human sign-off |
| Production changes | Change approval | Deployment gate |

### Verification:

```bash
# Check for approval gates in orchestrators
grep -rn "approval\|confirm\|human\|manual" src/orchestrators/ --include="*.py"

# Check for gates in critical operations
grep -rn "require.*approval\|must.*confirm\|human_gate" src/ --include="*.py"
```

---

## SEVERITY GUIDELINES

| Severity | Definition | Examples |
|----------|------------|----------|
| CRITICAL | Direct security risk or data corruption | Prompt injection, code execution |
| HIGH | Significant user impact | Wrong information persisted |
| MEDIUM | Workarounds available | Confidence scores missing |
| LOW | Edge cases only | Verbose AI responses |

---

## QUICK CHECK SCRIPT

```python
#!/usr/bin/env python3
"""
Hallucination risk checks for CORTEX.
Run: python scripts/hallucination_check.py
"""

import subprocess
from pathlib import Path

def check_prompt_injection():
    """Find potential prompt injection vectors."""
    result = subprocess.run(
        ["grep", "-rn", ".format(\\|f\".*{.*}", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    risky = [
        line for line in result.stdout.split('\n')
        if 'prompt' in line.lower() or 'template' in line.lower()
    ]
    return {
        "check": "prompt_injection",
        "potential_vectors": len(risky),
        "details": risky[:10]
    }

def check_eval_exec():
    """Find dangerous eval/exec usage."""
    result = subprocess.run(
        ["grep", "-rn", "eval(\\|exec(", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    violations = [line for line in result.stdout.split('\n') if line]
    return {
        "check": "eval_exec",
        "violations": len(violations),
        "details": violations
    }

def check_ai_output_validation():
    """Check if AI outputs are validated."""
    result = subprocess.run(
        ["grep", "-rn", "completion\\|response", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    lines_with_response = [l for l in result.stdout.split('\n') if l]
    
    validation_result = subprocess.run(
        ["grep", "-rn", "validate\\|schema\\|verify", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    validation_lines = len([l for l in validation_result.stdout.split('\n') if l])
    
    return {
        "check": "ai_output_validation",
        "response_handlers": len(lines_with_response),
        "validation_calls": validation_lines,
        "ratio": round(validation_lines / max(len(lines_with_response), 1), 2)
    }

if __name__ == "__main__":
    import json
    
    checks = [
        check_prompt_injection(),
        check_eval_exec(),
        check_ai_output_validation(),
    ]
    
    print(json.dumps({"hallucination_checks": checks}, indent=2))
```

---

## COPYRIGHT

Copyright © 2025-2026 Asif Hussain. All rights reserved.
