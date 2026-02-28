# Cross-Orchestrator Communication

---
title: Cross-Orchestrator Communication
type: reference
audience: [Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/core/master_orchestrator.py + cortex/orchestrators/response/engagement_renderer.py
order: 6
---

## How Orchestrators Communicate

Orchestrators don't call each other directly. All communication flows through **MasterOrchestrator**:

```
[Orchestrator A] ─── result ──→ [MasterOrchestrator] ─── dispatch ──→ [Orchestrator B]
```

This ensures:
1. All inter-orchestrator communication is auditable
2. Governance gates are checked between orchestrator handoffs
3. No circular dependencies between orchestrators
4. The audit trail captures the complete request path

## Common Communication Patterns

| Pattern | Example |
|---------|---------|
| **Sequential** | IntentRouter → TDDOrchestrator → EnforcementOrchestrator |
| **Fan-out** | MasterOrchestrator dispatches to multiple analyzers |
| **Callback** | Orchestrator requests LENS analysis mid-execution |
| **Pipeline** | RequestRephrase → Intent → TDD → Governance → Audit |

---

*Verified against orchestrator dispatch patterns*

---

## Orchestrator Engagement Visibility

Every orchestrator invocation emits engagement signals so users understand which orchestrator is active and why.

### BLOCK-ENGAGEMENT-BREADCRUMB

Rendered on every response header for multi-hop routing chains:

```
**Route:** `IntentRouter → MasterOrchestrator → TDDOrchestrator`
```

This is the primary engagement signal — always rendered, never omitted for 2+ hop chains.

### BLOCK-ENGAGEMENT-TIMELINE

Collapsible timing log emitted after 3+ step operations:

| Orchestrator | Duration | Status |
|---|---|---|
| IntentRouter | 0.3s | ✅ |
| MasterOrchestrator | 1.2s | ✅ |
| TDDOrchestrator | 8.4s | ✅ |
| **Total** | **9.9s** | ✅ |

Always wrapped in `<details>` — never expanded by default (CORE-049 noise reduction).

### BLOCK-PHASE-ROADMAP

Rendered once at the start of any multi-phase operation (N≥2 phases), giving users the full journey before work begins. Updates when phases complete.

**SSOT:** `.github/templates/cortex-response-templates.md` §BLOCK-ENGAGEMENT-BREADCRUMB, §BLOCK-ENGAGEMENT-TIMELINE, §BLOCK-PHASE-ROADMAP.

### EngagementRenderer — SSOT Breadcrumb Formatting (Phase 92)

`EngagementRenderer` at `cortex/orchestrators/response/engagement_renderer.py` is the single canonical formatter for all engagement blocks. It provides:

- `breadcrumb_for_command(command)` — returns pre-built engagement chains for 14 known commands (`/audit fix`, `/vacuum`, `/health`, `/debug`, etc.)
- `format_breadcrumb(chain)` — renders routing chains as `→`-separated orchestrator paths
- Integration with `InteractionOrchestrator` output — Stage 1 IO delegation emits the breadcrumb via EngagementRenderer

### Universal Convergence Gate (CORE-068, Phase 94)

Every code-modifying orchestrator operation must pass through a convergence gate before `AC_COMPLETE`:

1. **Detect** — rescan for test failures, compliance violations, regressions introduced by changes
2. **Fix** — remediate any P0/P1 issues found
3. **Rescan** — verify fixes did not introduce new issues
4. Loop back to step 1 if issues remain (max 3 cycles)

Work is **never** considered complete in one pass. The detect-fix-rescan loop primitive lives at `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`.

**Convergence predicate by mode:**
- IMPLEMENT: `test_pass_count >= baseline AND lint_errors == 0`
- FIX: `regression_count == 0 AND original_bug_fixed`
- REFACTOR: `test_pass_count >= baseline AND no_new_lint_errors`
- AUDIT: `p0_count == 0 AND p1_count == 0`
- DEBUG: `no_orphaned_markers AND fix_plan_verified`

*Verified against orchestrator engagement standards and Phase 89-94 wiring*
