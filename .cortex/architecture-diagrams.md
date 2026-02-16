# CORTEX Architecture Diagrams

**Generated:** 2026-02-15  
**Source:** Production Codebase Analysis  
**Status:** Auto-Generated from Implementation

---

## 1. MCP-First Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────────┐
│                         VS Code                                 │
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │  Copilot Chat    │  stdio  │   MCP Server                 │  │
│  │  (User Interface)│◀────────▶   (Auto-Started)             │  │
│  │                  │ JSON-RPC│   • python -m cortex.mcp     │  │
│  │  "/implement X"  │   2.0   │   • Local (Pylance-style)    │  │
│  └──────────────────┘         └──────────────────────────────┘  │
│                                         │                       │
│                                         ▼                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              MCP Tool Registry (24 Tools)                 │  │
│  │  • cortex_process_request  • cortex_lens_analyze         │  │
│  │  • cortex_challenge        • cortex_detect_duplicates    │  │
│  │  • cortex_total_recall     • cortex_audit                │  │
│  │  • cortex_onboard_repository                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                         │                       │
│                                         ▼                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          CORTEX Orchestration Layer (28 Orchestrators)    │  │
│  │                                                           │  │
│  │  Core (8)          Domain (6)         Support (14)       │  │
│  │  ├─ Master         ├─ Refactoring     ├─ Onboarding     │  │
│  │  ├─ Interaction    ├─ Planning        ├─ Tool Discovery │  │
│  │  ├─ Intent Router  ├─ Domain          ├─ LENS           │  │
│  │  ├─ LENS Synth     ├─ Conversation    ├─ Challenge      │  │
│  │  ├─ Enforcement    ├─ Documentation   ├─ (10 more)      │  │
│  │  ├─ TDD            └─ Challenge       │                 │  │
│  │  ├─ Task Decomp                       │                 │  │
│  │  └─ Workflow                          │                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                         │                       │
│                                         ▼                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Core Services                           │  │
│  │  • Git Operations    • Test Runner    • File System      │  │
│  │  • Code Analysis     • Compliance     • Metrics          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Pylance-Style:** MCP server auto-starts within VS Code (no manual server management)
- **stdio Transport:** JSON-RPC 2.0 over stdin/stdout
- **Local Execution:** All operations within VS Code process space
- **24 MCP Tools:** Single interface for all CORTEX capabilities

---

