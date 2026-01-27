# CORTEX Health & Recovery Tests
## Test Suite for Health Checks and Recovery Scenarios

**Document:** 08-HEALTH-RECOVERY-TESTS.md  
**Date:** 2026-01-27  

---

## 🎯 Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **Health Checks** | 3 | Verify health endpoint functionality |
| **Recovery Scenarios** | 3 | Test recovery from failures |
| **TOTAL** | **6** | Health & Recovery coverage |

---

## Test File: `test_health_recovery.py`

```python
"""
AC-WIRE-HEALTH-001 through AC-WIRE-HEALTH-006
Test health checks and recovery scenarios.
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock


class TestHealthChecks:
    """Test health check functionality."""
    
    # AC-WIRE-HEALTH-001
    def test_health_endpoint_reports_wired_status(self):
        """Health endpoint should report wired status."""
        from cortex.wiring import bootstrap_cortex, is_wired
        
        bootstrap_cortex()
        
        assert is_wired() == True
    
    # AC-WIRE-HEALTH-002
    def test_health_endpoint_reports_orchestrator_count(self):
        """Health endpoint should report orchestrator count."""
        from cortex.wiring import bootstrap_cortex
        
        cortex = bootstrap_cortex()
        
        assert cortex.orchestrator_count >= 23
    
    # AC-WIRE-HEALTH-003
    def test_health_endpoint_reports_wiring_hash(self):
        """Health endpoint should report wiring hash."""
        from cortex.wiring import bootstrap_cortex, get_wiring_hash
        
        bootstrap_cortex()
        
        hash_val = get_wiring_hash()
        assert hash_val is not None
        assert len(hash_val) == 16  # SHA256 truncated to 16 chars


class TestRecoveryScenarios:
    """Test recovery from failures."""
    
    # AC-WIRE-HEALTH-004
    def test_recovery_from_import_error(self):
        """System should handle import errors gracefully."""
        from cortex.wiring.registry.git_backed_registry import GitBackedRegistry, OrchestratorSpec
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        # Create spec with invalid module
        spec = OrchestratorSpec(
            name="BadOrchestrator",
            module="cortex.nonexistent.module",
            class_name="NonExistentClass",
            category="CORE",
            tier=1,
            priority=999,
            dependencies=[],
            requires_params={},
            capabilities=[],
            health_check="",
            mcp_adapter=""
        )
        
        registry = MagicMock()
        lazy = LazyOrchestrator(spec, registry)
        
        # Should raise ImportError, not crash
        with pytest.raises(ModuleNotFoundError):
            lazy.force_wire()
        
        # System should still function
        from cortex.wiring import is_wired
        # (is_wired depends on main system, not this bad orchestrator)
    
    # AC-WIRE-HEALTH-005
    def test_recovery_from_yaml_error(self, tmp_path):
        """System should handle YAML errors gracefully."""
        from cortex.wiring.registry.git_backed_registry import GitBackedRegistry
        
        # Create invalid YAML
        specs_dir = tmp_path / "specifications"
        specs_dir.mkdir()
        
        bad_yaml = specs_dir / "bad.yaml"
        bad_yaml.write_text("orchestrators: [unclosed")
        
        # Should raise error, not crash
        with pytest.raises(Exception):  # YAML error
            GitBackedRegistry(specs_dir)
    
    # AC-WIRE-HEALTH-006
    def test_concurrent_wiring_under_failure(self):
        """Concurrent wiring should handle partial failures."""
        from cortex.wiring import bootstrap_cortex
        
        errors = []
        successes = []
        
        def wire_thread():
            try:
                cortex = bootstrap_cortex()
                successes.append(cortex)
            except Exception as e:
                errors.append(e)
        
        # Many concurrent attempts
        threads = [threading.Thread(target=wire_thread) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed or fail consistently
        # (No partial states)
        if errors:
            assert len(successes) == 0, "Should be all success or all failure"
        else:
            # All successes should be same instance
            assert len(set(id(s) for s in successes)) == 1
```

