# CORTEX Review Agent: Hallucination Analysis
## AI Safety, Injection Vectors & Unvalidated Output

**Purpose:** Identify AI safety risks: unvalidated LLM output, prompt injection, missing guardrails, unsafe code generation.

---

## CHECKS PERFORMED

### 1. Unvalidated LLM Output Execution

**What to look for:**
- LLM-generated code executed without validation
- No confidence scoring before action
- Missing grounding checks
- Direct eval() of LLM output

**Search patterns:**
```bash
# eval() or exec() with LLM input
grep -rn "eval(\|exec(" cortex/ --include="*.py" | grep -v "# safe:"

# LLM integration without validation
grep -rn "claude\|gpt\|openai\|anthropic" cortex/ --include="*.py"

# Generated code paths
grep -rn "generate.*code\|code.*generation" cortex/ --include="*.py" -i
```

**Key concerns:**
- `cortex/mcp/` - MCP tool execution (validates LLM tool calls?)
- `cortex/brain/tier2/` - Code generation features
- `cortex/execution/` - Execution of generated workflows

---

### 2. Prompt Injection Vectors

**What to look for:**
- User input directly in prompts
- Template interpolation without escaping
- No input sanitization
- Jailbreak-susceptible prompt structure

**Search patterns:**
```bash
# Direct format strings
grep -rn "f\".*{.*prompt.*}\|f\".*{.*input.*}" cortex/ --include="*.py"

# Template rendering
grep -rn "\.format(\|\.substitute(\|render(" cortex/ --include="*.py"

# Unsafe string concatenation
grep -rn "str +\|\" + str(" cortex/ --include="*.py"
```

**Critical files:**
- `cortex/templates/` - Template safety?
- `cortex/tools/template_validator.py` - Validation logic
- `cortex/mcp/` - Tool parameter injection

---

### 3. MCP Protocol Compliance

**What to look for:**
- Tool definitions missing input schema
- No type validation on parameters
- Missing error handling for tool calls
- Tool exposure without authorization

**Verify:**
```bash
# MCP tool definitions
find cortex/mcp -name "*.py" -exec grep -l "@mcp_tool\|tool_schema" {} \;

# Tool parameter validation
grep -rn "validate.*parameter\|check.*input\|schema" cortex/mcp/ --include="*.py"

# Tool authorization
grep -rn "permission\|authorize\|role.*check" cortex/mcp/ --include="*.py"
```

**Expected:**
- All tools have input schemas
- All parameters have type annotations
- All tool calls validate inputs
- Tool exposure controlled by permissions

---

### 4. Missing Input Sanitization

**What to look for:**
- SQL injection vectors
- Path traversal vulnerabilities
- Script injection in shell commands
- XSS vectors in templates

**Search patterns:**
```bash
# SQL queries with direct string concat
grep -rn "SELECT.*{.*}\|INSERT.*{.*}\|UPDATE.*{.*}" cortex/ --include="*.py"

# Shell execution
grep -rn "os.system(\|subprocess.*shell=True" cortex/ --include="*.py"

# Path operations on user input
grep -rn "open(user_\|open(.*request\|os.path.join(.*user" cortex/ --include="*.py"

# Template rendering with user data
grep -rn "jinja\|render.*user\|template.*request" cortex/ --include="*.py"
```

**Key files:**
- `cortex/api/` - HTTP endpoint input handling
- `cortex/cli/` - CLI argument parsing
- `cortex/tools/` - Tool input handling

---

### 5. Unsafe Template Interpolation

**What to look for:**
- Autoescape disabled
- User content in templates
- Unsafe Jinja2 filters
- No context isolation

**Verify in:**
- `cortex/templates/` directory
- All uses of `jinja2.Template()`
- Template rendering in `cortex/tools/`

**Checks:**
```bash
grep -rn "autoescape=False\|autoescape.*False" cortex/ --include="*.py"
grep -rn "Template(" cortex/ --include="*.py" | grep -v "autoescape=True"
```

---

### 6. Code Generation Without Grounding

**What to look for:**
- Generated code not traced to source requirements
- No verification against spec
- Missing test generation alongside code
- Hallucinated features

**Verify:**
- Is code generation tied to specific AC requirements?
- Are generated classes/methods validated against schema?
- Do tests exist for generated code?
- Is generation deterministic (repeatable)?

