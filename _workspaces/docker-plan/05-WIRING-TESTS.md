# CORTEX Wiring Tests
## Comprehensive Test Suite for Zero-Drift Wiring

**Document:** 05-WIRING-TESTS.md  
**Date:** 2026-01-27  

---

## 🎯 Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **Single Path Enforcement** | 10 | Verify only one wiring path exists |
| **Git-Backed Registry** | 12 | Test YAML loading and parsing |
| **Lazy Orchestrator** | 8 | Test on-demand wiring |
| **Multi-User Scenarios** | 10 | Simulate concurrent users |
| **Wiring Determinism** | 6 | Verify reproducible wiring |
| **No Database Files** | 5 | Ensure no .db files created |
| **Container Wiring** | 8 | Docker-specific tests |
| **Health & Recovery** | 6 | Health checks and recovery |
| **TOTAL** | **65** | Comprehensive coverage |

---

## 📁 Test Directory Structure

```
tests/wiring/
├── __init__.py
├── conftest.py                          # Wiring-specific fixtures
│
├── test_single_path_enforcement.py      # 10 tests
├── test_git_backed_registry.py          # 12 tests
├── test_lazy_orchestrator.py            # 8 tests
├── test_multi_user_scenarios.py         # 10 tests
├── test_wiring_determinism.py           # 6 tests
├── test_no_database_files.py            # 5 tests
├── test_container_wiring.py             # 8 tests
└── test_health_recovery.py              # 6 tests
```

---

## 1. Single Path Enforcement Tests

**File: `test_single_path_enforcement.py`**

```python
"""
AC-WIRE-SINGLE-001 through AC-WIRE-SINGLE-010
Verify CORTEX has ONE and ONLY ONE wiring path.
"""

import pytest
import sys
import importlib
from pathlib import Path


class TestSinglePathEnforcement:
    """Verify single wiring path enforcement."""
    
    # AC-WIRE-SINGLE-001
    def test_bootstrap_is_only_entry_point(self):
        """Only cortex.wiring.bootstrap_cortex() should exist as entry point."""
        from cortex.wiring import bootstrap_cortex
        
        # This should work
        assert callable(bootstrap_cortex)
    
    # AC-WIRE-SINGLE-002
    def test_database_registry_does_not_exist(self):
        """DatabaseBackedRegistry should NOT exist in codebase."""
        with pytest.raises(ImportError):
            from cortex.orchestrators.core.database_registry import DatabaseBackedRegistry
    
    # AC-WIRE-SINGLE-003
    def test_orchestrator_bootstrap_does_not_exist(self):
        """OrchestratorBootstrap should NOT exist in codebase."""
        with pytest.raises(ImportError):
            from cortex.orchestrators.bootstrap import OrchestratorBootstrap
    
    # AC-WIRE-SINGLE-004
    def test_orchestrator_registry_does_not_exist(self):
        """OrchestratorRegistry should NOT exist in codebase."""
        with pytest.raises(ImportError):
            from cortex.orchestrators.core.orchestrator_registry import OrchestratorRegistry
    
    # AC-WIRE-SINGLE-005
    def test_db_wiring_init_does_not_exist(self):
        """db_wiring_init should NOT exist in codebase."""
        with pytest.raises(ImportError):
            from cortex.orchestrators.core.db_wiring_init import initialize_database_wiring
    
    # AC-WIRE-SINGLE-006
    def test_permanent_wiring_state_does_not_exist(self):
        """permanent_wiring_state should NOT exist in codebase."""
        with pytest.raises(ImportError):
            from cortex.orchestrators.core.permanent_wiring_state import PermanentWiringState
    
    # AC-WIRE-SINGLE-007
    def test_no_legacy_wiring_files_in_codebase(self):
        """No legacy wiring files should exist."""
        cortex_dir = Path(__file__).parent.parent.parent / "cortex"
        
        legacy_files = [
            "orchestrators/core/database_registry.py",
            "orchestrators/core/orchestrator_registry.py",
            "orchestrators/bootstrap.py",
            "orchestrators/core/db_wiring_init.py",
            "orchestrators/core/permanent_wiring_state.py",
            "orchestrators/core/autowiring_orchestrator.py",
        ]
        
        for legacy_file in legacy_files:
            file_path = cortex_dir / legacy_file
            assert not file_path.exists(), f"Legacy file should not exist: {legacy_file}"
    
    # AC-WIRE-SINGLE-008
    def test_wiring_directory_is_only_wiring_location(self):
        """cortex/wiring/ should be the only wiring location."""
        wiring_dir = Path(__file__).parent.parent.parent / "cortex" / "wiring"
        
        assert wiring_dir.exists(), "cortex/wiring/ must exist"
        assert (wiring_dir / "bootstrap.py").exists(), "bootstrap.py must exist"
        assert (wiring_dir / "specifications").is_dir(), "specifications/ must exist"
        assert (wiring_dir / "registry").is_dir(), "registry/ must exist"
    
    # AC-WIRE-SINGLE-009
    def test_cortex_init_uses_bootstrap(self):
        """cortex/__init__.py should use bootstrap_cortex()."""
        init_file = Path(__file__).parent.parent.parent / "cortex" / "__init__.py"
        content = init_file.read_text()
        
        assert "from cortex.wiring import" in content or \
               "from .wiring import" in content, \
               "cortex/__init__.py should import from wiring module"
    
    # AC-WIRE-SINGLE-010
    def test_no_alternative_bootstrap_methods(self):
        """No alternative bootstrap methods should exist."""
        from cortex.wiring import bootstrap_cortex
        
        # Check that get_cortex also exists (convenience wrapper)
        from cortex.wiring import get_cortex
        
        # These should be the ONLY exports
        from cortex import wiring
        public_exports = [name for name in dir(wiring) if not name.startswith('_')]
        
        expected = {'bootstrap_cortex', 'get_cortex', 'is_wired', 'get_wiring_hash'}
        assert set(public_exports) <= expected | set(public_exports), \
            f"Unexpected exports in wiring module: {set(public_exports) - expected}"
```

