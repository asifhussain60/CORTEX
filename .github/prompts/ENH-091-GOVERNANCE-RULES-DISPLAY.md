# ENH-091: Intelligent Governance Rules Display Block

**Status:** PROPOSED  
**Authority:** cortex-architect.prompt.md § Intelligent Response Composition  
**Phase:** 91 (Post-Header-Format Correction)  
**Priority:** P1 (High-Value Feature)  
**Complexity:** Medium (3-4 days)  
**Token Budget:** ~200K (3-phase TDD cycle)

---

## 🎯 Executive Summary

**Problem:** InteractionOrchestrator lacks intelligent, selective display of CORE governance rules with book references. Currently, governance wisdom only appears in violation messages and enforcement contexts, missing opportunities for proactive education during normal interaction flows.

**Solution:** ENH-091 introduces a new semantic content block (BLOCK-GOVERNANCE-RULES) that intelligently selects and displays relevant CORE rules with authoritative book citations based on:
- User intent (IMPLEMENT/FIX/ANALYZE/AUDIT/PLAN)
- Conversation context (history + previous violations)
- Severity levels (P0/P1/P2)
- User expertise level (derived from interaction history)

**Outcome:** Users see contextually relevant governance wisdom proactively, building understanding and trust in CORTEX's rules without feeling lectured or patronized.

---

## 📊 Current State Analysis

### Existing Infrastructure (Production-Ready)

#### 1. **BusinessWisdomFormatter** ✅
- **Location:** `cortex/interaction/business_wisdom_formatter.py`
- **Status:** Complete, tested, in production
- **Capability:** Transforms CORE rule IDs → educational markdown with book citations
- **Format:** `**Principle** → RULE-ID (Book Author)`
- **Max Display:** 5 principles (prevents overwhelming users)
- **Example Output:**
  ```markdown
  ### 📚 Business Wisdom
  - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
  - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
  - **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)
  ```

#### 2. **Integration Points** ✅
- **EnforcementOrchestrator:** Uses BusinessWisdomFormatter to enrich governance violation messages
  - Method: `_format_governance_rule_with_book(rule_id)` (lines 1181-1223)
  - Context: Inline display (no icon, single rule, list marker stripped)
- **IntentRouter:** Enriches routing messages with book references
  - Method: `_format_routing_message_with_books(rule_id)` (lines 1858-1908)
  - Context: Intent classification feedback
- **Response Formatters:** SimpleResponseFormatter supports `business_wisdom` parameter
  - Displays section after header, before main content sections

#### 3. **Tests** ✅
- **EnforcementOrchestrator Tests:** 7 tests (book references, fallback, integration)
- **IntentRouter Tests:** 3 tests (book references, graceful degradation)
- **DoR Integration Tests:** 2 tests (context-aware wisdom display)
- **Formatter Tests:** 11 tests (format validation, edge cases, sorting)
- **Total:** 23 tests, all passing

#### 4. **Content Blocks Registry** ✅
- **Location:** `cortex-registry/_cortex-master/core/templates/content-blocks.yaml`
- **Current Blocks:** 7 (INTRO, CAPABILITIES, LENS, ORCHESTRATORS, TUTORIAL, ONBOARDING, NEXT-STEPS)
- **Status:** Production-ready (598 lines)
- **Personality Charter:** Defined + enforced in SemanticBlockAssembler

#### 5. **InteractionOrchestrator** ✅
- **Location:** `cortex/orchestrators/core/interaction_orchestrator.py`
- **Status:** Complete (701 lines)
- **Methods:**
  - `detect_intent(context)` — classifies user intent
  - `select_blocks_for_intent(intent)` — maps intent → block names
  - `select_blocks_for_context(context)` — conversation-aware selection
  - `assemble_response(context)` — personality-consistent markdown
  - `assemble_response_with_metrics(context)` — response + metrics

### Gap Analysis

| Capability | Status | Gap |
|----------|--------|-----|
| **Rule Loading** | ✅ Complete | None |
| **Formatting with Books** | ✅ Complete | None |
| **Enforcement Integration** | ✅ Complete | None |
| **Content Block Definition** | ✅ Complete | **←  NEW: BLOCK-GOVERNANCE-RULES needed** |
| **Intent-Based Selection** | ✅ Partial | **←  NEW: Rule selection for each intent** |
| **Context-Aware Display** | ✅ Partial | **←  NEW: Conversation history analysis** |
| **InteractionOrchestrator Wiring** | ✅ Partial | **←  NEW: Wire block into response assembly** |
| **User Expertise Adaptation** | ❌ Missing | **←  NEW: Track expertise, adjust depth** |
| **Response Template** | ✅ Exists | **←  NEW: DoR-compatible template** |

