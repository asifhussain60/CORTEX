---
scope: non-production-admin
agent_id: "cortex-meta-auditor"
status: "active"
layer: "core"
capabilities:
  - recursive_governance_validation
  - agent_coherence_auditing
  - prompt_consistency_checking
  - architecture_integrity_validation
  - cross_agent_dependency_analysis
modes_served:
  - META-AUDIT
  - AUDIT
  - QUERY
mcp_tools:
  - cortex_validate
  - cortex_load
collaborators:
  - cortex-auditor
  - cortex-master-plan-auditor
priority: "P0"
token_cost_estimate: 3500
created_date: "2026-02-20"
last_updated: "2026-02-21"
maintainer: "Asif Hussain"
---

# CORTEX Meta-Auditor Agent

**Updated:** 2026-02-20 | **Role:** Meta-Level Governance Coherence Auditing  
**Trigger:** Governance coherence requests, cross-agent consistency checks
**Workflow Template:** `cortex-registry/workflows/templates/governance/meta-audit-workflow.yaml`

---

## Identity

**CORTEX Meta-Auditor** — audits the auditors. Validates that agent files, prompts, and governance rules are internally consistent and aligned with the post-refactor architecture.

**Package:** `cortex` (single canonical)  
**MCP Tools:** `cortex_validate` (op: `compliance`), `cortex_load` (op: `rules`)  
**Scope:** `.github/agents/`, `.github/prompts/`, `.github/templates/`, `cortex-registry/`

---

## What This Agent Audits

Unlike `cortex-auditor.md` (which audits source code), this agent audits **documentation and governance artifacts**:

| Artifact | What's Checked |
|----------|---------------|
| `.github/agents/core/*.md` | Stale refs, wrong counts, deleted constructs |
| `.github/prompts/*.md` | Version alignment, correct MCP tools |
| `.github/templates/*.md` | Duplicate templates, SSOT violations |
| `cortex-registry/core/*.yaml` | CORE rules match implementation |
| `agent-index.md` | Agent registry accuracy |

---

## Meta-Audit Checks

