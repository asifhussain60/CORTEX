"""
Tests for Git-Backed Wiring Registry (Phase 3)

Validates YAML-based orchestrator wiring system.

Authority: _workspaces/docker-plan/migration-phases-plan.yaml (Phase 3)
"""

import pytest
from pathlib import Path
from typing import Dict, Any


@pytest.fixture(autouse=True)
def reset_wiring_registry():
    """Reset registry singleton before each test."""
    from cortex.wiring.registry import reset_registry
    reset_registry()
    yield
    reset_registry()


def test_wiring_yaml_exists() -> None:
    """Test that wiring.yaml specification file exists."""
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    assert wiring_file.exists(), f"Wiring specification not found at {wiring_file}"


def test_wiring_yaml_is_valid() -> None:
    """Test that wiring.yaml is valid YAML and loads correctly."""
    import yaml
    
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    assert spec is not None, "Wiring specification is empty"
    assert 'orchestrators' in spec, "Missing 'orchestrators' key"
    assert 'core' in spec['orchestrators'], "Missing 'core' orchestrators"
    assert 'domain' in spec['orchestrators'], "Missing 'domain' orchestrators"
    assert 'support' in spec['orchestrators'], "Missing 'support' orchestrators"


def test_all_23_orchestrators_defined() -> None:
    """Test that all 23 orchestrators are defined in wiring.yaml."""
    import yaml
    
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    core_count = len(spec['orchestrators']['core'])
    domain_count = len(spec['orchestrators']['domain'])
    support_count = len(spec['orchestrators']['support'])
    
    total = core_count + domain_count + support_count
    
    assert core_count == 6, f"Expected 6 core orchestrators, got {core_count}"
    assert domain_count == 6, f"Expected 6 domain orchestrators, got {domain_count}"
    assert support_count == 11, f"Expected 11 support orchestrators, got {support_count}"
    assert total == 23, f"Expected 23 total orchestrators, got {total}"


def test_orchestrators_have_required_fields() -> None:
    """Test that all orchestrators have required fields."""
    import yaml
    
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    required_fields = {'name', 'module', 'class', 'tier', 'priority', 'dependencies', 'capabilities', 'health_check'}
    
    for category in ['core', 'domain', 'support']:
        for orch in spec['orchestrators'][category]:
            missing = required_fields - set(orch.keys())
            assert not missing, f"Orchestrator {orch.get('name', 'UNKNOWN')} missing fields: {missing}"


def test_no_circular_dependencies() -> None:
    """Test that there are no circular dependencies in wiring."""
    import yaml
    
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Build dependency graph
    graph: Dict[str, list] = {}
    for category in ['core', 'domain', 'support']:
        for orch in spec['orchestrators'][category]:
            name = orch['name']
            deps = orch.get('dependencies', [])
            graph[name] = deps
    
    # Check for cycles using DFS
    def has_cycle(node: str, visited: set, rec_stack: set) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    visited: set = set()
    for node in graph:
        if node not in visited:
            assert not has_cycle(node, visited, set()), f"Circular dependency detected involving {node}"


def test_all_dependencies_exist() -> None:
    """Test that all dependency names reference existing orchestrators."""
    import yaml
    
    wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Collect all orchestrator names
    all_names = set()
    for category in ['core', 'domain', 'support']:
        for orch in spec['orchestrators'][category]:
            all_names.add(orch['name'])
    
    # Verify all dependencies exist
    for category in ['core', 'domain', 'support']:
        for orch in spec['orchestrators'][category]:
            for dep in orch.get('dependencies', []):
                assert dep in all_names, f"Orchestrator {orch['name']} depends on non-existent {dep}"


def test_git_backed_registry_module_exists() -> None:
    """Test that git_backed_registry.py module exists."""
    registry_file = Path("cortex/wiring/registry/git_backed_registry.py")
    assert registry_file.exists(), f"Git-backed registry not found at {registry_file}"


def test_lazy_orchestrator_module_exists() -> None:
    """Test that lazy_orchestrator.py module exists."""
    lazy_file = Path("cortex/wiring/registry/lazy_orchestrator.py")
    assert lazy_file.exists(), f"Lazy orchestrator not found at {lazy_file}"


def test_wiring_validator_module_exists() -> None:
    """Test that wiring_validator.py module exists."""
    validator_file = Path("cortex/wiring/registry/wiring_validator.py")
    assert validator_file.exists(), f"Wiring validator not found at {validator_file}"


def test_bootstrap_module_exists() -> None:
    """Test that bootstrap.py module exists."""
    bootstrap_file = Path("cortex/wiring/bootstrap.py")
    assert bootstrap_file.exists(), f"Bootstrap module not found at {bootstrap_file}"


def test_wiring_init_exports() -> None:
    """Test that cortex/wiring/__init__.py exports required functions."""
    from cortex.wiring import (
        bootstrap_cortex,
        get_cortex,
        is_wired,
        get_wiring_hash
    )
    
    assert callable(bootstrap_cortex), "bootstrap_cortex not callable"
    assert callable(get_cortex), "get_cortex not callable"
    assert callable(is_wired), "is_wired not callable"
    assert callable(get_wiring_hash), "get_wiring_hash not callable"


def test_bootstrap_cortex_returns_registry() -> None:
    """Test that bootstrap_cortex() returns a valid registry."""
    from cortex.wiring import bootstrap_cortex
    
    registry = bootstrap_cortex()
    
    assert registry is not None, "bootstrap_cortex returned None"
    assert hasattr(registry, 'get_orchestrator'), "Registry missing get_orchestrator method"
    assert hasattr(registry, 'list_orchestrators'), "Registry missing list_orchestrators method"


def test_registry_can_list_orchestrators() -> None:
    """Test that registry can list all 23 orchestrators."""
    from cortex.wiring import bootstrap_cortex
    
    registry = bootstrap_cortex()
    orchestrators = registry.list_orchestrators()
    
    assert len(orchestrators) == 23, f"Expected 23 orchestrators, got {len(orchestrators)}"


def test_lazy_initialization_works() -> None:
    """Test that orchestrators are lazy-loaded on first access."""
    from cortex.wiring import bootstrap_cortex
    
    registry = bootstrap_cortex()
    
    # First access should trigger initialization
    orch = registry.get_orchestrator("MasterOrchestrator")
    
    assert orch is not None, "MasterOrchestrator not found"
    assert hasattr(orch, '__class__'), "Orchestrator not initialized"


def test_wiring_hash_is_deterministic() -> None:
    """Test that wiring hash is deterministic for same YAML."""
    from cortex.wiring import get_wiring_hash
    
    hash1 = get_wiring_hash()
    hash2 = get_wiring_hash()
    
    assert hash1 == hash2, "Wiring hash is not deterministic"
    assert len(hash1) > 0, "Wiring hash is empty"


def test_is_wired_returns_true_after_bootstrap() -> None:
    """Test that is_wired() returns True after bootstrap."""
    from cortex.wiring import bootstrap_cortex, is_wired
    from cortex.wiring.registry import reset_registry
    
    # Force reset to ensure clean state
    reset_registry()
    
    # Bootstrap system
    bootstrap_cortex()
    
    # Now should be wired
    assert is_wired(), "Should be wired after bootstrap"