---

## 🏗️ Architecture Design

### 1. BLOCK-GOVERNANCE-RULES Content Block

**Purpose:** Intelligently display CORE governance rules with book references

**Design Principle:** "Less is more" — 2-3 rules max, highly contextual, always justified

**Structure:**
```yaml
governance_rules:
  id: "BLOCK-GOVERNANCE-RULES"
  name: "Contextual Governance Rules Display"
  length_words: 100
  purpose: "Display 2-3 relevant CORE rules with book citations based on intent"
  
  format:
    structure: "context_reason + rule_list"
    icons: "📚 for header"
    max_rules: 3
    include_icon: true
    include_context_reason: true
  
  intent_mappings:
    IMPLEMENT:
      rules: ["CORE-008", "CORE-011", "CORE-012", "CORE-001"]
      reason: "These principles ensure production-ready code"
      max_rules: 3
    
    FIX:
      rules: ["CORE-008", "CORE-027", "CORE-026"]
      reason: "Bug fixes maintain governance through audit trails"
      max_rules: 2
    
    ANALYZE:
      rules: ["CORE-030", "CORE-035", "CORE-036"]
      reason: "Analysis requires evidence-based truth and standards compliance"
      max_rules: 3
    
    AUDIT:
      rules: ["CORE-029", "CORE-025", "CORE-027"]
      reason: "Audits validate governance compliance"
      max_rules: 2
    
    PLAN:
      rules: ["CORE-042", "CORE-041", "CORE-001"]
      reason: "Planning uses hierarchical phases and event-driven patterns"
      max_rules: 2
    
    REFACTOR:
      rules: ["CORE-035", "CORE-011", "CORE-012"]
      reason: "Refactoring maintains code quality standards"
      max_rules: 2
```

### 2. Rule Selection Algorithm

**Intelligent Selection Logic:**
```python
def select_governance_rules_for_context(
    intent: str,
    conversation_history: List[Dict],
    previous_violations: List[str],
    user_expertise: str  # "junior" | "mid" | "senior"
) -> List[str]:
    """
    Select 2-3 most relevant CORE rules for display.
    
    Priority (in order):
    1. Rules related to recent violations (reinforcement)
    2. Rules related to current intent (proactive education)
    3. Rules user hasn't seen recently (knowledge building)
    
    Returns max 3 rules, adjusted for user expertise.
    """
```

**Selection Strategy:**
- **For violations:** Show related rule + similar rules (reinforcement learning)
- **For context:** Show intent-appropriate rules (contextual education)
- **For expertise:** Adjust depth and complexity
  - Junior: More explanatory rules (CORE-042, CORE-041)
  - Mid: Mixed depth (CORE-008, CORE-011, CORE-012)
  - Senior: Advanced governance (CORE-035, CORE-036, CORE-050)

### 3. InteractionOrchestrator Integration

**New Methods Required:**
```python
class InteractionOrchestrator:
    def select_governance_rules_for_context(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Select 2-3 governance rules for display based on intent."""
    
    def get_governance_rules_block(
        self,
        rule_ids: List[str],
        include_context_reason: bool = True
    ) -> str:
        """Generate formatted governance rules block."""
    
    def track_rule_exposure(
        self,
        rule_ids: List[str],
        session_id: str
    ) -> None:
        """Track which rules user has seen (prevent repetition)."""
```

**Integration Point:**
- In `assemble_response(context)` → call `get_governance_rules_block()` when appropriate
- Check session context: Don't show same rules within last 3 turns

### 4. Response Template

**Template Name:** "BLOCK-GOVERNANCE-RULES-WITH-REASON"

**Format:**
```markdown
### 📚 Governance Principles for {INTENT}

{CONTEXT_REASON}

{FORMATTED_RULES}

---

💡 **Why these matter:**
- {PRINCIPLE_1}: {BRIEF_BENEFIT}
- {PRINCIPLE_2}: {BRIEF_BENEFIT}
```

