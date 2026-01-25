"""
Tests for Module Dependencies and Wiring - Comprehensive Module Integration Verification
AC-IDs tested: AC-FR-DISCOVERY-005+, AC-FR-MODULE-001-010, AC-CORE-020

Comprehensive module dependency tests ensuring:
- All module imports resolve correctly
- No broken module dependencies
- Proper module wiring and integration
- Module initialization order correct
- All expected modules present and accessible
- Dependency resolution without conflicts

"""

import pytest
import sys
import importlib
import inspect
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
from importlib.util import find_spec
import ast


# Module categories for comprehensive verification
MODULE_CATEGORIES = {
    "core_interfaces": [
        "cortex.core.interfaces",
        "cortex.core.result",
    ],
    "orchestrators": [
        "cortex.orchestrators.core",
        "cortex.orchestrators.core.master_orchestrator",
        "cortex.orchestrators.tools.todo_manager",
        "cortex.orchestrators.registry.orchestrator_registry",
        "cortex.orchestrators.registry.discovery_engine",
    ],
    "intent_routing": [
        "cortex.intent_router.classifier",
        "cortex.intent_router.routing_engine",
    ],
    "governance": [
        "cortex.brain.core.governance_registry",
        "cortex.brain.core.state_manager",
    ],
    "infrastructure": [
        "cortex.infrastructure.enhanced_audit_logger",
        "cortex.infrastructure.circuit_breaker",
        "cortex.infrastructure.connection_pool",
        "cortex.infrastructure.database",
    ],
}

# Critical module dependencies that must not be broken
CRITICAL_DEPENDENCIES = {
    "cortex.orchestrators.core.master_orchestrator": [
        "cortex.core.interfaces",
        "cortex.core.result",
        "cortex.brain.core.governance_registry",
        "cortex.infrastructure.enhanced_audit_logger",
        "cortex.orchestrators.tools.todo_manager",
    ],
    "cortex.orchestrators.tools.todo_manager": [
        "cortex.core.result",
    ],
    "cortex.brain.core.governance_registry": [
        "cortex.core.result",
    ],
}


class TestModuleCategoryImports:
    """AC-FR-MODULE-001: Test that all module categories are importable."""

    @pytest.mark.parametrize("category,modules", MODULE_CATEGORIES.items())
    def test_category_modules_importable(self, category: str, modules: List[str]) -> None:
        """Test AC-FR-MODULE-001: All modules in category are importable."""
        import_errors = {}
        
        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                import_errors[module_name] = str(e)
        
        assert not import_errors, (
            f"Failed to import modules in {category}:\n" +
            "\n".join(f"{m}: {e}" for m, e in import_errors.items())
        )


class TestCriticalDependencies:
    """AC-FR-MODULE-002: Test that critical dependencies are correctly resolved."""

    def test_critical_dependency_resolution(self) -> None:
        """Test AC-FR-MODULE-002: All critical dependencies resolve without errors."""
        unresolved = {}
        
        for module_name, dependencies in CRITICAL_DEPENDENCIES.items():
            try:
                module = importlib.import_module(module_name)
                
                # Verify each dependency is accessible
                for dep in dependencies:
                    try:
                        dep_module = importlib.import_module(dep)
                        assert dep_module is not None
                    except ImportError as e:
                        unresolved[f"{module_name} -> {dep}"] = str(e)
            except ImportError as e:
                unresolved[module_name] = str(e)
        
        assert not unresolved, (
            f"Unresolved critical dependencies:\n" +
            "\n".join(f"{d}: {e}" for d, e in unresolved.items())
        )

    def test_master_orchestrator_dependencies(self) -> None:
        """Test AC-FR-MODULE-003: MasterOrchestrator dependencies are complete."""
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            from cortex.core.interfaces import IOrchestrator
            from cortex.core.result import Result, Ok, Err
            from cortex.brain.core.governance_registry import GovernanceRegistry
            from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
            from cortex.orchestrators.tools.todo_manager import TodoManager
            
            # Instantiate to verify full initialization works
            master = MasterOrchestrator.instance()
            assert master is not None
            
        except ImportError as e:
            pytest.fail(f"MasterOrchestrator dependency import failed: {e}")

    def test_todo_manager_dependencies(self) -> None:
        """Test AC-FR-MODULE-004: TodoManager dependencies are complete."""
        try:
            from cortex.orchestrators.tools.todo_manager import TodoManager
            from cortex.core.result import Result, Ok, Err
            
            # Instantiate to verify initialization works
            mgr = TodoManager()
            assert mgr is not None
            
        except ImportError as e:
            pytest.fail(f"TodoManager dependency import failed: {e}")