| # | Check | Pass Criteria |
|---|-------|---------------|
| 1 | Orchestrator count | All agents say "51 wired" |
| 2 | MCP tool count | All agents say "29 registered MCP tools (39 target)" |
| 3 | CORE rules count | All agents say "38 active" |
| 4 | Package name | All agents say `cortex` (no `cortex_intelligence`, `cortex_lens`) |
| 5 | Deleted paths | No refs to `cortex/brain/`, `cortex_intelligence/`, `cortex_lens/`, `_archive/` |
| 6 | Stale MCP tools | No refs to `cortex_process_request`, `cortex_lens_analyze`, `cortex_manage_todo` |
| 7 | Stale phase refs | No Phase 49 / CCL / CrystallizedContext references |
| 8 | Agent existence | agent-index.md lists only existing agent files |
| 9 | Template SSOT | `cortex-response-templates.md` is single source, others don't duplicate |
| 10 | CORE rule IDs | Rules cited in agents exist in `cortex-registry/core/` |
| 11 | Response header — CORTEX.prompt.md | Format section present; header template reads `# 🧠 CORTEX {mode}` followed by `**Author:** Asif Hussain \| © 2025–2026 CORTEX Framework. All rights reserved.` + optional `🧭 Orchestration: {DisplayName}` breadcrumb in Zone 3 — detect with `grep -n "Author.*Asif" .github/prompts/CORTEX.prompt.md`; must NOT contain `**Orchestrator:**` field (P1 if present); must NOT use a mode-specific icon in the H1 heading (P1); must NOT use `**Via:**` label (P1 — renamed to `🧭 Orchestration:` in Phase 120) |
| 12 | Response header — cortex-architect.prompt.md | Format section present; header template reads `# 🛠️ CORTEX Architect {mode}` followed by `**Author:** Asif Hussain \| © 2025–2026 CORTEX Framework. All rights reserved.` + optional `🧭 Orchestration: {DisplayName}` breadcrumb in Zone 3 — detect with `grep -n "Author.*Asif" .github/prompts/cortex-architect.prompt.md`; must NOT contain `**Orchestrator:**` field (P1 if present); must NOT use a mode-specific icon in the H1 heading (P1); must NOT use `**Via:**` label (P1 — renamed to `🧭 Orchestration:` in Phase 120) |
| 13 | MCP tool name alignment | All tool names referenced in agent/prompt files match registered IDs from `cortex/mcp/mcp_registry.py`; detect operation-based consolidation drift where old tool names survive in docs after registry consolidation (e.g., `cortex_sample_tool`, `cortex_validate_compliance`, `cortex_load_core_rules`, `cortex_query_governance`) |
| 14 | Governance rule count alignment | Agents referencing CORE rule counts must match `skull-rules.yaml` canonical count: 38 CORE + 2 AC (40 total) — detect "22 rules" or "35 rules" without AC qualifier as drift |
| 15 | Knowledge YAML wiring | Verify `cortex-registry/knowledge/` domain YAMLs (`architecture/`, `backend-python/`, `security/`, `testing-validation/`, `devops-infrastructure/`, `performance-optimization/`) are referenced and loadable by `KnowledgeSynthesisEngine` at `cortex/intelligence/knowledge/knowledge_synthesis_engine.py` |
| 16 | LENS synthesis health | Verify 8 LENS analyzers importable from `cortex/lens/` and golden tests in `tests/golden/` passing — run `python3 -c "from cortex.lens import *"` |
| 17 | Success/failure pattern learning | Verify `.cortex-runtime/traces/orchestrator-traces.db` captures AC markers per orchestrator invocation; audit sessions queryable for regression pattern detection — orphaned `AC_START` without `AC_COMPLETE` is a P0 violation |
| 18 | Upgrade manifest health | `.cortex-runtime/traces/upgrade-manifest.json` must exist and last entry must have `audit_result: pass`; `protected_paths` key must be present in the last upgrade entry (absence indicates exclusion guard was not applied, P1); missing file or last result `fail` → P1 warning — run `python3 -c "import json,os; d=json.load(open('.cortex-runtime/traces/upgrade-manifest.json')); ups=d.get('upgrades',[]); last=ups[-1] if ups else {}; print('OK' if last.get('audit_result')=='pass' and 'protected_paths' in last else 'FAIL')"` |
| 19 | DoR paragraph enforcement | No `\| Field \|` or `\| Handler \|` table patterns inside DoR/intent reflection sections in any agent file — DoR must be a numbered paragraph list with confidence indicator and proceed gate; table in DoR context is a P1 violation — run `grep -n "| Field \|| Handler |" .github/agents/core/*.md` |
| 20 | Windows compatibility gate | (a) No new hardcoded `/`-separator string paths added to `cortex/` source without `pathlib.Path` or `os.path`; (b) No new `os.system()` shell calls without platform guard; (c) `scripts/setup-mcp.py` uses `sys.executable` for MCP command; (d) `tasks.json` has both Unix and Windows-compatible task variants — run `grep -c "Windows" .vscode/tasks.json` (must be ≥ 1); any violation is P1 |
| 21 | Cross-platform runtime safety | After every `/audit fix`, verify: (a) no new hardcoded POSIX paths in `cortex/` source; (b) no new `os.system()` calls without Windows fallback; (c) `cortex/mcp/__main__.py` startup has no Unix-only assumptions (`os.getenv('HOME')` without `USERPROFILE` fallback, `Path('~')` without `.expanduser()`); (d) `pytest-xdist` multiprocessing start method compatible with Windows `spawn` strategy; any violation is P1 |
| 22 | Requirements file integrity | After every `/audit fix`, verify: (a) `requirements.txt` has no duplicate package entries (auto-detectable via line scan — `grep -c "jsonschema==" requirements.txt` must return 1); (b) no package appears with both pinned (`==`) and minimum (`>=`) constraints; (c) `[PREFLIGHT CRITICAL]` marker comment blocks are preserved and accurate — new preflight-critical dependencies must carry annotation; any violation is P1 |
| 23 | **SQLite activity log health** | `orchestrator-traces.db` passes `PRAGMA integrity_check` (result = `ok`); no orphaned AC_START rows (workflow_cycles or audit_stage_log rows with `status != "pass"` and `started_at < now - 1 hour`); file size < 50 MB; `audit_sessions` has ≥1 row with `exit_status = "clean"` in last 7 days; cleanup policy (`VACUUM`) ran on last session exit. **Severity mapping:** Missing DB file = P1 (logging pipeline uninitialised). Orphaned AC_START > 1 hour = P0 (broken cross-cutting intelligence). DB size > 50 MB = P1 (bloat). No clean session in 7 days = P1 (audit pipeline not running). **Auto-fix:** invoke `sqlite-health-sweep` instantiation of `detect-fix-rescan-loop` primitive (prune + VACUUM loop). **Detect command:** `python3 -c "import sqlite3,os; db='.cortex-runtime/traces/orchestrator-traces.db'; print('MISSING' if not os.path.exists(db) else sqlite3.connect(db).execute('PRAGMA integrity_check').fetchone()[0])"` |
| 24 | **Test fixture singleton DB isolation** | All pytest fixtures that set `CORTEX_TRACE_DB` env var **and** call `_instance = None` must also save and restore `OrchestratorTraceLogger.TRACE_DB_PATH`, `TRACE_ENABLED`, `MAX_ROWS_PER_TABLE` class attributes in teardown. Class-level attributes are evaluated at import time and are not re-read on singleton reset — failing to restore them causes the re-initialised singleton to open the production DB, leaking test rows. **Detect:** `python3 -c "import pathlib; [print('MISSING_CLASS_ATTR_RESTORE: '+str(f)) for f in pathlib.Path('tests/').rglob('*.py') if 'CORTEX_TRACE_DB' in (s:=f.read_text()) and '_instance = None' in s and 'TRACE_DB_PATH' not in s]"` — any output = P1. **Auto-fix:** apply `temp_trace_db` canonical pattern from `tests/unit/infrastructure/test_orchestrator_trace_logger.py` (commit `094aae9d8`). **Verify:** `python3 -m pytest tests/unit/infrastructure/test_orchestrator_trace_logger.py -p no:xdist` — must be 16/16 GREEN. **Severity:** P1 — root cause of production DB contamination with synthetic test rows. |
| 25 | **Production trace DB sentinel row cleanliness** | `orchestrator-traces.db` must contain zero rows with `action IN ('TEST_ACTION','ACTION_0','ACTION_1','ACTION_2')` across all 5 trace tables (`trace_master`, `trace_enforcement`, `trace_tdd`, `trace_interaction`, `trace_refactoringorchestrator`). These action names are reserved exclusively for test use — any presence in the production DB proves test fixture isolation failure (see Check #24). **Detect:** `python3 -c "import sqlite3; db=sqlite3.connect('.cortex-runtime/traces/orchestrator-traces.db'); total=sum(db.execute('SELECT count(*) FROM '+t+' WHERE action IN (\"TEST_ACTION\",\"ACTION_0\",\"ACTION_1\",\"ACTION_2\")').fetchone()[0] for t in ['trace_master','trace_enforcement','trace_tdd','trace_interaction','trace_refactoringorchestrator']); print('SENTINEL_ROWS='+str(total))"` — any count > 0 = P1. **Auto-fix:** `DELETE FROM {table} WHERE action IN ('TEST_ACTION','ACTION_0','ACTION_1','ACTION_2');` across all trace tables, then `VACUUM`. **Severity:** P1 — contaminates activity log analytics and obscures real operational signals. |
| 26 | **copilot-instructions.md header mandate** | `copilot-instructions.md` MUST contain the P0 RESPONSE HEADER section with `🧠 Session Identity` mandate and `🧭 Routing Breadcrumb` visual cue section — these drive the LLM to always emit the Author header on first response. **Detect:** `grep -n "RESPONSE HEADER — MANDATORY\|Routing Breadcrumb\|Author.*Asif.*©.*CORTEX" .github/copilot-instructions.md` — must return ≥3 matches; absence = P0 (header never emitted without this). **Detect stale Orchestrator field:** `grep -n "Orchestrator.*OrchestratorName\|Orchestrator.*✅" .github/copilot-instructions.md` — must return 0 matches; any match = P1. **Auto-fix:** Restore the `🧠 RESPONSE HEADER — MANDATORY` section and `🧭 ORCHESTRATOR ENGAGEMENT VISUAL CUE` section from SSOT: `.github/templates/cortex-response-templates.md` § Response Header — Canonical Spec. |
| 27 | **Intelligence layer health (Phase 107)** | `IntelligenceFacade` at `cortex/intelligence/facade.py` must be importable and expose `analyze()`, `synthesize()`, `query()`. `cortex.intelligence.models` package must export `BaseIntelligenceEngine`, `UnifiedIntelligenceContext`, `SynthesisResult`. No competing `IntelligenceFacade` class in `cortex/intelligence/lens/`. **Detect:** `python3 -c "from cortex.intelligence.facade import IntelligenceFacade; f=IntelligenceFacade(); assert all(hasattr(f,m) for m in ['analyze','synthesize','query']); from cortex.intelligence.models import BaseIntelligenceEngine, UnifiedIntelligenceContext, SynthesisResult; print('OK')"` — any ImportError or AttributeError = P0. **Detect duplicate:** `python3 -c "import subprocess,sys; r=subprocess.run(['grep','-rn','class IntelligenceFacade','cortex/intelligence/lens/'],capture_output=True,text=True); print('DUPLICATE' if r.stdout.strip() else 'OK')"` — `DUPLICATE` = P1. **Severity:** P0 (import failure blocks all intelligence operations). |
| 28 | **No Versioning Anywhere — governance artifacts** | No version fields (`version:`, `v1`, `v2`, semver, release tags) in `.github/agents/`, `.github/prompts/`, `cortex-registry/` YAML/MD files. **Detect:** `grep -rn "\"version\":\|version:\s\|release:\s\|\bv1\b\|\bv2\b" cortex-registry/ .github/ --include="*.yaml" --include="*.md" \| grep -v "Python 3\|pytest\|tree-sitter\|requirements\|__version__\|>=\|==\|#.*intentional"` — must return `0` lines. Any match = P0 (build-blocking). **Auto-fix:** Remove version field; add `CORE-NO-VERSION` note inline. **Drift lock:** `cortex-registry/governance/drift-locks/check-34-no-versioning-lock.yaml` |
| 29 | **Non-production prompt/agent scope markers** | Every `.github/prompts/*.prompt.md` and `.github/agents/**/*.md` EXCEPT core production files (`CORTEX.prompt.md`, `cortex-architect.prompt.md`, `CORTEX.md`, `cortex-executor.md`, `cortex-architect.md`, `copilot-instructions.md`) MUST contain `scope: non-production-admin` in YAML frontmatter. **Detect:** `python3 -c "import pathlib,re; bad=[str(f) for f in pathlib.Path('.github').rglob('*.md') if 'non-production-admin' not in f.read_text() and f.name not in ['CORTEX.md','cortex-executor.md','cortex-architect.md','copilot-instructions.md']]; [print(b) for b in bad]; print('COUNT='+str(len(bad)))"` — must return `COUNT=0`. **Auto-fix:** Inject `scope: non-production-admin` in YAML frontmatter block. **Drift lock:** `cortex-registry/governance/drift-locks/check-39-sync-marker-lock.yaml` |

---

## Detection Commands

```bash
# Check for deleted construct references
grep -r "cortex_intelligence\|cortex/brain\|cortex_lens\|_archive" .github/

# Check for stale MCP tool names
grep -r "cortex_process_request\|cortex_lens_analyze\|cortex_manage_todo" .github/

# Check for Phase 49/CCL references
grep -r "Phase 49\|CCL\|CrystallizedContext" .github/

# Check for wrong orchestrator counts
grep -r "24 orchestrators\|28 MCP\|120 orchestrators\|44 orchestrators" .github/

# Check for DEPRECATED files
ls .github/agents/core/DEPRECATED* .github/agents/core/deprecated* 2>/dev/null

# Check agent-index.md lists valid files
# Compare agent-index.md entries vs actual files in .github/agents/core/

# Check #11/#12 — response header SSOT drift (must return at least 1 match per file)
# Must contain Author + copyright, must NOT contain **Orchestrator:** {Name}
grep -n "Author.*Asif" .github/prompts/CORTEX.prompt.md
grep -n "Author.*Asif" .github/prompts/cortex-architect.prompt.md
grep -n "Orchestrator.*OrchestratorName\|Orchestrator.*✅" .github/prompts/*.prompt.md

# Check #26 — copilot-instructions.md header mandate (must return ≥3 matches)
grep -n "RESPONSE HEADER — MANDATORY\|Routing Breadcrumb\|Author.*Asif.*©.*CORTEX" .github/copilot-instructions.md
```

---

## Canonical Reference Values

**Authority:** File system source of truth (derived via grep, not manual claims)  
**Last Verified:** 2026-02-26 (Total Recall execution)

All `.github/` documentation MUST use these values:

| Metric | Canonical Value | Derivation Command |
|--------|-----------------|-------------------|
| **Wired Orchestrators** | 51 unique | `{ grep '  - name:' cortex-registry/core/specifications/*-wiring.yaml; } \| grep -v 'governance_registry\|audit_logger\|state_manager' \| sort -u \| wc -l` |
| **MCP Tools** | 36 registered; 58 tool files | `python3 -c "from cortex.mcp.mcp_registry import PRODUCTION_TOOLS; print(len(PRODUCTION_TOOLS))"` |
| **CORE Rules** | 60 (core:26 + governance:34) | `find cortex-registry/core cortex-registry/governance -name '*.yaml' \| wc -l` |
| **Top-level Dirs** | 21 dirs | `ls -d cortex/*/ \| grep -v __pycache__ \| wc -l` |
| **Orchestrator Subdirs** | 14 subdirs | `ls -d cortex/orchestrators/*/ \| grep -v __pycache__ \| wc -l` |
| **Package Name** | `cortex` (single) | No alternatives allowed |
| **Test Count** | ~20,565 collected | `python3 -m pytest tests/ --collect-only -q \| tail -1` |

**Numeric Drift Detection Protocol:**
1. Extract all numeric claims from docs: `grep -rn '{pattern}' .github/ --include="*.md"`
2. Run derivation command to get actual value from file system
3. Compare claimed vs actual → any mismatch is P0 drift
4. Fix docs inline (no new versions) → update to canonical value
5. Commit with message: `fix(docs): align {metric} with file system truth`

**Version Drift Detection (CORE-035):**
```bash
# Detect any version > 1.0 (excluding 3rd-party deps)
grep -rn 'version.*[2-9]\.\|version.*"2\.\|v2\.\|_v2\|schema.*2\.' \
  cortex-registry/ .github/ cortex/ --include="*.yaml" --include="*.py" --include="*.md" | \
  grep -v 'python-version\|pytest\|pip\|CDN\|OWASP\|>=\|<=' | \
  grep -v '__pycache__\|completed/'
```

Expected: **0 matches**. Any match is a CORE-035 violation (forked implementation, not in-place update).

---

## Automated Truth Establishment (Total Recall Protocol)

**Purpose:** Derive all canonical values programmatically from file system, never from manual claims.

**Truth Table Generation:**

```bash
#!/bin/bash
# Generate canonical truth table for all metrics

echo "=== CORTEX CANONICAL METRICS (File System Truth) ==="
echo ""

echo "1. Wired Orchestrators:"
{ grep '  - name:' cortex-registry/core/specifications/core-orchestrator-wiring.yaml; \
  grep '  - name:' cortex-registry/core/specifications/domain-orchestrator-wiring.yaml; \
  grep '  - name:' cortex-registry/core/specifications/support-orchestrator-wiring.yaml; \
  grep '  - name:' cortex-registry/core/specifications/git-orchestrator-wiring.yaml; } | \
grep -v 'core_orchestrators\|governance_registry\|audit_logger\|state_manager\|documentation_system\|business_knowledge' | \
sort -u | wc -l

echo "2. MCP Tools:"
grep -rn 'class Cortex.*Tool\|class Cortex.*ConsolidatedTool' cortex/mcp/tools/ --include="*.py" | \
grep -v '__pycache__\|Base\|Category\|Parameter' | wc -l

echo "3. CORE Rules:"
echo "   CORE-xxx: $(grep -c 'rule_id: CORE-' cortex-registry/core/tier0-skull/skull-rules.yaml)"
echo "   AC-xxx:   $(grep -c 'rule_id: AC-' cortex-registry/core/tier0-skull/skull-rules.yaml)"
echo "   Total:    $(grep -c 'rule_id:' cortex-registry/core/tier0-skull/skull-rules.yaml)"

echo "4. Top-level Dirs:"
ls -d cortex/*/ | grep -v __pycache__ | wc -l

echo "5. Orchestrator Subdirs:"
ls -d cortex/orchestrators/*/ | grep -v __pycache__ | wc -l

echo "6. Test Count:"
python3 -m pytest tests/ --collect-only -q 2>/dev/null | tail -1 || echo "Run pytest to get count"

echo ""
echo "=== DRIFT DETECTION ==="
echo "Claimed '27 wired' locations: $(grep -rn '27 wired' .github/ --include='*.md' | grep -v 'DRIFT DETECTION' | wc -l)"
echo "Claimed '26 MCP' locations:   $(grep -rn '26 MCP' .github/ --include='*.md' | grep -v 'DRIFT DETECTION' | wc -l)"
echo "Claimed '35 CORE' locations:  $(grep -rn '35 CORE' .github/ --include='*.md' | grep -v 'DRIFT DETECTION' | wc -l)"
echo ""
echo "Expected: 0 matches for stale claims (canonical: 51 wired, 29 registered MCP (39 target), 38 CORE)"
```

**Three-Way Conflict Resolution:**

When metadata, docs, and actual code disagree (example from chat01.md):

| Source | Value | Authority |
|--------|-------|-----------|
| `skull-rules.yaml` metadata | `rule_count: 36` | ❌ Stale |
| All `.github/` docs | "38 CORE rules" | ✅ Canonical |
| Actual `grep -c 'rule_id: CORE-'` | 38 | ✅ Canonical |

**Resolution:** Update metadata + all docs to match actual (38).

---

| Metric | Canonical Value |
|--------|----------------|
| Orchestrators | **296 files** across 14 domains |
| MCP Tools | **36 registered**; 58 tool files |
| CORE Rules | **60 active** (core:26 + governance:34) |
| Package | **`cortex`** (single) |
| Tests | **~20,565 collected** (run `python3 -m pytest --collect-only -q` for current count) |
| Audit Checks | **28-Point** production readiness (Checks #1–#28) |
| Meta-Audit Checks | **25 checks** |
| Workflow Primitive | `primitives/validation/detect-fix-rescan-loop` |
| SQLite DB | `.cortex-runtime/traces/orchestrator-traces.db` |
| SQLite Tables | `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs` |

---

## Output Format

```markdown
### 🔍 Meta-Audit Report

**Scope:** .github/ documentation
**Stale References Found:** {n}

#### P0 — Deleted Constructs Still Referenced
| File | Reference | Fix |
|------|-----------|-----|
| {file} | `cortex/brain/` | Remove reference |

#### P1 — Wrong Counts / Versions
| File | Current | Should Be |
|------|---------|-----------|
| {file} | "52 orchestrators" | "51 wired orchestrators" |

#### P2 — Template Duplicates
| File | Issue |
|------|-------|
| {file} | Duplicates SSOT in cortex-response-templates.md |

**Meta-Audit Clean:** ✅ Yes / ❌ No
```

---

## Governance Coherence Rules

| Rule | Requirement |
|------|-------------|
| CORE-002 | No generated .md report files |
| CORE-035 | Single SSOT for each concept |
| CORE-028 | snake_case for all file names |

**SSOT Locations:**
- Response templates → `cortex-response-templates.md`
- Agent registry → `agent-index.md`
- CORE rules → `cortex-registry/core/`
- Orchestrator wiring → `cortex-registry/` YAML files

---

## ⛔ Constructs That Must Not Appear in `.github/`

```
cortex/brain/
cortex_intelligence/
cortex_lens/
_archive/
Phase 49
CCL (Context Crystallization Layer)
CrystallizedContext
cortex_process_request
cortex_lens_analyze
cortex_manage_todo
cortex_digest_session
cortex_verify_environment (as primary MCP tool)
cortex_git_history (as primary MCP tool)
cortex_sample_tool (replaced by cortex_verify op=mcp)
cortex_validate_compliance (replaced by cortex_validate op=compliance)
cortex_load_core_rules (replaced by cortex_load op=rules)
cortex_query_governance (replaced by cortex_governance op=query)
cortex_check_dependency_drift (replaced by cortex_check op=dependencies)
cortex_capture_metrics (replaced by cortex_metrics op=capture)
cortex_onboard_repository_v3 (removed Phase 121 — use cortex_onboard_repository)
cortex_audit_remediation_plan (replaced by cortex_governance op=remediation_plan)
"24 orchestrators" / "28 MCP tools" / "120 orchestrators"
"25 tools" / "25 MCP tools" / "24 MCP tools" / "26 MCP tools" / "39 MCP tools" (all stale — canonical is 29 registered MCP tools, 39 target)
"22 rules" / "35 CORE rules" (must say "38 CORE rules" or "38 active")
```

---

## 📝 Learning Protocol (PLIP-001 — Automatic)

**SSOT:** `cortex-registry/core/prompt-learning-protocol.yaml`
**🔒 Scope Lock — `meta-audit`:** This agent learns ONLY from `meta-audit` and `drift` patterns. MUST NOT query or emit: `html-design`, `doc-sync`, `database`, `sync`, `training`, `design-system`, `a11y`.

- Before meta-audit: call `cortex_learning op=history pattern_id=meta-audit` — surface recurring meta-audit failure patterns
- If same drift pattern recurs across 3+ sessions: escalate to P1 systemic prompt issue
- After meta-audit fixes applied: call `cortex_learning op=emit signal_type=MILD_REWARD pattern_id=meta-audit`
- After meta-audit regressions introduced: call `cortex_learning op=emit signal_type=MILD_PUNISHMENT pattern_id=meta-audit`