## 2. MasterOrchestrator 4-Stage Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│             cortex_process_request (Entry Point)                 │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1: INTERACTION (InteractionOrchestrator)                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • Display DoR (Definition of Ready) table                 │  │
│  │  • Show intent classification                              │  │
│  │  • Present estimated effort                                │  │
│  │  • Await approval: "proceed" / "yes" / "approve"           │  │
│  │                                                            │  │
│  │  Output: approval_received: bool                           │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼ (if approved)
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 2: INTENT ROUTING (IntentRouter)                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • LENS Classification: Language→Examination→Navigation    │  │
│  │  • Intent Detection: IMPLEMENT | FIX | REFACTOR | ANALYZE  │  │
│  │  • Context Loading: Pre-warm CCL (rules, infrastructure)   │  │
│  │  • Orchestrator Selection:                                 │  │
│  │    - IMPLEMENT → TDDOrchestrator                           │  │
│  │    - FIX → TDDOrchestrator                                 │  │
│  │    - REFACTOR → RefactoringOrchestrator                    │  │
│  │    - ANALYZE → LENSSynthesis                               │  │
│  │                                                            │  │
│  │  Output: target_orchestrator, intent, ccl_context          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3: INTELLIGENCE (CCL + LENS)                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Context Crystallization Layer (CCL):                      │  │
│  │  • Async prefetch started in Stage 2 (parallel)            │  │
│  │  • Rules: CORE governance rules                            │  │
│  │  • Infrastructure: Wiring, orchestrator specs              │  │
│  │  • LENS: Code intelligence, dependencies                   │  │
│  │                                                            │  │
│  │  LENS Analysis:                                            │  │
│  │  • Dependency graph                                        │  │
│  │  • Test coverage                                           │  │
│  │  • Compliance baseline                                     │  │
│  │  • Impact analysis                                         │  │
│  │                                                            │  │
│  │  Output: enriched_context, analysis_results                │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 4: EXECUTION (Selected Orchestrator)                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TDDOrchestrator (IMPLEMENT/FIX):                          │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐              │  │
│  │  │   RED    │──▶│  GREEN   │──▶│ REFACTOR │──▶ Commit    │  │
│  │  │ Write    │   │ Implement│   │ Improve  │              │  │
│  │  │ Test     │   │ Code     │   │ Quality  │              │  │
│  │  └──────────┘   └──────────┘   └──────────┘              │  │
│  │                                                            │  │
│  │  Governance Gates:                                         │  │
│  │  • Pre-execution: EnforcementOrchestrator (7 agents)      │  │
│  │  • Runtime: Real-time violation detection                 │  │
│  │  • Post-execution: Compliance audit                       │  │
│  │                                                            │  │
│  │  Audit Trail:                                              │  │
│  │  • AC_START markers                                       │  │
│  │  • AC_COMPLETE markers with test results                  │  │
│  │  • Git commits with governance metadata                   │  │
│  │                                                            │  │
│  │  Output: execution_result, test_results, audit_log        │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     COMPLETION REPORT                             │
│  • Implementation summary                                         │
│  • Test results (passed/total)                                   │
│  • Coverage metrics                                               │
│  • Compliance status                                              │
│  • Audit trail references                                         │
└──────────────────────────────────────────────────────────────────┘
```

**Stage Durations:**
- Stage 1: ~5-10 seconds (DoR display + approval)
- Stage 2: ~2-5 seconds (intent classification + CCL start)
- Stage 3: ~5-15 seconds (LENS analysis + context pre-warming)
- Stage 4: Variable (depends on implementation complexity)

---

## 3. Orchestrator Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      IOrchestrator Interface                    │
│  • get_name() → str                                             │
│  • get_version() → str                                          │
│  • initialize() → Result[str]                                   │
│  • execute_operation(request) → Result[ExecutionResult]         │
│  • get_mode() → OperationMode                                   │
│  • get_audit_trail() → Result[list]                             │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
         ┌────────────────────┴────────────────────┐
         │                                         │
         ▼                                         ▼
┌─────────────────────┐                 ┌─────────────────────┐
│  CORE ORCHESTRATORS │                 │ DOMAIN ORCHESTRATORS│
│  (8 orchestrators)  │                 │  (6 orchestrators)  │
├─────────────────────┤                 ├─────────────────────┤
│ • MasterOrchestrator│                 │ • RefactoringOrch   │
│   (4-stage pipeline)│                 │ • PlanningOrch      │
│                     │                 │ • DomainOrch        │
│ • InteractionOrch   │                 │ • ConversationOrch  │
│   (DoR display)     │                 │ • DocumentationOrch │
│                     │                 │ • ChallengeEngine   │
│ • IntentRouter      │                 └─────────────────────┘
│   (LENS + routing)  │
│                     │                 ┌─────────────────────┐
│ • LENSSynthesis     │                 │ SUPPORT ORCHESTRATORS│
│   (code intelligence)│                │  (14 orchestrators) │
│                     │                 ├─────────────────────┤
│ • EnforcementOrch   │                 │ • OnboardingOrch    │
│   (7-agent system)  │                 │ • ToolDiscoveryOrch │
│                     │                 │ • LENSOrch          │
│ • TDDOrchestrator   │                 │ • ChallengeOrch     │
│   (RED→GREEN→REF)   │                 │ • RecommendationGate│
│                     │                 │ • EducationalOrch   │
│ • IncrementalTask   │                 │ • PlanOrch          │
│   Decomposer        │                 │ • (7 more)          │
│                     │                 └─────────────────────┘
│ • WorkflowOrch      │
│   (stage execution) │
└─────────────────────┘
```

**Total:** 28 Orchestrators (8 core, 6 domain, 14 support)

---

## 4. Governance & Enforcement (4-Layer Defense)

