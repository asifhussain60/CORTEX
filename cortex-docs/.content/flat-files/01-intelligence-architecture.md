# CORTEX Intelligence Architecture

---
title: CORTEX Intelligence — Brain Tiers, LENS Integration, Intelligence Matrix, and RCA Memory Engine
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/intelligence/ + cortex/lens/ + cortex/intelligence/cross_cutting/ + cortex/intelligence/learning/
consolidates: [00-getting-started-brain-tier-architecture, 00-getting-started-intelligence-matrix, 00-getting-started-cortex-intelligence]
order: 2
phases_covered: [Phase 83 URS, Phase 84 Stub Elimination, Phase 87 RCA Memory Engine]
---

> **The central idea:** CORTEX's intelligence mirrors biological cognition — a perception layer that reads the world, a reasoning layer that interprets it, and an action layer that responds. Every request passes through all three tiers before any code is written.

---

## Why a "Brain" Architecture?

Most development tools react to explicit instructions. CORTEX is designed to understand them.

A developer rarely says exactly what they need with perfect precision. They say "fix this", "make this faster", "add tests for the auth module". The Brain transforms that ambiguity into structured, safe, executable plans — learning from every repository it touches so that future requests are handled with greater confidence.

The three tiers are interdependent cognitive layers. Perception shapes reasoning, and reasoning shapes how action plans are assembled and validated.

---

## Where Intelligence Lives

All intelligence lives under one canonical location: `cortex/intelligence/`. This directory contains subdirectories for perception (pattern recognition and signature matching), reasoning (strategy selection and ranking), action (execution planning and rollback design), domain_brain (domain-specific business knowledge), knowledge (knowledge synthesis), learning (pattern capture, confidence updates, and the Unified Reinforcement Signal), lens (LENS integration bridge), infrastructure (detection and catalog integration), governance, documentation, crawling, quality assessment, observability, cross_cutting (the Intelligence Matrix), and wiring (intelligence wiring and discovery bridges).

The old `cortex_intelligence/` and `cortex_lens/` packages were dissolved. All imports use `cortex.intelligence.*`.

---

## The Three Cognitive Tiers

### Tier 1 — Perception: The Pattern Registry

The Perception tier maintains a catalogue of known signatures. When CORTEX analyses a repository, it scans file structure, imports, and naming conventions; matches detected signals against nine registered enterprise patterns (mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command); scores each match with a confidence value between 0.0 and 1.0; and reports matched fields, missing fields, and associated risk factors.

The key output is a PatternMatch — a detected match between repository signals and a registered pattern. The LENS feed provides raw data from the parallel analyzers (AST, Git, Security, and others) that Perception uses as input.

For a business leader, Perception automatically identifies which enterprise patterns a team is using — or should be using. When a new repository is onboarded, it gets a pattern confidence map within seconds. For a product owner, it surfaces which repositories follow which patterns and where attention is needed. For a developer, when they ask CORTEX to implement a feature, Perception scans the repo to understand the architecture first — if it detects a Django project, strategy selection already knows to recommend Django-specific patterns.

### Tier 2 — Reasoning: The Strategy Selector

The Reasoning tier takes Perception's output and filters strategies applicable to detected patterns, ranks them by historical success rate and context fit, considers risk factors flagged by Perception, and selects the highest-confidence strategy or multiple strategies for comparison.

A Strategy is a named approach such as "tdd-incremental", "refactor-extract-service", or "security-audit-first". Each has a historical success rate (0.0 to 1.0) updated after each execution. The output is a StrategyRecommendation — a ranked list of applicable strategies with confidence scores.

Reasoning tracks which approaches work best over time. It learns, for example, that TDD-incremental has a 94% success rate for a team's Django projects and recommends it automatically. When planning a large refactor, Reasoning provides data about which strategy has the best track record for similar projects.

### Tier 3 — Action: The Execution Planner

The Action tier converts the chosen strategy into a step-by-step ExecutionPlan. It decomposes the strategy into ordered steps, inserts TDD gates (CORE-008) at each step boundary, defines rollback points in case any step fails, sets validation checkpoints for governance enforcement, and estimates effort and risk for the overall plan.

Every step in the plan has a mandatory test-first checkpoint (RED → GREEN → REFACTOR), a state snapshot for safe recovery if the step fails, and governance enforcement checks mid-execution. This ensures that even complex multi-step operations maintain safety and reversibility throughout.

---

## The Complete Journey of a Request Through Intelligence

To illustrate how all three tiers work together, consider a request like "Add a password reset feature that sends an email with a time-limited token":

**Governance Gate** — Before anything else, CORTEX checks the request against 38 governance rules. It notices the request involves security (passwords, tokens), flags it for security review, and attaches a note that TDD is mandatory.

**Interaction** — The InteractionOrchestrator parses the request, identifies key concepts (password reset, email, time-limited token), assesses confidence (0.92), and shows a Definition of Ready summary to confirm understanding before work begins.

