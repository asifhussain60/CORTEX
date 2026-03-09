# Orchestration — The Engine Room

---
title: Orchestration — How CORTEX Coordinates 330+ Specialised Engines
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-09
order: 5
---

> **The central idea:** CORTEX is not a single AI system. It is a coordinated network of 330+ specialised processing engines — each an expert at one category of engineering work — all coordinated through a central dispatcher that routes every request to the right expert in under 40 milliseconds. Think of it like a large hospital: when a patient arrives, the triage nurse (the router) instantly determines whether to send them to cardiology, orthopaedics, or radiology. Each department has deep expertise. The hospital works because every department follows the same protocols and communicates through a central system — never by shouting across the corridor.

---

## What an Orchestrator Is

An orchestrator is a specialised processing engine. Like a department in a well-run organisation, each orchestrator has deep expertise in one domain and communicates with other departments only through established, auditable channels.

Every orchestrator follows the same five-step lifecycle, regardless of its specialisation:

1. **Prepare** — Load configuration, establish connections, set up the working environment
2. **Govern** — Run the governance gate: check all relevant rules before any work begins
3. **Execute** — Do the actual work of the specialisation
4. **Validate** — Verify results against acceptance criteria
5. **Close** — Record the audit trail, clean up resources, emit completion signals

The governance step runs before execution on every orchestrator, every time. There is no shortcut. This is the structural mechanism that makes governance automatic rather than optional.

---

## The Architecture — Fourteen Domains

330+ orchestrators are organised across 14 specialised domains based on their role in the system.

### Core — The Command Layer (130+ orchestrators)

The core tier contains orchestrators responsible for coordination, routing, enforcement, and the central workflows. This is the intelligence hub of CORTEX — like the executive function of a brain, coordinating all the specialist regions.

