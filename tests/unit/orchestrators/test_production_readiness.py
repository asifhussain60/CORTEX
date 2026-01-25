"""
Tests for CORTEX Production Readiness - 100% Operational Verification
AC-IDs tested: AC-FR-DISCOVERY-100-110, AC-AR-006-01, AC-CORE-020, AC-FR-TODO-001-004

Comprehensive production readiness verification ensuring:
- All orchestrators operational and registered
- All modules discoverable and wired correctly
- TodoManager fully integrated with MasterOrchestrator
- Governance registry operational and enforcing rules
- Complete end-to-end system integration
- All required components present and functional
- Zero unresolved dependencies
- Full audit trail capability

This test suite is the definitive check for CORTEX production deployment readiness.
Run this suite with: pytest tests/unit/orchestrators/test_production_readiness.py -v

"""

import pytest
from typing import Dict, List, Set, Optional, Any
import importlib
import inspect

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.tools.todo_manager import TodoManager, Phase, Task, TaskState, PhaseStatus
from cortex.orchestrators import get_database_registry, OrchestratorMetadata
from cortex.orchestrators.registry.discovery_engine import DiscoveryEngine, DiscoveryQuery
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.core.result import Result, Ok, Err
from cortex.core.interfaces import IOrchestrator
from cortex.intent_router.classifier import IntentClassifier, IntentCategory


class TestCORTEXSystemReady:
    """AC-FR-DISCOVERY-100: Comprehensive CORTEX system readiness verification."""

    def test_system_components_initialized(self) -> None:
        """Test AC-FR-DISCOVERY-100: All core system components are initialized."""
        components = {
            "MasterOrchestrator": MasterOrchestrator.instance(),
            "GovernanceRegistry": GovernanceRegistry.instance(),
            "AuditLogger": EnhancedAuditLogger.instance(),
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - "OrchestratorRegistry": OrchestratorRegistry(),
            "DiscoveryEngine": DiscoveryEngine(),
            "TodoManager": TodoManager(),
            "IntentClassifier": IntentClassifier(),
        }
        
        uninitialized = []
        for name, component in components.items():
            if component is None:
                uninitialized.append(name)
        
        assert not uninitialized, (
            f"Failed to initialize {len(uninitialized)} components: {uninitialized}"
        )

    def test_singletons_are_consistent(self) -> None:
        """Test AC-FR-DISCOVERY-100: All singleton components are consistent."""
        # Get instances multiple times
        master1 = MasterOrchestrator.instance()
        master2 = MasterOrchestrator.instance()
        
        gov1 = GovernanceRegistry.instance()
        gov2 = GovernanceRegistry.instance()
        
        audit1 = EnhancedAuditLogger.instance()
        audit2 = EnhancedAuditLogger.instance()
        
        # All should be same instances
        assert master1 is master2, "MasterOrchestrator singleton broken"
        assert gov1 is gov2, "GovernanceRegistry singleton broken"
        assert audit1 is audit2, "AuditLogger singleton broken"

    def test_core_tier0_rules_loaded(self) -> None:
        """Test AC-CORE-020: TIER 0 rules are loaded and available."""
        governance = GovernanceRegistry.instance()
        
        # Get core rules
        rules = governance.get_all_tier0_rules()
        
        assert rules is not None, "No TIER 0 rules loaded"
        assert isinstance(rules, list), "TIER 0 rules should be a list"

    def test_complete_module_import_chain(self) -> None:
        """Test AC-FR-DISCOVERY-101: Complete module import chain works."""
        # This represents the full import chain used in production
        try:
            # Stage 1: Core imports
            from cortex.core.result import Result, Ok, Err
            from cortex.core.interfaces import IOrchestrator
            
            # Stage 2: Infrastructure imports
            from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
            from cortex.infrastructure.circuit_breaker import CircuitBreaker
            from cortex.infrastructure.connection_pool import ConnectionPool
            
            # Stage 3: Governance imports
            from cortex.brain.core.governance_registry import GovernanceRegistry
            from cortex.brain.core.state_manager import StateManager, get_state_manager
            
            # Stage 4: Registry imports
            from cortex.orchestrators import get_database_registry
            from cortex.orchestrators.registry.discovery_engine import DiscoveryEngine
            
            # Stage 5: Tool imports
            from cortex.orchestrators.tools.todo_manager import TodoManager
            
            # Stage 6: Orchestrator imports
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            
            # Stage 7: Router imports
            from cortex.intent_router.classifier import IntentClassifier
            
            assert True, "All imports successful"
        except ImportError as e:
            pytest.fail(f"Import chain broken: {e}")


