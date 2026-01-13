# 🔧 Orchestrator Development Guide (v1.0)

**Purpose:** Best practices and patterns for creating new CORTEX orchestrators  
**Version:** 1.0.0 | **Date:** 2026-01-13  
**Author:** Asif Hussain  
**Governance:** CORE-001 (incremental), CORE-008 (TDD), CORE-017 (governance enforcement)  
**Reference:** `.github/prompts/CORTEX.prompt.md` (entry point), `src/orchestrators/` (examples)

---

## 🎯 Core Principles

**Each orchestrator is:**
- ✅ A single, focused responsibility (SRP)
- ✅ Stateless (receives context via dependency injection)
- ✅ Testable (supports unit + integration tests)
- ✅ Auditable (all operations logged to EnterpriseAuditLogger)
- ✅ Flexible (supports multiple execution methods)
- ✅ Observable (returns structured reports)

---

## 📋 Orchestrator Interface Patterns

### Pattern 1: Flexible Execution Methods

**Design:** Support multiple method signatures, not just `execute()`.

**Why:** Different orchestrators have different natural operations:
- `execute()` → General-purpose executor
- `check()` → Validation / health check
- `run()` → Long-running process
- `diagnose()` → Detailed analysis with recommendations
- `repair()` → Auto-remediation

**Implementation:**

```python
class MyOrchestrator:
    """Example orchestrator with flexible methods."""
    
    def __init__(self, registry: OrchestratorRegistry, logger: EnterpriseAuditLogger):
        """Dependency injection of required services."""
        self.registry = registry
        self.logger = logger
    
    # PRIMARY EXECUTION METHOD
    def execute(self, user_request: str) -> ExecutionResult:
        """Main orchestrator logic."""
        self.logger.info("execute", category="ORCHESTRATOR", data={"request": user_request})
        # Implementation here
        return ExecutionResult(status="success", data={...})
    
    # VALIDATION METHOD
    def check(self) -> HealthCheckReport:
        """Run validation logic (no side effects)."""
        self.logger.info("check", category="ORCHESTRATOR")
        # Validation logic
        return HealthCheckReport(...)
    
    # DIAGNOSTIC METHOD
    def diagnose(self) -> DiagnosticReport:
        """Detailed diagnostics with recommendations."""
        self.logger.info("diagnose", category="ORCHESTRATOR")
        # Diagnostic logic with recommendations
        return DiagnosticReport(...)
    
    # AUTO-REPAIR METHOD
    def repair(self, auto_only: bool = True) -> RepairReport:
        """Auto-repair safe issues."""
        self.logger.warning("repair", category="ORCHESTRATOR", data={"auto_only": auto_only})
        # Repair logic (with audit trail)
        return RepairReport(...)
```

**MasterOrchestrator calls the RIGHT method automatically:**

```python
# In src/orchestrators/master_orchestrator.py execute_orchestrator()

# Flexible method resolution (tries in order)
execution_methods = ['execute', 'check', 'run', 'diagnose']
execute_method = None

for method_name in execution_methods:
    if hasattr(orchestrator, method_name):
        execute_method = getattr(orchestrator, method_name)
        break

# Call method with smart parameter passing
result = execute_method(...)  # Only passes accepted params
```

### Pattern 2: Smart Parameter Passing

**Design:** Only pass parameters that the method actually accepts.

**Why:** Different methods have different signatures. Don't force all parameters.

**Implementation:**

```python
import inspect

def call_orchestrator_method(orchestrator, method, user_context: Dict):
    """Call method with intelligent parameter mapping."""
    
    # Inspect the method signature
    sig = inspect.signature(method)
    method_params = set(sig.parameters.keys())
    method_params.discard('self')
    
    # Map available params to accepted params
    available_params = {
        'user_request': user_context.get('request'),
        'session_id': user_context.get('session_id'),
        'correlation_id': user_context.get('correlation_id'),
        'auto_only': True,
    }
    
    # Only pass params the method accepts
    call_params = {}
    for param_name, param_value in available_params.items():
        if param_name in method_params:
            call_params[param_name] = param_value
    
    # Call method with only accepted params
    if call_params:
        return method(**call_params)
    else:
        return method()
```

### Pattern 3: Report-to-Markdown Conversion

**Design:** Orchestrators return structured objects. MasterOrchestrator auto-converts to markdown.

**Why:** Clean separation - orchestrators focus on logic, conversion handled centrally.

**Implementation:**

```python
class MyReport:
    """Custom report object."""
    
    def to_markdown(self) -> str:
        """Convert report to markdown string."""
        return f"""
# My Report
## Summary
Total issues: {self.issue_count}
Status: {self.status}

## Issues
{self._format_issues()}
"""

# In MasterOrchestrator.execute_orchestrator()

result_data = execute_method(...)

# Auto-detect Report objects with to_markdown() method
if (hasattr(result_data, 'to_markdown') and 
    ('Report' in result_data.__class__.__name__ or 
     'Health' in result_data.__class__.__name__)):
    
    # Convert to markdown string
    result_data = result_data.to_markdown()

# Return in ExecutionResult
return ExecutionResult(
    status="success",
    data=result_data,
    format="markdown"
)
```