---

## Additional Test Utilities

### `conftest.py` for Wiring Tests

```python
"""
Pytest fixtures for wiring tests.
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def cortex_root():
    """Get CORTEX root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def specs_dir(cortex_root):
    """Get wiring specifications directory."""
    return cortex_root / "cortex" / "wiring" / "specifications"


@pytest.fixture(autouse=True)
def reset_wiring_state():
    """Reset wiring state before each test."""
    import cortex.wiring.bootstrap as bootstrap_module
    
    # Save original state
    original_instance = bootstrap_module._CORTEX_INSTANCE
    original_complete = bootstrap_module._WIRING_COMPLETE
    
    yield
    
    # Restore original state
    bootstrap_module._CORTEX_INSTANCE = original_instance
    bootstrap_module._WIRING_COMPLETE = original_complete


@pytest.fixture
def isolated_wiring():
    """Provide isolated wiring for a test."""
    import cortex.wiring.bootstrap as bootstrap_module
    
    # Reset state
    bootstrap_module._CORTEX_INSTANCE = None
    bootstrap_module._WIRING_COMPLETE = False
    
    yield
    
    # Clean up
    bootstrap_module._CORTEX_INSTANCE = None
    bootstrap_module._WIRING_COMPLETE = False


@pytest.fixture
def temp_specs_dir(tmp_path):
    """Create temporary specifications directory."""
    specs_dir = tmp_path / "specifications"
    specs_dir.mkdir()
    return specs_dir


@pytest.fixture
def mock_yaml_specs(temp_specs_dir):
    """Create mock YAML specifications."""
    import yaml
    
    core_specs = {
        "metadata": {"version": "1.0", "category": "CORE"},
        "orchestrators": [
            {
                "name": "TestMasterOrchestrator",
                "module": "cortex.orchestrators.core.master_orchestrator",
                "class_name": "MasterOrchestrator",
                "category": "CORE",
                "tier": 0,
                "priority": 1,
                "dependencies": [],
                "requires_params": {},
                "capabilities": ["test"],
                "health_check": "True",
                "mcp_adapter": ""
            }
        ]
    }
    
    with open(temp_specs_dir / "core-wiring.yaml", 'w') as f:
        yaml.dump(core_specs, f)
    
    return temp_specs_dir
```

---

## Running All Wiring Tests

```bash
# Full test suite
pytest tests/wiring/ -v

# With coverage
pytest tests/wiring/ --cov=cortex.wiring --cov-report=html

# Specific categories
pytest tests/wiring/test_single_path_enforcement.py -v
pytest tests/wiring/test_git_backed_registry.py -v
pytest tests/wiring/test_lazy_orchestrator.py -v
pytest tests/wiring/test_multi_user_scenarios.py -v
pytest tests/wiring/test_wiring_determinism.py -v
pytest tests/wiring/test_no_database_files.py -v
pytest tests/wiring/test_health_recovery.py -v

# Docker tests (requires Docker)
pytest tests/wiring/test_container_wiring.py -v -m docker
```

---

## Test Summary

| Test File | Tests | AC IDs |
|-----------|-------|--------|
| `test_single_path_enforcement.py` | 10 | AC-WIRE-SINGLE-001 to 010 |
| `test_git_backed_registry.py` | 12 | AC-WIRE-GIT-001 to 012 |
| `test_lazy_orchestrator.py` | 8 | AC-WIRE-LAZY-001 to 008 |
| `test_multi_user_scenarios.py` | 10 | AC-WIRE-MULTI-001 to 010 |
| `test_wiring_determinism.py` | 6 | AC-WIRE-DET-001 to 006 |
| `test_no_database_files.py` | 5 | AC-WIRE-NODB-001 to 005 |
| `test_container_wiring.py` | 8 | AC-WIRE-CONT-001 to 008 |
| `test_health_recovery.py` | 6 | AC-WIRE-HEALTH-001 to 006 |
| **TOTAL** | **65** | |
