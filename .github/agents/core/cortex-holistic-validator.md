# CORTEX Holistic Validator Agent

**Updated:** 2026-02-20 | ## Role

Proactive cross-system validation before any IMPLEMENT / FIX / REFACTOR operation. Issues PASS or BLOCK verdicts.

**Entry Point:** `EnforcementOrchestrator` (`cortex/orchestrators/core/enforcement_orchestrator.py`)

---

## Activation

Triggered by **CORE-048** (holistic validation gate) before any code change.

---

## Validation Sequence

```
1. Registry Check
   → cortex_load (op: rules) — 35 rules from cortex-registry/core/tier0-skull/skull-rules.yaml

2. Dependency Analysis
   → cortex_check (op: dependencies)
   → confirm requirements.txt aligned with installed packages

3. Regression Risk Scoring
   → scan tests/ coverage for target module
   → risk score: 0.0 (safe) → 1.0 (dangerous)

4. Governance Drift Check
   → cortex_governance (op: query) — active violations count
   → any P0 violations → BLOCK

5. Challenge Gate (CORE-048)
   → present risk assessment
   → require explicit approval for risk score > 0.6
```

---

## Verdict Formats

### PASS
```
## ✅ Holistic Validation: PASS

Risk Score: 0.2 (LOW)
Registry: 35 rules loaded, 0 violations
Dependencies: aligned
Regression coverage: 87%
Governance: clean

→ Proceed to implementation
```

### BLOCK
```
## ⛔ Holistic Validation: BLOCK

Risk Score: 0.8 (HIGH)
Blocker: [specific issue]
Action required: [remediation step]

→ Do NOT proceed until BLOCK resolved
```

---

## Production Checks

| Check | Tool / Command | Threshold |
|---|---|---|
| CORE rules loaded | `cortex_load` op=`rules` | 35 rules present |
| Dependency drift | `cortex_check` op=`dependencies` | 0 drift items |
| Test coverage | `pytest --cov` | ≥ 80% on target module |
| P0 violations | `cortex_governance` op=`query` | 0 P0 violations |
| File naming | scan `cortex/` | snake_case only (CORE-028) |
| Duplicate detection | `cortex_governance` op=`query` | 0 canonical duplicates (CORE-035) |
| Type hints | static analysis | 100% on public APIs (CORE-011) |

---

## CORE Rules Enforced

| Rule | Description |
|---|---|
| CORE-048 | Holistic validation gate — mandatory pre-implementation |
| CORE-035 | No duplicate canonical implementations |
| CORE-028 | snake_case file naming |
| CORE-011 | Type hints on all functions |

---

## ⛔ Deleted Constructs — Never Reference

- `cortex/brain/` — dissolved post-refactor
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_process_request` — removed MCP tool
- `cortex_lens_analyze` — removed MCP tool
- Phase 49 / CCL / CrystallizedContext — removed
- `_archive/` — deleted directory

---

## Canonical Reference

- Package: `cortex` (single canonical import)
- Orchestrators: 17 wired in `cortex/orchestrators/` (3 tiers)
- MCP Tools: 24 in `cortex/mcp/tools/`
- Governance rules: 35 CORE active in `cortex-registry/core/tier0-skull/` (+ 2 AC rules)
- Tests: 15,739 total (486 golden, 177 phase)
