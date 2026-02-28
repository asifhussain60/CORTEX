# Brain Tier Architecture

---```
cortex/intelligence/
├── perception/          Pattern recognition, signature matching
├── reasoning/           Strategy selection, ranking
├── action/              Execution planning, rollback design
├── domain_brain/        Domain-specific business knowledge repository
├── knowledge/           Knowledge synthesis (SynthesisEngine, KnowledgeIndexer)
├── learning/            Pattern capture, confidence updates
├── lens/                LENS integration bridge
├── infrastructure/      InfrastructureDetector, catalog integration
├── governance/          Governance integration
├── documentation/       Documentation intelligence
├── crawler/             Repository crawling
├── quality/             Quality assessment
├── observability/       Intelligence metrics
├── cross_cutting/       Intelligence Matrix — IntelligenceMatrixBuilder
└── wiring/              Intelligence wiring and discovery bridges
```

**Note:** `cortex/core/` was flattened to canonical subdirs — dissolving redundant nested packages into `cortex/core/common/`. All brain-related logic that was in `cortex/core/intelligence/` moved to `cortex/intelligence/`. The old `cortex_intelligence/` and `cortex_lens/` packages were dissolved. All imports use `cortex.intelligence.*`.n — 3-Tier Intelligence Architecture
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-28
source_of_truth: cortex/intelligence/provider.py + cortex/intelligence/knowledge/
order: 4
---

> **The central idea:** CORTEX's intelligence mirrors biological cognition — a perception layer that reads the world, a reasoning layer that interprets it, and an action layer that responds to it. Every request passes through all three tiers before any code is written.

---

## Why a "Brain" Architecture?

Most development tools react to explicit instructions. CORTEX is designed to *understand* them.

A developer rarely says exactly what they need with perfect precision. They say "fix this", "make this faster", "add tests for the auth module". The Brain transforms that ambiguity into structured, safe, executable plans — learning from every repository it touches so that future requests are handled with greater confidence.

The three tiers are **interdependent cognitive layers** — perception shapes reasoning, and reasoning shapes how action plans are assembled and validated.

---

## Where It Lives (Post-Refactor)

After the 12-phase Cohesive Brain Refactor, all intelligence lives under **one canonical location**:

```
cortex/intelligence/
├── perception/          Pattern recognition, signature matching
├── reasoning/           Strategy selection, ranking
├── action/              Execution planning, rollback design
├── domain_brain/        Domain-specific intelligence (business verticals)
├── knowledge/           Knowledge synthesis
├── learning/            Pattern capture, confidence updates
├── lens/                LENS integration bridge
├── infrastructure/      InfrastructureDetector, catalog integration
├── governance/          Governance integration
├── documentation/       Documentation intelligence
├── crawler/             Repository crawling
├── quality/             Quality assessment
├── observability/       Intelligence metrics
└── wiring/              Intelligence wiring and discovery
```

**Note:** The old `cortex_intelligence/` and `cortex_lens/` packages were dissolved in Phases 03–04. All imports use `cortex.intelligence.*`.

---

## The Three Tiers at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│                    🧠 CORTEX BRAIN ARCHITECTURE                   │
│                    cortex/intelligence/                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 1 — PERCEPTION  (Pattern Registry)                   │  │
│  │  "What is actually happening in this repository?"          │  │
│  │                                                            │  │
│  │  Scans repository signatures → produces PatternMatch       │  │
│  │  Module: cortex/intelligence/perception/                   │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │  confident pattern matches          │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 2 — REASONING  (Strategy Selector)                   │  │
│  │  "Given these patterns, what is the best approach?"        │  │
│  │                                                            │  │
│  │  Evaluates strategies → produces StrategyRecommendation    │  │
│  │  Module: cortex/intelligence/reasoning/                    │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │  ranked strategy list               │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 3 — ACTION  (Execution Planner)                      │  │
│  │  "How do we execute this step-by-step, safely?"            │  │
│  │                                                            │  │
│  │  Builds execution plan → produces ExecutionPlan            │  │
│  │  Module: cortex/intelligence/action/                       │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tier 1 — Perception: The Pattern Registry

### The Analogy

Think of the brain's visual cortex. It doesn't "see" a chair — it detects edges, angles, and surfaces that it recognises as the *signature* of a chair. CORTEX's Perception layer works identically: it detects file patterns, import structures, naming conventions, and framework signatures, then matches them against patterns learned from previous repositories.

### What It Does

The Perception tier (`cortex/intelligence/perception/`) maintains a catalogue of known signatures. When CORTEX analyses a repository:

1. **Scans** file structure, imports, and naming conventions
2. **Matches** detected signals against 9 registered enterprise patterns
3. **Scores** each match with a confidence value (0.0–1.0)
4. **Reports** matched fields, missing fields, and associated risk factors

### Key Concepts

| Concept | Description |
|---------|-------------|
| **PatternMatch** | A detected match between repository signals and a registered pattern |
| **Confidence Score** | 0.0–1.0 value indicating match quality |
| **Pattern Registry** | 9 enterprise patterns: mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command |
| **LENS Feed** | Raw data from 8 LENS analyzers (AST, Git, Security, etc.) |

### Practical Examples

**Business Leader:** "Perception automatically identifies which enterprise patterns your team is using — or should be using. When a new repo is onboarded, it gets a pattern confidence map within seconds."

**Product Owner:** "I can see which repos follow the mediator pattern vs the repository pattern. Perception scores tell me which codebases are well-structured and which need attention."

