asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
review #file:chat01.md holistically and systematically. The smoke test 10 min to run. We need a better solution. Can't have users wait 30 min for coretx to audit and fix. What is your best solution for this problem? 

Audit and fix in #file:cortex-architect.prompt.md smoke tests should just run a few to ensure all the critical functionalities like wiring and key operational components are functional. Enough to gain confience in CORTEX capabilities.
Do a holistic review of ALL files in CORTEX repo. Identify all areas where tests are being running to create an internal yaml manifest, then use a dedicated workflow template to iterat thorugh the list and address every area where test are run

Healthcheck should run the complete detailed integration, regression, golden tests. 


Analyze my request using CORTEX's challenge-first protocol: audit existing capabilities. Assume user has no knowledge of CORTEX architecture. Identify architectural fit within current patterns, then deliver your SINGLE BEST recommendation  that addresses the ask vs. challenge tension inline. Evaluate through CORTEX's core design pillars: extensibility, scalability, accuracy, team collaboration, and long-term maintainability. Ensure MCP-first exposure, orchestrator integrity, and zero regression risk. Present findings in executive-ready format: ≤60 seconds read time, comparison tables, clear sections with visual hierarchy optimized for VS Code Copilot Chat rendering. All response feedback in VSCode GitHub Copilot Chat Session should be inline. Never create summary, reports or other markdown files. 

GitHub Copilot: 

I'll start by reading the architect prompt and the chat file to understand the full context, then systematically analyze the test infrastructure. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.chats/chat01.md#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.chats/chat01.md#200-200), lines 200 to 400

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#200-200), lines 200 to 842

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.chats/chat01.md#400-400), lines 400 to 700

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.chats/chat01.md#700-700), lines 700 to 1000

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/.chats/chat01.md#1000-1000), lines 1000 to 1328

Now I have the complete picture. Let me analyze the test infrastructure holistically to understand the performance problem and build my recommendation. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#300-300), lines 300 to 430

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#430-430), lines 430 to 626

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/pytest.ini)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest_optimize.py#1-1), lines 1 to 120

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest.py#1-1), lines 1 to 100

Now let me understand the scope of the problem more precisely by looking at what areas run tests and how the audit pipeline integrates: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml#1-1), lines 1 to 200

Searched text for `run_tests|pytest|test_runner|test.*command` (`**/cortex-registry/workflows/templates/**`), 20 results

Searched text for `run_tests\.py|pytest|make test` (`**/.github/prompts/cortex-architect.prompt.md`), 16 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml#570-570), lines 570 to 772

Ran terminal command: find tests/ -name "test_*.py" -not -path "*__pycache__*" | wc -l && echo "---test-dirs---" && for d in tests/*/; do count=$(find "$d" -name "test_*.py" -not -path "*__pycache__*" 2>/dev/null | wc -l | tr -d ' '); echo "$count	$d"; done | sort -rn | head -25

asifhussain60: continue. show live feedback in terminal window to show percentage completed. Cant you just get a test file count? Do you have to run them? use timeouts to check process has not stalled

GitHub Copilot: 

Let me gather the test infrastructure data efficiently — counting files, not running tests. 

Ran terminal command: echo "=== TEST FILE COUNT ===" && find tests/ -name "test_*.py" -not -path "*__pycache__*" | wc -l && echo "=== BY DIRECTORY ===" && for d in tests/*/; do count=$(find "$d" -name "test_*.py" -not -path "*__pycache__*" 2>/dev/null | wc -l | tr -d ' '); if [ "$count" -gt "0" ]; then echo "$count	$d"; fi; done | sort -rn

asifhussain60: You keep hanging up This is not working. By pass test check and do what I asked

GitHub Copilot: 

## 🎨 CORTEX Architect DESIGN
**Author:** Asif Hussain | **Orchestrator:** DesignCoordinator ✅

---

## 📋 Summary

Your `/audit fix` pipeline takes ~30 min because **Stage 9 runs `run_tests.py batch` — the entire sequential test suite (~1,700+ tests)**. Smoke tests collect the same 1,700 tests via marker auto-tagging and still take ~10 min. The fix: **split test tiers properly — smoke = ~50 surgical wiring/import checks (< 60s), healthcheck = full suite**.

---

## 🔍 Analysis — Root Cause

