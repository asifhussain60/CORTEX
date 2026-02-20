# Brain Tier Architecture

---
title: CORTEX Brain Tier — 3-Layer Intelligence Explained
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-18
source_of_truth: cortex_intelligence/perception/ + cortex_intelligence/reasoning/ + cortex_intelligence/action/
related: 00-getting-started/04-brain-tier-architecture.md (canonical — brain-architecture.md removed as duplicate)
order: 4
---

> **The central idea:** CORTEX's Brain mirrors the structure of biological cognition — a perception layer that reads the world, a reasoning layer that interprets it, and an action layer that responds to it. Every request CORTEX handles passes through all three tiers before any code is written.

---

## Why a "Brain" Architecture?

Most development tools react to explicit instructions. CORTEX is designed to *understand* them.

A developer rarely says exactly what they need with perfect precision. They say "fix this", "make this faster", "add tests for the auth module". The Brain tier transforms that ambiguity into structured, safe, executable plans — learning from every repository it touches so that future requests are handled with greater confidence.

The three tiers are not sequential stages that run one-at-a-time and hand off a result. They are **interdependent cognitive layers** — perception shapes reasoning, and reasoning shapes how action plans are assembled and validated.

---

## The Three Tiers at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│                    🧠 CORTEX BRAIN ARCHITECTURE                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 1 — PERCEPTION  (Pattern Registry)                   │  │
│  │  "What is actually happening in this repository?"          │  │
│  │                                                            │  │
│  │  Scans repository signatures → produces PatternMatch       │  │
│  │  Module: cortex_intelligence/perception/pattern_registry   │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │  confident pattern matches          │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 2 — REASONING  (Strategy Selector)                   │  │
│  │  "Given these patterns, what is the best approach?"        │  │
│  │                                                            │  │
│  │  Evaluates strategies → produces StrategyRecommendation    │  │
│  │  Module: cortex_intelligence/reasoning/strategy_selector   │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │  ranked strategy list               │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TIER 3 — ACTION  (Execution Planner)                      │  │
│  │  "How do we execute this step-by-step, safely?"            │  │
│  │                                                            │  │
│  │  Builds execution plan → produces ExecutionPlan            │  │
│  │  Module: cortex_intelligence/action/execution_planner      │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tier 1 — Perception: The Pattern Registry

### The Analogy

Think of the brain's visual cortex. It doesn't "see" a chair — it detects edges, angles, and surfaces that it recognises as the *signature* of a chair. CORTEX's Perception layer works identically: it detects file patterns, import structures, naming conventions, and framework signatures, then matches them against patterns learned from previous repositories.

### What It Does

The **Pattern Registry** (`cortex_intelligence/perception/pattern_registry.py`) maintains a catalogue of known signatures. When CORTEX analyses a repository, the Perception tier:

1. **Scans** file structure, imports, and naming conventions
2. **Matches** detected signals against registered pattern signatures
3. **Scores** each match with a confidence value (0.0–1.0)
4. **Reports** matched fields, missing fields, and associated risk factors

### Key Concepts

| Concept | Description |
|---------|-------------|
| `RegisteredPattern` | A known pattern with a signature, context, associated strategies, risk factors, and historical success rate |
| `PatternMatch` | The result of scanning — which pattern was found, at what confidence, and which signature fields matched |
| `signature` | The detection rules: expected file names, import patterns, directory layouts |
| `success_rate` | How reliably this pattern's associated strategies have worked in the past (0.0–1.0) |
| `confidence` | How strongly the current repo matches this pattern's signature |

### Example

A repository with `manage.py`, `settings.py`, and Django imports in requirements yields a `PatternMatch` for the `django-web-application` pattern at confidence `0.92`. The Perception tier then forwards this — along with the list of matched and missing fields — to Reasoning.

---

## Tier 2 — Reasoning: The Strategy Selector

### The Analogy

Once the sensory cortex identifies a chair, the prefrontal cortex decides *what to do about it* — sit down, move it, inspect it for damage. The Reasoning tier plays this role: given a set of confident pattern matches, it selects the strategies most likely to succeed.

### What It Does

The **Strategy Selector** (`cortex_intelligence/reasoning/strategy_selector.py`) takes `PatternMatch` results from Perception and produces a `StrategyRecommendation`:

1. **Evaluates** which registered strategies apply to the detected patterns
2. **Weighs** each candidate strategy by its historical success rate and current context
3. **Ranks** strategies by confidence and expected impact
4. **Flags** risk factors that should influence execution

Reasoning doesn't just pick the top-rated strategy blindly. It compares alternatives and produces a ranked list — the Action layer uses this ranking to decide the execution sequence and fallback options.

### Key Concepts

| Concept | Description |
|---------|-------------|
| Strategy | A named approach: e.g., "tdd-incremental", "refactor-extract-service", "security-audit-first" |
| `StrategyRecommendation` | Ranked list of applicable strategies with associated confidence scores |
| Context weighting | Strategies are re-scored based on current project context (language, framework, team patterns) |
| Risk flags | Known challenges surfaced from pattern `risk_factors` so the Action layer can include mitigations |

### Holistic Validation Gate

Before passing recommendations to Action, Reasoning triggers the **Holistic Validation Gate** (CORE-048). This gate:

