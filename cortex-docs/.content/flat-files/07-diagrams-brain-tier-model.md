# Brain Tier Model

---
title: Brain Tier Intelligence Model
type: diagram
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/intelligence/ (perception/, reasoning/, action/)
order: 9
---

## Three-Tier Intelligence Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  TIER 3: ACTION                                             │
│  cortex/intelligence/action/                                │
│                                                             │
│  "Motor Cortex" — Executes decisions                        │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Code Gen  │  │ Test Gen     │  │ Refactoring Exec.    │  │
│  │ (write)   │  │ (test first) │  │ (transform)          │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Reasoned plan + context                          │
│  Produces: Code, tests, transformations                     │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │ plans & decisions
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                                                             │
│  TIER 2: REASONING                                          │
│  cortex/intelligence/reasoning/                             │
│                                                             │
│  "Prefrontal Cortex" — Analyzes, plans, decides             │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Intent    │  │ Risk         │  │ Strategy             │  │
│  │ Analysis  │  │ Assessment   │  │ Selection            │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Structured perceptions from Tier 1               │
│  Produces: Plans, strategies, routing decisions             │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │ structured perceptions
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                                                             │
│  TIER 1: PERCEPTION                                         │
│  cortex/intelligence/perception/                            │
│                                                             │
│  "Sensory Cortex" — Observes, parses, classifies            │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LENS      │  │ Code         │  │ Natural Language     │  │
│  │ Analysis  │  │ Parsing      │  │ Understanding        │  │
│  │ (8 analyz)│  │ (AST)        │  │ (intent)             │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Raw input (code, text, requests)                 │
│  Produces: Structured observations                          │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │
                    RAW INPUT
              (code, text, requests)
```

## Intelligence Subsystems

```
cortex/intelligence/
├── perception/       ← Tier 1: Observe & parse
├── reasoning/        ← Tier 2: Analyze & plan
├── action/           ← Tier 3: Execute & transform
├── domain_brain/     ← Domain-specific knowledge
├── learning/         ← Learning from past executions
├── knowledge/        ← Knowledge base management
├── lens/             ← LENS integration layer
├── infrastructure/   ← Intelligence infrastructure
├── governance/       ← Intelligence governance
├── documentation/    ← Documentation intelligence
├── crawler/          ← Code crawling & indexing
├── quality/          ← Quality assessment
├── observability/    ← Intelligence observability
└── wiring/           ← Cross-tier integration
```

## Learning Loop

```
┌────────────────────────────────────────────────┐
│                                                │
│  1. PERCEIVE → Code input analyzed by LENS     │
│                    │                           │
│  2. REASON  → IntentRouter classifies,         │
│                TDDOrchestrator plans            │
│                    │                           │
│  3. ACT     → Code generated, tests written    │
│                    │                           │
│  4. LEARN   → Outcome recorded in AuditDB      │
│                    │                           │
│  5. ADAPT   → Future perceptions enriched      │
│                by past outcomes                │
│                    │                           │
│  └────────────────┘ (continuous loop)          │
│                                                │
└────────────────────────────────────────────────┘
```

## Brain Analogy Summary

| Tier | Brain Region | Function | CORTEX Module |
|------|-------------|----------|---------------|
| Perception | Sensory cortex | See, hear, feel | `cortex/intelligence/perception/` |
| Reasoning | Prefrontal cortex | Think, plan, decide | `cortex/intelligence/reasoning/` |
| Action | Motor cortex | Move, build, execute | `cortex/intelligence/action/` |
| Learning | Hippocampus | Remember, adapt | `cortex/intelligence/learning/` |
| Knowledge | Long-term memory | Know, recall | `cortex/intelligence/knowledge/` |
| Domain | Specialized areas | Expert knowledge | `cortex/intelligence/domain_brain/` |

---

*Verified against `cortex/intelligence/` directory structure · 25 February 2026*
