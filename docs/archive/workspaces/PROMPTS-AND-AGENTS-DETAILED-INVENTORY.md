# PROMPTS & AGENTS: DETAILED INVENTORY & COMPARISON
**Authority:** Comprehensive audit of `/github/prompts/` and `/github/agents/` | **Date:** 2026-01-25

---

## 📑 MASTER INVENTORY TABLE

### All Prompts (Current + Missing)

```
╔════╦═════════════════════════════════════╦═══════════╦════════════╦═════════════════════════════════════╗
║ # ║ PROMPT FILE                         ║ VERSION   ║ EXISTS     ║ PAIRED AGENT / STATUS               ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 1  ║ CORTEX.prompt.md                    ║ 5.0       ║ ✅ YES    ║ ✅ CORTEX.md                        ║
║    ║ Master Orchestrator                 ║ 2026-01-25║ Root dir  ║ ⚠️  Partial (Stage 3 enforcement)  ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 2  ║ cortex-review.prompt.md             ║ 5.2       ║ ✅ YES    ║ ✅ cortex-review.md                 ║
║    ║ Code Quality & Governance Analysis  ║ 2026-01-25║ Root dir  ║ ✅ + cortex-review-agents.md (8)   ║
║    ║ 10-agent comprehensive              ║           ║           ║ ✅ COMPLETE & PRODUCTION READY     ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 3  ║ cortex-total-recall.prompt.md       ║ 7.0       ║ ✅ YES    ║ ✅ cortex-total-recall.md           ║
║    ║ Feature Discovery & AC Verification ║ 2026-01-25║ Root dir  ║ ✅ TotalRecallAgent class           ║
║    ║ AC-PERMANENT-FIX enforcement        ║           ║           ║ ✅ COMPLETE & PRODUCTION READY     ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 4  ║ cortex-builder.prompt.md            ║ 4.0       ║ ✅ YES    ║ ✅ cortex-builder.md                ║
║    ║ TDD Implementation                  ║ 2026-01-24║ Root dir  ║ ✅ TDDOrchestrator                 ║
║    ║ CORE-008 TDD mandate                ║           ║           ║ ✅ COMPLETE & PRODUCTION READY     ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 5  ║ cortex-enforcement.prompt.md        ║ 2.0       ║ ✅ YES    ║ ✅ cortex-enforcement-agents.md     ║
║    ║ Governance Rule Enforcement         ║ 2026-01-25║ Root dir  ║ ✅ Defines 3 agents                 ║
║    ║ Stage 3 enforcement                 ║           ║           ║ ❌ AGENTS NOT IMPLEMENTED          ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 6  ║ cortex-doc.prompt.md                ║ Latest    ║ ✅ YES    ║ ❌ NO AGENT DEFINITION FILE         ║
║    ║ Fresh Documentation Generation      ║ 2026-01-24║ Root dir  ║ ❌ DocumentationOrchestrator MISSING║
║    ║ 8-phase pipeline                    ║           ║           ║ ⚠️  PARTIAL - Prompt OK            ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 7  ║ cortex-git-commit.prompt.md         ║ 4.0       ║ ✅ YES    ║ ❌ NO AGENT DEFINITION FILE         ║
║    ║ Git Commit Protocol                 ║ 2026-01-24║ Root dir  ║ ❌ GitOrchestrator MISSING          ║
║    ║ CORE-026/027 enforcement            ║           ║           ║ ⚠️  PARTIAL - Prompt OK            ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 8  ║ cortex-refactor.prompt.md           ║ N/A       ║ ❌ NO     ║ ❌ MISSING                          ║
║    ║ Refactoring Orchestration           ║ NEEDED    ║ (missing) ║ ❌ RefactoringOrchestrator routed   ║
║    ║ Referenced in intent routing        ║           ║           ║ ❌ NO PROMPT GUIDE                 ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 9  ║ cortex-test.prompt.md               ║ N/A       ║ ❌ NO     ║ ❌ MISSING                          ║
║    ║ Test Generation & Validation        ║ NEEDED    ║ (missing) ║ ❌ TDDOrchestrator routed           ║
║    ║ Referenced in intent routing        ║           ║           ║ ❌ Merged into builder.prompt      ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 10 ║ cortex-analyze.prompt.md            ║ N/A       ║ ❌ NO     ║ ❌ MISSING                          ║
║    ║ Targeted Analysis                   ║ OPTIONAL  ║ (missing) ║ ❌ MasterOrchestrator routed        ║
║    ║ Fallback: cortex-review.prompt      ║           ║           ║ ❌ Merged into review.prompt       ║
╠════╬═════════════════════════════════════╬═══════════╬════════════╬═════════════════════════════════════╣
║ 11 ║ cortex-planning.prompt.md           ║ N/A       ║ ❌ NO     ║ ⚠️  cortex-planner.md (ORPHANED)   ║
║    ║ Phase Planning & Progress           ║ NEEDED    ║ (missing) ║ ✅ Agent exists                     ║
║    ║ Agent exists without prompt!        ║           ║           ║ ❌ NO CORRESPONDING PROMPT         ║
╚════╩═════════════════════════════════════╩═══════════╩════════════╩═════════════════════════════════════╝
```