- Checks for dependency graph conflicts
- Scores regression risk (0.0–1.0)
- Detects architecture drift
- Produces the Mandatory Challenge for high-risk changes

This is why CORTEX sometimes presents alternatives — Reasoning discovered that a simpler or safer approach exists.

---

## Tier 3 — Action: The Execution Planner

### The Analogy

The motor cortex doesn't just "decide to sit" — it orchestrates dozens of muscles in a precise sequence, with balance checks and correction loops throughout. CORTEX's Action tier does the same for code: it breaks the chosen strategy into discrete, ordered steps with validation gates, rollback points, and test verification at every stage.

### What It Does

The **Execution Planner** (`cortex_intelligence/action/execution_planner.py`) converts the `StrategyRecommendation` into an `ExecutionPlan`:

1. **Decomposes** the strategy into ordered, atomic steps
2. **Inserts** TDD gates — tests must be written before implementation code (CORE-008)
3. **Defines** validation checks at each step boundary
4. **Attaches** rollback procedures for every step that mutates state
5. **Assigns** checkpoints for long-running operations (persisted to SQLite)

### Key Concepts

| Concept | Description |
|---------|-------------|
| `ExecutionPlan` | Ordered list of steps, each with inputs, expected outputs, validation rules, and rollback |
| TDD Gate | A mandatory checkpoint: RED (failing test) must exist before GREEN (implementation) begins |
| Checkpoint | A saved state snapshot allowing recovery if execution is interrupted |
| Rollback | The inverse operation for each step, applied automatically on critical violations |

### TDD Enforcement Inside Action

The Action tier enforces the RED → GREEN → REFACTOR cycle at the plan-generation level. It is not possible for an `ExecutionPlan` produced by this tier to place implementation steps before their corresponding test steps. This is structural, not advisory.

```
For each feature unit in the plan:
  Step N:   Write failing test           [RED]
  Step N+1: Write minimal implementation [GREEN]
  Step N+2: Refactor + verify green      [REFACTOR]
  Gate:     Governance check before next unit
```

---

## How the Tiers Connect to the Rest of CORTEX

The Brain tiers do not operate in isolation. They sit at the centre of CORTEX's processing pipeline and interact with every other major subsystem:

```
                        ┌─────────────────┐
                        │   LENS Engine   │
                        │  (8 analyzers)  │
                        └────────┬────────┘
                                 │ LENSContext
                                 ▼
Request ──▶ Intent Router ──▶ PERCEPTION ──▶ REASONING ──▶ ACTION
                │                                              │
                │                                              ▼
                │                                    Orchestrator Dispatch
                │                                    (TDD / Refactor / Plan)
                ▼                                              │
           Governance Gate ◀──────────────────────────────────┘
           (7 agents, 59 rules)
                │
                ▼
           Audit Trail (Git-backed, immutable)
```

| Brain Tier | Receives From | Sends To |
|------------|--------------|----------|
| Perception | LENS `LENSContext`, repository file scan | Reasoning (`PatternMatch[]`) |
| Reasoning | Perception matches, Knowledge Base | Action (`StrategyRecommendation`) + Holistic Validation Gate |
| Action | Reasoning recommendations | Orchestrators (TDD, Refactor, Plan) + Governance Layer |

---

## How the Brain Learns

The Brain doesn't reset between projects. Every execution:

- **Updates** `success_rate` on matched patterns (rolling average)
- **Captures** new signatures if a novel pattern is encountered with sufficient confidence (≥0.75)
- **Adjusts** strategy rankings based on observed outcomes

This learning feeds the **Intelligence Layer** (LENS + Pattern Learner), which maintains a 48-hour git history window to improve accuracy continuously. The result: a repository onboarded today will be analysed faster and more accurately next week.

---

## Brain Tier vs. Other Cognitive Layers

New readers often ask how the Brain tier relates to LENS and the Intelligence Layer. Here is the distinction:

| Layer | Role | Analogy |
|-------|------|---------|
| **LENS** | Multi-sensor code scanning (AST, Git, Security, etc.) | Sensory organs gathering raw data |
| **Brain — Perception** | Pattern recognition against known signatures | Visual/auditory cortex identifying objects |
| **Brain — Reasoning** | Strategy selection and risk assessment | Prefrontal cortex making decisions |
| **Brain — Action** | Execution planning with TDD gates and rollback | Motor cortex orchestrating precise sequences |
| **Intelligence Layer** | Learning from past outcomes, reducing false positives | Neuroplasticity — the brain rewiring through experience |

LENS feeds raw intelligence *into* Perception. The Brain tiers produce plans that orchestrators *execute*. The Intelligence Layer improves the quality of all three over time.

---

## Reading Path

| Next question | Go to |
|---------------|-------|
| How does LENS produce the data Perception uses? | `02-lens/01-overview.md` |
| What orchestrators does Action dispatch to? | `03-orchestration/01-overview.md` |
| What governance rules does Reasoning trigger? | `01-capabilities/governance-compliance.md` |
| How does the Intelligence Layer learn? | `01-capabilities/intelligence-layer.md` |
| Full technical specification | `00-getting-started/04-brain-tier-architecture.md` |

---

*CORTEX  · February 2026 · Source of truth: `cortex_intelligence/perception/` · `cortex_intelligence/reasoning/` · `cortex_intelligence/action/`*