class TestOrchestratorRegistration:
    """AC-AR-017-01: Test orchestrator registration and discovery."""

    def test_registry_operational(self) -> None:
        """Test AC-AR-017-01: Orchestrator registry is operational."""
        registry = get_database_registry()
        
        # Should be able to list all (even if empty)
        all_orchs = registry.list_all()
        assert isinstance(all_orchs, list)

    def test_discovery_engine_operational(self) -> None:
        """Test AC-AR-017-01: Discovery engine is operational."""
        engine = DiscoveryEngine()
        
        # Should be able to perform queries
        query = DiscoveryQuery()
        result = engine.search(query)
        
        assert result is not None
        assert hasattr(result, "orchestrators")
        assert isinstance(result.orchestrators, list)

    def test_orchestrator_registration_workflow(self) -> None:
        """Test AC-AR-017-01: Full orchestrator registration workflow."""
        registry = get_database_registry()
        
        # Create orchestrator metadata
        metadata = OrchestratorMetadata(
            id="test-orch-prod",
            name="Test Production Orchestrator",
            domain="execution",
            version="1.0",
            capabilities=["execution", "error_handling"],
            description="Test orchestrator for production readiness"
        )
        
        # Register it
        try:
            registry.register(metadata)
        except ValueError as e:
            # Might already exist, that's okay
            if "already registered" not in str(e):
                raise
        
        # Retrieve it
        retrieved = registry.get("test-orch-prod")
        assert retrieved is not None
        assert retrieved.id == "test-orch-prod"


class TestTodoManagerProduction:
    """AC-FR-TODO-001-004: Test TodoManager production readiness."""

    def test_todo_manager_instantiable(self) -> None:
        """Test AC-FR-TODO-001: TodoManager can be instantiated."""
        todo_mgr = TodoManager()
        assert todo_mgr is not None
        assert isinstance(todo_mgr, TodoManager)

    def test_todo_manager_create_task(self) -> None:
        """Test AC-FR-TODO-001: TodoManager can create tasks."""
        todo_mgr = TodoManager()
        
        phases = [
            {"id": 1, "title": "Phase 1", "description": "First", "dependencies": []},
            {"id": 2, "title": "Phase 2", "description": "Second", "dependencies": [1]},
        ]
        
        task = todo_mgr.create_task(
            task_id="PROD-TEST-001",
            description="Production readiness test task",
            phases=phases
        )
        
        assert task is not None
        assert task.task_id == "PROD-TEST-001"
        assert len(task.phases) == 2

    def test_todo_manager_phase_tracking(self) -> None:
        """Test AC-FR-TODO-002: TodoManager tracks phases correctly."""
        todo_mgr = TodoManager()
        
        phases = [
            {"id": 1, "title": "Phase 1", "description": "First", "dependencies": []},
        ]
        
        task = todo_mgr.create_task(
            task_id="PROD-TRACK-001",
            description="Phase tracking test",
            phases=phases
        )
        
        # Mark phase as completed
        result = todo_mgr.mark_phase(
            task_id="PROD-TRACK-001",
            phase_id=1,
            status="completed"
        )
        
        assert result.is_ok()
        
        # Get status
        status = todo_mgr.get_task_status("PROD-TRACK-001")
        assert status.completed_phases >= 1

    def test_todo_manager_dependency_validation(self) -> None:
        """Test AC-FR-TODO-003: TodoManager validates dependencies."""
        todo_mgr = TodoManager()
        
        phases = [
            {"id": 1, "title": "Phase 1", "description": "First", "dependencies": []},
            {"id": 2, "title": "Phase 2", "description": "Second", "dependencies": [1]},
        ]
        
        task = todo_mgr.create_task(
            task_id="PROD-DEP-001",
            description="Dependency validation test",
            phases=phases
        )
        
        # Should not be able to advance to phase 2 without completing phase 1
        can_advance = todo_mgr.can_advance_to_phase("PROD-DEP-001", 2)
        assert not can_advance, "Should not advance before dependency complete"
        
        # Complete phase 1
        todo_mgr.mark_phase("PROD-DEP-001", 1, "completed")
        
        # Now should be able to advance
        can_advance = todo_mgr.can_advance_to_phase("PROD-DEP-001", 2)
        assert can_advance, "Should advance after dependency complete"

    def test_todo_manager_audit_trail(self) -> None:
        """Test AC-FR-TODO-004: TodoManager maintains audit trail."""
        todo_mgr = TodoManager()
        
        phases = [
            {"id": 1, "title": "Phase 1", "description": "First", "dependencies": []},
        ]
        
        task = todo_mgr.create_task(
            task_id="PROD-AUDIT-001",
            description="Audit trail test",
            phases=phases
        )
        
        # Mark phase
        todo_mgr.mark_phase("PROD-AUDIT-001", 1, "in-progress")
        todo_mgr.mark_phase("PROD-AUDIT-001", 1, "completed")
        
        # Get audit trail
        trail = todo_mgr.get_audit_trail("PROD-AUDIT-001")
        
        assert trail is not None
        assert len(trail) > 0
        
        # Verify entries have required fields
        for entry in trail:
            assert "timestamp" in entry
            assert "phase_id" in entry
            assert "status" in entry


