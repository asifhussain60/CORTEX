---
prompt_id: cortex-totalrecall
version: "1.0"
status: active
mode: REFACTOR
author: Asif Hussain
updated: 2026-02-26
agent: cortex-architect.md
orchestrators_used:
  - MasterOrchestrator (cortex/orchestrators/core/master_orchestrator.py)
  - EnforcementOrchestrator (cortex/orchestrators/core/enforcement_orchestrator.py)
  - TDDOrchestrator (cortex/orchestrators/core/tdd_orchestrator.py)
  - RefactoringOrchestrator (cortex/orchestrators/domain/refactoring_orchestrator.py)
  - HealthOrchestrator (cortex/orchestrators/health/health_orchestrator.py)
  - VacuumOrchestrator (cortex/orchestrators/health/vacuum_orchestrator.py)
  - SweepCatalogueOrchestrator (cortex/orchestrators/support/sweep_catalogue_orchestrator.py)
mcp_tools:
  - cortex_validate
  - cortex_governance
  - cortex_load
  - cortex_check
  - cortex_vacuum
  - cortex_tools_catalog
  - cortex_total_recall
token_cost_estimate: 4500
---

# CORTEX Total Recall — Holistic Production Readiness Protocol

**Author:** Asif Hussain | **Orchestrator:** MasterOrchestrator ✅
**Updated:** 2026-02-26 | **Authority:** `.github/prompts/cortex-totalrecall.prompt.md`
**Scope:** Full codebase refactor to 100% production readiness — zero drift, zero duplication, zero contradictions

---

## 🎯 Purpose

**Total Recall** is a single-command holistic refactoring protocol that systematically audits,
refactors, and hardens the entire CORTEX codebase to 100% production readiness. Unlike `/audit fix`
(which scans and patches), Total Recall **restructures** — it eliminates root causes, not symptoms.

**When to use Total Recall vs `/audit fix`:**

| Dimension | `/audit fix` | `/totalrecall` |
|-----------|-------------|----------------|
| Scope | 19-point checklist scan | Full codebase holistic refactor |
| Depth | Surface violations | Root-cause structural issues |
| Output | Violations table + patches | Restructured files + unified brain |
| Duration | Minutes | Hours (multi-session capable) |
| Goal | Pass audit gate | 100% production readiness |

---

## 🔧 Usage

```
/totalrecall                           # Full protocol — all 7 phases
/totalrecall phase={N}                 # Resume from specific phase
/totalrecall scope=prompts             # Target: prompts/ + agents/ only
/totalrecall scope=registry            # Target: cortex-registry/ only
/totalrecall scope=orchestrators       # Target: cortex/orchestrators/ only
/totalrecall scope=tests               # Target: tests/ only
/totalrecall scope=intelligence        # Target: cortex/intelligence/ + cortex/lens/
/totalrecall dry-run                   # Audit only — no edits
```

---

## 🏗️ 7-Phase Protocol

Total Recall executes **7 sequential phases** — each phase must complete before the next begins.
Every phase follows TDD (CORE-008) and Sweep Completeness (CORE-064).

```
Phase 1: INVENTORY        — Catalog everything (facts only, zero opinions)
Phase 2: CONTRADICTION     — Detect conflicts, drift, duplication, version violations
Phase 3: ARCHITECTURE      — Map the unified brain (tiers, routing, SSOT ownership)
Phase 4: CONSOLIDATION     — Merge duplicates, eliminate contradictions, enforce single canonical
Phase 5: HARDENING         — Type hints, docstrings, AC markers, test coverage, security
Phase 6: COHERENCE         — Cross-reference validation, end-to-end pipeline verification
Phase 7: CERTIFICATION     — Full test suite, regression proof, production sign-off
```

---

## Phase 1: INVENTORY (Facts Only)

**Goal:** Produce a complete, accurate catalog of every component in the system.
**Rule:** Zero opinions, zero recommendations — facts only.

### 1.1 File Inventory

Catalog every file in the following directories with: path, line count, purpose (1 sentence), last modified.