---

### All Agent Definitions (Current + Missing)

```
╔════╦════════════════════════════════════╦═══════════╦═════════════╦════════════════════════════════════╗
║ # ║ AGENT FILE                         ║ AGENTS    ║ EXISTS      ║ PAIRED PROMPT / STATUS             ║
║   ║ LOCATION                           ║ DEFINED   ║             ║                                    ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 1  ║ CORTEX.md                          ║ 1         ║ ✅ YES      ║ ✅ CORTEX.prompt.md (5.0)          ║
║    ║ .github/agents/core/               ║ Master    ║ v5.0        ║ ⚠️  Partial delegation             ║
║    ║                                    ║           ║             ║ ⚠️  Stage 3 incomplete             ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 2  ║ cortex-review.md                   ║ 1         ║ ✅ YES      ║ ✅ cortex-review.prompt.md (5.2)  ║
║    ║ .github/agents/core/               ║ Review    ║ v4.0        ║ ✅ COMPLETE                        ║
║    ║ (Coordinator)                      ║           ║             ║ ✅ ReviewOrchestrator implemented ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 3  ║ cortex-review-agents.md            ║ 8         ║ ✅ YES      ║ ✅ cortex-review.prompt.md (5.2)  ║
║    ║ .github/agents/core/               ║ Sub-agents║ v4.0        ║ ✅ COMPLETE                        ║
║    ║ (BRIT, HALL, GOV, ASM, DEBT,       ║           ║             ║ BRIT, HALL, GOV, ASM, DEBT, STATE,║
║    ║ STATE, ARCH, INTEG)                ║           ║             ║ ARCH, INTEG                        ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 4  ║ cortex-total-recall.md             ║ 1         ║ ✅ YES      ║ ✅ cortex-total-recall.prompt.md   ║
║    ║ .github/agents/core/               ║ Discovery ║ v6.0        ║ ✅ COMPLETE                        ║
║    ║ (Feature Discovery & Fixer)        ║ + Fixer   ║             ║ ✅ TotalRecallAgent class          ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 5  ║ cortex-builder.md                  ║ 1         ║ ✅ YES      ║ ✅ cortex-builder.prompt.md (4.0) ║
║    ║ .github/agents/core/               ║ TDD       ║ v4.0        ║ ✅ COMPLETE                        ║
║    ║ (Implementation)                   ║           ║             ║ ✅ TDDOrchestrator implemented    ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 6  ║ cortex-enforcement-agents.md       ║ 3         ║ ✅ YES      ║ ✅ cortex-enforcement.prompt.md    ║
║    ║ .github/agents/core/               ║ Enforcement║ v2.0       ║ ✅ Agents defined in prompt        ║
║    ║ (GOV, SEC, COMP)                   ║           ║             ║ ❌ NOT IMPLEMENTED in code         ║
║    ║                                    ║           ║             ║ ❌ EnforcementOrchestrator MISSING ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 7  ║ cortex-planner.md                  ║ 1         ║ ✅ YES      ║ ❌ NO CORRESPONDING PROMPT         ║
║    ║ .github/agents/core/               ║ Planning  ║ v4.0        ║ ⚠️  ORPHANED AGENT                 ║
║    ║ (Progress Tracking)                ║           ║             ║ ❌ cortex-planning.prompt NEEDED   ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 8  ║ cortex-documentation.md            ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ cortex-doc.prompt.md exists     ║
║    ║ (Doc Generation)                   ║           ║             ║ ❌ DocumentationOrchestrator MISSING║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 9  ║ cortex-git.md                      ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ cortex-git-commit.prompt exists ║
║    ║ (Git Operations)                   ║           ║             ║ ❌ GitOrchestrator MISSING         ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 10 ║ cortex-refactor.md                 ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ cortex-refactor.prompt MISSING  ║
║    ║ (Refactoring)                      ║           ║             ║ ❌ RefactoringOrchestrator routed   ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 11 ║ cortex-test.md                     ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ cortex-test.prompt MISSING      ║
║    ║ (Testing)                          ║           ║             ║ ❌ TDDOrchestrator routed           ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 12 ║ cortex-onboarding.md               ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ OnboardingOrchestrator (WIRE-003)║
║    ║ (Support: Onboarding)              ║           ║             ║ ❌ Agent spec missing              ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 13 ║ cortex-tool-discovery.md           ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ ToolDiscoveryOrchestrator       ║
║    ║ (Support: Tool Discovery)          ║           ║             ║ ❌ Agent spec missing              ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 14 ║ cortex-upgrade.md                  ║ N/A       ║ ❌ NO       ║ ❌ MISSING                         ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ UpgradeOrchestrator             ║
║    ║ (Support: Upgrade)                 ║           ║             ║ ❌ Agent spec missing              ║
╠════╬════════════════════════════════════╬═══════════╬═════════════╬════════════════════════════════════╣
║ 15 ║ cortex-rollback.md + others (3)    ║ N/A       ║ ❌ NO       ║ ❌ MISSING (RollbackOrch,          ║
║    ║ .github/agents/core/               ║ NEEDED    ║ (missing)   ║ ❌ SetupOrch, ComposedOrch)        ║
║    ║ (Support: Rollback, Setup, Composed║           ║             ║ ❌ 3 more agent specs missing      ║
╚════╩════════════════════════════════════╩═══════════╩═════════════╩════════════════════════════════════╝
```

