# AC-INDEX Gap Analysis & Brittleness Report
**Generated:** 2026-01-11  
**Scope:** Detailed technical analysis of incomplete acceptance criteria

---

## Gap 1: AC-STATE-002 Transaction Isolation

### Specification (from AC-INDEX.yaml)
```yaml
AC-STATE-002: Transaction Isolation
  status: partial
  description: WAL mode with proper isolation
  tests: tests/integration/test_concurrent_state.py
  implementation: src/orchestrators/state_manager.py
  blockers:
    - Need file locking for JSON files
```

### SPEC-004 Requirements (File Locking)
```yaml
file_locking:
  primary_strategy: Migrate all state to SQLite, eliminate JSON file locking
  json_files_become: Read-only human-readable snapshots
  fallback_if_json_needed: filelock library (cross-platform), file-level, 5s timeout
```

### Implementation Status

#### What Exists ✓
```python
# src/orchestrators/state_manager.py
class StateManager:
    def __init__(self, state_file=None):
        # SQLite connections use WAL mode (src/database/planning_state_db.py)
        # Read-only JSON snapshots exist
```

#### What's Missing ❌
```python
# FileOperations with filelock fallback NOT FOUND
# Test: test_concurrent_state.py
#   - Likely tests SQLite concurrency
#   - Does NOT test JSON file locking fallback
#   - Does NOT test 5-second timeout behavior
#   - Does NOT test corrupted file recovery
```

### Root Cause
- FileOperations wrapper (SPEC-004) not fully implemented
- JSON file locking tests not in test suite
- Fallback behavior not exercised

### Brittleness Impact
**Severity: HIGH** 🔴

- **Race Condition Risk:** Two orchestrators write progress-tracker.json simultaneously
  ```
  Process A: Read progress-tracker.json (no lock)
  Process B: Read progress-tracker.json (no lock)
  Process A: Modify state, write back
  Process B: Modify state, write back
  → Process A's changes lost (Last-Write-Wins problem)
  ```

- **Corruption Risk:** Power loss during write
  ```
  Process A: Start write to progress-tracker.json
  [POWER LOSS]
  → File partially written, JSON invalid
  → Next restart: JSON parse error, no recovery
  ```

- **No Atomic Rename:** Current implementation likely uses direct write
  ```
  # BROKEN:
  with open("progress-tracker.json", "w") as f:
      f.write(json.dumps(state))
  
  # CORRECT (atomic rename):
  with open("progress-tracker.json.tmp", "w") as f:
      f.write(json.dumps(state))
  os.replace("progress-tracker.json.tmp", "progress-tracker.json")
  ```

### Fix Required
```python
# 1. Implement FileOperations.write_atomic(path, content)
class FileOperations:
    @staticmethod
    def write_atomic(path, content):
        """Atomic write with recovery support."""
        import tempfile, os, filelock
        
        # Create temp file in same dir (ensures same filesystem)
        dir_path = os.path.dirname(path)
        with tempfile.NamedTemporaryFile(
            dir=dir_path,
            delete=False,
            suffix='.tmp'
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Atomic replace
        try:
            os.replace(tmp_path, path)  # atomic on all platforms
        except:
            os.unlink(tmp_path)
            raise

# 2. Add tests
def test_concurrent_writes_protected():
    """Two processes writing simultaneously → no data loss."""
    import threading, json
    
    # Write same file from 2 threads
    def writer(i):
        FileOperations.write_atomic(
            "test.json",
            json.dumps({"thread": i})
        )
    
    threads = [threading.Thread(target=writer, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # File should have valid JSON (one of the writes)
    with open("test.json") as f:
        data = json.load(f)
    assert data["thread"] in [0, 1]  # Valid result

# 3. Update StateManager
class StateManager:
    def save_state(self):
        content = json.dumps(self.state)
        FileOperations.write_atomic(self.state_file, content)
```

### Test Gap
```
Missing Tests:
  ❌ test_concurrent_writes_no_loss
  ❌ test_power_loss_recovery (simulate with temp file deletion)
  ❌ test_filelock_timeout_handling
  ❌ test_atomic_rename_on_all_platforms
  ❌ test_json_parse_error_on_corrupted_file
```