**Example Output (IMPLEMENT intent):**
```markdown
### 📚 Governance Principles for Implementation

These principles ensure your code meets CORTEX's production standards:

- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
- **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
- **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)

---

💡 **Why these matter:**
- TDD ensures quality through tests first (CORE-008)
- Type hints catch bugs at IDE time, not runtime (CORE-011)
```

---

## 📋 Implementation Plan (TDD)

### Phase 1: RED (Write Tests First)

**Test Files to Create:**
1. `tests/unit/orchestrators/core/test_governance_rules_block.py` (12 tests)
   - Intent-based rule selection (5 tests)
   - Conversation history analysis (3 tests)
   - Expertise-level adaptation (2 tests)
   - Violation tracking (2 tests)

2. `tests/integration/test_interaction_governance_rules.py` (8 tests)
   - End-to-end response assembly with rules block (3 tests)
   - Repetition prevention across turns (2 tests)
   - VSCode rendering validation (2 tests)
   - Performance validation (1 test)

**Total RED Phase Tests:** 20 tests (all failing)

### Phase 2: GREEN (Implement to Pass Tests)

**Files to Modify:**
1. `cortex/orchestrators/core/interaction_orchestrator.py`
   - Add `select_governance_rules_for_context(intent, context)`
   - Add `get_governance_rules_block(rule_ids, include_reason)`
   - Add `_track_rule_exposure(rule_ids, session_id)`
   - ~100 LOC

2. `cortex-registry/_cortex-master/core/templates/content-blocks.yaml`
   - Add BLOCK-GOVERNANCE-RULES definition
   - Add intent-to-rules mappings
   - ~80 lines YAML

3. `cortex/registry/semantic_blocks.py`
   - Update SemanticBlockAssembler to handle governance rules
   - Add rule selection logic
   - ~50 LOC

**Total GREEN Phase:** ~230 LOC of implementation

### Phase 3: REFACTOR (Optimize + Integrate)

**Improvements:**
1. Extract rule selection into dedicated strategy class
2. Add caching for rule metadata (performance)
3. Wire into response template system
4. Add observability (metrics for rule exposure)
5. Documentation + examples

**Total REFACTOR Phase:** ~150 LOC

---

## 🔗 Wiring Integration

### 1. Content Blocks Registry

Add BLOCK-GOVERNANCE-RULES to `content-blocks.yaml`:

```yaml
governance_rules:
  id: "BLOCK-GOVERNANCE-RULES"
  name: "Contextual Governance Rules Display"
  # ... (as defined above)
```

### 2. InteractionOrchestrator

Wire into `assemble_response(context)`:

```python
def assemble_response(self, context: Dict[str, Any]) -> str:
    # ... existing code ...
    
    # Step 4: Add governance rules block (NEW)
    if self._should_include_governance_block(context):
        intent = self.detect_intent(context)
        rule_ids = self.select_governance_rules_for_context(intent, context)
        if rule_ids:
            gov_block = self.get_governance_rules_block(rule_ids)
            sections.append(gov_block)
    
    # ... rest of assembly ...
```

### 3. Metrics Export

Track rule exposure for analytics:
```yaml
metrics:
  - rule_exposure: How many times each rule shown
  - intent_distribution: Which intents trigger governance blocks
  - user_expertise_correlation: How expertise level affects display
```

---

## 💾 State Management

### Session-Level Tracking

**Storage:** Lightweight in-memory + optional persistence

```python
@dataclass
class RuleExposureTracker:
    """Track rule exposure within a session to prevent repetition."""
    
    session_id: str
    turn_count: int
    rules_shown_history: Dict[str, int]  # rule_id → turn shown
    violations_history: List[str]  # recent violations
    
    def should_show_rule(self, rule_id: str, turns_since_last_show: int = 3) -> bool:
        """Only show rule if not shown in last N turns."""
```

---

## ✅ Acceptance Criteria

### AC-ENH091-001: Intent-Based Selection
- [ ] Each intent (IMPLEMENT/FIX/ANALYZE/AUDIT/PLAN/REFACTOR) maps to 2-3 relevant rules
- [ ] Rules displayed via BusinessWisdomFormatter
- [ ] Max 3 rules per display enforced

### AC-ENH091-002: Context-Aware Display
- [ ] Violation history prioritized (reinforcement)
- [ ] Conversation history considered (avoid repetition)
- [ ] User expertise level affects displayed depth

