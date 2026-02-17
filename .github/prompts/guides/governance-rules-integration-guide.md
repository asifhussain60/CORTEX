# InteractionOrchestrator × BusinessWisdomFormatter Integration Guide

**Updated:** 2026-02-16  
**Authority:** ENH-091 + cortex-architect.prompt.md  
**Status:** PROPOSAL  
**Phase:** 91 (Design → Implementation)

---

## 🎯 Quick Answer to Your Question

> **"Will the interaction orchestrator intelligently and selectively show the book references bound to the CORE governance rules?"**

**Current Status:** ✅ **Partially YES** (infrastructure exists, wiring incomplete)

### What Already Works (Production-Ready)

| Component | Status | Feature | Location |
|-----------|--------|---------|----------|
| **BusinessWisdomFormatter** | ✅ Complete | Loads rules + formats with book refs | `cortex/interaction/business_wisdom_formatter.py` (300 LOC) |
| **EnforcementOrchestrator** | ✅ Integrated | Shows rules on violations | `cortex/orchestrators/core/enforcement_orchestrator.py` (line 1181+) |
| **IntentRouter** | ✅ Integrated | Shows rules for routing decisions | `cortex/orchestrators/core/intent_router.py` (line 1858+) |
| **Response Formatters** | ✅ Integrated | Renders business wisdom sections | `cortex/orchestrators/response/simple_response_formatter.py` (line 27) |
| **Content Blocks Registry** | ✅ Complete | 7 reusable blocks (templates) | `cortex-registry/core/templates/content-blocks.yaml` (604 LOC) |

### What's Missing (ENH-091 Scope)

| Capability | Status | What's Needed |
|-----------|--------|--------------|
| **BLOCK-GOVERNANCE-RULES** | ❌ Missing | Semantic content block definition for governance rules |
| **Intent-Based Rule Selection** | ✅ Partial | Map each intent (IMPLEMENT/FIX/ANALYZE/etc) → relevant rules |
| **Conversation-Aware Display** | ⚠️ Partial | Track rule exposure per session, avoid repetition |
| **InteractionOrchestrator Integration** | ⚠️ Partial | Wire rule selection into `assemble_response()` method |
| **User Expertise Adaptation** | ❌ Missing | Adjust rule depth based on user skill level |

---

## 🏗️ Architecture: How It Works (When Complete)

```
User Input (e.g., "implement user auth")
    ↓
InteractionOrchestrator.assemble_response(context)
    ↓
    ├─ Step 1: detect_intent("implement user auth")
    │   → Intent = IMPLEMENT
    │
    ├─ Step 2: select_governance_rules_for_context(
    │              intent="IMPLEMENT",
    │              context={"violations": [...], "turn": 3}
    │          )
    │   → Selected Rules = ["CORE-008", "CORE-011", "CORE-012"]
    │   → Reason: "These principles ensure production-ready code"
    │
    ├─ Step 3: get_governance_rules_block(
    │              rule_ids=["CORE-008", "CORE-011", "CORE-012"],
    │              include_reason=True
    │          )
    │   → Calls BusinessWisdomFormatter.format_governance_with_books()
    │   → Returns markdown with book references
    │
    └─ Step 4: Assemble full response with governance block
        → User sees:
           ### 📚 Governance Principles for Implementation
           
           These principles ensure your code meets CORTEX's production standards:
           
           - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
           - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
           - **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)
           
           💡 **Why these matter:**
           - TDD ensures quality through tests first
           - Type hints catch bugs at IDE time, not runtime
```

---

## 📦 Integration Points

### 1. Content Blocks Registry (NEW - ENH-091)

**File:** `cortex-registry/core/templates/content-blocks.yaml`

