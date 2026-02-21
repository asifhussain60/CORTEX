asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
review CORTEX holistically and systematically . AUDIT overall layout based on #file:audit.txt. Have we built a fully tested, with all KEY functionalites with end to end audit log validated golden tests to ensure orchestrators work end to end as expected.

GitHub Copilot: 

I'll start by reading the architect prompt and the audit file to understand the full requirements, then systematically review the CORTEX codebase. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#1-1), lines 1 to 200

Searched for files matching `**/audit.txt`, 2 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#200-200), lines 200 to 570

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.recommendations/audit.txt)

Now let me systematically gather the data needed for this holistic audit. I'll examine orchestrators, tests, golden tests, MCP tools, wiring contracts, and key infrastructure. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden)

Searched for files matching `**/wiring*.yaml`, 2 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/domain)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/support)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/health)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/intelligence)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/strategies)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/synthesis)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/validation)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/workflow)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/git)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/routing)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/holistic_integration)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/governance)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/production)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators/support)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators/health_vacuum)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators/master_plan)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators/plan_gate)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/orchestrators/phase_50)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/agents)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/onboarding)

Now let me examine the wiring contract, OrchestratorBase protocol, key golden tests, and test infrastructure: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/wiring/specifications/wiring.yaml#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/orchestrator_base.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/wiring/specifications/wiring.yaml#200-200), lines 200 to 287

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/orchestrator_base.py#100-100), lines 100 to 285

Now let me check for golden tests that specifically validate audit trails end-to-end, and check the audit_db infrastructure: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_audit_trail_verification.py)

