#!/usr/bin/env python3
"""
Tests for CORE-035: Single Canonical Implementation Enforcement

AC-CORE-035-TEST-001: Duplicate Detection
AC-CORE-035-TEST-002: Registry Validation
AC-CORE-035-TEST-003: Execution Path Analysis

Author: Asif Hussain
Date: 2026-01-29
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add CORTEX root to path
cortex_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(cortex_root))


class TestCore035Enforcement:
    """Test CORE-035 enforcement rules."""
    
    # AC-CORE-035-TEST-001
    def test_no_forbidden_file_patterns(self):
        """Verify no *_unified, *_refactored, *_v2 files exist."""
        forbidden_patterns = [
            "*_unified.py",
            "*_refactored.py",
            "*_v2.py",
            "*_v3.py",
            "*_alternative.py",
            "*_new.py",
            "*_old.py",
            "*_legacy.py",
            "*_backup.py",
        ]
        
        violations: List[Path] = []
        cortex_dir = cortex_root / "cortex"
        
        for pattern in forbidden_patterns:
            found = list(cortex_dir.rglob(pattern))
            violations.extend(found)
        
        assert len(violations) == 0, (
            f"CORE-035 VIOLATION: Found {len(violations)} forbidden file patterns:\n"
            + "\n".join(f"  - {v.relative_to(cortex_root)}" for v in violations)
        )
    
    # AC-CORE-035-TEST-002
    def test_single_registry_implementation(self):
        """Verify only one canonical registry exists."""
        from cortex.wiring.registry.git_backed_registry import GitBackedRegistry
        from cortex.wiring import get_registry
        
        # Should get same instance
        registry1 = get_registry()
        registry2 = get_registry()
        
        assert registry1 is registry2, (
            "get_registry() should return singleton instance"
        )
        
        assert isinstance(registry1, GitBackedRegistry), (
            f"Expected GitBackedRegistry, got {type(registry1)}"
        )
    
    # AC-CORE-035-TEST-003
    def test_no_duplicate_bootstrap_functions(self):
        """Verify only one bootstrap_cortex exists."""
        import ast
        import importlib.util
        
        bootstrap_locations: List[str] = []
        cortex_dir = cortex_root / "cortex"
        
        for py_file in cortex_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name == "bootstrap_cortex":
                            bootstrap_locations.append(
                                str(py_file.relative_to(cortex_root))
                            )
            except Exception:
                pass
        
        assert len(bootstrap_locations) <= 1, (
            f"CORE-035 VIOLATION: Multiple bootstrap_cortex implementations:\n"
            + "\n".join(f"  - {loc}" for loc in bootstrap_locations)
        )
    
    # AC-CORE-035-TEST-004
    def test_no_duplicate_get_orchestrator_implementations(self):
        """Verify single get_orchestrator execution path."""
        import ast
        
        get_orch_locations: List[str] = []
        cortex_dir = cortex_root / "cortex"
        
        # Exclude known legitimate locations
        exclude_paths = [
            "cortex/wiring/registry/git_backed_registry.py",  # Canonical
            "cortex/wiring/registry/lazy_orchestrator.py",    # Proxy
        ]
        
        for py_file in cortex_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue
            
            relative_path = str(py_file.relative_to(cortex_root))
            if any(exc in relative_path for exc in exclude_paths):
                continue
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if "get_orchestrator" in node.name and "registry" not in relative_path:
                            get_orch_locations.append(relative_path)
            except Exception:
                pass
        
        # Allow up to 2 (GitBackedRegistry + one helper)
        assert len(get_orch_locations) <= 2, (
            f"CORE-035 WARNING: Multiple get_orchestrator implementations:\n"
            + "\n".join(f"  - {loc}" for loc in get_orch_locations)
        )
    
    # AC-CORE-035-TEST-005
    def test_wiring_yaml_is_single_source_of_truth(self):
        """Verify wiring.yaml is the only orchestrator definition source."""
        wiring_yaml = cortex_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"
        
        assert wiring_yaml.exists(), (
            "wiring.yaml must exist at cortex/wiring/specifications/wiring.yaml"
        )
        
        # Check no alternate YAML registries exist
        yaml_files = list((cortex_root / "cortex").rglob("*orchestrator*.yaml"))
        yaml_files = [
            f for f in yaml_files 
            if f != wiring_yaml and "test" not in str(f)
        ]
        
        assert len(yaml_files) == 0, (
            f"CORE-035 VIOLATION: Found alternate orchestrator YAML files:\n"
            + "\n".join(f"  - {f.relative_to(cortex_root)}" for f in yaml_files)
        )
    
    # AC-CORE-035-TEST-006
    def test_no_competing_registry_classes(self):
        """Verify no competing registry implementations exist."""
        import ast
        
        registry_classes: Dict[str, List[str]] = {}
        cortex_dir = cortex_root / "cortex"
        
        # Canonical registry
        canonical = "cortex/wiring/registry/git_backed_registry.py::GitBackedRegistry"
        
        for py_file in cortex_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "Registry" in node.name and "Orchestrator" in node.name:
                            relative_path = str(py_file.relative_to(cortex_root))
                            class_name = f"{relative_path}::{node.name}"
                            
                            if node.name not in registry_classes:
                                registry_classes[node.name] = []
                            registry_classes[node.name].append(class_name)
            except Exception:
                pass
        
        # Check for duplicates
        duplicates = {
            name: locs 
            for name, locs in registry_classes.items() 
            if len(locs) > 1
        }
        
        assert len(duplicates) == 0, (
            f"CORE-035 VIOLATION: Found duplicate registry classes:\n"
            + "\n".join(
                f"  - {name}: {len(locs)} implementations"
                for name, locs in duplicates.items()
            )
        )


class TestProductionReadinessHooks:
    """Test Git hooks integration."""
    
    # AC-HOOK-TEST-001
    def test_pre_commit_hook_exists(self):
        """Verify pre-commit hook is installed."""
        hook_path = cortex_root / ".git" / "hooks" / "pre-commit"
        
        assert hook_path.exists(), (
            "pre-commit hook must exist at .git/hooks/pre-commit"
        )
        
        # Check it's executable
        assert hook_path.stat().st_mode & 0o111, (
            "pre-commit hook must be executable"
        )
    
    # AC-HOOK-TEST-002
    def test_pre_commit_enforces_core_rules(self):
        """Verify pre-commit checks CORE rules."""
        hook_path = cortex_root / ".git" / "hooks" / "pre-commit"
        content = hook_path.read_text()
        
        # Should check CORE-013, CORE-028, CORE-038
        assert "CORE-013" in content or "bare except" in content.lower()
        assert "CORE-028" in content or "snake_case" in content.lower()
        assert "CORE-038" in content or "FILE PLACEMENT" in content
    
    # AC-HOOK-TEST-003
    def test_verify_prod_ready_script_exists(self):
        """Verify production readiness script exists."""
        script_path = cortex_root / "_workspaces" / "cortex-plan" / "verify_prod_ready.py"
        
        assert script_path.exists(), (
            "verify_prod_ready.py must exist in _workspaces/cortex-plan/"
        )
        
        # Check it's executable
        assert script_path.stat().st_mode & 0o111, (
            "verify_prod_ready.py must be executable"
        )
    
    # AC-HOOK-TEST-004
    def test_verify_prod_ready_has_16_checks(self):
        """Verify production readiness script has all checks."""
        script_path = cortex_root / "_workspaces" / "cortex-plan" / "verify_prod_ready.py"
        content = script_path.read_text()
        
        # Should have 16 check methods
        check_methods = [
            "check_01_orchestrators_wired",
            "check_02_lens_intelligence",
            "check_03_master_orchestrator",
            "check_04_machine_readable_config",
            "check_05_no_duplicates",
            "check_06_clean_test_suite",
            "check_07_docker_plan_compliance",
            "check_08_production_ready",
            "check_09_mcp_exposure",
            "check_10_docker_configuration",
            "check_11_database_cleanliness",
            "check_12_prompt_code_sync",
            "check_13_cortical_memory_system_readiness",
            "check_14_capacity_estimation_readiness",
            "check_15_adaptive_bluf_readiness",
            "check_16_complete_production_readiness",
        ]
        
        missing = [m for m in check_methods if m not in content]
        
        assert len(missing) == 0, (
            f"verify_prod_ready.py missing checks: {missing}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