---

## 🏗️ Registry & Dependency Injection Pattern

### Pattern: Consolidate Registries (No Duplication)

**Design:** Receive registry via constructor, never create new one.

**Why:** Duplicate registries cause sync issues and inconsistent state.

**❌ WRONG:**
```python
class BadOrchestrator:
    def __init__(self):
        # DON'T: Create new registry in orchestrator
        self.registry = OrchestratorRegistry(workspace_root=Path.cwd())
        # This creates EMPTY registry, separate from MasterOrchestrator's registry
```

**✅ CORRECT:**
```python
class GoodOrchestrator:
    def __init__(self, registry: OrchestratorRegistry, logger: EnterpriseAuditLogger):
        # DO: Receive pre-loaded registry from MasterOrchestrator
        self.registry = registry
        self.logger = logger
        
        # Now orchestrator uses the SAME registry that MasterOrchestrator sees
        # All orchestrators are visible here
        orchestrators = self.registry.list_all()
```

### Registration Pattern

**In `src/entry_point/cortex_entry.py`:**

```python
def _register_core_orchestrators(self):
    """Register all core orchestrators."""
    
    # Health Check Orchestrator (Priority 6)
    self.orchestrator_registry.register(
        id="health_check_v1",
        name="Health Check Orchestrator v1",
        module="src.orchestrators.health.health_check_orchestrator_v1",
        class_name="HealthCheckOrchestratorV1",
        patterns=[
            r"^(health check|repair cortex|wiring|diagnose cortex|architecture health).*$"
        ],
        priority=6,
        metadata={
            "ac_ids": ["AC-CORTEX-001", "AC-CORTEX-002", "AC-CORTEX-003"],
            "category": "ARCHITECTURE_HEALTH",
        }
    )
    
    # Your Orchestrator (Priority N)
    self.orchestrator_registry.register(
        id="my_orchestrator",
        name="My Orchestrator",
        module="src.orchestrators.my_module.my_orchestrator",
        class_name="MyOrchestrator",
        patterns=[r"^(my intent|my keyword).*$"],
        priority=30,  # Lower number = higher priority
        metadata={
            "ac_ids": ["AC-MY-001", "AC-MY-002"],
            "category": "MY_CATEGORY",
        }
    )
```

---

## ✅ Testing Orchestrators

### Unit Test Pattern

```python
import pytest
from unittest.mock import Mock, MagicMock

class TestMyOrchestrator:
    """Tests for MyOrchestrator."""
    
    @pytest.fixture
    def setup(self):
        """Setup test fixtures."""
        self.mock_registry = Mock(spec=OrchestratorRegistry)
        self.mock_logger = Mock(spec=EnterpriseAuditLogger)
        self.orchestrator = MyOrchestrator(
            registry=self.mock_registry,
            logger=self.mock_logger
        )
        yield
    
    def test_execute_success(self, setup):
        """Test successful execution."""
        result = self.orchestrator.execute("test request")
        assert result.status == "success"
        self.mock_logger.info.assert_called()
    
    def test_check_validation(self, setup):
        """Test validation method."""
        report = self.orchestrator.check()
        assert isinstance(report, HealthCheckReport)
        assert report.status in ["HEALTHY", "UNHEALTHY"]
    
    def test_diagnose_with_recommendations(self, setup):
        """Test diagnostic method."""
        diagnostic = self.orchestrator.diagnose()
        assert hasattr(diagnostic, 'recommendations')
        assert len(diagnostic.recommendations) > 0
```

### Integration Test Pattern

```python
@pytest.mark.integration
@pytest.mark.cross_platform
def test_orchestrator_via_master():
    """Test orchestrator invocation via MasterOrchestrator."""
    # This runs on BOTH MAC and WIN
    
    master = MasterOrchestrator(
        registry=OrchestratorRegistry(...),
        state_manager=StateManager(...),
        logger=EnterpriseAuditLogger(...)
    )
    
    result = master.execute_orchestrator(
        orchestrator_id="my_orchestrator",
        user_request="my intent test"
    )
    
    assert result.status == "success"
    assert result.format == "markdown"
```

### Health Check Integration Pattern

```python
@pytest.mark.unit
def test_health_check_detects_my_issue():
    """Test that health check can detect issues from this orchestrator."""
    
    health_check = HealthCheckOrchestratorV1(
        registry=mock_registry,
        logger=mock_logger
    )
    
    # Run health check
    report = health_check.check()
    
    # Verify it detects issues related to my orchestrator
    issue_ids = [issue.id for issue in report.issues]
    assert any("MY_ORCHESTRATOR" in id for id in issue_ids)
```

---

## 📋 Audit & Logging Pattern

**Every orchestrator should log operations:**

