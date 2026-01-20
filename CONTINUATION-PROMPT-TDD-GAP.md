# CORTEX TDD Gap Remediation - Implementation Continuation Prompt
# Generated: 2026-01-20
# Session Handoff: Complete 125 Missing Module Implementations

## EXECUTIVE SUMMARY

You are continuing autonomous implementation of CORTEX. Previous session completed:
- **P0 Priority**: Context-aware governance (GOV-CTX-001) - 75 tests passing, 28/29 rules now functional
- **P1 Priority**: Intelligence modules (INT-001/002/003) - 42 tests passing for routing, duration, and error tracking

**CURRENT TASK**: Implement 125 missing modules that have TDD tests but no implementations.

**IMPACT**: 170 test errors due to import failures blocking production readiness.

**REPOSITORY**: CORTEX (branch: CORTEX, owner: asifhussain60)

**WORKING DIRECTORY**: D:\PROJECTS\CORTEX

## PROBLEM STATEMENT

### Root Cause
Package consolidation from `src/` → `cortex/` orphaned test imports. Tests reference `src.*` modules that don't exist in the consolidated structure.

### Current State
- **Test Collection**: ~262 tests collected
- **Import Failures**: 170+ errors
- **Missing Modules**: 125 across multiple categories
- **Test Files Affected**: ~200 files

### Breakdown by Category
```yaml
core: 87               # Largest gap - orchestrator, knowledge, governance
orchestrators: 9       # Core orchestration implementations
domain: 14            # Domain-specific brain modules
infrastructure: 5      # Database, logging, caching
mcp: 1                # MCP server SDK
other: 9              # CLI, confirmation, versioning, etc.
```

## IMPLEMENTATION STRATEGY

### Three-Phase Approach

#### PHASE 1: Stub Generation (1-2 days)
**Goal**: Resolve all import errors so tests collect without failures

**Deliverables**:
- 125 stub .py files in correct `cortex/` locations
- All imports resolve (tests collect without import errors)
- Each stub has correct module structure and function signatures
- Type hints for all function signatures (CORE-011 compliant)
- Placeholder docstrings (CORE-012 compliant)

**Method**: 
```python
# Example stub structure
"""
Module: cortex/core/orchestrator/conversation_protocol.py
Stub implementation - requires business logic
"""

from typing import Dict, Any, Optional
from cortex.brain.core.result import Result, Ok, Err

class ConversationProtocol:
    \"\"\"Manages conversation flow and state.\"\"\"
    
    def __init__(self) -> None:
        \"\"\"Initialize conversation protocol.\"\"\"
        pass
    
    def validate_turn(self, context: Dict[str, Any]) -> Result[bool]:
        \"\"\"
        Validate conversation turn.
        
        Args:
            context: Turn context
            
        Returns:
            Result containing validation status
        \"\"\"
        # TODO: Implement validation logic
        return Ok(True)
```

#### PHASE 2: Implementation (8-12 days)
**Goal**: Working implementations with actual business logic

**Priority Tiers**:

**P0 - Critical (Blocks All Tests)** - Days 1-3:
1. `core.decorators.orchestrator_decorator` - 50+ test references
2. `core.orchestrator.conversation_protocol` - 35+ test references
3. `core.interfaces.i_orchestrator` - Interface definition
4. `infrastructure.database` - 15+ test dependencies
5. `infrastructure.enhanced_audit_logger` - Cross-cutting concern

**P1 - High (Blocks Major Features)** - Days 4-6:
6. `core.knowledge.knowledge_graph` - E2E tests blocked
7. `core.knowledge.unified_service` - Knowledge ecosystem
8. `core.governance_pregate` - Governance validation
9. `core.governance_registry` - Rule management
10. `orchestrators.core.master_orchestrator` - Central coordination

**P2 - Medium (Blocks Specific Features)** - Days 7-9:
11. `core.intent.intent_router` - Intent classification
12. `core.intent.lens_context_builder` - Context extraction
13. `mcp.server_sdk` - MCP protocol implementation
14. `domain_brain.*` (14 modules) - Domain-specific logic
15. `orchestrators.response.*` - Response handling

