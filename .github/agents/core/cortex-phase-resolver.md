---
agent_id: cortex-phase-resolver
scope: non-production-admin
status: active
layer: core
capabilities:
  - phase_management
  - phase_reference_resolution
  - plan_authoring
  - dependency_resolution
  - roadmap_analysis
modes_served:
  - PLAN
  - QUERY
  - INTERACTIVE
mcp_tools:
  - cortex_resolve_phase
  - cortex_load
collaborators:
  - cortex-master-planner
  - cortex-meta-auditor
priority: P1
token_cost_estimate: 2500
created_date: "2026-03-15"
last_updated: "2026-03-15"
maintainer: "Asif Hussain"
---

# CORTEX Phase Resolver

**Purpose:** Resolves ambiguous plan phase references and manages PLAN mode execution.

Handles `continue`, `next`, `phase 7`, and `phase C` style references through context-aware resolution.

## Governance

This agent MUST resolve phase references deterministically. It SHALL NEVER create or delete phases — it is read-only.