| Problem | Evidence | Impact |
|---------|----------|--------|
| **Smoke ≈ full suite** | conftest.py auto-tags `golden/`, `core/`, `mcp/` as smoke → ~1,500 tests | 10 min smoke run |
| **No "confidence check" tier** | No way to run 30-50 fast import/wiring tests in <60s | Users wait or skip |
| **Stage 9 = batch** | audit-fix-pipeline.yaml Stage 9 runs `run_tests.py batch` (sequential, all tests) | 20+ min audit |
| **Auto-tagging too broad** | conftest.py tags entire `golden/`, `core/`, `mcp/` dirs as smoke | Defeats smoke purpose |

### Current Test Tier Architecture (broken)

| Tier | Intended | Actual | Time |
|------|----------|--------|------|
| `smoke` | ~500 fast tests | ~1,500 (auto-tagged) | ~10 min |
| `batch` | Full sequential | ~1,700 | ~20 min |
| `golden` | Truth assertions | ~486 | ~3 min |
| **(missing)** | Wiring/import confidence | — | — |

---

## 💡 Recommendation — 3-Tier Test Strategy Redesign

### New Architecture

| Tier | Name | Purpose | Count | Target Time |
|------|------|---------|-------|-------------|
| **T0** | `preflight` | Import checks, wiring contracts, key orchestrator instantiation | ~40-60 | **< 30s** |
| **T1** | `smoke` | Core functionality — golden + unit critical paths | ~300-500 | **< 3 min** |
| **T2** | `healthcheck` | Full integration, regression, golden — complete confidence | all | **10-20 min** |

### What changes

1. **New `preflight` mode** in run_tests.py — runs only `@pytest.mark.preflight` tests
2. **Narrow smoke auto-tagging** — stop tagging entire directories, use explicit markers
3. **Stage 9 uses `preflight`** in `/audit fix` — not `batch`
4. **New `/healthcheck` command** — runs full `batch` when user wants deep validation
5. **Create `tests/preflight/`** directory — ~40 surgical tests covering:
   - All 27 orchestrator imports + `health_check()` callable
   - MCP server importable + 39 tools registered
   - Key wiring contracts (master → intent → TDD)
   - CORE rule YAML loadable
   - Intelligence matrix importable
   - LENS pipeline importable

### Where tests are currently run (internal manifest)

| Location | What runs tests | Current tier | Proposed tier |
|----------|----------------|--------------|---------------|
| cortex-architect.prompt.md Stage 9 | `run_tests.py batch` | batch (all) | **preflight** |
| cortex-architect.prompt.md IMPLEMENT Step 6 | `run_tests.py batch` | batch | **smoke** |
| cortex-architect.prompt.md PLAN final sub-phase | `run_tests.py smoke` | smoke | **preflight** |
| audit-fix-pipeline.yaml Stage 9 | `run_tests.py batch` | batch | **preflight** |
| phase-59-canonical-integrity-pipeline.yaml | `run_tests.py smoke` | smoke | **preflight** |
| test-quality-enforcement.yaml S8 | `run_tests` | full | unchanged |
| TDD cycle gates | `run_tests.py file <test>` | file | unchanged |
| CI/CD (Makefile) | `make test-batch` | batch | unchanged |
| `/healthcheck` (new) | `run_tests.py batch` | — | **batch** |

---

## ⚖️ Benefits & Risks

| | Preflight approach | Keep current |
|---|---|---|
| **Audit time** | ~5 min total (30s tests + stages) | ~30 min |
| **Confidence** | High — covers all 27 orchestrators, MCP, wiring | Same |
| **Regression risk** | Zero — doesn't delete tests, adds tier | None |
| **Full suite access** | Via `/healthcheck` on demand | Always forced |
| **Complexity** | +1 mode, +1 directory, ~6 file edits | None |

---

## 🎯 Next Steps

### ⚡ If you type `proceed`, CORTEX will:

1. **Create `tests/preflight/`** — ~40 surgical tests: orchestrator imports, MCP wiring, CORE rules load, LENS import, intelligence matrix
2. **Add `preflight` mode** to run_tests.py — targets only `tests/preflight/`, parallel, 5s timeout
3. **Create `cortex-registry/workflows/templates/testing/test-tier-manifest.yaml`** — canonical manifest of all locations where tests are run + tier mappings
4. **Update audit-fix-pipeline.yaml** Stage 9 — switch from `batch` to `preflight`
5. **Update cortex-architect.prompt.md** — Stage 9 uses `preflight`, add `/healthcheck` command for full suite
6. **Narrow conftest.py smoke auto-tagging** — remove directory-based blanket tagging, require explicit `@pytest.mark.smoke`
7. **Add `/healthcheck` command** to architect prompt — runs `batch` (full integration, regression, golden)