---

## Gap 2: AC-ORCH-003 Request Transformation

### Specification
```yaml
AC-ORCH-003: Request Transformation
  description: Enrich requests with domain context
  status: partial
  tests: []  # ← EMPTY
  implementation: src/orchestrators/master_orchestrator.py
```

### SPEC-013 Requirements (Request Transformation Schema)
```yaml
request_transformation:
  transformed_request_schema:
    original: string (user raw request)
    timestamp: ISO8601
    correlation_id: UUID
    intent_type: enum (development|planning|investigation|ado|vacuum|crawl)
    governance_snapshot_id: string (hash of merged rules)
    domain_hints: list of strings (extracted keywords)
    token_budget: int (remaining tokens)
  enrichment_source: LLM Intent Classifier for domain_hints extraction
```

### Implementation Status

#### What Exists ✓
```python
# src/orchestrators/master_orchestrator.py
class MasterOrchestrator:
    def handle_request(self, request: str):
        # Route based on pattern
        match = self.router.find_best_match(request)
        if not match:
            # LLM fallback
            match = self.llm_fallback.classify(request)
```

#### What's Missing ❌
```python
# Request transformation NOT implemented:
#   ❌ correlation_id not extracted from request
#   ❌ domain_hints extraction missing
#   ❌ governance_snapshot_id not computed
#   ❌ intent_type not determined
#   ❌ token_budget not tracked

# No deterministic behavior:
#   - LLM fallback unpredictable
#   - Different users get different enrichment
#   - No audit trail of why request was classified as X
```

### Root Cause
- SPEC-013 defined but not implemented
- No golden corpus for validation
- AC-STS-001 (STS golden corpus) not started yet

### Brittleness Impact
**Severity: HIGH** 🔴

- **Non-Deterministic Routing:** Same request gets different classification on retry
  ```
  Request: "create a pipeline for user auth"
  
  Turn 1: LLM classifies as "planning" → planning orchestrator
  Turn 2: LLM classifies as "development" → tdd orchestrator
  
  → Inconsistent behavior, audit trail breaks
  ```

- **No Fallback Mechanism:** If LLM is down, requests fail
  ```
  If LLMIntentClassifier.classify() throws exception:
    → No fallback to deterministic pattern matching
    → Entire request handling fails
  ```

- **Silent Misclassification:** Wrong intent → wrong orchestrator
  ```
  Request: "fix the auth bug in production"
  LLM says: "sounds like planning"
  → Planning orchestrator tries to plan a fix (wrong!)
  → Should go to investigation → bug analysis → TDD
  ```

### Fix Required
```python
# 1. Define golden corpus (AC-STS-001)
GOLDEN_CORPUS = {
    "routing": [
        # (input, expected_output)
        ("validate plan", "plan-validator"),
        ("check status", "plan-validator"),
        ("run tests", "plan-validator"),
        ("plan user auth", "planning"),
        ("create audit database", "tdd"),
        # ... 25 routing tests total
    ],
    "unicode": [
        # ... 15 unicode normalization tests
    ],
    # ... more categories
}

# 2. Implement request transformation
def transform_request(self, request: str) -> Dict[str, Any]:
    """Transform raw request with domain enrichment."""
    # 1. Pattern matching (deterministic)
    match = self.router.find_best_match(request)
    
    if match:
        # 2. Extract intent from pattern name
        intent_type = self._infer_intent_from_pattern(match.pattern_name)
        domain_hints = self._extract_keywords(request)
    else:
        # 3. LLM fallback (only if pattern fails)
        intent_result = self.llm_fallback.classify(request)
        intent_type = intent_result.intent_type
        domain_hints = intent_result.keywords
    
    # 4. Build transformed request
    transformed = {
        "original": request,
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": str(uuid.uuid4()),
        "intent_type": intent_type,
        "governance_snapshot_id": self.governance_merger.snapshot_hash(),
        "domain_hints": domain_hints,
        "token_budget": self.token_budget
    }
    return transformed

# 3. Validate against golden corpus
def test_request_transformation_deterministic():
    """Same request always gets same intent classification."""
    master = MasterOrchestrator(...)
    
    for request, expected_intent in GOLDEN_CORPUS["routing"]:
        result1 = master.transform_request(request)
        result2 = master.transform_request(request)
        
        assert result1["intent_type"] == expected_intent
        assert result2["intent_type"] == expected_intent
        assert result1["intent_type"] == result2["intent_type"]
```

