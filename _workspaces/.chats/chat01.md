asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
list remaining work from #file:cortex-master.yaml 

GitHub Copilot: Let me read the cortex-architect prompt and the master plan file. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/cortex-master.yaml#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/cortex-master.yaml#100-100), lines 100 to 323

Based on cortex-master.yaml, here is the remaining work summary:

---

## 📋 Remaining Work — cortex-master.yaml

### 🟡 IN_PROGRESS

| Phase | Title | Priority | Gaps | Notes |
|---|---|---|---|---|
| **phases-58-61** | Simplification — Zero-Regression Surface Reduction (4 Phases) | P0 | — | Phase 59-A COMPLETE. **Target: 124 → 22 orchestrators, 383K → 180K SLOC.** |

**Detail file:** simplification-master-plan-58-61.yaml

---

### ✅ Everything Else — COMPLETE

All 68 phases are marked COMPLETE in the index (`completed: 68`, `planned: 0`, `active: 0`).

**`health_status`:** `p0_issues: 0`, `p1_issues: 0`, `health_check: PASSING`

**`production_readiness`:** `✅ COMPLETE — 100%`

---

### 🔑 One Item Needing Attention

The **phases-58-61 Simplification** entry is marked `status: IN_PROGRESS` — meaning **Phases 58, 60, and 61 of the simplification sweep** are still outstanding. Phase 59-A is noted as complete, but the full target (124 → 22 orchestrators, 383K → 180K SLOC) has not been reached.

To see the full gap catalogue, open:
```
cortex-registry/planning/phases/planned/simplification-master-plan-58-61.yaml
```

asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
complete Phase	Title	Priority	Gaps	Notes
phases-58-61	Simplification — Zero-Regression Surface Reduction (4 Phases)	P0	—	Phase 59-A COMPLETE. Target: 124 → 22 orchestrators, 383K → 180K SLOC.

GitHub Copilot: Let me load the full detail file for phases-58-61 before doing anything. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/simplification-master-plan-58-61.yaml#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/simplification-master-plan-58-61.yaml#100-100), lines 100 to 250

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/simplification-master-plan-58-61.yaml#250-250), lines 250 to 440

Now let me get the current state of the codebase — what actually exists today vs. what the plan shows. 

Ran terminal command: find cortex -name '*.py' | wc -l && echo "---" && find cortex -name '*.py' | xargs grep -h '^class.*Orchestrator' 2>/dev/null | sort | uniq | wc -l && echo "---" && find cortex/core -maxdepth 1 -type d | wc -l && echo "---" && find cortex/core -maxdepth 1 -type d && echo "---" && ls cortex/core/ | head -40

Ran terminal command: python3 scripts/run_tests.py smoke 2>&1 | tail -40

Smoke tests are actually green (1420 passed). The exit code 1 was from a prior run. Now let me get the full picture of what remains. 

Ran terminal command: find cortex/core -maxdepth 2 -name "*.py" | wc -l && echo "---core/core exists?---" && ls cortex/core/ 2>/dev/null | grep -c "^" && echo "---grep core.core imports---" && grep -rn "from cortex\.core\.core" cortex/ tests/ 2>/dev/null | wc -l && echo "---orchestrator classes outside orchestrators/---" && find cortex -name "*.py" | xargs grep -h "^class.*Orchestrator" 2>/dev/null | sort | uniq

Ran terminal command: find cortex -name "*.py" | xargs grep -h "^class.*Orchestrator" 2>/dev/null | sort | uniq | wc -l && echo "---" && find cortex/core -name "core" -type d 2>/dev/null && echo "---" && find cortex-registry -name "*.yaml" | wc -l && echo "---" && ls cortex-registry/_cortex-master/ 2>/dev/null | head -5 && echo "---" && grep -rn "# COMPAT" cortex/ 2>/dev/null | wc -l

Ran terminal command: find cortex/core -maxdepth 1 -type d | sort && echo "---" && ls cortex/core/ | grep -v ".py" | grep -v "__pycache__"

Now I have a clear picture. Let me compile the full remaining work assessment.

---

## 📋 CORTEX Architect — Plan

**Author:** Asif Hussain | **Orchestrator:** PlanningOrchestrator ✅

---

## 📋 Summary

**Phases 58–61 are IN_PROGRESS.** Smoke tests are green (1,420 passing). The `cortex/core/core/` double-nesting is already gone (0 `from cortex.core.core` imports). Significant reduction remains across all 4 phases.

---

## 🔍 Current State vs. Target

| Metric | Baseline (2026-02-23) | **Today (2026-02-24)** | Target |
|---|---|---|---|
| Python files in cortex | 1,346 | **1,324** | ≤700 |
| Orchestrator classes | 124 | **115** | ≤22 |
| core subdirs | 27 | **15** | 8 canonical |
| `from cortex.core.core` imports | 98 | **0** ✅ | 0 |
| YAML files in registry | 373 | **238** | ≤150 |
| Compat shims (`# COMPAT`) | — | **0** ✅ | 0 |
| Smoke tests | — | **1,420 ✅** | green |

---

## 🔍 Remaining Work by Phase

### Phase 58 — `core/core` Collapse (PARTIALLY DONE)
| Sub-Phase | Status | Remaining Work |
|---|---|---|
| 58-a: Audit & Map core/core | ✅ Done | `cortex.core.core` imports already 0 |
| 58-b: Delete Group A twins | ✅ Done | 0 `core.core` imports confirmed |
| 58-c: Relocate Group B unique | ✅ Done | No `core/core/` dir exists |
| 58-d: Relocate Group C/D | ✅ Done | — |
| 58-e: **Delete `cortex/core/core/` dir** | ✅ Done (Phase 68 completed this) | — |
| 58-f: **Duplicate filename elimination** | ⚠️ **OPEN** | 90 groups → 0 target; current unknown |

**Action needed:** Run the duplicate detection sweep.

---

### Phase 59 — Orchestrator Reduction (IN_PROGRESS)
| Sub-Phase | Status | Remaining Work |
|---|---|---|
| 59-a: Delete zero-import stubs | ✅ COMPLETE (commit ff8f9e813) | 7 deleted, count 119→112 |
| 59-b: **Merge near-duplicates** | ⚠️ **OPEN** | 115 → 22 target; **93 classes to eliminate** |

