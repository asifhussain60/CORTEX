# CORTEX Governance Rules Display Architecture (ENH-091)

**Status:** PROPOSED | **Authority:** cortex-architect.prompt.md § Intelligent Response Composition | **Date:** 2026-02-16

---

## 🏗️ System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        INTERACTION FLOW (ENH-091)                          │
└────────────────────────────────────────────────────────────────────────────┘

USER INPUT
   │
   ├─ "implement user auth"
   ├─ "fix validation bug"
   ├─ "analyze performance"
   └─ "audit codebase"
   
   ↓
   
┌─────────────────────────────────────────────────────────────────────────────┐
│ InteractionOrchestrator.assemble_response(context)                          │
│                                                                             │
│ INPUT: context = {                                                          │
│   "user_input": "implement user auth",                                      │
│   "turn_number": 2,                                                         │
│   "session_id": "session-123",                                              │
│   "violations": ["CORE-008", "CORE-012"],  ← Recent violations              │
│   "conversation_history": [...]                                             │
│ }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
   │
   ├─ STEP 1: detect_intent(context)
   │   └─→ Intent = "IMPLEMENT"
   │
   ├─ STEP 2: select_governance_rules_for_context(intent, context)
   │   │
   │   └─→ PRIORITY LOGIC:
   │       1. Check for recent violations → reinforce
   │       2. Match intent to registry rules → educate
   │       3. Check exposure tracker → avoid repetition
   │       4. Select top 2-3 rules
   │       5. Sort by severity (P0 → P1 → P2)
   │
   │   └─→ Selected Rules: ["CORE-008", "CORE-011", "CORE-012"]
   │
   ├─ STEP 3: get_governance_rules_block(rule_ids, include_reason=True)
   │   │
   │   ├─→ Load block template from content-blocks.yaml
   │   │   - BLOCK-GOVERNANCE-RULES
   │   │   - intent_mappings["IMPLEMENT"]
   │   │   - context_reason: "These principles ensure production-ready code"
   │   │
   │   ├─→ Call BusinessWisdomFormatter.format_governance_with_books()
   │   │   │
   │   │   ├─→ Load rules from governance registry
   │   │   ├─→ Format with arrow notation: **Principle** → RULE-ID (Book)
   │   │   ├─→ Sort by severity (P0 → P1 → P2)
   │   │   └─→ Return markdown:
   │   │       ### 📚 Business Wisdom
   │   │       - **Red-Green-Refactor** → CORE-008 (TDD by Kent Beck)
   │   │       - **Type Hints** → CORE-011 (Clean Code by Robert Martin)
   │   │       - **Docstrings** → CORE-012 (Pragmatic Programmer)
   │   │
   │   └─→ gov_block = formatted markdown string
   │
   ├─ STEP 4: _track_rule_exposure(rule_ids, session_id)
   │   └─→ Update RuleExposureTracker:
   │       - Track which rules shown in this session
   │       - Record turn number
   │       - Prevent repetition within N turns
   │
   ├─ STEP 5: Assemble full response
   │   │
   │   ├─→ Response sections = []
   │   ├─→ sections.append(header)  ← "# 🧠 CORTEX"
   │   ├─→ sections.append(gov_block)  ← GOVERNANCE RULES (NEW - ENH-091)
   │   ├─→ sections.append(dor_section)  ← DoR/Intent Classification
   │   ├─→ sections.append(main_content)  ← Task breakdown
   │   ├─→ sections.append(commands)  ← Next steps
   │   │
   │   └─→ return "\n\n".join(sections)
   │
   ↓

OUTPUT (User sees in VSCode Copilot Chat):

