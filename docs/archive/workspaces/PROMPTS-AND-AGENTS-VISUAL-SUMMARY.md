# Prompts & Agents: Gap Analysis Visual Summary

**Date:** 2026-01-25 | **Authority:** Holistic review

---

## 📊 Gap Inventory Matrix

```
PROMPTS (Rows) vs AGENTS (Columns)
─────────────────────────────────────────────────────────────────────────

PROMPT FILE                          | AGENT EXISTS? | IMPLEMENTATION STATUS
────────────────────────────────────|───────────────|─────────────────────────
✅ CORTEX.prompt.md (v5.0)           | ✅ CORTEX.md  | ⚠️  Partial (orchestrator only)
✅ cortex-review.prompt.md (v5.2)    | ✅ cortex-review.md + review-agents | ✅ Complete
✅ cortex-total-recall.prompt.md (v7.0) | ✅ cortex-total-recall.md | ✅ Complete
✅ cortex-builder.prompt.md (v4.0)   | ✅ cortex-builder.md | ✅ Complete
✅ cortex-enforcement.prompt.md (v2.0)| ✅ cortex-enforcement-agents.md | 🔴 UNIMPLEMENTED (3 agents)
✅ cortex-doc.prompt.md (Latest)     | ❌ MISSING | ❌ NOT IMPLEMENTED
✅ cortex-git-commit.prompt.md (v4.0)| ❌ MISSING | ❌ NOT IMPLEMENTED
───────────────────────────────────────────────────────────────────────────
✅ cortex-planner.md (AGENT)         | ❌ MISSING PROMPT | ⚠️  Orphaned agent

Missing Prompt Files:
────────────────────────────────────────────────────────────────────────────
❌ cortex-refactor.prompt.md         | ❌ (referenced in intent routing)
❌ cortex-test.prompt.md             | ❌ (referenced in intent routing)
❌ cortex-analyze.prompt.md          | ❌ (referenced in intent routing)
```

---

## 🎯 Orchestrator Coverage Map

```
MASTER ORCHESTRATOR INTENT ROUTING
──────────────────────────────────────────────────────────────────

        ┌─────────────────────────────────────────────────────┐
        │          CORTEX MASTER ORCHESTRATOR                 │
        │            (CORTEX.prompt.md v5.0)                  │
        └────────────────┬────────────────────────────────────┘
                         │
                         ├─ Stage 1: Intent Classification (LENS)
                         │
                         ├─ Stage 2: DoR Approval
                         │
                         ├─ Stage 3: Enforcement [⚠️ INCOMPLETE]
                         │    └─ EnforcementOrchestrator ❌ NOT IMPL
                         │       ├─ GovernanceEnforcementAgent ❌
                         │       ├─ SecurityCheckpointAgent ❌
                         │       └─ ComplianceValidationAgent ❌
                         │
                         └─ Stage 4: Domain Delegation
                              │
                              ├─→ IMPLEMENT intent
                              │   └─→ TDDOrchestrator ✅ (cortex-builder.prompt)
                              │
                              ├─→ REVIEW intent
                              │   └─→ ReviewOrchestrator ✅ (cortex-review.prompt)
                              │
                              ├─→ REFACTOR intent
                              │   └─→ RefactoringOrchestrator ❌ (no prompt/agent)
                              │
                              ├─→ TEST intent
                              │   └─→ TDDOrchestrator ⚠️ (no dedicated prompt)
                              │
                              ├─→ ANALYZE intent
                              │   └─→ MasterOrchestrator ⚠️ (no dedicated prompt)
                              │
                              ├─→ DOCUMENT intent
                              │   └─→ DocumentationOrchestrator ❌ (no agent/impl)
                              │
                              ├─→ DEPLOY intent
                              │   └─→ GitOrchestrator ❌ (no agent/impl)
                              │
                              └─→ GOVERNANCE intent
                                  └─→ GovernanceRegistry ⚠️ (unspecified)
```

---

## 📍 Prompt-Agent Pairing Status

