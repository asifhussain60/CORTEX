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
    # AC-CORE-035-TEST-004
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
        script_path = cortex_root / "cortex" / "tools" / "verify_production_readiness.py"
        
        assert script_path.exists(), (
            "verify_production_readiness.py must exist in cortex/tools/"
        )
    
    # AC-HOOK-TEST-004
    def test_verify_prod_ready_has_core_checks(self):
        """Verify production readiness script has core verification checks."""
        script_path = cortex_root / "cortex" / "tools" / "verify_production_readiness.py"
        content = script_path.read_text()
        
        # Should have core verification sections
        required_sections = [
            "PRODUCTION READINESS",
            "CORE ORCHESTRATORS",
        ]
        
        missing = [s for s in required_sections if s not in content]
        
        assert len(missing) == 0, (
            f"verify_production_readiness.py missing sections: {missing}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