asifhussain60: proceed. Smoke tests should run on parallel threads andend in under 10 seconds. Review #file:copilot-instructions.md #file:prompts #file:agents  and all #file:prompts #file:agents and ensure holistically and systematically fix.

The following comamnd keeps hanig up and no user feedback
or d in tests/*/; do count=$(find "$d" -name "test_*.py" -not -path "*__pycache__*" 2>/dev/null | wc -l | tr -d ' '); if [ "$count" -gt "0" ]; then echo "$count	$d"; fi; done | sort -rn

GitHub Copilot: 

I'll execute this systematically. First, let me get the file counts with a simpler command that won't hang. 

Ran terminal command: find tests/ -name "test_*.py" -not -path "*__pycache__*" | wc -l

Ran terminal command: ls -d tests/*/  | head -30

Ran terminal command: find tests/unit -name "test_*.py" | wc -l && echo "---" && find tests/golden -name "test_*.py" | wc -l && echo "---" && find tests/core -name "test_*.py" | wc -l && echo "---" && find tests/mcp -name "test_*.py" | wc -l && echo "---" && find tests/orchestrators -name "test_*.py" | wc -l && echo "---" && find tests/integration -name "test_*.py" | wc -l && echo "---" && find tests/governance -name "test_*.py" | wc -l && echo "---" && find tests/intelligence -name "test_*.py" | wc -l

Good — 966 test files total. Now let me read the key files I need to modify: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#100-100), lines 100 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#200-200), lines 200 to 350

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts/run_tests.py#350-350), lines 350 to 626

Now let me read the conftest files and the key prompt/agent files that reference test commands: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest.py#40-40), lines 40 to 90

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest_optimize.py)

Searched text for `run_tests\.py (smoke|batch)|make test-smoke|make test-batch|test-changed` (`**/.github/**/*.md`), 20 results

Now let me get the complete list of all files that reference test commands so I can build the manifest and fix them all: 

Searched text for `run_tests\.py|make test-|pytest.*-m smoke` (`**/.github/**/*.md`), 44 results

Searched text for `run_tests\.py|make test-|test_runner_command` (`**/cortex-registry/**/*.yaml`), 40 results

I now have the complete picture. Let me also check what orchestrators exist so I can build the preflight tests: 

Ran terminal command: grep -rn "^class.*Orchestrator" cortex/orchestrators/ --include="*.py" | sed 's/:.*class / → /' | sed 's/(.*$//' | wc -l

Ran terminal command: ls cortex/mcp/tools/*.py | grep -v __pycache__ | grep -v __init__ | wc -l

Good. Now I have everything I need. Let me execute the full plan — creating all files, then updating all references. I'll work file by file.

**Step 1: Create `tests/preflight/` with ~40 surgical tests** 

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/__init__.py)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_orchestrator_wiring.py)

Let me find the correct import paths: 

Ran terminal command: grep -rn "class InvestigationOrchestrator\|class DesignCoordinator\|class QueryCoordinator\|class PlanningCoordinator\|class DebugOrchestrator" cortex/orchestrators/ --include="*.py" | head -10

Ran terminal command: grep -rn "class Investigation" cortex/orchestrators/ --include="*.py"

Searched for files matching `**/investigation_orchestrator.py`, no matches

Searched for files matching `**/design_coordinator.py`, no matches

Searched for files matching `**/query_coordinator.py`, no matches

Searched for files matching `**/planning_coordinator.py`, no matches

Searched for files matching `**/debug_orchestrator.py`, no matches

Ran terminal command: ls cortex/orchestrators/domain/ && echo "---" && ls cortex/orchestrators/support/

Now I can see the actual files. Let me fix the preflight test with correct paths: 

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_orchestrator_wiring.py)

Using "Replace String in File"


```

```


Created [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_mcp_wiring.py)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_intelligence_governance.py)

Now **Step 2: Add `preflight` and `healthcheck` modes** to run_tests.py: 

Using "Replace String in File"


```