**Add Block Definition:**
```yaml
governance_rules:
  id: "BLOCK-GOVERNANCE-RULES"
  name: "Contextual Governance Rules Display"
  length_words: 100
  purpose: "Display 2-3 relevant CORE rules with book citations based on intent"
  
  format:
    structure: "context_reason + rule_list + benefit_explanation"
    icons: "📚"
    max_rules: 3
    include_context_reason: true
  
  intent_mappings:
    IMPLEMENT:
      rules: ["CORE-008", "CORE-011", "CORE-012"]
      reason: "These principles ensure production-ready code"
      max_rules: 3
    
    ANALYZE:
      rules: ["CORE-030", "CORE-035", "CORE-036"]
      reason: "Analysis requires evidence-based truth and standards compliance"
      max_rules: 3
    
    # ... (FIX, AUDIT, PLAN, REFACTOR mappings)
```

### 2. InteractionOrchestrator (ENHANCE - ENH-091)

**File:** `cortex/orchestrators/core/interaction_orchestrator.py`

**New Methods:**
```python
def select_governance_rules_for_context(
    self,
    intent: str,
    context: Dict[str, Any]
) -> List[str]:
    """
    Select 2-3 governance rules relevant to user's intent.
    
    Priority:
    1. Rules related to recent violations (reinforce)
    2. Rules matching intent (educate proactively)
    3. Rules not shown recently (knowledge building)
    
    Returns max 3 rule IDs from registry mappings.
    """

def get_governance_rules_block(
    self,
    rule_ids: List[str],
    include_context_reason: bool = True
) -> str:
    """
    Generate formatted governance rules block.
    
    Uses BusinessWisdomFormatter to create markdown with:
    - Context reason (WHY these rules)
    - Formatted rules with book references
    - Benefit explanation
    
    Returns markdown string ready for response assembly.
    """

def _track_rule_exposure(
    self,
    rule_ids: List[str],
    session_id: str
) -> None:
    """Track which rules shown to prevent repetition."""
```

**Update `assemble_response()`:**
```python
def assemble_response(self, context: Dict[str, Any]) -> str:
    # ... existing code ...
    
    # NEW: Add governance rules block
    if self._should_include_governance_block(context):
        intent = self.detect_intent(context)
        rule_ids = self.select_governance_rules_for_context(intent, context)
        
        if rule_ids:
            gov_block = self.get_governance_rules_block(rule_ids)
            sections.append(gov_block)  # Add before main content
            self._track_rule_exposure(rule_ids, context.get('session_id'))
    
    # ... rest of assembly ...
```

### 3. Response Template System (ENHANCE - ENH-091)

**File:** `.github/prompts/response-format-standards.md`

**Template:** "BLOCK-GOVERNANCE-RULES-WITH-REASON"

```markdown
### 📚 Governance Principles for {INTENT}

{CONTEXT_REASON}

{FORMATTED_RULES_FROM_BUSINESSWISDOMFORMATTER}

---

💡 **Why these matter:**
{BENEFIT_LIST}
```

---

## 💡 How BusinessWisdomFormatter is Used

### Method: `format_governance_with_books()`

**Location:** `cortex/interaction/business_wisdom_formatter.py` (lines 83-135)

**Input:**
```python
formatter = BusinessWisdomFormatter()
markdown = formatter.format_governance_with_books(
    rule_ids=["CORE-008", "CORE-011", "CORE-012"],
    max_display=3,
    include_icon=True
)
```

**Output:**
```markdown
### 📚 Business Wisdom
- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
- **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
- **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)
```

**Features:**
- ✅ Automatically loads rules from governance registry
- ✅ Formats with arrow notation: `**Principle** → RULE-ID (Book Author)`
- ✅ Max 5 principles enforced (configurable via `max_display`)
- ✅ Severity-sorted (P0 → P1 → P2)
- ✅ Graceful degradation (missing books still display principle)

### Current Usage (Already Wired)

| Orchestrator | Method | Context |
|-------------|--------|---------|
| **EnforcementOrchestrator** | `_format_governance_rule_with_book(rule_id)` | Violation messages |
| **IntentRouter** | `_format_routing_message_with_books(rule_id)` | Intent classification |
| **SimpleResponseFormatter** | `business_wisdom` parameter | Response sections |

