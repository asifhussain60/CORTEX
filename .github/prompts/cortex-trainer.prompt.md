# CORTEX Trainer Prompt

**Updated:** 2026-02-26 | **Agent:** `cortex-trainer.md`
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
```

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

See `.github/agents/education/cortex-trainer.md` for full agent specification.
