# MCP Request Lifecycle

---
id: mcp-request-lifecycle
title: MCP Request Processing Lifecycle
purpose: Visualize the complete journey of a user request through CORTEX
audience: [Product Owners, Software Developers]
source_of_truth: cortex/mcp/server.py + cortex/orchestrators/master_orchestrator.py
last_verified: 2026-02-15
diagram_type: Sequence
interactive: false
word_count: 800
---

## Request Lifecycle Overview

Every user interaction with CORTEX follows a standardized request processing lifecycle, from IDE invocation through governance validation, orchestrator dispatch, and response delivery. This diagram traces a typical IMPLEMENT request end-to-end.

```mermaid
sequenceDiagram
    participant User as Developer<br/>(VS Code)
    participant IDE as Copilot Chat<br/>(Extension)
    participant MCP as MCP Gateway<br/>(stdio)
    participant Gate as Native Tool Gate
    participant Master as MasterOrchestrator
    participant Validation as Holistic<br/>Validation
    participant CCL as Context<br/>Crystallization
    participant Router as IntentRouter
    participant TDD as TDDOrchestrator
    participant LENS as LENS<br/>Analyzers
    participant Gov as Governance<br/>Engine
    participant Git as Git Repository
    
    %% User initiates request
    User->>IDE: "/implement add user authentication"
    IDE->>MCP: cortex_process_request(operation="implement", request="add user authentication")
    
    %% MCP Gateway processing
    MCP->>MCP: Validate JSON-RPC schema
    MCP->>Gate: Check intent classification
    
    alt Intent = IMPLEMENT/FIX/REFACTOR
        Gate->>Gate: ✅ MCP tool required (bypass blocked)
    else Intent = ANALYZE/QUERY
        Gate->>Gate: ⚠️ Direct tools allowed (read-only)
    end
    
    Gate->>Master: Dispatch to MasterOrchestrator
    
    %% Pre-flight checks
    Master->>Validation: Pre-flight validation
    
    par Parallel Pre-Flight
        Validation->>Gov: Run 7 enforcement agents
        Gov->>Gov: Check CORE rules (TDD, security, naming)
        Gov-->>Validation: ✅ PASS (0 violations)
    and
        Master->>CCL: Async context prefetch
        CCL->>Git: Load rules (tier precedence)
        CCL->>LENS: Warm AST cache
        CCL->>CCL: Detect infrastructure capabilities
        CCL-->>Master: Context ready (245ms avg)
    end
    
    Validation-->>Master: ✅ Pre-flight passed
    
    %% Intent classification
    Master->>Router: Classify intent via LENS
    Router->>Router: LANGUAGE: Parse request semantics<br/>EXAMINATION: Analyze codebase<br/>NAVIGATION: Find target files<br/>SYNTHESIS: Determine orchestrator
    Router-->>Master: Intent = IMPLEMENT → TDDOrchestrator
    
    %% TDD workflow
    Master->>TDD: Execute TDD workflow
    
    TDD->>LENS: Analyze target area
    LENS->>LENS: Parallel analyzer execution (8 analyzers)
    LENS-->>TDD: Intelligence report
    
    TDD->>TDD: RED: Write failing tests
    TDD->>Git: Create test file
    TDD->>TDD: Run tests → ❌ FAIL (expected)
    
    TDD->>TDD: GREEN: Implement minimal code
    TDD->>Git: Create implementation file
    TDD->>TDD: Run tests → ✅ PASS
    
    TDD->>TDD: REFACTOR: Improve code
    TDD->>LENS: Detect duplications
    LENS-->>TDD: No violations
    TDD->>Git: Apply refactorings
    TDD->>TDD: Run tests → ✅ PASS
    
    TDD->>Git: Commit with AC markers
    Git-->>TDD: Commit SHA: a1b2c3d
    
    TDD-->>Master: Completion report
    
    %% Response delivery
    Master->>Master: Format response (silent execution template)
    Master->>MCP: Return MCP response
    MCP->>IDE: JSON-RPC response
    IDE->>User: Display progress bars + completion table
    
    Note over User,Git: Total latency: 1200-2500ms<br/>(varies by code complexity)
```

## Lifecycle Phases Explained

### Phase 1: Request Initiation (5-10ms)

**Developer action:** User types `/implement add user authentication` in Copilot Chat  
**IDE processing:** VS Code extension detects cortex_* MCP tool invocation  
**Transport:** Sends JSON-RPC 2.0 message over stdio to MCP server