```
┌─────────────────────────────────────────────────────────────────┐
│  USER REQUEST: "implement feature X"                            │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: PRE-EXECUTION GATE (EnforcementOrchestrator)          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  7 Enforcement Agents (Parallel Validation):              │  │
│  │  1. GovernanceEnforcementAgent                            │  │
│  │     → CORE-008 (TDD), 011 (types), 012 (docs), 029       │  │
│  │  2. SecurityCheckpointAgent                               │  │
│  │     → CORE-025 (git), 026 (commits), 027 (audit)         │  │
│  │  3. ComplianceValidationAgent                             │  │
│  │     → Tier 1 domain rules                                 │  │
│  │  4. FileNamingEnforcementAgent                            │  │
│  │     → CORE-028 (kebab-case, no SCREAMING_CASE)           │  │
│  │  5. IncrementalExecutionAgent                             │  │
│  │     → CORE-001 (<500 LOC), 004 (no silent fails)         │  │
│  │  6. MarkdownSuppressionAgent                              │  │
│  │     → CORE-002 (no markdown generation)                   │  │
│  │  7. ArchitectureIntegrityAgent                            │  │
│  │     → CORE-035 (single canonical impl)                    │  │
│  │                                                           │  │
│  │  Verdict: BLOCKED | WARNING | PASS                        │  │
│  │  Performance: <150ms                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼ (if PASS or WARNING)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: RUNTIME MONITORING                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Real-time violation detection                          │  │
│  │  • Violation counter (stops at 3+)                        │  │
│  │  • Pattern matching (anti-patterns)                       │  │
│  │  • Dependency analysis                                    │  │
│  │                                                           │  │
│  │  Actions: WARN | STOP | ROLLBACK                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼ (on completion)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: POST-EXECUTION AUDIT                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Code compliance scan                                   │  │
│  │  • Test coverage validation                               │  │
│  │  • Audit trail verification                               │  │
│  │  • Bypass detection                                       │  │
│  │                                                           │  │
│  │  Output: audit_report, compliance_score                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼ (before deployment)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: PRODUCTION GATE                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • All tests passing                                      │  │
│  │  • Zero P0 violations                                     │  │
│  │  • Complete audit trail                                   │  │
│  │  • Documentation coverage                                 │  │
│  │                                                           │  │
│  │  Verdict: APPROVED | REJECTED                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Coverage:** 26/30 CORE rules automated (87%)  
**Performance:** <150ms pre-execution validation  
**Current Status:** 0 P0 violations (production-ready)

---

## 5. Data Flow: Request → Execution → Completion

```
[User Input]
     │
     ├─ "implement auth system"
     │
     ▼
[MCP Gateway]
     │
     ├─ cortex_process_request(request="implement auth system")
     │
     ▼
[Stage 1: Interaction]
     │
     ├─ Display DoR: "IMPLEMENT | auth system | Estimated: 2-4 hrs"
     ├─ Await approval...
     │
     ▼ (user: "proceed")
[Stage 2: Intent]
     │
     ├─ LENS: IMPLEMENT intent detected
     ├─ CCL: Start async prefetch (rules + infra)
     ├─ Route: IMPLEMENT → TDDOrchestrator
     │
     ▼
[Stage 3: Intelligence]
     │
     ├─ LENS Analysis:
     │   • Dependencies: fastapi, passlib, jwt
     │   • Impact: 3 modules, 8 tests
     │   • Risk: Medium (new auth code)
     │
     ├─ CCL Context (pre-warmed):
     │   • CORE-008: TDD required
     │   • CORE-025: Git commit required
     │   • OWASP: Input validation mandatory
     │
     ▼
[Stage 4: Execution (TDDOrchestrator)]
     │
     ├─ RED: Write failing test
     │   • test_auth_endpoint_requires_valid_token()
     │   • pytest → FAILED ✗
     │
     ├─ GREEN: Implement feature
     │   • Add token validation logic
     │   • pytest → PASSED ✓
     │
     ├─ REFACTOR: Improve code
     │   • Extract validation function
     │   • Add type hints
     │   • pytest → PASSED ✓
     │
     ├─ Governance Check (Layer 1):
     │   • TDD: ✓ Test-first
     │   • Types: ✓ All parameters typed
     │   • Docs: ✓ Docstrings present
     │   • Verdict: PASS
     │
     ├─ Audit Trail:
     │   • AC_START: AC-AUTH-001
     │   • AC_COMPLETE: AC-AUTH-001 ✓ 8/8 tests passing
     │
     ├─ Git Commit:
     │   • Message: "feat: Add token validation (AC-AUTH-001)"
     │   • Pre-commit hook: ✓ All checks passed
     │
     ▼
[Completion Report]
     │
     └─ Display:
        ✅ Implementation Complete
        • Tests: 8/8 passing
        • Coverage: 94%
        • Compliance: 100% (0 violations)
        • Audit: AC-AUTH-001 ✓
        • Files: auth/token_validator.py, tests/test_auth.py
```

**End-to-End Duration:** ~15-45 minutes (typical feature)  
**Quality Gates:** 4 layers (pre-exec, runtime, post-exec, production)  
**Test-First:** 100% of implementations (CORE-008 enforced)

---

## Diagram Generation Tools

These diagrams were **manually created** based on production code analysis.

**For automated diagram generation in future:**
- **PlantUML:** Text-based UML diagrams
- **Mermaid:** Markdown-native diagrams
- **Graphviz:** Dependency graphs
- **py2puml:** Python → UML auto-generation

**See:** `cortex-docs/content/src/diagrams/` for existing diagram sources

---

**Generated from:** CORTEX v1.0.0 (2026-02-15)  
**Architecture:** MCP-First Service-Oriented  
**Orchestrators:** 28 | **Tests:** 16,208 | **Violations:** 0 P0