**P3 - Low (Nice to Have)** - Days 10-12:
16. `devx.*` - Developer experience tools
17. `templates.*` - Template management
18. `versioning.*` - Version control
19. `observability.*` - Monitoring and metrics

**Implementation Standards**:
- Type hints on all functions (CORE-011)
- Google-style docstrings (CORE-012)
- Result monad for error handling (CORE-019)
- No bare except clauses (CORE-013)
- Incremental commits <500 lines (CORE-001)
- Git checkpoints every 2-3 modules (CORE-026)

#### PHASE 3: Validation (3-4 days)
**Goal**: Production-ready validated implementation

**Deliverables**:
- ≥98% test pass rate
- Integration test validation
- E2E smoke tests passing
- Performance benchmarks within SLAs

## DETAILED MODULE SPECIFICATIONS

### Critical Path: Top 10 Modules

#### 1. core.decorators.orchestrator_decorator
```yaml
location: cortex/core/decorators/orchestrator_decorator.py
purpose: Decorator for orchestrator lifecycle management
dependencies:
  - cortex.brain.core.result
  - cortex.infrastructure.enhanced_audit_logger
key_functions:
  - orchestrator_lifecycle(): Manages pre/post execution hooks
  - governance_check(): Validates governance compliance
  - audit_wrapper(): Logs execution details
tests: 50+ references across test suite
```

#### 2. core.orchestrator.conversation_protocol
```yaml
location: cortex/core/orchestrator/conversation_protocol.py
purpose: Conversation state and flow management
dependencies:
  - cortex.brain.core.governance_registry
  - cortex.brain.core.rule_evaluator
key_classes:
  - ConversationProtocol: Main protocol manager
  - TurnValidator: Validates conversation turns
  - StateManager: Manages conversation state
tests: 35+ references in conversation tests
```

#### 3. core.interfaces.i_orchestrator
```yaml
location: cortex/core/interfaces/i_orchestrator.py
purpose: Base interface for all orchestrators
dependencies: None (base interface)
key_interfaces:
  - IOrchestrator: Base orchestrator protocol
  - IExecutor: Execution interface
  - IPlanner: Planning interface
  - IAnalyzer: Analysis interface
  - IValidator: Validation interface
tests: Referenced by all orchestrator implementations
```

#### 4. infrastructure.database
```yaml
location: cortex/infrastructure/database.py
purpose: Database connection and query management
dependencies:
  - sqlite3
  - cortex.brain.core.result
key_classes:
  - DatabaseConnection: Connection pool management
  - QueryExecutor: Safe query execution
  - SchemaManager: Schema migration
tests: 15+ test dependencies
```

#### 5. infrastructure.enhanced_audit_logger
```yaml
location: cortex/infrastructure/enhanced_audit_logger.py
purpose: Enhanced logging with governance tracking
dependencies:
  - logging
  - cortex.brain.core.path_resolver
key_classes:
  - EnhancedAuditLogger: Main logger (singleton)
  - AuditEntry: Structured log entry
methods:
  - log_operation_start()
  - log_operation_complete()
  - log_governance_violation()
tests: Cross-cutting - used by all modules
```

#### 6. core.knowledge.knowledge_graph
```yaml
location: cortex/core/knowledge/knowledge_graph.py
purpose: Knowledge graph storage and retrieval
dependencies:
  - cortex.infrastructure.database
  - cortex.brain.core.result
key_classes:
  - KnowledgeGraph: Graph storage
  - Node: Knowledge node
  - Edge: Knowledge relationship
methods:
  - add_node(), add_edge()
  - query_subgraph()
  - semantic_search()
tests: E2E tests blocked without this
```

#### 7. core.knowledge.unified_service
```yaml
location: cortex/core/knowledge/unified_service.py
purpose: Unified knowledge service facade
dependencies:
  - cortex.core.knowledge.knowledge_graph
  - cortex.brain.core.result
key_classes:
  - UnifiedKnowledgeService: Service facade
methods:
  - store_knowledge()
  - retrieve_knowledge()
  - semantic_query()
tests: Knowledge protocol tests
```