**Example payload:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_process_request",
    "arguments": {
      "operation": "implement",
      "request": "add user authentication",
      "mode": "TDD"
    }
  },
  "id": "req-12345"
}
```

### Phase 2: Gateway Validation (5-15ms)

**MCP Gateway responsibilities:**
1. Validate JSON-RPC schema compliance
2. Authenticate request (if multi-tenant mode enabled)
3. Log request for observability (Prometheus metrics)
4. Route to Native Tool Gate

**Native Tool Gate checks:**
- Intent classification (IMPLEMENT/FIX/REFACTOR require MCP)
- Direct file operation bypass prevention (CORE-049)
- If MCP unavailable + blocking intent → ERROR (setup required)

### Phase 3: Pre-Flight Checks (150-300ms)

**Parallel execution of two critical paths:**

**Path A: Governance Validation**
- 7 enforcement agents execute CORE rule checks
- TDD-first enforcement (CORE-008)
- Type hint validation (CORE-011)
- File naming checks (CORE-028)
- Incremental execution limits (CORE-001)
- Verdict: BLOCKED, WARNING, or PASS

**Path B: Context Crystallization (Phase 49)**
- Async prefetch of governance rules with tier precedence
- LENS state warming (AST cache, git history)
- Infrastructure capability detection
- Target SLA: 300ms, fallback max: 500ms

**Blocking conditions:**
- Governance verdict = BLOCKED → Request terminated
- MCP tools unavailable → Request terminated
- Context warm-up timeout → Proceed with cold context (degraded mode)

### Phase 4: Intent Classification (20-40ms)

**LENS-based classification:**

| Step | Operation | Output |
|------|-----------|--------|
| **LANGUAGE** | Parse request semantics using NLP | "User wants authentication feature" |
| **EXAMINATION** | Analyze existing codebase patterns | "Project uses FastAPI + JWT" |
| **NAVIGATION** | Identify target files and dependencies | "auth/ directory, user.py model" |
| **SYNTHESIS** | Select orchestrator | "IMPLEMENT → TDDOrchestrator" |

**Intent mapping:**
- IMPLEMENT, FIX → TDDOrchestrator
- ANALYZE → LENSSynthesis
- REFACTOR → RefactoringOrchestrator
- PLAN → PlanOrchestrator

### Phase 5: TDD Workflow Execution (500-2000ms)

**RED phase (200-600ms):**
- LENS analyzes target implementation area
- Generate test file with failing tests
- Run pytest → Expected failure ❌
- Commit checkpoint: `git commit -m "test: add auth tests (RED)"`

**GREEN phase (200-800ms):**
- Implement minimal code to pass tests
- Create/modify implementation files
- Run pytest → Success ✅
- Commit: `git commit -m "feat: implement auth (GREEN)"`

**REFACTOR phase (100-600ms):**
- LENS detects code duplications (CORE-035)
- Apply safe refactorings (extract method, rename variable)
- Run pytest → Success ✅
- Commit: `git commit -m "refactor: improve auth code (REFACTOR)"`

**Audit trail:**
```python
# AC_START: AC-IMPLEMENT-AUTH-001
# Description: Add user authentication with JWT
# ... implementation code ...
# AC_COMPLETE: AC-IMPLEMENT-AUTH-001 ✅ 18/18 tests passing
```

### Phase 6: Response Delivery (10-20ms)

**Silent execution response format:**

```markdown
---
📋 **Authentication Feature: IMPLEMENTATION**

`██████████` 100% Complete

| # | Status | Component | Detail |
|---|--------|-----------|--------|
| 1 | ✅ | Tests | auth/test_auth.py (RED) |
| 2 | ✅ | Implementation | auth/jwt_handler.py (GREEN) |
| 3 | ✅ | Refactoring | Extract token validation (REFACTOR) |
| 4 | ✅ | Commit | Audit trail complete |

**Tests:** 18/18 | **Coverage:** 94%
**Fixed:** User authentication with JWT tokens

---
```

## Error Handling Paths

```mermaid
graph TB
    Request[User Request] --> Validate{Gateway<br/>Validation}
    
    Validate -->|Invalid Schema| E1[Error: Invalid JSON-RPC]
    Validate -->|Valid| PreFlight{Pre-Flight<br/>Checks}
    
    PreFlight -->|BLOCKED| E2[Error: Governance violation]
    PreFlight -->|MCP Unavailable| E3[Error: MCP setup required]
    PreFlight -->|PASS| Execute{Orchestrator<br/>Execution}
    
    Execute -->|Test Failure| E4[Error: Tests not passing]
    Execute -->|Code Error| E5[Error: Implementation failed]
    Execute -->|Success| Response[Success Response]
    
    E1 --> User[Return to User]
    E2 --> User
    E3 --> User
    E4 --> Retry{Auto-Retry?}
    E5 --> Retry
    
    Retry -->|Yes| Execute
    Retry -->|No| User
    Response --> User
    
    style E1 fill:#dc2626,stroke:#991b1b
    style E2 fill:#dc2626,stroke:#991b1b
    style E3 fill:#dc2626,stroke:#991b1b
    style E4 fill:#f59e0b,stroke:#d97706
    style E5 fill:#f59e0b,stroke:#d97706
    style Response fill:#10b981,stroke:#059669
```

**Error recovery strategies:**
- **Governance violations:** Display fix instructions, block execution
- **MCP unavailable:** Guide user through setup (python .cortex/setup-mcp.py)
- **Test failures:** Analyze error, retry implementation with corrections
- **Implementation errors:** Rollback to last known good state

## Performance Metrics

| Metric | Target | P50 | P95 | P99 |
|--------|--------|-----|-----|-----|
| **Gateway validation** | <20ms | 8ms | 15ms | 22ms |
| **Pre-flight checks** | <300ms | 245ms | 320ms | 450ms |
| **Intent classification** | <50ms | 32ms | 45ms | 62ms |
| **TDD cycle (small)** | <1000ms | 850ms | 1200ms | 1800ms |
| **TDD cycle (large)** | <2500ms | 2100ms | 2600ms | 3500ms |
| **End-to-end (avg)** | <2000ms | 1650ms | 2300ms | 3200ms |

> **Notice:** Performance metrics represent internal testing results with typical codebases (50-100K LOC). Production performance depends on codebase complexity, hardware specifications, and concurrent operations. Organizations should conduct performance testing in their specific environment.

**Related Diagrams:**
- [C4 Container Architecture](./c4-container.md)
- [Orchestrator Dispatch Flow](./orchestrator-dispatch.md)
- [Governance Gate Details](./governance-gate.md)