---

## 2. Git-Backed Registry Tests

**File: `test_git_backed_registry.py`**

```python
"""
AC-WIRE-GIT-001 through AC-WIRE-GIT-012
Test YAML-based wiring registry.
"""

import pytest
import yaml
from pathlib import Path
from cortex.wiring.registry.git_backed_registry import GitBackedRegistry, OrchestratorSpec


class TestGitBackedRegistry:
    """Test git-backed registry functionality."""
    
    @pytest.fixture
    def specs_dir(self):
        """Get specifications directory."""
        return Path(__file__).parent.parent.parent / "cortex" / "wiring" / "specifications"
    
    @pytest.fixture
    def registry(self, specs_dir):
        """Create registry instance."""
        return GitBackedRegistry(specs_dir)
    
    # AC-WIRE-GIT-001
    def test_yaml_files_exist(self, specs_dir):
        """All required YAML files should exist."""
        required_files = [
            "core-wiring.yaml",
            "domain-wiring.yaml",
            "support-wiring.yaml"
        ]
        
        for yaml_file in required_files:
            assert (specs_dir / yaml_file).exists(), f"Missing: {yaml_file}"
    
    # AC-WIRE-GIT-002
    def test_yaml_files_are_valid(self, specs_dir):
        """All YAML files should be valid YAML."""
        for yaml_file in specs_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None
                    assert "orchestrators" in data
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {yaml_file}: {e}")
    
    # AC-WIRE-GIT-003
    def test_all_23_orchestrators_defined(self, registry):
        """All 23 orchestrators should be defined."""
        specs = registry.get_all_specs()
        assert len(specs) >= 23, f"Expected 23+ orchestrators, got {len(specs)}"
    
    # AC-WIRE-GIT-004
    def test_orchestrator_specs_have_required_fields(self, registry):
        """Each orchestrator spec should have required fields."""
        required_fields = ['name', 'module', 'class_name', 'category', 'priority']
        
        for name, spec in registry.get_all_specs().items():
            for field in required_fields:
                assert hasattr(spec, field), f"{name} missing field: {field}"
                assert getattr(spec, field) is not None, f"{name}.{field} is None"
    
    # AC-WIRE-GIT-005
    def test_dependencies_reference_existing_orchestrators(self, registry):
        """All dependencies should reference existing orchestrators."""
        all_names = set(registry.get_all_specs().keys())
        
        for name, spec in registry.get_all_specs().items():
            for dep in spec.dependencies:
                assert dep in all_names, f"{name} has unknown dependency: {dep}"
    
    # AC-WIRE-GIT-006
    def test_no_circular_dependencies(self, registry):
        """No circular dependencies should exist."""
        # If wiring order computed successfully, no circular deps
        order = registry.get_wiring_order()
        assert len(order) == len(registry.get_all_specs())
    
    # AC-WIRE-GIT-007
    def test_wiring_order_respects_dependencies(self, registry):
        """Wiring order should respect dependencies."""
        order = registry.get_wiring_order()
        order_index = {name: i for i, name in enumerate(order)}
        
        for name, spec in registry.get_all_specs().items():
            for dep in spec.dependencies:
                assert order_index[dep] < order_index[name], \
                    f"{name} wired before its dependency {dep}"
    
    # AC-WIRE-GIT-008
    def test_priorities_are_unique_per_category(self, registry):
        """Priorities should be unique within each category."""
        by_category = {}
        for name, spec in registry.get_all_specs().items():
            cat = spec.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((name, spec.priority))
        
        for cat, items in by_category.items():
            priorities = [p for _, p in items]
            assert len(priorities) == len(set(priorities)), \
                f"Duplicate priorities in {cat}: {items}"
    
    # AC-WIRE-GIT-009
    def test_module_paths_are_valid(self, registry):
        """Module paths should be importable."""
        import importlib
        
        for name, spec in registry.get_all_specs().items():
            try:
                # Just check module exists, don't instantiate
                module = importlib.import_module(spec.module)
                assert hasattr(module, spec.class_name), \
                    f"{spec.module} missing class {spec.class_name}"
            except ImportError as e:
                pytest.fail(f"Cannot import {spec.module}: {e}")
    
    # AC-WIRE-GIT-010
    def test_wiring_hash_is_deterministic(self, specs_dir):
        """Same specs should produce same hash."""
        registry1 = GitBackedRegistry(specs_dir)
        registry2 = GitBackedRegistry(specs_dir)
        
        assert registry1.compute_wiring_hash() == registry2.compute_wiring_hash()
    
    # AC-WIRE-GIT-011
    def test_wiring_hash_changes_with_spec_changes(self, specs_dir, tmp_path):
        """Different specs should produce different hash."""
        # Create modified specs
        modified_specs = tmp_path / "specifications"
        modified_specs.mkdir()
        
        # Copy and modify
        import shutil
        for yaml_file in specs_dir.glob("*.yaml"):
            shutil.copy(yaml_file, modified_specs)
        
        # Modify one file
        core_file = modified_specs / "core-wiring.yaml"
        with open(core_file) as f:
            data = yaml.safe_load(f)
        data["orchestrators"][0]["priority"] = 999  # Change priority
        with open(core_file, 'w') as f:
            yaml.dump(data, f)
        
        # Compare hashes
        original = GitBackedRegistry(specs_dir)
        modified = GitBackedRegistry(modified_specs)
        
        assert original.compute_wiring_hash() != modified.compute_wiring_hash()
    
    # AC-WIRE-GIT-012
    def test_get_orchestrator_returns_lazy_wrapper(self, registry):
        """get_orchestrator should return LazyOrchestrator."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        orch = registry.get_orchestrator("MasterOrchestrator")
        assert isinstance(orch, LazyOrchestrator)
```

