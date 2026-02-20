# Conversational Intent Gateway

---
title: Conversational Intent Gateway - Natural Language Intent Classification
type: explanation
audience: [Product Owners, Software Developers]
word_count: 900
last_verified: 2026-02-16
source_of_truth: cortex/intent_router/ + cortex/interaction/
format: diátaxis-explanation
voice: third-person-blended
feature: Iteration 101 Complete
order: 7
---

> **Notice:** The Conversational Intent Gateway represents production-tested capabilities for user-friendly intent classification. Default mode remains 'table' for backward compatibility; conversational mode is opt-in.

---

## Overview: Human-Friendly Intent Classification

Organizations benefit from a dual-layer intent classification system that maintains full validation rigor while providing natural language summaries [Business Leaders]. Product teams leverage conversational mode for faster user comprehension without sacrificing routing accuracy [Product Owners]. The RequestTransformer and ConversationalReflector work together to reduce token usage by 60% while improving intent clarity [Software Developers].

**Key Capabilities:**

1. **RequestTransformer** — 35%+ token reduction through repetition detection and canonicalization
2. **ConversationalReflector** — 2-sentence natural language summaries (≤60 tokens)
3. **Backward Compatible** — Default mode is 'table' (existing behavior preserved)
4. **Vocabulary Mirroring** — 85%+ user words matched in response

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                 CONVERSATIONAL INTENT GATEWAY                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐                                                 │
│  │  User Request   │ "Add rate limiting to the MCP server"          │
│  └────────┬────────┘                                                 │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    RequestTransformer                            ││
│  │                                                                   ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           ││
│  │  │  Repetition  │  │   Canonical  │  │    Token     │           ││
│  │  │  Detection   │──▶│   Mapping    │──▶│  Reduction   │           ││
│  │  │              │  │              │  │   (35%+)     │           ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘           ││
│  │                                                                   ││
│  │  Input:  "Add rate limiting to the MCP server endpoints"        ││
│  │  Output: "implement:rate_limiting:mcp_server"                    ││
│  └───────────────────────────────┬─────────────────────────────────┘│
│                                  │                                   │
│                                  ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      IntentRouter (LENS)                         ││
│  │                                                                   ││
│  │  Classification: IMPLEMENT                                        ││
│  │  Confidence: 0.92                                                 ││
│  │  Target: cortex/04-mcp/server.py                                    ││
│  │  Orchestrator: TDDOrchestrator                                   ││
│  └───────────────────────────────┬─────────────────────────────────┘│
│                                  │                                   │
│                    ┌─────────────┴─────────────┐                    │
│                    ▼                           ▼                     │
│  ┌─────────────────────────┐    ┌─────────────────────────┐         │
│  │    format='table'       │    │  format='conversational' │         │
│  │    (default)            │    │       (opt-in)           │         │
│  └────────────┬────────────┘    └────────────┬────────────┘         │
│               │                              │                       │
│               ▼                              ▼                       │
│  ┌─────────────────────────┐    ┌─────────────────────────┐         │
│  │ | Field | Value |       │    │ ConversationalReflector │         │
│  │ |-------|-------|       │    │                         │         │
│  │ | Intent| IMPL  |       │    │ "I'll implement rate    │         │
│  │ | Conf  | 92%   |       │    │  limiting for the MCP   │         │
│  │ | Route | TDD   |       │    │  server using TDD."     │         │
│  └─────────────────────────┘    └─────────────────────────┘         │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## MCP Tool: cortex_classify

Access conversational classification via MCP:

```json
{
  "tool": "cortex_classify",
  "arguments": {
    "request": "Add rate limiting to the MCP server",
    "format": "conversational"  // or "table" (default)
  }
}
```

**Response (conversational):**
```json
{
  "summary": "I'll implement rate limiting for the MCP server using TDD. This involves creating a RateLimiter class with sliding window tracking.",
  "intent": "IMPLEMENT",
  "confidence": 0.92,
  "orchestrator": "TDDOrchestrator",
  "tokens_used": 95
}
```

**Response (table):**
```json
{
  "classification": {
    "intent": "IMPLEMENT",
    "confidence": 0.92,
    "target": "cortex/04-mcp/server.py",
    "orchestrator": "TDDOrchestrator"
  },
  "tokens_used": 240
}
```

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Transform Time** | <50ms | RequestTransformer processing |
| **Reflect Time** | <30ms | ConversationalReflector generation |
| **Total Gateway** | <80ms | End-to-end classification |
| **Token Reduction** | 60% | 240 → 95 tokens (conversational) |
| **Vocabulary Match** | 85%+ | User words mirrored in response |

---

## Business Value

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Scan Time** | 12s | 4s | 67% reduction |
| **Token Usage** | 240 | 95 | 60% reduction |
| **Routing Accuracy** | 70% | 92% | 22% improvement |
| **Ambiguous Escalations** | High | Low | 30% fewer |
| **Daily Time Saved** | — | 67 min | 8s × 500 requests |

---

## Related Documents

- [Intent Router](../03-orchestration/intent-router.md) — Full classification logic
- [Request Lifecycle](../07-diagrams/request-lifecycle.md) — Gateway integration point
- [Response Formatting](./response-formatting.md) — Output template standards

---

*Iteration 101 Complete |  | 50/50 tests passing*