---

## 📋 User Response Template Options

### Option 1: Proactive Education (Default - ENH-091)

Shows governance rules contextually during normal interactions:

```markdown
# 🧠 CORTEX IMPLEMENT
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### 📚 Governance Principles for Implementation

These principles ensure your code meets CORTEX's production standards:

- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
- **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
- **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)

---

### 📋 Definition of Ready

[... rest of response ...]
```

### Option 2: Violation Context (Already Wired)

Shows rules when governance violations detected:

```
❌ GOVERNANCE VIOLATION
Rule: **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
Issue: Tests not found before implementation
```

### Option 3: Intent Routing (Already Wired)

Shows rules when routing between orchestrators:

```
🔀 ROUTING TO: TDDOrchestrator
Reason: **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
```

---

## 🔄 Session-Level State Management

### What Gets Tracked (ENH-091)

```python
@dataclass
class RuleExposureTracker:
    """Track rule exposure within session to prevent repetition."""
    
    session_id: str
    turn_number: int
    rules_shown: Dict[str, int]  # rule_id → turn shown
    violations_history: List[str]  # recent violations for reinforcement
    
    def should_show_rule(self, rule_id: str, turns_since_min: int = 3) -> bool:
        """Only show if not shown in last N turns."""
        last_shown = self.rules_shown.get(rule_id, -999)
        return (self.turn_number - last_shown) > turns_since_min
```

### Logic

- **Don't repeat rules in same session** (within 3 turns)
- **Prioritize violated rules** (reinforce what user got wrong)
- **Show proactively, not punitively** (context explains why)

---

## 🎯 Implementation Checklist (ENH-091)

### RED Phase (Write Tests First)
- [ ] Create `tests/unit/orchestrators/core/test_governance_rules_block.py` (12 tests)
  - [ ] Intent-based rule selection (5 tests)
  - [ ] Conversation history analysis (3 tests)
  - [ ] Expertise-level adaptation (2 tests)
  - [ ] Violation tracking (2 tests)
- [ ] Create `tests/integration/test_interaction_governance_rules.py` (8 tests)
  - [ ] End-to-end assembly with rules block (3 tests)
  - [ ] Repetition prevention (2 tests)
  - [ ] VSCode rendering (2 tests)
  - [ ] Performance (<50ms) (1 test)

### GREEN Phase (Implement)
- [ ] Add BLOCK-GOVERNANCE-RULES to `content-blocks.yaml`
- [ ] Implement `select_governance_rules_for_context()` in InteractionOrchestrator
- [ ] Implement `get_governance_rules_block()` in InteractionOrchestrator
- [ ] Implement `_track_rule_exposure()` in InteractionOrchestrator
- [ ] Update `assemble_response()` to include governance block
- [ ] All 20 tests passing

### REFACTOR Phase (Optimize)
- [ ] Extract rule selection into dedicated strategy class
- [ ] Add caching for rule metadata (performance optimization)
- [ ] Add observability (metrics for rule exposure)
- [ ] Update `content-blocks.yaml` with all intent mappings
- [ ] Add documentation + examples
- [ ] All 28 tests passing with 100% coverage

---

## 📊 Governance Rules Available (30 Total)

### P0 (Blocking - Critical)
- CORE-008: TDD Mandatory (Red-Green-Refactor)
- CORE-011: Type Hints Mandatory
- CORE-012: Google-Style Docstrings
- CORE-030: Implementation Truth
- CORE-050: MCP Circuit Breaker

### P1 (Warning - Important)
- CORE-001: Incremental Delivery (≤500 LOC)
- CORE-025: Git Discipline
- CORE-026: Checkpoint Commits
- CORE-027: Audit Trail
- CORE-028: File Naming
- CORE-035: Single Canonical Implementation
- CORE-036: Industry Standards Compliance
- CORE-041: Event-Driven Architecture
- CORE-042: Hierarchical Terminology