#### 8. core.governance_pregate
```yaml
location: cortex/core/governance_pregate.py
purpose: Pre-execution governance validation
dependencies:
  - cortex.brain.core.rule_evaluator
  - cortex.brain.core.governance_registry
key_classes:
  - GovernancePregate: Validation gateway
methods:
  - validate_operation()
  - check_tier_compliance()
  - enforce_rules()
tests: Governance validation tests
```

#### 9. core.governance_registry
```yaml
location: cortex/core/governance_registry.py
purpose: Governance rule registry and management
note: Already exists in cortex/brain/core/governance_registry.py
action: Either update import path or create facade
```

#### 10. orchestrators.core.master_orchestrator
```yaml
location: cortex/orchestrators/core/master_orchestrator.py
purpose: Central orchestration coordinator
note: Already exists - check if tests import from wrong location
action: Verify import paths and update tests if needed
```

## IMPLEMENTATION WORKFLOW

### Per-Module Checklist

```bash
# 1. Create stub file
touch cortex/path/to/module.py

# 2. Add stub structure with signatures
# - Class definitions
# - Method signatures with type hints
# - Placeholder docstrings
# - Return Ok(None) or similar default

# 3. Run tests to verify imports resolve
pytest tests/ --co -q 2>&1 | grep "module.py"

# 4. Implement business logic
# - Read test file to understand expected behavior
# - Implement actual logic
# - Follow CORE governance rules

# 5. Run module tests
pytest tests/unit/path/test_module.py -v

# 6. Fix failures iteratively
# - Read test failures
# - Update implementation
# - Re-run tests

# 7. Git checkpoint (every 2-3 modules)
git add -A
git commit -m "feat: implement module_name

- Resolves import errors
- Implements business logic
- X tests passing"

# 8. Move to next priority module
```

### Batch Processing Strategy

**Day 1**: P0 modules 1-2 (orchestrator_decorator, conversation_protocol)
**Day 2**: P0 modules 3-5 (i_orchestrator, database, enhanced_audit_logger)
**Day 3**: P1 modules 6-7 (knowledge_graph, unified_service)
**Day 4**: P1 modules 8-10 (governance_pregate, governance_registry, master_orchestrator)
**Days 5-6**: P2 intent and MCP modules
**Days 7-9**: P2 domain_brain modules (batch of 14)
**Days 10-12**: P3 devx, templates, versioning

## TESTING STRATEGY

### Continuous Validation

```bash
# After each module implementation
pytest tests/ --co -q | grep -c "test_"  # Should increase as imports resolve

# After each day
pytest tests/unit/core/ -v --tb=short  # Should show progress

# Phase 1 complete checkpoint
pytest tests/ --co -q 2>&1 | grep -c "ERROR"  # Should be 0

# Phase 2 complete checkpoint  
pytest tests/ -x --tb=short  # Should pass ≥98%

# Phase 3 integration validation
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### Test Failure Patterns

**Import Errors** → Stub not created or wrong location
**AttributeError** → Missing method/class in stub
**TypeError** → Wrong signature or return type
**AssertionError** → Wrong business logic implementation
**NotImplementedError** → Stub not replaced with real implementation

## COMMON PATTERNS

### Result Monad Pattern
```python
from cortex.brain.core.result import Result, Ok, Err

def operation() -> Result[str]:
    try:
        # Business logic
        result = do_something()
        return Ok(result)
    except Exception as e:
        return Err(f"Operation failed: {str(e)}")
```

### Enhanced Audit Logger Pattern
```python
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()

logger.log_operation_start(
    ac_id="AC-XXX-YY",
    operation="OPERATION_NAME",
    details={"key": "value"}
)

# Do work

logger.log_operation_complete(
    ac_id="AC-XXX-YY",
    operation="OPERATION_NAME",
    success=True,
    details={"result": "value"}
)
```

### Governance Validation Pattern
```python
from cortex.brain.core.rule_evaluator import RuleEvaluator

evaluator = RuleEvaluator()
context = {
    "file_path": path,
    "operation_type": "MODIFY",
    "lines_changed": count
}

result = evaluator.evaluate_rules(context)
if result.is_ok() and not result.unwrap().passed:
    # Handle violations
    violations = result.unwrap().violations