**Intent Routing** — The IntentRouter classifies this as IMPLEMENT (build something new) with high confidence, routing to TDDOrchestrator with LENS analysis and security review activated.

**Intelligence Gathering** — Three knowledge sources feed into one unified context. LENS scans the actual codebase and discovers existing services (UserService, EmailService, TokenService), their locations, and the architectural patterns in use. The Knowledge Engine loads best practices from the knowledge base covering security (cryptographically secure tokens, hash before storing, 15–30 minute expiry), architecture (follow existing service layer patterns), and testing (cover happy path, expired token, invalid token, already-used token, and rate limiting). Company Standards layer on team-specific rules that always win when they conflict with generic best practices.

**Execution** — If the risk score exceeds 0.4 or the change touches more than three files, a Challenge Gate presents alternatives with trade-offs. Once an approach is selected, the TDD cycle begins: RED (write failing tests covering all scenarios), GREEN (implement minimum code to pass), and REFACTOR (improve code while keeping tests green).

**Sweep Check** — CORE-064 ensures no partial work. If a weak hashing pattern is found, CORTEX scans the entire codebase for the same issue, builds a complete catalogue, fixes every instance, and blocks completion until the catalogue is exhausted.

---

## Intelligence Tiers — Speed vs Depth

Not every request needs the full intelligence treatment. CORTEX uses three speed tiers:

| Tier | Latency | Scope | When Used |
|------|---------|-------|-----------|
| Quick | Under 200ms | Cached rules only | Simple queries — "What is CORE-008?" |
| Targeted | Under 2 seconds | LENS scan plus relevant knowledge files | Building and fixing — "Add a password reset feature" |
| Full | Under 10 seconds | LENS plus Knowledge Graph plus Profiles plus deep analysis | Complex investigations — "Why do our auth tests fail intermittently?" |

The IntentRouter automatically picks the right tier based on the request. Simple questions get fast answers, complex builds get deep analysis, and investigations get the full treatment.

---

## The Intelligence Matrix

The Intelligence Matrix is CORTEX's neural wiring map — a structured cross-check of every intelligence capability against every operational capability, ensuring all subsystems are connected.

### What It Answers

For every possible intersection of an intelligence-providing subsystem (like LENS, Brain Tiers, or KnowledgeIndexer) and an intelligence-consuming system (like TDDOrchestrator, AuditFix pipeline, or MCP tools), the matrix answers: "Should these two capabilities be wired together — and if so, how?" Each cell carries a priority score (CRITICAL, HIGH, MEDIUM, LOW) aligned with the P0–P3 governance severity system.

### The Seven Dimensions

The matrix operates across seven capability dimensions: brain_tier (learned, adaptive, and scratch memory), lens (AST, semantic, and graph analysis), intelligence (orchestrated intelligence, synthesis, blind spot detection), toolkit (scanning, batch processing, adapters), workflow (documentation generation, audit-fix, TDD, sweep catalogue pipelines), response (template generation and formatting hooks), and governance (enforcement, vacuum, blind spot detection).

### Intelligence Capabilities (x-axis)

Fifteen intelligence-providing subsystems form the x-axis, including LENS Analysis, SynthesisEngine, DomainBrain, three Brain Tier memory levels (T1 Learned, T2 Adaptive, T3 Scratch), IntelligenceOrchestrator, ResponseTemplateGenerator, BlindSpotDetector, KnowledgeIndexer, HierarchicalScannerAdapter, KnowledgeIndexerDocGenBridge, IntelligenceWiringBridges, CortexBrainQuery (MCP), and FormatResponseHook.

### Operational Capabilities (y-axis)

Fifteen intelligence-consuming systems form the y-axis, including HierarchicalScanner, BatchProcessor, DomainAdapter, DocGenPlaybook, AuditFixPipeline, EnforcementOrchestrator, VacuumOrchestrator, MCPToolRegistry, SweepCatalogueOrchestrator, TDDOrchestrator, SynthesisEngineBridge, RetrievalOptimizerBridge, TDDStubGenerator, ResponseTemplateHook, and T1T2EnrichmentHooks.

**Phase 86 additions (PLANNED):** `DebuggerOrchestrator` (cells CC-021/IC-021) will be added as an intelligence consumer — enabling the matrix to query debugger capability, health, and readiness, and allowing debug insights to flow into the intelligence layer via OPJMixin, URS, and KnowledgeSynthesisEngine.

### Critical Wired Connections

The most important wiring pairs, all established as production architecture:

**LENS × HierarchicalScanner** — LENS needs file discovery as its foundation. Without the scanner feeding files to LENS, no analysis is possible.

**Brain Tiers × MCP** — Brain tier memories must be surfaced via MCP for IDE consumption. This connects the entire memory subsystem to the user interface.

**BlindSpotDetector × EnforcementOrchestrator** — Detected gaps must trigger governance violations. Without this wiring, blind spots become silent technical debt.