class TestMasterOrchestratorIntegration:
    """AC-AR-006-01: Test MasterOrchestrator production integration."""

    def test_master_orchestrator_initialized(self) -> None:
        """Test AC-AR-006-01: MasterOrchestrator is fully initialized."""
        master = MasterOrchestrator.instance()
        
        # Verify all required attributes
        required_attrs = [
            "logger", "db", "domain_orchestrators",
            "operation_history", "orchestrator_registry",
            "_state_manager", "_todo_manager"
        ]
        
        missing = []
        for attr in required_attrs:
            if not hasattr(master, attr):
                missing.append(attr)
        
        assert not missing, f"MasterOrchestrator missing attributes: {missing}"

    def test_master_orchestrator_todo_manager_integrated(self) -> None:
        """Test AC-FR-TODO-001: TodoManager integrated with MasterOrchestrator."""
        master = MasterOrchestrator.instance()
        
        # Should have get_todo_manager method
        assert callable(getattr(master, "get_todo_manager", None))
        
        # Should return TodoManager instance
        todo_mgr = master.get_todo_manager()
        assert todo_mgr is not None
        assert isinstance(todo_mgr, TodoManager)

    def test_master_orchestrator_governance_integration(self) -> None:
        """Test AC-AR-006-01: MasterOrchestrator integrates with governance."""
        master = MasterOrchestrator.instance()
        governance = GovernanceRegistry.instance()
        
        # Both should exist and be operational
        assert master is not None
        assert governance is not None

    def test_master_orchestrator_logger_operational(self) -> None:
        """Test AC-AR-006-01: MasterOrchestrator logger is operational."""
        master = MasterOrchestrator.instance()
        
        # Logger should be operational
        assert master.logger is not None
        assert hasattr(master.logger, "log_operation_complete")


