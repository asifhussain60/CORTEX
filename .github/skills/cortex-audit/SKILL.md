---
name: cortex-audit
description: 'CORTEX audit and quality skill. Use when: running /audit, /audit fix, /health, /healthcheck, checking production readiness, scanning for issues, running governance checks, or validating wiring contracts. Covers the 9-stage audit pipeline, 29-point + 12 hardening checks, health endpoints, and drift lock protocol.'
argument-hint: 'fix | health | stage <1-9> | check <1-41>'
detail-prompt-file: '../../prompts/cortex-architect.prompt.md'
---

# CORTEX Audit & Quality

---

## `/audit fix` — Full Production-Readiness Pipeline (9 stages)

**Workflow template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`

**Steps:**
1. Run holistic validation gate (CORE-048)
2. Open sweep catalogue (CORE-064) — tracks every issue found
3. Stages 1-6: Static analysis → governance compliance → wiring contracts → AC marker integrity → MCP tool registry → YAML schema validation
4. Stages 7-8: `detect-fix-rescan-loop.yaml` — loops until `p0_count == 0 AND p1_count == 0` (max 3 cycles)
5. Stage 9: Preflight test gate → `make test-preflight` (must be GREEN)
6. Close sweep catalogue — all gaps must have `status: CLOSED`

**Convergence guarantee:** NOT a single pass. All P0/P1 must be zero.

---

## `/health` — Orchestrator Health Endpoints

Runs all 22 orchestrator health endpoints. Latency envelopes: core:<200ms, domain:<500ms, support:<1s.

```bash
/health
```

Entry points: `HealthOrchestrator` → `cortex/orchestrators/health/health_orchestrator.py`

---

## `/healthcheck` — Full Test Suite

```bash
make test-healthcheck
```

---

## 29-Point Check Summary

Checks #1–#29 cover: stale imports, empty stubs, duplicate orchestrators, low-value tests, broken file references, root-level clutter, CORE rule violations, scattered DB files, deprecated filenames, test-source mirror, orchestrator health, markdown sprawl, prompt coherence, response header drift, MCP registry alignment, knowledge wiring, LENS health, ghost directories, SQLite health, workflow composer health, challenge gate drift, duplicate methods (F811), unused imports (F401), OS artifacts, THIN INDEX CONTRACT, duplicate classes, stale test dirs, AC marker persistence, intelligence layer health.

For full check specifications during an active audit: [See audit checks reference](./references/checks.md)

---

## Hardening Checks #30–#41

Extended checks from Phase 126: Windows boot wiring, architecture runtime connectivity, stub eradication, YAML reader no-bypass, no versioning, repo hygiene, prompt determinism, response template golden snapshot, registry cohesion, sync non-production markers, production readiness green gate, drift lock system.

For full hardening check detail: [See audit checks reference](./references/checks.md)

---

## Wiring Contract Validation (Stage 3)

| Level | Checks | Blocks? |
|---|---|---|
| L1 — Structural | Module importable, class exists, health_check present | YES |
| L2 — Functional | MCP adapter, dependencies, unique priorities | No |
| L3 — Quality | Coverage ≥85%, recent invocations, docs | No |

Source: `cortex-registry/core/specifications/` (4 YAML files)

---

## Drift Lock Protocol

Every gap closed by `/audit fix` emits:
1. Lock YAML: `cortex-registry/governance/drift-locks/<check-id>-lock.yaml`
2. Preflight test: `tests/preflight/test_drift_lock_<check-id>.py`

Locks are always P0 severity with `ci_gate: true` — merge blocked on violation.

---

## Governance Rules (Merged from `cortex-governance`)

Use this section whenever governance context is required.

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create .md/.txt report files |
| CORE-008 | TDD mandatory — write failing test first, then implement |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent autonomous execution (progress bars only) |
| CORE-064 | Sweep completeness — every FIX/REFACTOR/AUDIT exhausts full catalogue |
| CORE-068 | Universal convergence gate — detect→fix→rescan until 0 P0/P1 (max 3 cycles) |

### AC Marker Contract

Format: `AC-{DOMAIN}-{SEQUENCE}` (example: `AC-P89-001`)

- `AC_START` at entry of every public orchestrator method
- `AC_COMPLETE` on success/failure with timing and status
- No orphaned `AC_START` markers
- Trace persistence: `.cortex-runtime/traces/orchestrator-traces.db`

### PLIP-001 Guard

Before code-modifying operations:
1. Query history: `cortex_learning op=history`
2. Query prevention rules: `cortex_learning op=rca rca_action=query`
3. Emit reinforcement signal after outcome (`MILD_REWARD` or `MILD_PUNISHMENT`)

---

## Key Commands

```bash
/audit fix          # Full scan + auto-fix (9 stages)
/audit              # Scan only (stages 1-6)
/health             # Orchestrator health endpoints
make test-preflight # Audit gate (< 10s)
```
