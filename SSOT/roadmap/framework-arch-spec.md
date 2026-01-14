# Framework Architecture Specification

**Date:** 2026-01-14  
**Version:** 1.0.0-APPROVED  
**Status:** Ready for Implementation  
**Scope:** Orchestrators, Response Templates, MCP Integration, Base Interfaces

---

## Part 1: Orchestrator Framework

### 1.1 Base Orchestrator Interface

All orchestrators (CORTEX-owned and custom) implement `BaseOrchestrator` with mandatory methods:

**Core Contract:**
- `execute(request: ExecutionRequest) -> ExecutionResult` (REQUIRED)
- `can_handle(request: ExecutionRequest) -> bool` (REQUIRED)
- `delegate(request: ExecutionRequest) -> Optional[ExecutionResult]` (PROVIDED)
- `get_metadata() -> OrchestratorMetadata` (REQUIRED)

**Orchestrator Lifecycle:**
```
PENDING → RUNNING → COMPLETED/FAILED/CANCELLED
```

**State Transitions:**
- PENDING: Just created, not yet executed
- RUNNING: execute() called, in progress
- COMPLETED: execute() returned successfully (result.success = true)
- FAILED: execute() threw exception or returned failure (result.success = false)
- CANCELLED: User explicitly cancelled via cancel() method

---

### 1.2 Composite Pattern: Parent-Child Orchestrators

**Hierarchy:**
```
MasterOrchestrator (root)
├─ PlanningOrchestrator (core)
├─ TddMasterOrchestrator (core)
├─ AdoOrchestrator (domain)
├─ GovernanceOrchestrator (core)
├─ EvidenceOrchestrator (core)
└─ CustomPaymentOrchestrator (user-defined, isolated)
    └─ StripeMicroOrchestrator (child, handles payment processing)
```

**Delegation Rules:**
- Parent calls first child that returns `can_handle(request) = true`
- If no child handles, parent returns error
- If child raises exception, parent catches and logs; attempts next child
- No unhandled exceptions propagate to MasterOrchestrator (critical for stability)

---

### 1.3 Orchestrator Registry (Plugin System)

**Registration Points:**
- Auto-discovery: Scan `src/orchestrators/custom/` at startup
- Manual registration: Call `registry.register(name, class, is_core)`
- Runtime check: `if registry.has_orchestrator('payment'):`

**Safety Guardrails:**
- Custom orchestrators run in separate process (multiprocessing)
- Unhandled exceptions don't crash parent (caught at boundary)
- Dependency resolution: Orchestrators can declare dependencies
- Circular dependencies detected at startup (startup fails if cycle detected)

---

## Part 2: Response Template Architecture

### 2.1 Response Template System

**Purpose:** Standardized response format for all operations (success, error, partial)

**Template Hierarchy:**
```
BaseResponseTemplate
├─ SuccessResponse
│  ├─ SingletonResponse (one outcome)
│  └─ CompositeResponse (multiple orchestrator outcomes)
├─ ErrorResponse
│  ├─ ValidationError
│  ├─ RuntimeError
│  └─ TimeoutError
└─ PartialResponse (for degraded mode)
```

---

### 2.2 Response Schema

**Mandatory Fields (All Responses):**
```json
{
  "correlation_id": "uuid",
  "timestamp": "ISO8601",
  "status": "success|error|partial",
  "operation": "AC-ID or user request",
  "execution_time_ms": 1234
}
```

**Success Response:**
```json
{
  "correlation_id": "...",
  "timestamp": "...",
  "status": "success",
  "operation": "implement AC-AUDIT-001",
  "execution_time_ms": 2500,
  "results": {
    "planning": {
      "status": "completed",
      "output": "7-step plan generated",
      "time_ms": 500
    },
    "tdd": {
      "status": "completed",
      "output": "5 red tests created",
      "time_ms": 800
    },
    "governance": {
      "status": "completed",
      "passed_rules": 24,
      "violations": 0,
      "time_ms": 150
    }
  },
  "evidence": {
    "bundle_id": "evidence-2026-01-14-abc123",
    "artifacts": [
      "test_results.json",
      "code_diff.patch",
      "audit_log.sqlite"
    ]
  }
}
```

**Error Response:**
```json
{
  "correlation_id": "...",
  "timestamp": "...",
  "status": "error",
  "operation": "implement AC-AUDIT-001",
  "execution_time_ms": 1200,
  "error": {
    "code": "GOVERNANCE_VIOLATION",
    "message": "CORE-002: Root-level markdown not allowed",
    "rule_violated": "CORE-002",
    "severity": "blocked",
    "context": {
      "file_attempted": "architecture-summary.md",
      "location": "root",
      "expected_location": "cortex-brain/documents/ or docs/"
    }
  },
  "recovery_suggestion": "Move file to docs/ and retry"
}
```