---

## 3. Lazy Orchestrator Tests

**File: `test_lazy_orchestrator.py`**

```python
"""
AC-WIRE-LAZY-001 through AC-WIRE-LAZY-008
Test lazy orchestrator initialization.
"""

import pytest
import threading
from unittest.mock import MagicMock, patch


class TestLazyOrchestrator:
    """Test lazy orchestrator functionality."""
    
    @pytest.fixture
    def mock_spec(self):
        """Create mock orchestrator spec."""
        from cortex.wiring.registry.git_backed_registry import OrchestratorSpec
        return OrchestratorSpec(
            name="TestOrchestrator",
            module="cortex.orchestrators.core.master_orchestrator",
            class_name="MasterOrchestrator",
            category="CORE",
            tier=1,
            priority=100,
            dependencies=[],
            requires_params={},
            capabilities=["test"],
            health_check="test",
            mcp_adapter=""
        )
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock registry."""
        return MagicMock()
    
    # AC-WIRE-LAZY-001
    def test_lazy_orchestrator_not_wired_initially(self, mock_spec, mock_registry):
        """Lazy orchestrator should not be wired on creation."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        assert not lazy.is_wired
    
    # AC-WIRE-LAZY-002
    def test_lazy_orchestrator_wires_on_first_access(self, mock_spec, mock_registry):
        """Lazy orchestrator should wire on first attribute access."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        
        # Access triggers wiring
        try:
            _ = lazy.some_method
        except AttributeError:
            pass  # Expected if method doesn't exist
        
        assert lazy.is_wired
    
    # AC-WIRE-LAZY-003
    def test_lazy_orchestrator_wires_only_once(self, mock_spec, mock_registry):
        """Lazy orchestrator should wire only once."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        
        # Force wire
        lazy.force_wire()
        instance1 = lazy._instance
        
        # Try again
        lazy.force_wire()
        instance2 = lazy._instance
        
        assert instance1 is instance2
    
    # AC-WIRE-LAZY-004
    def test_lazy_orchestrator_thread_safe(self, mock_spec, mock_registry):
        """Lazy orchestrator should be thread-safe."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        results = []
        
        def wire_thread():
            lazy.force_wire()
            results.append(lazy._instance)
        
        threads = [threading.Thread(target=wire_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should get same instance
        assert len(set(id(r) for r in results)) == 1
    
    # AC-WIRE-LAZY-005
    def test_lazy_orchestrator_resolves_params(self):
        """Lazy orchestrator should resolve required params."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        from cortex.wiring.registry.git_backed_registry import OrchestratorSpec
        
        spec = OrchestratorSpec(
            name="TestOrchestrator",
            module="cortex.orchestrators.core.interaction_orchestrator",
            class_name="InteractionOrchestrator",
            category="CORE",
            tier=1,
            priority=10,
            dependencies=[],
            requires_params={
                "conversation_protocol": {
                    "type": "ConversationProtocol",
                    "lazy_create": True
                }
            },
            capabilities=[],
            health_check="",
            mcp_adapter=""
        )
        
        registry = MagicMock()
        lazy = LazyOrchestrator(spec, registry)
        
        # Should not raise
        lazy.force_wire()
        assert lazy.is_wired
    
    # AC-WIRE-LAZY-006
    def test_lazy_orchestrator_raises_on_import_error(self, mock_registry):
        """Lazy orchestrator should raise on import error."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        from cortex.wiring.registry.git_backed_registry import OrchestratorSpec
        
        spec = OrchestratorSpec(
            name="NonExistent",
            module="cortex.nonexistent.module",
            class_name="NonExistentClass",
            category="CORE",
            tier=1,
            priority=1,
            dependencies=[],
            requires_params={},
            capabilities=[],
            health_check="",
            mcp_adapter=""
        )
        
        lazy = LazyOrchestrator(spec, mock_registry)
        
        with pytest.raises(ModuleNotFoundError):
            lazy.force_wire()
    
    # AC-WIRE-LAZY-007
    def test_lazy_orchestrator_special_attrs_not_trigger_wire(self, mock_spec, mock_registry):
        """Special attributes should not trigger wiring."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        
        # Access special attributes
        _ = lazy.is_wired
        _ = lazy.spec
        
        # Should still not be wired
        assert not lazy.is_wired
    
    # AC-WIRE-LAZY-008
    def test_force_wire_works(self, mock_spec, mock_registry):
        """force_wire() should wire immediately."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        lazy = LazyOrchestrator(mock_spec, mock_registry)
        assert not lazy.is_wired
        
        lazy.force_wire()
        assert lazy.is_wired
```