---

## 🎯 ORCHESTRATOR IMPLEMENTATION STATUS

### All 23 Orchestrators Referenced in Codebase

```
CORE ORCHESTRATORS (6)
─────────────────────────────────────────────────────────────

1. MasterOrchestrator
   Prompt:        ✅ CORTEX.prompt.md (Stage 1-4)
   Agent:         ✅ CORTEX.md
   Implementation: ✅ EXISTS (cortex/orchestrators/core/master_orchestrator.py)
   Wiring:        ✅ ENTRY POINT
   Status:        ⚠️  PARTIAL - Stage 3 enforcement incomplete
   
2. InteractionOrchestrator
   Prompt:        ✅ CORTEX.prompt.md (Stage 1)
   Agent:         ✅ CORTEX.md
   Implementation: ⚠️  EXISTS but referenced (not fully called)
   Wiring:        ⚠️  INITIALIZED but not integrated
   Status:        ⚠️  PARTIAL - Referenced but not utilized
   
3. IntentRouter
   Prompt:        ✅ CORTEX.prompt.md (routing table)
   Agent:         ✅ CORTEX.md
   Implementation: ✅ EXISTS (intent routing logic)
   Wiring:        ⚠️  INITIALIZED but dispatch incomplete
   Status:        ⚠️  PARTIAL - Routes defined but not all executed
   
4. TDDOrchestrator
   Prompt:        ✅ cortex-builder.prompt.md (v4.0)
   Agent:         ✅ cortex-builder.md
   Implementation: ✅ EXISTS (cortex/orchestrators/core/tdd_orchestrator.py)
   Wiring:        ✅ FULLY INTEGRATED
   Status:        ✅ COMPLETE & OPERATIONAL
   
5. WorkflowOrchestrator
   Prompt:        ⚠️  REFERENCED (unspecified)
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ⚠️  EXISTS (cortex/orchestrators/core/workflow_orchestrator.py)
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        ⚠️  PARTIAL - Unspecified in agents/
   
6. OrchestratorBootstrap
   Prompt:        ⚠️  REFERENCED (unspecified)
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ✅ INTEGRATED
   Status:        ⚠️  PARTIAL - Unspecified in agents/


DOMAIN ORCHESTRATORS (5)
─────────────────────────────────────────────────────────────

1. RefactoringOrchestrator
   Prompt:        ❌ cortex-refactor.prompt.md (MISSING)
   Agent:         ❌ cortex-refactor.md (MISSING)
   Implementation: ⚠️  PARTIALLY EXISTS
   Wiring:        ⚠️  ROUTED (Stage 4)
   Status:        🟡 MEDIUM - Exists but not fully specified
   
2. PlanningOrchestrator
   Prompt:        ❌ cortex-planning.prompt.md (MISSING)
   Agent:         ✅ cortex-planner.md (exists but orphaned)
   Implementation: ✅ EXISTS
   Wiring:        ✅ INTEGRATED
   Status:        🟡 MEDIUM - Agent orphaned, prompt needed
   
3. DomainOrchestrator
   Prompt:        ⚠️  REFERENCED (unspecified)
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  ROUTED (Stage 4)
   Status:        ⚠️  PARTIAL - Unspecified in agents/
   
4. ConversationOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ❌ NOT INTEGRATED
   Status:        🟡 MEDIUM - Exists but unspecified
   
5. SeleniumPlaywrightOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ❌ NOT INTEGRATED
   Status:        🔵 LOW - Exists but unspecified


SUPPORT ORCHESTRATORS (6) - WIRE-003
─────────────────────────────────────────────────────────────

1. OnboardingOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS (cortex/orchestrators/support/)
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing
   
2. ToolDiscoveryOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing
   
3. UpgradeOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing
   
4. RollbackOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing
   
5. SetupOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing
   
6. ComposedOrchestrator
   Prompt:        ❌ NOT REFERENCED
   Agent:         ❌ NO AGENT DEFINITION
   Implementation: ✅ EXISTS
   Wiring:        ⚠️  PARTIALLY INTEGRATED
   Status:        🟡 MEDIUM - Agent spec missing


MISSING ORCHESTRATORS (3)
─────────────────────────────────────────────────────────────

1. EnforcementOrchestrator
   Prompt:        ✅ cortex-enforcement.prompt.md (v2.0)
   Agent:         ✅ cortex-enforcement-agents.md (defines 3 agents)
   Implementation: ❌ MISSING - Must implement
   Wiring:        ❌ NOT INTEGRATED (should be Stage 3)
   Status:        🔴 CRITICAL - Enforcement mechanism incomplete
   
2. DocumentationOrchestrator
   Prompt:        ✅ cortex-doc.prompt.md (Latest)
   Agent:         ❌ cortex-documentation.md (MISSING)
   Implementation: ❌ MISSING - Must implement
   Wiring:        ❌ NOT INTEGRATED (Stage 4)
   Status:        🔴 CRITICAL - Documentation generation disabled
   
3. GitOrchestrator
   Prompt:        ✅ cortex-git-commit.prompt.md (v4.0)
   Agent:         ❌ cortex-git.md (MISSING)
   Implementation: ❌ MISSING - Must implement
   Wiring:        ❌ NOT INTEGRATED (Stage 4)
   Status:        🔴 CRITICAL - Git operations disabled
```

