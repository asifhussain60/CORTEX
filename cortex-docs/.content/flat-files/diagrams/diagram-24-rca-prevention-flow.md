# Diagram 24 — RCA Prevention Flow

```
                         FAILURE OCCURS
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OPJMixin._opj_record_failure()                                     │
│  • root_cause: str (existing)                                       │
│  • avoid_in_future: str (existing)                                  │
│  • rca: True ← NEW Phase 87 flag                                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  rca=True triggers
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  RCAEngine.select_methodology()                                     │
│                                                                     │
│  Category → Methodology mapping:                                    │
│  TECHNOLOGY  → Five Whys or Fault Tree                              │
│  PROCESS     → Fishbone (Ishikawa)                                  │
│  DATA        → Causal Chain                                         │
│  PEOPLE      → Fishbone (Ishikawa)                                  │
└─────┬───────────────┬────────────────┬────────────────┬─────────────┘
      │               │                │                │
      ▼               ▼                ▼                ▼
 FIVE_WHYS      FISHBONE          FAULT_TREE      CAUSAL_CHAIN
 (linear)    (4 categories)   (AND/OR gates)    (time sequence)
      │               │                │                │
      └───────────────┴────────────────┴────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  RCAAnalysis (dataclass)                                            │
│  • id: "RCA-{uuid}"                                                 │
│  • methodology: RCATemplate enum                                    │
│  • root_cause: str (structured)                                     │
│  • category: RCACategory enum                                       │
│  • analysis_data: dict (methodology-specific)                       │
│  • confidence: float                                                │
│  • prevention_rule: PreventionRule                                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┴─────────────────┐
              │                                  │
              ▼                                  ▼
┌─────────────────────────┐         ┌──────────────────────────────┐
│  RCAStore (SQLite)      │         │  RecurrenceSignatureEngine   │
│  .cortex-runtime/rca/  │         │                              │
│  • rca_analyses         │         │  Signature:                  │
│  • prevention_rules     │         │  RCA-SIG-{method}-{cat}     │
│  • recurrence_sigs      │         │        -{hash[:8]}           │
│  • recurrence_incidents │         │                              │
└─────────────────────────┘         │  Similarity check:           │
                                    │  ≥85% → RECURRENCE           │
                                    │  70–84% → CLUSTER MATCH      │
                                    │  <70% → NOVEL FAILURE        │
                                    └──────────────┬───────────────┘
                                                   │
                                    ┌──────────────┴───────────────┐
                                    │  Recurrence Count?           │
                                    └──────────────┬───────────────┘
                                                   │
                        ┌──────────────────────────┼──────────────────────────┐
                        │                          │                          │
                    Count = 1                  Count = 2                Count ≥ 3 + P0
                        │                          │                          │
                        ▼                          ▼                          ▼
                   ADVISORY                    WARNING                    BLOCKING
             (info in next OPJ         (governance gate             (operation halted —
              consult response)         response includes           structured review
                                        RCA reference)              required before
                                                                     proceeding)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  FUTURE OPERATION ARRIVES
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OPJMixin._opj_check_prevention_gate(operation_context)             │
│                                                                     │
│  1. Vectorise operation_context                                     │
│  2. Compare against all active PreventionRules                      │
│  3. Find rules with similarity ≥ 85%                               │
│  4. Return PreventionGateResult                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
            No match                  Match found
            (PASS)                         │
                  │              ┌──────────┴──────────┐
                  │              │                     │
                  │         Advisory/Warning         BLOCKING
                  │         (surface to dev)    (halt operation)
                  │                                    │
                  ▼                                    ▼
           Proceed normally                cortex_learning
                                           op="rca"
                                           action="review_required"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  URS SIGNAL EMISSION

  RCA outcome → ReinforcementEngine.emit_signal()

  P0 recurrence blocked:       STRONG_PUNISHMENT  (−1.0)
  P1 recurrence warned:        MODERATE_PUNISHMENT (−0.5)
  Gate fired correctly:        MODERATE_REWARD    (+0.5)
  Gate blocked, confirmed:     STRONG_REWARD      (+1.0)
  Gate false-positive bypass:  MODERATE_PUNISHMENT (−0.5)
          │
          ▼
  EffectivenessAnalyzer.apply_to_learning()
  → Pattern confidence updated
  → Prevention rule promoted/quarantined
  → CrossSessionPatternCache updated
```

## Nodes and Components

| Node | File | Phase |
|------|------|-------|
| `RCAEngine` | `cortex/intelligence/learning/rca_engine.py` | Phase 87 |
| `RCAAnalysis` | `cortex/intelligence/learning/rca_models.py` | Phase 87 |
| `RCAStore` | `cortex/intelligence/learning/rca_store.py` | Phase 87 |
| `PreventionGate` | `cortex/intelligence/learning/prevention_gate.py` | Phase 87 |
| `RecurrenceSignatureEngine` | `cortex/intelligence/learning/recurrence_engine.py` | Phase 87 |
| `OPJMixin._opj_analyze_rca()` | `cortex/core/orchestrator_protocol_mixin.py` | Phase 87 |
| `OPJMixin._opj_check_prevention_gate()` | `cortex/core/orchestrator_protocol_mixin.py` | Phase 87 |
| `cortex_learning op="rca"` | `cortex/mcp/tools/cortex_learning.py` | Phase 87 |
| `ReinforcementEngine` | `cortex/intelligence/learning/reinforcement_engine.py` | Phase 83 (existing) |
| `CrossSessionPatternCache` | `cortex/intelligence/learning/` | Phase 83 (extended) |

## Key Design Decisions

- **Zero new orchestrators** — pure extension of OPJMixin
- **Zero new MCP tools** — extends existing `cortex_learning` with `op="rca"`
- **Advisory by default** — Prevention Gate never blocks on first occurrence
- **P0-only blocking** — P1/P2 recurrences never escalate beyond Warning
- **Cross-orchestrator** — same root cause class tracked across all 51 orchestrators
- **Methodology auto-selection** — RCAEngine selects methodology from failure category; developer can override