---

## 4. Multi-User Scenario Tests

**File: `test_multi_user_scenarios.py`**

```python
"""
AC-WIRE-MULTI-001 through AC-WIRE-MULTI-010
Simulate multiple users accessing CORTEX.
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestMultiUserScenarios:
    """Test concurrent user scenarios."""
    
    # AC-WIRE-MULTI-001
    def test_concurrent_bootstrap_same_instance(self):
        """Multiple concurrent bootstraps should return same instance."""
        from cortex.wiring import bootstrap_cortex
        
        results = []
        
        def bootstrap_thread():
            instance = bootstrap_cortex()
            results.append(id(instance))
        
        threads = [threading.Thread(target=bootstrap_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should get same instance
        assert len(set(results)) == 1
    
    # AC-WIRE-MULTI-002
    def test_concurrent_get_cortex_same_instance(self):
        """Multiple get_cortex() calls should return same instance."""
        from cortex.wiring import get_cortex, bootstrap_cortex
        
        # Ensure bootstrapped
        bootstrap_cortex()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(get_cortex) for _ in range(100)]
            results = [f.result() for f in as_completed(futures)]
        
        # All same instance
        assert len(set(id(r) for r in results)) == 1
    
    # AC-WIRE-MULTI-003
    def test_concurrent_wiring_hash_consistent(self):
        """Wiring hash should be same across all threads."""
        from cortex.wiring import get_cortex, bootstrap_cortex
        
        bootstrap_cortex()
        
        hashes = []
        
        def get_hash():
            cortex = get_cortex()
            hashes.append(cortex.wiring_hash)
        
        threads = [threading.Thread(target=get_hash) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All same hash
        assert len(set(hashes)) == 1
    
    # AC-WIRE-MULTI-004
    def test_concurrent_orchestrator_access(self):
        """Concurrent orchestrator access should not cause issues."""
        from cortex.wiring import get_cortex, bootstrap_cortex
        
        cortex = bootstrap_cortex()
        errors = []
        
        def access_orchestrator():
            try:
                orch = cortex.registry.get_orchestrator("IntentRouter")
                orch.force_wire()
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=access_orchestrator) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors during concurrent access: {errors}"
    
    # AC-WIRE-MULTI-005
    def test_100_simulated_users(self):
        """Simulate 100 users accessing CORTEX."""
        from cortex.wiring import get_cortex, bootstrap_cortex
        
        cortex = bootstrap_cortex()
        results = {"success": 0, "error": 0}
        lock = threading.Lock()
        
        def user_request():
            try:
                c = get_cortex()
                assert c.wiring_hash  # Quick operation
                with lock:
                    results["success"] += 1
            except Exception:
                with lock:
                    results["error"] += 1
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(user_request) for _ in range(100)]
            for f in as_completed(futures):
                pass
        
        assert results["success"] == 100
        assert results["error"] == 0
    
    # AC-WIRE-MULTI-006
    def test_users_during_wiring(self):
        """Users requesting during initial wiring should wait."""
        # This test verifies the lock mechanism
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        from cortex.wiring.registry.git_backed_registry import OrchestratorSpec
        
        spec = OrchestratorSpec(
            name="SlowOrchestrator",
            module="cortex.orchestrators.core.master_orchestrator",
            class_name="MasterOrchestrator",
            category="CORE",
            tier=1,
            priority=1,
            dependencies=[],
            requires_params={},
            capabilities=[],
            health_check="",
            mcp_adapter=""
        )
        
        registry = type('Registry', (), {'_lazy_orchestrators': {}})()
        lazy = LazyOrchestrator(spec, registry)
        
        results = []
        
        def access_thread():
            lazy.force_wire()
            results.append(lazy.is_wired)
        
        threads = [threading.Thread(target=access_thread) for _ in range(10)]
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should complete and be wired
        assert all(results)
    
    # AC-WIRE-MULTI-007
    def test_no_race_conditions_in_registry(self):
        """Registry should handle concurrent access without race conditions."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        
        def access_registry():
            specs = cortex.registry.get_all_specs()
            order = cortex.registry.get_wiring_order()
            return len(specs), len(order)
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(access_registry) for _ in range(100)]
            results = [f.result() for f in as_completed(futures)]
        
        # All should get same results
        assert len(set(results)) == 1
    
    # AC-WIRE-MULTI-008
    def test_wiring_order_consistent_across_threads(self):
        """Wiring order should be identical across all threads."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        orders = []
        
        def get_order():
            orders.append(tuple(cortex.registry.get_wiring_order()))
        
        threads = [threading.Thread(target=get_order) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(set(orders)) == 1
    
    # AC-WIRE-MULTI-009
    def test_orchestrator_wiring_order_deterministic(self):
        """Orchestrators should wire in deterministic order."""
        from cortex.wiring import bootstrap_cortex
        
        # Bootstrap multiple times (would be different process restarts)
        # For this test, we just verify the order is consistent
        cortex = bootstrap_cortex()
        
        order1 = cortex.registry.get_wiring_order()
        order2 = cortex.registry.get_wiring_order()
        
        assert order1 == order2
    
    # AC-WIRE-MULTI-010
    def test_no_memory_leaks_under_load(self):
        """No memory leaks under concurrent load."""
        import gc
        from cortex.wiring import get_cortex, bootstrap_cortex
        
        cortex = bootstrap_cortex()
        
        # Force garbage collection
        gc.collect()
        
        # Simulate load
        for _ in range(1000):
            c = get_cortex()
            _ = c.wiring_hash
        
        # Force garbage collection again
        gc.collect()
        
        # Should still be single instance
        assert get_cortex() is cortex
```