**Partial Response (Degraded Mode):**
```json
{
  "correlation_id": "...",
  "timestamp": "...",
  "status": "partial",
  "operation": "implement AC-TDD-001",
  "execution_time_ms": 5100,
  "warning": "Operation completed with reduced capability",
  "completed_stages": [
    "planning",
    "tdd"
  ],
  "skipped_stages": [
    "ado",
    "evidence"
  ],
  "reason": "ADO orchestrator timeout (>10s) triggered fallback mode",
  "results": {
    "planning": { "status": "completed", ... },
    "tdd": { "status": "completed", ... },
    "ado": { "status": "timeout", "error": "Connection to Azure DevOps failed" },
    "governance": { "status": "skipped", "reason": "ADO failed; cannot assess compliance" }
  }
}
```

---

### 2.3 Response Template Configuration

**YAML Configuration:**
```yaml
response_templates:
  version: "1.0.0"
  
  success:
    include_evidence: true
    include_timing: true
    include_rule_evaluation: true
    max_output_size_mb: 10
  
  error:
    include_context: true
    include_recovery_suggestion: true
    include_full_stack_trace: false  # Production safety
    redact_secrets: true
  
  partial:
    include_completion_percentage: true
    include_next_steps: true
    include_retry_advice: true
```

---

## Part 3: MCP Integration Strategy

### 3.1 Standard MCP Tools (Use These)

**MCP Server: Filesystem**
- `list_directory(path)` - List files
- `read_file(path, start_line, end_line)` - Read file contents
- `write_file(path, contents)` - Create/write file
- `search_files(pattern)` - Find files by glob

**MCP Server: Git**
- `get_commit_history(branch)` - Get recent commits
- `create_branch(name, base)` - Create feature branch
- `commit(message, files)` - Commit changes
- `create_pull_request(title, body)` - Open PR

**MCP Server: SQLite**
- `query(sql)` - Execute SELECT/INSERT/UPDATE/DELETE
- `run_migration(script)` - Run schema migration

---

### 3.2 Custom CORTEX MCP Tools

**Tool Set 1: Audit Operations**
- `audit_query(filter, correlation_id)` - Query audit trail
- `audit_export(format)` - Export logs (JSON/CSV)
- `audit_verify_chain(start, end)` - Verify hash chain integrity

**Tool Set 2: Governance Operations**
- `governance_evaluate(rules, context)` - Evaluate rules against context
- `governance_add_rule(yaml)` - Add new rule to registry
- `governance_status()` - Show loaded rules + violations

**Tool Set 3: Orchestrator Operations**
- `orchestrator_list()` - List available orchestrators
- `orchestrator_execute(name, request)` - Trigger orchestrator
- `orchestrator_status()` - Show running orchestrators

**Tool Set 4: Evidence Operations**
- `evidence_create_bundle(test_results, code_changes)` - Create evidence
- `evidence_query(ac_id)` - Find evidence for AC-ID
- `evidence_export(bundle_id)` - Export bundle

**Tool Set 5: State Operations**
- `state_get(ac_id)` - Get current state
- `state_transition(ac_id, target_state)` - Attempt transition
- `state_list_active()` - List all active operations

---

### 3.3 MCP Tool Invocation Pattern

**Safe Invocation Protocol:**
```
1. Tool registration: @mcp_tool decorator + metadata
2. Schema validation: Copilot validates request against schema
3. Execution in sandbox: Tool runs with resource limits (timeout, memory)
4. Result wrapping: Result wrapped in ExecutionResult
5. Audit logging: Tool invocation logged with correlation_id
6. Error handling: Tool exception caught, wrapped in error response
```

**Example Tool Definition:**
```python
@mcp_tool(
    name="audit_query",
    description="Query audit log with filters",
    input_schema={
        "type": "object",
        "properties": {
            "filter": {
                "type": "string",
                "description": "SQL WHERE clause (e.g., 'ac_id = AC-AUDIT-001')"
            },
            "correlation_id": {
                "type": "string",
                "description": "Optional: specific operation UUID"
            },
            "limit": {
                "type": "integer",
                "default": 100,
                "description": "Max results to return"
            }
        },
        "required": ["filter"]
    }
)
def audit_query(filter: str, correlation_id: str = None, limit: int = 100) -> Dict[str, Any]:
    """Query audit log. Returns list of matching entries."""
    # Implementation
    pass
```

---

## Part 4: Base Infrastructure Interfaces

### 4.1 Execution Request / Response Types

**ExecutionRequest:**
```python
@dataclass
class ExecutionRequest:
    correlation_id: str  # UUID for tracing
    operation: str  # AC-ID or human-readable operation
    user_intent: str  # What user asked for
    context: Dict[str, Any]  # Operation-specific context
    timeout_seconds: int = 30  # Max execution time
    audit_mode: str = "development"  # development | production | hybrid
```

**ExecutionResult:**
```python
@dataclass
class ExecutionResult:
    success: bool  # True if operation completed successfully
    correlation_id: str  # Trace ID
    operation: str  # What was executed
    message: str  # Human-readable result
    data: Dict[str, Any]  # Operation-specific output
    evidence: Optional[EvidenceBundle] = None  # Proof of execution
    duration_ms: int = 0  # Execution time
    violations: List[GovernanceViolation] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
```