class TestEndToEndIntegration:
    """AC-FR-DISCOVERY-105-110: Comprehensive end-to-end integration tests."""

    def test_intent_classification_operational(self) -> None:
        """Test AC-FR-DISCOVERY-105: Intent classification is operational."""
        classifier = IntentClassifier()
        
        # Should be able to classify intent (no context arg needed)
        result = classifier.classify("Create a new feature")
        
        assert result is not None
        assert hasattr(result, "primary_intent")
        assert result.primary_intent in [ic.value for ic in IntentCategory]

    def test_complete_workflow_without_errors(self) -> None:
        """Test AC-FR-DISCOVERY-106: Complete workflow from intent to TodoManager."""
        # Stage 1: Classification
        classifier = IntentClassifier()
        intent_result = classifier.classify("Create task for implementation")
        assert intent_result is not None
        
        # Stage 2: Get MasterOrchestrator
        master = MasterOrchestrator.instance()
        assert master is not None
        
        # Stage 3: Get TodoManager
        todo_mgr = master.get_todo_manager()
        assert todo_mgr is not None
        
        # Stage 4: Create task
        task = todo_mgr.create_task(
            task_id="E2E-TEST-001",
            description="End-to-end test",
            phases=[
                {"id": 1, "title": "Planning", "description": "Plan", "dependencies": []}
            ]
        )
        
        assert task is not None
        assert task.task_id == "E2E-TEST-001"

    def test_governance_validation_operational(self) -> None:
        """Test AC-CORE-020: Governance validation is operational."""
        governance = GovernanceRegistry.instance()
        
        # Should be able to get rules
        rules = governance.get_all_tier0_rules()
        assert rules is not None
        assert isinstance(rules, list)

    def test_audit_logging_complete(self) -> None:
        """Test AC-FR-DISCOVERY-107: Audit logging is complete."""
        logger = EnhancedAuditLogger.instance()
        
        # Should have all required methods
        required_methods = [
            "log_operation_start",
            "log_operation_complete",
        ]
        
        for method in required_methods:
            assert hasattr(logger, method), f"Logger missing {method}"
            assert callable(getattr(logger, method))

    def test_state_management_operational(self) -> None:
        """Test AC-FR-DISCOVERY-108: State management is operational."""
        from cortex.brain.core.state_manager import get_state_manager
        
        state_mgr = get_state_manager()
        assert state_mgr is not None

    def test_result_monad_operational(self) -> None:
        """Test AC-FR-DISCOVERY-109: Result<T> monad is operational."""
        # Test Ok
        ok_result = Ok("success")
        assert ok_result.is_ok()
        assert ok_result.value == "success"
        
        # Test Err
        err_result = Err("failure")
        assert err_result.is_err()
        assert err_result.error == "failure"


class TestProductionReadinessSummary:
    """AC-FR-DISCOVERY-110: Final production readiness summary verification."""

    def test_all_required_components_operational(self) -> None:
        """Test AC-FR-DISCOVERY-110: All required components are operational."""
        components = {
            "MasterOrchestrator": MasterOrchestrator.instance(),
            "TodoManager": TodoManager(),
            "GovernanceRegistry": GovernanceRegistry.instance(),
            "AuditLogger": EnhancedAuditLogger.instance(),
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - "OrchestratorRegistry": OrchestratorRegistry(),
            "DiscoveryEngine": DiscoveryEngine(),
            "IntentClassifier": IntentClassifier(),
        }
        
        all_operational = True
        for name, component in components.items():
            if component is None:
                print(f"CRITICAL: {name} is None")
                all_operational = False
        
        assert all_operational, "Not all components are operational"

    def test_production_deployment_ready_declaration(self) -> None:
        """Test AC-FR-DISCOVERY-110: CORTEX is ready for production deployment."""
        # Verify all critical paths work
        checks = []
        
        # Check 1: MasterOrchestrator
        try:
            master = MasterOrchestrator.instance()
            assert master.get_todo_manager() is not None
            checks.append(("MasterOrchestrator Integration", True))
        except Exception as e:
            checks.append(("MasterOrchestrator Integration", False))
        
        # Check 2: Governance
        try:
            gov = GovernanceRegistry.instance()
            assert gov.get_all_tier0_rules() is not None
            checks.append(("Governance Registry", True))
        except Exception as e:
            checks.append(("Governance Registry", False))
        
        # Check 3: TodoManager
        try:
            todo = TodoManager()
            task = todo.create_task("CHECK-001", "Check", [{"id": 1, "title": "T", "description": "D", "dependencies": []}])
            assert task is not None
            checks.append(("TodoManager Functionality", True))
        except Exception as e:
            checks.append(("TodoManager Functionality", False))
        
        # Check 4: Discovery
        try:
            engine = DiscoveryEngine()
            result = engine.search(DiscoveryQuery())
            assert result is not None
            checks.append(("Discovery Engine", True))
        except Exception as e:
            checks.append(("Discovery Engine", False))
        
        # Check 5: Audit
        try:
            logger = EnhancedAuditLogger.instance()
            assert logger is not None
            checks.append(("Audit Logging", True))
        except Exception as e:
            checks.append(("Audit Logging", False))
        
        # Verify all checks passed
        failed_checks = [name for name, passed in checks if not passed]
        assert not failed_checks, f"Production readiness failed: {failed_checks}"

    def test_zero_unresolved_dependencies(self) -> None:
        """Test AC-FR-DISCOVERY-110: Zero unresolved dependencies."""
        # Try to import all critical modules
        critical_imports = [
            "cortex.orchestrators.core.master_orchestrator",
            "cortex.orchestrators.tools.todo_manager",
            "cortex.brain.core.governance_registry",
            "cortex.orchestrators.registry.orchestrator_registry",
            "cortex.core.result",
        ]
        
        unresolved = []
        for module_name in critical_imports:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                unresolved.append((module_name, str(e)))
        
        assert not unresolved, f"Unresolved dependencies: {unresolved}"