class TestModuleAttributeAvailability:
    """AC-FR-MODULE-005: Test that expected module attributes are available."""

    def test_result_monad_has_required_methods(self) -> None:
        """Test AC-FR-MODULE-005: Result<T> monad has all required methods."""
        from cortex.core.result import Result, Ok, Err
        
        # Test Ok
        ok = Ok("value")
        assert hasattr(ok, "is_ok")
        assert hasattr(ok, "is_err")
        assert hasattr(ok, "value")
        assert callable(ok.is_ok)
        assert ok.is_ok()
        
        # Test Err
        err = Err("error")
        assert hasattr(err, "is_ok")
        assert hasattr(err, "is_err")
        assert hasattr(err, "error")
        assert callable(err.is_err)
        assert err.is_err()

    def test_orchestrator_interface_completeness(self) -> None:
        """Test AC-FR-MODULE-006: IOrchestrator interface is complete."""
        from cortex.core.interfaces import IOrchestrator
        
        # Verify interface has required methods
        required_methods = inspect.getmembers(IOrchestrator, predicate=inspect.isfunction)
        
        # Should have at least a few abstract methods
        assert len(required_methods) > 0, "IOrchestrator interface seems empty"

    def test_governance_registry_required_methods(self) -> None:
        """Test AC-FR-MODULE-007: GovernanceRegistry has required methods."""
        from cortex.brain.core.governance_registry import GovernanceRegistry
        
        registry = GovernanceRegistry.instance()
        
        required_methods = [
            "get_all_tier0_rules",
            "get_all_rules",
            "get_rule",
        ]
        
        for method in required_methods:
            assert hasattr(registry, method), f"GovernanceRegistry missing {method}"

    def test_audit_logger_required_methods(self) -> None:
        """Test AC-FR-MODULE-008: EnhancedAuditLogger has required methods."""
        from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
        
        logger = EnhancedAuditLogger.instance()
        
        required_methods = [
            "log_operation_start",
            "log_operation_complete",
        ]
        
        for method in required_methods:
            assert hasattr(logger, method), f"EnhancedAuditLogger missing {method}"


class TestModuleInitializationOrder:
    """AC-FR-MODULE-009: Test that module initialization order is correct."""

    def test_core_initializes_before_orchestrators(self) -> None:
        """Test AC-FR-MODULE-009: Core modules initialize before orchestrator modules."""
        try:
            # Import core first
            from cortex.core.result import Result
            from cortex.core.interfaces import IOrchestrator
            
            # Then import orchestrators
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            
            assert MasterOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Module initialization order issue: {e}")

    def test_governance_initializes_before_master(self) -> None:
        """Test AC-FR-MODULE-009: Governance registry initializes before MasterOrchestrator."""
        try:
            # Import governance
            from cortex.brain.core.governance_registry import GovernanceRegistry
            
            # Get instance (initialization)
            gov = GovernanceRegistry.instance()
            
            # Then import and initialize master
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            master = MasterOrchestrator.instance()
            
            assert gov is not None
            assert master is not None
        except Exception as e:
            pytest.fail(f"Governance initialization before master failed: {e}")


class TestModuleCircularImportDetection:
    """AC-FR-MODULE-010: Test detection and prevention of circular imports."""

    def test_no_circular_imports_in_core(self) -> None:
        """Test AC-FR-MODULE-010: No circular imports in core modules."""
        core_modules = [
            "cortex.core.result",
            "cortex.core.interfaces",
        ]
        
        for module_name in core_modules:
            try:
                # First import
                module1 = importlib.import_module(module_name)
                
                # Verify reimport returns same module
                module2 = importlib.import_module(module_name)
                
                assert module1 is module2, f"Module {module_name} not cached correctly"
            except ImportError as e:
                pytest.fail(f"Circular import detected in {module_name}: {e}")

    def test_module_dependency_graph_acyclic(self) -> None:
        """Test AC-FR-MODULE-010: Module dependency graph is acyclic."""
        # This is a simplified check - a full implementation would use AST analysis
        test_modules = [
            "cortex.core.result",
            "cortex.core.interfaces",
            "cortex.orchestrators.core.master_orchestrator",
        ]
        
        # Try importing in various orders - all should succeed
        import_orders = [
            test_modules,
            test_modules[::-1],
            [test_modules[1], test_modules[0], test_modules[2]],
        ]
        
        for order in import_orders:
            try:
                # Clear modules
                modules_to_clear = [m for m in sys.modules if any(m.startswith(t) for t in ["cortex"])]
                for m in modules_to_clear:
                    del sys.modules[m]
                
                # Re-import in order
                for module_name in order:
                    importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Circular dependency or import error in order {order}: {e}")


