# CORTEX University — Learning Path Content Model

---
title: CORTEX University — Structured Learning Path Content
type: learning-content
audience: [Curious Learners, Software Developers, Product Owners, Business Leaders]
last_verified: 2026-03-09
order: 15
---

> **CORTEX University is a structured learning experience** that transforms the framework's architecture, governance, and intelligence capabilities into progressive educational content — designed to build understanding from orientation through mastery.

---

## Learning Philosophy

CORTEX University follows four research-backed pedagogical principles:

**Progressive Disclosure** — You encounter concepts in order of dependency. High-level orientation before architectural detail. Conceptual foundation before implementation specifics. Every section builds on what came before.

**Active Learning** — Interactive diagrams, practical examples, and explorable concept maps replace passive reading. You engage with the system rather than observing it.

**Visual Knowledge Mapping** — Concept relationship graphs help you see how ideas connect. Architecture patterns link to orchestrators. Governance rules link to enforcement mechanisms. Every concept exists in a web of relationships.

**Multi-Diagram Teaching** — Different diagrams explain different aspects. Architecture layers need tree diagrams. Workflows need pipeline visualizations. Relationships need force-directed graphs. The visualization matches the concept.

---

## The Three Levels

### Level 1 — Orientation

You start by choosing what to learn. Six learning domains present the major capability areas of CORTEX, each with difficulty level, estimated duration, and a preview of what you will discover.

The domains are:

| Domain | Difficulty | Topics | Duration | What You Learn |
|--------|-----------|--------|----------|---------------|
| **Architecture Patterns** | Intermediate | 8 | ~45 min | How 330+ orchestrators coordinate across 14 domains — the structural backbone |
| **AI Orchestration** | Intermediate | 7 | ~40 min | Intent routing, LENS intelligence tiers, Perception → Reasoning → Action |
| **Workflow Automation** | Advanced | 6 | ~35 min | Declarative templates, primitive composition, WorkflowComposer engine |
| **Governance & Quality** | Beginner | 9 | ~50 min | 60+ self-enforcing rules across pre-commit, CI, and runtime layers |
| **TDD-First Development** | Beginner | 5 | ~30 min | The mandatory Red → Green → Refactor cycle, test scoring, golden tests |
| **Intelligence & Learning** | Advanced | 8 | ~45 min | LENS sensory system, RCA memory, URS reinforcement, knowledge acquisition |

### Level 2 — Concept Explorer

Instead of a static list of topics, you explore an interactive concept map. Concepts appear as nodes. Relationships appear as edges. The graph reveals how patterns connect to orchestrators, how governance rules connect to enforcement mechanisms, and how intelligence flows through the system.

**Node types:**
- **Patterns** — Architecture and design patterns used throughout CORTEX
- **Orchestrators** — The 330+ specialised processing engines
- **Workflows** — Declarative execution templates
- **Governance** — Rules, gates, and enforcement mechanisms
- **Intelligence** — LENS, RCA, URS, and knowledge systems

**Relationship types:**
- `uses` — Pattern A is used by Orchestrator B
- `implements` — Orchestrator C implements Pattern D
- `references` — Workflow E references Governance Rule F
- `composes` — Template G composes Primitives H, I, J

### Level 3 — Deep Dive

Each concept has a full educational page containing:

1. **Plain-language explanation** — What the concept is and why it matters
2. **Real-world analogy** — A familiar comparison that grounds the technical idea
3. **CORTEX implementation** — How the concept appears inside the framework
4. **Interactive diagram** — A D3.js visualization that makes the concept visual
5. **Practical example** — A realistic usage scenario with code context
6. **Related concepts** — Links to neighbouring concepts in the knowledge graph

---

## Architecture Domain — Key Concepts

### The Hospital Analogy