```
COMPLETE PAIRINGS (5)
═══════════════════════════════════════════════════════════════

  cortex-review.prompt.md (v5.2)
      ✅ cortex-review.md (Coordinator)
      ✅ cortex-review-agents.md (8 sub-agents: BRIT, HALL, GOV, ASM, DEBT, STATE, ARCH, INTEG)
      ✅ IMPLEMENTATION: ReviewOrchestrator exists
      ✅ STATUS: COMPLETE & PRODUCTION READY

  cortex-total-recall.prompt.md (v7.0)
      ✅ cortex-total-recall.md (Discovery Agent)
      ✅ IMPLEMENTATION: TotalRecallAgent class exists
      ✅ AC-PERMANENT-FIX enforcement active (8 fixes)
      ✅ STATUS: COMPLETE & PRODUCTION READY

  cortex-builder.prompt.md (v4.0)
      ✅ cortex-builder.md (TDD Agent)
      ✅ IMPLEMENTATION: TDDOrchestrator exists
      ✅ CORE-008 TDD mandate enforced
      ✅ STATUS: COMPLETE & PRODUCTION READY

  CORTEX.prompt.md (v5.0)
      ✅ CORTEX.md (Master Agent)
      ✅ IMPLEMENTATION: MasterOrchestrator exists
      ⚠️  STATUS: COMPLETE but PARTIAL (not all delegations working)

  cortex-enforcement.prompt.md (v2.0)
      ✅ cortex-enforcement-agents.md (defines 3 agents)
      ❌ IMPLEMENTATION: EnforcementOrchestrator MISSING
      ❌ STATUS: PROMPT OK, IMPLEMENTATION MISSING


INCOMPLETE PAIRINGS (2)
═══════════════════════════════════════════════════════════════

  cortex-doc.prompt.md (Latest)
      ❌ NO AGENT DEFINITION FILE
      ❌ IMPLEMENTATION: DocumentationOrchestrator MISSING
      ⚠️  STATUS: PROMPT EXISTS, AGENT & CODE MISSING

  cortex-git-commit.prompt.md (v4.0)
      ❌ NO AGENT DEFINITION FILE
      ❌ IMPLEMENTATION: GitOrchestrator MISSING
      ⚠️  STATUS: PROMPT EXISTS, AGENT & CODE MISSING


ORPHANED COMPONENTS (1)
═══════════════════════════════════════════════════════════════

  cortex-planner.md (v4.0) - AGENT WITHOUT PROMPT
      ✅ AGENT DEFINITION exists
      ❌ NO CORRESPONDING PROMPT FILE
      ⚠️  STATUS: AGENT DEFINED, PROMPT MISSING


MISSING PROMPTS (3)
═══════════════════════════════════════════════════════════════

  cortex-refactor.prompt.md
      ❌ NOT CREATED
      ❌ NOT REFERENCED: Intent routing table in CORTEX.prompt
      ⚠️  STATUS: NEEDED FOR REFACTOR OPERATIONS

  cortex-test.prompt.md
      ❌ NOT CREATED
      ❌ NOT REFERENCED: Intent routing table in CORTEX.prompt
      ⚠️  STATUS: NEEDED FOR TEST OPERATIONS

  cortex-analyze.prompt.md
      ❌ NOT CREATED
      ❌ NOT REFERENCED: Intent routing table in CORTEX.prompt
      ⚠️  STATUS: NEEDED FOR ANALYZE OPERATIONS
```

---

## 🔴 Critical Deficiencies

