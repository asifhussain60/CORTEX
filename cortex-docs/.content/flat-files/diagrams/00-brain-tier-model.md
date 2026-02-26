# Brain Tier Intelligence — Perception → Reasoning → Action
# The three-tier cognitive model and learning feedback loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BRAIN TIER INTELLIGENCE MODEL                           │
│                     cortex/intelligence/                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ TIER 3: ACTION — "Motor Cortex"                                     │    │
│  │ cortex/intelligence/action/                                         │    │
│  │                                                                     │    │
│  │  Input: Reasoned execution plan from Tier 2                         │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │    │
│  │  │ Code Generation │  │ Test Generation │  │ Refactoring     │     │    │
│  │  │                 │  │                 │  │ Execution       │     │    │
│  │  │ Write new code  │  │ TDD test-first  │  │ Apply semantic  │     │    │
│  │  │ based on plan   │  │ (CORE-008)      │  │ transformations │     │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │    │
│  │                                                                     │    │
│  │  Features:                                                          │    │
│  │  • Step-by-step execution with TDD gates                           │    │
│  │  • Rollback points at every step boundary                          │    │
│  │  • Governance enforcement mid-execution                             │    │
│  │  • Effort and risk estimation                                       │    │
│  └───────────────────────────────┬─────────────────────────────────────┘    │
│                                  ▲                                          │
│                                  │ plans & decisions                        │
│                                  │                                          │
│  ┌───────────────────────────────┴─────────────────────────────────────┐    │
│  │ TIER 2: REASONING — "Prefrontal Cortex"                             │    │
│  │ cortex/intelligence/reasoning/                                      │    │
│  │                                                                     │    │
│  │  Input: Structured perceptions from Tier 1                          │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │    │
│  │  │ Intent Analysis │  │ Risk Assessment │  │ Strategy Select │     │    │
│  │  │                 │  │                 │  │                 │     │    │
│  │  │ "What does the  │  │ "What could go  │  │ "What approach  │     │    │
│  │  │  user need?"    │  │  wrong?"        │  │  works best?"   │     │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │    │
│  │                                                                     │    │
│  │  Strategy Selection:                                                │    │
│  │  • Filters strategies applicable to detected patterns               │    │
│  │  • Ranks by historical success rate (0.0–1.0)                      │    │
│  │  • Considers risk factors from Perception                           │    │
│  │  • Outputs: StrategyRecommendation (ranked list)                   │    │
│  └───────────────────────────────┬─────────────────────────────────────┘    │
│                                  ▲                                          │
│                                  │ structured perceptions                   │
│                                  │                                          │
│  ┌───────────────────────────────┴─────────────────────────────────────┐    │
│  │ TIER 1: PERCEPTION — "Sensory Cortex"                               │    │
│  │ cortex/intelligence/perception/                                     │    │
│  │                                                                     │    │
│  │  Input: Raw input (code, text, requests) + LENS data                │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │    │
│  │  │ LENS Feed       │  │ Code Parsing    │  │ NL Understanding│     │    │
│  │  │ (10 analyzers)  │  │ (AST)           │  │ (intent)        │     │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │    │
│  │                                                                     │    │
│  │  Pattern Recognition:                                               │    │
│  │  • Scans against 9 registered enterprise patterns                  │    │
│  │  • Scores each match: confidence 0.0–1.0                           │    │
│  │  • Reports matched fields, missing fields, risk factors             │    │
│  │  • Output: PatternMatch objects                                     │    │
│  └───────────────────────────────┬─────────────────────────────────────┘    │
│                                  ▲                                          │
│                                  │                                          │
│                            RAW INPUT                                        │
│                      (code, text, requests)                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LEARNING LOOP (Unified Reinforcement Signal)                        │    │
│  │ cortex/intelligence/learning/                                       │    │
│  │                                                                     │    │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │    │
│  │  │PERCEIVE │───→│ REASON  │───→│   ACT   │───→│  LEARN  │──┐       │    │
│  │  │         │    │         │    │         │    │         │  │       │    │
│  │  │ LENS    │    │ Router  │    │ Code    │    │ Record  │  │       │    │
│  │  │ scans   │    │ plans   │    │ written │    │ outcome │  │       │    │
│  │  └─────────┘    └─────────┘    └─────────┘    └────┬────┘  │       │    │
│  │                                                    │       │       │    │
│  │                                               ┌────┴────┐  │       │    │
│  │                                               │  ADAPT  │──┘       │    │
│  │                                               │         │          │    │
│  │                                               │ Enrich  │          │    │
│  │                                               │ future  │          │    │
│  │                                               │ percep. │          │    │
│  │                                               └─────────┘          │    │
│  │                                                                     │    │
│  │  Signals: STRONG_REWARD (+1.0) → STRONG_PUNISHMENT (−1.0)          │    │
│  │  High confidence + rewards → promote to top-tier knowledge         │    │
│  │  Low confidence + punishments → quarantine                         │    │
│  │  Idle patterns → gradual decay                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```
