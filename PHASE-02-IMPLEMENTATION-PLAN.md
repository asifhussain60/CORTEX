# PHASE-02 Implementation Plan

**Phase**: Orchestration Core  
**Status**: IN_PROGRESS 🚀  
**AC-IDs**: 27 total  
**Predecessor**: PHASE-01 ✅ LOCKED  
**Estimated Duration**: 3-4 weeks  
**Start Date**: 2026-01-14

---

## Phase-02 Overview

Phase-02 focuses on building the orchestration core - the architecture that coordinates multiple domain-specific orchestrators and exposes them through the Model Context Protocol (MCP) for LLM integration.

### Key Deliverables
1. **Master Orchestrator** - Coordinates all domain orchestrators
2. **Orchestrator Registry** - Auto-registration via decorators
3. **MCP Server** - LLM integration point
4. **Governance Evaluator** - Rule evaluation pipeline
5. **Response Templates** - Configurable response system

---

## Architecture Decisions (9 AC-IDs)

### AR-006: Orchestrator Architecture

**AC-AR-006-01**: MasterOrchestrator coordinates domain orchestrators

```
Status: NOT STARTED
Description: MasterOrchestrator delegates to domain orchestrators based on 
             operation context. Implements coordinator pattern.
Test: test_master_orchestrator_coordination
Expected Behavior:
  1. MasterOrchestrator receives operation request
  2. Determines applicable domain orchestrators
  3. Delegates to appropriate orchestrator(s)
  4. Aggregates results
  5. Logs all delegation decisions to audit trail

Dependencies:
  - AR-002 (SQLite - for audit logging)
  - AR-003 (Decorators - for operation decoration)
  - AR-011 (Reference Orchestrator - pattern reference)

Implementation Approach:
  1. Extend base Orchestrator interface
  2. Use @orchestrator decorator for auto-registration
  3. Implement delegation logic
  4. Add comprehensive audit logging
  5. Create unit tests with mocked domain orchestrators
```

**AC-AR-006-02**: Orchestrators auto-registered via @orchestrator decorator

```
Status: NOT STARTED
Description: All orchestrators registered in OrchestratorRegistry via 
             decorator. Enables dynamic discovery and composition.
Test: test_orchestrator_auto_registration
Expected Behavior:
  1. @orchestrator decorator applied to orchestrator class
  2. Class automatically registered in OrchestratorRegistry
  3. Registry contains reference to all registered orchestrators
  4. Registry provides metadata (domain, version, capabilities)

Reference Implementation:
  - Use @mcp_tool pattern from AR-011 (PlanningOrchestrator)
  - Similar to @governance_enforced from AR-003

Implementation Approach:
  1. Create @orchestrator decorator
  2. Implement OrchestratorRegistry.register()
  3. Implement registry lookup methods
  4. Add metadata tracking
  5. Create comprehensive registry tests
```

**AC-AR-006-03**: Orchestrator registry queryable by domain

```
Status: NOT STARTED
Description: Registry supports querying orchestrators by domain (e.g., 
             "governance", "audit", "evidence"). Enables flexible composition.
Test: test_registry_query_by_domain
Expected Behavior:
  1. Registry stores domain information for each orchestrator
  2. Query by domain returns matching orchestrators
  3. Supports wildcards and patterns
  4. Returns metadata with results

Implementation Approach:
  1. Add domain field to orchestrator metadata
  2. Implement query methods
  3. Add indexing for performance
  4. Create comprehensive query tests
```

### AR-007: MCP Server Integration

**AC-AR-007-01**: MCP server starts and accepts connections

```
Status: NOT STARTED
Description: MCP server initializes, listens for connections, and accepts 
             client connections for LLM integration.
Test: test_mcp_server_startup
Expected Behavior:
  1. MCP server starts on configured port
  2. Server is in LISTENING state
  3. Server accepts incoming connections
  4. Connection is established with client
  5. Server logs connection events to audit trail

Dependencies:
  - AR-002 (SQLite - for audit logging)
  - AR-004 (Tiered Logging - for operation logging)

Implementation Approach:
  1. Create MCPServer class
  2. Implement connection handling
  3. Use asyncio for concurrent connections
  4. Add comprehensive logging
  5. Create tests with mock MCP clients
```

**AC-AR-007-02**: Orchestrators exposed as MCP tools

```
Status: NOT STARTED
Description: Each orchestrator's operations are exposed as MCP tools that 
             can be invoked by LLMs.
Test: test_orchestrators_as_mcp_tools
Expected Behavior:
  1. Each orchestrator method becomes an MCP tool
  2. Tools registered in MCPToolRegistry
  3. Tool schema includes parameters, return type, documentation
  4. Tools can be invoked through MCP protocol

Reference Implementation:
  - Use @mcp_tool pattern from AR-011 (PlanningOrchestrator)
  - Methods: plan_status, next_ac, enforce_phase_lock

Implementation Approach:
  1. Create @mcp_tool decorator
  2. Implement tool schema extraction
  3. Register orchestrator methods as tools
  4. Implement tool invocation handler
  5. Create integration tests
```

