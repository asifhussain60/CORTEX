---
id: governance-vacuum-source-protection
title: Vacuum Source Protection — Hardened Cleanup with PROTECTED_DIRS
purpose: Show how VacuumOrchestrator enforces source directory protection across all 8 cleanup stages.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/health/vacuum_orchestrator.py
  - cortex/orchestrators/health/constants.py
  - cortex/core/rollback_manager.py
last_verified: 2026-03-09
phase_status: "Phase 141 COMPLETE"
diagram_type: Governance
render: ascii
render_html: true
d3_method: "d3.tree() — protection shield with directory list"
---

# Vacuum Source Protection — Hardened Cleanup Safety

```
 ═══════════════════════════════════════════════════════════════════════════════
  VACUUM SOURCE PROTECTION
  "Source directories are NEVER modified — guaranteed by design"
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  🛡️ PROTECTED_DIRS CONSTANT (15 Directories)                               │
  │                                                                             │
  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
  │  │   cortex/       │  │   tests/        │  │   .github/      │              │
  │  │   (source)      │  │   (tests)       │  │   (CI/prompts)  │              │
  │  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
  │                                                                             │
  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
  │  │   scripts/      │  │   deployment/   │  │   .vscode/      │              │
  │  │   (tooling)     │  │   (infra)       │  │   (IDE config)  │              │
  │  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
  │                                                                             │
  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
  │  │ cortex-registry │  │   docs/         │  │   .git/         │              │
  │  │   (config)      │  │   (docs site)   │  │   (VCS)         │              │
  │  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
  │                                                                             │
  │  + node_modules/, venv/, .venv/, __pycache__/, .pytest_cache/, .mypy_cache/ │
  │                                                                             │
  │  ⚠️ ANY file inside these directories is IMMUNE to vacuum operations        │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  🔍 validate_safe_run() — Pre-Flight Safety Check                           │
  │                                                                             │
  │  BEFORE any vacuum operation executes:                                      │
  │                                                                             │
  │  1. Run dry-run with recency_guard_hours=0 (get ALL planned operations)     │
  │  2. For each planned operation:                                             │
  │     ├── Extract source path                                                 │
  │     ├── Check against PROTECTED_DIRS constant                               │
  │     └── If protected → add to warnings list                                 │
  │  3. Return List[str] of any unsafe operations detected                      │
  │  4. If warnings non-empty → ABORT vacuum with detailed explanation          │
  │                                                                             │
  │  ✅ GUARANTEE: Zero source files modified if validate_safe_run() passes     │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  📋 8 VACUUM STAGES — All Protected                                         │
  │                                                                             │
  │  ┌──────────────────┬──────────────────────────────────────────────────┐   │
  │  │ Stage            │ Protection Applied                               │   │
  │  ├──────────────────┼──────────────────────────────────────────────────┤   │
  │  │ 1. Naming        │ File naming violations — PROTECTED_DIRS exempt   │   │
  │  │ 2. Root Clutter  │ Root directory cleanup — source dirs excluded    │   │
  │  │ 3. Empty Dirs    │ Empty folder removal — protected paths skipped   │   │
  │  │ 4. Orphan Files  │ Orphan detection — source files ignored          │   │
  │  │ 5. Markdown      │ Doc sprawl cleanup — .github/, docs/ protected   │   │
  │  │ 6. Digest        │ Digest artifact cleanup — source exempt          │   │
  │  │ 7. Build         │ Build artifact removal — source never touched    │   │
  │  │ 8. OS Artifacts  │ .DS_Store, Thumbs.db — only in safe directories  │   │
  │  └──────────────────┴──────────────────────────────────────────────────┘   │
  │                                                                             │
  │  🔒 INVARIANT: No stage can modify any file inside PROTECTED_DIRS           │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  🔐 RollbackManager SHA Validation                                          │
  │                                                                             │
  │  Pattern: _SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")                      │
  │                                                                             │
  │  Before git reset --hard:                                                   │
  │  1. Validate target_sha against 40-character hex pattern                    │
  │  2. If invalid → raise ValueError (no git operation)                        │
  │  3. If valid → proceed with safe rollback                                   │
  │                                                                             │
  │  ✅ PREVENTS: Malformed SHA injection, arbitrary git commands               │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  🧪 8 GOLDEN TESTS (GV-012 through GV-019)                                  │
  │                                                                             │
  │  tests/golden/orchestrators/health_vacuum/                                  │
  │                                                                             │
  │  GV-012: test_vacuum_never_touches_cortex_dir                               │
  │  GV-013: test_vacuum_never_touches_tests_dir                                │
  │  GV-014: test_vacuum_never_touches_github_dir                               │
  │  GV-015: test_vacuum_never_touches_scripts_dir                              │
  │  GV-016: test_vacuum_never_touches_deployment_dir                           │
  │  GV-017: test_vacuum_never_touches_vscode_dir                               │
  │  GV-018: test_validate_safe_run_detects_protected_path                      │
  │  GV-019: test_rollback_manager_rejects_invalid_sha                          │
  │                                                                             │
  │  ✅ ALL PASSING: Source protection enforced at test level                   │
  └─────────────────────────────────────────────────────────────────────────────┘
```

## Why Source Protection Matters

The VacuumOrchestrator is an aggressive cleanup tool designed to remove stale files, documentation sprawl, and build artifacts. Without proper protection, a misconfigured vacuum operation could delete source code.

**Phase 141** established these guarantees:

1. **PROTECTED_DIRS constant** — A single source of truth for all protected directories, used across all 8 vacuum stages
2. **validate_safe_run()** — A pre-flight check that simulates the vacuum operation and verifies no protected paths would be touched
3. **SHA validation** — The RollbackManager validates git SHA format before any `git reset --hard` operation
4. **Golden tests** — 8 deterministic tests that verify source protection invariants on every build

## Business Impact

**For Business Leaders:** Automated cleanup that is provably safe — source code is mathematically protected from deletion, not just "carefully coded."

**For Product Owners:** Confidence that developer automation tools have safety rails that prevent catastrophic accidents.

**For Engineers:** The ability to run `/vacuum` aggressively without fear — knowing that source directories are protected by design, not by careful usage.

---

*Vacuum Source Protection verified against live implementation · Phase 141 COMPLETE*