| Directory | What to catalog |
|-----------|----------------|
| `.github/prompts/` | Every `.prompt.md` — what mode it serves, which orchestrator it routes to |
| `.github/agents/` | Every agent `.md` — what intent it handles, what it duplicates |
| `.github/templates/` | Every template — what format it defines |
| `cortex/orchestrators/` | Every orchestrator — domain, tier, wiring status, health |
| `cortex/mcp/tools/` | Every MCP tool — operation, registry name, deprecated status |
| `cortex/core/` | Every core module — responsibility, dependencies |
| `cortex/intelligence/` | Every intelligence module — what data it consumes/produces |
| `cortex/lens/` | Every analyzer — pipeline position, input/output types |
| `cortex/governance/` | Every enforcement module — what rules it checks |
| `cortex-registry/core/` | Every governance YAML — rule count, tier, enforcement level |
| `cortex-registry/config/` | Every config YAML — what loader consumes it |
| `cortex-registry/workflows/` | Every workflow template — what pipeline it defines |
| `tests/` | Top-level test dirs — test count per dir, golden vs unit vs integration |

### 1.2 Responsibility Matrix

For each of these **12 cross-cutting concerns**, identify which files own it (SSOT) and which files duplicate it:

| Concern | Expected SSOT | Check for duplicates in |
|---------|--------------|------------------------|
| Intent routing table | `cortex/orchestrators/core/intent_router.py` | prompts, agents, copilot-instructions.md |
| CORE rules list | `cortex-registry/core/tier0-skull/skull-rules.yaml` | prompts, agents, copilot-instructions.md |
| MCP tool count/list | `cortex/mcp/tools/` (source of truth) | prompts, agents, copilot-instructions.md |
| Orchestrator count | `cortex-registry/core/specifications/` wiring YAMLs | prompts, agents, copilot-instructions.md |
| `/audit fix` pipeline | `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml` | prompts, agents |
| Response format | `.github/templates/cortex-response-templates.md` | prompts, agents |
| File placement rules | `cortex-architect.prompt.md` § FILE PLACEMENT | prompts, agents, copilot-instructions.md |
| Deleted path warnings | `cortex-architect.prompt.md` § Deleted paths | prompts, agents |
| Quick commands table | `CORTEX.prompt.md` § QUICK COMMANDS | cortex-architect.prompt.md, copilot-instructions.md |
| Test execution rules | `copilot-instructions.md` § Test Execution | prompts |
| AC marker rules | `cortex-architect.prompt.md` § CROSS-CUTTING INTELLIGENCE | prompts, agents |
| Brain tiers / intelligence | `cortex/intelligence/provider.py` | prompts, agents |

### 1.3 Output Format

```
## Phase 1: INVENTORY COMPLETE
- Files cataloged: {N}
- Orchestrators: {N} wired, {N} unwired
- MCP tools: {N} active, {N} deprecated
- CORE rules: {N} active
- Tests: {N} total ({N} golden, {N} unit, {N} integration)
- SSOT violations: {N} concerns with duplicate ownership
- Contradictions detected: {N} (detailed in Phase 2)
```

---

## Phase 2: CONTRADICTION DETECTION

**Goal:** Identify every conflict, drift, duplication, and version violation.
**Rule:** Every finding must cite both source locations with line numbers.

### 2.1 Numeric Drift

Scan all prompts, agents, and copilot-instructions.md for these values. Flag any mismatch:

| Metric | Canonical Value | Canonical Source | Scan targets |
|--------|----------------|-----------------|-------------|
| Orchestrator count | Count from wiring YAMLs | `cortex-registry/core/specifications/` | All `.md` in `.github/` |
| MCP tool count | Count from `cortex/mcp/tools/` | File system | All `.md` in `.github/` |
| CORE rule count | Count from `skull-rules.yaml` | `cortex-registry/core/tier0-skull/` | All `.md` in `.github/` |
| Audit check count | Count from `audit-checklist.yaml` | `cortex-registry/governance/` | All `.md` in `.github/` |
| Meta-audit check count | Count from `cortex-meta-auditor.md` | `.github/agents/core/` | All `.md` in `.github/` |
| Phase count | Count from `cortex-master.yaml` | `cortex-registry/` | `copilot-instructions.md` |
| Test count | Count from pytest collection | `python3 -m pytest --collect-only` | `copilot-instructions.md` |

### 2.2 Version Drift (CORE-035 — P0)