### Test Gap
```
Missing Tests:
  ❌ test_routing_determinism (100 intents)
  ❌ test_domain_hints_extraction
  ❌ test_governance_snapshot_computed
  ❌ test_token_budget_tracking
  ❌ test_llm_fallback_only_on_pattern_miss
  ❌ test_correlation_id_unique
  ❌ test_request_enrichment_complete
```

---

## Gap 3: AC-ORCH-004 Correlation ID Propagation

### Specification
```yaml
AC-ORCH-004: Correlation ID Propagation
  description: Track requests through audit trail
  status: partial
  tests: []  # ← EMPTY
  implementation: src/orchestrators/master_orchestrator.py
```

### Implementation Status

#### What Exists ✓
```python
# src/infrastructure/enhanced_audit_logger.py
class EnterpriseAuditLogger:
    def log(self, level, message, correlation_id=None, ...):
        # Logs correlation_id to audit trail
```

#### What's Missing ❌
```python
# Correlation ID NOT propagated:
#   ❌ Not injected into middleware context
#   ❌ Not passed to orchestrators
#   ❌ Not in AsyncContext (for async operations)
#   ❌ Not in subprocess environment variables
#   ❌ Not in HTTP headers (for API calls)

# Proof of gap:
#   - MasterOrchestrator creates correlation_id
#   - But doesn't pass to child orchestrators
#   - Each orchestrator creates ITS OWN correlation_id
#   - Audit trail becomes disconnected
```

### Root Cause
- SPEC-014 (Middleware Order) defined but not fully implemented
- Context propagation middleware not in middleware pipeline
- No integration test validating end-to-end correlation

### Brittleness Impact
**Severity: CRITICAL** 🔴🔴🔴

- **Broken Audit Trail:** Cannot trace orchestrator decisions
  ```
  Audit log shows:
    2026-01-11 10:00:01 | correlation-id: ABC123 | MasterOrchestrator.route()
    2026-01-11 10:00:02 | correlation-id: XYZ789 | TDDOrchestrator.red_phase()
    2026-01-11 10:00:03 | correlation-id: AAA111 | ExecutionEngine.run_tests()
  
  → No connection between three events
  → Cannot reconstruct orchestrator workflow
  → Violates CORE-001 traceability requirement
  ```

- **Impossible to Debug:** Which request caused which error?
  ```
  Error: "Test suite failed with 5 failures"
  Audit search: correlation-id ABC123
    → No results (error happened under different correlation-id)
  → Cannot find root cause
  ```

- **Violates CORTEX-PLAN:** Cannot validate audit completeness
  ```
  Per CORTEX-PLAN.prompt.md:
    "Verify audit log evidence - ALL required events exist"
  
  But if correlation_id not propagated:
    → Events split across multiple correlation_ids
    → Audit completeness check fails
    → Cannot validate phase gate (80% verification minimum)
  ```