---

### 4.2 Governance Evaluation Interface

**GovernanceEvaluation:**
```python
@dataclass
class GovernanceEvaluation:
    passed: bool  # True if all rules passed
    rules_evaluated: int  # How many rules checked
    violations: List[GovernanceViolation]  # Failed rules
    execution_time_ms: float  # How long evaluation took
    registry_version: str  # Hash of loaded ruleset (for consistency check)
```

**GovernanceViolation:**
```python
@dataclass
class GovernanceViolation:
    rule_id: str  # e.g., "CORE-002"
    severity: str  # "blocked" | "warning" | "info"
    message: str  # Human-readable violation reason
    context: Dict[str, Any]  # What triggered violation
```

---

### 4.3 State Manager Interface

**LifecycleManager Methods:**
```python
class LifecycleManager:
    def get_state(self, ac_id: str) -> OperationState:
        """Get current state."""
        pass
    
    def transition(self, ac_id: str, target_state: str) -> bool:
        """Attempt state transition. Returns success."""
        pass
    
    def register_callback(self, state: str, callback: Callable):
        """Call callback when entering state."""
        pass
    
    def cancel(self, ac_id: str) -> bool:
        """Attempt to cancel operation."""
        pass
```

---

## Part 5: Implementation Sequence

### Phase 1: Foundations (Week 1)
- [x] ExecutionRequest / ExecutionResult types
- [x] BaseOrchestrator interface + Composite pattern
- [x] OrchestratorRegistry (plugin system)
- [x] Response template types
- [x] Governance evaluation interface
- [x] Unit tests: 100% interface coverage

### Phase 2: Integration (Week 2)
- [ ] MasterOrchestrator implementation (uses interfaces above)
- [ ] MCP tool registration system
- [ ] Response template rendering
- [ ] Error handling + fallback strategies
- [ ] Integration tests: All orchestrators work together

### Phase 3: Safety (Week 3)
- [ ] Distributed lock for state manager
- [ ] Circuit breaker for timeouts
- [ ] Exception isolation (process sandboxing)
- [ ] Graceful degradation (partial mode)
- [ ] Chaos tests: Kill random components, verify recovery

### Phase 4: Observability (Week 4)
- [ ] OpenTelemetry instrumentation
- [ ] Governance evaluation tracing
- [ ] Orchestrator dependency graph visualization
- [ ] Alerting: governance inconsistency, slow rules, broken chains

---

## Part 6: Framework Guidelines

### Design Principles

**1. Simplicity Over Completeness**
- ✅ Implement 80% of features cleanly
- ❌ Don't implement 100% with complexity
- Trade-off: Some advanced features deferred to Phase 2+

**2. Fail-Safe Defaults**
- ✅ Operations blocked until governance passes
- ✅ Secrets redacted by default (opt-in to log)
- ✅ Orchestrators isolated by default
- ❌ No "unsafe mode" that disables safety

**3. Observable From First Principles**
- ✅ Every operation traced (correlation_id from start)
- ✅ Governance evaluations timed + logged
- ✅ Orchestrator execution order visible
- ❌ No "magic" behavior that's hard to trace

**4. Graceful Degradation**
- ✅ If ADO fails, continue with other orchestrators
- ✅ If KG load fails, continue without intent clarification
- ✅ If evidence capture fails, log warning but don't block
- ❌ Cascade failures (one broken component stops everything)

---

### Code Organization

```
src/
├── orchestrators/
│   ├── base/
│   │   ├── base_orchestrator.py
│   │   ├── orchestrator_registry.py
│   │   └── execution_types.py
│   ├── core/
│   │   ├── master_orchestrator.py
│   │   ├── todo_manager.py
│   │   └── ...
│   ├── domain/
│   │   ├── planning_orchestrator.py
│   │   ├── tdd_master.py
│   │   └── ...
│   └── custom/
│       └── (user-defined orchestrators auto-discovered)
├── infrastructure/
│   ├── execution_request.py
│   ├── execution_result.py
│   ├── response_template.py
│   ├── governance_evaluation.py
│   └── lifecycle_manager.py
├── mcp/
│   ├── mcp_decorator.py
│   ├── audit_tools.py
│   ├── governance_tools.py
│   ├── orchestrator_tools.py
│   ├── evidence_tools.py
│   └── state_tools.py
└── tools/
    └── (existing helper utilities)
```

---

## Final Checklist

- [ ] All interfaces documented with examples
- [ ] Base orchestrator interface implemented (100 lines max)
- [ ] Response template types defined (50 lines)
- [ ] MCP tool decorators working
- [ ] Unit tests for all interfaces (coverage > 95%)
- [ ] No external framework dependencies
- [ ] Cross-platform tested (Windows + macOS + Linux)