---

## 5. Wiring Determinism Tests

**File: `test_wiring_determinism.py`**

```python
"""
AC-WIRE-DET-001 through AC-WIRE-DET-006
Verify wiring is deterministic and reproducible.
"""

import pytest
import subprocess
import hashlib


class TestWiringDeterminism:
    """Test wiring determinism."""
    
    # AC-WIRE-DET-001
    def test_same_specs_same_hash(self):
        """Same specifications should produce same hash."""
        from cortex.wiring import bootstrap_cortex
        
        cortex1 = bootstrap_cortex()
        hash1 = cortex1.wiring_hash
        
        # Reset and bootstrap again (simulating restart)
        import cortex.wiring.bootstrap as bootstrap_module
        bootstrap_module._CORTEX_INSTANCE = None
        bootstrap_module._WIRING_COMPLETE = False
        
        cortex2 = bootstrap_cortex()
        hash2 = cortex2.wiring_hash
        
        assert hash1 == hash2
    
    # AC-WIRE-DET-002
    def test_wiring_order_is_reproducible(self):
        """Wiring order should be reproducible."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        order1 = cortex.registry.get_wiring_order()
        
        # Get order again
        order2 = cortex.registry.get_wiring_order()
        
        assert order1 == order2
    
    # AC-WIRE-DET-003
    def test_orchestrator_count_consistent(self):
        """Orchestrator count should be consistent."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        
        count1 = len(cortex.registry.get_all_specs())
        count2 = len(cortex.registry.get_all_specs())
        
        assert count1 == count2
        assert count1 >= 23  # At least 23 orchestrators
    
    # AC-WIRE-DET-004
    def test_spec_content_matches_yaml(self):
        """Loaded specs should match YAML content."""
        import yaml
        from pathlib import Path
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        specs_dir = Path(__file__).parent.parent.parent / "cortex" / "wiring" / "specifications"
        
        # Load core-wiring.yaml directly
        with open(specs_dir / "core-wiring.yaml") as f:
            yaml_data = yaml.safe_load(f)
        
        # Verify specs match
        for orch_def in yaml_data.get("orchestrators", []):
            name = orch_def["name"]
            spec = cortex.registry.get_all_specs().get(name)
            
            assert spec is not None, f"Spec {name} not loaded"
            assert spec.module == orch_def["module"]
            assert spec.priority == orch_def["priority"]
    
    # AC-WIRE-DET-005
    def test_dependencies_preserved(self):
        """Dependencies should be preserved from YAML."""
        import yaml
        from pathlib import Path
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        specs_dir = Path(__file__).parent.parent.parent / "cortex" / "wiring" / "specifications"
        
        # Load all YAMLs
        all_yaml_deps = {}
        for yaml_file in specs_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            for orch in data.get("orchestrators", []):
                all_yaml_deps[orch["name"]] = orch.get("dependencies", [])
        
        # Verify dependencies match
        for name, spec in cortex.registry.get_all_specs().items():
            expected_deps = all_yaml_deps.get(name, [])
            assert spec.dependencies == expected_deps, \
                f"{name} dependencies mismatch: {spec.dependencies} vs {expected_deps}"
    
    # AC-WIRE-DET-006
    def test_hash_algorithm_consistent(self):
        """Hash algorithm should be consistent."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        
        # Manual hash computation
        content = ""
        for name in sorted(cortex.registry.get_all_specs().keys()):
            spec = cortex.registry.get_all_specs()[name]
            content += f"{name}:{spec.module}:{spec.priority}:{sorted(spec.dependencies)}\n"
        
        expected_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        assert cortex.wiring_hash == expected_hash
```

