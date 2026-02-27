# Intelligence Matrix — Cross-Wiring Map
# Shows how intelligence-providing and intelligence-consuming subsystems connect

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        INTELLIGENCE MATRIX                                        │
│                                                                                   │
│  The neural wiring map — every intelligence capability × every operational        │
│  capability. Each cell: "Should these be wired? If so, how?"                      │
│                                                                                   │
│  Intelligence Providers (x-axis, 15 subsystems):                                  │
│  LENS · Synthesis · DomainBrain · T1Learned · T2Adaptive · T3Scratch ·            │
│  IntelligenceOrch · ResponseTemplate · BlindSpot · KnowledgeIndexer ·             │
│  HierScanner · KnowIdxDocBridge · WiringBridges · BrainQuery · FormatHook         │
│                                                                                   │
│  Operational Consumers (y-axis, 15 subsystems):                                   │
│  HierScanner · BatchProc · DomainAdapter · DocGenPlaybook · AuditFix ·            │
│  EnforcementOrch · VacuumOrch · MCPToolRegistry · SweepCatalogue ·                │
│  TDDOrch · SynthesisBridge · RetrievalOptBridge · TDDStubGen ·                    │
│  ResponseHook · T1T2EnrichHooks                                                   │
│                                                                                   │
│                                                                                   │
│             LENS  Synth  Brain  T1   T2   T3   IntO  Resp  Blind KnIdx ...        │
│           ┌──────┬──────┬──────┬────┬────┬────┬─────┬─────┬─────┬─────┐           │
│  HierScan │ CRIT │  ·   │  ·   │ ·  │ ·  │ ·  │  ·  │  ·  │  ·  │  ·  │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  BatchPrc │  ·   │  ·   │  ·   │ ·  │ ·  │ ·  │HIGH │  ·  │  ·  │  ·  │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  DocGen   │  ·   │  ·   │  ·   │ ·  │ ·  │ ·  │  ·  │  ·  │  ·  │CRIT │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  AuditFix │ HIGH │ HIGH │  ·   │ ·  │ ·  │ ·  │  ·  │  ·  │HIGH │  ·  │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  Enforcem │  ·   │  ·   │  ·   │ ·  │ ·  │ ·  │  ·  │  ·  │CRIT │  ·  │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  MCP Reg  │  ·   │  ·   │ CRIT │CRIT│CRIT│CRIT│  ·  │CRIT │  ·  │  ·  │          │
│           ├──────┼──────┼──────┼────┼────┼────┼─────┼─────┼─────┼─────┤           │
│  TDDOrch  │ HIGH │  ·   │  ·   │ ·  │ ·  │ ·  │  ·  │  ·  │  ·  │  ·  │          │
│           └──────┴──────┴──────┴────┴────┴────┴─────┴─────┴─────┴─────┘           │
│                                                                                   │
│  Legend:  CRIT = Critical wiring (P0)                                             │
│           HIGH = High priority (P1)                                               │
│            ·   = Not wired or lower priority                                      │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐       │
│  │  CRITICAL WIRING PAIRS                                                  │       │
│  │                                                                         │       │
│  │  LENS × HierScanner      → LENS needs file discovery as foundation     │       │
│  │  BrainTiers × MCP        → Memory surfaced to IDE via MCP              │       │
│  │  BlindSpot × Enforcement → Gaps trigger governance violations           │       │
│  │  KnowIdx × DocGen        → Docs draw from canonical knowledge index   │       │
│  │  ResponseTemplate × MCP  → All MCP results pass through formatting    │       │
│  └─────────────────────────────────────────────────────────────────────────┘       │
│                                                                                   │
│  Coverage Gate: ≥ 50% of cells must be wired                                      │
│  Below threshold → MatrixCoverageError → pipeline halts                           │
│                                                                                   │
│  7 Dimensions: brain_tier · lens · intelligence · toolkit ·                       │
│                 workflow · response · governance                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```