```
DEFICIENCY #1: ENFORCEMENT AGENTS UNDEFINED (BLOCKING)
═══════════════════════════════════════════════════════════════

Prompt References (cortex-enforcement.prompt.md):
  - GovernanceEnforcementAgent (enforces CORE-008 through CORE-035)
  - SecurityCheckpointAgent (enforces CORE-026, CORE-030)
  - ComplianceValidationAgent (escalates TIER 1-3 violations)

Agent Definition File:
  Location: .github/agents/core/cortex-enforcement-agents.md
  Status: ✅ EXISTS - describes 3 agents
  
Implementation:
  Code Location: cortex/orchestrators/core/enforcement_orchestrator.py
  Status: ❌ MISSING - orchestrator not implemented
  
Sub-Agents Implementation:
  - GovernanceEnforcementAgent: ❌ NOT IMPLEMENTED
  - SecurityCheckpointAgent: ❌ NOT IMPLEMENTED
  - ComplianceValidationAgent: ❌ NOT IMPLEMENTED
  
Wiring:
  Integration Point: MasterOrchestrator.stage_3_enforcement()
  Status: ❌ NOT WIRED
  
Impact:
  🔴 CRITICAL: Governance enforcement mechanism INOPERABLE
  • CORE rule violations not blocked
  • CORE-030 (Implementation Truth) not enforced
  • CORE-035 (Single Canonical) not enforced
  
Fix Effort: 2-3 hours


DEFICIENCY #2: DOCUMENTATION ORCHESTRATOR MISSING (HIGH)
═══════════════════════════════════════════════════════════════

Prompt:
  File: cortex-doc.prompt.md (Latest version)
  Status: ✅ DEFINED - 8-phase pipeline documented
  
Agent Definition:
  File: .github/agents/core/cortex-documentation.md
  Status: ❌ MISSING
  
Implementation:
  Code Location: cortex/orchestrators/documentation/documentation_orchestrator.py
  Status: ❌ MISSING - orchestrator not implemented
  
Affected Commands:
  • /doc-fresh-generate ❌ NOT FUNCTIONAL
  
Impact:
  🟠 HIGH: Documentation generation disabled
  • Cannot execute fresh documentation pipeline
  • 8-phase workflow not operational
  
Fix Effort: 2-3 hours


DEFICIENCY #3: GIT ORCHESTRATOR MISSING (HIGH)
═══════════════════════════════════════════════════════════════

Prompt:
  File: cortex-git-commit.prompt.md (v4.0)
  Status: ✅ DEFINED
  
Agent Definition:
  File: .github/agents/core/cortex-git.md
  Status: ❌ MISSING
  
Implementation:
  Code Location: cortex/orchestrators/deployment/git_orchestrator.py
  Status: ❌ MISSING - orchestrator not implemented
  
Affected Commands:
  • /git-checkpoint ❌ NOT FUNCTIONAL
  • /git-commit ❌ NOT FUNCTIONAL
  • /git-push ❌ NOT FUNCTIONAL
  • /git-merge ❌ NOT FUNCTIONAL
  
Impact:
  🟠 HIGH: Git operations disabled
  • Pre-commit validation not available (CORE-026 checkpoint blocking)
  • Audit trail logging (CORE-027) not enforced
  
Fix Effort: 2-3 hours


DEFICIENCY #4: MISSING PROMPT FILES (HIGH)
═══════════════════════════════════════════════════════════════

Refactoring Orchestration:
  Prompt: cortex-refactor.prompt.md
  Status: ❌ NOT CREATED
  Intent Routing: Referenced in CORTEX.prompt.md as REFACTOR → RefactoringOrchestrator
  Impact: REFACTOR operations lack orchestration guide
  Effort: 1-2 hours to create

Test Orchestration:
  Prompt: cortex-test.prompt.md
  Status: ❌ NOT CREATED
  Intent Routing: Referenced in CORTEX.prompt.md as TEST → TDDOrchestrator
  Impact: TEST operations mixed with IMPLEMENT (builder.prompt)
  Effort: 1-2 hours to create

Analysis Orchestration:
  Prompt: cortex-analyze.prompt.md
  Status: ❌ NOT CREATED
  Intent Routing: Referenced in CORTEX.prompt.md as ANALYZE → MasterOrchestrator
  Impact: ANALYZE operations mixed with REVIEW
  Effort: 1-2 hours to create

Planning Orchestration:
  Prompt: cortex-planning.prompt.md
  Status: ❌ NOT CREATED (cortex-planner.md AGENT exists without prompt)
  Impact: Planning operations lack prompt guide, agent orphaned
  Effort: 1-2 hours to create


DEFICIENCY #5: REFACTORING ORCHESTRATOR UNDEFINED (MEDIUM)
═══════════════════════════════════════════════════════════════

Intent Routing:
  Defined in CORTEX.prompt.md: REFACTOR → RefactoringOrchestrator
  Status: ✅ Routed to orchestrator
  
Agent Definition:
  File: .github/agents/core/cortex-refactor.md
  Status: ❌ MISSING
  
Implementation:
  Code Location: cortex/orchestrators/domain/refactoring_orchestrator.py
  Status: ⚠️ EXISTS BUT NOT FULLY SPECIFIED in agents/
  
Impact:
  🟡 MEDIUM: REFACTOR operations can route but not guided by prompt
  
Fix Effort: 1-2 hours


DEFICIENCY #6: SUPPORT ORCHESTRATORS UNSPECIFIED (MEDIUM)
═══════════════════════════════════════════════════════════════

Referenced in: cortex-total-recall.prompt.md (WIRE-003)

Missing Agent Definitions (6):
  1. OnboardingOrchestrator ❌
  2. ToolDiscoveryOrchestrator ❌
  3. UpgradeOrchestrator ❌
  4. RollbackOrchestrator ❌
  5. SetupOrchestrator ❌
  6. ComposedOrchestrator ❌

Current Status:
  • Orchestrators may exist in codebase
  • Not documented in agents/ directory
  • No agent specification files
  
Impact:
  🟡 MEDIUM: Support orchestrators lack documented behavior
  
Fix Effort: 2-3 hours to create 6 agent definition files
```

