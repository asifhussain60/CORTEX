# SDLC Workflow Orchestrator

---
title: SDLCWorkflowOrchestrator — Full Lifecycle Execution
type: orchestration
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/domain/sdlc_workflow_orchestrator.py
order: 13
---

> Domain orchestrator that maps user intents to SDLC phases and executes workflow templates.

---

## Purpose

The `SDLCWorkflowOrchestrator` is a domain-tier orchestrator that provides end-to-end software development lifecycle execution. It bridges user intent classification (from `IntentRouter`) to YAML workflow template execution (via `WorkflowEngine`).

## Intent-to-Phase Mapping

```python
INTENT_TO_PHASE = {
    "ANALYZE":    "requirements-analysis",
    "DESIGN":     "solution-design",
    "IMPLEMENT":  "implementation-execution",
    "TEST":       "testing-strategy",
    "SECURITY":   "security-review",
    "DEPLOY":     "deployment-pipeline",
    "REVIEW":     "code-review-checklist",
}
```

## Execution Flow

1. Receive classified intent from `IntentRouter`
2. Map intent to SDLC phase template
3. Load knowledge from `cortex-registry/knowledge/sdlc/`
4. Execute template via `WorkflowEngine.load()` + `execute_step()`
5. Emit scaffold files via `ScaffoldWriter`
6. Run security gate at phase transition
7. Emit URS reinforcement signal

## Location

`cortex/orchestrators/domain/sdlc_workflow_orchestrator.py`

---

**Full documentation:** `flat-files/16-sdlc-workflow-engine.md`
**Related:** `03-orchestration/11-workflow-engine.md`