**Developer:** "When I ask CORTEX to implement a feature, Perception first scans my repo to understand the architecture. If it detects a Django project, the strategy selection already knows to recommend Django-specific patterns."

---

## Tier 2 — Reasoning: The Strategy Selector

### The Analogy

The prefrontal cortex weighs options, considers consequences, and makes decisions. CORTEX's Reasoning layer does the same: given the patterns detected by Perception, it evaluates available strategies, ranks them by historical success rate, and selects the best approach.

### What It Does

The Reasoning tier (`cortex/intelligence/reasoning/`) takes Perception's output and:

1. **Filters** strategies applicable to detected patterns
2. **Ranks** strategies by historical success rate and context fit
3. **Considers** risk factors flagged by Perception
4. **Selects** the highest-confidence strategy (or multiple for comparison)

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Strategy** | A named approach: `tdd-incremental`, `refactor-extract-service`, `security-audit-first` |
| **Success Rate** | Historical effectiveness (0.0–1.0) — updated after each execution |
| **StrategyRecommendation** | Ranked list of applicable strategies with confidence scores |

### Practical Examples

**Business Leader:** "Reasoning tracks which approaches work best. Over time, the system learns that TDD-incremental has a 94% success rate for your team's Django projects — and recommends it automatically."

**Product Owner:** "When planning a large refactor, Reasoning tells me which strategy has the best track record for similar projects. I don't guess — the system provides data."

**Developer:** "Reasoning picked `refactor-extract-service` over `refactor-inline` because my repo's pattern registry shows a microservices architecture. It chose based on evidence, not assumption."

---

## Tier 3 — Action: The Execution Planner

### The Analogy

The motor cortex converts decisions into precise muscle movements. CORTEX's Action layer converts the chosen strategy into a step-by-step execution plan — complete with TDD gates, rollback points, and validation checkpoints.

### What It Does

The Action tier (`cortex/intelligence/action/`) builds an `ExecutionPlan`:

1. **Decomposes** the strategy into ordered steps
2. **Inserts** TDD gates (CORE-008) at each step boundary
3. **Defines** rollback points in case any step fails
4. **Sets** validation checkpoints (governance gate checks)
5. **Estimates** effort and risk for the overall plan

### Key Concepts

| Concept | Description |
|---------|-------------|
| **ExecutionPlan** | Ordered list of steps with gates, rollback, and validation |
| **TDD Gate** | Mandatory test-first checkpoint (RED → GREEN → REFACTOR) |
| **Rollback Point** | State snapshot for safe recovery if a step fails |
| **Validation Checkpoint** | Governance enforcement check mid-execution |

### Practical Examples

**Business Leader:** "Every plan has built-in rollback. If step 3 of a 5-step refactor fails, CORTEX reverts to the state after step 2. No partial, broken implementations."

**Product Owner:** "The execution plan shows me exactly what will happen — step count, estimated effort, risk level. I can approve or adjust before any code is written."

**Developer:** "Action generated a 4-step plan: (1) write auth middleware test, (2) implement middleware, (3) write integration test, (4) update route configuration. Each step has a TDD gate. If step 2 fails the test from step 1, it loops back to RED."

---

## How the Tiers Connect

```
[LENS 9-Analyzer Output]
        │
        ▼
[UnifiedIntelligenceProvider]  ← cortex/intelligence/provider.py
     quick() / targeted() / full()
        │
        ├── company/domains/*.yaml (CompanyDomainLoader, 5-min TTL)
        ├── knowledge-base/profiles/{domain}.yaml (tag-matched)
        ├── ADO sprint context (ADO_ORG_URL guard, ADOContextMapper)
        └── KG entity indexing (KnowledgeIndexer, idempotent)
        │
        ▼
[KnowledgeSynthesisEngine.synthesize_unified_context()]
        │
        ├── architecture patterns (cortex-registry/patterns/*.yaml)
        ├── security rules (knowledge-base/security/)
        └── testing standards (CORE-008, CORE-064)
        │
        ▼
[UnifiedIntelligenceContext] → MasterOrchestrator
        │
        ▼
[Orchestrator Execution] ── RED → GREEN → REFACTOR
        │
        ▼
[Governance Validation] ── CORE rules, EnforcementOrchestrator
        │
        ▼
[Learning Update] ── success rates updated for next time
```

## UnifiedIntelligenceProvider — The Intelligence Hub

`cortex/intelligence/provider.py` is the canonical entry point post-Phase-18. It replaces the old three-package split (`cortex_intelligence/`, `cortex_lens/`, `cortex.brain/` — all dissolved).

| Tier | Method | Latency | Company Knowledge |
|------|--------|---------|------------------|
| Quick | `provider.quick(intent)` | <200ms | ✅ (cached) |
| Targeted | `provider.targeted(intent, file_path)` | <2s | ✅ + domain profile |
| Full | `provider.full(intent, repo_name)` | <10s | ✅ + ADO + KG |

Company domain rules take **precedence over all CORTEX defaults** (`CompanyKnowledge.precedence = "OVERRIDE"`). This means your `cortex-registry/company/domains/*.yaml` files are the highest-authority knowledge source in the entire pipeline.

---

## The Learning Loop

After every execution, the intelligence system updates:
- **Pattern confidence** — did the detected pattern help or mislead?
- **Strategy success rate** — did the selected strategy succeed?
- **Domain knowledge** — new patterns discovered in this repository

This feedback loop means CORTEX improves with every project it touches. The `cortex/intelligence/learning/` module captures these updates and feeds them back into the Pattern Registry.

---

*All module paths verified against live codebase*
