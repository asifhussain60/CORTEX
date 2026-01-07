# BaseOrchestrator - Universal Orchestrator Foundation (CORTEX 5.0)

**Author:** Asif Hussain  
**CORTEX Version:** 5.0  
**Created:** January 6, 2026  
**Purpose:** SOLID/DRY-compliant base class enforcing governance, audit logging, and knowledge integration

---

## 🎯 Executive Summary

BaseOrchestrator provides a universal foundation for ALL CORTEX 5.0 orchestrators (planning, TDD, ADO, cleanup, etc.) and allows seamless extension for company-specific orchestrators. It enforces key requirements automatically:

1. **Governance Rules** - SKULL enforcement at every execution turn
2. **Audit Logging** - 4-level enterprise audit trail (task→phase→epicfrom src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator, OrchestratorMetadata, OrchestratorType, OrchestratorResult
)

class PlanningOrchestrator(BaseOrchestrator):
    """
    CORTEX Planning Orchestrator - Feature plan generation.
    
    Inherits ALL governance/audit/knowledge enforcement from BaseOrchestrator.
    Only implements planning-specific workflow.
    """
    
    def _get_orchestrator_metadata(self) -> OrchestratorMetadata:
        return OrchestratorMetadata(
            name="Planning Orchestrator",
            version="5.0",owledge Library Integration** - Automatic SOLID/DRY/pattern consultation
4. **SOLID Compliance** - Architecture follows all 5 SOLID principles
5. **DRY Enforcement** - Zero duplicate validation/logging/governance code
6. **Extensibility** - Clear extension points for CORTEX/company orchestrators

---

## 🏗️ Architecture Principles

### SOLID Compliance

#### 1. **Single Responsibility Principle (SRP)**
**Each class does ONE thing:**

```
BaseOrchestrator         → Lifecycle management (setup→execute→teardown)
GovernanceValidator      → SKULL rule enforcement
AuditLogger              → 4-level audit trail
KnowledgeConsultant      → Knowledge library queries
PhaseManager             → Phase execution orchestration
ErrorHandler             → Error recovery & rollback
```

#### 2. **Open/Closed Principle (OCP)**
**Open for extension, closed for modification:**

```python
# ✅ EXTEND via inheritance
class PlanningOrchestrator(BaseOrchestrator):
    def _execute_core_workflow(self, context: Dict) -> OrchestratorResult:
        # Custom planning logic here
        pass

# ❌ NEVER modify BaseOrchestrator for new features
# Add extension points instead
```

#### 3. **Liskov Substitution Principle (LSP)**
**All orchestrators are substitutable:**

```python
def run_orchestrator(orch: BaseOrchestrator, request: str) -> OrchestratorResult:
    # Works with ANY orchestrator (planning, TDD, ADO, custom)
    return orch.execute(request)
```

#### 4. **Interface Segregation Principle (ISP)**
**Small, focused interfaces:**

```
IAuditableOrchestrator    → log_start(), log_complete(), log_error()
IGovernanceCompliant      → validate_tdd(), validate_git_isolation()
IKnowledgeAware          → consult_patterns(), consult_principles()
IPhaseExecutor           → execute_phase(), rollback_phase()
```

#### 5. **Dependency Inversion Principle (DIP)**
**Depend on abstractions:**

```python
# ✅ Depend on abstract interfaces
self.audit_logger: IAuditLogger
self.governance: IGovernanceValidator
self.knowledge: IKnowledgeConsultant

# ❌ Never depend on concrete implementations
# self.audit_logger = EnterpriseAuditLogger()  # WRONG
```

---

## 📐 Class Hierarchy

```
BaseOrchestrator (Abstract)
├── Core Services (Injected Dependencies)
│   ├── GovernanceValidator      → SKULL enforcement
│   ├── AuditLogger             → 4-level logging
│   ├── KnowledgeConsultant     → SOLID/pattern queries
│   ├── PhaseManager            → Phase execution
│   └── ErrorHandler            → Recovery & rollback
│
├── Template Methods (Final - Cannot Override)
│   ├── execute()               → Lifecycle: setup→core→teardown
│   ├── _setup_verification()   → Phase -2 (SKULL: SetupVerifier)
│   ├── _governance_checkpoint() → Runtime (SKULL: GovernanceCheckpoint)
│   └── _teardown_refactor()    → Phase N+1 (SKULL: TeardownRefactor)
│
├── Abstract Methods (MUST Override)
│   ├── _execute_core_workflow() → Orchestrator-specific logic
│   ├── _validate_preconditions() → Pre-execution validation
│   └── _get_orchestrator_metadata() → Name, version, capabilities
│
└── Hook Methods (MAY Override)
    ├── _on_phase_start()
    ├── _on_phase_complete()
    ├── _on_error()
    └── _on_rollback()


CORTEX-Specific Orchestrators
├── PlanningOrchestrator        (CORTEX feature planning)
├── TDDOrchestrator             (CORTEX TDD workflow)
├── ADOOrchestrator             (CORTEX Azure DevOps integration)
├── CleanupOrchestrator         (CORTEX cache/log cleanup)
├── VacuumOrchestrator          (CORTEX deep filesystem cleanup)
├── SanitizationOrchestrator    (CORTEX PII/secret removal)
├── InvestigationOrchestrator   (CORTEX root cause analysis)
└── MaintenanceOrchestrator     (CORTEX 12-phase health pipeline)

Company-Specific Orchestrators (Extensibility Point)
├── CompanyWorkflowOrchestrator   (Custom business logic)
├── CompanyComplianceOrchestrator (Industry-specific rules)
├── CompanyDeploymentOrchestrator (Custom CI/CD)
└── CompanyReportingOrchestrator  (Custom analytics)
```

---

## 🔒 Enforced Requirements

### 1. Governance Rules (SKULL)

**Enforced at THREE checkpoints:**

```python
# Phase -2: Setup Verification
def _setup_verification(self, context: Dict) -> SetupResult:
    """
    MANDATORY pre-execution checks:
    - Workspace integrity (git clean, no conflicts)
    - Test coverage baseline captured
    - Knowledge graph available
    - Required tools installed
    """
    return self.setup_verifier.verify_all()

# Runtime: Governance Checkpoint
def _governance_checkpoint(self, phase_num: int, context: Dict) -> GovernanceResult:
    """
    MANDATORY runtime checks:
    - TDD_ENFORCEMENT: Tests fail before implementation
    - HOLISTIC_DISCOVERY: Search before create
    - GIT_ISOLATION: CORTEX code never commits to user repos
    - PLANNING_ISOLATION: Planning commands create plans ONLY
    """
    return self.governance.checkpoint_phase_start(phase_num, self.name, context)

# Phase N+1: Teardown Refactor
def _teardown_refactor(self, context: Dict) -> RefactorResult:
    """
    MANDATORY post-execution cleanup:
    - Whole-file refactor (no commented code)
    - SOLID compliance check
    - Test coverage verification
    - Documentation sync
    """
    return self.teardown_refactor.refactor_all_modified_files()
```

**Reference:** `cortex-brain/brain-protection-rules.yaml` (loaded automatically)

### 2. Audit Logging (4-Level Enterprise Trail)

**Level 1: Task-Level**
```json
{
  "task_id": "T001",
  "phase_id": "P02",
  "orchestrator": "planning_v6",
  "status": "completed",
  "duration_seconds": 323,
  "success": true
}
```

**Level 2: Phase-Level**
```json
{
  "phase_id": "P02",
  "orchestrator": "planning_v6",
  "tasks_completed": 8,
  "dependencies_satisfied": true,
  "checkpoint_id": "checkpoint_P02_2026-01-06"
}
```

**Level 3: Epic-Level**
```json
{
  "epic_id": "cortex5-remediation",
  "overall_progress": 0.57,
  "phases_complete": 8,
  "current_phase": "P08",
  "cumulative_efficiency_gain": 0.42
}
```

**Level 4: System-Level**
```json
{
  "brittleness_score": 28,
  "test_coverage": 0.83,
  "orchestrator_success_rate": 0.94
}
```

**Storage:** `cortex-brain/documents/planning/active/{epic_id}/tracking/audit-log.jsonl`

### 3. Knowledge Library Integration

**Automatic consultation for:**

- **SOLID Principles** (`cortex-brain/knowledge/engineering/solid-principles.yaml`)
- **Design Patterns** (`cortex-brain/knowledge/engineering/design-patterns.yaml`)
- **Refactoring Techniques** (`cortex-brain/knowledge/engineering/refactoring.yaml`)
- **Anti-Patterns** (`cortex-brain/knowledge/engineering/anti-patterns.yaml`)
- **TDD Best Practices** (`cortex-brain/knowledge/tdd/tdd-practices.yaml`)

**Usage:**
```python
# In orchestrator execution
solid_guidance = self.knowledge.consult_solid_principle("SRP")
pattern_match = self.knowledge.find_matching_pattern(code_context)
refactoring_steps = self.knowledge.get_refactoring_technique("extract_class")
```

---

## 💻 Implementation Specification

### File: `src/orchestrators/base/base_orchestrator_v6.py`

```python
"""
BaseOrchestrator  - Universal Orchestrator Foundation

SOLID/DRY-compliant base class enforcing:
- Governance rules (SKULL)
- Audit logging (4-level)
- Knowledge integration (SOLID/patterns)
- Extensibility (CORTEX + company orchestrators)

Author: Asif Hussain
Version: 5.0
Created: January 6, 2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Core dependencies (interface-based for DIP)
from src.orchestrators.middleware.governance_checkpoint import (
    GovernanceCheckpoint, IGovernanceValidator
)
from src.orchestrators.middleware.setup_verification import (
    SetupVerifier, ISetupValidator
)
from src.orchestrators.middleware.teardown_refactor import (
    TeardownRefactor, ITeardownRefactor
)
from src.orchestrators.audit_logger import AuditLogger, IAuditLogger
from src.orchestrators.base.knowledge_consultant import (
    KnowledgeConsultant, IKnowledgeConsultant
)
from src.orchestrators.base.phase_manager import PhaseManager
from src.orchestrators.base.error_handler import ErrorHandler


class OrchestratorType(Enum):
    """Orchestrator classification for routing and registry"""
    CORTEX_PLANNING = "cortex_planning"
    CORTEX_TDD = "cortex_tdd"
    CORTEX_ADO = "cortex_ado"
    CORTEX_CLEANUP = "cortex_cleanup"
    CORTEX_VACUUM = "cortex_vacuum"
    CORTEX_SANITIZATION = "cortex_sanitization"
    CORTEX_INVESTIGATION = "cortex_investigation"
    CORTEX_MAINTENANCE = "cortex_maintenance"
    COMPANY_CUSTOM = "company_custom"


class ExecutionPhase(Enum):
    """Execution lifecycle phases"""
    PHASE_NEG2_SETUP = "phase_-2_setup"          # Setup verification
    PHASE_CORE = "phase_core"                    # Core workflow
    PHASE_NPLUS1_TEARDOWN = "phase_n+1_teardown" # Teardown refactor


@dataclass
class OrchestratorMetadata:
    """Metadata for orchestrator registration"""
    name: str
    version: str
    type: OrchestratorType
    description: str
    author: str
    capabilities: List[str]
    requires_tdd: bool = True
    requires_git_isolation: bool = True


@dataclass
class OrchestratorResult:
    """Result from orchestrator execution"""
    success: bool
    orchestrator: str
    duration_seconds: float
    phases_completed: int
    errors: List[str]
    warnings: List[str]
    artifacts: Dict[str, Any]
    audit_log_path: str
    metrics: Dict[str, Any]


class BaseOrchestrator(ABC):
    """
    Universal base class for ALL orchestrators (CORTEX + company-specific).
    
    Enforces:
    - SOLID principles (SRP, OCP, LSP, ISP, DIP)
    - DRY (no duplicate governance/audit/knowledge code)
    - Governance rules (SKULL) at setup/runtime/teardown
    - 4-level audit logging (task→phase→epic→system)
    - Knowledge library integration (SOLID/patterns)
    
    Extensibility:
    - CORTEX orchestrators: Planning, TDD, ADO, etc.
    - Company orchestrators: CompanyWorkflow, CompanyCompliance, etc.
    
    Template Method Pattern (final methods - cannot override):
    - execute() → Orchestrates: setup → core → teardown
    - _setup_verification() → Phase -2 (SKULL)
    - _governance_checkpoint() → Runtime (SKULL)
    - _teardown_refactor() → Phase N+1 (SKULL)
    
    Abstract Methods (MUST implement):
    - _execute_core_workflow() → Orchestrator-specific logic
    - _validate_preconditions() → Pre-execution validation
    - _get_orchestrator_metadata() → Name, version, capabilities
    
    Hook Methods (MAY override):
    - _on_phase_start(), _on_phase_complete(), _on_error(), _on_rollback()
    """
    
    def __init__(
        self,
        workspace_root: Path,
        audit_logger: Optional[IAuditLogger] = None,
        governance: Optional[IGovernanceValidator] = None,
        knowledge: Optional[IKnowledgeConsultant] = None,
        setup_verifier: Optional[ISetupValidator] = None,
        teardown_refactor: Optional[ITeardownRefactor] = None
    ):
        """
        Initialize base orchestrator with dependency injection (DIP).
        
        Args:
            workspace_root: Root path of CORTEX workspace
            audit_logger: Audit logging service (4-level trail)
            governance: Governance validation service (SKULL)
            knowledge: Knowledge library service (SOLID/patterns)
            setup_verifier: Setup validation service (Phase -2)
            teardown_refactor: Refactor service (Phase N+1)
        """
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(f"cortex.orchestrators.{self.__class__.__name__}")
        
        # Dependency injection (defaults for convenience, interfaces for testing)
        self.audit_logger = audit_logger or AuditLogger(workspace_root)
        self.governance = governance or GovernanceCheckpoint(str(workspace_root))
        self.knowledge = knowledge or KnowledgeConsultant(workspace_root)
        self.setup_verifier = setup_verifier or SetupVerifier(workspace_root)
        self.teardown_refactor = teardown_refactor or TeardownRefactor(workspace_root)
        
        # Phase management
        self.phase_manager = PhaseManager(self.audit_logger)
        self.error_handler = ErrorHandler(self.audit_logger)
        
        # Execution state
        self._current_phase: Optional[ExecutionPhase] = None
        self._execution_context: Dict[str, Any] = {}
        self._start_time: Optional[float] = None
        
        # Metadata (loaded from subclass)
        self._metadata = self._get_orchestrator_metadata()
        
        self.logger.info(
            f"{self._metadata.name} v{self._metadata.version} initialized "
            f"(type={self._metadata.type.value})"
        )
    
    # =================================================================
    # TEMPLATE METHOD (Final - Cannot Override)
    # =================================================================
    
    def execute(self, request: str, context: Optional[Dict] = None) -> OrchestratorResult:
        """
        Execute orchestrator with MANDATORY lifecycle:
        Phase -2 → Core Workflow → Phase N+1
        
        This is the TEMPLATE METHOD - subclasses CANNOT override.
        Enforces consistent governance/audit/refactor workflow.
        
        Args:
            request: User request (e.g., "plan user authentication")
            context: Optional execution context (epic_id, parent_plan_id, etc.)
        
        Returns:
            OrchestratorResult with success status, metrics, artifacts
        """
        import time
        
        self._start_time = time.time()
        self._execution_context = context or {}
        
        # Start audit logging (Level 3: Epic-level)
        self.audit_logger.log_execution_start(
            orchestrator=self._metadata.name,
            request=request,
            context=self._execution_context
        )
        
        try:
            # ==================== PHASE -2: SETUP VERIFICATION ====================
            self._current_phase = ExecutionPhase.PHASE_NEG2_SETUP
            self.logger.info("Phase -2: Setup Verification")
            
            setup_result = self._setup_verification(self._execution_context)
            if not setup_result.success:
                return self._handle_setup_failure(setup_result)
            
            # ==================== CORE WORKFLOW (Orchestrator-Specific) ====================
            self._current_phase = ExecutionPhase.PHASE_CORE
            self.logger.info("Core Workflow: Executing orchestrator-specific logic")
            
            # Runtime governance checkpoint (SKULL enforcement)
            gov_result = self._governance_checkpoint(0, self._execution_context)
            if not gov_result.success:
                return self._handle_governance_failure(gov_result)
            
            # Execute core workflow (implemented by subclass)
            result = self._execute_core_workflow(self._execution_context)
            
            # ==================== PHASE N+1: TEARDOWN REFACTOR ====================
            self._current_phase = ExecutionPhase.PHASE_NPLUS1_TEARDOWN
            self.logger.info("Phase N+1: Teardown Refactor")
            
            refactor_result = self._teardown_refactor(self._execution_context)
            if not refactor_result.success:
                self.logger.warning(f"Teardown refactor warnings: {refactor_result.warnings}")
            
            # ==================== FINALIZE ====================
            duration = time.time() - self._start_time
            
            # Audit logging (Level 2: Phase-level + Level 3: Epic-level)
            self.audit_logger.log_execution_complete(
                orchestrator=self._metadata.name,
                duration_seconds=duration,
                success=result.success,
                artifacts=result.artifacts
            )
            
            return OrchestratorResult(
                success=result.success,
                orchestrator=self._metadata.name,
                duration_seconds=duration,
                phases_completed=result.phases_completed,
                errors=result.errors,
                warnings=result.warnings,
                artifacts=result.artifacts,
                audit_log_path=str(self.audit_logger.audit_file),
                metrics=result.metrics
            )
            
        except Exception as e:
            return self.error_handler.handle_exception(
                e, self._metadata.name, self._execution_context
            )
    
    def _setup_verification(self, context: Dict) -> Any:
        """
        Phase -2: Setup verification (SKULL enforcement).
        
        MANDATORY checks:
        - Workspace integrity (git clean, no conflicts)
        - Test coverage baseline
        - Knowledge graph available
        - Required tools installed
        
        Returns:
            SetupResult with success status and warnings
        """
        return self.setup_verifier.verify_all()
    
    def _governance_checkpoint(self, phase_num: int, context: Dict) -> Any:
        """
        Runtime governance checkpoint (SKULL enforcement).
        
        MANDATORY checks:
        - TDD_ENFORCEMENT: Tests fail before implementation
        - HOLISTIC_DISCOVERY: Search before create
        - GIT_ISOLATION: CORTEX code never commits to user repos
        - PLANNING_ISOLATION: Planning creates plans ONLY
        
        Returns:
            GovernanceResult with success status and violations
        """
        return self.governance.checkpoint_phase_start(
            phase_num, self._metadata.name, context
        )
    
    def _teardown_refactor(self, context: Dict) -> Any:
        """
        Phase N+1: Teardown refactor (SKULL enforcement).
        
        MANDATORY cleanup:
        - Whole-file refactor (no commented code)
        - SOLID compliance check
        - Test coverage verification
        - Documentation sync
        
        Returns:
            RefactorResult with success status and metrics
        """
        return self.teardown_refactor.refactor_all_modified_files()
    
    # =================================================================
    # ABSTRACT METHODS (Subclasses MUST Implement)
    # =================================================================
    
    @abstractmethod
    def _execute_core_workflow(self, context: Dict) -> OrchestratorResult:
        """
        Execute orchestrator-specific core workflow.
        
        Examples:
        - PlanningOrchestrator: Generate feature plan YAML
        - TDDOrchestrator: Execute RED→GREEN→REFACTOR cycle
        - ADOOrchestrator: Generate Azure DevOps work items
        
        Args:
            context: Execution context (epic_id, request, etc.)
        
        Returns:
            OrchestratorResult with success status and artifacts
        """
        pass
    
    @abstractmethod
    def _validate_preconditions(self, context: Dict) -> bool:
        """
        Validate orchestrator-specific preconditions.
        
        Examples:
        - PlanningOrchestrator: Check workspace clean, no active plans
        - TDDOrchestrator: Verify tests exist, can run pytest
        - ADOOrchestrator: Check ADO credentials configured
        
        Args:
            context: Execution context
        
        Returns:
            True if preconditions met, False otherwise
        """
        pass
    
    @abstractmethod
    def _get_orchestrator_metadata(self) -> OrchestratorMetadata:
        """
        Return orchestrator metadata for registration.
        
        Returns:
            OrchestratorMetadata with name, version, type, capabilities
        """
        pass
    
    # =================================================================
    # HOOK METHODS (Subclasses MAY Override)
    # =================================================================
    
    def _on_phase_start(self, phase_id: str, context: Dict) -> None:
        """Hook called before phase execution"""
        pass
    
    def _on_phase_complete(self, phase_id: str, result: Any) -> None:
        """Hook called after phase completion"""
        pass
    
    def _on_error(self, error: Exception, context: Dict) -> None:
        """Hook called on error"""
        pass
    
    def _on_rollback(self, checkpoint_id: str) -> None:
        """Hook called during rollback"""
        pass
    
    # =================================================================
    # HELPER METHODS
    # =================================================================
    
    def _handle_setup_failure(self, setup_result: Any) -> OrchestratorResult:
        """Handle setup verification failure"""
        return OrchestratorResult(
            success=False,
            orchestrator=self._metadata.name,
            duration_seconds=0,
            phases_completed=0,
            errors=[f"Setup verification failed: {setup_result.message}"],
            warnings=setup_result.warnings,
            artifacts={},
            audit_log_path=str(self.audit_logger.audit_file),
            metrics={}
        )
    
    def _handle_governance_failure(self, gov_result: Any) -> OrchestratorResult:
        """Handle governance checkpoint failure"""
        violations = [v.message for v in gov_result.violations]
        return OrchestratorResult(
            success=False,
            orchestrator=self._metadata.name,
            duration_seconds=0,
            phases_completed=0,
            errors=[f"Governance violations: {', '.join(violations)}"],
            warnings=[],
            artifacts={},
            audit_log_path=str(self.audit_logger.audit_file),
            metrics={"violations": len(violations)}
        )
```

---

## 🔄 Extension Points

### CORTEX-Specific Orchestrator Example

```python
from src.orchestrators.base.base_orchestrator_v6 import (
    BaseOrchestrator, OrchestratorMetadata, OrchestratorType, OrchestratorResult
)

class PlanningOrchestrator(BaseOrchestrator):
    """
    CORTEX Planning Orchestrator v6 - Feature plan generation.
    
    Inherits ALL governance/audit/knowledge enforcement from BaseOrchestrator.
    Only implements planning-specific workflow.
    """
    
    def _get_orchestrator_metadata(self) -> OrchestratorMetadata:
        return OrchestratorMetadata(
            name="Planning Orchestrator",
            CORTEX 5.0",
            type=OrchestratorType.CORTEX_PLANNING,
            description="Generate feature plans with YAML manifest",
            author="Asif Hussain",
            capabilities=["plan_generation", "yaml_manifest", "plan_viewer"],
            requires_tdd=True,
            requires_git_isolation=True
        )
    
    def _validate_preconditions(self, context: Dict) -> bool:
        # Check workspace clean
        # Check no active plans with same name
        return True
    
    def _execute_core_workflow(self, context: Dict) -> OrchestratorResult:
        """
        Planning-specific workflow:
        1. Extract feature name from request
        2. Query knowledge library for patterns/principles
        3. Generate YAML plan manifest
        4. Create plan folder structure
        5. Generate plan viewer HTML
        """
        # Use knowledge consultant (inherited from BaseOrchestrator)
        patterns = self.knowledge.find_matching_patterns(context["request"])
        solid_principles = self.knowledge.consult_solid_principles()
        
        # Generate plan (implementation details)
        plan_folder = self._generate_plan_folder(context)
        plan_yaml = self._generate_plan_yaml(context, patterns, solid_principles)
        viewer_html = self._generate_plan_viewer(context)
        
        return OrchestratorResult(
            success=True,
            orchestrator=self._metadata.name,
            duration_seconds=0,  # Filled by BaseOrchestrator
            phases_completed=5,
            errors=[],
            warnings=[],
            artifacts={
                "plan_folder": str(plan_folder),
                "plan_yaml": str(plan_yaml),
                "plan_viewer": str(viewer_html)
            },
            audit_log_path="",  # Filled by BaseOrchestrator
            metrics={"patterns_used": len(patterns)}
        )
```

### Company-Specific Orchestrator Example

```python
class CompanyComplianceOrchestrator(BaseOrchestrator):
    """
    Company-specific compliance orchestrator for HIPAA/SOC2/PCI.
    
    Inherits ALL CORTEX governance/audit infrastructure.
    Adds company-specific compliance rules.
    """
    
    def _get_orchestrator_metadata(self) -> OrchestratorMetadata:
        return OrchestratorMetadata(
            name="Company Compliance Orchestrator",
            version="1.0.0",
            type=OrchestratorType.COMPANY_CUSTOM,
            description="HIPAA/SOC2/PCI compliance validation",
            author="Company Engineering Team",
            capabilities=["hipaa_scan", "soc2_audit", "pci_validate"],
            requires_tdd=True,
            requires_git_isolation=False  # Company code in same repo
        )
    
    def _validate_preconditions(self, context: Dict) -> bool:
        # Company-specific checks
        return True
    
    def _execute_core_workflow(self, context: Dict) -> OrchestratorResult:
        # Company-specific compliance logic
        pass
```

---

## ✅ Benefits

### For CORTEX Developers

✅ **No repeated code** - Governance/audit/knowledge logic centralized  
✅ **SOLID compliance** - All orchestrators follow same architecture  
✅ **Automatic enforcement** - SKULL rules applied at every turn  
✅ **4-level audit trail** - Enterprise logging without extra code  
✅ **Knowledge integration** - SOLID/patterns automatically consulted

### For Company Developers

✅ **Easy extension** - Inherit from BaseOrchestrator, implement 3 methods  
✅ **Full CORTEX infrastructure** - Get governance/audit/knowledge for free  
✅ **Clear separation** - CORTEX vs company orchestrators distinguished  
✅ **Backward compatible** - Existing CORTEX orchestrators still work  
✅ **Production-ready** - Enterprise logging, error handling, rollback built-in

---

## 📊 Compliance Checklist

**Before merging to main:**

- [ ] BaseOrchestrator implements ALL 5 SOLID principles
- [ ] Zero duplicate governance/audit/knowledge code (DRY)
- [ ] All 3 SKULL checkpoints enforced (Phase -2, Runtime, Phase N+1)
- [ ] 4-level audit logging implemented (task→phase→epic→system)
- [ ] Knowledge library integration tested (SOLID/patterns queries)
- [ ] Example CORTEX orchestrator (Planning) implemented
- [ ] Example company orchestrator template provided
- [ ] 100% test coverage for BaseOrchestrator
- [ ] Integration tests for inheritance chain
- [ ] Documentation complete (this file + docstrings)

---

## 🚀 Migration Path

**Existing CORTEX orchestrators upgrade sequence:**

1. **Phase A: BaseOrchestrator v6 Foundation** (1 day)
   - Implement `src/orchestrators/base/base_orchestrator_v6.py`
   - Add interfaces (IAuditLogger, IGovernanceValidator, etc.)
   - Test with mock implementations

2. **Phase B: Planning Orchestrator ** (1 day)
   - Refactor `planning_orchestrator_v5.py` → `planning_orchestrator_v6.py`
   - Inherit from BaseOrchestrator
   - Remove duplicate governance/audit code
   - Test end-to-end

3. **Phase C: Remaining Orchestrators** (3 days)
   - TDD → TDD
   - ADO → ADO
   - Cleanup → Cleanup
   - Vacuum → Vacuum
   - Sanitization → Sanitization
   - Investigation → Investigation
   - Maintenance → Maintenance

4. **Phase D: Deprecate Old Versions** (1 day)
   - Archive v4/v5 base orchestrators
   - Update registry
   - Update documentation

**Total: 6 days**

---

**END OF SPECIFICATION**