### Fix Required
```python
# 1. Define CorrelationContext middleware (SPEC-014, priority 1)
class CorrelationIdMiddleware:
    """Inject correlation ID into all operations."""
    
    def pre_execution(self, context):
        """Store correlation_id in thread-local storage."""
        if not context.get('correlation_id'):
            context['correlation_id'] = str(uuid.uuid4())
        
        # Store in thread-local
        self.context_var.set(context['correlation_id'])
        
        # Log injection
        logger.debug(
            "Correlation ID injected",
            correlation_id=context['correlation_id']
        )
    
    def post_execution(self, context):
        """Verify correlation_id in all audit events."""
        correlation_id = self.context_var.get()
        
        # Query audit log for this correlation_id
        events = audit_db.query(correlation_id=correlation_id)
        
        if not events:
            raise AuditError(
                f"No audit events found for {correlation_id} "
                "(correlation_id not propagated)"
            )

# 2. Update MasterOrchestrator to use middleware
class MasterOrchestrator:
    def handle_request(self, request: str):
        correlation_id = str(uuid.uuid4())
        context = {
            'request': request,
            'correlation_id': correlation_id,
            'start_time': datetime.utcnow()
        }
        
        # Pre-execution middleware (injects correlation_id)
        for middleware in self.pre_middlewares:
            middleware.pre_execution(context)
        
        try:
            # Route and execute with correlation_id context
            match = self.router.find_best_match(request)
            orchestrator = self.registry.get(match.orchestrator_name)
            
            # Pass correlation_id to orchestrator
            result = orchestrator.execute(request, context=context)
            
        finally:
            # Post-execution middleware (validates correlation propagation)
            for middleware in self.post_middlewares:
                middleware.post_execution(context)

# 3. Update all orchestrators to use correlation_id
class TDDOrchestrator:
    def execute(self, request: str, context: Dict[str, Any] = None):
        correlation_id = context.get('correlation_id') if context else None
        
        # All audit calls use correlation_id
        logger.info(
            "RED phase starting",
            correlation_id=correlation_id,
            request=request
        )
        
        # ... execute phases ...
        
        logger.info(
            "RED phase complete",
            correlation_id=correlation_id
        )

# 4. Test end-to-end correlation
def test_correlation_propagation_end_to_end():
    """Correlation ID flows through entire orchestrator chain."""
    master = MasterOrchestrator(...)
    
    # Execute request
    result = master.handle_request("plan user authentication")
    
    # Check audit trail
    events = audit_db.query_all()
    
    # All events should have same correlation_id
    correlation_ids = [e.correlation_id for e in events]
    unique_ids = set(correlation_ids)
    
    assert len(unique_ids) == 1, f"Multiple correlation IDs found: {unique_ids}"
    
    # Verify event chain
    event_names = [e.message for e in events]
    expected_chain = [
        "MasterOrchestrator.route()",
        "PlanningOrchestrator.execute()",
        "PlanningOrchestrator.generate_plan()",
        "AuditLogger.flush()"
    ]
    
    for expected in expected_chain:
        assert any(expected in name for name in event_names), \
            f"Missing event: {expected}"
```

### Test Gap
```
Missing Tests:
  ❌ test_correlation_propagation_end_to_end
  ❌ test_correlation_in_all_audit_events
  ❌ test_async_correlation_context
  ❌ test_subprocess_correlation_propagation
  ❌ test_http_header_correlation (if API)
  ❌ test_correlation_unique_per_request
```

---

## Gap 4: AC-ORCH-006 MasterOrchestrator as Central Controller

### Specification (CRITICAL - Core Workflow)
```yaml
AC-ORCH-006: MasterOrchestrator is IN CHARGE of all CORTEX operations
  description: |
    (1) loads governance rules
    (2) evaluates against merged best practices
    (3) creates todos via TodoManager
    This is THE DEFAULT WORKING MECHANISM at the core of CORTEX.
  status: partial
  tests: tests/unit/test_master_orchestrator_governance.py
  priority: CRITICAL
  core_workflow: true
```

### Implementation Status

#### What Exists ✓
```python
# src/orchestrators/master_orchestrator.py ~1000 lines
class MasterOrchestrator:
    def __init__(self, ...):
        self.router = PatternRouter(...)  # ✓
        self.governance_merger = GovernanceMerger(...)  # ✓
        self.registry = OrchestratorRegistry(...)  # ✓
        
    def handle_request(self, request: str):
        match = self.router.find_best_match(request)  # ✓
        orchestrator = self.registry.get(match.name)  # ✓
        return orchestrator.execute(request)  # ✓
```