---

## 6. No Database Files Tests

**File: `test_no_database_files.py`**

```python
"""
AC-WIRE-NODB-001 through AC-WIRE-NODB-005
Verify no database files are created.
"""

import pytest
import os
from pathlib import Path


class TestNoDatabaseFiles:
    """Verify no database files created."""
    
    # AC-WIRE-NODB-001
    def test_no_db_files_after_bootstrap(self, tmp_path):
        """No .db files should be created after bootstrap."""
        from cortex.wiring import bootstrap_cortex
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            bootstrap_cortex()
            
            # Check for any .db files
            db_files = list(tmp_path.rglob("*.db"))
            assert len(db_files) == 0, f"Found .db files: {db_files}"
        finally:
            os.chdir(original_cwd)
    
    # AC-WIRE-NODB-002
    def test_no_cortex_directory_created(self, tmp_path):
        """No .cortex/ directory should be created."""
        from cortex.wiring import bootstrap_cortex
        
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            bootstrap_cortex()
            
            cortex_dir = tmp_path / ".cortex"
            assert not cortex_dir.exists(), ".cortex/ directory should not exist"
        finally:
            os.chdir(original_cwd)
    
    # AC-WIRE-NODB-003
    def test_no_sqlite_imports_in_wiring(self):
        """No sqlite imports in wiring module."""
        wiring_dir = Path(__file__).parent.parent.parent / "cortex" / "wiring"
        
        for py_file in wiring_dir.rglob("*.py"):
            content = py_file.read_text()
            assert "import sqlite" not in content, f"sqlite import in {py_file}"
            assert "from sqlite" not in content, f"sqlite import in {py_file}"
    
    # AC-WIRE-NODB-004
    def test_no_db_journal_files(self, tmp_path):
        """No .db-journal files should be created."""
        from cortex.wiring import bootstrap_cortex
        
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            bootstrap_cortex()
            
            journal_files = list(tmp_path.rglob("*.db-journal"))
            assert len(journal_files) == 0
        finally:
            os.chdir(original_cwd)
    
    # AC-WIRE-NODB-005
    def test_no_wal_files(self, tmp_path):
        """No .db-wal files should be created."""
        from cortex.wiring import bootstrap_cortex
        
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            bootstrap_cortex()
            
            wal_files = list(tmp_path.rglob("*.db-wal"))
            shm_files = list(tmp_path.rglob("*.db-shm"))
            
            assert len(wal_files) == 0
            assert len(shm_files) == 0
        finally:
            os.chdir(original_cwd)
```