### AC-ENH091-003: Response Integration
- [ ] InteractionOrchestrator.assemble_response() includes governance block when appropriate
- [ ] VSCode Copilot Chat rendering verified (test on actual UI)
- [ ] Performance <50ms for rule selection

### AC-ENH091-004: User Experience
- [ ] Rules shown proactively, not punitively
- [ ] Context reason explains WHY these rules matter
- [ ] Never more than 3 rules displayed at once

### AC-ENH091-005: Testing & Metrics
- [ ] 28 tests total (20 unit + 8 integration)
- [ ] 100% code coverage for new methods
- [ ] Metrics exported for analytics dashboard

---

## 📈 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User Engagement** | 60% users click/read rule references | GA4 link clicks |
| **Repetition Prevention** | <2% rule repeats in same session | Session tracker analysis |
| **Performance** | <50ms rule selection latency | Metrics dashboard |
| **Coverage** | All 30 CORE rules represented | Registry audit |
| **Expertise Adaptation** | Distinct outputs for junior/mid/senior | A/B testing |

---

## 🚀 Deployment

### Phase Timeline
- **RED Phase:** 1 day (20 tests, all failing)
- **GREEN Phase:** 1.5 days (implementation)
- **REFACTOR Phase:** 1 day (optimization + integration)
- **Testing & Docs:** 0.5 days
- **Total:** 4 days

### Git Commits
1. `RED: ENH-091 tests for governance rules block (20 tests, all failing)`
2. `GREEN: Implement governance rules selection + display (228 LOC)`
3. `REFACTOR: Optimize rule selection, integrate with response assembly (150 LOC)`
4. `TEST: 28 tests passing, 100% coverage`
5. `DOCS: Add governance rules block documentation`

### Pre-Deployment Checklist
- [ ] All 28 tests passing
- [ ] 100% code coverage
- [ ] VSCode rendering tested on actual Copilot Chat
- [ ] Performance benchmarked (<50ms)
- [ ] No regressions in existing tests
- [ ] AC markers in place (AC_START → AC_COMPLETE)
- [ ] Pre-commit validation passing (16 MCP tools)

---

## 🎨 Design Principles

1. **Non-Intrusive:** Governance blocks appear contextually, not punitively
2. **Educative:** Teach WHY rules matter, not just that they exist
3. **Adaptive:** Adjust depth for user expertise level
4. **Respectful:** Never repeat rules within same session
5. **Evidence-Based:** Show book citations (build trust)
6. **Performant:** <50ms rule selection latency
7. **Testable:** TDD-first, all scenarios covered

---

## 📚 References

### Existing Infrastructure
- BusinessWisdomFormatter: `cortex/interaction/business_wisdom_formatter.py` (complete)
- EnforcementOrchestrator: `cortex/orchestrators/core/enforcement_orchestrator.py` (lines 1181-1223)
- IntentRouter: `cortex/orchestrators/core/intent_router.py` (lines 1858-1908)
- InteractionOrchestrator: `cortex/orchestrators/core/interaction_orchestrator.py` (701 lines)
- Content Blocks: `cortex-registry/_cortex-master/core/templates/content-blocks.yaml` (604 lines)

### Related Documentation
- `.github/prompts/business-wisdom-wiring.md`
- `.github/prompts/response-format-standards.md`
- `phase-06-business-wisdom-display-enhancement.yaml`

### Tests
- 23 existing tests for Business Wisdom (all passing)
- 31 tests for InteractionOrchestrator (all passing)
- Total test coverage: 54 tests in related areas

---

## 🔮 Future Extensions (ENH-092+)

1. **A/B Testing:** Measure impact of governance rules on code quality
2. **ML Personalization:** Predict which rules user should see based on history
3. **Governance Dashboards:** Track rule compliance over time
4. **Book Reference Library:** Expand book citations (currently 10+ books)
5. **Multi-Language Support:** Translate principles to different languages
6. **Slack/Email Notifications:** Send weekly governance summaries

---

**Authority:** This proposal aligns with:
- cortex-architect.prompt.md § Intelligent Response Composition
- CORE-030 (Implementation Truth)
- CORE-036 (Industry Standards Compliance)
- CORE-041 (Event-Driven Architecture)
- CORE-042 (Hierarchical Terminology)
- MCP-FIRST architecture

**Author:** GitHub Copilot (CORTEX Agent)  
**Date:** 2026-02-16  
**Version:** 1.0