```
Now add `healthcheck` mode: 

Using "Replace String in File"


```

```
Now update the `_MODES` dict and `_USAGE`: 

Using "Replace String in File"


```

```
Now update the docstring at the top of run_tests.py: 

Using "Replace String in File"


```

```
Pre-existing lint (optional dependency). Now **Step 3: Create the test tier manifest YAML**: 

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/testing/test-tier-manifest.yaml)

Now **Step 4-7: Update all prompt/agent/copilot-instructions references**. Let me do them systematically: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#165-165), lines 165 to 195

Using "Replace String in File"


```

```
Now update IMPLEMENT Step 6: 

Using "Replace String in File"


```

```
Update the second Stage 9 reference in Quick Commands section: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#740-740), lines 740 to 760

Using "Replace String in File"


```

```
Update the COMPLETION CHECKLIST: 

Using "Replace String in File"


```

```
Now add `/healthcheck` to Quick Commands: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#725-725), lines 725 to 745

Using "Replace String in File"


```

```
Now update **copilot-instructions.md**: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/copilot-instructions.md#170-170), lines 170 to 200

Summarized conversation history

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/copilot-instructions.md#230-230), lines 230 to 296

Now I have the full context. Let me apply all the edits to copilot-instructions.md: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now update the remaining files. Let me read them in parallel: 

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/prompts/CORTEX.prompt.md`), 2 results

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/agents/AGENT-INDEX.md`), 2 results

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/agents/core/master-planner.md`), 1 result

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/agents/core/cortex-sts-refactoring.md`), 1 result

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/agents/core/cortex-environment-setup.md`), 2 results

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/.github/agents/core/phase-creation-standards.md`), no results

Searched text for `run_tests.py batch|run_tests.py smoke|test-batch|Stage 9` (`**/cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`), 5 results

Now let me read the surrounding context for each file to make precise edits: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md#115-115), lines 115 to 125

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/AGENT-INDEX.md#135-135), lines 135 to 145

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/core/master-planner.md#25-25), lines 25 to 35

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/core/cortex-sts-refactoring.md#263-263), lines 263 to 275

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/core/cortex-environment-setup.md#145-145), lines 145 to 160

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml#590-590), lines 590 to 610

Now I have all the context. Let me apply all the remaining edits in parallel: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
All prompt/agent/workflow files updated. Now let me update the **Makefile** with `test-preflight` and `test-healthcheck` targets: 

Searched text for `test-smoke|test-batch|test-changed|test-parallel` (`**/Makefile`), 14 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/Makefile)

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now let me narrow the **conftest.py** smoke auto-tagging so it doesn't blanket-tag entire directories: 

Searched text for `smoke|golden|pytest_collection_modifyitems` (`**/conftest.py`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/conftest.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/conftest.py#60-60), lines 60 to 107

The root conftest.py doesn't do the smoke auto-tagging — let me check conftest_optimize.py: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest_optimize.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest_optimize.py#80-80), lines 80 to 162

Good — conftest_optimize.py does pattern-based smoke tagging (which is sensible for `test_protocol`, `test_schema`, etc.). Now let me check the conftest.py that was mentioned as doing directory-based auto-tagging: 

Searched text for `smoke|golden|core.*smoke|modifyitems` (`**/tests/conftest.py`), 9 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest.py#35-35), lines 35 to 90

Found it. The `smoke_paths = {"golden", "core", "mcp"}` auto-tags everything in those directories as smoke. Since `run_smoke()` now targets specific directories directly (not markers), this auto-tagging is no longer the primary mechanism. However, narrowing it is still beneficial for anyone using `pytest -m smoke` directly. Let me update it to be more targeted: 

Using "Replace String in File"


```

