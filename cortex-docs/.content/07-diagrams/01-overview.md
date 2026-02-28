# Diagrams Overview

---
title: Architecture Diagrams
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
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
| 3 | [Orchestrator Map](04-orchestrator-map.md) | Wired orchestrators across 4 tiers (core, domain, support, git) + additional dirs (health, git, intelligence, strategies, synthesis, validation, workflow) | Developers |
| 4 | [LENS Pipeline](05-lens-pipeline.md) | 15 analyzer components → Synthesis | Developers |
| 5 | [Governance Flow](06-governance-flow.md) | CORE rule enforcement lifecycle | All |
| 6 | [MCP Transport](07-mcp-transport.md) | IDE ↔ CORTEX communication (39 tools) | Developers |
| 7 | [Testing Pyramid](08-testing-pyramid.md) | Test tiers and execution | Developers, POs |
| 8 | [Brain Tier Model](09-brain-tier-model.md) | Intelligence tiers (Perception → Reasoning → Action) | All |
| 9 | [Golden Test Taxonomy](10-golden-test-taxonomy.md) | Golden test subfolder structure and scoring | Developers |
| 10 | [Golden Test Lifecycle](11-golden-test-lifecycle.md) | Scoring, promotion, maintenance, demotion | Developers, POs |
| 11 | [SDLC Pipeline](12-sdlc-pipeline.md) | 7-phase SDLC lifecycle with security gates | All |
| 12 | [Workflow Template Engine](13-workflow-template-engine.md) | 17 categories, primitive composition | Developers |
| 13 | [RGR Quality Cycle](14-rgr-cycle.md) | Two-level Red-Green-Refactor cycle | Developers, POs |
| 14 | [STS Transformation](15-sts-transformation.md) | Sharpen The Saw — before/after demo | All |
| 15 | [Security-First Architecture](16-security-first.md) | 5-layer security defence model | All |
| 16 | [Knowledge Hydration](17-knowledge-hydration.md) | Knowledge resolution and context assembly | Developers |

---

## D3.js Interactive Diagrams

Located in `cortex-docs/assets/diagrams/d3/`:

| File | Type | Description |
|------|------|-------------|
| `governance-pyramid.html` | Sunburst | Interactive 35-rule governance pyramid |
| `request-lifecycle-sankey.html` | Sankey | 17-orchestrator request flow |
| `tdd-knowledge-cycle.html` | Circular flow | RED → GREEN → REFACTOR cycle |
| `orchestrator-tier-map.html` | Layered | 4-tier orchestrator architecture |

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

*Verified against live CORTEX architecture*
