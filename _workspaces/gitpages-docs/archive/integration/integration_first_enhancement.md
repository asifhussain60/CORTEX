"""
Integration-First Enhancement for copilot-instructions.md

AC_START: AC-INTEGRATION-004
Description: Add intent classification and MCP routing to copilot instructions
Authority: ROOT-CAUSE-ANALYSIS-2026-02-08 (P0: MCP-FIRST Enforcement Missing)

This content should be inserted into copilot-instructions.md after the MCP section.
"""

# Content to add to copilot-instructions.md after line ~400

INTEGRATION_FIRST_SECTION = """
---

## 🎯 INTENT CLASSIFICATION & MCP ROUTING (MANDATORY)

**Authority:** AC-INTEGRATION-001 | **Trigger:** Every user request

### Auto-Execute Before Processing

**STEP 1: Classify User Intent**

```
User Request Analysis:
┌─ Keywords Detection
├─ "fix" / "broken" / "error" → FIX intent
├─ "implement" / "add" / "create" → IMPLEMENT intent
├─ "refactor" / "improve" / "clean" → REFACTOR intent
├─ "analyze" / "explain" / "why" → ANALYZE intent
├─ "audit" / "compliance" / "health" → AUDIT intent
└─ "plan" / "design" / "strategy" → PLAN intent
```

**STEP 2: Determine MCP Requirement**

| Intent | MCP Required | Tool | Enforcement |
|--------|--------------|------|-------------|
| **IMPLEMENT** | ✅ YES | `cortex_process_request` | BLOCKING |
| **FIX** | ✅ YES | `cortex_process_request` | BLOCKING |
| **REFACTOR** | ✅ YES | `cortex_process_request` | BLOCKING |
| **ANALYZE** | ✅ YES | `cortex_lens_analyze` | BLOCKING |
| **AUDIT** | ✅ YES | `cortex_lens_analyze` | BLOCKING |
| **PLAN** | ✅ YES | `cortex_plan_setup` | BLOCKING |
| **QUERY** | ⚠️ OPTIONAL | None | INFO |

**STEP 3: Validate MCP Availability (If Required)**

```python
if intent.requires_mcp():
    result = check_mcp_availability()
    if not result.is_available():
        BLOCK with message:
        result.get_block_message()
        return HALT_EXECUTION
    
    # Route to MCP tool
    tool = get_mcp_tool(intent)
    return invoke_mcp_tool(tool, request)
```

**STEP 4: Execute** (If no MCP required)

Proceed with analysis/response.

---

### MCP Tool Reference

**cortex_process_request** - Main Implementation Tool
- **Purpose:** TDD-based implementation (tests before code)
- **When to use:** IMPLEMENT, FIX, REFACTOR intents
- **Input:** User request, target file/feature
- **Output:** Code changes + generated tests + validation
- **Example:** `cortex_process_request(operation="FIX", target="visualizations.js", request="Fix packages.slice error")`

**cortex_lens_analyze** - Code Intelligence & Analysis
- **Purpose:** Analyze code structure, find issues, understand problems
- **When to use:** ANALYZE, AUDIT intents, or when understanding errors
- **Input:** File path, analysis type (AST|security|complexity|duplicates)
- **Output:** Detailed analysis report with line numbers and severity
- **Example:** `cortex_lens_analyze(file="visualizations.js", include_ast=true)`

**cortex_challenge** - Risk Assessment & Alternatives
- **Purpose:** Generate challenge gate with risk scoring and alternatives
- **When to use:** Before major changes, when validation needed
- **Input:** Proposed change, affected components
- **Output:** Risk score, challenge gate, recommended alternatives
- **Example:** `cortex_challenge(operation_type="IMPLEMENT", scope="dashboard-refactor")`

**cortex_plan_setup** - Phase Planning
- **Purpose:** Initialize phase execution with setup hooks
- **When to use:** When starting a PLAN intent or new phase
- **Input:** Phase ID, stage count, acceptance criteria
- **Output:** Phase context, completion checklist, resource requirements
- **Example:** `cortex_plan_setup(phase_id="phase-45", stages=6)`

---

### Intent Classification Examples

**Example 1: User says "fix dashboard HTML errors"**
```
Input: "fix dashboard HTML errors"
Analysis:
  ✅ Intent: FIX
  ✅ MCP Required: YES
  ✅ Tool: cortex_process_request
  ✅ Enforcement: BLOCKING

Flow:
  1. Validate MCP available
  2. Invoke cortex_process_request with FIX operation
  3. TDD mode: Tests first, then fixes
  4. Auto-generated validation
  5. Commit results
```

**Example 2: User says "why isn't console-log showing this error"**
```
Input: "why isn't console-log showing this error"
Analysis:
  ✅ Intent: ANALYZE
  ✅ MCP Required: YES
  ✅ Tool: cortex_lens_analyze
  ✅ Enforcement: BLOCKING

Flow:
  1. Validate MCP available
  2. Invoke cortex_lens_analyze on relevant file
  3. AST analysis to detect type mismatches
  4. Identify root cause
  5. Suggest fix via cortex_process_request
```

**Example 3: User says "what are the deployment options?"**
```
Input: "what are the deployment options?"
Analysis:
  ✅ Intent: QUERY
  ✅ MCP Required: NO
  ✅ Enforcement: INFO

Flow:
  1. Respond directly with information
  2. No MCP invocation needed
```

---

### Integration-First Enforcement Rules

**RULE 1: Intent Classification is Automatic**
- ❌ DON'T wait for explicit command
- ✅ DO classify intent from natural language
- ✅ DO block if required tools unavailable

**RULE 2: MCP-FIRST for Implementation**
- ❌ DON'T use create_file / replace_string_in_file for IMPLEMENT/FIX/REFACTOR
- ✅ DO route to cortex_process_request
- ✅ DO show clear error if MCP unavailable

**RULE 3: Tool Invocation is Explicit**
- ✅ DO call MCP tools with clear parameters
- ✅ DO show tool invocation in response
- ✅ DO wait for tool results before proceeding

**RULE 4: No Silent Fallbacks**
- ❌ DON'T skip MCP and do direct edits
- ❌ DON'T bypass validation gates
- ✅ DO fail loudly if MCP unavailable

---

### Integration-First Flow Diagram

```
User Request
    ↓
Classify Intent
    ↓
MCP Required?
    ├─ YES → Check MCP Available?
    │         ├─ YES → Invoke MCP Tool → Execute → Complete
    │         └─ NO → BLOCK + Show Error
    └─ NO → Process Directly → Complete
```

"""

# Instructions for integration
INTEGRATION_INSTRUCTIONS = """
Add this content to .github/copilot-instructions.md:

1. Locate: Line 400 (after MCP ACTIVATION section)
2. Insert: INTEGRATION_FIRST_SECTION content above
3. Test: On next "fix" or "implement" request, verify:
   - Intent classification runs first
   - MCP tool is invoked (not direct file edit)
   - Tool name appears in response
   - Results are validated
4. Commit: git add .github/copilot-instructions.md
           git commit -m "Integration-First: Add intent classification and MCP routing"
"""

print(__doc__)
print(INTEGRATION_INSTRUCTIONS)

# AC_COMPLETE: AC-INTEGRATION-004 ✅