**Command:**
```bash
grep -rn 'version.*[2-9]\.' cortex-registry/ .github/ cortex/ \
  --include="*.yaml" --include="*.yml" --include="*.md" --include="*.py" \
  | grep -v 'python-version\|python_version\|Python.*version\|sys.version\|version_info' \
  | grep -v 'pytest.*version\|pip\|CDN\|library.*version\|node_modules' \
  | grep -v '>=\|<=\|OWASP\|D3\|Chart\.js\|mermaid' \
  | grep -v 'completed/'
```

**Rule:** Zero matches allowed. Every CORTEX-internal version must be `1.0`.
Any match = P0 violation → remediate in Phase 4.

### 2.3 Content Duplication

For each cross-cutting concern from §1.2, compare the text across all locations:
- **Identical duplication** — same content in multiple files → consolidate to SSOT + pointer
- **Conflicting duplication** — different content on same topic → P0, resolve in Phase 4
- **Intentional duplication** — different loading contexts need the same data → mark as ACCEPTED with justification

### 2.4 Structural Drift

| Check | Command | Expected |
|-------|---------|----------|
| Ghost directories | `find cortex/ -maxdepth 1 -name "*.*" -type d` | Zero matches |
| Stale imports | `grep -rn 'cortex_intelligence\|cortex_lens\|cortex\.brain\|from cortex.brain' cortex/ tests/` | Zero matches |
| Orphan files | `find cortex/ -name "*.py" -not -path "*__pycache__*"` vs wiring contracts | All files accounted for |
| Empty stubs | AST scan for `pass`/`...`-only function bodies in `cortex/` | Zero in production code |
| Deprecated files | `find . -name "DEPRECATED-*" -o -name "*.old" -o -name "*.backup"` | Zero in active dirs |

### 2.5 Output Format

```
## Phase 2: CONTRADICTIONS FOUND

| # | Type | Severity | Location A | Location B | Resolution |
|---|------|----------|-----------|-----------|------------|
| 1 | Numeric drift | P1 | file:line | file:line | Update B to match A |
| ... |
```

---

## Phase 3: ARCHITECTURE (Unified Brain Map)

**Goal:** Define the authoritative architecture — who owns what, how things route, what loads when.

### 3.1 Brain Tiers (Loading Model)

Document the canonical 3-tier loading model:

| Tier | File | When Loaded | Token Budget | What It Contains |
|------|------|-------------|-------------|-----------------|
| **T0 — Auto** | `copilot-instructions.md` | Every session (auto by GitHub Copilot) | ~300 tokens | Architecture summary, key rules, test commands |
| **T1 — Prompt** | `CORTEX.prompt.md` or `cortex-architect.prompt.md` | Per session type (user selects) | ~1,500-2,700 tokens | Full mode definitions, routing, governance, response format |
| **T2 — Agent** | Individual agent files | Per intent (lazy-loaded) | ~1,000-5,000 tokens | Specialist logic for specific modes |

**Rule:** Each tier may repeat key facts (counts, rules) for context, but the **values** must be identical.
Conflicting values across tiers = P0 violation.

### 3.2 SSOT Ownership Map

For every cross-cutting concern, declare the single canonical owner:

```yaml
ssot_ownership:
  intent_routing: cortex/orchestrators/core/intent_router.py
  core_rules: cortex-registry/core/tier0-skull/skull-rules.yaml
  mcp_tools: cortex/mcp/tools/  # directory = source of truth
  orchestrator_wiring: cortex-registry/core/specifications/
  audit_pipeline: cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml
  response_format: .github/templates/cortex-response-templates.md
  file_placement: cortex-architect.prompt.md  # § FILE PLACEMENT
  test_execution: copilot-instructions.md  # § Test Execution
  ac_markers: cortex-architect.prompt.md  # § CROSS-CUTTING INTELLIGENCE
  deleted_paths: cortex-architect.prompt.md  # § Deleted paths
  quick_commands: CORTEX.prompt.md  # § QUICK COMMANDS
  modes: cortex-registry/config/modes.yaml
```

### 3.3 Pipeline Integrity

Verify every pipeline is wired end-to-end:

| Pipeline | Entry | Stages | Exit | Verification |
|----------|-------|--------|------|-------------|
| `/audit fix` | MasterOrchestrator | 9 stages (-1 through 9) | AC_COMPLETE | `cortex_validate` op=`compliance` |
| `/totalrecall` | This prompt | 7 phases | CERTIFICATION | Full test suite green |
| Intent routing | MasterOrchestrator.coordinate_operation() | 4 stages | Domain orchestrator result | Health check all 22 |
| YAML loading | yaml_loaders.py | 4 loaders | Pydantic models | `load_core_rules()` + 3 others |
| TDD cycle | TDDOrchestrator | RED→GREEN→REFACTOR | Tests passing | `run_tests.py smoke` |

---

## Phase 4: CONSOLIDATION (Eliminate Contradictions)

**Goal:** Fix every contradiction found in Phase 2. Single canonical value everywhere.
**Rule:** Every edit must be TDD — write a test that fails on the contradiction, then fix.

### 4.1 Numeric Alignment

For every numeric drift found in Phase 2:
1. Determine the canonical value from the source of truth
2. Update all locations to match
3. Verify with grep that no stale values remain

### 4.2 Version Normalization

For every version drift found in Phase 2:
1. Change the version field to `"1.0"`
2. If source code emits a version, update the source + tests
3. Re-run the grep scan — must return zero matches

### 4.3 Duplication Resolution

For every content duplication found in Phase 2:

| Duplication Type | Action |
|-----------------|--------|
| Identical (same content, N files) | Keep in SSOT, replace others with pointer reference |
| Conflicting (different content, same topic) | Determine correct value, update all to match |
| Intentional (same content, different loading contexts) | Keep as-is, add `<!-- SSOT: {path} -->` comment to non-canonical copies |

### 4.4 Structural Cleanup

- Delete ghost directories
- Rewrite stale imports
- Delete deprecated/backup files
- Implement or delete empty stubs
- Consolidate scattered .db/.log files into `.cortex-runtime/`

### 4.5 Verification Gate

```bash
# All loaders work
python3 -c "from cortex.core.yaml_loaders import load_core_rules, load_audit_checklist, load_modes, load_response_format; [f() for f in [load_core_rules, load_audit_checklist, load_modes, load_response_format]]; print('ALL LOADERS PASS')"

# Zero version drift
grep -rn 'version.*[2-9]\.' cortex-registry/ .github/ cortex/ --include="*.yaml" --include="*.md" --include="*.py" | grep -v 'python\|pip\|CDN\|>=\|<=\|OWASP\|completed/' | wc -l
# Expected: 0

# Tests pass
make test-preflight
```

---

## Phase 5: HARDENING

**Goal:** Every public API has type hints + docstrings. Every orchestrator has AC markers.
Every module has test coverage ≥80%.

### 5.1 Type Hints (CORE-011)

```bash
# Find functions missing type hints in production code
grep -rn "def " cortex/ --include="*.py" | grep -v "__pycache__" | grep -v "-> " | grep -v "test_" | head -50
```

Every function in `cortex/` must have return type annotation and parameter type annotations.

### 5.2 Docstrings (CORE-012)

```bash
# Find public functions missing docstrings
python3 -c "
import ast, pathlib
for f in pathlib.Path('cortex').rglob('*.py'):
    if '__pycache__' in str(f): continue
    try:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    print(f'{f}:{node.lineno} {node.name}()')
    except: pass
" | head -50
```

### 5.3 AC Markers

Every public orchestrator method must have `AC_START` and `AC_COMPLETE` markers.

```bash
# Find orchestrators missing AC markers
for f in $(find cortex/orchestrators -name "*.py" -not -name "__init__*" -not -path "*__pycache__*"); do
  if ! grep -q "AC_START\|AC_COMPLETE" "$f"; then
    echo "MISSING AC: $f"
  fi
done
```

### 5.4 Test Coverage

```bash
# Check coverage per module
python3 -m pytest tests/ --cov=cortex --cov-report=term-missing --cov-fail-under=80 -q 2>&1 | tail -30
```

### 5.5 Security Hardening

