# End-to-End Flow

---
title: CORTEX End-to-End Request Flow
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/core/ + cortex/mcp/
order: 8
---

## Complete Pipeline

```
[Developer types: "implement user authentication"]
                    │
                    ▼
┌─── Stage -1: RequestRephraseOrchestrator (15-35ms) ───────────────┐
│  Enriches with: CORE-008 (TDD), CORE-013 (error handling),       │
│  security context, breaking-risk: MEDIUM                          │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 0: MCP Gateway (5-15ms) ────────────────────────────────┐
│  Validates JSON-RPC, routes to cortex_process_request             │
│  Native Tool Gate check: IMPLEMENT intent → MCP-first enforced    │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 1: IntentRouter (20-40ms) ──────────────────────────────┐
│  LENS classification → Intent: IMPLEMENT                          │
│  Route to: TDDOrchestrator                                        │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 2: LENS Analysis (300-800ms) ───────────────────────────┐
│  8 parallel analyzers scan the auth module                        │
│  AST: 3 classes, 12 functions, 2 missing type hints               │
│  Security: 1 hardcoded secret found                               │
│  Metrics: cyclomatic complexity 8 (acceptable)                    │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 3: Brain Intelligence (50-200ms) ───────────────────────┐
│  Perception: matches "web-api" pattern (confidence 0.87)          │
│  Reasoning: selects "tdd-incremental" strategy (success rate 94%) │
│  Action: 4-step plan with TDD gates at each boundary              │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 4: Governance Gate (<150ms) ────────────────────────────┐
│  10 agents check:                                                  │
│  ✅ TDD Agent: test-first required (CORE-008)                    │
│  ✅ Security Agent: hardcoded secret flagged (CORE-013)          │
│  ✅ Naming Agent: snake_case verified (CORE-028)                 │
│  Result: PASS with 1 WARNING (fix hardcoded secret)               │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 5: TDDOrchestrator Execution ───────────────────────────┐
│  RED:      test_user_auth_rejects_invalid_token() → FAILS ✅     │
│  GREEN:    implement UserAuthMiddleware → test PASSES ✅          │
│  REFACTOR: extract TokenValidator class → all tests PASS ✅      │
└───────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─── Stage 6: Result Delivery ─────────────────────────────────────┐
│  Result delivered inline (CORE-002)                               │
│  Audit trail → CortexAuditDB (.cortex-runtime/)                  │
│  AC_COMPLETE marker with test results                             │
└───────────────────────────────────────────────────────────────────┘
```

---

*Verified against complete orchestrator pipeline · 20 February 2026*
