---
scope: non-production-admin
---
# Request Rephrase Orchestrator

**Authority:** MCP-First Architecture + Challenge-First Protocol | **Status:** ✅ ACTIVE | **Integration:** Pre-MasterOrchestrator Gate

---

## 🎯 Purpose

**Automatic context injection layer** that enhances EVERY user request with CORTEX architectural intelligence BEFORE handing to MasterOrchestrator.

**Why:** MasterOrchestrator makes perfect decisions when requests are "self-documenting" — containing governance rules, architecture context, wiring hints, risk assessment, and execution path guidance.

---

## 🔄 Orchestration Flow

```
USER REQUEST (raw)
    ↓
REPHRASE ORCHESTRATOR (automatic, always)
    ├─ Step 1: Parse intent + entity scope
    ├─ Step 2: Inject governance rules (CORE-XXX matching)
    ├─ Step 3: Inject architecture context (orchestrators, wiring, protocols)
    ├─ Step 4: Inject risk assessment + dependencies
    ├─ Step 5: Apply challenge-first protocol
    └─ Step 6: Output "self-documenting request"
    ↓
MASTER ORCHESTRATOR (enhanced context available)
    ├─ Intent Router (with governance pre-loaded)
    ├─ LENS Classification (with architecture hints)
    ├─ Challenge Gate (already evaluated via rephrase)
    └─ Execution (high confidence, zero waste)
```

---

## 📋 Rephrase Algorithm

### Step 1: Intent Parsing

**Input:** User request (raw natural language)  
**Output:** `{intent_type, entity_scope, confidence, ambiguity_level}`

```python
# Pseudo-code
intent = classify_primary_intent(request)  # IMPLEMENT|FIX|REFACTOR|ANALYZE|PLAN|DESIGN|DIGEST
scope = extract_scope(request)              # file|module|component|system|architecture
confidence = measure_confidence(request)     # 0.0-1.0
```

**Examples:**
```
"implement response templates" 
  → intent: IMPLEMENT, scope: module, confidence: 0.95

"follow cortex-architect.prompt.md and check holistically"
  → intent: QUERY, scope: architecture, confidence: 0.98 (explicit instructions)
```

### Step 2: Governance Rule Injection

**Input:** intent_type + entity_scope  
**Lookup:** cortex-registry/governance/CORE-rules.yaml

**Output:** List of applicable CORE rules with context

```yaml
# Example: IMPLEMENT intent on Python module
Applicable Rules:
  - CORE-002: File generation restrictions (allowed: .github/**/*.md)
  - CORE-008: TDD mandatory (tests before code)
  - CORE-011: Type hints required
  - CORE-012: Google-style docstrings required
  - CORE-049: Silent autonomous execution (if user says "proceed")
  - CORE-053: Auto-healing for infrastructure
```

**Injection format:**
```
GOVERNANCE RULES ACTIVE:
1. CORE-002: [context-specific explanation]
2. CORE-008: [context-specific explanation]
...
```

### Step 3: Architecture Context Injection

**Input:** intent_type, scope, governance rules  
**Lookup:** Architecture components from wiring

**Output:** Relevant orchestrators, protocols, integration points

```
ORCHESTRATOR ROUTING:
- Primary: {orchestrator_name}
- Path: MasterOrchestrator → {path}
- Wiring Status: {active|pending|deprecated}
- Integration Points: {components}

PROTOCOLS ACTIVE:
- ConversationProtocol (all intents)
- LENS Protocol (IMPLEMENT/FIX/REFACTOR/ANALYZE)
- Challenge-First Protocol (DESIGN/PLAN)
```

### Step 4: Risk Assessment

**Input:** Scope + governance rules + dependencies  
**Analysis:** Breaking risk, dependency graph, alternative approaches

**Output:** Risk matrix

```
Risk Assessment:
- Breaking Risk: {LOW|MEDIUM|HIGH}
- Reason: {explanation}
- Dependencies: {list}
- Alternative Approaches: {if any}
- Confidence: {%}
```

### Step 5: Challenge-First Evaluation

**Input:** Proposed approach + governance rules + architecture  
**Check:** Does this match CORTEX design pillars?

**Design Pillars:**
1. **Extensibility** — Can this be extended without modification?
2. **Scalability** — Does this scale to N concurrent users?
3. **Accuracy** — Are results deterministic?
4. **Team Collaboration** — Can others understand and maintain this?
5. **Long-term Maintainability** — Will this be a burden in 6 months?