| Check | Command | Expected |
|-------|---------|----------|
| No hardcoded secrets | `grep -rn 'password\|secret\|api_key\|token' cortex/ --include="*.py" \| grep -v 'test_\|#\|"""'` | Zero real credentials |
| No eval/exec | `grep -rn 'eval(\|exec(' cortex/ --include="*.py"` | Zero matches or justified |
| Dependencies pinned | `pip check` | No broken dependencies |
| No SQL injection | `grep -rn 'f".*SELECT\|f".*INSERT\|f".*UPDATE\|f".*DELETE' cortex/ --include="*.py"` | Zero matches |

---

## Phase 6: COHERENCE (Cross-Reference Validation)

**Goal:** Every reference in every file resolves to a real target. End-to-end pipelines work.

### 6.1 Path References

```bash
# Extract all file path references from prompts/agents and verify they exist
grep -rn '`cortex/\|`cortex-registry/\|`.github/\|`.cortex-runtime/' .github/ --include="*.md" | \
  grep -oP '`[^`]+`' | sort -u | while read -r path; do
    clean=$(echo "$path" | tr -d '`')
    [ ! -e "$clean" ] && echo "BROKEN: $path"
  done
```

### 6.2 YAML Cross-References

```bash
# Validate all YAML files parse without errors
find cortex-registry -name "*.yaml" -exec python3 -c "
import yaml, sys
try:
    yaml.safe_load(open(sys.argv[1]))
except Exception as e:
    print(f'INVALID: {sys.argv[1]}: {e}')
" {} \;
```

### 6.3 Import Validation

```bash
# Verify all cortex imports resolve
python3 -c "
import importlib, pathlib
for f in pathlib.Path('cortex').rglob('*.py'):
    if '__pycache__' in str(f) or f.name == '__init__.py': continue
    module = str(f).replace('/', '.').replace('.py', '')
    try:
        importlib.import_module(module)
    except Exception as e:
        print(f'IMPORT FAIL: {module}: {e}')
" 2>&1 | head -30
```

### 6.4 End-to-End Pipeline Verification

| Pipeline | Test Command | Expected |
|----------|-------------|----------|
| YAML loaders | `python3 -c "from cortex.core.yaml_loaders import load_core_rules, load_audit_checklist, load_modes, load_response_format; [f() for f in [load_core_rules, load_audit_checklist, load_modes, load_response_format]]; print('PASS')"` | `PASS` |
| MCP tools importable | `python3 -c "from cortex.mcp import tools; print('PASS')"` | `PASS` |
| Orchestrator health | All 22 orchestrators return `status: healthy` | 22/22 healthy |
| Wiring contracts valid | All wiring YAML specs load and reference importable modules | Zero broken refs |
| Golden tests | `python3 -m pytest tests/golden/ -q` | All pass |

### 6.5 Vacuum Cleanup

**Goal:** Clean workspace of markdown sprawl, root clutter, and stale runtime artifacts before certification.
**Orchestrator:** `VacuumOrchestrator` (`cortex/orchestrators/health/vacuum_orchestrator.py`)
**MCP Tool:** `cortex_vacuum`

This step runs the same vacuum pipeline as `/audit fix` Stage 5, ensuring Total Recall
(the superset protocol) includes everything `/audit fix` does.

```bash
# Vacuum targets:
# 1. Markdown sprawl — orphaned .md files outside canonical dirs
# 2. Root clutter — files that belong in subdirectories
# 3. Runtime hygiene — stale .db/.log files in .cortex-runtime/
# 4. __pycache__ cleanup — stale bytecode dirs

find . -maxdepth 1 -name "*.md" -not -name "README.md" -not -name "LICENSE*" -not -name "CHANGELOG*" -not -name "CONTRIBUTING*" | head -20
find . -name "__pycache__" -type d | wc -l
find .cortex-runtime -name "*.log" -mtime +30 2>/dev/null | wc -l
```

**Rule:** Vacuum runs after coherence checks (Phase 6.1–6.4) and before certification (Phase 7)
so the final test suite executes against a clean workspace.

---

## Phase 7: CERTIFICATION (Production Sign-Off)

**Goal:** Prove 100% readiness with passing tests, zero violations, and documented evidence.

### 7.1 Test Suite

```bash
# Full test suite — must pass with zero new failures
make test-preflight      # < 10s — wiring/import checks
make test-smoke          # < 60s — preflight + core
make test-parallel       # Full suite — all tiers
```

### 7.2 Governance Scan

```bash
# Zero P0/P1 violations
# (conceptual — run via MCP or manually inspect)
cortex_validate op=compliance    # via MCP tool
cortex_governance op=query       # via MCP tool
```

### 7.3 Production Readiness Scorecard

| Category | Weight | Check | Target |
|----------|--------|-------|--------|
| Architecture | 25% | Zero SSOT conflicts, all wiring valid | 100% |
| Security | 25% | No credentials, no eval/exec, deps pinned | 100% |
| Testing | 20% | Coverage ≥80%, golden tests green, no low-value tests | ≥80% |
| Documentation | 15% | All public APIs have docstrings, prompts coherent | 100% |
| Governance | 10% | Zero P0/P1 violations, AC markers present | 100% |
| Traceability | 5% | SQLite activity log healthy, no orphaned AC_START | 100% |

**Pass threshold:** Weighted score ≥ 95%

### 7.4 Certification Output

```
## 🎯 CORTEX Total Recall — CERTIFICATION

**Date:** {date}
**Score:** {weighted_score}% ({PASS|FAIL})

### Results by Category
| Category | Score | Issues |
|----------|-------|--------|
| Architecture | {score}% | {count} issues |
| Security | {score}% | {count} issues |
| Testing | {score}% | {count} issues |
| Documentation | {score}% | {count} issues |
| Governance | {score}% | {count} issues |
| Traceability | {score}% | {count} issues |

### Regression Proof
- Preflight: {N}/{N} pass
- Smoke: {N}/{N} pass ({N} pre-existing failures)
- Golden: {N}/{N} pass
- New failures introduced: 0

### AC_COMPLETE: AC-TOTALRECALL-{TIMESTAMP} ✅
```

---

## ⛔ Hard Rules (Immutable)

| Rule | Enforcement |
|------|-------------|
| **CORE-002** | All output inline — never create .md/.txt report files |
| **CORE-008** | TDD mandatory — write failing test before every fix |
| **CORE-035** | Single canonical implementation — zero version drift, zero forks |
| **CORE-048** | Holistic validation gate before structural changes |
| **CORE-049** | Silent autonomous execution — progress bars only |
| **CORE-064** | Sweep Completeness — no partial sweeps, exhaust full catalogue |
| **Zero versioning** | Everything is version 1.0 — no v2, no "enhanced" copies |
| **Zero contradictions** | No two files may give conflicting guidance on the same topic |
| **SSOT enforcement** | One file owns each concept; all others pointer-reference it |

---

## 🔄 Multi-Session Support

Total Recall is designed to run across multiple Copilot Chat sessions if needed.

**Session continuity protocol:**
1. At end of each session, emit current phase + completion status
2. At start of next session, reference this prompt + specify phase to resume
3. Each phase is independently verifiable — no hidden state between phases

**Resume command:**
```
/totalrecall phase=4    # Resume from Phase 4: CONSOLIDATION
```

**Progress tracking:**
```
[██████████] 100% Phase 1: INVENTORY ✅
[██████████] 100% Phase 2: CONTRADICTION ✅
[██████████] 100% Phase 3: ARCHITECTURE ✅
[████░░░░░░]  40% Phase 4: CONSOLIDATION 🔵
[░░░░░░░░░░]   0% Phase 5: HARDENING ⚪
[░░░░░░░░░░]   0% Phase 6: COHERENCE ⚪
[░░░░░░░░░░]   0% Phase 7: CERTIFICATION ⚪
```

---

## 🔗 References

| Doc | Purpose |
|-----|---------|
| `cortex-architect.prompt.md` | Architect prompt (execution modes, CORE rules, response format) |
| `CORTEX.prompt.md` | Master orchestrator prompt (routing, governance) |
| `copilot-instructions.md` | Auto-loaded instructions (architecture summary) |
| `.github/templates/cortex-response-templates.md` | Response formatting SSOT |
| `cortex-registry/core/tier0-skull/skull-rules.yaml` | CORE governance rules |
| `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml` | Audit pipeline definition |
| `cortex-registry/config/modes.yaml` | HEXA-MODE definitions |
| `_workspaces/.chats/totalrecall.md` | Original spec (challenge-first protocol) |

---

**Token Usage:** ~4,500