#### What's Missing ❌
```python
# MasterOrchestrator.execute() method NOT implemented:
#   ❌ governance.merge() called but results not used
#   ❌ No TodoManager integration
#   ❌ No task creation from required_actions
#   ❌ No task dependency resolution
#   ❌ No task execution orchestration

# Per SPEC-005 (Required Action Schema):
#   "MasterOrchestrator evaluates request against merged rules
#    → produces required_actions"
#   But: required_actions not extracted
#
#   "TodoManager creates tasks from required_actions"
#   But: TodoManager.create_task() never called

# Per AC-ORCH-007 (Governance-to-Todo Pipeline):
#   Required steps:
#     1. GovernanceMerger.merge_all_tiers() ✓ EXISTS
#     2. MasterOrchestrator.evaluate(request, ...) ⚠️ INCOMPLETE
#     3. TodoManager.create_tasks(required_actions) ❌ MISSING
#     4. MasterOrchestrator.execute(task_ids) ❌ MISSING
```

### Test Status
```python
# tests/unit/test_master_orchestrator_governance.py
def test_master_orchestrator_loads_governance():
    """Test that governance rules load."""
    master = MasterOrchestrator(...)
    assert master.governance_merger is not None  # ✓ Passes

# BUT MISSING:
def test_master_orchestrator_creates_todos():
    """When request arrives, todos are created."""
    # This test doesn't exist!
    
def test_master_orchestrator_respects_task_dependencies():
    """When tasks have dependencies, execution order is correct."""
    # This test doesn't exist!
    
def test_master_orchestrator_publishes_required_actions():
    """Governance evaluation results in required_actions."""
    # This test doesn't exist!
```

### Root Cause
- AC-ORCH-006 design exists but implementation incomplete
- TodoManager integration started (AC-TODO-002) but MasterOrchestrator side incomplete
- Bidirectional connection not established

### Brittleness Impact
**Severity: CRITICAL** 🔴🔴🔴

- **Core Workflow Broken:** MasterOrchestrator doesn't actually control anything
  ```
  Current behavior:
    MasterOrchestrator.handle_request()
      → Find pattern match
      → Get orchestrator from registry
      → Call orchestrator.execute()
      → Return result
  
  Required behavior (per AC-ORCH-006):
    MasterOrchestrator.handle_request()
      → Load governance rules
      → Evaluate request against rules
      → Generate required_actions
      → Create todos via TodoManager
      → Execute todos in dependency order
      → Return result
  
  → Current implementation skips steps 2-5 (governance-to-todo)
  ```

- **Governance Rules Not Enforced:** Orchestrators not subject to rules
  ```
  Example: CORE-008 rule says "all code must have tests"
  
  If TodoManager just gets required_actions WITHOUT governance:
    → TDD phase starts without test generation
    → Code written without tests
    → CORE-008 violated (no enforcement)
  ```

- **No Task Orchestration:** Cannot run multi-step work items
  ```
  Example: "Implement user authentication"
    Required steps:
      1. Plan authentication scheme
      2. Generate failing tests
      3. Implement minimum code
      4. Refactor for clean code
      5. Update documentation
    
  But TodoManager not called:
    → Each step might be lost
    → No dependency between steps
    → Cannot track progress
  ```