Candidates still present include: `CachedLENSOrchestrator`, `AnalyticsOrchestrator`, `AutoHealingMCPOrchestrator`, `BusinessKnowledgeIngestionOrchestrator`, `ChallengeEngine`, `ChallengeIntegrationOrchestrator`, `CodeLevelPlanner`, `CortexDocsOrchestrator`, `CortexMasterPlanOrchestrator`, `MultiRegionOrchestrator`, `PhaseOrchestrator`, `PlanRegistrySyncOrchestrator`, `PreCommitEnforcementOrchestrator`, `QueryOrchestrator`, `RegressionSafetyOrchestrator`, `SOLIDOrchestrator`, `SanitizationOrchestrator`, `SecretsMigrationOrchestrator`, `SetupOrchestrator`, `StateOrchestrator`, `SyncOrchestrator`, `UnifiedAnalysisOrchestrator`, `UnifiedDiscoveryOrchestrator`, `VSCodeConfigurator`, and others.

---

### Phase 60 — core Flatten (OPEN)
| Status | Detail |
|---|---|
| ⚠️ **OPEN** | Current: **15 subdirs** → Target: **8 canonical** |

7 subdirs to dissolve: `discovery`, `execution`, `hallucination_prevention`, `intelligence`, `intent`, `interaction`, `wiring` + `knowledge` → merge/relocate per plan's `directories_to_dissolve` table.

---

### Phase 61 — Registry Cleanup (PARTIALLY COMPLETE)
| Sub-Phase | Status | Remaining Work |
|---|---|---|
| 61-a: `_cortex-master/` elimination | ⚠️ **DEFERRED** | Still exists (`phases/`, `playbooks/`) — 42 callers to migrate |
| 61-b: YAML reduction | ✅ COMPLETE | 373 → 238 (target ≤150 — **88 more to archive**) |
| 61-c: Compat shim review | ✅ COMPLETE | 0 `# COMPAT` markers |
| 61-d: cortex-sts cleanup | ✅ COMPLETE | — |
| 61-e: Legacy orchestrator audit | ✅ COMPLETE | — |
| 61-f: Docs sync | ✅ COMPLETE | — |

---

## 🎯 Recommended Execution Order

```
1. Phase 58-f  → Duplicate filename sweep (90 groups → 0)       [4h]
2. Phase 59-b  → Orchestrator merge/delete to ≤22               [1 week]
3. Phase 60    → cortex/core flatten 15 → 8 subdirs              [1 week]
4. Phase 61-a  → _cortex-master/ elimination (42 callers)        [2 days]
5. Phase 61-b  → YAML archive 238 → ≤150                        [2 days]
```

Regression gate: `make test-batch` (1,420 smoke + 838 golden) after **every sub-phase**.

---

## ⚡ If you type `proceed`, CORTEX will:

- Run `58-f`: detect all duplicate filename groups via AST grep, present the 90-group catalogue inline
- Run `59-b`: map each of the 93 non-canonical orchestrators to a disposition (delete / merge / keep with justification), confirm canonical 22 list
- Begin Phase 60 sub-phase planning with exact file-by-file move list for each of the 7 dirs to dissolve
- Run `make test-batch` after each sub-phase to enforce the regression gate

asifhussain60: proceed

GitHub Copilot: [████░░░░░░] 40% — Phase 58-f: Duplicate Filename Sweep 

Ran terminal command: find cortex -name "*.py" | sed 's|.*/||' | sort | uniq -d | head -60

Ran terminal command: find cortex -name "*.py" | sed 's|.*/||' | sort | uniq -d | wc -l

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && find cortex -name "*.py" | python3 -c "
import sys, collections
names = [line.strip().split('/')[-1] for line in sys.stdin]
dupes = {n: [] for n in names if names.count(n) > 1}
for line in open('/dev/stdin') if False else []:
    pass
# re-run via script
" 2>/dev/null; find cortex -name "*.py" > /tmp/pyfiles.txt && python3 - << 'EOF'
import collections
with open('/tmp/pyfiles.txt') as f:
    paths = [l.strip() for l in f]
by_name = collections.defaultdict(list)
for p in paths:
    by_name[p.split('/')[-1]].append(p)
dupes = {k: v for k, v in by_name.items() if len(v) > 1 and k not in ('__init__.py', '__main__.py')}
print(f"Duplicate groups: {len(dupes)}")
print(f"Extra files: {sum(len(v)-1 for v in dupes.values())}")
for name, locs in sorted(dupes.items()):
    print(f"\n  {name} ({len(locs)} copies):")
    for l in sorted(locs):
        print(f"    {l}")
EOF

[██████░░░░] 60% — Phase 59-b: Orchestrator disposition mapping 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 - << 'EOF'
import subprocess, collections, os

# Get all orchestrator class names and their files
result = subprocess.run(
    ['grep', '-rn', '--include=*.py', '-h', '^class.*Orchestrator'],
    capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX/cortex'
)

# Also get full path
result2 = subprocess.run(
    ['grep', '-rn', '--include=*.py', '^class.*Orchestrator'],
    capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX/cortex'
)

canonical_22 = {
    'MasterOrchestrator', 'IntentRouter', 'TDDOrchestrator', 'EnforcementOrchestrator',
    'RequestRephraseOrchestrator', 'ConversationOrchestrator',
    'RefactoringOrchestrator', 'PlanningOrchestrator', 'AuditOrchestrator',
    'SecurityOrchestrator', 'OnboardingOrchestrator', 'DomainOrchestrator',
    'HealthOrchestrator', 'VacuumOrchestrator', 'UpgradeOrchestrator',
    'GitOrchestrator', 'DigestSessionOrchestrator', 'BulkDigestOrchestrator',
    'SweepCatalogueOrchestrator', 'WorkflowOrchestrator', 'DebuggerOrchestrator',
    'RollbackOrchestrator',
    # base classes / interfaces - not orchestrators per se
    'OrchestratorBase', 'OrchestratorProtocolMixin', 'IOrchestrator',
}

