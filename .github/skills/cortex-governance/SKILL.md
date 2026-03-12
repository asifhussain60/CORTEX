---
name: cortex-governance
description: 'CORTEX governance rules and enforcement reference. Hidden from slash menu — auto-loaded when governance context is needed. Covers all CORE rules (CORE-002 through CORE-068), enforcement orchestrator behavior, drift-lock protocol, AC marker format, and pre-commit hook requirements.'
user-invocable: false
---

# CORTEX Governance Rules

**Hidden skill — auto-loaded by model when governance context is needed.**

---

## CORE Rules Quick Reference

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

---

## Enforcement

| Component | Location |
|---|---|
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| Rule definitions | `cortex-registry/core/` (26 YAMLs) |
| Governance policies | `cortex-registry/governance/` (35 YAMLs) |
| Pre-commit hook | `.github/hooks/pre-commit` → `cortex/scripts/verify_environment.py` |

---

## AC Marker Format

Format: `AC-{DOMAIN}-{SEQUENCE}` (e.g. `AC-P89-001`, `AC-CORE-042`)

- `AC_START` at entry of every public orchestrator method
- `AC_COMPLETE` on success with ✅ + timing (ms)
- `AC_COMPLETE` on failure with ❌ + error classification
- No orphaned `AC_START` without matching `AC_COMPLETE` (P0 violation)
- Persistence: `.cortex-runtime/traces/orchestrator-traces.db`

---

## Drift-Lock Protocol

Every gap closed by `/audit fix` emits:
1. Lock YAML: `cortex-registry/governance/drift-locks/<check-id>-lock.yaml`
2. Preflight test: `tests/preflight/test_drift_lock_<check-id>.py`

Locks are P0 severity, `ci_gate: true`.

---

## MCP Tool Authoring Guard

All MCP tool functions calling `validate_orchestrator_context` must guard:

```python
if orchestrator_context is not None:
    validate_orchestrator_context(orchestrator_context)
```

---

## Dissolved Packages (NEVER import)

- `cortex_intelligence` → `cortex.intelligence`
- `cortex_lens` → `cortex.lens`
- `cortex.brain` → `cortex.intelligence`
- `cortex_brain` → `cortex.intelligence`

---

## PLIP-001 (Prompt-Layer Intelligence Protocol)

Before code-modifying operations:
1. `cortex_learning op=history` — surface prior failure patterns
2. `cortex_learning op=rca rca_action=query` — check prevention rules
3. After success: `op=emit signal_type=MILD_REWARD`
4. After failure: `op=emit signal_type=MILD_PUNISHMENT`

Exempt intents: QUERY, REPHRASE, INTRODUCE, DIGEST, DESIGN, PLAN, RCA