class TestModulePublicInterface:
    """AC-FR-MODULE-011: Test that public interfaces are properly exposed."""

    def test_master_orchestrator_public_interface(self) -> None:
        """Test AC-FR-MODULE-011: MasterOrchestrator exposes correct public interface."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        # Public methods that should not start with _
        public_members = [m for m in dir(MasterOrchestrator) if not m.startswith('_')]
        
        # Should have at least instance method
        assert any("instance" in m.lower() for m in public_members), \
            "MasterOrchestrator should have instance method"

    def test_todo_manager_public_interface(self) -> None:
        """Test AC-FR-MODULE-011: TodoManager exposes correct public interface."""
        from cortex.orchestrators.tools.todo_manager import TodoManager
        
        mgr = TodoManager()
        
        # Public methods
        public_methods = [m for m in dir(mgr) if not m.startswith('_') and callable(getattr(mgr, m))]
        
        # Should have main CRUD operations
        expected = ["create_task", "mark_phase", "get_task_status"]
        found = [m for m in expected if m in public_methods]
        
        assert len(found) >= 2, f"TodoManager missing expected methods: {expected}"


class TestPythonImportResolution:
    """AC-FR-DISCOVERY-005+: Test Python import system resolution."""

    def test_package_paths_resolvable(self) -> None:
        """Test AC-FR-DISCOVERY-005+: All package paths are resolvable."""
        packages_to_check = [
            "cortex",
            "cortex_brain",
            "cortex.orchestrators",
            "cortex.brain",
            "cortex.infrastructure",
        ]
        
        for pkg_name in packages_to_check:
            spec = find_spec(pkg_name)
            assert spec is not None, f"Cannot resolve package: {pkg_name}"

    def test_module_specs_complete(self) -> None:
        """Test AC-FR-DISCOVERY-005+: All module specs are complete."""
        modules = [
            "cortex.core.result",
            "cortex.core.interfaces",
            "cortex.orchestrators.core.master_orchestrator",
        ]
        
        for module_name in modules:
            spec = find_spec(module_name)
            assert spec is not None, f"Cannot find spec for {module_name}"
            assert spec.origin is not None, f"Module {module_name} has no origin"


class TestModuleLoading:
    """AC-FR-MODULE-012: Test that modules load without side effects issues."""

    def test_module_loading_idempotent(self) -> None:
        """Test AC-FR-MODULE-012: Module loading is idempotent."""
        module_name = "cortex.core.result"
        
        # Load multiple times
        m1 = importlib.import_module(module_name)
        m2 = importlib.import_module(module_name)
        m3 = importlib.import_module(module_name)
        
        # Should be same instance
        assert m1 is m2 is m3

    def test_orchestrator_modules_load_independently(self) -> None:
        """Test AC-FR-MODULE-012: Orchestrator modules can load independently."""
        orchestrator_modules = [
            "cortex.orchestrators.registry.orchestrator_registry",
            "cortex.orchestrators.registry.discovery_engine",
            "cortex.orchestrators.tools.todo_manager",
        ]
        
        for module_name in orchestrator_modules:
            try:
                # Should load successfully
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Orchestrator module failed to load: {module_name}: {e}")


class TestModuleConsistency:
    """AC-FR-MODULE-013: Test module consistency and coherence."""

    def test_singleton_instances_consistent(self) -> None:
        """Test AC-FR-MODULE-013: Singleton instances are consistent across imports."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        # Get instance multiple times
        m1 = MasterOrchestrator.instance()
        m2 = MasterOrchestrator.instance()
        
        # Should be same instance
        assert m1 is m2

    def test_registry_consistency(self) -> None:
        """Test AC-FR-MODULE-013: Registry instances are consistent."""
        # AC-PERMANENT-FIX-012: Use DatabaseBackedRegistry only
        from cortex.orchestrators import get_database_registry
        
        # Test DatabaseBackedRegistry consistency
        r1 = get_database_registry()
        r2 = get_database_registry()
        
        # Should be same instance (singleton pattern)
        assert r1 is r2

    def test_governance_registry_consistency(self) -> None:
        """Test AC-FR-MODULE-013: GovernanceRegistry instances are consistent."""
        from cortex.brain.core.governance_registry import GovernanceRegistry
        
        g1 = GovernanceRegistry.instance()
        g2 = GovernanceRegistry.instance()
        
        # Should be same instance
        assert g1 is g2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