---

## 📈 Coverage Metrics

```
PROMPT COVERAGE SCORECARD
═══════════════════════════════════════════════════════════════

Core Intents (8 total):
  ✅ IMPLEMENT      (cortex-builder.prompt.md)
  ✅ REVIEW         (cortex-review.prompt.md)
  ✅ DOCUMENT       (cortex-doc.prompt.md)
  ✅ DEPLOY         (cortex-git-commit.prompt.md)
  ✅ FIX            (implied in CORTEX.prompt.md)
  ❌ REFACTOR       (missing prompt)
  ❌ TEST           (missing prompt)
  ❌ ANALYZE        (missing prompt)

Coverage: 5/8 = 62.5% ⚠️


AGENT COVERAGE SCORECARD
═══════════════════════════════════════════════════════════════

Defined Agent Files (Current: 7):
  ✅ CORTEX.md (Master)
  ✅ cortex-review.md + cortex-review-agents.md (Review: 9 agents)
  ✅ cortex-total-recall.md (Discovery)
  ✅ cortex-builder.md (TDD)
  ✅ cortex-enforcement-agents.md (Enforcement: 3 agents)
  ✅ cortex-planner.md (Planning)
  ❌ cortex-documentation.md (MISSING)
  ❌ cortex-git.md (MISSING)
  ❌ cortex-refactor.md (MISSING)
  ❌ cortex-test.md (MISSING)

Coverage: 6/10 = 60% ⚠️


AGENT IMPLEMENTATION STATUS
═══════════════════════════════════════════════════════════════

Fully Implemented (3):
  ✅ ReviewOrchestrator + 8 sub-agents
  ✅ TDDOrchestrator
  ✅ TotalRecallAgent (not an orchestrator, but functional)

Partially Implemented (2):
  ⚠️  MasterOrchestrator (Stage 3 enforcement incomplete)
  ⚠️  PlanningOrchestrator (exists, but orphaned from prompt)

Not Implemented (5):
  ❌ EnforcementOrchestrator (+ 3 sub-agents)
  ❌ DocumentationOrchestrator
  ❌ GitOrchestrator
  ❌ RefactoringOrchestrator (exists in codebase? unspecified in agents/)
  ❌ Support Orchestrators (6: Onboarding, ToolDiscovery, Upgrade, Rollback, Setup, Composed)

Implementation Coverage: 3/11 = 27% 🔴


ORCHESTRATOR WIRING MATRIX
═══════════════════════════════════════════════════════════════

Core Orchestrators (6):
  1. MasterOrchestrator              ✅ Wired
  2. InteractionOrchestrator         ⚠️  Wired (not fully integrated)
  3. IntentRouter                    ⚠️  Wired (not fully integrated)
  4. TDDOrchestrator                 ✅ Wired
  5. WorkflowOrchestrator            ❌ Unspecified
  6. OrchestratorBootstrap           ❌ Unspecified

Domain Orchestrators (5):
  1. RefactoringOrchestrator         ⚠️  Exists (no agent spec)
  2. PlanningOrchestrator            ✅ Wired (orphaned from prompt)
  3. DomainOrchestrator              ⚠️  Routed (not fully wired)
  4. ConversationOrchestrator        ❌ Unspecified
  5. SeleniumPlaywrightOrchestrator  ❌ Unspecified

Support Orchestrators (6):
  1. OnboardingOrchestrator          ❌ Unspecified
  2. ToolDiscoveryOrchestrator       ❌ Unspecified
  3. UpgradeOrchestrator             ❌ Unspecified
  4. RollbackOrchestrator            ❌ Unspecified
  5. SetupOrchestrator               ❌ Unspecified
  6. ComposedOrchestrator            ❌ Unspecified

Missing (3):
  1. EnforcementOrchestrator         ❌ Not implemented
  2. DocumentationOrchestrator       ❌ Not implemented
  3. GitOrchestrator                 ❌ Not implemented

Wiring Coverage: ~8-10/23 = 35-43% 🔴


GOVERNANCE RULE ENFORCEMENT
═══════════════════════════════════════════════════════════════

Rules Defined: 35 (CORE-001 through CORE-035)
Rules with Enforcement Agents: 0 (not wired!)

Latest Rules Added:
  ✅ CORE-030: Implementation Truth (in review agents)
  ✅ CORE-035: Single Canonical Implementation (in review agents)
  ⚠️  Enforcement agents reference CORE-008 through CORE-035 but NOT IMPLEMENTED

Enforcement Coverage: 0% (agents defined in prompt but not in code)
```