### P2 (Info - Guidance)
- CORE-002: No Markdown File Generation
- CORE-004: No Silent Failures
- CORE-013: No Bare Except
- CORE-019: TDD Routing
- CORE-029: Response Header
- CORE-031-040: Domain-specific rules
- CORE-048: Holistic Validation Gate
- CORE-049: Silent Autonomous Execution
- CORE-051: Cross-Platform MCP
- CORE-052: Single Branch Policy
- CORE-053: Auto-Healing Infrastructure

---

## 🚀 Why This Matters

### Current State (Gap)
- ❌ Users only see rules when they violate them (reactive, punitive)
- ❌ No proactive education about WHY rules exist
- ❌ No context for when/why specific rules apply
- ❌ No respect for repetition (same rule shown multiple times)

### With ENH-091 (Solution)
- ✅ Users see relevant rules proactively (teaching, not punishing)
- ✅ Rules shown with book citations (build trust + knowledge)
- ✅ Rules selected intelligently by intent (contextual education)
- ✅ No repetition within session (respectful UX)
- ✅ Adapt depth to user expertise level (personalized learning)

### Impact
- **User Trust:** "CORTEX understands why these rules matter"
- **Knowledge Building:** Rules become part of learning journey
- **Compliance:** Higher governance adherence through understanding
- **Confidence:** Users feel supported, not controlled

---

## 📚 Related Files & References

### Core Implementation
- `cortex/interaction/business_wisdom_formatter.py` — Rule formatting (300 LOC, complete)
- `cortex/orchestrators/core/interaction_orchestrator.py` — Response assembly (701 LOC)
- `cortex-registry/core/templates/content-blocks.yaml` — Block definitions (604 LOC)

### Integration Points
- `cortex/orchestrators/core/enforcement_orchestrator.py` (lines 1181-1223) — Violation context
- `cortex/orchestrators/core/intent_router.py` (lines 1858-1908) — Intent routing
- `cortex/orchestrators/response/simple_response_formatter.py` (line 27) — Response rendering

### Tests
- `tests/unit/orchestrators/core/test_enforcement_orchestrator_books.py` — 7 tests
- `tests/unit/orchestrators/core/test_intent_router_wisdom.py` — 3 tests
- `tests/unit/orchestrators/core/test_dor_wisdom_integration.py` — 2 tests
- `tests/unit/interaction/test_business_wisdom_formatter.py` — 11 tests

### Documentation
- `.github/prompts/business-wisdom-wiring.md` — Integration guide
- `.github/prompts/response-format-standards.md` — Template standards
- `phase-06-business-wisdom-display-enhancement.yaml` — Enhancement spec

---

## 💬 To Answer Your Question Directly

> **"Is there a user response template for this that can be wired in with interaction and other orchestrators?"**

**Answer:** ✅ **YES** — Multiple templates available, ready for wiring:

1. **Block Definition:** BLOCK-GOVERNANCE-RULES (ENH-091, needs creation)
2. **Integration Method:** BusinessWisdomFormatter.format_governance_with_books()
3. **Orchestrator Method:** InteractionOrchestrator.get_governance_rules_block() (ENH-091, needs implementation)
4. **Response Template:** "BLOCK-GOVERNANCE-RULES-WITH-REASON" (ENH-091, needs creation)
5. **Wiring Location:** InteractionOrchestrator.assemble_response() (ENH-091, needs update)

**Status:**
- ✅ 60% infrastructure exists (BusinessWisdomFormatter, rules loaded, tests)
- ⚠️ 40% wiring needed (content block def, orchestrator methods, integration)

**Effort:** 3-4 days TDD (RED → GREEN → REFACTOR → DOCS)

---

**Author:** GitHub Copilot (CORTEX Agent)  
**Date:** 2026-02-16  
**Authority:** ENH-091 + cortex-architect.prompt.md + MCP-FIRST