**Check files:**
- `cortex/scripts/` - Code generation scripts
- `cortex/mcp/tools/` - Tool generation
- `cortex/templates/` - Template expansion

---

### 7. Missing Confidence Thresholds

**What to look for:**
- Actions taken without confidence scoring
- No uncertainty handling
- Fallback-on-confidence missing
- Always-trusting behavior

**Search patterns:**
```bash
# Confidence checks
grep -rn "confidence\|certainty\|score" cortex/ --include="*.py" | grep -v test

# Decisions without confidence
grep -rn "if.*llm\|if.*gpt\|if.*claude" cortex/ --include="*.py" | grep -v "confidence\|score"
```

**Expected:**
- All LLM-based decisions have confidence scoring
- Low-confidence paths have fallbacks
- High-risk operations require high confidence

---

### 8. Human-in-the-Loop Gaps

**What to look for:**
- No approval gates for high-risk operations
- No logging of autonomous decisions
- Missing "why" documentation
- No reversal/rollback capability

**Verify:**
- Critical operations require review
- All autonomous actions are logged
- Decisions are reversible
- Users can understand why decision was made

---

## OUTPUT FORMAT

Create: `_workspaces/roadmap/issues/findings-hallucination-YYYYMMDD.yaml`

```yaml
hallucination_findings:
  metadata:
    review_date: "YYYYMMDD"
    total_issues: X
    by_severity:
      critical: Y
      high: Z
      medium: A
    
  critical_issues:
    - issue_id: "HALL-001"
      category: "UNVALIDATED_EXECUTION"
      severity: "CRITICAL"
      location: "cortex/mcp/tools/code_generator.py:XX"
      description: "Generated code executed without validation"
      vulnerability: "LLM-generated code directly executed with eval()"
      impact: "Arbitrary code execution if LLM compromised or jailbroken"
      evidence:
        - "Tool returns code_output without schema validation"
        - "Executor calls eval(code_output) without checks"
        - "No confidence scoring on generation"
      remediation: "Validate generated code structure, type annotations, and dependencies"
      blocking_phase: "arch-011-hallucination"
      
    - issue_id: "HALL-002"
      category: "PROMPT_INJECTION"
      severity: "CRITICAL"
      location: "cortex/templates/template_resolver.py:XX"
      description: "User input directly in LLM prompts"
      vulnerability: "Prompt injection via user-controlled parameters"
      impact: "LLM jailbreak, unauthorized actions, information disclosure"
      evidence:
        - "User input interpolated in prompt template"
        - "No escaping or sanitization"
        - "No input length limits"
      remediation: "Sanitize input, use structured prompts, implement input validation"
      
  high_severity_issues:
    - issue_id: "HALL-003"
      category: "MCP_COMPLIANCE"
      severity: "HIGH"
      location: "cortex/mcp/tools/XX"
      description: "Tool parameters lack input schema"
      vulnerability: "Type confusion, unexpected input types"
      impact: "Tool execution errors, potential crashes"
      evidence:
        - "Tool definition missing @param_schema"
        - "No type hints on tool functions"
        - "No parameter validation"
      remediation: "Add comprehensive input schemas to all tools"
      
  recommendations:
    - "Implement input validation framework for all user-facing APIs"
    - "Add prompt injection detection and blocking"
    - "Require confidence thresholds for all LLM-based decisions"
    - "Implement code signing for generated code"
    - "Add human approval gate for high-risk operations"
```

---

## DECISION TREE

```
For each potential hallucination issue:

Q1: Is LLM output executed without validation?
  → YES: CRITICAL hallucination (arbitrary execution)
  → NO: Next question

Q2: Can user input influence LLM prompts?
  → YES: CRITICAL hallucination (injection vector)
  → NO: Next question

Q3: Is generated code safety-checked?
  → NO: HIGH hallucination (code safety gap)
  → YES: Next question

Q4: Is there human approval for high-risk actions?
  → NO: MEDIUM hallucination (autonomous risk)
  → YES: LOW or no issue
```

---

## VALIDATION

Before finalizing findings:
- [ ] Vulnerability is exploitable (not theoretical)
- [ ] Attack path is realistic and documented
- [ ] Impact includes user harm scenarios
- [ ] Evidence includes code locations and patterns
- [ ] Remediation is specific and implementable