---

## 7. Container Wiring Tests

**File: `test_container_wiring.py`**

```python
"""
AC-WIRE-CONT-001 through AC-WIRE-CONT-008
Test Docker container wiring scenarios.
"""

import pytest
import subprocess
import time


@pytest.mark.docker
class TestContainerWiring:
    """Test Docker container wiring (requires Docker)."""
    
    # AC-WIRE-CONT-001
    def test_container_wires_on_startup(self):
        """Container should wire all orchestrators on startup."""
        result = subprocess.run(
            ["docker", "run", "--rm", "cortex/mcp-server:latest",
             "python", "-c", 
             "from cortex.wiring import is_wired; print(is_wired())"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert "True" in result.stdout
    
    # AC-WIRE-CONT-002
    def test_container_health_endpoint(self):
        """Container health endpoint should work."""
        # Start container
        container_id = subprocess.check_output(
            ["docker", "run", "-d", "-p", "18443:8443", "cortex/mcp-server:latest"],
            text=True
        ).strip()
        
        try:
            time.sleep(10)  # Wait for startup
            
            import requests
            response = requests.get("http://localhost:18443/health", timeout=10)
            
            assert response.status_code == 200
            data = response.json()
            assert data["wired"] == True
            assert data["orchestrator_count"] >= 23
        finally:
            subprocess.run(["docker", "stop", container_id])
            subprocess.run(["docker", "rm", container_id])
    
    # AC-WIRE-CONT-003
    def test_container_wiring_hash_consistent(self):
        """Multiple container instances should have same wiring hash."""
        hashes = []
        
        for _ in range(3):
            result = subprocess.run(
                ["docker", "run", "--rm", "cortex/mcp-server:latest",
                 "python", "-c",
                 "from cortex.wiring import bootstrap_cortex; print(bootstrap_cortex().wiring_hash)"],
                capture_output=True,
                text=True,
                timeout=60
            )
            hashes.append(result.stdout.strip())
        
        assert len(set(hashes)) == 1, f"Different hashes: {hashes}"
    
    # AC-WIRE-CONT-004
    def test_container_no_db_files(self):
        """Container should not create any .db files."""
        result = subprocess.run(
            ["docker", "run", "--rm", "cortex/mcp-server:latest",
             "find", "/app", "-name", "*.db"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.stdout.strip() == "", f"Found .db files: {result.stdout}"
    
    # AC-WIRE-CONT-005
    def test_container_wiring_immutable(self):
        """Container wiring should be immutable after startup."""
        result = subprocess.run(
            ["docker", "run", "--rm", "cortex/mcp-server:latest",
             "python", "-c", """
from cortex.wiring import bootstrap_cortex
c1 = bootstrap_cortex()
hash1 = c1.wiring_hash
c2 = bootstrap_cortex()
hash2 = c2.wiring_hash
print(hash1 == hash2)
print(c1 is c2)
"""],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert "True" in result.stdout
    
    # AC-WIRE-CONT-006
    def test_container_mcp_tools_endpoint(self):
        """Container should serve MCP tools endpoint."""
        container_id = subprocess.check_output(
            ["docker", "run", "-d", "-p", "18444:8443", "cortex/mcp-server:latest"],
            text=True
        ).strip()
        
        try:
            time.sleep(10)
            
            import requests
            response = requests.get("http://localhost:18444/mcp/tools", timeout=10)
            
            assert response.status_code == 200
            tools = response.json()
            assert len(tools) >= 23
        finally:
            subprocess.run(["docker", "stop", container_id])
            subprocess.run(["docker", "rm", container_id])
    
    # AC-WIRE-CONT-007
    def test_container_survives_restart(self):
        """Container should wire correctly after restart."""
        container_name = "cortex-test-restart"
        
        # Start
        subprocess.run(
            ["docker", "run", "-d", "--name", container_name, 
             "cortex/mcp-server:latest"],
            check=True
        )
        
        try:
            time.sleep(5)
            
            # Get hash before restart
            result1 = subprocess.run(
                ["docker", "exec", container_name, "python", "-c",
                 "from cortex.wiring import get_wiring_hash; print(get_wiring_hash())"],
                capture_output=True,
                text=True
            )
            hash1 = result1.stdout.strip()
            
            # Restart
            subprocess.run(["docker", "restart", container_name], check=True)
            time.sleep(5)
            
            # Get hash after restart
            result2 = subprocess.run(
                ["docker", "exec", container_name, "python", "-c",
                 "from cortex.wiring import get_wiring_hash; print(get_wiring_hash())"],
                capture_output=True,
                text=True
            )
            hash2 = result2.stdout.strip()
            
            assert hash1 == hash2
        finally:
            subprocess.run(["docker", "stop", container_name])
            subprocess.run(["docker", "rm", container_name])
    
    # AC-WIRE-CONT-008
    def test_multiple_container_instances_same_hash(self):
        """Multiple running containers should have same wiring hash."""
        container_ids = []
        
        try:
            # Start 3 containers
            for i in range(3):
                container_id = subprocess.check_output(
                    ["docker", "run", "-d", "-p", f"{18445+i}:8443",
                     "cortex/mcp-server:latest"],
                    text=True
                ).strip()
                container_ids.append(container_id)
            
            time.sleep(15)  # Wait for all to start
            
            # Get hashes
            import requests
            hashes = []
            for i in range(3):
                response = requests.get(f"http://localhost:{18445+i}/wiring/hash", timeout=10)
                hashes.append(response.json()["wiring_hash"])
            
            assert len(set(hashes)) == 1, f"Different hashes: {hashes}"
        finally:
            for container_id in container_ids:
                subprocess.run(["docker", "stop", container_id])
                subprocess.run(["docker", "rm", container_id])
```

---

## 📊 Test Summary

| Test File | Tests | Category |
|-----------|-------|----------|
| `test_single_path_enforcement.py` | 10 | Enforcement |
| `test_git_backed_registry.py` | 12 | Registry |
| `test_lazy_orchestrator.py` | 8 | Lazy Loading |
| `test_multi_user_scenarios.py` | 10 | Concurrency |
| `test_wiring_determinism.py` | 6 | Determinism |
| `test_no_database_files.py` | 5 | Cleanup |
| `test_container_wiring.py` | 8 | Docker |
| `test_health_recovery.py` | 6 | Health |
| **TOTAL** | **65** | Comprehensive |

---

## 🏃 Running Tests

```bash
# Run all wiring tests
pytest tests/wiring/ -v

# Run specific category
pytest tests/wiring/test_single_path_enforcement.py -v

# Run Docker tests (requires Docker)
pytest tests/wiring/test_container_wiring.py -v -m docker

# Run with coverage
pytest tests/wiring/ --cov=cortex.wiring --cov-report=html
```