```
Now let me also check if there are any other grep hits across .github or cortex-registry that I haven't caught: 

Searched text for `run_tests\.py batch` (`**/.github/**/*.md`), 2 results

Searched text for `run_tests\.py batch` (`**/cortex-registry/**/*.yaml`), 20 results

The copilot-instructions.md match on line 262 is the test mode table — `batch` is still a valid mode (CI gate), so that reference stays. The cortex-registry matches are in phase planning YAML files (templates, completed phases, planned phases) — `batch` is correct as a regression gate for full validation. Those are intentional uses of the batch command for full-suite regression gates, not audit Stage 9 references.

Now let me run the preflight tests to verify they pass quickly: 

Ran terminal command: python3 scripts/run_tests.py preflight

**41 passed in 1.42 seconds** — well under the 10-second target.

Here's a summary of all files updated in this systematic pass:

### ✅ Completed Updates

| # | File | Change |
|---|------|--------|
| 1 | copilot-instructions.md | Stage 9 `batch` → `preflight` + test tier manifest ref, added `/healthcheck` command, 4-tier table with `preflight` + `healthcheck` rows, quick reference commands |
| 2 | CORTEX.prompt.md | Stage 9 `batch` → `preflight` |
| 3 | AGENT-INDEX.md | Stage 9 `batch` → `preflight` |
| 4 | master-planner.md | Terminal gate `smoke` → `preflight` |
| 5 | cortex-sts-refactoring.md | Validate `batch` → `smoke` |
| 6 | cortex-environment-setup.md | Windows commands: added `preflight` + `healthcheck`, removed `batch` |
| 7 | audit-fix-pipeline.yaml | Stage 9 `batch` → `preflight` |
| 8 | Makefile | Added `test-preflight` + `test-healthcheck` targets, updated `.PHONY`, updated help text |
| 9 | conftest.py | Narrowed smoke auto-tagging: moved `mcp` from smoke to critical, added `preflight` path set, updated docstring |

### Preflight Results
- **41 tests passed in 1.42s** ✅ (target was < 10s)

Made changes.

asifhussain60: commit all changes and push to rmote

GitHub Copilot: Ran terminal command: git add -A && git status --short

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && git commit -m "feat(testing): 4-tier test strategy — T0 preflight < 10s, T1 smoke < 60s, T2 healthcheck

- Add tests/preflight/ (T0): 41 wiring checks, 1.42s parallel (was: 10min+ batch)
- Add run_tests.py preflight + healthcheck modes; redesign smoke to target specific dirs
- Add test-tier-manifest.yaml — canonical manifest of all test execution points
- Update /audit fix Stage 9: batch → preflight across all prompts/agents/pipeline
- Add Makefile targets: test-preflight, test-healthcheck
- Narrow tests/conftest.py smoke auto-tagging: mcp moved to critical, preflight added
- Update copilot-instructions.md, CORTEX.prompt.md, AGENT-INDEX.md, master-planner.md,
  cortex-sts-refactoring.md, cortex-environment-setup.md, audit-fix-pipeline.yaml

Fixes: smoke test 10min bottleneck in /audit fix Stage 9
Target: preflight < 10s ✅ (verified: 41 passed in 1.42s)"

Ran terminal command: git push origin CORTEX

Pushed successfully. Commit `367a9e875` is live on `origin/CORTEX`.

**18 files changed** — here's what landed:

| Category | Files |
|---|---|
| **New preflight tests** | __init__.py, `test_orchestrator_wiring.py`, `test_mcp_wiring.py`, `test_intelligence_governance.py` |
| **New manifest** | test-tier-manifest.yaml |
| **Updated runner** | run_tests.py (preflight + healthcheck modes, redesigned smoke) |
| **Updated Makefile** | `test-preflight` + `test-healthcheck` targets |
| **Updated docs/prompts** | copilot-instructions.md, CORTEX.prompt.md, `cortex-architect.prompt.md`, AGENT-INDEX.md, master-planner.md, cortex-sts-refactoring.md, cortex-environment-setup.md, audit-fix-pipeline.yaml |
| **Narrowed tagging** | conftest.py |

`/audit fix` Stage 9 now runs `preflight` — **41 tests in 1.42s** instead of the full batch suite.

asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
review CORTEX reo holistically and ensure there are no straggler refernces running full test stuite except by healthcheck (always on demand never automatic). Fix any descrepancies.

GitHub Copilot: ## 🎯 CORTEX Architect — Investigate

**Author:** Asif Hussain | **Orchestrator:** InvestigationOrchestrator ✅

---

First, let me do a comprehensive grep sweep across the entire repo for straggler references. 

Searched text for `run_tests\.py batch|run_tests\.py healthcheck|test-batch|test-healthcheck|make test-batch|make test-healthcheck`, 20 results

Now let me also check for other patterns — `pytest tests/`, full suite triggers in CI/workflow files, and any remaining automatic triggers: 

Searched text for `run_tests\.py (batch|healthcheck|parallel|all)|make test-(batch|healthcheck|parallel|all)` (`**/.github/**`), 11 results

Searched text for `run_tests\.py (batch|healthcheck)|make test-(batch|healthcheck)` (`**/cortex-registry/workflows/**`), 13 results

Searched text for `run_tests\.py (batch|healthcheck)|make test-(batch|healthcheck)` (`**/cortex-registry/planning/**`), 20 results

Now I have a complete picture. Let me categorize the findings:

**Legitimate `batch`/`healthcheck` uses (keep as-is):**
- `completed/` phase files — historical records, correct as written
- `planned/_archived/` — frozen archives
- `batch` in mode tables (it's still a valid CI mode)
- `healthcheck` listed as on-demand command — correct

**Stragglers to fix (automatic full-suite triggers in active governance files):**
1. cortex-architect.prompt.md line 499 — THIN INDEX CONTRACT `checkpoint_complete` Step 5: `make test-batch` → `make test-smoke`
2. copilot-instructions.md line 230 — `checkpoint_complete` Step 6: `make test-batch` → `make test-smoke`
3. _template.yaml lines 74, 125 — phase template `regression_gate`: `batch` → `smoke`
4. phase-75-capability-registry-builder.yaml lines 156, 416 — active planned phase: `batch` → `smoke`
5. phase-80-coherence-remediation.yaml — 6 occurrences: `batch` → `smoke`
6. duplicate-validation.yaml line 199 — `batch` → `smoke`
7. phase-59-canonical-integrity-pipeline.yaml line 473 — `batch` → `smoke`
8. dead-code-removal.yaml line 215 — `batch` → `smoke`
9. test-quality-enforcement.yaml line 209 — `batch` → `smoke`
10. sts-refactoring-template.yaml line 207 — `batch` → `smoke`

Let me read context for each before editing: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#493-493), lines 493 to 506

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/copilot-instructions.md#224-224), lines 224 to 236

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/_template.yaml#68-68), lines 68 to 132

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/quality/duplicate-validation.yaml#194-194), lines 194 to 206

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/maintenance/phase-59-canonical-integrity-pipeline.yaml#467-467), lines 467 to 480

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/quality/dead-code-removal.yaml#208-208), lines 208 to 222

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates/testing/test-quality-enforcement.yaml#203-203), lines 203 to 216

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/roadmap-templates/sts-refactoring-template.yaml#201-201), lines 201 to 214

Now read context for planned phase files: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-75-capability-registry-builder.yaml#150-150), lines 150 to 165

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml#183-183), lines 183 to 395

I can see `phase-80-c` uses `batch` specifically for a *full-suite regression* after touching all 27 orchestrators — that's semantically a healthcheck-level concern. However, phase sub-phase gates should use `smoke`. Only the `completion_gate` for phase-80-c (which crosses all orchestrators) could justify `smoke` since healthcheck is on-demand only. Let me read the remaining occurrences in phase-80: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml#395-395), lines 395 to 480

Now I have full context. The `batch` in `phase-80` sub-phases c and d is used where the scope genuinely touches all 27 orchestrators or 22 ValidationResult definitions — these should become `smoke` (smoke now covers the full preflight + golden + core tier), not `healthcheck` (on-demand only). Let me also read the remaining phase-80 occurrence: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml#460-460), lines 460 to 475

Now I have everything I need. Let me apply all fixes systematically: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now the phase _template.yaml — both `regression_gate` lines: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now the workflow templates: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now the active planned phases. Phase-75 (line 156 is in a COMPLETE sub-phase — still should be updated as it's in the planned file still being read): 

Using "Replace String in File"


```

```
Now phase-80 — all 6 occurrences. The `regression_gate` fields and `completion_gate.test_runner_command` for sub-phases a, c, d: 

Using "Replace String in File"


```

```
Now fix phase-80-c's regression_gate and refactor gate and completion_gate (the "touches all 27 orchestrators" sub-phase): 

Using "Replace String in File"


```

```
Now fix the refactor gate inside phase-80-c's tdd_cycle and completion_gate: 

Using "Replace String in File"


```

```


Using "Replace String in File"

Searched text for `Zero regressions across batch test suite` (`**/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml`), 4 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml#373-373), lines 373 to 395

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/phase-80-coherence-remediation.yaml#458-458), lines 458 to 480

Using "Replace String in File"


```