Searched text for `audit_db|AuditEntry|EventType|audit_trail` (`**/cortex/infrastructure/**`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/production/test_implement_workflow.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/production/test_implement_workflow.py#100-100), lines 100 to 271

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/production/test_audit_workflow.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/production/test_onboard_workflow.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/infrastructure/audit_db.py#1-1), lines 1 to 120

Searched text for `AC_START|AC_COMPLETE|audit_trail|ORCHESTRATOR_START|ORCHESTRATOR_END` (`**/tests/golden/**`), 20 results

Let me now check for critical gaps — do golden tests exist for all key orchestrators, and is there e2e audit trail validation: 

Ran terminal command: find tests/golden -name "*.py" -not -name "__init__.py" -not -name "conftest.py" | sort

Ran terminal command: find cortex/orchestrators -name "*.py" -not -name "__init__.py" -not -name "*.old*" -not -name "*.backup*" | wc -l

Ran terminal command: find cortex/orchestrators -name "*.py" -not -name "__init__.py" -not -name "*.old*" -not -name "*.backup*" | head -80

Ran terminal command: find tests/golden -name "*.py" -not -name "__init__.py" -not -name "conftest.py" | wc -l

Ran terminal command: grep -rl "pytest.mark.skip\|@pytest.mark.skip" tests/golden/ | wc -l

Ran terminal command: grep -rn "pytest.mark.skip" tests/golden/ | head -20

Ran terminal command: grep -rn "def test_" tests/golden/test_audit_trail_verification.py

Ran terminal command: wc -l tests/golden/test_audit_trail_verification.py

This is a critical finding. Now let me check more areas: 

Ran terminal command: grep -rn "audit_db\|get_audit_db\|AuditEntry\|ORCHESTRATOR_START\|ORCHESTRATOR_END" tests/ --include="*.py" | grep -v "__pycache__" | wc -l

Ran terminal command: grep -rn "audit_db\|get_audit_db\|AuditEntry" tests/golden/ --include="*.py" | head -20

Ran terminal command: grep -rn "def test_" tests/golden/ --include="*.py" | wc -l

Now let me check some critical areas for the audit - stale imports, wiring contract health, MCP tools count, and test mirror: 

Ran terminal command: grep -rn "from cortex_intelligence\|from cortex_lens\|from cortex\.brain\." cortex/ --include="*.py" | grep -v "__pycache__" | head -20

Ran terminal command: ls cortex/mcp/tools/*.py | grep -v __pycache__ | grep -v __init__ | wc -l

Ran terminal command: find cortex/orchestrators -name "*.old*" -o -name "*.backup*" -o -name "DEPRECATED*" | head -10

Ran terminal command: find . -name "*.db" -not -path "./.cortex-runtime/*" -not -path "./.git/*" -not -path "./node_modules/*" | head -10

Ran terminal command: ls -la cortex/orchestrators/core/architecture_guard.py* 2>/dev/null; ls -la cortex/orchestrators/core/coordination/ 2>/dev/null; ls -la cortex/orchestrators/core/execution/ 2>/dev/null; ls -la cortex/orchestrators/core/integration/ 2>/dev/null; ls -la cortex/orchestrators/core/solid_analyzers/ 2>/dev/null; ls -la cortex/orchestrators/core/validation/ 2>/dev/null

Ran terminal command: cat cortex/orchestrators/core/solid_analyzers/__init__.py | head -30

Now let me check the key orchestrator E2E coverage and check what the holistic integration tests look like: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/holistic_integration/test_holistic_integration_simple.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_mcp_e2e_truth.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_mcp_e2e_truth.py#60-60), lines 60 to 222

Now let me check the intent router and master orchestrator for key functionality: 

Ran terminal command: grep -rn "def test_" tests/orchestrators/core/ --include="*.py" | wc -l

Ran terminal command: find tests/orchestrators/core -name "*.py" -not -name "__init__.py" | sort

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators/core)

Ran terminal command: find tests/ -name "*.py" -not -name "__init__.py" -not -name "conftest*.py" | grep -i "master_orchestrator\|intent_router\|enforcement_orchestrator\|interaction_orchestrator\|request_rephrase" | sort

Ran terminal command: find tests/ -name "*.py" -not -name "__init__.py" -not -name "conftest*.py" | grep -i "security_orchestrator\|refactoring_orchestrator\|tdd_orchestrator\|conversation_orchestrator" | sort

Now let me check which wired orchestrators have NO corresponding golden/e2e tests: 

Ran terminal command: grep -E "name:|class:" cortex/core/wiring/specifications/wiring.yaml | grep "name:" | awk -F'"' '{print $2}'

Ran terminal command: grep -rn "health_check\|def health_check" cortex/core/orchestrator_base.py cortex/orchestrators/core/master_orchestrator.py cortex/orchestrators/core/tdd_orchestrator.py cortex/orchestrators/core/intent_router.py cortex/orchestrators/core/enforcement_orchestrator.py

Ran terminal command: grep -rn "def health_check" cortex/orchestrators/ --include="*.py" | head -20

Ran terminal command: grep -rn "class.*OrchestratorBase\|class.*ABC" cortex/orchestrators/core/master_orchestrator.py cortex/orchestrators/core/tdd_orchestrator.py cortex/orchestrators/core/intent_router.py cortex/orchestrators/core/enforcement_orchestrator.py | head -10

Ran terminal command: head -40 cortex/orchestrators/core/master_orchestrator.py

Ran terminal command: grep -n "class MasterOrchestrator" cortex/orchestrators/core/master_orchestrator.py

Ran terminal command: grep -rn "class.*Orchestrator.*OrchestratorBase" cortex/orchestrators/ --include="*.py" | head -20

Ran terminal command: grep -rn "class.*IOrchestrator\|class.*OrchestratorAuditMixin\|class.*OrchestratorBase" cortex/orchestrators/core/tdd_orchestrator.py cortex/orchestrators/core/enforcement_orchestrator.py cortex/orchestrators/core/intent_router.py cortex/orchestrators/core/security_orchestrator.py | head -10

Ran terminal command: grep -rn "class EnforcementOrchestrator" cortex/orchestrators/ --include="*.py"

Ran terminal command: grep -rn "class EnforcementOrchestrator" cortex/orchestrators/git/enforcement_orchestrator.py

Ran terminal command: grep -rn "class.*Orchestrator" cortex/orchestrators/git/enforcement_orchestrator.py

Now let me check the `SeleniumPlaywrightOrchestrator` — the wiring references a `migration` module that doesn't exist: 

Ran terminal command: python3 -c "from cortex.orchestrators.migration.selenium_playwright_orchestrator import SeleniumPlaywrightOrchestrator" 2>&1

Ran terminal command: find cortex -name "*selenium*" -o -name "*playwright*" 2>/dev/null

Critical finding: `SeleniumPlaywrightOrchestrator` is wired but doesn't exist. Let me check `ArchitectureGuard`: 

Ran terminal command: python3 -c "from cortex.orchestrators.core.architecture_guard import ArchitectureGuard" 2>&1

Ran terminal command: ls cortex/orchestrators/core/architecture_guard*

Another critical finding. Let me now do a broader check of all wired module paths: 

Ran terminal command: grep 'module:' cortex/core/wiring/specifications/wiring.yaml | awk -F'"' '{print $2}' | while read mod; do python3 -c "import $mod" 2>&1 | grep -v "^$" && echo "FAIL: $mod" || echo "OK: $mod"; done

This is very revealing. Let me check the CORE rules registry and count: 

Ran terminal command: find cortex-registry/core -name "CORE-*.yaml" -o -name "CORE-*.yml" | sort

Ran terminal command: ls cortex-registry/core/

Ran terminal command: ls cortex-registry/core/governance/

Ran terminal command: grep -c "CORE-" cortex-registry/core/governance/governance-kernel.yaml

Ran terminal command: grep "CORE-" cortex-registry/core/governance/governance-kernel.yaml

Ran terminal command: grep -rn "CORE-" cortex-registry/core/governance/skull-rules.yaml | head -30

Ran terminal command: grep "rule_id: CORE-" cortex-registry/core/governance/skull-rules.yaml | wc -l

Ran terminal command: grep "rule_id: CORE-" cortex-registry/core/governance/skull-rules.yaml

Now let me check for the brain directory (should be deleted per spec): 

Ran terminal command: ls -la cortex/brain/ 2>/dev/null | head -5

Ran terminal command: find cortex/brain -type f | head -10

Ran terminal command: find cortex/brain -type f | wc -l

Let me run one final set of checks — total test count and key test coverage areas: 

Ran terminal command: grep -rn "def test_" tests/ --include="*.py" | wc -l

Ran terminal command: find tests/ -name "*.py" -empty -not -name "__init__.py" | head -10

Ran terminal command: grep -rn "pass$" tests/golden/ --include="*.py" | grep "def test_" -A1 | head -20

Ran terminal command: grep -B1 "pass$" tests/golden/production/test_audit_workflow.py

Now let me check the holistic integration harness and priority conflicts: 

Ran terminal command: grep "priority:" cortex/core/wiring/specifications/wiring.yaml | awk -F': ' '{print $2}' | sort -n | uniq -d

Good — no duplicate priorities. Let me do the final checks: 

Ran terminal command: find . -maxdepth 1 -type f -not -name "conftest.py" -not -name "pyproject.toml" -not -name "pytest.ini" -not -name "README.md" -not -name "requirements.txt" -not -name "Makefile" -not -name ".gitignore" -not -name ".python-version" -not -name "*.cfg" -not -name "*.toml" -not -name ".DS_Store" | head -20

Ran terminal command: grep -rn "Phase 52 TODO\|Phase 53 TODO\|TODO.*audit" tests/golden/ --include="*.py" | wc -l

Ran terminal command: grep -rn "Phase 52 TODO" tests/golden/holistic_integration/ --include="*.py" | head -15

Now I have enough data. Let me compile the comprehensive audit report.

---

## 🔎 CORTEX HOLISTIC COHESIVENESS AUDIT
**Orchestrator:** Architect ✅ | **Date:** 2026-02-21

---

## 📋 Summary

CORTEX has a **massive foundation** — 15,421 tests, 536 golden tests across 44 files, 214 orchestrator source files, 23 MCP tools, and 33 CORE governance rules. However, the system is **NOT fully cohesive** as a unified brain. There are **6 critical (P0) blockers**, **5 high-severity (P1) gaps**, and **7 moderate (P2) issues** preventing true end-to-end validated orchestrator operation.

---

## 🔍 Analysis — Findings Table

### ⛔ P0 — CRITICAL BLOCKERS (Must Fix)

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| **P0-1** | **6 wired orchestrators fail to import** | `ArchitectureGuard`, `SeleniumPlaywrightOrchestrator`, `UnifiedAnalysisOrchestrator`, `UnifiedDiscoveryOrchestrator`, `UnifiedQualityOrchestrator`, `ComplexityAnalyzer` — all throw `ModuleNotFoundError` | Wiring contract structurally broken; lazy-load will crash at runtime. L1 blocking failure. |
| **P0-2** | **`test_audit_trail_verification.py` is EMPTY (0 bytes)** | The designated golden test file for E2E audit trail validation has zero content | **No end-to-end audit trail golden test exists.** The most critical cohesion validation is absent. |
| **P0-3** | **101 "Phase 52 TODO" deferrals** in golden tests | Holistic integration tests have audit trail assertions commented out: `# Phase 52 TODO: Audit trail validation` | Golden tests pass execution but **do NOT validate audit trail completeness** — the core requirement from the audit.txt spec. |
| **P0-4** | **No `health_check()` on any wired orchestrator** | Only `CrossLayerOptimizer` implements `health_check()`. Zero of the 26 wired orchestrators expose the method. Wiring YAML says `health_check: "ping"` but the method doesn't exist. | GP50 Health Check Protocol is a phantom; health endpoints are dead. |
| **P0-5** | **2 golden audit workflow tests are SKIPPED** | `test_audit_codebase_compliance` and `test_audit_detects_core_008_violation` both `@pytest.mark.skip(reason="EnforcementOrchestrator integration deferred")` | Core audit workflow golden path is untested. |
| **P0-6** | **brain directory still exists** (12 files) | Contains dashboard CSS/JS assets. Prompt spec says "dissolved" and "never reference." | Violates CORE-035 (single canonical), architect prompt explicitly marks as deleted. |

### 🟠 P1 — HIGH SEVERITY (Should Fix)

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| **P1-1** | **Inconsistent base class hierarchy** | `MasterOrchestrator(IOrchestrator, OrchestratorAuditMixin)`, `TDDOrchestrator(IOrchestrator)`, `EnforcementOrchestrator` (no inheritance at all). `OrchestratorBase` with 5-step lifecycle is only used by `LegacyModernizationOrchestrator`. | No uniform lifecycle contract across orchestrators. Can't reliably call `setup→govern→execute→validate→teardown` on all. |
| **P1-2** | **CORE rules count mismatch** | Prompt says "17 CORE rules", registry has **33 rules** (CORE-001 through CORE-054). | Documentation/prompt is stale. Governance kernel disagrees with architect prompt. |
| **P1-3** | **No golden tests for 20+ wired orchestrators** | Missing golden coverage: `SecurityOrchestrator`, `ArchitectureGuard`, `EnhancedPlanningOrchestrator`, `CodeLevelPlanner`, `DomainOrchestrator`, `DependencyResolver`, `SeleniumPlaywright`, `SetupOrchestrator`, `RollbackOrchestrator`, `ToolchainValidator`, `UpgradeOrchestrator`, etc. | Most orchestrators have no E2E proof they work end-to-end. |
| **P1-4** | **MCP E2E golden test is shallow** | test_mcp_e2e_truth.py tests server initialization and JSON-RPC parsing, but does NOT exercise a full tool invocation cycle with audit trail verification. | MCP "truth test" doesn't prove the 23 tools work end-to-end. |
| **P1-5** | **4 empty `__init__.py` sub-packages in core** | `coordination/`, `execution/`, `integration/`, `validation/` under core contain only `__init__.py` — no actual modules. `solid_analyzers/` has a 20KB `__init__.py` with all code in one file. | Phantom packages; confusing structure. |

### 🟡 P2 — MODERATE (Improve)

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| **P2-1** | **`architecture_guard.py.old-complex`** in active directory | 21KB deprecated file sitting alongside active orchestrators | Violates repo hygiene protocol (no `.old` files in active dirs). |
| **P2-2** | **Priority range doesn't match spec** | Spec says: Master=10, IntentRouter=20, Core=30-99. Actual: Master=100, TDD=95, IntentRouter=90. Priorities are inverted from documented ranges. | Wiring documentation misleading. |
| **P2-3** | **4 empty test files** | `test_promotion_gate.py`, `test_context_budget_manager.py`, `test_audit_trail_verification.py`, `test_semantic_blocks.py` | Dead weight; violates CORE-008 (tests must have content). |
| **P2-4** | **`solid_analyzers/__init__.py` is 20KB** | All SOLID analyzer code packed into single `__init__.py` instead of separate modules | Violates SRP and CORE-028 (organization). |
| **P2-5** | **Stale references in comments** | `cortex_lens` and `cortex_intelligence` appear in comments in `dashboards/json_data_generator.py` and tool utilities | Not blocking but misleading. |
| **P2-6** | **Phase 27 golden tests conditionally skipped** | 3 phase_27 golden test files use `skipif` based on module availability | Phase 27 may have incomplete deployment. |
| **P2-7** | **Wiring validation rules don't match OrchestratorBase** | Wiring YAML `required_methods` lists `get_name`, `get_version`, `initialize` — but `OrchestratorBase` exposes `setup`, `govern`, `execute_operation`, `validate`, `teardown` | Contract and implementation diverge. |

---

## 💡 Recommendation — Remediation Priority

### Phase 1: Fix Critical (P0) — Must do before any "production-ready" claim

1. **Fix wiring contract** — Remove or implement the 6 broken orchestrator entries. For `ArchitectureGuard`, either restore from `.old-complex` or remove from wiring. For `SeleniumPlaywright`, create module or remove entry.
2. **Implement `test_audit_trail_verification.py`** — This is the SINGLE MOST IMPORTANT gap. Create a golden test that:
   - Instantiates a real orchestrator (e.g., TDDOrchestrator)
   - Executes a complete lifecycle
   - Queries `CortexAuditDB` for `ORCHESTRATOR_START` and `ORCHESTRATOR_END` events
   - Validates timestamps, orchestrator_id, status, duration_ms
   - Confirms governance_checks table has entries
   - Proves the full audit chain: `User Request → Stage 0 → IntentRouter → Target Orchestrator → Enforcement → Audit DB`
3. **Resolve the 101 "Phase 52 TODO" audit trail assertions** — Uncomment and implement audit trail validation in holistic integration tests.
4. **Add `health_check()` to `OrchestratorBase`** — Default implementation returning `{"status": "healthy", "uptime": N, "request_count": N}`.
5. **Remove skips from audit workflow golden tests** — Implement the `EnforcementOrchestrator` integration.
6. **Delete brain** — Move dashboard assets to dashboards or assets.

### Phase 2: Fix High (P1)

7. **Unify orchestrator base class** — All wired orchestrators should extend `OrchestratorBase` or implement `IOrchestrator` + `OrchestratorAuditMixin`.
8. **Correct CORE rules count** — Update architect prompt from "17" to "33" or explicitly mark the active subset.
9. **Add golden tests for wired orchestrators** — At minimum: `SecurityOrchestrator`, `EnforcementOrchestrator`, `RefactoringOrchestrator`, `RollbackOrchestrator`.
10. **Deepen MCP E2E test** — Execute `cortex_sample_tool` through real MCPServer and verify audit trail entry.

---

## ⚖️ Benefits & Risks

| Metric | Current State | Target State |
|--------|--------------|--------------|
| Wired orchestrators importable | 20/26 (77%) | 26/26 (100%) |
| Golden test files | 44 | 55+ (add per-orchestrator) |
| E2E audit trail golden tests | **0** | **5+** |
| Orchestrators with `health_check()` | 1/26 (4%) | 26/26 (100%) |
| Skipped golden tests | 7 files | 0 |
| "Phase 52 TODO" deferrals | 101 | 0 |
| CORE rules documented vs actual | 17 vs 33 | Aligned |

---

## 🎯 Next Steps

1. **Fix the 6 broken wiring entries** — immediate, ~30 min
2. **Write `test_audit_trail_verification.py`** — the #1 missing golden test, ~2 hours
3. **Implement `health_check()` in `OrchestratorBase`** — ~1 hour
4. **Delete brain directory** — move assets, ~15 min
5. **Remove `architecture_guard.py.old-complex`** — ~5 min
6. **Batch-resolve Phase 52 TODOs** — prioritize audit trail assertions, ~4 hours

### ⚡ If you type `proceed`, CORTEX will:
- Fix the wiring contract (wiring.yaml) by removing the 6 broken entries
- Implement test_audit_trail_verification.py with 5+ E2E audit trail golden tests
- Add `health_check()` to `OrchestratorBase` with default implementation
- Delete brain and `architecture_guard.py.old-complex`
- Run `make test-batch` to verify zero regressions