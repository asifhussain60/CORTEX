# Diagrams Overview

---
title: Architecture Diagrams
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/ (live architecture)
order: 1
---

> **Brain analogy:** These diagrams are **brain scans** — MRI, CT, and PET images that reveal the brain's structure and function. Each diagram shows a different layer: anatomy (architecture), blood flow (data flow), neural pathways (orchestration), and immune response (governance).

---

## Diagram Index

| # | Diagram | Purpose | Primary Audience |
|---|---------|---------|------------------|
| 1 | [High-Level Architecture](02-high-level-architecture.md) | System overview — all major components | All |
| 2 | [Request Flow](03-request-flow.md) | End-to-end request lifecycle | Developers, POs |
| 3 | [Orchestrator Map](04-orchestrator-map.md) | 52 orchestrators across 10 domains | Developers |
| 4 | [LENS Pipeline](05-lens-pipeline.md) | 8 analyzers → Synthesis | Developers |
| 5 | [Governance Flow](06-governance-flow.md) | Rule enforcement lifecycle | All |
| 6 | [MCP Transport](07-mcp-transport.md) | IDE ↔ CORTEX communication | Developers |
| 7 | [Testing Pyramid](08-testing-pyramid.md) | Test tiers and execution | Developers, POs |
| 8 | [Brain Tier Model](09-brain-tier-model.md) | Intelligence tiers (Perception → Reasoning → Action) | All |

---

## Notation

All diagrams use ASCII art for universal compatibility (no external rendering tools required).

| Symbol | Meaning |
|--------|---------|
| `[Component]` | System component |
| `─── →` | Data flow |
| `│` | Vertical connection |
| `├──` | Branch connection |
| `▼` | Direction indicator |
| `(description)` | Annotation |

---

*Verified against live CORTEX architecture · 20 February 2026*