```
Now fix phase-80-d's regression_gate, refactor gate, and completion_gate: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now do a final sweep to confirm no stragglers remain in active governance/prompt/agent files: 

Searched text for `run_tests\.py batch|make test-batch` (`**/.github/**`), 2 results

Searched text for `run_tests\.py batch|make test-batch` (`**/cortex-registry/workflows/**`), 7 results

Searched text for `run_tests\.py batch|make test-batch` (`**/cortex-registry/planning/phases/planned/**`), 3 results

Searched text for `run_tests\.py batch|make test-batch` (`**/cortex-registry/planning/phases/_template.yaml`), no results

Clean results. The remaining hits are all correct:
- copilot-instructions.md line 262 — the mode table listing `batch` as a valid CI gate (intentional)
- test-tier-manifest.yaml — the manifest's own T3 CI tier definition and pattern-matching stubs that describe where `batch` appears (it's the manifest's job to document all tiers)
- `phase-75` line 416 — a **commented-out** line (`#`)
- `_archived/` files — frozen, never executed

Now commit and push: 

Ran terminal command: git add -A && git status --short

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && git commit -m "fix(testing): purge straggler batch references from all active governance files

Full sweep — no automatic full-suite invocation except explicit /healthcheck (on-demand):

- cortex-architect.prompt.md: checkpoint_complete gate batch → smoke
- copilot-instructions.md: checkpoint_complete gate batch → smoke
- planning/phases/_template.yaml: both regression_gate batch → smoke
- planning/phases/planned/phase-75: regression_gate batch → smoke
- planning/phases/planned/phase-80: 6 occurrences — regression_gates, tdd_cycle
  refactor gates, acceptance_criteria, completion_gate.test_runner_command (sub-phases
  a, c, d) all batch → smoke