**AC-AR-007-03**: Governance context included in MCP responses

```
Status: NOT STARTED
Description: MCP responses include governance context (applicable rules, 
             phase locks, audit trail) so LLM has full context.
Test: test_governance_in_mcp_response
Expected Behavior:
  1. Tool response includes governance context
  2. Context includes applicable governance rules
  3. Context includes phase lock status
  4. Context includes recent audit entries
  5. Context formatted for LLM consumption

Implementation Approach:
  1. Create response wrapper with governance context
  2. Implement context extraction
  3. Add context formatting
  4. Create comprehensive tests
```

### AR-009: Custom Response Templates

**AC-AR-009-01**: Response templates loaded from cortex-brain/tier2/

```
Status: NOT STARTED
Description: Response templates loaded from configuration files enabling 
             customization without code changes.
Test: test_template_loading
Expected Behavior:
  1. TemplateEngine scans cortex-brain/tier2/ directory
  2. Loads JSON/YAML template files
  3. Parses template structure
  4. Makes templates available for use

Dependencies:
  - AR-001 (Governance - templates follow governance rules)

Implementation Approach:
  1. Create TemplateEngine class
  2. Implement directory scanning
  3. Add template parsing (JSON, YAML support)
  4. Create template registry
  5. Create comprehensive loading tests
```

**AC-AR-009-02**: Templates support variable substitution

```
Status: NOT STARTED
Description: Templates support variable placeholders that are substituted 
             with runtime values.
Test: test_template_variables
Expected Behavior:
  1. Templates contain placeholders (e.g., {{variable_name}})
  2. Substitution engine replaces placeholders with values
  3. Supports nested variables
  4. Handles missing variables gracefully

Implementation Approach:
  1. Implement variable parsing
  2. Create substitution engine
  3. Add type coercion support
  4. Implement error handling
  5. Create comprehensive substitution tests
```

**AC-AR-009-03**: Template inheritance working

```
Status: NOT STARTED
Description: Templates can inherit from base templates, allowing 
             customization through extension rather than replacement.
Test: test_template_inheritance
Expected Behavior:
  1. Child template specifies parent template
  2. Child template overrides specific blocks
  3. Parent template blocks used if not overridden
  4. Multi-level inheritance works

Implementation Approach:
  1. Add inheritance metadata to templates
  2. Implement template merging logic
  3. Handle override scenarios
  4. Validate inheritance chains
  5. Create comprehensive inheritance tests
```

---

## Functional Requirements (15 AC-IDs)

### FR-002: Governance Rule Evaluation (3 AC-IDs)

**AC-FR-002-01**: Rules evaluated in tier priority order

```
Status: NOT STARTED
Description: Rules evaluated in correct priority order: Tier 0 > Tier 1 > Tier 2
Test: test_rules_evaluated_in_tier_order
```

**AC-FR-002-02**: Returns pass/fail with violations

```
Status: NOT STARTED
Description: Evaluation returns PASS or FAIL with list of rule violations
Test: test_evaluation_returns_violations
```

**AC-FR-002-03**: Evaluation context includes operation metadata

```
Status: NOT STARTED
Description: Evaluation context includes operation, actor, resource, and 
             other metadata needed for rule matching
Test: test_evaluation_with_context
```

### FR-003: State Machine Context Tracking (3 AC-IDs)

**AC-FR-003-01**: State transitions logged with context

```
Status: NOT STARTED
Description: Each state transition is logged with full context
Test: test_state_transition_logging
```

**AC-FR-003-02**: Context preserved across transitions

```
Status: NOT STARTED
Description: Operation context is preserved through state transitions
Test: test_context_preservation_across_transitions
```

**AC-FR-003-03**: State history queryable

```
Status: NOT STARTED
Description: Full state transition history can be queried by AC-ID
Test: test_state_history_query
```

### FR-004: Evidence Bundle Auto-Generation (3 AC-IDs)

**AC-FR-004-01**: Bundles auto-created for orchestrator operations

```
Status: NOT STARTED
Description: Evidence bundles automatically created for all orchestrator 
             operations without explicit coding
Test: test_auto_bundle_creation_for_operations
```

**AC-FR-004-02**: Bundle contains operation artifacts

```
Status: NOT STARTED
Description: Bundles contain all relevant artifacts (logs, state, outputs)
Test: test_bundle_contains_artifacts
```

**AC-FR-004-03**: Bundle integrity verified

```
Status: NOT STARTED
Description: Bundle integrity verified before storage
Test: test_bundle_integrity_verification
```

### FR-005: Progress Tracking with Blockers (3 AC-IDs)

**AC-FR-005-01**: Blockers detected automatically

```
Status: NOT STARTED
Description: Blockers (missing AC-IDs, locked phases) detected and reported
Test: test_blocker_auto_detection
```

**AC-FR-005-02**: Blocker resolution tracked

```
Status: NOT STARTED
Description: Blocker resolution attempts and outcomes are tracked
Test: test_blocker_resolution_tracking
```