CORTEX operates like a large hospital. When a patient (request) arrives, the triage nurse (IntentRouter) instantly determines whether to send them to cardiology, orthopaedics, or radiology. Each department has deep expertise. The hospital works because every department follows the same protocols and communicates through a central system.

### Fourteen Domains

330+ orchestrators are organised across 14 specialised domains:

- **Core** (130+) — The command layer: routing, coordination, enforcement, central workflows
- **Support** (50+) — Operations: health monitoring, cleanup, debugging, onboarding
- **Domain** (25+) — Specialists: code review, refactoring, planning, dashboards
- **Health** (25+) — System wellness: preflight checks, environment verification
- **Intelligence** (15+) — Learning: RCA memory, URS signals, knowledge synthesis
- **Validation** (13) — Contract verification across orchestrator boundaries
- **Persona** (7) — Role-specific behaviour adaptation
- **Workflow** (7) — Template execution and composition
- **Response** (5) — Output formatting and template assembly
- **Git** (5) — Version control operations and pre-commit enforcement

### The Five-Step Lifecycle

Every orchestrator follows the same lifecycle, regardless of specialisation:

1. **Prepare** — Load configuration, establish connections
2. **Govern** — Run the governance gate before any work begins
3. **Execute** — Perform the specialised work
4. **Validate** — Verify results against acceptance criteria
5. **Close** — Record audit trail, emit completion signals

---

## Intelligence Domain — Key Concepts

### LENS — The Sensory System

Before CORTEX writes a single line, 9 parallel analyzers build a complete picture of your workspace — structure, history, coupling, security, patterns, and complexity — all in under one second.

The nine analyzers: structure, pattern, dependency, history, security, documentation, complexity, business-domain, technology-stack.

### Three Intelligence Tiers

| Tier | Speed | When Used |
|------|-------|-----------|
| **Quick** | <200ms | Simple queries, definitions, rule lookups |
| **Targeted** | <2s | Daily workflow: build, fix, refactor |
| **Full** | <10s | Audits, investigations, architecture changes |

### The Brain — Perception → Reasoning → Action

CORTEX is a three-tier intelligence system:

1. **Perception** — LENS scans 9 dimensions, matching your codebase against canonical patterns with confidence scores 0–1.0
2. **Reasoning** — IntelligenceFacade selects the optimal strategy based on request complexity and historical success rates
3. **Action** — MasterOrchestrator routes to intent-specialised orchestrators with enforcement gates and convergence loops

---

## Recent Capabilities (Issue-Derived Knowledge)

### CORTEX Autonomous Planning Engine (CAPE)

CAPE introduces intelligent plan generation driven by a 5-dimension complexity scoring engine. A request's clarity, LENS context quality, change scope, architectural risk, and historical precedent combine into a Complexity-Driven Routing (CDR) score that classifies the request as SIMPLE, MODERATE, or COMPLEX. Five mandatory analysis gates validate every plan before execution.

**Design patterns demonstrated:** Strategy (scoring dimensions), Builder (scaffolder), Chain of Responsibility (gates), Pipeline (execution loop).

### Knowledge Acquisition Layer (KAL)

KAL enables on-demand domain knowledge synthesis. When knowledge coverage drops below threshold, a 6-step pipeline automatically assesses gaps, synthesizes structured YAML knowledge files, validates schema, and registers new knowledge — all driven by LENS analysis output.

**Design patterns demonstrated:** Observer (coverage-triggered), Pipeline (6-step), Factory (synthesizer), Registry (index registrar).

### PO Change Intelligence (Phase 129 — PO Intelligence Suite)

Three new orchestrators extend CORTEX to Product Owner decision support: process discovery via LENS, best-practice comparison with gap analysis, change recommendations with ROI analysis, and structured requirements engineering.

**Traceability spine:** process-discovery → best-practice-comparison → change-recommendation → requirements-synthesis → implementation → training-doc-generation.

---

*CORTEX University content model · Updated 2026-03-08 · Documentation reflects live architecture*