```python
class MyOrchestrator:
    def execute(self, user_request: str) -> ExecutionResult:
        """Execute with audit trail."""
        
        # Log START
        self.logger.info(
            "execute",
            category="ORCHESTRATOR",
            data={
                "orchestrator": "my_orchestrator",
                "request": user_request,
            }
        )
        
        try:
            # Do work
            result = self._do_work(user_request)
            
            # Log SUCCESS
            self.logger.info(
                "execute_complete",
                category="ORCHESTRATOR",
                data={
                    "status": "success",
                    "items_processed": result.count,
                }
            )
            
            return ExecutionResult(status="success", data=result)
        
        except Exception as e:
            # Log ERROR
            self.logger.error(
                "execute_failed",
                category="ORCHESTRATOR",
                error={
                    "type": e.__class__.__name__,
                    "message": str(e),
                }
            )
            
            return ExecutionResult(status="error", error=str(e))
```

---

## 🏗️ Orchestrator Structure (Directory Layout)

```
src/orchestrators/
├─ core/
│  ├─ master_orchestrator.py         (Central router)
│  ├─ governance_merger.py            (Rule enforcement)
│  └─ todo_orchestrator.py            (Task management)
│
├─ health/
│  ├─ __init__.py
│  ├─ health_check_orchestrator_v1.py (Example: flexibility patterns)
│  └─ validators/
│      ├─ tier_zero_validator.py
│      ├─ tier_one_validator.py
│      └─ ...
│
├─ my_module/  # YOUR ORCHESTRATOR
│  ├─ __init__.py
│  ├─ my_orchestrator.py              (Main class)
│  ├─ my_components.py                (Helper classes)
│  └─ __pycache__/
│
└─ other_orchestrators/
   ├─ planning_orchestrator.py
   ├─ investigation_orchestrator.py
   └─ ...
```

---

## 📝 Registration Checklist

Before considering your orchestrator "done":

- [ ] **Interface Design**
  - [ ] Supports at least one execution method (execute, check, run, diagnose)
  - [ ] Receives dependencies via constructor (registry, logger)
  - [ ] Returns structured result/report object
  - [ ] Has `to_markdown()` if returning custom Report

- [ ] **Registration**
  - [ ] Added to `_register_core_orchestrators()` in cortex_entry.py
  - [ ] Registered in `cortex-brain/registry/orchestrators.json`
  - [ ] Patterns configured in routing rules
  - [ ] Priority set appropriately (lower number = higher priority)

- [ ] **Testing**
  - [ ] Unit tests exist for all methods
  - [ ] Integration test via MasterOrchestrator
  - [ ] Cross-platform markers applied (@pytest.mark.cross_platform)
  - [ ] ≥80% code coverage

- [ ] **Documentation**
  - [ ] Docstrings on all public methods
  - [ ] Audit logging implemented
  - [ ] Error handling with try/except
  - [ ] Usage examples in module docstring

- [ ] **Governance**
  - [ ] Follows CORE-001 (incremental execution)
  - [ ] Follows CORE-005 (path portability)
  - [ ] Follows CORE-008 (TDD enforcement)
  - [ ] Follows CORE-017 (governance enforcement)

- [ ] **Integration**
  - [ ] Tested with MasterOrchestrator
  - [ ] Tested with HealthCheckOrchestratorV1
  - [ ] Added to health check (if applicable)
  - [ ] Verified via `python3 -m src.main "test my orchestrator"`

---

## 🔗 Related Documentation

- **Entry Point:** `.github/prompts/CORTEX.prompt.md` (routing logic)
- **Health Check:** `.github/prompts/cortex-wiring.prompt.md` (validation)
- **Execution:** `.github/prompts/cortex-exec.prompt.md` (phase execution)
- **Governance:** `cortex-brain/tier0/governance/core-rules.yaml` (SKULL rules)
- **Registry:** `cortex-brain/registry/orchestrators.json` (orchestrator metadata)

---

## 📚 Example Implementations

**Reference these working orchestrators:**

1. **HealthCheckOrchestratorV1** (`src/orchestrators/health/health_check_orchestrator_v1.py`)
   - Demonstrates flexible methods (check, repair, diagnose)
   - Shows report-to-markdown conversion
   - Multiple validators (architectural pattern)
   - Auto-repair logic with audit trail

2. **MasterOrchestrator** (`src/orchestrators/core/master_orchestrator.py`)
   - Central dispatcher pattern
   - Registry consolidation (no duplication)
   - Flexible method resolution (core pattern)
   - Smart parameter passing

3. **GovernanceMerger** (`src/orchestrators/core/governance_merger.py`)
   - Rule merging from multiple tiers
   - Conflict resolution logic
   - SKULL rule enforcement

---

## ✨ Best Practices Checklist

- ✅ **Single Responsibility:** Orchestrator has ONE clear purpose
- ✅ **Stateless:** No stored state between calls (everything via DI)
- ✅ **Dependency Injection:** Constructor accepts all external services
- ✅ **Error Handling:** Try/except with audit logging
- ✅ **Type Hints:** All method signatures have type annotations
- ✅ **Testable:** Unit tests with mocks, integration tests with real objects
- ✅ **Observable:** All operations logged to audit logger
- ✅ **Flexible:** Support multiple execution methods when applicable
- ✅ **Documented:** Docstrings explain purpose and parameters
- ✅ **Auditable:** Every action traceable via correlation IDs

---

**Version:** 1.0.0 | **Last Updated:** 2026-01-13  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