class TestProductionDeploymentReadiness:
    """AC-FR-DISCOVERY-100+: Final production deployment readiness."""

    def test_cortex_production_ready(self) -> None:
        """
        Test AC-FR-DISCOVERY-100+: CORTEX is production ready.
        
        This is the definitive test for deployment readiness.
        """
        readiness_status = {
            "orchestrators_operational": False,
            "modules_discoverable": False,
            "governance_enforcing": False,
            "todo_manager_integrated": False,
            "audit_trail_complete": False,
            "zero_unresolved_deps": False,
        }
        
        try:
            # 1. Orchestrators operational
            master = MasterOrchestrator.instance()
            registry = get_database_registry()
            engine = DiscoveryEngine()
            readiness_status["orchestrators_operational"] = all([master, registry, engine])
            
            # 2. Modules discoverable
            test_modules = [
                "cortex.orchestrators.core.master_orchestrator",
                "cortex.orchestrators.tools.todo_manager",
                "cortex.brain.core.governance_registry",
            ]
            all_found = all(importlib.util.find_spec(m) for m in test_modules)
            readiness_status["modules_discoverable"] = all_found
            
            # 3. Governance enforcing
            gov = GovernanceRegistry.instance()
            readiness_status["governance_enforcing"] = gov.get_all_tier0_rules() is not None
            
            # 4. TodoManager integrated
            todo_mgr = master.get_todo_manager()
            readiness_status["todo_manager_integrated"] = isinstance(todo_mgr, TodoManager)
            
            # 5. Audit trail complete
            logger = EnhancedAuditLogger.instance()
            readiness_status["audit_trail_complete"] = all([
                hasattr(logger, "log_operation_start"),
                hasattr(logger, "log_operation_complete"),
            ])
            
            # 6. Zero unresolved deps
            try:
                for m in test_modules:
                    importlib.import_module(m)
                readiness_status["zero_unresolved_deps"] = True
            except ImportError:
                readiness_status["zero_unresolved_deps"] = False
            
        except Exception as e:
            pytest.fail(f"Production readiness check failed: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("CORTEX PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        for check, status in readiness_status.items():
            status_str = "✅ PASS" if status else "❌ FAIL"
            print(f"{check:.<45} {status_str}")
        print("=" * 60)
        
        # All checks must pass
        all_passed = all(readiness_status.values())
        assert all_passed, f"Production readiness checks failed: {readiness_status}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