**Output:** Challenge gate status

```
Challenge-First Protocol:
- Pillar Analysis: [table showing PASS/REVIEW/CONCERN for each pillar]
- Recommended Approach: {SINGLE BEST recommendation}
- Why: {executive summary}
- No Alternatives: Recommended approach addresses all tensions
```

### Step 6: Output Format

**CRITICAL: Single paragraph ONLY (copy-pasteable into new Copilot Chat session):**

**Template:**
```
{REFINED_REQUEST_AS_SINGLE_PARAGRAPH_WITH_CORTEX_CONTEXT_INLINE}
```

**Format Rules:**
- ✅ ONE paragraph of plain text (no markdown formatting)
- ✅ Remove filler words ("I think", "probably", "some kind of")
- ✅ Inject CORTEX technical context inline (e.g., "via TDDOrchestrator")
- ✅ Include relevant governance rules inline (e.g., "per CORE-008")
- ✅ Include orchestrator routing inline (e.g., "via {OrchestratorName}")
- ✅ Self-contained and copy-pasteable
- ❌ NO markdown headers, code blocks, tables, or bullet lists
- ❌ NO multi-paragraph output
- ❌ NO challenge protocol (that's for implementation mode)
- ❌ NO metrics or before/after comparisons

**Example Output:**
```
Implement user authentication for admin panel security via TDDOrchestrator with module-level scope, including JWT token validation, role-based access control, and secure session management following CORTEX governance rules CORE-008 (TDD mandatory) and CORE-011 (type hints required).
```

---

## 🚀 Execution Rules

### When to Rephrase

**ALWAYS (default):**
- Every user request triggers rephrase layer automatically
- No user action required
- Rephrase runs before any response generation

**EXCEPT (Skip if):**
- User explicitly says "rephrase: ..." (they're doing it manually)
- Request is DIAGNOSE/QUERY mode (educational, no execution risk)
- Request is internal tool call (not user-facing)

### Rephrase Output Disposition

| Intent | Display Rephrase | Hidden | Merged |
|--------|------------------|--------|--------|
| IMPLEMENT/FIX/REFACTOR | ✅ Inline | — | Yes (context for execution) |
| ANALYZE/AUDIT | ✅ Inline | — | Yes (context for analysis) |
| PLAN/DESIGN | ✅ Inline | — | Yes (context for design) |
| QUERY (educational) | — | ✅ | — (not execution) |
| Manual "rephrase:" | ✅ Inline | — | — (standalone) |

### Token Budget Integration

**Rephrase cost:** ~200-400 tokens (governance + architecture lookup)

**Savings:** 2-3x reduction in clarification turns + better first-try success rate

**Net impact:** Positive ROI after first iteration

---

## 🔌 Integration Points

### MasterOrchestrator Hook

```python
# In MasterOrchestrator.__init__ or main entry
def process_user_request(user_request: str) -> Response:
    # STEP 0: Auto-rephrase (NEW)
    rephrase = RequestRephraseOrchestrator.analyze(user_request)
    
    # Merge rephrase context into request
    enhanced_request = merge_context(user_request, rephrase)
    
    # STEP 1: Interaction Layer (existing)
    interaction_result = self.interaction_orchestrator.process(enhanced_request)
    
    # STEP 2: Intent Router (existing)
    intent = self.intent_router.classify(enhanced_request)
    
    # ... rest of pipeline
```

### Rephrase Display Rules

- Display AFTER user request is received
- Display BEFORE DoR approval gate
- Include in MCP tool invocation (as metadata)
- Log to audit trail

---

## 📊 Effectiveness Metrics

**Track:**
- Rephrase generation time (target: <200ms)
- Challenge gate effectiveness (% user agreement with recommendation)
- Breaking risk accuracy (% of assessed risks that materialized)
- Governance rule accuracy (% of injected rules that applied)
- Token savings (vs. manual rephrase + clarification)

---

## 🎓 Philosophy

**Request Rephrase = Architecture-Aware Request Enhancement**

By injecting governance, architecture, risk, and challenge context into EVERY request, we transform:

- **Reactive** MasterOrchestrator (guessing context) 
- → **Proactive** MasterOrchestrator (context provided)

Result: **Perfect decisions, zero waste, maximum scalability.**

---

*Authority: User Vision ("every request should be rephrased before MasterOrchestrator") + Challenge-First Protocol + MCP-First Architecture*