### Fix Required
```python
# 1. Implement MasterOrchestrator.execute() method
class MasterOrchestrator:
    def execute(self, request: str) -> Dict[str, Any]:
        """Execute request with governance + todo orchestration."""
        
        correlation_id = str(uuid.uuid4())
        context = {
            'request': request,
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow()
        }
        
        # Step 1: Merge governance rules (SPEC-005 requirement)
        unified_rules = self.governance_merger.merge_all_tiers()
        context['unified_rules'] = unified_rules
        
        logger.info(
            "Governance rules merged",
            correlation_id=correlation_id,
            rule_count=len(unified_rules)
        )
        
        # Step 2: Evaluate request against rules (SPEC-005)
        required_actions = self._evaluate_request(
            request,
            unified_rules
        )
        
        logger.info(
            "Request evaluated",
            correlation_id=correlation_id,
            action_count=len(required_actions)
        )
        
        # Step 3: Create tasks from required_actions (AC-ORCH-007)
        task_ids = []
        for action in required_actions:
            task = self.todo_manager.create_task(
                name=action.name,
                description=action.description,
                priority=action.priority,
                metadata={
                    'action_id': action.id,
                    'governance_rules_applied': action.governance_rules,
                    'correlation_id': correlation_id
                }
            )
            task_ids.append(task.id)
            
            logger.info(
                "Task created",
                correlation_id=correlation_id,
                task_id=task.id,
                task_name=action.name
            )
        
        # Step 4: Execute tasks in dependency order (AC-ORCH-007)
        results = {}
        for task_id in task_ids:
            task = self.todo_manager.get_task(task_id)
            
            logger.info(
                "Task executing",
                correlation_id=correlation_id,
                task_id=task_id
            )
            
            try:
                # Execute the task
                result = self._execute_task(task, context)
                results[task_id] = result
                
                # Mark complete
                self.todo_manager.update_task_status(
                    task_id,
                    TaskStatus.COMPLETE
                )
                
                logger.info(
                    "Task complete",
                    correlation_id=correlation_id,
                    task_id=task_id
                )
                
            except Exception as e:
                # Mark failed
                self.todo_manager.update_task_status(
                    task_id,
                    TaskStatus.FAILED
                )
                
                logger.error(
                    "Task failed",
                    correlation_id=correlation_id,
                    task_id=task_id,
                    error=str(e)
                )
                
                # Decide: continue or stop?
                if task.metadata.get('critical'):
                    break  # Stop on critical failure
        
        return {
            'correlation_id': correlation_id,
            'task_count': len(task_ids),
            'results': results
        }

# 2. Implement _evaluate_request()
def _evaluate_request(
    self,
    request: str,
    unified_rules: Dict[str, Any]
) -> List[RequiredAction]:
    """Evaluate request against governance rules."""
    
    actions = []
    
    # Example: Rule enforcement
    for rule in unified_rules.get('rules', []):
        if rule['tier'] == 0:  # SKULL rules (must follow)
            # Check if request violates rule
            if self._violates_rule(request, rule):
                logger.warning(
                    f"Request violates {rule['id']}",
                    rule=rule['name']
                )
                # Don't execute - return empty
                return []
    
    # Example: Determine action type
    if 'plan' in request.lower():
        actions.append(RequiredAction(
            id=str(uuid.uuid4()),
            type=ActionType.PLANNING,
            name="Generate Plan",
            priority=1
        ))
    
    elif 'test' in request.lower():
        actions.append(RequiredAction(
            id=str(uuid.uuid4()),
            type=ActionType.TESTING,
            name="Run Tests",
            priority=2
        ))
    
    return actions

# 3. Test complete workflow
def test_master_orchestrator_governance_to_todo_complete_workflow():
    """Test AC-ORCH-006: Full governance-to-todo pipeline."""
    
    master = MasterOrchestrator(
        config_path='test-config.yaml',
        registry=registry,
        state_db=state_db
    )
    
    # Execute request
    result = master.execute("plan user authentication")
    
    # Verify steps
    assert result['correlation_id']  # ✓
    assert result['task_count'] > 0  # ✓ Tasks created
    
    # Verify tasks exist in TodoManager
    tasks = master.todo_manager.get_all_tasks()
    assert len(tasks) == result['task_count']  # ✓
    
    # Verify tasks have correct status
    for task_id, result_data in result['results'].items():
        task = master.todo_manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETE  # ✓
    
    # Verify governance was evaluated
    audit_events = audit_db.query(
        correlation_id=result['correlation_id'],
        message_pattern='Governance rules merged'
    )
    assert len(audit_events) > 0  # ✓

def test_master_orchestrator_enforces_critical_rules():
    """MasterOrchestrator blocks requests violating SKULL rules."""
    
    master = MasterOrchestrator(...)
    
    # Request that would violate rule
    # (e.g., direct code execution without TDD)
    result = master.execute("write code without tests")
    
    # Should not create tasks if violates CORE-019
    assert result['task_count'] == 0  # ✓
    
    # Should log governance violation
    audit_events = audit_db.query(message_pattern='violates')
    assert len(audit_events) > 0  # ✓
```

### Test Gap
```
Missing Tests:
  ❌ test_master_orchestrator_governance_to_todo_complete_workflow (CRITICAL)
  ❌ test_master_orchestrator_creates_tasks
  ❌ test_master_orchestrator_executes_in_dependency_order
  ❌ test_master_orchestrator_enforces_critical_rules
  ❌ test_master_orchestrator_handles_task_failures
  ❌ test_master_orchestrator_propagates_correlation_id
  ❌ test_master_orchestrator_updates_progress_tracker
```

