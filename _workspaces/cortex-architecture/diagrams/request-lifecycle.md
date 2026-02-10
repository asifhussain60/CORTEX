# Request Lifecycle Diagram

**Purpose:** Interactive request processing flow with d3.js visualizations  
**Audience:** Developers, Architects  
**Last Updated:** 2026-02-10

---

## Interactive Request Lifecycle Flow

### D3.js Sequence Diagram

```json
{
  "type": "sequence",
  "title": "CORTEX Request Lifecycle",
  "participants": [
    {"id": "client", "name": "Client (VS Code)", "color": "#4CAF50"},
    {"id": "gateway", "name": "MCP Gateway", "color": "#2196F3"},
    {"id": "master", "name": "MasterOrchestrator", "color": "#FF9800"},
    {"id": "intent", "name": "IntentRouter", "color": "#9C27B0"},
    {"id": "lens", "name": "LENS", "color": "#E91E63"},
    {"id": "tdd", "name": "TDDOrchestrator", "color": "#795548"}
  ],
  "interactions": [
    {
      "from": "client",
      "to": "gateway",
      "message": "POST /tools/cortex_process_request",
      "details": "JSON-RPC 2.0 request with operation details",
      "timing": "0ms",
      "type": "request"
    },
    {
      "from": "gateway",
      "to": "gateway",
      "message": "Authenticate & Validate",
      "details": "API key validation, rate limiting, JSON schema validation",
      "timing": "5-15ms",
      "type": "internal"
    },
    {
      "from": "gateway",
      "to": "master",
      "message": "Route Request",
      "details": "Forward validated request to MasterOrchestrator",
      "timing": "20ms",
      "type": "request"
    },
    {
      "from": "master",
      "to": "intent",
      "message": "Classify Intent",
      "details": "Analyze request to determine IMPLEMENT/FIX/REFACTOR/etc.",
      "timing": "25ms",
      "type": "request"
    },
    {
      "from": "intent",
      "to": "master",
      "message": "Intent: IMPLEMENT (95% confidence)",
      "details": "Classification result with confidence score",
      "timing": "45ms",
      "type": "response"
    },
    {
      "from": "master",
      "to": "lens",
      "message": "Analyze Context",
      "details": "Request code analysis and context synthesis",
      "timing": "50ms",
      "type": "request"
    },
    {
      "from": "lens",
      "to": "master",
      "message": "Context Analysis",
      "details": "Git history, AST analysis, pattern detection results",
      "timing": "200ms",
      "type": "response"
    },
    {
      "from": "master",
      "to": "tdd",
      "message": "Execute TDD Workflow",
      "details": "Delegate to TDDOrchestrator with enriched context",
      "timing": "220ms",
      "type": "request"
    },
    {
      "from": "tdd",
      "to": "tdd",
      "message": "RED → GREEN → REFACTOR",
      "details": "Execute TDD cycle with tests first",
      "timing": "220ms-2000ms",
      "type": "internal"
    },
    {
      "from": "tdd",
      "to": "master",
      "message": "Implementation Complete",
      "details": "Result with test coverage and quality metrics",
      "timing": "2000ms",
      "type": "response"
    },
    {
      "from": "master",
      "to": "gateway",
      "message": "Aggregated Result",
      "details": "Final response with audit trail",
      "timing": "2010ms",
      "type": "response"
    },
    {
      "from": "gateway",
      "to": "client",
      "message": "HTTP 200 OK",
      "details": "JSON response with implementation details",
      "timing": "2015ms",
      "type": "response"
    }
  ]
}
```

### D3.js Flow Chart Data