┌─────────────────────────────────────────────────────────────────────────────┐
│ # 🧠 CORTEX IMPLEMENT                                                       │
│ **Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅             │
│                                                                             │
│ ---                                                                         │
│                                                                             │
│ ### 📚 Governance Principles for Implementation                             │
│                                                                             │
│ These principles ensure your code meets CORTEX's production standards:      │
│                                                                             │
│ - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)           │
│ - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)         │
│ - **Google-Style Docstrings** → CORE-012 (Pragmatic Programmer)             │
│                                                                             │
│ 💡 **Why these matter:**                                                    │
│ - TDD ensures quality through tests first (CORE-008)                        │
│ - Type hints catch bugs at IDE time, not runtime (CORE-011)                 │
│ - Docstrings enable maintainability and knowledge transfer (CORE-012)       │
│                                                                             │
│ ---                                                                         │
│                                                                             │
│ ### 📋 Definition of Ready                                                  │
│ [... rest of response ...]                                                  │
│                                                                             │
│ ---                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          CONTENT BLOCKS REGISTRY                             │
│  cortex-registry/core/templates/content-blocks.yaml          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  blocks:                                                                     │
│    governance_rules:  ← NEW (ENH-091)                                        │
│      id: "BLOCK-GOVERNANCE-RULES"                                           │
│      intent_mappings:                                                        │
│        IMPLEMENT:                                                            │
│          rules: ["CORE-008", "CORE-011", "CORE-012"]                        │
│          reason: "These principles ensure production-ready code"             │
│        ANALYZE:                                                              │
│          rules: ["CORE-030", "CORE-035", "CORE-036"]                        │
│          reason: "Analysis requires evidence-based truth"                    │
│        # ... FIX, AUDIT, PLAN, REFACTOR mappings                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↑                ↑
                              │                │
                              │                └─ Read intent mappings
                              └─ Load when assembling response

┌──────────────────────────────────────────────────────────────────────────────┐
│                   GOVERNANCE RULE REGISTRY (EXISTING)                       │
│            cortex_intelligence/governance/rules/CORE-rules.yaml                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CORE-008:                                                                   │
│    principle: "Red-Green-Refactor Discipline"                               │
│    book_reference: "TDD by Kent Beck"                                       │
│    description: "Tests before code..."                                      │
│    severity: "blocked"  (P0)                                                │
│                                                                              │
│  CORE-011:                                                                   │
│    principle: "Type Hints Mandatory"                                        │
│    book_reference: "Clean Code by Robert Martin"                            │
│    description: "All parameters + returns..."                               │
│    severity: "blocked"  (P0)                                                │
│                                                                              │
│  ... (28 more rules)                                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↑
                              │
                              └─ BusinessWisdomFormatter.format_governance_with_books()
                                 (loads rules by ID, formats with book refs)

┌──────────────────────────────────────────────────────────────────────────────┐
│                     BUSINESS WISDOM FORMATTER                                │
│         cortex/interaction/business_wisdom_formatter.py                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Input: rule_ids=["CORE-008", "CORE-011", "CORE-012"]                       │
│                                                                              │
│  Process:                                                                    │
│  1. Load each rule from governance registry by ID                           │
│  2. Sort by severity (blocked → warning → other)                            │
│  3. Limit to max_display (5 max)                                            │
│  4. Format each as: "- **Principle** → RULE-ID (Book)"                      │
│                                                                              │
│  Output:                                                                     │
│  ### 📚 Business Wisdom                                                      │
│  - **Red-Green-Refactor** → CORE-008 (TDD by Kent Beck)                     │
│  - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)        │
│  - **Google-Style Docstrings** → CORE-012 (Pragmatic Programmer)            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↑
                              │
                              └─ InteractionOrchestrator.get_governance_rules_block()
                                 (calls formatter, wraps with context reason)

┌──────────────────────────────────────────────────────────────────────────────┐
│                    INTERACTION ORCHESTRATOR (ENHANCED)                       │
│       cortex/orchestrators/core/interaction_orchestrator.py (ENH-091)       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NEW Methods:                                                                │
│                                                                              │
│  1. select_governance_rules_for_context(intent, context) → List[str]       │
│     - Loads mappings from content-blocks.yaml                              │
│     - Prioritizes violated rules (reinforce)                               │
│     - Matches intent to rules (educate)                                    │
│     - Checks exposure tracker (avoid repetition)                           │
│     - Returns top 2-3 rules                                                │
│                                                                              │
│  2. get_governance_rules_block(rule_ids, include_reason) → str             │
│     - Wraps formatter output with context reason                          │
│     - Adds "Why these matter" explanation                                 │
│     - Returns formatted markdown block                                    │
│                                                                              │
│  3. _track_rule_exposure(rule_ids, session_id) → None                      │
│     - Updates RuleExposureTracker                                         │
│     - Prevents showing same rules in next 3 turns                         │
│                                                                              │
│  UPDATED Method:                                                             │
│                                                                              │
│  assemble_response(context) → str                                          │
│     ├─ Detect intent                                                       │
│     ├─ Select governance rules (NEW - ENH-091)                             │
│     ├─ Get formatted block (NEW - ENH-091)                                 │
│     ├─ Track exposure (NEW - ENH-091)                                      │
│     └─ Assemble full response                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↑
                              │
                              └─ Called from MasterOrchestrator.execute_turn()
                                 (Stage 1 comprehension)

