---
scope: non-production-admin
---
# CORTEX Trainer Prompt

**Updated:** 2026-02-26 | **Agent:** `cortex-learning.md`
**Orchestrator:** `TrainerOrchestrator` (`cortex/orchestrators/intelligence/trainer_orchestrator.py`)
**MCP Tool:** `cortex_train`

---

## Purpose

Gap-driven intelligence growth for CORTEX. Analyze external repositories, extract coding patterns, detect gaps against existing workflow templates, and propose surgical changes (CREATE/ENHANCE/DELETE) — never random generation.

---

## Usage

```
/train {path}                    # Full pipeline: analyze → propose
/train cortex-sts/CortexLabs/BadMonolith
```

---

## How It Works

1. **Inventory** — Catalog existing templates in `cortex-registry/workflows/templates/`
2. **Analyze** — Extract patterns, tech stack, anti-patterns from target
3. **Detect Gaps** — Compare analysis vs inventory
4. **Propose** — Generate change manifest (CREATE/ENHANCE/REVIEW_FOR_DELETE)
5. **Execute** — Apply approved changes (requires explicit approval)

---

## Key Principles

- ❌ Never randomly generates templates
- ❌ Never duplicates existing templates
- ❌ Never deletes without human review
- ✅ Evidence-backed proposals (every action traces to detected pattern)
- ✅ Inventory-aware (checks what exists first)
- ✅ Human-in-the-loop approval before execution

---

## MCP Tool

```python
cortex_train(op="scan", target_path="/path/to/repo")
cortex_train(op="propose", gaps={...})
cortex_train(op="execute", proposal={...})
cortex_train(op="score", execution_report={...})  # Phase 83: URS scoring
```

---

## URS Scoring Model (Phase 83)

### 🧠 Learning Protocol (PLIP-001)

**SSOT:** `cortex-registry/core/prompt-learning-protocol.yaml`

**🔒 Scope Lock — `training`:** This prompt learns ONLY from training and gap-detection patterns: `training`, `gap-detection`. It MUST NOT query or emit patterns scoped to: `html-design`, `doc-sync`, `database`, `sync`, `debug`, `vacuum`, `design-system`, `a11y`. Those domains belong to other prompts. Violation = P1 scope bleed.

Before every gap detection and proposal generation:
- Call `cortex_learning op=history scope=training` — retrieve prior training session outcomes
- If prior failures exist (e.g. rejected proposals, failed template applications): surface as `⚠️ Prior failure pattern: {description}`

After every training execution:
- On success (proposal applied, tests pass): `cortex_learning op=emit signal_type=MILD_REWARD pattern_id=training`
- On failure (proposal rejected, tests fail): `cortex_learning op=emit signal_type=MILD_PUNISHMENT pattern_id=training`

The URS scoring model below provides the signal vocabulary for these emissions.

The Unified Reinforcement Signal (URS) system closes the learning loop. When orchestrators complete operations, they emit reinforcement signals that adjust pattern confidence.

### Signal Types

| Signal | Score | Example |
|--------|-------|---------|
| `STRONG_REWARD` | +1.0 | Test passes, zero governance violations |
| `MILD_REWARD` | +0.5 | Partial success, P2-only warnings |
| `NEUTRAL` | 0.0 | Informational, ignored instruction |
| `MILD_PUNISHMENT` | -0.5 | Partial failure, P0 violations present |
| `STRONG_PUNISHMENT` | -1.0 | Complete test failure, critical error |

### Confidence Rules

- **PROMOTE** at ≥0.9 confidence with 3+ rewards → T1 knowledge tier
- **QUARANTINE** at ≤0.3 confidence with 2+ punishments → excluded from guidance
- **DECAY** 0.1 per 30 days of inactivity → stale patterns weaken
- **CROSS-CUTTING BOOST** +0.15 when validated by 3+ orchestrators

### MCP Tools

- `cortex_train(op="score")` — Score an execution report via TrainerOrchestrator
- `cortex_learning(op="emit")` — Emit a reinforcement signal directly
- `cortex_learning(op="history")` — View signal history (filterable by pattern_id)
- `cortex_learning(op="decay")` — Decay stale patterns
- `cortex_learning(op="promote")` — Promote high-confidence patterns
- `cortex_learning(op="quarantine")` — Quarantine low-confidence patterns

---

## Related Components

| Component | Role |
|-----------|------|
| `BulkDigestOrchestrator` | Content classification |
| `UniversalLearningLoop` | Pattern capture |
| `WorkflowTemplateMixin` | Template discovery |
| `RefactoringOrchestrator` | STS 7-gate analysis |

---

## Agent Reference

See `.github/agents/education/cortex-learning.md` for full agent specification.