| Orchestrator | What It Does |
|---|---|
| **Central Coordinator** | Receives every request, routes to the appropriate specialist, monitors execution, records the complete audit trail |
| **Request Classifier** | Classifies every incoming request into one of 30+ intent types in under 40 milliseconds |
| **Interaction Handler** | Understands the request in context of the current codebase before routing |
| **Development Engine** | Enforces the three-phase test-driven cycle on every build and fix |
| **Governance Enforcer** | Coordinates ten specialised agents that check different categories of rules |
| **Workflow Runner** | Reads structured workflow templates and executes them as typed step sequences |
| **Audit Orchestrator** | Coordinates the comprehensive nine-stage production readiness audit |
| **Conversation Manager** | Maintains multi-turn session state so context is preserved across interactions |
| **Complexity Triage Engine** | Scores every request on five CDR dimensions — clarity, context, scope, risk, and precedent — routing to the correct planning tier (SIMPLE/MODERATE/COMPLEX) in a single pass |
| **Autonomous Planning Engine** | CAPE: 11-component pipeline that converts complex requests into governed execution plans with dependency ordering (Kahn's algorithm), five analysis gates, seven-item machine-checkable completion checklists, and per-sub-phase stabilisation injection |

### Domain — The Specialist Layer (25+ orchestrators)

The domain tier contains orchestrators with deep expertise in specific engineering disciplines — like the specialised brain regions for language, spatial reasoning, and music.

| Orchestrator | What It Does |
|---|---|
| **Code Review Specialist** | Runs multi-pass code reviews across changed files: structural analysis, security audit, governance compliance, test-coverage gap detection, and style conformance — all surfaced inline with severity and fix suggestions |
| **Refactoring Specialist** | Performs semantic code improvements — extract methods, rename symbols, resolve duplication — across Python, TypeScript, and C# |
| **Planning Engine** | Decomposes complex requests into structured, executable plans with work items and acceptance criteria |
| **Enhanced Planner** | Advanced planning with return-on-investment scoring and wave-based delivery decomposition |
| **SDLC Workflow Engine** | Manages the complete software delivery lifecycle from requirements through release |
| **Dashboard Generator** | Produces interactive HTML dashboards with codebase metrics, quality scores, and architecture visualisations |
| **Domain Intelligence** | Applies domain-specific knowledge and governance to requests in specialised business verticals |
| **Service Decomposer** | Analyses monolithic codebases and produces structured decomposition plans |
| **Feedback Processor** | Captures structured user feedback — satisfaction signals, corrections, suggestions — and routes them into the Unified Reinforcement Signal for confidence adjustment |
| **Change Intelligence Analyst** | Discovers current-state processes via LENS, compares them against best-practice patterns, produces gap analyses with severity scores, evaluates ROI for proposed changes, and generates system capability inventories — purpose-built for Product Owner decision support |
| **Requirements Engineer** | Decomposes stakeholder intent into structured, testable requirements — business requirements, functional requirements, non-functional requirements, and acceptance criteria — grounded in LENS analysis of the actual codebase |
| **Knowledge Acquisition Orchestrator** | 6-stage auto-synthesis pipeline: detects knowledge gaps when LENS domain signal coverage drops below 80%, synthesises domain YAML, validates against a 7-rule schema, and registers in the knowledge index — integrates OPJ learning and URS reinforcement |
| **Cross-Repo Extractor** | 6-stage pipeline that extracts operational learnings from git history, classifies changes into 8 categories (NEW_CAPABILITY, BUG_FIX, GOVERNANCE, etc.), and scrubs all proprietary content through an 8-gate sanitisation system before output |

### Support — The Operations Layer (50+ orchestrators)

The support tier handles operational concerns — health monitoring, cleanup, onboarding, debugging, and the infrastructure that keeps everything running.

Key support orchestrators include the health monitor (checks all systems and reports status), the cleanup engine (removes accumulated documentation sprawl and stale files — protected by a Vacuum Recency Guard that excludes files modified within the last 7 days from deletion), the debugging pipeline (multi-strategy debugging for Python, TypeScript, C#, SQL, and REST APIs), the onboarding engine (analyses a new repository and produces a complete intelligence profile), the upgrade manager (handles CORTEX version updates and dependency resolution), the sync engine (one-way synchronisation between private and shared repositories with automatic privacy protection), and the Rollback Manager (records a git HEAD checkpoint before every sub-phase and restores to it on failure — emitting a MILD_PUNISHMENT signal to the learning loop so the failure informs future decisions).

### Health — System Wellness (25+ orchestrators)

A dedicated health domain monitors system wellness with 25+ orchestrators covering preflight checks, dependency validation, environment verification, and continuous health reporting.

### Intelligence — The Learning Layer (15+ orchestrators)

The intelligence tier powers CORTEX's learning capabilities including the RCA Memory Engine (4 methodologies), the Unified Reinforcement Signal, knowledge synthesis, and the PrincipleSelector for contextual wisdom injection.

### Git — The Version Control Layer (5 orchestrators)

Four dedicated orchestrators handle all interactions with version control: standard git operations (commit, branch, merge, diff), structured publishing (conventional commits, branch management), security sanitisation before commit (secret scanning, PII removal, branch hygiene), and pre-commit governance enforcement (blocking non-compliant changes at the commit boundary).

---

## The 30+ Intent Types — Speaking CORTEX's Language

Every request to CORTEX is classified into one of 30+ intent types. This classification happens in under 40 milliseconds and determines which specialist handles the request, which workflow template applies, and which governance rules are activated. It works like a skilled receptionist who hears "I need help with my knee" and immediately knows to book an orthopaedic appointment — not a dental one.

| Category | Intents |
|---|---|
| **Building** | Implement (new feature), Fix (bug repair), Test (test creation) |
| **Understanding** | Analyse (code examination), Investigate (root cause research), Query (information retrieval) |
| **Improving** | Refactor (code quality), Vacuum (cleanup), Upgrade (dependency updates) |
| **Reviewing** | Review (multi-pass code review), Feedback (structured user feedback capture) |
| **Optimising** | Optimize (multi-file content optimization and compression) |
| **Planning** | Plan (structured planning), Design (architecture decisions) |
| **Auditing** | Audit (compliance check), Health (system status), Security (vulnerability scan) |
| **Learning** | Digest (content ingestion), Train (knowledge building), Distill (conversation → executable prompt) |
| **Decision Support** | Change Intelligence (process discovery, gap analysis, ROI evaluation), Requirements (structured requirements generation from stakeholder intent), PO Training (training documentation for product owners) |
| **Collaborating** | Challenge (alternatives analysis), Rephrase (request clarification) |
| **Operating** | Onboard (repository setup), Sync (repository synchronisation), Publish (release), Rollback (undo), Introduce (role-based onboarding) |
| **Visualising** | Dashboard (reporting), Discover (exploration) |
| **Coordinating** | Workflow (template execution), Compose (pipeline building), Document (documentation) |

When a request falls below the confidence threshold for automatic classification, CORTEX asks one targeted clarifying question rather than proceeding with uncertainty. If no intent can be identified, the request is rephrased collaboratively before any action is taken.

---

## Request Enrichment — Context Before Classification

Before any orchestrator sees a request, a silent enrichment step adds context the developer didn't explicitly provide. The enrichment layer injects relevant governance rules, a risk assessment of the proposed change, design principle considerations, and flags for high-risk operations that should trigger a challenge review.

The developer sees none of this. The enrichment happens automatically and produces a fully contextualised request that the routing and specialist layers can act on with complete information.

---

## Cross-Orchestrator Communication — No Direct Calls

Orchestrators never communicate directly with each other. All communication flows through the central coordinator. This architectural constraint has three important consequences:

**Full auditability** — every orchestrator interaction passes through a single logging point, producing a complete record of which specialists were involved in every decision.

**Governance between handoffs** — governance gates run not just at the start of a request, but at each transition between orchestrators. A governance check passed at the beginning doesn't mean a downstream operation can proceed unchecked.

**No circular dependencies** — because communication is always mediated, it is structurally impossible for two orchestrators to create a dependency loop.

---

## Workflow Templates — Codified Best Practice

Many operations in CORTEX follow structured templates stored as configuration files in a version-controlled registry. Think of these like recipes in a professional kitchen: each recipe defines the ingredients, the sequence of steps, the quality checks between steps, and the criteria for "done." The chef (orchestrator) follows the recipe; the recipe ensures consistency regardless of who is cooking.

90+ workflow templates span 17 categories, covering the complete development lifecycle from requirements analysis through production release. When a request matches a known workflow, CORTEX selects the appropriate template automatically based on the request intent and the technology stack detected by the code intelligence layer.

Templates are composed from atomic building blocks — reusable single-responsibility steps that handle specific tasks like running an analysis scan, applying a governance check, opening a sweep catalogue, or recording an audit trace. Complex workflows are assembled from these building blocks, ensuring consistency across all operations while keeping each step independently testable.

### The Three-Tier Template Hierarchy

Workflow templates are organised into three tiers that mirror the granularity of operations.

**Primitives** are atomic, reusable steps — the smallest units of work. A primitive might check a single governance rule, record an audit trace, create a rollback checkpoint, or emit a completion signal. Primitives are never modified for specific use cases; they are used as-is across all workflows.

**Mode Workflows** compose primitives into complete sequences for a specific operation type. The implementation workflow, the refactoring workflow, the audit workflow — each is a distinct template that assembles the right primitives in the right order with the right governance gates between steps.

**Composite Pipelines** coordinate multiple mode workflows into complex, multi-phase operations. The full production audit, for example, sequences nine distinct phases — each its own workflow — into a single coordinated pipeline with convergence guarantees.

### Dynamic Composition — Templates Built on the Fly

For operations that don't match any pre-existing template, CORTEX includes a workflow composer that assembles templates dynamically from validated primitives. The composer selects the appropriate building blocks based on the request intent, the technology stack, and the governance constraints, then produces a purpose-built workflow that follows the same structural guarantees as any pre-defined template.

This means teams are not limited to the workflows that ship with CORTEX. New workflow patterns emerge naturally as the composer discovers effective primitive combinations — and successful compositions can be promoted to permanent templates for future reuse.

---

## Real-Time Visibility — Breadcrumbs and Timelines

Every orchestrator operation surfaces a routing breadcrumb showing which specialists are involved and in what sequence. For multi-step operations, a collapsible timeline shows how long each step took. For the largest operations — full audits, complete lifecycle workflows — a phase roadmap appears at the start and updates as stages complete.

This visibility is structural. It is generated by a dedicated rendering component that every orchestrator uses. The format is consistent across all operations, so developers quickly build intuition about what each breadcrumb pattern means.

---

*Orchestrator count verified against live codebase (330+) · Intent routing verified against live IntentRouter implementation (30+ intent types) · Last verified: 2026-03-09*