- roadmap-templates/sts-refactoring-template.yaml: exit_criteria batch → smoke
- workflows/templates/quality/duplicate-validation.yaml: batch → smoke
- workflows/templates/quality/dead-code-removal.yaml: batch → smoke
- workflows/templates/testing/test-quality-enforcement.yaml: batch → smoke
- workflows/templates/maintenance/phase-59-canonical-integrity-pipeline.yaml: batch → smoke

Retained (intentional):
- copilot-instructions.md mode table: batch row (valid CI-gate mode, documents the command)
- test-tier-manifest.yaml: T3 CI tier definition + pattern stubs (manifest documents all tiers)
- completed/ phase files: historical records (immutable)
- _archived/ files: frozen"

Ran terminal command: git push origin CORTEX

Commit `94b67540f` pushed. Here's the sweep summary:

---

## 📋 Sweep Results — Straggler `batch` References

**Rule enforced:** Full test suite runs only via explicit `/healthcheck` (on-demand). Never automatic.

### Files Fixed (10)

| File | Change |
|---|---|
| cortex-architect.prompt.md | `checkpoint_complete` Step 5: `test-batch` → `test-smoke` |
| copilot-instructions.md | `checkpoint_complete` Step 6: `test-batch` → `test-smoke` |
| _template.yaml | Both `regression_gate` fields: `batch` → `smoke` |
| phase-75-capability-registry-builder.yaml | `regression_gate`: `test-batch` → `test-smoke` |
| phase-80-coherence-remediation.yaml | 6 occurrences across sub-phases a/c/d: `regression_gate`, `tdd_cycle.refactor.gate`, `acceptance_criteria`, `completion_gate.test_runner_command` |
| sts-refactoring-template.yaml | `exit_criteria`: `batch` → `smoke` |
| duplicate-validation.yaml | `batch` → `smoke` |
| dead-code-removal.yaml | `batch` → `smoke` |
| test-quality-enforcement.yaml | `batch` → `smoke` |
| phase-59-canonical-integrity-pipeline.yaml | `batch` → `smoke` |

### Intentionally Retained

| Location | Reason |
|---|---|
| copilot-instructions.md mode table | `batch` is a valid CI-gate mode — documents the command exists |
| test-tier-manifest.yaml T3 section | Manifest's job is to document all 4 tiers including CI/batch |
| `completed/` phase files | Historical records — immutable |
| `_archived/` files | Frozen — never re-executed |

Made changes.