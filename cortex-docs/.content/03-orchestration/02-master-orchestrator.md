# MasterOrchestrator

---
title: MasterOrchestrator — The Executive Coordinator
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/core/master_orchestrator.py
order: 2
---

> **Brain analogy:** MasterOrchestrator is the **thalamus** — the central relay hub. Every sensory signal (request) passes through it before reaching the specialized cortical regions (domain orchestrators). It doesn't process the work itself; it ensures the right region handles it.

## Responsibility

MasterOrchestrator coordinates all other orchestrators through hierarchical dispatch:

1. Receives enriched request from MCP Gateway
2. Invokes IntentRouter for classification
3. Dispatches to the appropriate orchestrator
4. Monitors execution progress
5. Records audit trail

**Location:** `cortex/orchestrators/core/master_orchestrator.py`

**Implements:** `IOrchestrator`, `OrchestratorAuditMixin`

---

*Verified against live implementation · 20 February 2026*