┌──────────────────────────────────────────────────────────────────────────────┐
│                        USER-FACING OUTPUT                                    │
│              (VSCode Copilot Chat markdown rendering)                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  # 🧠 CORTEX IMPLEMENT                                                       │
│  **Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅             │
│                                                                              │
│  ---                                                                         │
│                                                                              │
│  ### 📚 Governance Principles for Implementation                             │
│                                                                              │
│  These principles ensure your code meets CORTEX's production standards:      │
│                                                                              │
│  - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)           │
│  - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)         │
│  - **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas) │
│                                                                              │
│  💡 **Why these matter:**                                                    │
│  - TDD ensures quality through tests first (CORE-008)                        │
│  - Type hints catch bugs at IDE time, not runtime (CORE-011)                 │
│  - Docstrings enable maintainability and knowledge transfer (CORE-012)       │
│                                                                              │
│  ---                                                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Session-Level State Management

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RuleExposureTracker (Per Session)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Tracks:                                                                    │
│  - session_id: "session-123"                                               │
│  - turn_number: 5                                                           │
│  - rules_shown_history: {                                                   │
│      "CORE-008": 2,  ← Shown at turn 2                                      │
│      "CORE-011": 3,  ← Shown at turn 3                                      │
│      "CORE-012": 4,  ← Shown at turn 4                                      │
│    }                                                                        │
│  - violations_history: ["CORE-008", "CORE-027"]                             │
│                                                                             │
│  Decision Logic (turn 5):                                                   │
│                                                                             │
│  Should show CORE-008?                                                      │
│    - Last shown: turn 2                                                    │
│    - Turns since: 5 - 2 = 3                                                │
│    - Min turns required: 3 (configurable)                                   │
│    - Result: NO (don't repeat within 3 turns)                              │
│                                                                             │
│  Should show CORE-027?                                                      │
│    - Last shown: never (not in history)                                    │
│    - Is violation: YES (in violations_history)                             │
│    - Result: YES (prioritize violated rules for reinforcement)             │
│                                                                             │
│  Should show CORE-042 (new rule)?                                           │
│    - Last shown: never                                                     │
│    - Is violation: NO                                                      │
│    - Result: YES (unless max rules reached)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Intent-to-Rules Mapping

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Intent Classification Rules Mapping                       │
│                     (from content-blocks.yaml)                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  IMPLEMENT                                                                   │
│  ├─ Primary Rules: CORE-008 (TDD), CORE-011 (Type Hints), CORE-012 (Docs)  │
│  ├─ Reason: "These principles ensure production-ready code"                │
│  └─ Max: 3 rules                                                            │
│                                                                              │
│  FIX                                                                         │
│  ├─ Primary Rules: CORE-008 (TDD), CORE-027 (Audit), CORE-026 (Commits)    │
│  ├─ Reason: "Bug fixes maintain governance through audit trails"            │
│  └─ Max: 2 rules                                                            │
│                                                                              │
│  ANALYZE                                                                     │
│  ├─ Primary Rules: CORE-030 (Truth), CORE-035 (Canonical), CORE-036 (Std)  │
│  ├─ Reason: "Analysis requires evidence-based truth and standards"          │
│  └─ Max: 3 rules                                                            │
│                                                                              │
│  AUDIT                                                                       │
│  ├─ Primary Rules: CORE-029 (Header), CORE-025 (Git), CORE-027 (Audit)     │
│  ├─ Reason: "Audits validate governance compliance"                         │
│  └─ Max: 2 rules                                                            │
│                                                                              │
│  PLAN                                                                        │
│  ├─ Primary Rules: CORE-042 (Hierarchy), CORE-041 (Events), CORE-001 (Inc) │
│  ├─ Reason: "Planning uses hierarchical phases and event-driven patterns"   │
│  └─ Max: 2 rules                                                            │
│                                                                              │
│  REFACTOR                                                                    │
│  ├─ Primary Rules: CORE-035 (Canonical), CORE-011 (Hints), CORE-012 (Docs) │
│  ├─ Reason: "Refactoring maintains code quality standards"                  │
│  └─ Max: 2 rules                                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Integration Points (Existing + New)

```
EXISTING INTEGRATIONS (Already Wired)
├─ BusinessWisdomFormatter → EnforcementOrchestrator (violation messages)
├─ BusinessWisdomFormatter → IntentRouter (routing decisions)
├─ BusinessWisdomFormatter → SimpleResponseFormatter (response sections)
└─ Content Blocks Registry → SemanticBlockAssembler (response composition)

NEW INTEGRATIONS (ENH-091)
├─ BLOCK-GOVERNANCE-RULES → content-blocks.yaml (block definition)
├─ InteractionOrchestrator.select_governance_rules_for_context()
│   └─ Reads intent_mappings from content-blocks.yaml
├─ InteractionOrchestrator.get_governance_rules_block()
│   └─ Calls BusinessWisdomFormatter.format_governance_with_books()
├─ InteractionOrchestrator.assemble_response()
│   └─ Calls get_governance_rules_block() during response assembly
└─ RuleExposureTracker → Session state (prevent repetition)
```

---

## 💾 File Structure

```
cortex/
├─ orchestrators/
│  ├─ core/
│  │  └─ interaction_orchestrator.py (ENHANCE - ENH-091)
│  │     ├─ select_governance_rules_for_context() [NEW]
│  │     ├─ get_governance_rules_block() [NEW]
│  │     ├─ _track_rule_exposure() [NEW]
│  │     └─ assemble_response() [UPDATE]
│  │
│  └─ response/
│     └─ simple_response_formatter.py (ALREADY INTEGRATED)
│
├─ interaction/
│  └─ business_wisdom_formatter.py (ALREADY COMPLETE)
│     └─ format_governance_with_books() ← Used by get_governance_rules_block()
│
└─ registry/
   └─ semantic_blocks.py (ALREADY COMPLETE)
      └─ SemanticBlockAssembler ← Uses content blocks

cortex-registry/
└─ 
   └─ core/
      ├─ templates/
      │  └─ content-blocks.yaml (ENHANCE - ADD BLOCK-GOVERNANCE-RULES)
      │
      └─ governance/
         └─ CORE-rules.yaml (ALREADY COMPLETE)
            └─ All 30 rules with principles + book references

.github/
└─ prompts/
   ├─ response-format-standards.md (REFERENCE)
   ├─ business-wisdom-wiring.md (REFERENCE)
   ├─ ENH-091-GOVERNANCE-RULES-DISPLAY.md [NEW - CREATED]
   └─ guides/
      └─ GOVERNANCE-RULES-INTEGRATION-GUIDE.md [NEW - CREATED]

tests/
├─ unit/
│  └─ orchestrators/
│     └─ core/
│        ├─ test_governance_rules_block.py [NEW - ENH-091]
│        ├─ test_enforcement_orchestrator_books.py (EXISTING)
│        └─ test_intent_router_wisdom.py (EXISTING)
│
└─ integration/
   └─ test_interaction_governance_rules.py [NEW - ENH-091]
```

---

## ✅ Completion Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| **Block Definition** | ✅ Will add | BLOCK-GOVERNANCE-RULES in content-blocks.yaml |
| **Intent Mappings** | ✅ Will add | 6 intents → rule IDs + context reasons |
| **Rule Selection Logic** | ✅ Will implement | select_governance_rules_for_context() method |
| **Formatter Integration** | ✅ Will implement | get_governance_rules_block() method |
| **Response Assembly** | ✅ Will integrate | assemble_response() updated |
| **Session Tracking** | ✅ Will implement | RuleExposureTracker class |
| **Tests** | ✅ Will create | 20 unit + 8 integration tests |
| **Documentation** | ✅ Will create | ENH-091 + Integration Guide |
| **Performance** | ✅ Target | <50ms rule selection |
| **Coverage** | ✅ Target | 100% code coverage |

---

**Authority:** ENH-091 + cortex-architect.prompt.md § Intelligent Response Composition  
**Author:** GitHub Copilot (CORTEX Agent)  
**Date:** 2026-02-16