```json
{
  "type": "flowchart",
  "title": "Request Processing Pipeline",
  "nodes": [
    {"id": "start", "label": "Request Received", "type": "start", "x": 100, "y": 50},
    {"id": "auth", "label": "Authentication\n& Rate Limiting", "type": "process", "x": 100, "y": 150, "timing": "5-15ms"},
    {"id": "validate", "label": "JSON-RPC\nValidation", "type": "process", "x": 100, "y": 250, "timing": "1-2ms"},
    {"id": "route", "label": "Route to\nMasterOrchestrator", "type": "process", "x": 100, "y": 350, "timing": "1ms"},
    {"id": "classify", "label": "Intent\nClassification", "type": "process", "x": 300, "y": 350, "timing": "20-50ms"},
    {"id": "context", "label": "LENS Context\nAnalysis", "type": "process", "x": 500, "y": 350, "timing": "100-300ms"},
    {"id": "decision", "label": "Intent Type?", "type": "decision", "x": 300, "y": 500},
    {"id": "implement", "label": "TDD\nOrchestrator", "type": "process", "x": 150, "y": 650, "timing": "500-3000ms"},
    {"id": "analyze", "label": "LENS\nSynthesis", "type": "process", "x": 300, "y": 650, "timing": "200-800ms"},
    {"id": "refactor", "label": "Refactoring\nOrchestrator", "type": "process", "x": 450, "y": 650, "timing": "800-2000ms"},
    {"id": "aggregate", "label": "Aggregate\nResults", "type": "process", "x": 300, "y": 800, "timing": "5-10ms"},
    {"id": "audit", "label": "Audit Trail\n& Logging", "type": "process", "x": 500, "y": 800, "timing": "2-5ms"},
    {"id": "response", "label": "JSON Response\nto Client", "type": "end", "x": 300, "y": 950}
  ],
  "edges": [
    {"from": "start", "to": "auth", "label": ""},
    {"from": "auth", "to": "validate", "label": "✅ Authorized"},
    {"from": "validate", "to": "route", "label": "✅ Valid"},
    {"from": "route", "to": "classify", "label": ""},
    {"from": "classify", "to": "context", "label": ""},
    {"from": "context", "to": "decision", "label": ""},
    {"from": "decision", "to": "implement", "label": "IMPLEMENT"},
    {"from": "decision", "to": "analyze", "label": "ANALYZE"},
    {"from": "decision", "to": "refactor", "label": "REFACTOR"},
    {"from": "implement", "to": "aggregate", "label": ""},
    {"from": "analyze", "to": "aggregate", "label": ""},
    {"from": "refactor", "to": "aggregate", "label": ""},
    {"from": "aggregate", "to": "audit", "label": ""},
    {"from": "audit", "to": "response", "label": ""}
  ],
  "error_paths": [
    {"from": "auth", "to": "response", "label": "❌ Unauthorized", "color": "red"},
    {"from": "validate", "to": "response", "label": "❌ Invalid JSON", "color": "red"}
  ]
}
```

### Performance Metrics Dashboard

```json
{
  "type": "metrics_dashboard",
  "title": "Request Lifecycle Performance",
  "time_range": "Last 24 hours",
  "metrics": [
    {
      "name": "Request Latency",
      "type": "histogram",
      "data": [
        {"bucket": "0-50ms", "count": 1250, "percentage": 45},
        {"bucket": "50-200ms", "count": 980, "percentage": 35},
        {"bucket": "200-500ms", "count": 420, "percentage": 15},
        {"bucket": "500ms-2s", "count": 112, "percentage": 4},
        {"bucket": "2s+", "count": 28, "percentage": 1}
      ],
      "p50": "85ms",
      "p95": "450ms",
      "p99": "1.2s"
    },
    {
      "name": "Phase Breakdown",
      "type": "stacked_bar",
      "data": [
        {"phase": "Authentication", "avg_time": 8, "color": "#FF5722"},
        {"phase": "Intent Classification", "avg_time": 32, "color": "#9C27B0"},
        {"phase": "LENS Analysis", "avg_time": 185, "color": "#E91E63"},
        {"phase": "Orchestrator Execution", "avg_time": 850, "color": "#4CAF50"},
        {"phase": "Result Aggregation", "avg_time": 12, "color": "#2196F3"}
      ]
    },
    {
      "name": "Success Rate by Intent",
      "type": "donut",
      "data": [
        {"intent": "IMPLEMENT", "success_rate": 94.2, "total_requests": 1580},
        {"intent": "ANALYZE", "success_rate": 98.7, "total_requests": 890},
        {"intent": "REFACTOR", "success_rate": 91.8, "total_requests": 420},
        {"intent": "FIX", "success_rate": 96.1, "total_requests": 340}
      ]
    }
  ]
}
```

## Request Flow Phases