**KnowledgeIndexer × DocGenPlaybook** — Documentation generation draws from the canonical knowledge index. Without this wire, documentation drifts from the live implementation.

**ResponseTemplate × MCP** — All MCP tool results pass through response formatting before returning to the IDE, ensuring consistent rendering.

### Coverage Gate

A coverage gate (minimum 50%) is enforced in the AuditFix pipeline. If the proportion of wired cells drops below the threshold, the pipeline halts with a MatrixCoverageError — preventing deployment with an under-wired intelligence layer.

---

## The Knowledge Loop — How CORTEX Gets Smarter

CORTEX does not just execute and forget. Every request teaches it something. If a security pattern is flagged and fixed, that pattern gets stored so it is caught earlier next time. If a particular test structure works well for a service class, that pattern is suggested for similar future services. If a company-specific rule is applied, it is remembered and applied automatically going forward.

All learning is stored in the Knowledge Registry, organised by domain: architecture, security, testing, performance, migration, and operational patterns. The Unified Reinforcement Signal (URS) provides the feedback mechanism — orchestrators emit reinforcement signals after every operation, and these signals adjust pattern confidence scores over time. Patterns with high confidence and multiple rewards are promoted to top-tier knowledge. Patterns with low confidence and punishments are quarantined. Idle patterns decay gradually.

## The Knowledge Loop — How CORTEX Gets Smarter

CORTEX does not just execute and forget. Every request teaches it something. If a security pattern is flagged and fixed, that pattern gets stored so it is caught earlier next time. If a particular test structure works well for a service class, that pattern is suggested for similar future services. If a company-specific rule is applied, it is remembered and applied automatically going forward.

All learning is stored in the Knowledge Registry, organised by domain: architecture, security, testing, performance, migration, and operational patterns. The Unified Reinforcement Signal (URS) provides the feedback mechanism — orchestrators emit reinforcement signals after every operation, and these signals adjust pattern confidence scores over time. Patterns with high confidence and multiple rewards are promoted to top-tier knowledge. Patterns with low confidence and punishments are quarantined. Idle patterns decay gradually.

---

## RCA Memory Engine — Root Cause Analysis (Phase 87)

The RCA Memory Engine extends CORTEX's learning infrastructure from simple pattern capture into structured root-cause reasoning. It answers the question every engineering team asks but rarely answers systematically: "Why does the same class of mistake keep happening?"

### The Problem It Solves

Before Phase 87, CORTEX's OPJMixin captured `root_cause` as free-text — useful for reference but impossible to compare, cluster, or act upon automatically. A developer who repeated the same class of mistake (say, missing error boundaries in async chains) would get no advance warning. The root cause was recorded but never cross-referenced.

### Structured RCA Methodologies

The RCA Engine implements four proven industrial methodologies:

| Methodology | When To Use | Output |
|-------------|-------------|--------|
| **Five Whys** | Linear causal chains — most common failures | Ordered why→answer chain, root cause at depth ≥3 |
| **Fishbone (Ishikawa)** | Multi-category failures (People/Process/Technology/Data) | Category → contributing cause map |
| **Fault Tree** | Complex system failures with multiple contributing paths | AND/OR gate tree, probability-weighted |
| **Causal Chain** | Sequential dependency failures | Ordered event chain with time deltas |

### Prevention Gate

Once an RCA is recorded, the Prevention Gate intercepts future operations that match the same root cause signature:

- **Advisory mode (default):** Warns the developer — "This operation matches a known failure pattern (RCA-2026-001). Previous fix: check async error boundaries."
- **Blocking mode (≥3 P0 recurrences):** Halts execution — "This exact root cause class has caused 3 P0 failures. A structured review is required before proceeding."

### Recurrence Signatures

The RecurrenceSignatureEngine generates a canonical fingerprint for every RCA. When a new failure arrives, its signature is compared against all stored signatures. A match above 85% similarity triggers a recurrence alert with the full history of prior fixes and their effectiveness scores.

### Integration Points

The RCA Engine is purely additive — it extends existing infrastructure:

| Component | Extension |
|-----------|-----------|
| `OPJMixin` | Two new methods: `_opj_analyze_rca()` and `_opj_check_prevention_gate()` |
| `cortex_learning` MCP tool | New operation: `op="rca"` — runs structured analysis, returns RCA report inline |
| `CrossSessionPatternCache` | New tables: `rca_analyses`, `prevention_rules`, `recurrence_signatures`, `recurrence_incidents` |
| URS | RCA results emit reinforcement signals — P0 recurrences emit STRONG_PUNISHMENT |

### For Business Leaders

Every engineering team builds the same bugs twice, three times, a hundred times. RCA Memory is the institutional knowledge that says "we've been here before — here's why, here's what we did, and here's what to watch for." It transforms individual debugging sessions into organisation-wide learning that compounds over time.

---

*All intelligence module paths verified against live codebase · February 2026 · Phase 87 RCA Memory Engine planned*
