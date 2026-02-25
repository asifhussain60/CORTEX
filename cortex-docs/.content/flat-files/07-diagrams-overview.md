# Diagrams Overview

---
title: Architecture Diagrams
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
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
| 3 | [Orchestrator Map](04-orchestrator-map.md) | 27 wired orchestrators across 3 canonical tiers (7 core, 6 domain, 14 support) + 7 additional dirs (health, git, intelligence, strategies, synthesis, validation, workflow) | Developers |
| 4 | [LENS Pipeline](05-lens-pipeline.md) | 8 analyzers → Synthesis | Developers |
| 5 | [Governance Flow](06-governance-flow.md) | 35 CORE rule enforcement lifecycle | All |
| 6 | [MCP Transport](07-mcp-transport.md) | IDE ↔ CORTEX communication (39 tools) | Developers |
| 7 | [Testing Pyramid](08-testing-pyramid.md) | Test tiers and execution (15,739 tests) | Developers, POs |
| 8 | [Brain Tier Model](09-brain-tier-model.md) | Intelligence tiers (Perception → Reasoning → Action) | All |

---

## D3.js Interactive Diagrams

Located in `cortex-docs/assets/diagrams/d3/`:

| File | Type | Description |
|------|------|-------------|
| `governance-pyramid.html` | Sunburst | Interactive 35-rule governance pyramid |
| `request-lifecycle-sankey.html` | Sankey | 17-orchestrator request flow |
| `tdd-knowledge-cycle.html` | Circular flow | RED → GREEN → REFACTOR cycle |
| `orchestrator-tier-map.html` | Layered | 3-tier orchestrator architecture (27 wired) |

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

*Verified against live CORTEX architecture · 25 February 2026*