### Phase 1: Neural Signal Reception (5-15ms)
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │  │
│  │  │  Parse Tool     │───►│  Lookup in      │───►│  Validate       │              │  │
│  │  │  Name           │    │  Registry       │    │  Arguments      │              │  │
│  │  │                 │    │                 │    │                 │              │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘              │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 4: INTENT CLASSIFICATION (10-20ms)                                         │  │
│  │                                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                      IntentRouter                                            │ │  │
│  │  │                                                                              │ │  │
│  │  │  Request ──► Keyword Analysis ──► Pattern Matching ──► Confidence Score    │ │  │
│  │  │                                                              │               │ │  │
│  │  │                                                              ▼               │ │  │
│  │  │                                                    ┌─────────────────┐      │ │  │
│  │  │                                                    │  Intent Type    │      │ │  │
│  │  │                                                    │  (14 types)     │      │ │  │
│  │  │                                                    └─────────────────┘      │ │  │
│  │  │                                                                              │ │  │
│  │  │  IMPLEMENT │ FIX │ REFACTOR │ ANALYZE │ TEST │ DEPLOY │ ...               │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 5: CONTEXT GATHERING (50-200ms)                                            │  │
│  │                                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                        LENS Engine                                           │ │  │
│  │  │                                                                              │ │  │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐              │ │  │
│  │  │  │  Git   │  │  AST   │  │Comment │  │Pattern │  │ Config │              │ │  │
│  │  │  │Analyzer│  │Analyzer│  │Analyzer│  │Analyzer│  │Analyzer│              │ │  │
│  │  │  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘              │ │  │
│  │  │      │           │           │           │           │                    │ │  │
│  │  │      └───────────┴───────────┴───────────┴───────────┘                    │ │  │
│  │  │                              │                                             │ │  │
│  │  │                              ▼                                             │ │  │
│  │  │                    ┌─────────────────────┐                                │ │  │
│  │  │                    │     Synthesizer     │                                │ │  │
│  │  │                    │  (Merge + Score)    │                                │ │  │
│  │  │                    └─────────────────────┘                                │ │  │
│  │  │                              │                                             │ │  │
│  │  │                              ▼                                             │ │  │
│  │  │                    ┌─────────────────────┐                                │ │  │
│  │  │                    │   Unified Context   │                                │ │  │
│  │  │                    └─────────────────────┘                                │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 6: GOVERNANCE VALIDATION (50-150ms)                                        │  │
│  │                                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    EnforcementOrchestrator                                   │ │  │
│  │  │                                                                              │ │  │
│  │  │  Context ──► Agent 1 ──► Agent 2 ──► Agent 3 ──► ... ──► Agent 7           │ │  │
│  │  │                │           │           │                    │                │ │  │
│  │  │                ▼           ▼           ▼                    ▼                │ │  │
│  │  │             PASS/WARN   PASS/WARN   PASS/WARN           PASS/WARN           │ │  │
│  │  │                                                                              │ │  │
│  │  │                              │                                               │ │  │
│  │  │                              ▼                                               │ │  │
│  │  │                    ┌─────────────────────┐                                  │ │  │
│  │  │                    │  Aggregate Result   │                                  │ │  │
│  │  │                    │  PASS / WARN / BLOCK│                                  │ │  │
│  │  │                    └─────────────────────┘                                  │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                                    │  │
│  │  If BLOCK: Return error immediately with violations                               │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼ (if PASS/WARN)                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 7: ORCHESTRATOR EXECUTION (100-5000ms)                                     │  │
│  │                                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                      Selected Orchestrator                                   │ │  │
│  │  │                                                                              │ │  │
│  │  │  IMPLEMENT ──► TDDOrchestrator                                              │ │  │
│  │  │      │                                                                       │ │  │
│  │  │      ▼                                                                       │ │  │
│  │  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │  │
│  │  │  │  RED Phase                                                             │  │ │  │
│  │  │  │  • Generate failing test                                               │  │ │  │
│  │  │  │  • Validate test fails                                                 │  │ │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │ │  │
│  │  │      │                                                                       │ │  │
│  │  │      ▼                                                                       │ │  │
│  │  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │  │
│  │  │  │  GREEN Phase                                                           │  │ │  │
│  │  │  │  • Implement minimal code                                              │  │ │  │
│  │  │  │  • Run test until pass                                                 │  │ │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │ │  │
│  │  │      │                                                                       │ │  │
│  │  │      ▼                                                                       │ │  │
│  │  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │  │
│  │  │  │  REFACTOR Phase                                                        │  │ │  │
│  │  │  │  • Clean up code                                                       │  │ │  │
│  │  │  │  • Ensure tests still pass                                             │  │ │  │
│  │  │  └───────────────────────────────────────────────────────────────────────┘  │ │  │
│  │  │                                                                              │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 8: RESPONSE FORMATTING (5-10ms)                                            │  │
│  │                                                                                    │  │
│  │  Result ──► Format as MCP Response ──► Add Metadata ──► Serialize JSON           │  │
│  │                                             │                                      │  │
│  │                                             ▼                                      │  │
│  │                                    ┌─────────────────┐                            │  │
│  │                                    │  Audit Entry    │                            │  │
│  │                                    │  (async write)  │                            │  │
│  │                                    └─────────────────┘                            │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                                   │
│                                      ▼                                                   │
│                                   CLIENT                                                 │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Timing Breakdown

| Phase | Component | Typical Time | Max Time |
|-------|-----------|--------------|----------|
| 1 | Ingestion | 5-10ms | 50ms |
| 2 | Auth/Authz | 10-20ms | 100ms |
| 3 | Tool Resolution | 5ms | 20ms |
| 4 | Intent Classification | 10-20ms | 50ms |
| 5 | LENS Context | 50-200ms | 500ms |
| 6 | Governance | 50-150ms | 300ms |
| 7 | Execution | 100-5000ms | 30s |
| 8 | Response | 5-10ms | 50ms |

**Total P50:** ~300ms | **Total P95:** ~2s | **Total P99:** ~5s

---

## Related Documents

- [Architecture Overview](architecture-overview.md) — System architecture
- [Data Flow](data-flow.md) — Data movement
- [Component Relationships](component-relationships.md) — Dependencies

---

*Part of CORTEX Architecture Documentation*