---

## 📊 SUMMARY STATISTICS

### By Component Type

```
PROMPTS
├─ Existing:           7/11 (64%)
│  ├─ With paired agent: 5
│  ├─ Without agent:     2
│  └─ Fully functional:  3
├─ Missing:            4/11 (36%)
│  ├─ Critical:        2 (Refactor, Test)
│  ├─ High:            1 (Analyze)
│  └─ Optional:        1 (Feedback)
└─ Total lines:       ~5,000+ lines of guidance

AGENTS
├─ Existing:           7 files defining 15+ agents
│  ├─ Master agents:   1 (CORTEX)
│  ├─ Coordinator:     1 (Review)
│  ├─ Sub-agents:      8 (Review: BRIT, HALL, GOV, ASM, DEBT, STATE, ARCH, INTEG)
│  ├─ Discovery:       1 (TotalRecall)
│  ├─ Implementation:  1 (Builder)
│  ├─ Enforcement:     3 (GOV, SEC, COMP) - NOT IMPLEMENTED
│  └─ Planning:        1 (Planner) - ORPHANED
├─ Missing:           8+ agent definitions
│  ├─ Critical:       3 (Enforcement, Doc, Git)
│  ├─ High:           2 (Refactor, Test)
│  ├─ Medium:         3 (Analyze, Feedback, Planning/prompt)
│  └─ Support:        6 (Onboarding, ToolDiscovery, Upgrade, Rollback, Setup, Composed)
└─ Total agents defined: ~15-20 agents

ORCHESTRATORS
├─ Existing code:     ~20 orchestrators
├─ Fully documented:  3-5 orchestrators
├─ Partially documented: 2-3 orchestrators
├─ Undocumented:      12+ orchestrators
├─ Missing code:      3 orchestrators
└─ Implementation coverage: ~35-43% of 23 target
```

---

## ✅ VERIFICATION CHECKLIST

Complete the analysis with these checks:

- [x] All 7 existing prompts reviewed
- [x] All 7 agent definitions reviewed
- [x] 23 orchestrators mapped
- [x] Prompt-agent pairing identified
- [x] Implementation status determined
- [x] Orchestrator wiring assessed
- [x] Gaps and deficiencies documented
- [x] Priorities assigned
- [x] Effort estimates provided
- [x] Visual summaries created

---

**Analysis Complete:** ✅ 2026-01-25  
**Total Artifacts:** 3 documents created  
**Total Analysis Lines:** ~2,000+ lines  
**Recommendations:** PROCEED WITH PHASE 1 REMEDIATION