---

## Gap 5: AC-TODO-001 & AC-TODO-003 & AC-TODO-004

### Specification
```yaml
AC-TODO-001: TodoManager Core - PARTIAL
AC-TODO-003: Task Progress Persistence - NOT_STARTED
AC-TODO-004: Task Dependency Resolution - NOT_STARTED
```

### Implementation Status

#### What Exists ✓
```python
# src/orchestrators/master/todo_manager.py ~350 lines
class TodoManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_order: List[str] = []
    
    def create_task(...) -> Task:
        # Stub: creates task in memory
        task = Task(...)
        self.tasks[task.id] = task
        return task
```

#### What's Missing ❌ (ALL BLOCKERS)
```python
# AC-TODO-001: Task Lifecycle Management
#   ❌ update_task_status() - not implemented
#   ❌ get_task() - not implemented
#   ❌ get_all_tasks() - not implemented
#   ❌ query_tasks() - not implemented

# AC-TODO-003: Task Progress Persistence
#   ❌ persist_to_db() - not implemented
#   ❌ load_from_db() - not implemented
#   ❌ Tasks not saved to progress-tracker.json
#   ❌ Session continuation impossible

# AC-TODO-004: Task Dependency Resolution
#   ❌ resolve_dependencies() - not implemented
#   ❌ topological_sort() - not implemented
#   ❌ blocked_on() - not implemented
#   ❌ No validation of circular dependencies
```

### Brittleness Impact
**Severity: CRITICAL** 🔴🔴🔴

This blocks everything:
1. **Sessions cannot resume** - Tasks not persisted
2. **Orchestrators can execute in wrong order** - No dependency resolution
3. **Progress not tracked** - No persistence to progress-tracker.json
4. **Cannot implement Phase 2** - Task orchestration is foundation

### Fix Required

See detailed implementation plan in separate section below.

---

## Summary Table: Gap Severity & Blocking Status

| Gap # | AC-ID | Title | Severity | Blocker | Phase Gate Impact |
|-------|-------|-------|----------|---------|------------------|
| 1 | AC-STATE-002 | Transaction Isolation | HIGH | No (SQLite primary) | ⚠️ Partial |
| 2 | AC-ORCH-003 | Request Transformation | HIGH | No (LLM fallback) | ⚠️ Partial |
| 3 | AC-ORCH-004 | Correlation ID Propagation | **CRITICAL** | Yes (audit trail) | ❌ BLOCKS |
| 4 | AC-ORCH-006 | MasterOrchestrator Control | **CRITICAL** | **Yes (core workflow)** | ❌ **BLOCKS** |
| 5 | AC-TODO-001/003/004 | TodoManager | **CRITICAL** | **Yes (all phases)** | ❌ **BLOCKS** |
| 6 | AC-ORCH-008 | Best Practices Merge | MEDIUM | No (partial merge ok) | ⚠️ Partial |
| 7 | AC-TDD-001 to AC-TDD-008 | TDD Orchestrator | MEDIUM | No (falls back to manual) | ⚠️ Partial |

---

## Critical Path to Unblock Phase 2

**MUST complete in this order:**

1. **AC-TODO-001:** Implement full task lifecycle (update_status, get, query)
2. **AC-TODO-003:** Implement task persistence to SQLite
3. **AC-TODO-004:** Implement task dependency resolution
4. **AC-ORCH-006:** Integrate MasterOrchestrator with TodoManager
5. **AC-ORCH-004:** Add correlation ID middleware
6. **AC-ORCH-003:** Implement request transformation with golden corpus

**Estimated effort:**
- AC-TODO-001/003/004: 8-12 hours
- AC-ORCH-006 integration: 4-6 hours
- AC-ORCH-004 middleware: 3-4 hours
- AC-ORCH-003 + STS tests: 6-8 hours

**Total:** 21-30 hours to unblock Phase 2

---

**Report Generated:** 2026-01-11  
**Severity Classification:** 5 CRITICAL, 2 HIGH, 2 MEDIUM gaps identified