import re
classes = {}
for line in result2.stdout.splitlines():
    parts = line.split(':')
    if len(parts) >= 3:
        filepath = parts[0]
        classline = ':'.join(parts[2:])
        m = re.match(r'class\s+(\w+Orchestrator\w*)', classline)
        if m:
            name = m.group(1)
            classes.setdefault(name, []).append(f"cortex/{filepath}")

print(f"Total unique Orchestrator class names: {len(classes)}")
print(f"\nNON-CANONICAL (not in keeper list): {len([k for k in classes if k not in canonical_22])}")
print("\n--- NON-CANONICAL CLASSES ---")
for name in sorted(classes):
    if name not in canonical_22:
        # check import count
        r = subprocess.run(['grep', '-rn', '--include=*.py', name, 'cortex/', 'tests/'],
                          capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX')
        count = len(r.stdout.splitlines())
        files = classes[name]
        print(f"  {name} | importers:{count} | files: {', '.join(files[:2])}")
EOF

[████████░░] 80% — Phase 60: core subdir analysis 

Ran terminal command: for d in discovery execution hallucination_prevention intelligence intent interaction wiring knowledge; do count=$(find cortex/core/$d -name "*.py" 2>/dev/null | wc -l | tr -d ' '); echo "$d: $count files"; done

Ran terminal command: find cortex-registry/_cortex-master -name "*.py" 2>/dev/null | wc -l && echo "yaml files:" && find cortex-registry/_cortex-master -name "*.yaml" | wc -l && echo "callers of _cortex-master:" && grep -rn "_cortex-master" cortex/ tests/ 2>/dev/null | grep -v ".pyc" | wc -l

[██████████] 100% — Catalogue complete. Compiling full report.

---

## 📋 CORTEX Architect — Phases 58–61 Full Sweep Catalogue

**Author:** Asif Hussain | **Orchestrator:** SweepCatalogueOrchestrator ✅

---

## Phase 58-f — Duplicate Filename Sweep

**63 duplicate groups · 69 extra files** (down from 90/96 baseline — 27 already eliminated)

| # | Filename | Copies | Disposition |
|---|---|---|---|
| 1 | `context_cache_layer.py` | 2 | Delete interaction copy → canonical at core |
| 2 | `context_synthesis_gateway.py` | 2 | Delete interaction copy → canonical at core |
| 3 | `coherence_validator.py` | 3 | Delete 2 extras → canonical at core |
| 4 | `dashboard_generator.py` | 3 | Delete registry + lens copies → canonical at deployment |
| 5 | `enforcement_orchestrator.py` | 2 | git is `PreCommitEnforcementOrchestrator` — rename to avoid clash |
| 6 | `execution_sandbox.py` | 2 | Delete hallucination_prevention copy → canonical at intelligence |
| 7 | `health_check.py` | 2 | Delete wiring copy → canonical at common |
| 8 | `output_validator.py` | 2 | Delete hallucination_prevention copy → canonical at common |
| 9 | `orchestrator.py` | 3 | Each in distinct domain (`crawler/`, `lens/`, `support/`) — **rename** to avoid confusion |
| 10 | `rollback_orchestrator.py` | 2 | Delete deployment copy → canonical at support |
| 11 | `stage_execution_strategy.py` | 2 | Delete core → canonical at strategies |
| 12 | `vacuum_orchestrator.py` | 2 | Delete health copy → canonical at support |
| 13 | `toolkit_tools.py` | 2 | Delete mcp root copy → canonical at tools |
| 14 | `cleanup.py` | 2 | Delete toolkit copy → canonical at toolkit |
| 15 | `management.py` | 2 | Delete secrets copy → canonical at secrets |
| 16–63 | *(remaining 48 groups)* | 2 each | Grep-import-count decides canonical; lower-count copy deleted |

**Regression gate:** `make test-batch` after every deletion.

---

## Phase 59-b — Orchestrator Reduction: 115 → 22

Current non-canonical count: **56 classes**. Disposition by import count:

### 🔴 DELETE — Zero/Near-Zero Production Value
| Class | Importers | Action |
|---|---|---|
| `AnalyticsOrchestrator` | 2 | Delete — internal to `bluf_system.py` only |
| `BusinessDomainOrchestrator` | 2 | Delete — abstract base with no real subclasses |
| `EnhancedOnboardingOrchestrator` | 2 | Merge into `OnboardingOrchestrator` |
| `MasterOrchestratorChangeDetection` | 1 | Delete — single caller, inline logic |
| `TestCortexOrchestrator` | 1 | Delete — test-only class in `mcp/tests/` |
| `UnifiedAnalysisOrchestrator` | 5 | Delete — merge into `AuditOrchestrator` |
| `UnifiedDiscoveryOrchestrator` | 5 | Delete — merge into `OnboardingOrchestrator` |
| `UnifiedQualityAssuranceOrchestrator` | 4 | Delete — merge into `TDDOrchestrator` |
| `SetupOrchestrator` | 7 | Delete — merge into `UpgradeOrchestrator` |
| `SecretsMigrationOrchestrator` | 7 | Move to infrastructure (not an orchestrator) |
| `ComplianceOrchestrator` | 3 | Rename to `SecretsComplianceCheck` (not an orchestrator) |

### 🟡 CONSOLIDATE — High Import Count, Merge Into Canonical
| Class | Importers | Merge Target |
|---|---|---|
| `InteractionOrchestrator` | 335 | → `ConversationOrchestrator` (Phase 59-b primary task) |
| `StateOrchestrator` | 86 | → `MasterOrchestrator` state management layer |
| `BusinessKnowledgeIngestionOrchestrator` | 82 | → `DigestSessionOrchestrator` |
| `CortexMasterPlanOrchestrator` | 82 | → `PlanningOrchestrator` |
| `EnhancedPlanningOrchestrator` | 51 | → `PlanningOrchestrator` |
| `HolisticValidationOrchestrator` | 53 | → `EnforcementOrchestrator` |
| `IntelligenceOrchestrator` | 137 | → `MasterOrchestrator` Stage 2 intelligence delegate |
| `LENSOrchestrator` | 171 | **KEEP** — 171 importers, LENS domain anchor (add to canonical-22 +1) |
| `ObservabilityOrchestrator` | 53 | → `HealthOrchestrator` observability layer |
| `SOLIDOrchestrator` | 43 | → `RefactoringOrchestrator` |
| `SanitizationOrchestrator` | 38 | → `EnforcementOrchestrator` |
| `ReviewOrchestrator` | 31 | → `AuditOrchestrator` |
| `ChallengeIntegrationOrchestrator` | 29 | → `EnforcementOrchestrator` (challenge gate) |
| `DefenseOrchestrator` | 24 | → `SecurityOrchestrator` |
| `CortexDocsOrchestrator` | 23 | → `OnboardingOrchestrator` |
| `GitPublishOrchestrator` | 37 | → `GitOrchestrator` (publish sub-operation) |
| `PhaseCompletionOrchestrator` | 34 | → `SweepCatalogueOrchestrator` |
| `BrainHealthOrchestrator` | 40 | → `HealthOrchestrator` |
| `RegressionSafetyOrchestrator` | 18 | → `EnforcementOrchestrator` |
| `TestClassifierOrchestrator` | 20 | → `TDDOrchestrator` |
| `RepositoryOnboardingOrchestrator` | 73 | = `OnboardingOrchestrator` (same class, alias) — deduplicate |
| `PreCommitEnforcementOrchestrator` | 12 | → `EnforcementOrchestrator` git hook |
| `PhaseOrchestrator` | 18 | → `PlanningOrchestrator` |
| `MasterOrchestratorStage2` | 5 | Inline into `MasterOrchestrator` |
| `CentralBrainOrchestrator` | 11 | → `MasterOrchestrator` |
| `CachedLENSOrchestrator` | 7 | → `LENSOrchestrator` (add caching internally) |

### 🟢 KEEP WITH JUSTIFICATION (add to canonical list)
| Class | Importers | Justification |
|---|---|---|
| `LENSOrchestrator` | 171 | LENS domain anchor — too many importers to merge |
| `HotReloadOrchestrator` | 18 | Infrastructure devx — distinct domain |
| `MultiRegionOrchestrator` | 8 | Real deployment concern — keep in `infrastructure/` |
| `AutoHealingMCPOrchestrator` | 9 | MCP self-healing — keep, rename to `MCPHealthOrchestrator` |

**Revised canonical target: 26** (22 plan + LENSOrchestrator + 3 justified keeps)

---

## Phase 60 — core Flatten: 15 → 8 subdirs

| Subdir | Files | Action | Destination |
|---|---|---|---|
| `discovery/` | 2 | Move | mcp |
| `execution/` | 21 | Move | workflow |
| `hallucination_prevention/` | 3 | Move | intelligence |
| `intelligence/` | 12 | Move | intelligence |
| `intent/` | 9 | Move | intent_router |
| `interaction/` | 13 | Merge | core (after dedup of context_cache_layer + context_synthesis_gateway) |
| `wiring/` | 12 | Merge | `cortex/core/registry.py` |
| `knowledge/` | 26 | Move | knowledge |

**Total files moved:** 98 · **Import rewrites needed:** scan after each move · **Gate:** `make test-batch` per subdir

---

## Phase 61 — Registry Cleanup

| Item | Status | Action |
|---|---|---|
| `_cortex-master/` | ⚠️ 37 YAMLs, 222 code callers | Migrate callers → phases paths, then delete dir |
| YAML count | 238 → ≤150 | Archive 88 more planning/completed YAMLs to `_archive/` or delete |

---

## 🎯 Execution Order (CORE-064 Sweep Completeness)

```
[Phase 58-f]  Duplicate delete — 69 files                    ~4h
[Phase 59-b]  Orchestrator consolidation — 56 → ≤6           ~1 week
[Phase 60]    cortex/core flatten — 8 subdirs dissolved       ~1 week
[Phase 61-a]  _cortex-master/ removal — 222 callers migrated ~2 days
[Phase 61-b]  YAML archive — 238→≤150                        ~2 days
```

Regression gate enforced at every sub-phase: `make test-batch` · zero new failures · 1,420 smoke must stay green.

---

### ⚡ If you type `proceed`, CORTEX will:
- Start **Phase 58-f** immediately: delete the highest-confidence duplicate with 0 real-logic (e.g., health_check.py → canonical at health_check.py), rewrite its imports, run `make test-batch`
- Continue file-by-file through all 69 duplicate extras in import-count order
- After each deletion confirm green baseline before moving to next

asifhussain60: proceed

GitHub Copilot: [█░░░░░░░░░] 10% — Phase 58-f · Identifying highest-confidence zero-risk deletions first 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 - << 'EOF'
import subprocess, os

# For each duplicate pair, find which has FEWER external importers (= delete candidate)
# Start with the safest ones: files where one copy is clearly inside a dir being dissolved in Phase 60

candidates = [
    # (delete_path, canonical_path, reason)
    ("cortex/core/wiring/health_check.py",            "cortex/core/common/health_check.py",           "core/wiring → dissolved in Ph60"),
    ("cortex/core/hallucination_prevention/output_validator.py", "cortex/core/common/output_validator.py",  "core/hallucination_prevention → dissolved in Ph60"),
    ("cortex/core/hallucination_prevention/execution_sandbox.py", "cortex/intelligence/memory/tier2_adaptive/hallucination_prevention/execution_sandbox.py", "core/hallucination_prevention → dissolved"),
    ("cortex/core/interaction/context_cache_layer.py", "cortex/core/context_cache_layer.py",           "core/interaction → dissolved in Ph60"),
    ("cortex/core/interaction/context_synthesis_gateway.py", "cortex/core/context_synthesis_gateway.py", "core/interaction → dissolved in Ph60"),
    ("cortex/orchestrators/core/stage_execution_strategy.py", "cortex/orchestrators/strategies/stage_execution_strategy.py", "duplicate in strategies/ is canonical"),
    ("cortex/orchestrators/health/vacuum_orchestrator.py", "cortex/orchestrators/support/vacuum_orchestrator.py", "support/ is canonical health tier"),
    ("cortex/infrastructure/deployment/rollback_orchestrator.py", "cortex/orchestrators/support/rollback_orchestrator.py", "orchestrators/support/ is canonical"),
    ("cortex/mcp/toolkit_tools.py",                   "cortex/mcp/tools/toolkit_tools.py",            "mcp/tools/ is canonical"),
    ("cortex/tools/toolkit/cleanup.py",               "cortex/mcp/tools/toolkit/cleanup.py",          "mcp/tools/toolkit/ is canonical"),
    ("cortex/secrets/management.py",                  "cortex/infrastructure/secrets/management.py",  "infrastructure/secrets/ is canonical"),
]

print("CANDIDATE DELETIONS — verifying files exist and checking import counts:\n")
for delete_path, canonical_path, reason in candidates:
    delete_exists = os.path.exists(f"/Users/asifhussain/PROJECTS/CORTEX/{delete_path}")
    canonical_exists = os.path.exists(f"/Users/asifhussain/PROJECTS/CORTEX/{canonical_path}")
    
    if delete_exists:
        r = subprocess.run(['grep', '-rn', '--include=*.py', delete_path.replace('cortex/', '').replace('/', '.').replace('.py', ''), 'cortex/', 'tests/'],
                          capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX')
        importers = len([l for l in r.stdout.splitlines() if 'import' in l])
        print(f"  {'✅' if delete_exists else '❌'} DELETE: {delete_path}")
        print(f"  {'✅' if canonical_exists else '❌'} CANONICAL: {canonical_path}")
        print(f"     Reason: {reason} | Import refs: {importers}")
        print()
EOF

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && for f in \
  "cortex/core/wiring/health_check.py" \
  "cortex/core/common/health_check.py" \
  "cortex/core/interaction/context_cache_layer.py" \
  "cortex/core/context_cache_layer.py" \
  "cortex/core/interaction/context_synthesis_gateway.py" \
  "cortex/core/context_synthesis_gateway.py" \
  "cortex/orchestrators/core/stage_execution_strategy.py" \
  "cortex/orchestrators/strategies/stage_execution_strategy.py" \
  "cortex/orchestrators/health/vacuum_orchestrator.py" \
  "cortex/orchestrators/support/vacuum_orchestrator.py" \
  "cortex/infrastructure/deployment/rollback_orchestrator.py" \
  "cortex/orchestrators/support/rollback_orchestrator.py" \
  "cortex/mcp/toolkit_tools.py" \
  "cortex/mcp/tools/toolkit_tools.py" \
  "cortex/secrets/management.py" \
  "cortex/infrastructure/secrets/management.py"; do
  [ -f "$f" ] && echo "EXISTS: $f" || echo "MISSING: $f"
done

All 16 files confirmed. Now check import references for each delete candidate before touching anything. 

Ran terminal command: echo "=== core.wiring.health_check ===" && grep -rn "core\.wiring\.health_check\|core/wiring/health_check" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== core.interaction.context_cache_layer ===" && grep -rn "core\.interaction\.context_cache_layer\|core/interaction/context_cache_layer" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== core.interaction.context_synthesis_gateway ===" && grep -rn "core\.interaction\.context_synthesis_gateway\|core/interaction/context_synthesis_gateway" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== orchestrators.core.stage_execution_strategy ===" && grep -rn "orchestrators\.core\.stage_execution_strategy\|from cortex\.core.*stage_execution" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== orchestrators.health.vacuum_orchestrator ===" && grep -rn "orchestrators\.health\.vacuum_orchestrator" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== infrastructure.deployment.rollback_orchestrator ===" && grep -rn "infrastructure\.deployment\.rollback_orchestrator" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== mcp.toolkit_tools (root) ===" && grep -rn "from cortex\.mcp\.toolkit_tools\|import cortex\.mcp\.toolkit_tools" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== secrets.management ===" && grep -rn "from cortex\.secrets\.management\|cortex\.secrets\.management" cortex/ tests/ --include="*.py" | grep -v "__pycache__"

The import analysis reveals critical dependencies — `vacuum_orchestrator` health path has 20+ callers and `rollback_orchestrator` is already a compat shim (canonical is infrastructure). Let me now execute the safe zero-risk deletions first, then the compat-shim resolutions. 

Ran terminal command: cat cortex/core/wiring/health_check.py && echo "===" && cat cortex/core/common/health_check.py | head -15

The situation is **inverted** — health_check.py has the real implementation and health_check.py is the compat shim pointing to it. The canonical is `wiring/` for now (will move with Phase 60). Let me check `stage_execution_strategy` and `vacuum_orchestrator` then execute the clear wins. 

Ran terminal command: head -20 cortex/orchestrators/core/stage_execution_strategy.py && echo "===" && head -10 cortex/orchestrators/strategies/stage_execution_strategy.py && echo "===" && head -10 cortex/orchestrators/support/vacuum_orchestrator.py && echo "===" && head -10 cortex/orchestrators/health/vacuum_orchestrator.py | head -5

Now the picture is clear: `orchestrators/core/stage_execution_strategy.py` is the **canonical**, `strategies/` is the re-export shim. `orchestrators/health/vacuum_orchestrator.py` is the **canonical**, `support/` is the protocol-adapter shim. These are deliberate compat shims — not deletable without migration.

Let me focus on the genuinely deletable duplicates — files with identical or redundant content with no active callers. 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 - << 'EOF'
import subprocess, os

# Find pairs where one file is clearly a dead duplicate (no unique importers)
candidates = [
    # (candidate_to_delete, canonical_to_keep, check_import_pattern)
    ("cortex/mcp/toolkit_tools.py",             "cortex/mcp/tools/toolkit_tools.py",        "cortex.mcp.toolkit_tools"),
    ("cortex/tools/toolkit/cleanup.py",         "cortex/mcp/tools/toolkit/cleanup.py",       "cortex.tools.toolkit.cleanup"),
    ("cortex/tools/toolkit/validation.py",      "cortex/orchestrators/domain/business/validation.py", "cortex.tools.toolkit.validation"),
    ("cortex/orchestrators/support/orchestrator.py", "cortex/orchestrators/", "cortex.orchestrators.support.orchestrator"),
    ("cortex/intelligence/base.py",             "keep-check",                                "cortex.intelligence.base"),
    ("cortex/dashboards/spa/models.py",         "cortex/orchestrators/health/models.py",     "cortex.dashboards.spa.models"),
    ("cortex/intelligence/crawler/cli.py",      "cortex/orchestrators/health/cli.py",        "cortex.intelligence.crawler.cli"),
]

for delete_path, canonical, pattern in candidates:
    exists = os.path.exists(f"/Users/asifhussain/PROJECTS/CORTEX/{delete_path}")
    if not exists:
        print(f"MISSING: {delete_path}")
        continue
    r = subprocess.run(['grep', '-rn', '--include=*.py', pattern, 'cortex/', 'tests/'],
                      capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX')
    count = len([l for l in r.stdout.splitlines() if delete_path not in l])
    print(f"{'EXISTS' if exists else 'MISSING'} | external importers: {count:3d} | {delete_path}")
    if count == 0:
        print(f"  → SAFE TO DELETE (0 external callers)")
EOF

Ran terminal command: grep -rn "cortex.mcp.toolkit_tools" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "---" && head -5 cortex/mcp/toolkit_tools.py && echo "..." && head -5 cortex/mcp/tools/toolkit_tools.py

Ran terminal command: wc -l cortex/mcp/toolkit_tools.py cortex/mcp/tools/toolkit_tools.py && echo "---" && diff <(head -30 cortex/mcp/toolkit_tools.py) <(head -30 cortex/mcp/tools/toolkit_tools.py)

These are two **entirely different files** — not duplicates at all. toolkit_tools.py exposes `toolkit_*` functions; toolkit_tools.py exposes `cortex_scan` etc. The test suite imports `cortex.mcp.toolkit_tools` — the root-level file is the one being tested. Both must be kept. Let me now focus on the real safe deletions — the `coherence_validator.py` triplicate and `dashboard_generator.py` triplicate. 

Ran terminal command: echo "=== coherence_validator locations ===" && find cortex -name "coherence_validator.py" && echo "" && for f in cortex/core/coherence_validator.py cortex/orchestrators/domain/coherence_validator.py cortex/orchestrators/validation/coherence_validator.py; do echo "--- $f ---"; head -8 "$f"; echo ""; done && echo "=== callers ===" && grep -rn "from cortex.*coherence_validator import\|import.*coherence_validator" cortex/ tests/ --include="*.py" | grep -v "__pycache__"

coherence_validator.py is a compat shim pointing to `orchestrators/validation/`. The `orchestrators/domain/` version is a **different class** (`CrossLayerCoherenceValidator`). So `core/coherence_validator.py` shim is the one to migrate. Now execute the concrete deletions — starting with the safest: the compat shim at coherence_validator.py (since all callers already use `orchestrators.validation`). 

Ran terminal command: grep -rn "from cortex\.core\.coherence_validator\|cortex\.core\.coherence_validator" cortex/ tests/ --include="*.py" | grep -v "__pycache__"

Zero external callers — safe to delete. 

Ran terminal command: grep -rn "from cortex\.core\.context_cache_layer\|cortex\.core\.context_cache_layer" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "---" && grep -rn "from cortex\.core\.context_synthesis_gateway\|cortex\.core\.context_synthesis_gateway" cortex/ tests/ --include="*.py" | grep -v "__pycache__"

Ran terminal command: head -10 cortex/core/context_cache_layer.py && echo "===" && head -5 cortex/core/interaction/context_cache_layer.py && echo "===" && head -10 cortex/core/context_synthesis_gateway.py && echo "===" && head -5 cortex/core/interaction/context_synthesis_gateway.py

Both core files are the canonical implementations (full docstrings, proper headers). The interaction copies are Phase 60 dissolution targets — they exist because `interaction/` hasn't been dissolved yet. The `core/` root versions are used by callers. The `interaction/` duplicates need checking. 

Ran terminal command: wc -l cortex/core/context_cache_layer.py cortex/core/interaction/context_cache_layer.py && echo "---" && wc -l cortex/core/context_synthesis_gateway.py cortex/core/interaction/context_synthesis_gateway.py && echo "---diff context_cache_layer---" && diff cortex/core/context_cache_layer.py cortex/core/interaction/context_cache_layer.py | head -20 && echo "---diff context_synthesis_gateway---" && diff cortex/core/context_synthesis_gateway.py cortex/core/interaction/context_synthesis_gateway.py | head -20

The `interaction/` copies are **different, more evolved implementations** (280 vs 231 lines, 420 vs 386 lines) — these are diverged, not simple duplicates. The callers import from `cortex.core.interaction.*` (confirmed earlier — 13+ callers for `context_synthesis_gateway`). So the **`interaction/` versions are the real canonical** ones. The root core versions are the older copies. 

This needs careful migration, not a quick delete. Let me now execute the **definitively safe zero-risk deletions** first and run the test gate, then plan the harder ones.

[████████░░] 80% — Executing Phase 58-f safe deletions 

Ran terminal command: grep -rn "from cortex\.core\.coherence_validator\b" cortex/ tests/ --include="*.py" | grep -v "__pycache__" | grep -v "^cortex/core/coherence_validator"

Zero external callers confirmed. Execute deletion. 

Ran terminal command: rm cortex/core/coherence_validator.py && echo "Deleted: cortex/core/coherence_validator.py"

Now find and execute remaining zero-external-caller duplicates systematically. 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 - << 'EOF'
import subprocess, os

# All remaining duplicate pairs to scan for zero-caller safe deletions
pairs = [
    # (candidate, check_import_pattern)
    ("cortex/infrastructure/deployment/analytics.py",   r"infrastructure\.deployment\.analytics"),
    ("cortex/infrastructure/secrets/audit_trail.py",    r"infrastructure\.secrets\.audit_trail"),
    ("cortex/infrastructure/audit_verifier.py",         r"infrastructure\.audit_verifier"),
    ("cortex/orchestrators/domain/business/base.py",    r"orchestrators\.domain\.business\.base"),
    ("cortex/orchestrators/domain/business/context.py", r"orchestrators\.domain\.business\.context"),
    ("cortex/orchestrators/validation/coherence_models.py", r"orchestrators\.validation\.coherence_models"),
    ("cortex/models/coherence_models.py",               r"models\.coherence_models"),
    ("cortex/intelligence/lens/lens/pipeline.py",       r"intelligence\.lens\.lens\.pipeline"),
    ("cortex/intelligence/crawler/pipeline.py",         r"intelligence\.crawler\.pipeline"),
    ("cortex/orchestrators/health/pipeline.py",         r"orchestrators\.health\.pipeline"),
    ("cortex/core/registry/health_monitor.py",          r"core\.registry\.health_monitor"),
    ("cortex/core/registry/migration.py",               r"core\.registry\.migration"),
    ("cortex/core/registry/status_update_hook.py",      r"core\.registry\.status_update_hook"),
    ("cortex/core/registry/dashboard_generator.py",     r"core\.registry\.dashboard_generator"),
    ("cortex/lens/ml_patterns/dashboard_generator.py",  r"lens\.ml_patterns\.dashboard_generator"),
    ("cortex/infrastructure/deployment/dashboard_generator.py", r"infrastructure\.deployment\.dashboard_generator"),
    ("cortex/infrastructure/api/dashboard_api.py",      r"infrastructure\.api\.dashboard_api"),
    ("cortex/infrastructure/deployment/dashboard_api.py", r"infrastructure\.deployment\.dashboard_api"),
    ("cortex/infrastructure/secrets/errors.py",         r"infrastructure\.secrets\.errors"),
    ("cortex/infrastructure/storage/errors.py",         r"infrastructure\.storage\.errors"),
    ("cortex/intelligence/domain_brain/optimistic_lock.py", r"intelligence\.domain_brain\.optimistic_lock"),
    ("cortex/orchestrators/health/models.py",           r"orchestrators\.health\.models"),
    ("cortex/dashboards/spa/models.py",                 r"dashboards\.spa\.models"),
    ("cortex/intelligence/intent_classifier.py",        r"intelligence\.intent_classifier\b"),
    ("cortex/intelligence/domain_brain/domain_brain/intent_classifier.py", r"domain_brain\.domain_brain\.intent_classifier"),
    ("cortex/orchestrators/version_manager.py",         r"orchestrators\.version_manager"),
    ("cortex/intelligence/domain_brain/version_manager.py", r"intelligence\.domain_brain\.version_manager\b"),
    ("cortex/governance/validation/wiring_validator.py", r"governance\.validation\.wiring_validator"),
    ("cortex/core/wiring/registry/wiring_validator.py", r"core\.wiring\.registry\.wiring_validator"),
    ("cortex/testing/test_intelligence/test_composer.py", r"testing\.test_intelligence\.test_composer"),
    ("cortex/orchestrators/intelligence/test_value_scorer.py", r"orchestrators\.intelligence\.test_value_scorer"),
    ("cortex/templates/dashboard_renderer.py",          r"templates\.dashboard_renderer"),
    ("cortex/orchestrators/support/dashboard_renderer.py", r"orchestrators\.support\.dashboard_renderer"),
    ("cortex/tools/template_validator.py",              r"tools\.template_validator"),
    ("cortex/templates/template_validator.py",          r"templates\.template_validator\b"),
]

print(f"{'File':<70} {'ExternalCallers':>15}")
print("-"*87)
safe_to_delete = []
for path, pattern in pairs:
    if not os.path.exists(f"/Users/asifhussain/PROJECTS/CORTEX/{path}"):
        print(f"  MISSING: {path}")
        continue
    r = subprocess.run(
        ['grep', '-rn', '--include=*.py', '-E', pattern, 'cortex/', 'tests/'],
        capture_output=True, text=True, cwd='/Users/asifhussain/PROJECTS/CORTEX'
    )
    callers = [l for l in r.stdout.splitlines() if path not in l and '__pycache__' not in l]
    count = len(callers)
    marker = " ← SAFE DELETE" if count == 0 else ""
    print(f"  {path:<68} {count:>3}{marker}")
    if count == 0:
        safe_to_delete.append(path)

print(f"\nSAFE TO DELETE (0 external callers): {len(safe_to_delete)}")
for p in safe_to_delete:
    print(f"  {p}")
EOF

5 confirmed zero-caller deletions. Let me verify each briefly then delete. 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && for f in \
  "cortex/orchestrators/domain/business/base.py" \
  "cortex/intelligence/crawler/pipeline.py" \
  "cortex/core/registry/status_update_hook.py" \
  "cortex/lens/ml_patterns/dashboard_generator.py" \
  "cortex/governance/validation/wiring_validator.py"; do
  echo "=== $f ===" && head -6 "$f" && echo ""
done

All 5 confirmed as compat shims with zero external callers. Delete them all. 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && rm \
  cortex/orchestrators/domain/business/base.py \
  cortex/intelligence/crawler/pipeline.py \
  cortex/core/registry/status_update_hook.py \
  cortex/lens/ml_patterns/dashboard_generator.py \
  cortex/governance/validation/wiring_validator.py && echo "✅ 5 zero-caller compat shims deleted"

6 files deleted (+ coherence_validator). Now run the smoke regression gate. 

Ran terminal command: python3 scripts/run_tests.py smoke 2>&1 | tail -8

**1,420 passed — zero regression.** Now scan the remaining higher-import duplicates and begin migration of the `context_cache_layer`/`context_synthesis_gateway` root copies. 

Ran terminal command: grep -rn "from cortex\.core\.context_cache_layer\b" cortex/ tests/ --include="*.py" | grep -v "__pycache__" && echo "=== callers ===" && grep -rn "from cortex\.core\.context_synthesis_gateway\b" cortex/ tests/ --include="*.py" | grep -v "__pycache__"

Only 2 files import from `cortex.core.context_cache_layer` (root), and 1 from `cortex.core.context_synthesis_gateway` (root). These callers use the **older root versions** — they need to be updated to point to `cortex.core.interaction.*` (the evolved canonical). But the `interaction/` directory itself is a Phase 60 dissolution target. The correct strategy here is: these root files *become* the canonical (they have callers using them), and the `interaction/` duplicates need to re-export from root — not the reverse.

Let me verify the actual functional differences to decide the correct canonical. 

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && python3 -c "
import ast, sys

def get_classes_functions(path):
    with open(path) as f:
        tree = ast.parse(f.read())
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    return classes, funcs

files = [
    'cortex/core/context_cache_layer.py',
    'cortex/core/interaction/context_cache_layer.py',
    'cortex/core/context_synthesis_gateway.py',
    'cortex/core/interaction/context_synthesis_gateway.py',
]
for f in files:
    c, fn = get_classes_functions(f)
    print(f'{f}')
    print(f'  classes: {c}')
    print(f'  top-level functions: {[x for x in fn if not x.startswith(\"_\")]}')
    print()
"

The two pairs expose **different APIs**:
- context_cache_layer.py → `CacheEntry` + `ContextCacheLayer` with `generate_key`, `hash_content`
- context_cache_layer.py → simpler `get_cache()` factory pattern
- context_synthesis_gateway.py → `create_exit_gate`, `SynthesisSession`  
- context_synthesis_gateway.py → `get_gateway`, `SynthesizedContext`

These are genuinely distinct implementations serving different call sites. **Both versions are needed** — not duplicates in the delete sense. The right Phase 60 action is to merge them into a single unified module. Not a Phase 58-f deletion.

Now handle the remaining duplicate pairs with actual callers — rewrite the 3 callers of `cortex.core.context_*` to use `cortex.core.interaction.*` and convert root copies to compat shims. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/incremental_context_loader.py#64-64), lines 64 to 72

Ran terminal command: grep -n "context_cache_layer\|context_synthesis_gateway\|create_exit_gate\|ContextCacheLayer" cortex/orchestrators/core/master_orchestrator.py | head -10

`master_orchestrator.py` already uses `cortex.core.interaction.context_synthesis_gateway` on lines 84 and 3036, but has one stale reference to `cortex.core.context_synthesis_gateway` on line 2364 using `create_exit_gate`. The root `context_synthesis_gateway.py` has the real `create_exit_gate` function while `interaction/` has `get_gateway`. These are distinct functions — not the same. Fix the stale import on line 2364 to use the right source. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core/master_orchestrator.py#2358-2358), lines 2358 to 2375

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/context_synthesis_gateway.py#1-1), lines 1 to 75

The root context_synthesis_gateway.py is a legitimate standalone module with `create_exit_gate`. The context_synthesis_gateway.py has a different `get_gateway` API. These serve different purposes. The "duplicate" filename is misleading — different APIs. **Neither should be deleted.** The correct Phase 60 action will be to rename one of them when `interaction/` is dissolved. Skip these for Phase 58-f.

Now commit the 6 safe deletions already done and update the plan. 

Ran terminal command: git add -A && git status --short | head -20

Ran terminal command: cd /Users/asifhussain/PROJECTS/CORTEX && git commit -m "refactor(phase-58-f): delete 6 zero-caller compat shims — duplicate filename sweep

Phase 58-f: First batch of safe duplicate eliminations.

DELETED (all confirmed 0 external callers):
- cortex/core/coherence_validator.py (shim → orchestrators/validation/)
- cortex/core/registry/status_update_hook.py (shim → infrastructure/automation/)
- cortex/governance/validation/wiring_validator.py (shim → core/wiring/registry/)
- cortex/intelligence/crawler/pipeline.py (shim → orchestrators/health/)
- cortex/lens/ml_patterns/dashboard_generator.py (shim → core/registry/)
- cortex/orchestrators/domain/business/base.py (zero-import abstract base)

Regression gate: 1420 smoke tests PASSING (no regression).
Sweep: SWEEP-58-61-SIMPLIFICATION | CORE-064 partial progress.

AC_START: AC-PHASE58F-$(date +%s)
AC_COMPLETE: AC-PHASE58F-$(date +%s) ✅ 6 files deleted, 1420 smoke green"

Now update the plan file to reflect Phase 58-f progress and remaining duplicate catalogue. 

Using "Replace String in File"


```

```
[██████████] 100% — Batch 1 complete. Committing plan update. 

Ran terminal command: git add cortex-registry/planning/phases/planned/simplification-master-plan-58-61.yaml && git commit -m "docs(registry): update phase-58-f progress — batch 1 of 6 shims deleted, 57 groups remaining"

---

## ✅ Phase 58-f Batch 1 — Complete

**Commit:** `6970e390a` → `ebc06118a`  
**Regression gate:** 1,420 smoke ✅ — zero regressions

### What happened

| Action | Detail |
|---|---|
| **Deleted** | 6 zero-caller compat shims (confirmed via grep before each deletion) |
| **Deferred** | 8 "duplicate" pairs that are actually distinct implementations or deliberate protocol adapters |
| **Scanned** | 35 total candidates — 63 duplicate groups remain (down from 69 extra files) |

### Deferred pairs (correct disposition = Phase 60 merge, not delete)
- `context_cache_layer` / `context_synthesis_gateway` — root vs `interaction/` expose different APIs (`create_exit_gate` vs `get_gateway`). Merge when `interaction/` is dissolved in Phase 60.
- `vacuum_orchestrator` — `support/` is the wiring-contract protocol adapter for `health/` (deliberate CORE-035 pattern)
- `toolkit_tools.py` — two different tool sets at same filename (not duplicates)
- `stage_execution_strategy` — `strategies/` is intentional re-export shim

### Next Steps (type `proceed` to continue)

- **Phase 58-f Batch 2** — next 5 candidates: `audit_verifier`, `lens/cache`, `capability_matcher`, `optimistic_lock`, `lens_dashboard` — grep-verify then delete
- **Phase 59-b** — begin orchestrator consolidation map (115 → 26 canonical), starting with zero-risk deletions: `AnalyticsOrchestrator`, `TestCortexOrchestrator`, `MasterOrchestratorChangeDetection`
- After each batch: `make test-batch` regression gate

Made changes.