```

## FILE LOCATIONS

### Test Reference
```
tests/unit/              # Unit tests by module
tests/integration/       # Integration tests
tests/e2e/              # End-to-end tests
```

### Implementation Reference
```
cortex/
├── core/
│   ├── decorators/          # Decorator utilities
│   ├── interfaces/          # Protocol definitions
│   ├── orchestrator/        # Orchestration core
│   ├── knowledge/           # Knowledge management
│   ├── intent/             # Intent routing
│   └── governance/         # Governance utilities
├── orchestrators/
│   ├── core/               # Core orchestrators
│   └── response/           # Response handling
├── domain_brain/           # Domain-specific modules
├── infrastructure/         # Infrastructure layer
└── mcp/                    # MCP protocol
```

### Documentation Reference
```
_workspaces/roadmap/
├── cortex-impl-map.yaml           # Implementation status
├── reports/
│   └── tdd-gap-analysis.yaml     # Detailed gap analysis
└── phases/
    └── impl-tdd-prod-ready.yaml  # This implementation plan
```

## SUCCESS CRITERIA

### Phase 1 Complete
- [ ] All 125 stub files created
- [ ] `pytest tests/ --co -q` completes with 0 import errors
- [ ] Test collection count increases to ~262 tests

### Phase 2 Complete
- [ ] All stubs replaced with working implementations
- [ ] ≥98% test pass rate
- [ ] No `NotImplementedError` or placeholder logic
- [ ] All implementations follow CORE governance rules

### Phase 3 Complete
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance benchmarks within SLAs
- [ ] Production readiness confirmed

## CONTINUATION COMMAND

```bash
# Start implementation session
cd D:\PROJECTS\CORTEX

# Verify starting state
git status  # Should show clean state from previous session
pytest tests/ --co -q 2>&1 | grep -c "ERROR"  # Should show ~170 errors

# Begin Phase 1: Stub Generation
# Start with P0 Critical modules (1-5)
# Create stubs following template above
# Verify imports resolve after each stub

# Use this prompt as your implementation guide
# Follow priority order strictly
# Commit every 2-3 modules
# Update cortex-impl-map.yaml at each phase completion
```

## GOVERNANCE NOTES

**Active Rules** (enforced via context-aware governance):
- CORE-001: Incremental execution <500 lines per turn
- CORE-008: Tests before code (tests already exist)
- CORE-011: Type hints required
- CORE-012: Docstrings required
- CORE-013: No bare except
- CORE-026: Git checkpoints
- CORE-028: File length limits

**Testing Framework**: pytest with conftest.py fixtures

**Python Version**: 3.13.7

**Branch**: CORTEX (current)

## PREVIOUS SESSION ACHIEVEMENTS

### Context-Aware Governance (GOV-CTX-001) - COMPLETE
- Context extraction: 15 tests passing
- Rule applicability: 17 tests passing  
- Rule validators: 18 tests passing (7 implemented, 22 future enhancements)
- RuleEvaluator integration: 25 tests passing
- **Total**: 75 tests passing
- **Impact**: 28/29 governance rules now functional (was only 1/29)

### Intelligence Modules (INT-001/002/003) - COMPLETE
- Routing intelligence: 12 tests passing
- Duration intelligence: 15 tests passing
- Error intelligence: 15 tests passing
- **Total**: 42 tests passing
- **Impact**: Operational intelligence for routing accuracy, performance baselines, error patterns

### Combined Achievement
- **117 new tests passing** in previous session
- **P0 and P1 priorities complete**
- **P0-NEXT** (this task) is now the critical path to production

## START HERE

1. Review this prompt completely
2. Review `_workspaces/roadmap/reports/tdd-gap-analysis.yaml` for full module list
3. Start Phase 1 with module #1: `core.decorators.orchestrator_decorator`
4. Work through priority order systematically
5. Commit progress every 2-3 modules
6. Report status at phase completions

**Estimated Total Effort**: 12-18 days (Phase 1: 1-2 days, Phase 2: 8-12 days, Phase 3: 3-4 days)

**Critical Success Factor**: Follow priority order strictly - P0 modules unblock the most tests.

Good luck! The codebase structure is solid, governance is enforced, and intelligence is tracking. This TDD gap remediation is the final major hurdle to production readiness.