---

## 🎯 Priority Remediation Queue

```
IMMEDIATE (THIS WEEK) - BLOCKING FIXES
═══════════════════════════════════════════════════════════════

🔴 P0.1: Implement EnforcementOrchestrator + 3 Sub-Agents
    Effort: 2-3 hours
    Impact: CRITICAL - Governance enforcement mechanism
    Blocks: All enforcement operations
    File: cortex/orchestrators/core/enforcement_orchestrator.py
    Wiring: MasterOrchestrator.stage_3_enforcement()

🔴 P0.2: Create cortex-enforcement-agents-DETAIL.md (Agent Spec)
    Effort: 1 hour
    Impact: CRITICAL - Agent behavior documentation
    Dependencies: P0.1
    File: .github/agents/core/cortex-enforcement-agents-DETAIL.md


HIGH PRIORITY (THIS SPRINT) - BLOCKING FEATURES
═══════════════════════════════════════════════════════════════

🟠 P1.1: Create cortex-refactor.prompt.md
    Effort: 1-2 hours
    Impact: HIGH - REFACTOR operations blocked
    Reference: cortex-builder.prompt.md pattern
    File: .github/prompts/cortex-refactor.prompt.md

🟠 P1.2: Create cortex-test.prompt.md
    Effort: 1-2 hours
    Impact: HIGH - TEST operations lack dedicated guidance
    Reference: cortex-builder.prompt.md pattern
    File: .github/prompts/cortex-test.prompt.md

🟠 P1.3: Implement DocumentationOrchestrator
    Effort: 2-3 hours
    Impact: HIGH - /doc-fresh-generate disabled
    Blocks: Documentation pipeline
    File: cortex/orchestrators/documentation/documentation_orchestrator.py

🟠 P1.4: Implement GitOrchestrator
    Effort: 2-3 hours
    Impact: HIGH - Git operations disabled
    Blocks: /git-checkpoint, /git-commit commands
    File: cortex/orchestrators/deployment/git_orchestrator.py


MEDIUM PRIORITY (NEXT SPRINT) - COMPLETENESS
═══════════════════════════════════════════════════════════════

🟡 P2.1: Create cortex-planning.prompt.md
    Effort: 1-2 hours
    Impact: MEDIUM - Planning operations orphaned
    Dependent: cortex-planner.md (agent exists without prompt)
    File: .github/prompts/cortex-planning.prompt.md

🟡 P2.2: Create cortex-documentation.md (Agent Spec)
    Effort: 1 hour
    Impact: MEDIUM - Documentation agent not documented
    Dependent: P1.3
    File: .github/agents/core/cortex-documentation.md

🟡 P2.3: Create cortex-git.md (Agent Spec)
    Effort: 1 hour
    Impact: MEDIUM - Git agent not documented
    Dependent: P1.4
    File: .github/agents/core/cortex-git.md

🟡 P2.4: Document Support Orchestrators (6 agents)
    Effort: 2-3 hours
    Impact: MEDIUM - Support orchestrators lack agent specs
    Files: .github/agents/core/cortex-*.md (6 files)


LOW PRIORITY (BACKLOG) - OPTIONAL
═══════════════════════════════════════════════════════════════

🔵 P3.1: Create cortex-analyze.prompt.md
    Effort: 1-2 hours
    Impact: LOW - Can use review.prompt as fallback
    File: .github/prompts/cortex-analyze.prompt.md

🔵 P3.2: Create cortex-feedback.prompt.md
    Effort: 1-2 hours
    Impact: LOW - Enhancement, not critical
    File: .github/prompts/cortex-feedback.prompt.md
```

---

## ✅ Validation Checklist

**Before declaring analysis "complete", verify:**

- [ ] All 7 prompts reviewed and gaps identified
- [ ] All 7 agent definition files reviewed
- [ ] All 23 orchestrators mapped to prompts/agents
- [ ] All 8 sub-agents (review) documented
- [ ] All enforcement agents (3) identified as unimplemented
- [ ] All missing prompts (3-4) identified with effort estimates
- [ ] Prompt-agent pairing matrix completed (5 complete, 2 incomplete, 1 orphaned)
- [ ] Orchestrator coverage calculated (35-43%)
- [ ] Deficiencies prioritized with effort estimates
- [ ] Remediation roadmap created with phased approach

---

**Analysis Status:** ✅ COMPLETE  
**Generated:** 2026-01-25  
**Authority:** Holistic Review of Prompts & Agents Directories