**AC-FR-005-03**: Phase progress calculated accurately

```
Status: NOT STARTED
Description: Phase progress percentage calculated from AC-ID completion
Test: test_phase_progress_calculation
```

### FR-006: Resumption with State Preservation (3 AC-IDs)

**AC-FR-006-01**: Partial state saved before long operations

```
Status: NOT STARTED
Description: Partial progress saved before long-running operations
Test: test_partial_state_save_before_long_ops
```

**AC-FR-006-02**: Operations resumable from saved state

```
Status: NOT STARTED
Description: Operations can resume from saved state without re-execution
Test: test_operation_resumption_from_state
```

**AC-FR-006-03**: No data loss on interruption

```
Status: NOT STARTED
Description: Interruptions do not cause data loss or inconsistency
Test: test_no_data_loss_on_interruption
```

---

## Special Implementation (3 AC-IDs)

### PR-001, PR-002, PR-003: Protocol Implementation Notes

- **PR-001**: Orchestrator composition patterns
- **PR-002**: MCP tool registration conventions
- **PR-003**: Response template organization

---

## Implementation Strategy

### Phase 1: Foundation (Days 1-5)
1. **AR-006-01 & 02**: Master Orchestrator & Auto-registration
   - Build coordinator pattern
   - Create orchestrator decorator
   - Set up registry

2. **AR-007-01**: MCP Server Startup
   - Initialize server
   - Connection handling
   - Basic logging

### Phase 2: Integration (Days 6-10)
1. **AR-007-02 & 03**: MCP Tool Exposure & Governance Context
   - Expose orchestrator methods as tools
   - Add governance context to responses
   - Test LLM integration

2. **FR-002**: Governance Rule Evaluation
   - Build rule evaluation pipeline
   - Handle tier precedence
   - Comprehensive testing

### Phase 3: Enhancement (Days 11-15)
1. **AR-009-01 to 03**: Response Templates
   - Template loading system
   - Variable substitution
   - Template inheritance

2. **FR-003 to 006**: State Machine & Progress Tracking
   - State machine context tracking
   - Evidence bundle auto-generation
   - Progress tracking with blockers
   - Resumption with state preservation

### Phase 4: Polish & Verification (Days 16-21)
1. Integration testing
2. Performance optimization
3. Documentation
4. Audit verification
5. Phase lock preparation

---

## Reference Implementations

### From PHASE-01 (Use as Pattern)

1. **AR-011: Reference Orchestrator (PlanningOrchestrator)**
   - Location: `src/orchestrators/domain/planning_orchestrator.py`
   - Use Case: Template for new orchestrators
   - Key Methods: get_mcp_tools(), plan_status(), next_ac()

2. **AR-003: Decorators**
   - Location: `src/core/decorators/`
   - Use Case: @governance_enforced, @audit_logged patterns
   - Apply to: Orchestrator methods

3. **AR-002: Database**
   - Location: `src/infrastructure/database.py`
   - Use Case: Audit logging, phase lock tracking
   - Apply to: All orchestrator operations

---

## Testing Strategy

### Unit Tests (Per AC-ID)
- Mock domain orchestrators
- Mock MCP clients
- Mock database
- Test error handling

### Integration Tests
- Multi-orchestrator coordination
- MCP server + tool exposure
- Governance evaluation + orchestration
- State machine + progress tracking

### System Tests
- Full workflow: request → orchestration → governance → response
- Edge cases and error scenarios
- Performance under load

---

## Success Criteria

- [ ] All 27 AC-IDs implemented
- [ ] All unit tests passing (target: 300+ new tests)
- [ ] Integration tests passing
- [ ] Audit trail verified
- [ ] No phase lock violations
- [ ] Hash chain integrity maintained
- [ ] Performance benchmarks met
- [ ] Documentation complete

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Orchestrator interaction complexity | HIGH | Use Reference Orchestrator as pattern, start simple |
| MCP integration issues | MEDIUM | Test with real MCP client early, mock extensively |
| Performance degradation | MEDIUM | Profile early, optimize hot paths |
| State preservation challenges | MEDIUM | Use existing CheckpointManager pattern |
| Template system flexibility | LOW | Extend gradually, learn from usage |

---

## Git Checkpoint Strategy

```
checkpoint: before AR-006-01
checkpoint: before AR-007-01
checkpoint: before AR-009-01

AC-AR-006-01: Master Orchestrator - tests passing
AC-AR-006-02: Orchestrator auto-registration - tests passing
AC-AR-007-01: MCP server startup - tests passing
AC-AR-007-02: MCP tool exposure - tests passing
...
phase-02: COMPLETED - all 27 AC-IDs implemented, audit verified
```

---

## Next Actions

1. ✅ Review this implementation plan
2. ⏭️ Start with AR-006-01: Create MasterOrchestrator
3. ⏭️ Set up comprehensive test suite
4. ⏭️ Reference AR-011 (PlanningOrchestrator) patterns
5. ⏭️ Create git checkpoint before AR-006-01

---

**Ready to begin PHASE-02 implementation!** 🚀
